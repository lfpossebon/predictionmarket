"""
🔔 Polymarket Real-Time Monitor
Monitora top traders e envia alertas via Telegram.

Uso:
  python3 realtime_monitor.py              # Roda uma vez
  python3 realtime_monitor.py --loop       # Loop contínuo (a cada 5min)
  python3 realtime_monitor.py --setup      # Setup inicial (cria snapshot base)

Alertas enviados via OpenClaw → Telegram
"""

import requests
import json
import time
import sys
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# === CONFIG ===
DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "polymarket"
MONITOR_DIR = DATA_DIR / "monitor"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)

# Arquivo de estado
STATE_FILE = MONITOR_DIR / "monitor_state.json"
ALERTS_LOG = MONITOR_DIR / "alerts_log.json"

# Configuração do monitor
POLL_INTERVAL = 300  # 5 minutos
TOP_TRADERS_LIMIT = 50  # Monitorar top 50
MIN_TRADE_VALUE = 100  # Mínimo USD pra alertar
MIN_POSITION_VALUE = 500  # Mínimo USD pra alertar nova posição
CONSENSUS_THRESHOLD = 0.60  # 60% pra alertar (mais sensível que o trading)
PRICE_CHANGE_THRESHOLD = 0.10  # 10% de mudança de preço


def api_get(url, params=None, retries=3):
    """GET com retry."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep((2 ** attempt) * 2)
                continue
            if r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries - 1:
                return None
            time.sleep(2 ** attempt)
    return None


def send_alert(message: str):
    """Envia alerta via OpenClaw → Telegram."""
    print(f"  📨 {message[:80]}...")
    try:
        # Usar openclaw CLI pra enviar mensagem
        result = subprocess.run(
            ["openclaw", "send", "--channel", "telegram", "--message", message],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            # Fallback: salvar no log
            print(f"    ⚠️ Falha no envio, salvando no log")
            log_alert(message)
    except Exception as e:
        print(f"    ⚠️ Erro envio: {e}")
        log_alert(message)


def log_alert(message: str):
    """Salva alerta no log local."""
    alerts = []
    if ALERTS_LOG.exists():
        try:
            alerts = json.loads(ALERTS_LOG.read_text())
        except:
            alerts = []
    
    alerts.append({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })
    
    # Manter últimos 500
    alerts = alerts[-500:]
    ALERTS_LOG.write_text(json.dumps(alerts, indent=2))


# === STATE MANAGEMENT ===

def load_state() -> dict:
    """Carrega estado anterior."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {
        "last_scan": None,
        "tracked_wallets": [],
        "known_positions": {},  # wallet -> {conditionId: {outcome, size, value}}
        "known_trades": {},  # wallet -> last_trade_id
        "market_prices": {},  # conditionId -> last_price
        "scan_count": 0
    }


def save_state(state: dict):
    """Salva estado."""
    state["last_scan"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


# === DATA COLLECTION ===

def get_tracked_wallets(limit=50) -> list:
    """Pega top traders pra monitorar."""
    data = api_get(f"{DATA_API}/v1/leaderboard", {
        "category": "OVERALL", "timePeriod": "MONTH",
        "orderBy": "PNL", "limit": limit
    })
    if not data:
        return []
    
    wallets = []
    for t in data:
        addr = t.get("proxyWallet") or t.get("userAddress", "")
        if addr:
            wallets.append({
                "address": addr,
                "username": t.get("userName", addr[:10]),
                "pnl": float(t.get("pnl", 0)),
                "volume": float(t.get("vol", 0))
            })
    return wallets


def get_positions(wallet: str) -> list:
    """Posições atuais."""
    data = api_get(f"{DATA_API}/positions", {"user": wallet, "sizeThreshold": 0})
    return data if data else []


def get_recent_activity(wallet: str, limit=20) -> list:
    """Atividade recente."""
    data = api_get(f"{DATA_API}/activity", {"user": wallet, "limit": limit})
    return data if data else []


# === DETECÇÃO DE MUDANÇAS ===

def detect_new_trades(wallet: str, username: str, activity: list, state: dict) -> list:
    """Detecta trades novos desde último scan."""
    alerts = []
    last_known = state["known_trades"].get(wallet)
    
    new_trades = []
    for trade in activity:
        trade_id = trade.get("id") or trade.get("transactionHash", "")
        if trade_id == last_known:
            break
        new_trades.append(trade)
    
    # Atualizar last known
    if activity:
        first_id = activity[0].get("id") or activity[0].get("transactionHash", "")
        state["known_trades"][wallet] = first_id
    
    for trade in new_trades:
        trade_type = trade.get("type", "")
        if trade_type != "TRADE":
            continue
        
        side = trade.get("side", "?")
        title = trade.get("title") or trade.get("question") or trade.get("market", "?")
        outcome = trade.get("outcome", "?")
        price = float(trade.get("price", 0))
        size = float(trade.get("size", 0))
        value = price * size if price and size else 0
        
        if value < MIN_TRADE_VALUE:
            continue
        
        emoji = "🟢" if side == "BUY" else "🔴"
        alerts.append(
            f"{emoji} {username} — {side}\n"
            f"📌 {title[:60]}\n"
            f"Outcome: {outcome} @ ${price:.2f}\n"
            f"Valor: ${value:,.0f}"
        )
    
    return alerts


def detect_position_changes(wallet: str, username: str, positions: list, state: dict) -> list:
    """Detecta novas posições ou posições fechadas."""
    alerts = []
    
    # Posições atuais indexadas por conditionId+outcome
    current = {}
    for pos in positions:
        cid = pos.get("conditionId", "")
        outcome = pos.get("outcome", "")
        key = f"{cid}_{outcome}"
        current[key] = {
            "title": pos.get("title", "?"),
            "outcome": outcome,
            "size": float(pos.get("size", 0)),
            "value": float(pos.get("currentValue", 0)),
            "pnl": float(pos.get("cashPnl", 0))
        }
    
    # Posições anteriores
    previous = state["known_positions"].get(wallet, {})
    
    # Novas posições
    for key, pos in current.items():
        if key not in previous and pos["value"] >= MIN_POSITION_VALUE:
            alerts.append(
                f"🆕 {username} — Nova posição\n"
                f"📌 {pos['title'][:60]}\n"
                f"Outcome: {pos['outcome']}\n"
                f"Valor: ${pos['value']:,.0f}"
            )
    
    # Posições fechadas (com lucro ou prejuízo significativo)
    for key, pos in previous.items():
        if key not in current and pos.get("value", 0) >= MIN_POSITION_VALUE:
            alerts.append(
                f"📤 {username} — Posição fechada\n"
                f"📌 {pos['title'][:60]}\n"
                f"Outcome: {pos['outcome']}"
            )
    
    # Atualizar estado
    state["known_positions"][wallet] = current
    
    return alerts


def detect_consensus(wallets_positions: dict, wallets_info: dict) -> list:
    """Detecta consenso entre traders."""
    alerts = []
    
    # Agrupa por mercado
    market_votes = defaultdict(lambda: {"YES": [], "NO": [], "title": ""})
    
    for wallet, positions in wallets_positions.items():
        username = wallets_info.get(wallet, {}).get("username", wallet[:10])
        for pos in positions:
            cid = pos.get("conditionId", "")
            outcome = pos.get("outcome", "")
            title = pos.get("title", "?")
            value = float(pos.get("currentValue", 0))
            
            if value < 50:  # Ignorar posições muito pequenas
                continue
            
            if outcome in ("Yes", "YES"):
                market_votes[cid]["YES"].append({"wallet": wallet, "username": username, "value": value})
            elif outcome in ("No", "NO"):
                market_votes[cid]["NO"].append({"wallet": wallet, "username": username, "value": value})
            
            market_votes[cid]["title"] = title
    
    total_wallets = len(wallets_positions)
    if total_wallets < 5:
        return alerts
    
    for cid, votes in market_votes.items():
        for outcome in ["YES", "NO"]:
            voters = votes[outcome]
            if len(voters) < 3:
                continue
            
            consensus_pct = len(voters) / total_wallets
            total_value = sum(v["value"] for v in voters)
            
            if consensus_pct >= CONSENSUS_THRESHOLD:
                top_voters = sorted(voters, key=lambda x: x["value"], reverse=True)[:5]
                voter_names = ", ".join(v["username"] for v in top_voters)
                
                alerts.append(
                    f"🎯 CONSENSO: {consensus_pct*100:.0f}% dos top traders\n"
                    f"📌 {votes['title'][:60]}\n"
                    f"Outcome: {outcome}\n"
                    f"Traders: {len(voters)}/{total_wallets} (${total_value:,.0f})\n"
                    f"Top: {voter_names}"
                )
    
    return alerts


# === MAIN SCAN ===

def run_scan(state: dict, verbose=True) -> list:
    """Executa um scan completo."""
    all_alerts = []
    scan_start = time.time()
    state["scan_count"] = state.get("scan_count", 0) + 1
    
    if verbose:
        print(f"\n{'='*50}")
        print(f"🔍 Scan #{state['scan_count']} — {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
    
    # 1. Pegar wallets pra monitorar
    if verbose:
        print("\n[1] Carregando top traders...")
    
    wallets = get_tracked_wallets(TOP_TRADERS_LIMIT)
    if not wallets:
        print("  ⚠️ Não conseguiu carregar traders")
        return []
    
    if verbose:
        print(f"  {len(wallets)} traders monitorados")
    
    wallets_info = {w["address"]: w for w in wallets}
    wallets_positions = {}
    
    # 2. Scan por trader
    if verbose:
        print(f"\n[2] Escaneando {len(wallets)} traders...")
    
    for i, w in enumerate(wallets):
        addr = w["address"]
        username = w["username"]
        
        # Activity
        activity = get_recent_activity(addr, limit=10)
        time.sleep(0.3)
        
        # Positions
        positions = get_positions(addr)
        time.sleep(0.3)
        
        wallets_positions[addr] = positions
        
        # Detectar mudanças (só se não é primeiro scan)
        if state.get("last_scan"):
            trade_alerts = detect_new_trades(addr, username, activity, state)
            position_alerts = detect_position_changes(addr, username, positions, state)
            all_alerts.extend(trade_alerts)
            all_alerts.extend(position_alerts)
        else:
            # Primeiro scan: só inicializar estado
            if activity:
                first_id = activity[0].get("id") or activity[0].get("transactionHash", "")
                state["known_trades"][addr] = first_id
            
            current = {}
            for pos in positions:
                cid = pos.get("conditionId", "")
                outcome = pos.get("outcome", "")
                key = f"{cid}_{outcome}"
                current[key] = {
                    "title": pos.get("title", "?"),
                    "outcome": outcome,
                    "size": float(pos.get("size", 0)),
                    "value": float(pos.get("currentValue", 0)),
                    "pnl": float(pos.get("cashPnl", 0))
                }
            state["known_positions"][addr] = current
        
        if verbose and (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(wallets)}] escaneados...")
    
    # 3. Detectar consenso
    if verbose:
        print(f"\n[3] Analisando consenso...")
    
    consensus_alerts = detect_consensus(wallets_positions, wallets_info)
    all_alerts.extend(consensus_alerts)
    
    # 4. Salvar estado
    save_state(state)
    
    elapsed = time.time() - scan_start
    
    if verbose:
        print(f"\n✅ Scan completo em {elapsed:.0f}s")
        print(f"   Alertas: {len(all_alerts)}")
    
    return all_alerts


def run_setup():
    """Setup inicial — cria snapshot base sem enviar alertas."""
    print("🔧 Setup inicial — criando snapshot base...")
    state = load_state()
    alerts = run_scan(state, verbose=True)
    print(f"\n✅ Setup completo! Base criada com {len(state.get('known_positions', {}))} traders.")
    print(f"   Próximos scans vão detectar mudanças a partir deste ponto.")
    print(f"   State salvo em: {STATE_FILE}")


def run_once():
    """Roda um scan e envia alertas."""
    state = load_state()
    
    if not state.get("last_scan"):
        print("⚠️ Primeiro scan — rodando setup...")
        run_setup()
        return
    
    alerts = run_scan(state, verbose=True)
    
    if alerts:
        # Agrupar alertas em uma mensagem
        header = f"🔔 Polymarket Monitor — {datetime.now().strftime('%d/%m %H:%M')}\n{'─'*30}\n\n"
        
        # Enviar em blocos de 5 alertas (limite de tamanho do Telegram)
        for i in range(0, len(alerts), 5):
            batch = alerts[i:i+5]
            message = header + "\n\n".join(batch)
            send_alert(message)
            log_alert(message)
    else:
        print("  Nenhum alerta novo")


def run_loop():
    """Loop contínuo com intervalo configurável."""
    print(f"🔄 Monitor em loop — scan a cada {POLL_INTERVAL//60} minutos")
    print(f"   Ctrl+C para parar\n")
    
    state = load_state()
    
    if not state.get("last_scan"):
        print("Primeiro scan — setup...")
        run_scan(state, verbose=True)
        print(f"\nBase criada. Próximo scan em {POLL_INTERVAL//60} min...\n")
        time.sleep(POLL_INTERVAL)
    
    while True:
        try:
            alerts = run_scan(state, verbose=True)
            
            if alerts:
                header = f"🔔 Polymarket Monitor — {datetime.now().strftime('%d/%m %H:%M')}\n{'─'*30}\n\n"
                for i in range(0, len(alerts), 5):
                    batch = alerts[i:i+5]
                    message = header + "\n\n".join(batch)
                    send_alert(message)
                    log_alert(message)
                print(f"  📨 {len(alerts)} alertas enviados")
            
            print(f"\n⏳ Próximo scan em {POLL_INTERVAL//60} min...")
            time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor parado.")
            save_state(state)
            break
        except Exception as e:
            print(f"\n⚠️ Erro no scan: {e}")
            print(f"   Tentando novamente em {POLL_INTERVAL//60} min...")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        run_setup()
    elif "--loop" in sys.argv:
        run_loop()
    else:
        run_once()

"""
🔔 Polymarket Real-Time Monitor v2
Monitoramento otimizado com requests paralelos + websocket de preços.

Uso:
  python3 realtime_monitor.py              # Roda uma vez
  python3 realtime_monitor.py --loop       # Loop contínuo (~90s entre scans)
  python3 realtime_monitor.py --setup      # Setup inicial (cria snapshot base)
  python3 realtime_monitor.py --ws         # Loop + websocket de preços real-time

Alertas enviados via OpenClaw → Telegram
"""

import requests
import json
import time
import sys
import subprocess
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIG ===
DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
CLOB_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "polymarket"
MONITOR_DIR = DATA_DIR / "monitor"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = MONITOR_DIR / "monitor_state.json"
ALERTS_LOG = MONITOR_DIR / "alerts_log.json"
PRICES_FILE = MONITOR_DIR / "live_prices.json"

# Configuração
POLL_INTERVAL = 90  # 90 segundos entre scans
TOP_TRADERS_LIMIT = 50
MAX_WORKERS = 10  # Threads paralelas
REQUEST_TIMEOUT = 15
MIN_TRADE_VALUE = 100
MIN_POSITION_VALUE = 500
CONSENSUS_THRESHOLD = 0.60
PRICE_ALERT_THRESHOLD = 0.08  # 8% mudança de preço


def api_get(url, params=None, retries=2):
    """GET com retry rápido."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429:
                time.sleep(1 + attempt)
                continue
            if r.status_code >= 500:
                time.sleep(0.5)
                continue
            r.raise_for_status()
            return r.json()
        except:
            if attempt == retries - 1:
                return None
            time.sleep(0.5)
    return None


def send_alert(message: str):
    """Envia alerta via OpenClaw → Telegram."""
    print(f"  📨 {message[:80]}...")
    try:
        subprocess.run(
            ["openclaw", "send", "--channel", "telegram", "--message", message],
            capture_output=True, text=True, timeout=15
        )
    except:
        pass
    log_alert(message)


def log_alert(message: str):
    """Salva alerta no log local."""
    alerts = []
    if ALERTS_LOG.exists():
        try:
            alerts = json.loads(ALERTS_LOG.read_text())
        except:
            alerts = []
    alerts.append({"timestamp": datetime.now().isoformat(), "message": message})
    alerts = alerts[-1000:]
    ALERTS_LOG.write_text(json.dumps(alerts, indent=2))


# === STATE ===

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {
        "last_scan": None, "tracked_wallets": [],
        "known_positions": {}, "known_trades": {},
        "market_prices": {}, "scan_count": 0
    }


def save_state(state: dict):
    state["last_scan"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


# === PARALLEL DATA COLLECTION ===

def fetch_trader_data(wallet: str) -> dict:
    """Busca activity + positions de um trader em sequência rápida."""
    activity = api_get(f"{DATA_API}/activity", {"user": wallet, "limit": 15})
    positions = api_get(f"{DATA_API}/positions", {"user": wallet, "sizeThreshold": 0})
    return {
        "wallet": wallet,
        "activity": activity or [],
        "positions": positions or []
    }


def get_tracked_wallets(limit=50) -> list:
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


# === DETECTION ===

def detect_new_trades(wallet, username, activity, state):
    alerts = []
    last_known = state["known_trades"].get(wallet)
    new_trades = []
    for trade in activity:
        trade_id = trade.get("id") or trade.get("transactionHash", "")
        if trade_id == last_known:
            break
        new_trades.append(trade)
    if activity:
        first_id = activity[0].get("id") or activity[0].get("transactionHash", "")
        state["known_trades"][wallet] = first_id
    for trade in new_trades:
        if trade.get("type") != "TRADE":
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


def detect_position_changes(wallet, username, positions, state):
    alerts = []
    current = {}
    for pos in positions:
        cid = pos.get("conditionId", "")
        outcome = pos.get("outcome", "")
        key = f"{cid}_{outcome}"
        current[key] = {
            "title": pos.get("title", "?"), "outcome": outcome,
            "size": float(pos.get("size", 0)),
            "value": float(pos.get("currentValue", 0)),
            "pnl": float(pos.get("cashPnl", 0))
        }
    previous = state["known_positions"].get(wallet, {})
    for key, pos in current.items():
        if key not in previous and pos["value"] >= MIN_POSITION_VALUE:
            alerts.append(
                f"🆕 {username} — Nova posição\n"
                f"📌 {pos['title'][:60]}\n"
                f"Outcome: {pos['outcome']}\nValor: ${pos['value']:,.0f}"
            )
    for key, pos in previous.items():
        if key not in current and pos.get("value", 0) >= MIN_POSITION_VALUE:
            alerts.append(
                f"📤 {username} — Posição fechada\n"
                f"📌 {pos['title'][:60]}\nOutcome: {pos['outcome']}"
            )
    state["known_positions"][wallet] = current
    return alerts


def detect_consensus(wallets_positions, wallets_info):
    alerts = []
    market_votes = defaultdict(lambda: {"YES": [], "NO": [], "title": ""})
    for wallet, positions in wallets_positions.items():
        username = wallets_info.get(wallet, {}).get("username", wallet[:10])
        for pos in positions:
            cid = pos.get("conditionId", "")
            outcome = pos.get("outcome", "")
            title = pos.get("title", "?")
            value = float(pos.get("currentValue", 0))
            if value < 50:
                continue
            if outcome in ("Yes", "YES"):
                market_votes[cid]["YES"].append({"wallet": wallet, "username": username, "value": value})
            elif outcome in ("No", "NO"):
                market_votes[cid]["NO"].append({"wallet": wallet, "username": username, "value": value})
            market_votes[cid]["title"] = title
    total = len(wallets_positions)
    if total < 5:
        return alerts
    for cid, votes in market_votes.items():
        for outcome in ["YES", "NO"]:
            voters = votes[outcome]
            if len(voters) < 3:
                continue
            pct = len(voters) / total
            total_value = sum(v["value"] for v in voters)
            if pct >= CONSENSUS_THRESHOLD:
                top = sorted(voters, key=lambda x: x["value"], reverse=True)[:5]
                names = ", ".join(v["username"] for v in top)
                alerts.append(
                    f"🎯 CONSENSO: {pct*100:.0f}% dos top traders\n"
                    f"📌 {votes['title'][:60]}\n"
                    f"Outcome: {outcome}\n"
                    f"Traders: {len(voters)}/{total} (${total_value:,.0f})\n"
                    f"Top: {names}"
                )
    return alerts


# === WEBSOCKET — Preços Real-Time ===

live_prices = {}

async def ws_price_stream(token_ids: list):
    """Conecta ao websocket e monitora preços em tempo real."""
    import websockets
    
    global live_prices
    
    while True:
        try:
            async with websockets.connect(CLOB_WS) as ws:
                # Subscrever aos mercados
                for token_id in token_ids[:50]:  # Limite de 50
                    sub_msg = json.dumps({
                        "type": "market",
                        "assets_ids": [token_id]
                    })
                    await ws.send(sub_msg)
                
                print(f"  🔌 WebSocket conectado — {len(token_ids[:50])} mercados")
                
                async for message in ws:
                    try:
                        data = json.loads(message)
                        if isinstance(data, list):
                            for item in data:
                                process_ws_price(item)
                        else:
                            process_ws_price(data)
                    except:
                        pass
        
        except Exception as e:
            print(f"  ⚠️ WebSocket desconectado: {e}. Reconectando em 5s...")
            await asyncio.sleep(5)


def process_ws_price(data):
    """Processa update de preço do websocket."""
    global live_prices
    
    asset_id = data.get("asset_id") or data.get("market", "")
    price = data.get("price") or data.get("last_price")
    
    if not asset_id or not price:
        return
    
    price = float(price)
    old_price = live_prices.get(asset_id, {}).get("price")
    
    live_prices[asset_id] = {
        "price": price,
        "updated_at": datetime.now().isoformat()
    }
    
    # Detectar mudança significativa
    if old_price and old_price > 0:
        change = abs(price - old_price) / old_price
        if change >= PRICE_ALERT_THRESHOLD:
            direction = "📈" if price > old_price else "📉"
            log_alert(
                f"{direction} Preço moveu {change*100:.1f}%\n"
                f"Token: {asset_id[:16]}...\n"
                f"${old_price:.3f} → ${price:.3f}"
            )
    
    # Salvar periodicamente
    if len(live_prices) % 10 == 0:
        try:
            PRICES_FILE.write_text(json.dumps(live_prices, indent=2))
        except:
            pass


def start_ws_thread(token_ids):
    """Inicia websocket em thread separada."""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ws_price_stream(token_ids))
    
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t


# === MAIN SCAN (PARALELO) ===

def run_scan(state, verbose=True):
    all_alerts = []
    scan_start = time.time()
    state["scan_count"] = state.get("scan_count", 0) + 1
    
    if verbose:
        print(f"\n{'='*50}")
        print(f"🔍 Scan #{state['scan_count']} — {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Top traders
    wallets = get_tracked_wallets(TOP_TRADERS_LIMIT)
    if not wallets:
        print("  ⚠️ Não conseguiu carregar traders")
        return []
    
    wallets_info = {w["address"]: w for w in wallets}
    wallets_positions = {}
    
    # 2. Fetch paralelo
    if verbose:
        print(f"  Escaneando {len(wallets)} traders (parallel)...", end=" ", flush=True)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_trader_data, w["address"]): w
            for w in wallets
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                wallet = result["wallet"]
                activity = result["activity"]
                positions = result["positions"]
                wallets_positions[wallet] = positions
                
                w_info = wallets_info.get(wallet, {})
                username = w_info.get("username", wallet[:10])
                
                if state.get("last_scan"):
                    all_alerts.extend(detect_new_trades(wallet, username, activity, state))
                    all_alerts.extend(detect_position_changes(wallet, username, positions, state))
                else:
                    if activity:
                        first_id = activity[0].get("id") or activity[0].get("transactionHash", "")
                        state["known_trades"][wallet] = first_id
                    current = {}
                    for pos in positions:
                        cid = pos.get("conditionId", "")
                        outcome = pos.get("outcome", "")
                        key = f"{cid}_{outcome}"
                        current[key] = {
                            "title": pos.get("title", "?"), "outcome": outcome,
                            "size": float(pos.get("size", 0)),
                            "value": float(pos.get("currentValue", 0)),
                            "pnl": float(pos.get("cashPnl", 0))
                        }
                    state["known_positions"][wallet] = current
            except Exception as e:
                pass
    
    # 3. Consenso
    consensus_alerts = detect_consensus(wallets_positions, wallets_info)
    all_alerts.extend(consensus_alerts)
    
    # 4. Salvar
    save_state(state)
    
    elapsed = time.time() - scan_start
    if verbose:
        print(f"✅ {elapsed:.0f}s — {len(all_alerts)} alertas")
    
    return all_alerts


def run_setup():
    print("🔧 Setup inicial...")
    state = load_state()
    run_scan(state, verbose=True)
    print(f"\n✅ Base criada com {len(state.get('known_positions', {}))} traders.")


def run_once():
    state = load_state()
    if not state.get("last_scan"):
        run_setup()
        return
    alerts = run_scan(state, verbose=True)
    if alerts:
        header = f"🔔 Polymarket Monitor — {datetime.now().strftime('%d/%m %H:%M')}\n{'─'*30}\n\n"
        for i in range(0, len(alerts), 5):
            batch = alerts[i:i+5]
            message = header + "\n\n".join(batch)
            send_alert(message)


def run_loop(with_ws=False):
    print(f"🔄 Monitor v2 — scan a cada {POLL_INTERVAL}s | {MAX_WORKERS} threads paralelas")
    if with_ws:
        print(f"  🔌 WebSocket de preços ativado")
    
    state = load_state()
    
    if not state.get("last_scan"):
        print("\nPrimeiro scan — setup...")
        run_scan(state, verbose=True)
        print(f"\nBase criada. Iniciando monitoramento...\n")
        time.sleep(5)
    
    # Iniciar websocket se solicitado
    if with_ws:
        # Coletar token_ids das posições monitoradas
        token_ids = set()
        for wallet, positions in state.get("known_positions", {}).items():
            for key in positions:
                cid = key.split("_")[0]
                token_ids.add(cid)
        if token_ids:
            start_ws_thread(list(token_ids))
    
    while True:
        try:
            alerts = run_scan(state, verbose=True)
            if alerts:
                header = f"🔔 Polymarket Monitor — {datetime.now().strftime('%d/%m %H:%M')}\n{'─'*30}\n\n"
                for i in range(0, len(alerts), 5):
                    batch = alerts[i:i+5]
                    message = header + "\n\n".join(batch)
                    send_alert(message)
                print(f"  📨 {len(alerts)} alertas enviados")
            
            time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n🛑 Monitor parado.")
            save_state(state)
            break
        except Exception as e:
            print(f"\n⚠️ Erro: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if "--setup" in sys.argv:
        run_setup()
    elif "--loop" in sys.argv:
        run_loop(with_ws="--ws" in sys.argv)
    elif "--ws" in sys.argv:
        run_loop(with_ws=True)
    else:
        run_once()

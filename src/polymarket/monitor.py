"""
Módulo MONITOR — Monitora posições e detecta sinais de consenso
Baseado no copy bot do RobotTraders, expandido pra wallet baskets
"""
import requests
import json
import time
from datetime import datetime
from collections import defaultdict
from config import DATA_API, GAMMA_API, MIN_CONSENSUS_PCT, MIN_WALLETS_IN_BASKET, DATA_DIR


def get_positions(wallet_address: str) -> list:
    """Busca posições atuais de uma wallet."""
    response = requests.get(
        f"{DATA_API}/positions",
        params={"user": wallet_address, "sizeThreshold": 0}
    )
    response.raise_for_status()
    return response.json()


def get_latest_buys(wallet_address: str, limit=20) -> list:
    """Busca últimas compras de uma wallet."""
    response = requests.get(
        f"{DATA_API}/activity",
        params={"user": wallet_address, "limit": limit}
    )
    response.raise_for_status()
    return [a for a in response.json() if a.get("type") == "TRADE" and a.get("side") == "BUY"]


def load_baskets(filepath=None) -> dict:
    """Carrega wallet baskets do arquivo."""
    if filepath is None:
        filepath = DATA_DIR / "wallet_baskets.json"
    
    if not filepath.exists():
        print("⚠️ wallet_baskets.json não encontrado. Rode o scorer primeiro.")
        return {}
    
    with open(filepath) as f:
        return json.load(f)


def scan_basket_consensus(basket_name: str, wallets: list) -> list:
    """
    Escaneia um basket e detecta consenso.
    Retorna sinais quando 80%+ das wallets têm a mesma posição.
    """
    # Coleta posições de todas as wallets do basket
    all_positions = {}
    for wallet in wallets:
        addr = wallet["address"]
        try:
            positions = get_positions(addr)
            all_positions[addr] = positions
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Erro {addr[:10]}: {e}")
    
    # Agrupa por mercado (conditionId + outcome)
    market_votes = defaultdict(lambda: {"YES": set(), "NO": set(), "title": "", "token_id": ""})
    
    for addr, positions in all_positions.items():
        for pos in positions:
            condition_id = pos.get("conditionId", "")
            outcome = pos.get("outcome", "")
            title = pos.get("title", "")
            token_id = pos.get("asset", "")
            
            if outcome in ("Yes", "YES"):
                market_votes[condition_id]["YES"].add(addr)
            elif outcome in ("No", "NO"):
                market_votes[condition_id]["NO"].add(addr)
            
            market_votes[condition_id]["title"] = title
            market_votes[condition_id]["token_id"] = token_id
    
    # Detecta consenso
    signals = []
    total_wallets = len(wallets)
    
    for condition_id, votes in market_votes.items():
        for outcome in ["YES", "NO"]:
            voters = votes[outcome]
            if len(voters) < MIN_WALLETS_IN_BASKET:
                continue
            
            consensus_pct = len(voters) / total_wallets
            
            if consensus_pct >= MIN_CONSENSUS_PCT:
                signals.append({
                    "basket": basket_name,
                    "condition_id": condition_id,
                    "market_title": votes["title"],
                    "outcome": outcome,
                    "consensus_pct": round(consensus_pct, 2),
                    "wallets_in": len(voters),
                    "wallets_total": total_wallets,
                    "wallet_addresses": list(voters),
                    "token_id": votes["token_id"],
                    "detected_at": datetime.now().isoformat()
                })
    
    return signals


def scan_all_baskets() -> list:
    """Escaneia todos os baskets e retorna sinais."""
    baskets = load_baskets()
    if not baskets:
        return []
    
    all_signals = []
    
    for basket_name, basket_data in baskets.items():
        wallets = basket_data.get("wallets", [])
        print(f"\n  Escaneando basket '{basket_name}' ({len(wallets)} wallets)...")
        
        signals = scan_basket_consensus(basket_name, wallets)
        all_signals.extend(signals)
        
        if signals:
            for s in signals:
                print(f"  🎯 SINAL: {s['market_title'][:50]}")
                print(f"     {s['outcome']} — {s['consensus_pct']*100:.0f}% consenso ({s['wallets_in']}/{s['wallets_total']})")
        else:
            print(f"  Nenhum consenso detectado")
    
    return all_signals


def save_signals(signals: list):
    """Salva sinais detectados."""
    if not signals:
        return
    
    signals_dir = DATA_DIR / "signals"
    signals_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = signals_dir / f"signals-{today}.json"
    
    # Append se já existe
    existing = []
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)
    
    existing.extend(signals)
    
    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2)
    
    print(f"\n✅ {len(signals)} sinais salvos: {filepath}")


def main():
    print("=" * 50)
    print("🔍 Polymarket Copy Trading — Monitor")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    signals = scan_all_baskets()
    save_signals(signals)
    
    return signals


if __name__ == "__main__":
    main()

"""
Módulo COLETOR — Coleta leaderboard e posições dos top traders
Usa apenas APIs públicas (sem auth)
"""
import requests
import json
import time
from datetime import datetime
from pathlib import Path
from config import DATA_API, GAMMA_API, DATA_DIR


def get_leaderboard(category="OVERALL", period="ALL", limit=50) -> list:
    """Busca top traders do leaderboard."""
    response = requests.get(
        f"{DATA_API}/v1/leaderboard",
        params={
            "category": category,
            "timePeriod": period,
            "orderBy": "PNL",
            "limit": limit,
            "offset": 0
        }
    )
    response.raise_for_status()
    return response.json()


def get_profile(wallet_address: str) -> dict:
    """Busca perfil público de uma wallet."""
    response = requests.get(
        f"{GAMMA_API}/public-profile",
        params={"address": wallet_address}
    )
    response.raise_for_status()
    return response.json()


def get_positions(wallet_address: str) -> list:
    """Busca posições atuais de uma wallet."""
    response = requests.get(
        f"{DATA_API}/positions",
        params={"user": wallet_address, "sizeThreshold": 0}
    )
    response.raise_for_status()
    return response.json()


def get_activity(wallet_address: str, limit=20) -> list:
    """Busca atividade recente de uma wallet."""
    response = requests.get(
        f"{DATA_API}/activity",
        params={"user": wallet_address, "limit": limit}
    )
    response.raise_for_status()
    return response.json()


def collect_all_leaderboards() -> dict:
    """Coleta leaderboards de todas as categorias relevantes."""
    categories = ["OVERALL", "POLITICS", "CRYPTO", "SPORTS", "ECONOMICS", "FINANCE"]
    periods = ["MONTH", "ALL"]
    
    all_traders = {}
    
    for cat in categories:
        for period in periods:
            print(f"  Coletando {cat}/{period}...")
            try:
                data = get_leaderboard(cat, period, limit=50)
                for trader in data:
                    addr = trader.get("proxyWallet") or trader.get("userAddress") or trader.get("address", "")
                    if not addr:
                        continue
                    if addr not in all_traders:
                        all_traders[addr] = {
                            "address": addr,
                            "username": trader.get("userName") or trader.get("username") or trader.get("name", ""),
                            "pnl": float(trader.get("pnl", 0)),
                            "volume": float(trader.get("vol") or trader.get("volume", 0)),
                            "categories": set(),
                            "leaderboard_appearances": 0
                        }
                    all_traders[addr]["categories"].add(cat)
                    all_traders[addr]["leaderboard_appearances"] += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  ⚠️ Erro {cat}/{period}: {e}")
    
    # Convert sets to lists for JSON serialization
    for addr in all_traders:
        all_traders[addr]["categories"] = list(all_traders[addr]["categories"])
    
    return all_traders


def collect_positions_for_traders(traders: dict, max_traders=30) -> dict:
    """Coleta posições atuais dos top traders."""
    positions = {}
    sorted_traders = sorted(traders.values(), key=lambda x: x["pnl"], reverse=True)[:max_traders]
    
    for i, trader in enumerate(sorted_traders):
        addr = trader["address"]
        print(f"  [{i+1}/{len(sorted_traders)}] Posições de {trader.get('username', addr[:10])}...")
        try:
            pos = get_positions(addr)
            if pos:
                positions[addr] = pos
            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")
    
    return positions


def save_snapshot(traders: dict, positions: dict):
    """Salva snapshot diário."""
    today = datetime.now().strftime("%Y-%m-%d")
    snapshot_dir = DATA_DIR / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot = {
        "date": today,
        "collected_at": datetime.now().isoformat(),
        "total_traders": len(traders),
        "traders_with_positions": len(positions),
        "traders": traders,
        "positions": positions
    }
    
    filepath = snapshot_dir / f"snapshot-{today}.json"
    with open(filepath, "w") as f:
        json.dump(snapshot, f, indent=2, default=str)
    
    print(f"\n✅ Snapshot salvo: {filepath}")
    print(f"   {len(traders)} traders | {len(positions)} com posições")
    return filepath


def main():
    print("=" * 50)
    print("📊 Polymarket Copy Trading — Coletor")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n[1] Coletando leaderboards...")
    traders = collect_all_leaderboards()
    print(f"   Total: {len(traders)} traders únicos")
    
    print("\n[2] Coletando posições dos top traders...")
    positions = collect_positions_for_traders(traders)
    
    print("\n[3] Salvando snapshot...")
    filepath = save_snapshot(traders, positions)
    
    return traders, positions


if __name__ == "__main__":
    main()

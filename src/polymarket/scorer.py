"""
Módulo SCORER — Analisa traders e monta wallet baskets
"""
import json
import time
import requests
from datetime import datetime
from config import DATA_API, GAMMA_API, MIN_TRADES, DATA_DIR


def load_latest_snapshot() -> dict:
    """Carrega o snapshot mais recente."""
    snapshot_dir = DATA_DIR / "snapshots"
    if not snapshot_dir.exists():
        print("⚠️ Nenhum snapshot encontrado. Rode o collector primeiro.")
        return {}
    
    snapshots = sorted(snapshot_dir.glob("snapshot-*.json"), reverse=True)
    if not snapshots:
        return {}
    
    with open(snapshots[0]) as f:
        return json.load(f)


def score_trader(trader: dict) -> float:
    """
    Calcula score de um trader baseado em:
    - PnL total (25%)
    - Nº de aparições no leaderboard (25%) — proxy pra consistência
    - Nº de categorias (15%) — diversificação
    - Volume (15%)
    - PnL normalizado (20%)
    """
    pnl = float(trader.get("pnl", 0))
    appearances = trader.get("leaderboard_appearances", 0)
    categories = len(trader.get("categories", []))
    volume = float(trader.get("volume", 0))
    
    # Normalize scores (0-1)
    pnl_score = min(pnl / 1_000_000, 1.0) if pnl > 0 else 0
    appearances_score = min(appearances / 10, 1.0)
    categories_score = min(categories / 5, 1.0)
    volume_score = min(volume / 10_000_000, 1.0) if volume > 0 else 0
    
    score = (
        pnl_score * 0.30 +
        appearances_score * 0.25 +
        categories_score * 0.15 +
        volume_score * 0.30
    )
    
    return round(score, 4)


def build_baskets(traders: dict, top_n_per_basket=10) -> dict:
    """
    Monta wallet baskets temáticos.
    Cada basket contém as top wallets especializadas naquela categoria.
    """
    # Score all traders
    scored = []
    for addr, trader in traders.items():
        trader["score"] = score_trader(trader)
        trader["address"] = addr
        scored.append(trader)
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Build category baskets
    categories = ["POLITICS", "CRYPTO", "SPORTS", "ECONOMICS", "FINANCE"]
    baskets = {}
    
    for cat in categories:
        # Filter traders that appear in this category's leaderboard
        cat_traders = [t for t in scored if cat in t.get("categories", [])]
        top = cat_traders[:top_n_per_basket]
        
        if len(top) >= 3:  # Minimum 3 wallets per basket
            baskets[cat.lower()] = {
                "category": cat,
                "wallets": [
                    {
                        "address": t["address"],
                        "username": t.get("username", ""),
                        "score": t["score"],
                        "pnl": t.get("pnl", 0)
                    }
                    for t in top
                ],
                "updated_at": datetime.now().isoformat()
            }
            print(f"  Basket '{cat}': {len(top)} wallets (top score: {top[0]['score']:.4f})")
        else:
            print(f"  Basket '{cat}': insuficiente ({len(top)} wallets)")
    
    # Also build an OVERALL basket with the absolute best
    overall_top = scored[:top_n_per_basket]
    if overall_top:
        baskets["overall"] = {
            "category": "OVERALL",
            "wallets": [
                {
                    "address": t["address"],
                    "username": t.get("username", ""),
                    "score": t["score"],
                    "pnl": t.get("pnl", 0)
                }
                for t in overall_top
            ],
            "updated_at": datetime.now().isoformat()
        }
        print(f"  Basket 'OVERALL': {len(overall_top)} wallets (top score: {overall_top[0]['score']:.4f})")
    
    return baskets


def save_baskets(baskets: dict):
    """Salva baskets em arquivo."""
    filepath = DATA_DIR / "wallet_baskets.json"
    with open(filepath, "w") as f:
        json.dump(baskets, f, indent=2)
    
    total_wallets = sum(len(b["wallets"]) for b in baskets.values())
    print(f"\n✅ Baskets salvos: {filepath}")
    print(f"   {len(baskets)} baskets | {total_wallets} wallets total")


def main():
    print("=" * 50)
    print("🏆 Polymarket Copy Trading — Scorer")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n[1] Carregando snapshot...")
    snapshot = load_latest_snapshot()
    if not snapshot:
        return
    
    traders = snapshot.get("traders", {})
    print(f"   {len(traders)} traders no snapshot")
    
    print("\n[2] Montando baskets...")
    baskets = build_baskets(traders)
    
    print("\n[3] Salvando...")
    save_baskets(baskets)
    
    return baskets


if __name__ == "__main__":
    main()

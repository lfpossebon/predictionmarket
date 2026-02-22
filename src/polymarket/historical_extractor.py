"""
📊 Polymarket Historical Data Extractor
Coleta histórico completo de traders para análise de padrões comportamentais.

Uso:
  cd ~/clawd/src/polymarket
  python historical_extractor.py          # Extração completa
  python historical_extractor.py --test   # Teste com 5 traders
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# APIs
DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "polymarket" / "historical"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["OVERALL", "POLITICS", "CRYPTO", "SPORTS", "ECONOMICS", "FINANCE", "CULTURE"]
PERIODS = ["ALL", "MONTH", "WEEK", "DAY"]


def api_get(url, params=None, retries=3):
    """GET com retry e backoff exponencial."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 429:
                wait = (2 ** attempt) * 2
                print(f"    ⏳ Rate limited, aguardando {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code >= 500:
                wait = (2 ** attempt) * 1
                print(f"    ⚠️ Server error {r.status_code}, retry em {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            print(f"    ⏳ Timeout, retry {attempt+1}/{retries}...")
            time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                print(f"    ✗ Erro definitivo: {e}")
                return None
            time.sleep(2 ** attempt)
    return None


# ============================================================
# 1. COLETA DE TRADERS
# ============================================================

def collect_all_traders(limit_per_query=50):
    """Coleta traders únicos de todos os leaderboards."""
    print("\n[1/4] 🏆 Coletando leaderboards...")
    traders = {}
    
    for cat in CATEGORIES:
        for period in PERIODS:
            print(f"  {cat}/{period}...", end=" ", flush=True)
            data = api_get(f"{DATA_API}/v1/leaderboard", {
                "category": cat, "timePeriod": period,
                "orderBy": "PNL", "limit": limit_per_query, "offset": 0
            })
            if not data:
                print("✗")
                continue
            
            count = 0
            for t in data:
                addr = t.get("proxyWallet") or t.get("userAddress") or t.get("address", "")
                if not addr:
                    continue
                if addr not in traders:
                    traders[addr] = {
                        "address": addr,
                        "username": t.get("userName") or t.get("username") or t.get("name", ""),
                        "pnl": float(t.get("pnl", 0)),
                        "volume": float(t.get("vol") or t.get("volume", 0)),
                        "markets_traded": int(t.get("marketsTraded", 0)),
                        "num_trades": int(t.get("numTrades", 0)),
                        "categories": set(),
                        "periods": set(),
                        "ranks": {}
                    }
                traders[addr]["categories"].add(cat)
                traders[addr]["periods"].add(period)
                traders[addr]["ranks"][f"{cat}/{period}"] = count + 1
                # Atualizar PnL se maior
                pnl = float(t.get("pnl", 0))
                if pnl > traders[addr]["pnl"]:
                    traders[addr]["pnl"] = pnl
                count += 1
            
            print(f"✓ ({count})")
            time.sleep(0.3)
    
    # Converter sets pra lists
    for addr in traders:
        traders[addr]["categories"] = sorted(traders[addr]["categories"])
        traders[addr]["periods"] = sorted(traders[addr]["periods"])
    
    print(f"\n  → {len(traders)} traders únicos encontrados")
    return traders


# ============================================================
# 2. HISTÓRICO DE TRADES POR TRADER
# ============================================================

def collect_trader_activity(wallet: str, max_pages=50) -> list:
    """Coleta todo o histórico de trades de um trader com paginação."""
    all_trades = []
    offset = 0
    page_size = 100
    
    for page in range(max_pages):
        data = api_get(f"{DATA_API}/activity", {
            "user": wallet, "limit": page_size, "offset": offset
        })
        
        if not data or len(data) == 0:
            break
        
        all_trades.extend(data)
        offset += page_size
        
        if len(data) < page_size:
            break  # Última página
        
        time.sleep(0.3)
    
    return all_trades


# ============================================================
# 3. POSIÇÕES ATUAIS
# ============================================================

def collect_trader_positions(wallet: str) -> list:
    """Coleta posições atuais de um trader."""
    data = api_get(f"{DATA_API}/positions", {
        "user": wallet, "sizeThreshold": 0
    })
    return data if data else []


# ============================================================
# 4. PERFIL
# ============================================================

def collect_trader_profile(wallet: str) -> dict:
    """Coleta perfil público de um trader."""
    data = api_get(f"{GAMMA_API}/public-profile", {"address": wallet})
    return data if data else {}


# ============================================================
# SALVAMENTO
# ============================================================

def save_trader_data(wallet: str, trader_info: dict, trades: list, positions: list, profile: dict):
    """Salva dados de um trader individual."""
    trader_dir = DATA_DIR / "traders"
    trader_dir.mkdir(exist_ok=True)
    
    filename = trader_info.get("username", wallet[:16]).replace("/", "_").replace(" ", "_")
    if not filename or filename == "":
        filename = wallet[:16]
    
    data = {
        "wallet": wallet,
        "info": trader_info,
        "profile": profile,
        "trades_count": len(trades),
        "positions_count": len(positions),
        "trades": trades,
        "positions": positions,
        "extracted_at": datetime.now().isoformat()
    }
    
    filepath = trader_dir / f"{filename}_{wallet[:8]}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath


def save_summary(traders: dict, stats: dict):
    """Salva relatório resumo."""
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "total_traders": stats["total_traders"],
        "traders_with_trades": stats["traders_with_trades"],
        "total_trades": stats["total_trades"],
        "total_positions": stats["total_positions"],
        "date_range": stats.get("date_range", {}),
        "category_distribution": stats.get("category_dist", {}),
        "top_10_pnl": stats.get("top_10", []),
        "top_10_by_trades": stats.get("top_10_trades", []),
        "errors": stats.get("errors", [])
    }
    
    filepath = DATA_DIR / "extraction_summary.json"
    with open(filepath, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Também salvar índice de traders (leve, sem trades)
    index = []
    for addr, info in traders.items():
        index.append({
            "wallet": addr,
            "username": info.get("username", ""),
            "pnl": info.get("pnl", 0),
            "volume": info.get("volume", 0),
            "categories": info.get("categories", []),
            "periods": info.get("periods", []),
            "trades_collected": info.get("trades_collected", 0),
            "positions_collected": info.get("positions_collected", 0)
        })
    
    index.sort(key=lambda x: x["pnl"], reverse=True)
    
    index_path = DATA_DIR / "traders_index.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    
    return filepath, index_path


# ============================================================
# MAIN
# ============================================================

def run_extraction(test_mode=False):
    """Executa extração completa."""
    start = time.time()
    
    print("=" * 60)
    print("📊 Polymarket Historical Extractor")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Modo: {'TESTE (5 traders)' if test_mode else 'COMPLETO'}")
    print(f"   Output: {DATA_DIR}")
    print("=" * 60)
    
    # 1. Coletar traders
    traders = collect_all_traders()
    
    if not traders:
        print("❌ Nenhum trader encontrado. Abortando.")
        return
    
    # Salvar lista de traders
    traders_list_path = DATA_DIR / "traders_list.json"
    traders_serializable = {k: {**v} for k, v in traders.items()}
    with open(traders_list_path, "w") as f:
        json.dump(traders_serializable, f, indent=2, default=str)
    print(f"  💾 Lista salva: {traders_list_path}")
    
    # Ordenar por PnL (top primeiro)
    sorted_wallets = sorted(traders.keys(), key=lambda w: traders[w]["pnl"], reverse=True)
    
    if test_mode:
        sorted_wallets = sorted_wallets[:5]
        print(f"\n🧪 Modo teste: processando apenas {len(sorted_wallets)} traders")
    
    # 2-4. Coletar dados por trader
    print(f"\n[2/4] 📥 Coletando histórico de {len(sorted_wallets)} traders...")
    
    stats = {
        "total_traders": len(sorted_wallets),
        "traders_with_trades": 0,
        "total_trades": 0,
        "total_positions": 0,
        "all_dates": [],
        "errors": []
    }
    
    for i, wallet in enumerate(sorted_wallets):
        info = traders[wallet]
        username = info.get("username", wallet[:10])
        
        if (i + 1) % 10 == 0 or i == 0 or test_mode:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed * 60 if elapsed > 0 else 0
            print(f"\n  [{i+1}/{len(sorted_wallets)}] {username} (PnL: ${info['pnl']:,.0f}) — {rate:.0f} traders/min")
        
        try:
            # Trades
            trades = collect_trader_activity(wallet)
            time.sleep(0.3)
            
            # Posições
            positions = collect_trader_positions(wallet)
            time.sleep(0.3)
            
            # Perfil
            profile = collect_trader_profile(wallet)
            time.sleep(0.3)
            
            # Atualizar info
            info["trades_collected"] = len(trades)
            info["positions_collected"] = len(positions)
            
            # Stats
            if trades:
                stats["traders_with_trades"] += 1
                stats["total_trades"] += len(trades)
                # Extrair datas
                for t in trades:
                    ts = t.get("timestamp") or t.get("createdAt") or t.get("date", "")
                    if ts:
                        stats["all_dates"].append(str(ts)[:10])
            
            stats["total_positions"] += len(positions)
            
            # Salvar incrementalmente
            save_trader_data(wallet, info, trades, positions, profile)
            
            if test_mode:
                print(f"    → {len(trades)} trades, {len(positions)} posições")
        
        except Exception as e:
            err_msg = f"{username} ({wallet[:10]}): {e}"
            stats["errors"].append(err_msg)
            print(f"    ⚠️ Erro: {e}")
    
    # Gerar stats finais
    print("\n[3/4] 📊 Gerando relatório...")
    
    if stats["all_dates"]:
        dates_sorted = sorted(set(stats["all_dates"]))
        stats["date_range"] = {"min": dates_sorted[0], "max": dates_sorted[-1]}
    
    # Distribuição por categoria
    cat_counter = Counter()
    for w in sorted_wallets:
        for cat in traders[w].get("categories", []):
            cat_counter[cat] += 1
    stats["category_dist"] = dict(cat_counter.most_common())
    
    # Top 10 por PnL
    stats["top_10"] = [
        {"username": traders[w].get("username", w[:10]), "pnl": traders[w]["pnl"],
         "trades": traders[w].get("trades_collected", 0)}
        for w in sorted_wallets[:10]
    ]
    
    # Top 10 por volume de trades
    by_trades = sorted(sorted_wallets, key=lambda w: traders[w].get("trades_collected", 0), reverse=True)
    stats["top_10_trades"] = [
        {"username": traders[w].get("username", w[:10]), "trades": traders[w].get("trades_collected", 0),
         "pnl": traders[w]["pnl"]}
        for w in by_trades[:10]
    ]
    
    del stats["all_dates"]  # Não precisa no summary
    
    print("\n[4/4] 💾 Salvando summary...")
    summary_path, index_path = save_summary(traders, stats)
    
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print(f"   Tempo: {elapsed/60:.1f} minutos")
    print(f"   Traders: {stats['total_traders']}")
    print(f"   Com trades: {stats['traders_with_trades']}")
    print(f"   Total trades: {stats['total_trades']:,}")
    print(f"   Total posições: {stats['total_positions']:,}")
    if stats.get("date_range"):
        print(f"   Range: {stats['date_range']['min']} → {stats['date_range']['max']}")
    print(f"   Erros: {len(stats['errors'])}")
    print(f"\n   📁 Dados: {DATA_DIR}")
    print(f"   📋 Summary: {summary_path}")
    print(f"   📇 Índice: {index_path}")
    print("=" * 60)


if __name__ == "__main__":
    test = "--test" in sys.argv
    run_extraction(test_mode=test)

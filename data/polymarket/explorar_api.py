"""
🔍 Polymarket API Explorer — Script básico pra explorar a API
Roda: python explorar_api.py
Ou importa as funções no Jupyter/IPython

APIs públicas (sem autenticação):
- Data API: https://data-api.polymarket.com
- Gamma API: https://gamma-api.polymarket.com
- CLOB API: https://clob.polymarket.com
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime

# === ENDPOINTS ===
DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


# ============================================================
# 1. MERCADOS — Listar mercados ativos
# ============================================================

def get_markets(limit=100, offset=0, active=True, closed=False) -> pd.DataFrame:
    """Lista mercados do Polymarket via Gamma API."""
    params = {
        "limit": limit,
        "offset": offset,
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "order": "volume24hr",
        "ascending": "false"
    }
    r = requests.get(f"{GAMMA_API}/markets", params=params)
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Converter colunas numéricas
    for col in ['volume', 'volume24hr', 'liquidity']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def get_market_detail(condition_id: str) -> dict:
    """Detalhe de um mercado específico."""
    r = requests.get(f"{GAMMA_API}/markets/{condition_id}")
    r.raise_for_status()
    return r.json()


# ============================================================
# 2. LEADERBOARD — Top traders
# ============================================================

def get_leaderboard(category="OVERALL", period="ALL", limit=50) -> pd.DataFrame:
    """
    Busca leaderboard.
    Categorias: OVERALL, POLITICS, CRYPTO, SPORTS, ECONOMICS, FINANCE, SCIENCE, CULTURE
    Períodos: ALL, MONTH, WEEK, DAY
    """
    r = requests.get(f"{DATA_API}/v1/leaderboard", params={
        "category": category,
        "timePeriod": period,
        "orderBy": "PNL",
        "limit": limit,
        "offset": 0
    })
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    for col in ['pnl', 'vol', 'marketsTraded', 'numTrades']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def get_all_leaderboards(limit=50) -> pd.DataFrame:
    """Coleta leaderboards de todas as categorias e períodos. Retorna DataFrame consolidado."""
    categories = ["OVERALL", "POLITICS", "CRYPTO", "SPORTS", "ECONOMICS", "FINANCE"]
    periods = ["ALL", "MONTH", "WEEK", "DAY"]
    
    frames = []
    for cat in categories:
        for period in periods:
            print(f"  {cat}/{period}...", end=" ")
            try:
                df = get_leaderboard(cat, period, limit)
                df["_category"] = cat
                df["_period"] = period
                frames.append(df)
                print(f"✓ ({len(df)} traders)")
                time.sleep(0.3)
            except Exception as e:
                print(f"✗ ({e})")
    
    if not frames:
        return pd.DataFrame()
    
    all_df = pd.concat(frames, ignore_index=True)
    print(f"\nTotal: {len(all_df)} linhas, {all_df['proxyWallet'].nunique() if 'proxyWallet' in all_df.columns else '?'} traders únicos")
    return all_df


# ============================================================
# 3. POSIÇÕES e ATIVIDADE de um trader
# ============================================================

def get_positions(wallet: str) -> pd.DataFrame:
    """Posições atuais de uma wallet."""
    r = requests.get(f"{DATA_API}/positions", params={
        "user": wallet, "sizeThreshold": 0
    })
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    for col in ['currentValue', 'initialValue', 'cashPnl', 'percentPnl', 'size']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def get_activity(wallet: str, limit=50) -> pd.DataFrame:
    """Trades recentes de uma wallet."""
    r = requests.get(f"{DATA_API}/activity", params={
        "user": wallet, "limit": limit
    })
    r.raise_for_status()
    data = r.json()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def get_profile(wallet: str) -> dict:
    """Perfil público de uma wallet."""
    r = requests.get(f"{GAMMA_API}/public-profile", params={"address": wallet})
    r.raise_for_status()
    return r.json()


# ============================================================
# 4. PREÇOS — Histórico de preço de um token
# ============================================================

def get_price_history(token_id: str, fidelity=60) -> pd.DataFrame:
    """
    Histórico de preços de um token.
    fidelity: resolução em minutos (1, 5, 60, 1440)
    """
    r = requests.get(f"{CLOB_API}/prices-history", params={
        "market": token_id, "interval": "max", "fidelity": fidelity
    })
    r.raise_for_status()
    data = r.json()
    if not data or "history" not in data:
        return pd.DataFrame()
    df = pd.DataFrame(data["history"])
    if 't' in df.columns:
        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
    if 'p' in df.columns:
        df['price'] = pd.to_numeric(df['p'], errors='coerce')
    return df


# ============================================================
# 5. ORDERBOOK — Book de ofertas de um token
# ============================================================

def get_orderbook(token_id: str) -> dict:
    """Orderbook atual de um token."""
    r = requests.get(f"{CLOB_API}/book", params={"token_id": token_id})
    r.raise_for_status()
    return r.json()


# ============================================================
# DEMO — Roda tudo e mostra
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Polymarket API Explorer")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. Mercados mais ativos
    print("\n📈 TOP 10 MERCADOS POR VOLUME 24H:")
    markets = get_markets(limit=10)
    if not markets.empty:
        cols = ['question', 'volume24hr', 'liquidity', 'active', 'closed']
        cols = [c for c in cols if c in markets.columns]
        print(markets[cols].to_string(index=False))
        print(f"\n  → {len(markets)} mercados carregados")
    
    # 2. Top traders
    print("\n🏆 TOP 10 TRADERS (ALL TIME):")
    leaders = get_leaderboard("OVERALL", "ALL", limit=10)
    if not leaders.empty:
        cols = ['userName', 'pnl', 'vol', 'marketsTraded']
        cols = [c for c in cols if c in leaders.columns]
        print(leaders[cols].to_string(index=False))
    
    # 3. Posições do #1
    if not leaders.empty:
        top_wallet = leaders.iloc[0].get('proxyWallet') or leaders.iloc[0].get('userAddress', '')
        top_name = leaders.iloc[0].get('userName', top_wallet[:10])
        if top_wallet:
            print(f"\n💼 POSIÇÕES DE {top_name}:")
            positions = get_positions(top_wallet)
            if not positions.empty:
                cols = ['title', 'currentValue', 'cashPnl', 'percentPnl']
                cols = [c for c in cols if c in positions.columns]
                print(positions[cols].head(10).to_string(index=False))
                print(f"  → {len(positions)} posições totais")
            else:
                print("  Nenhuma posição aberta")

    # 4. Exemplo de histórico de preço
    if not markets.empty and 'clobTokenIds' in markets.columns:
        try:
            token_ids = json.loads(markets.iloc[0]['clobTokenIds'])
            if token_ids:
                token = token_ids[0]
                print(f"\n📊 HISTÓRICO DE PREÇO (mercado: {markets.iloc[0].get('question', '')[:50]}...):")
                prices = get_price_history(token, fidelity=1440)
                if not prices.empty:
                    print(f"  {len(prices)} pontos de dados")
                    print(f"  Último preço: {prices.iloc[-1].get('price', 'N/A')}")
                    print(f"  Range: {prices['price'].min():.3f} — {prices['price'].max():.3f}")
        except Exception as e:
            print(f"  ⚠️ Erro no histórico: {e}")

    print("\n" + "=" * 60)
    print("✅ Pronto! Importa as funções no Jupyter:")
    print("   from explorar_api import *")
    print("   markets = get_markets(100)")
    print("   leaders = get_leaderboard('POLITICS', 'MONTH')")
    print("   positions = get_positions('0x...')")
    print("=" * 60)

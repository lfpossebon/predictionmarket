"""Polymarket Copy Trading - Configuração"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

# APIs
DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Trading (Fase 2 - não usar ainda)
PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
FUNDER_ADDRESS = os.getenv("POLYMARKET_FUNDER_ADDRESS", "")
SIGNATURE_TYPE = int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "1"))

# Copy Trading
BET_AMOUNT = float(os.getenv("POLYMARKET_BET_AMOUNT", "5.0"))
DRY_RUN = True  # SEMPRE dry run até validar

# Estratégia
MIN_CONSENSUS_PCT = 0.80  # 80% das wallets do basket devem concordar
MAX_POSITION_PCT = 0.10   # Máximo 10% do capital por trade
MAX_CORRELATED_PCT = 0.40 # Máximo 40% em eventos correlacionados
MIN_LIQUIDITY_24H = 50000 # Volume mínimo 24h
MAX_PRICE_DRIFT = 0.10    # Não entrar se preço moveu >10%
MIN_TRADES = 100           # Mínimo de trades pra considerar wallet
MIN_WALLETS_IN_BASKET = 5

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "polymarket"
DATA_DIR.mkdir(parents=True, exist_ok=True)

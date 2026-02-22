# 🎲 Prediction Market — Multi-Strategy Trading System

Sistema de trading multi-estratégia para mercados de previsão (Polymarket), combinando Data Science e automação.

---

## 📋 Visão Geral

Framework de **5 estratégias complementares** com uma **meta-estratégia (Blend)** que aloca capital dinamicamente entre elas.

| # | Estratégia | Horizonte | Ideia Central |
|---|-----------|-----------|---------------|
| S1 | **Copy Trading** | Médio prazo | Seguir basket de top traders quando há consenso |
| S2 | **Early Value** | Longo prazo | Identificar mercados subprecificados |
| S3 | **Momentum** | Curto prazo | Surfar movimentos rápidos pré/pós eventos |
| S4 | **Mean Reversion** | Curto prazo | Apostar contra overreactions |
| S5 | **Arbitragem** | Variável | Explorar inconsistências entre mercados correlacionados |

**Meta-estratégia:** Alocação dinâmica via Risk Parity, Markowitz, Kelly Criterion ou Bandit Learning.

---

## 📂 Estrutura do Projeto

```
src/polymarket/
├── config.py                # Configurações e endpoints
├── collector.py             # Coleta de leaderboards e posições
├── historical_extractor.py  # Extração histórica completa de traders
├── monitor.py               # Monitoramento real-time de posições
├── scorer.py                # Scoring e seleção de basket
└── alerts.py                # Alertas via Telegram

data/polymarket/
├── POLYMARKET-PROJETO-COMPLETO.md    # Documentação completa do projeto
├── POLYMARKET-BENCHMARK-ESTRATEGIAS.md  # Benchmark de 8 estratégias
├── explorar_api.py          # Script para exploração interativa da API
├── polymarket_eda.ipynb     # Notebook de EDA
├── explorer2.html           # Dashboard de traders (com sistema de basket)
├── plano.html               # Plano visual do projeto
├── benchmark.html           # Dashboard de benchmarks
└── *.json                   # Dados de EDA e benchmarks
```

---

## 🚀 Como Usar

### Explorar a API
```python
from data.polymarket.explorar_api import *

# Mercados mais ativos
markets = get_markets(100)

# Top traders por categoria
leaders = get_leaderboard("POLITICS", "MONTH")

# Posições de um trader
positions = get_positions("0x...")

# Histórico de preço
prices = get_price_history(token_id)
```

### Coletar Dados
```bash
# Snapshot do leaderboard
cd src/polymarket
python3 collector.py

# Extração histórica completa (891+ traders)
python3 historical_extractor.py

# Teste com 5 traders
python3 historical_extractor.py --test
```

### Dashboards
Servir localmente e acessar no browser:
```bash
cd data/polymarket
python3 -m http.server 8899
```
- **Explorer:** http://localhost:8899/explorer2.html
- **Plano:** http://localhost:8899/plano.html
- **Benchmark:** http://localhost:8899/benchmark.html

---

## 📊 Dados

- **891+ traders** coletados de 7 categorias × 4 períodos
- **APIs públicas** do Polymarket (sem autenticação):
  - Data API: `https://data-api.polymarket.com`
  - Gamma API: `https://gamma-api.polymarket.com`
  - CLOB API: `https://clob.polymarket.com`

---

## 🔬 Pipeline de Data Science

| Notebook | Escopo |
|----------|--------|
| 1 | Coleta e EDA |
| 2 | Análise por Tema/Categoria |
| 3 | Detecção de Sybils |
| 4 | Feature Engineering (35+ features) |
| 5 | Modelo S1 — Copy Trading |
| 6 | Modelo S2 — Early Value |
| 7 | Modelo S3 — Momentum |
| 8 | Modelo S4 — Mean Reversion |
| 9 | Modelo S5 — Arbitragem |
| 10 | Meta-Estratégia (Blend) |
| 11 | Backtest Integrado |

---

## 🛠️ Stack

- **Python** — pandas, requests, XGBoost/LightGBM, scikit-learn
- **Jupyter** — notebooks de análise
- **HTML/JS** — dashboards interativos
- **Polymarket APIs** — dados públicos

---

## 📈 Referências

O benchmark (`POLYMARKET-BENCHMARK-ESTRATEGIAS.md`) compila dados de:
- 5 papers acadêmicos (arXiv, SSRN, UCD, ScienceDirect)
- 6 análises de mercado (Medium, newsletters)
- Ferramentas: Polymarket Analytics, BetMoar, Calibration City

**Dado chave:** 92% dos traders perdem dinheiro no Polymarket. Um sistema disciplinado e baseado em dados já começa com vantagem sobre o participante médio.

---

*Projeto em desenvolvimento — 2026*

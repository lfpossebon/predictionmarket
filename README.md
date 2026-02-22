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
├── POLYMARKET-PROJETO-COMPLETO.md       # Documentação completa do projeto
├── POLYMARKET-BENCHMARK-ESTRATEGIAS.md  # Benchmark de 8 estratégias
├── TRADER-COHORTS-ANALYSIS.md           # 🧬 Análise de safras de traders
├── explorar_api.py              # Script para exploração interativa da API
├── consolidate_lite.py          # Gera JSON consolidado para dashboards
├── consolidate_historical.py    # Gera JSON completo (401MB, uso offline)
│
├── polymarket_eda.ipynb         # 📓 Notebook 1: EDA inicial
├── historical_analysis.ipynb    # 📓 Notebook 2: Análise histórica de traders  
├── trader_cohorts_analysis.ipynb # 📓 Notebook 3: Análise de safras (pré/pós Trump)
│
├── explorer2.html               # 📊 Dashboard: traders + sistema de basket
├── monitor_dashboard.html       # 📊 Dashboard: monitor real-time + alertas
├── historical_dashboard.html    # 📊 Dashboard: análise histórica interativa
├── plano.html                   # 📊 Dashboard: plano visual do projeto
├── benchmark.html               # 📊 Dashboard: benchmark de estratégias
│
├── historical/                  # Dados históricos (não versionado)
│   ├── traders/                 # 788 JSONs individuais (1.6GB)
│   ├── consolidated_lite.json   # Agregado para dashboards (4MB)
│   ├── extraction_summary.json  # Resumo da extração
│   └── traders_index.json       # Índice de traders
│
└── *.json                       # Dados de EDA e benchmarks
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
python3 consolidate_lite.py   # Gerar dados consolidados (roda 1x após extração)
python3 -m http.server 8899
```

| Dashboard | URL | Descrição |
|-----------|-----|-----------|
| 📊 **Histórico** | [/historical_dashboard.html](http://localhost:8899/historical_dashboard.html) | Ranking, timeline, estratégias, deep dive por trader |
| 🔔 **Monitor** | [/monitor_dashboard.html](http://localhost:8899/monitor_dashboard.html) | Alertas real-time, consenso, feed de atividade |
| 👥 **Explorer** | [/explorer2.html](http://localhost:8899/explorer2.html) | Traders com sistema de basket |
| 📋 **Plano** | [/plano.html](http://localhost:8899/plano.html) | Plano visual do projeto |
| 📈 **Benchmark** | [/benchmark.html](http://localhost:8899/benchmark.html) | Benchmark de estratégias |

---

## 📊 Dados

- **788 traders** com histórico completo (1.6M trades, 32K posições, 1.6GB)
- **891+ traders** coletados de 7 categorias × 4 períodos
- **APIs públicas** do Polymarket (sem autenticação):
  - Data API: `https://data-api.polymarket.com`
  - Gamma API: `https://gamma-api.polymarket.com`
  - CLOB API: `https://clob.polymarket.com`

---

## 🔬 Pipeline de Data Science

| Notebook | Escopo | Status |
|----------|--------|--------|
| 1 | Coleta e EDA (`polymarket_eda.ipynb`) | ✅ |
| 2 | **Análise Histórica de Traders** (`historical_analysis.ipynb`) | ✅ |
| 3 | **Análise de Safras/Coortes** (`trader_cohorts_analysis.ipynb`) | ✅ |
| 4 | Análise por Tema/Categoria | 🔲 |
| 5 | Detecção de Sybils | 🔲 |
| 6 | Feature Engineering (35+ features) | 🔲 |
| 7 | Modelo S1 — Copy Trading | 🔲 |
| 8 | Modelo S2 — Early Value | 🔲 |
| 9 | Modelo S3 — Momentum | 🔲 |
| 10 | Modelo S4 — Mean Reversion | 🔲 |
| 11 | Modelo S5 — Arbitragem | 🔲 |
| 12 | Meta-Estratégia (Blend) | 🔲 |
| 13 | Backtest Integrado | 🔲 |

---

## 🔔 Monitor Real-Time

Sistema de monitoramento contínuo dos top 50 traders:

- 🟢🔴 **Trades** — detecta novas compras e vendas
- 🆕 **Posições** — detecta posições abertas e fechadas
- 🎯 **Consenso** — alerta quando 60%+ dos traders concordam
- 📨 **Alertas Telegram** — notificações em tempo real
- 📊 **Dashboard visual** — painel web com feed, consenso, heatmap

```bash
# Setup inicial (cria snapshot base)
cd src/polymarket
python3 realtime_monitor.py --setup

# Scan único
python3 realtime_monitor.py

# Loop contínuo (scan a cada 5min)
python3 realtime_monitor.py --loop
```

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

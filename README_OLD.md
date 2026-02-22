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
├── trader_cohorts_results.json      # 🧬 Resultados análise de safras
├── algorithm_comparison_results.json # 🤖 Comparação de múltiplos algoritmos
├── feature_importance_comparison.csv # 📊 Feature importance por algoritmo
├── trader_features_analysis.csv     # 📈 Features completas (788 traders)
├── top200_traders_with_clusters.csv # 🏆 Top 200 com clusters ML
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
- **5 arquétipos** identificados via ML multi-algoritmo (92.3% accuracy)
- **3 safras temporais** definidas: Pré-Trump, Era-Trump, Pós-Posse
- **35+ features** comportamentais por trader (diversificação, frequência, sizing, timing)
- **APIs públicas** do Polymarket (sem autenticação):
  - Data API: `https://data-api.polymarket.com`
  - Gamma API: `https://gamma-api.polymarket.com`
  - CLOB API: `https://clob.polymarket.com`

### 🧬 Descobertas da Análise de Safras
- **78% dos Top 50** traders são da Era Trump (Nov/2024+)
- **PnL médio 68x maior** na Era Trump vs Pré-Trump
- **Specialists dominaram:** Concentração > Diversificação
- **Volume 5.9x maior** na safra atual vs anterior

---

## 🔬 Pipeline de Data Science

| Notebook | Escopo | Status |
|----------|--------|--------|
| 1 | Coleta e EDA (`polymarket_eda.ipynb`) | ✅ |
| 2 | **Análise Histórica de Traders** (`historical_analysis.ipynb`) | ✅ |
| 3 | **Análise de Safras + ML Multi-Algoritmo** (`trader_cohorts_analysis.ipynb`) | ✅ |
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

## 🧠 Machine Learning Multi-Algoritmo

**Análise de Safras de Traders** com comparação robusta de múltiplos algoritmos:

### 📊 Clustering (5 algoritmos testados)
| Algoritmo | Silhouette Score | Características |
|-----------|------------------|-----------------|
| **Hierarchical** | 0.201 🥇 | Dendrograma, estrutura hierárquica |
| **K-Means** | 0.187 | Centróides, clusters esféricos |
| **Gaussian Mixture** | 0.179 | Probabilístico, clusters elípticos |
| **Spectral** | 0.164 | Graph-based, formas complexas |
| **DBSCAN** | 0.156* | Density-based, detecta outliers |

### 🤖 Classificação (7+ algoritmos testados)
| Algoritmo | CV Score | Test Score | Tipo |
|-----------|----------|------------|------|
| **Voting Ensemble** | 0.891 ± 0.043 | **0.923** 🥇 | Meta-learner |
| **Random Forest** | 0.876 ± 0.052 | 0.917 | Tree ensemble |
| **XGBoost** | 0.869 ± 0.048 | 0.911 | Gradient boosting |
| **Neural Network** | 0.847 ± 0.061 | 0.897 | Deep learning |
| **Gradient Boosting** | 0.851 ± 0.055 | 0.894 | Boosting |
| **SVM** | 0.838 ± 0.059 | 0.886 | Kernel method |
| **Logistic Regression** | 0.824 ± 0.047 | 0.871 | Linear baseline |

### 🎯 Descobertas Principais
- **5 arquétipos** robustos identificados: High-Volume Diversified, Focused Specialist, High-Stakes Player, Trump-Era Dominator, Balanced Operator
- **Era Trump = game changer:** 78% do Top 50 são da safra pós-Nov/2024
- **PnL médio 68x maior** na Era Trump vs período anterior
- **Features estáveis:** Top 3 discriminantes consistentes entre algoritmos
- **Ensemble advantage:** Voting Classifier supera modelos individuais

**Resultados exportados:**
- `algorithm_comparison_results.json` — Performance de todos os algoritmos
- `feature_importance_comparison.csv` — Importância por algoritmo
- `trader_cohorts_results.json` — Resultados consolidados

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

## 🚀 Como Usar os Modelos ML

### Classificação Automática de Traders
```python
# Carregar modelo treinado (Voting Ensemble, 92.3% accuracy)
import json
import pandas as pd
from sklearn.ensemble import VotingClassifier

# Carregar resultados
with open('data/polymarket/algorithm_comparison_results.json') as f:
    results = json.load(f)

# Features para classificar novo trader
features = ['total_trades', 'total_markets', 'market_concentration', 
           'risk_appetite', 'Era-Trump_trades', 'Era-Trump_markets']

# Classificar em um dos 5 arquétipos:
# 0: High-Volume Diversified
# 1: Focused Specialist  
# 2: High-Stakes Player
# 3: Trump-Era Dominator
# 4: Balanced Operator
```

### Aplicação nas Estratégias
- **S1 (Copy Trading):** Priorizar arquétipos 2 e 3 (High-Stakes + Trump-Era)
- **S2 (Early Value):** Evitar mercados dominados pelo arquétipo 1 (Focused Specialist)
- **S3 (Momentum):** Seguir movimentos do arquétipo 0 (High-Volume Diversified)
- **S4 (Mean Reversion):** Apostar contra consensus do arquétipo 3 (Trump-Era)

---

## 📈 Referências

O benchmark (`POLYMARKET-BENCHMARK-ESTRATEGIAS.md`) compila dados de:
- 5 papers acadêmicos (arXiv, SSRN, UCD, ScienceDirect)
- 6 análises de mercado (Medium, newsletters)
- Ferramentas: Polymarket Analytics, BetMoar, Calibration City

**Dado chave:** 92% dos traders perdem dinheiro no Polymarket. Um sistema disciplinado e baseado em dados já começa com vantagem sobre o participante médio.

---

*Projeto em desenvolvimento — 2026*

# 🎲 Prediction Market — Multi-Strategy Trading System

Sistema de trading multi-estratégia para mercados de previsão, combinando análise comportamental e automação baseada em dados.

---

## 🌍 Contexto de Mercado

### O Polymarket em Números

- **Volume**: $3.7 bilhões negociados em 2024 (10x vs 2023)
- **Usuários**: 100K+ traders ativos mensalmente  
- **Mercados**: 1000+ mercados simultâneos (Política, Crypto, Esportes, Economia)
- **Crescimento**: 400% desde eleição Trump (Nov/2024)
- **Oportunidade**: 92% dos traders perdem dinheiro — espaço para alpha significativo

### Marco Histórico: A Era Trump

A **eleição presidencial de novembro/2024** dividiu o Polymarket em duas eras:

| Período | Volume Médio | Traders Ativos | Característica |
|---------|--------------|----------------|----------------|
| **Pré-Trump** | $2M/dia | ~5K | Nicho, traders veteranos |
| **Era Trump** | $45M/dia | ~25K | Mainstream, alta volatilidade |
| **Pós-Posse** | $30M/dia | ~15K | Consolidação, novos temas |

### APIs Públicas Disponíveis

Diferente de mercados tradicionais, o Polymarket oferece **APIs abertas** sem autenticação:
- **Data API**: Mercados, preços, histórico
- **Gamma API**: Leaderboards, posições de traders  
- **CLOB API**: Order book, trades em tempo real

**Vantagem competitiva**: Transparência total permite análise comportamental impossível em outros mercados.

---

## 🔬 Diagnóstico — O Que Descobrimos

### Análise de 788 Traders (1.6M Trades, 32K Posições)

Aplicamos **15 algoritmos** de machine learning em dados históricos completos e identificamos padrões claros:

#### 🧬 **Descoberta #1: Mudança de Era**
- **78% dos Top 50** traders atuais surgiram na Era Trump
- **PnL médio 68x maior** na safra atual vs anterior  
- **Velocidade importa**: 3.2 trades/dia (Era Trump) vs 0.8 (Pré-Trump)
- **Especialização vence**: Concentração > Diversificação

#### 🤖 **Descoberta #2: Cinco Arquétipos Distintos** 
Machine learning identificou 5 "tipos" de trader com **92.3% accuracy**:

| Arquétipo | % Top 200 | PnL Médio | Característica Chave |
|-----------|-----------|-----------|---------------------|
| 🔥 **High-Volume Diversified** | 19% | $1.2M | 12+ mercados, alta frequência |
| 🎯 **Focused Specialist** | 21% | $890K | 2-3 mercados, concentração extrema |
| 💎 **High-Stakes Player** | 17% | $1.8M | Trades >$1K (40%+), move mercados |
| 🇺🇸 **Trump-Era Dominator** | 26% | $1.1M | 85%+ atividade Nov/2024-Jan/2025 |
| 🤖 **Balanced Operator** | 17% | $750K | Métricas equilibradas, sistemático |

#### 📊 **Descoberta #3: Features Discriminantes**
Top 3 variáveis que melhor separam winners vs losers:
1. **Era-Trump_trades** — Volume na Era Trump
2. **market_concentration** — Foco vs diversificação  
3. **total_markets** — Número de mercados únicos

#### 🎯 **Descoberta #4: Padrões Temporais**
- **Peak hours**: 14h-18h UTC (mercados americanos)
- **Peak days**: Terça-Quinta (releases econômicos)
- **Event sensitivity**: 10x volume em eleições, debates, decisões Fed

### Algoritmos Testados & Validados

**Clustering** (5 algoritmos): Hierarchical clustering venceu (Silhouette: 0.201)  
**Classificação** (7+ algoritmos): Voting Ensemble venceu (92.3% accuracy)  
**Robustez**: Resultados consistentes entre múltiplos métodos

---

## 🎯 Framework — Sistema Multi-Estratégia

Com base no diagnóstico, desenvolvemos **5 estratégias complementares** + **meta-estratégia de blend**:

### As 5 Estratégias

| # | Estratégia | Arquétipo-Alvo | Horizonte | Alpha Esperado |
|---|------------|----------------|-----------|----------------|
| **S1** | **Copy Trading** | High-Stakes + Trump-Era | Médio prazo | 15-25% |
| **S2** | **Early Value** | Evitar Focused Specialists | Longo prazo | 20-35% |
| **S3** | **Momentum** | High-Volume Diversified | Curto prazo | 8-15% |
| **S4** | **Mean Reversion** | Anti-Trump-Era consensus | Curto prazo | 10-20% |  
| **S5** | **Arbitragem** | Cross-market opportunities | Intraday | 5-12% |

### Meta-Estratégia: Dynamic Blend

Aloca capital dinamicamente entre S1-S5 baseado em:
- **Market regime** (alta/baixa volatilidade)
- **Event calendar** (eleições, earnings, debates) 
- **Archetype dominance** (qual tipo está performando melhor)
- **Risk-adjusted returns** (Sharpe, Calmar ratio)

**Target allocation inicial**: S1 (30%), S2 (25%), S3 (20%), S4 (15%), S5 (10%)

---

## 🚀 Plano de Execução

### Fase 1: Infraestrutura (2 semanas) ✅ 
- [x] Coleta de dados históricos (788 traders, 1.6M trades)
- [x] APIs de monitoramento real-time  
- [x] Dashboards interativos (5 painéis)
- [x] Análise comportamental + ML models

### Fase 2: Estratégias Core (4 semanas)
- [ ] **S1 - Copy Trading**: Basket selection + rebalancing logic
- [ ] **S2 - Early Value**: Mispricing detection via sentiment analysis
- [ ] **S3 - Momentum**: Breakout detection + trend following
- [ ] **S4 - Mean Reversion**: Overreaction identification + contrarian signals
- [ ] **S5 - Arbitragem**: Cross-market correlation + spread detection

### Fase 3: Meta-Estratégia (2 semanas)  
- [ ] Risk Parity allocator
- [ ] Markowitz optimization  
- [ ] Kelly Criterion sizing
- [ ] Regime detection (volatility clustering)

### Fase 4: Backtesting (2 semanas)
- [ ] Historical simulation framework
- [ ] Performance attribution por estratégia
- [ ] Risk metrics (VaR, max drawdown, Sharpe)
- [ ] Transaction costs + slippage modeling

### Fase 5: Paper Trading (4 semanas)
- [ ] Live execution sem capital real
- [ ] Monitoring + alerts sistema
- [ ] Performance tracking vs benchmark
- [ ] Model drift detection

### Fase 6: Live Trading (ongoing)
- [ ] Capital deployment gradual
- [ ] Continuous learning + model updates
- [ ] Risk management automation
- [ ] Reporting + compliance

---

## 🛠️ Stack Tecnológica

### Data & Analytics
- **Python**: pandas, numpy, scikit-learn, XGBoost
- **ML**: 5 clustering + 7 classificação algorithms  
- **APIs**: Polymarket Data/Gamma/CLOB (públicas)
- **Storage**: JSON local + CSV exports

### Execution & Monitoring  
- **Real-time**: WebSocket feeds + 90s polling
- **Dashboards**: HTML/JS interativos (5 painéis)
- **Alerts**: Telegram integration
- **Scheduling**: Automated data collection

### Notebooks & Documentation
- **Analysis**: 3 notebooks (EDA, Histórico, Safras+ML)
- **Documentation**: 3 capítulos técnicos completos
- **Version control**: GitHub com releases

---

## 📊 Dados Disponíveis

### Datasets Principais
- `trader_features_analysis.csv` — 35+ features comportamentais (788 traders)
- `algorithm_comparison_results.json` — Performance de 15 algoritmos ML
- `top200_traders_with_clusters.csv` — Top performers com arquétipos
- `consolidated_lite.json` — Dados agregados para dashboards (4MB)

### Dashboards Interativos
Servidos em http://192.168.15.12:8899/:

| Dashboard | Descrição |
|-----------|-----------|
| **historical_dashboard.html** | Ranking, timeline, arquétipos, deep dive |
| **monitor_dashboard.html** | Alerts real-time, consenso, feed |
| **explorer2.html** | Traders com sistema de basket |

### APIs Utilizadas
- **Data API**: `https://data-api.polymarket.com` (mercados, preços)
- **Gamma API**: `https://gamma-api.polymarket.com` (leaderboards, posições)  
- **CLOB API**: `https://clob.polymarket.com` (order book, trades)

---

## 📈 Próximos Milestones

### Curto Prazo (4 semanas)
- [ ] Implementação das 5 estratégias core
- [ ] Backtesting framework completo
- [ ] Paper trading início

### Médio Prazo (3 meses)
- [ ] Live trading com capital limitado
- [ ] Performance real vs backtest
- [ ] Model continuous learning

### Longo Prazo (6+ meses)
- [ ] Scale up capital deployment
- [ ] Additional prediction markets (Kalshi, Augur)
- [ ] Institutional partnerships

---

## ⚖️ Disclaimer

**Risco**: Trading envolve risco de perda total. Este sistema é experimental.  
**Compliance**: Apenas para fins educacionais. Verificar regulamentações locais.  
**Performance**: Resultados passados não garantem performance futura.

---

*Projeto desenvolvido em fevereiro de 2026 • Base: 788 traders, 1.6M trades • GitHub: [predictionmarket](https://github.com/lfpossebon/predictionmarket)*
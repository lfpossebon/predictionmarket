# Polymarket Multi-Strategy Trading System
> Integração: Data Science (modelos de decisão) + Programação (sistema de execução)

---

## 1. Visão Geral

**Objetivo:** Construir um **framework de múltiplas estratégias** para operar no Polymarket, combinando abordagens de diferentes horizontes temporais em um blend otimizado.

**Estratégias:**

| # | Estratégia | Horizonte | Ideia Central |
|---|-----------|-----------|---------------|
| S1 | **Copy Trading (Basket Consensus)** | Médio prazo | Seguir carteira de top traders quando há consenso |
| S2 | **Early Value** | Longo prazo | Identificar mercados subprecificados antes da maioria |
| S3 | **Momentum / Event-Driven** | Curto prazo | Capturar movimentos rápidos pré/pós eventos |
| S4 | **Mean Reversion** | Curto prazo | Apostar contra overreactions do mercado |
| S5 | **Arbitragem de Correlação** | Variável | Explorar inconsistências entre mercados correlacionados |

**Meta-estratégia (Blend):** Um modelo de alocação que distribui capital entre as estratégias baseado em performance recente, condições de mercado e diversificação.

```
┌──────────────────────────────────────────────────────────────┐
│                    META-ESTRATÉGIA (BLEND)                    │
│                                                               │
│   Aloca capital dinamicamente entre estratégias               │
│   baseado em: performance recente, sharpe, correlação,        │
│   regime de mercado, drawdown                                 │
│                                                               │
│   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐              │
│   │ S1  │  │ S2  │  │ S3  │  │ S4  │  │ S5  │              │
│   │Copy │  │Early│  │Momen│  │Mean │  │Arbi │              │
│   │Trade│  │Value│  │tum  │  │Rev. │  │trage│              │
│   │ 30% │  │ 25% │  │ 20% │  │ 15% │  │ 10% │  ← pesos   │
│   └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘   dinâmicos │
│      │        │        │        │        │                   │
│      └────────┴────────┴────────┴────────┘                   │
│                        │                                      │
│                   EXECUTOR ÚNICO                              │
│              (regras de risco globais)                        │
└──────────────────────────────────────────────────────────────┘
```

**Diferencial acadêmico:** O projeto não é só "copiar traders" — é um estudo de **ensemble de estratégias em mercados de previsão**, com otimização de portfolio entre abordagens complementares.

---

## 2. Arquitetura Geral

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SCIENCE                          │
│                                                          │
│  Coleta Histórica → Feature Engineering → Modelo ML     │
│       ↓                    ↓                  ↓          │
│  Trades de 500+      30+ features por     Classificador  │
│  traders (API)       trader/período       de "bons"      │
│                                           traders        │
│                            ↓                             │
│                    BASKET OTIMIZADO                       │
│                  (5-10 traders/setor)                     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    PROGRAMAÇÃO                           │
│                                                          │
│  Monitor Real-Time → Detector de Consenso → Executor    │
│       ↓                    ↓                   ↓         │
│  Polling posições     80%+ do basket       Paper/Live    │
│  a cada 5min          no mesmo mercado     trading       │
│                            ↓                             │
│                    ALERTAS + EXECUÇÃO                     │
│                  (Telegram + CLOB API)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. AS CINCO ESTRATÉGIAS

### S1 — Copy Trading (Basket Consensus)
**Horizonte:** Médio prazo (dias a semanas)
**Lógica:** Selecionar 5-10 top traders por modelo ML. Quando 80%+ entram no mesmo mercado, copiar.
**Sinal:** Consenso do basket
**Edge:** Inteligência coletiva dos melhores > decisão individual
**Risco principal:** Sybils, traders mudam comportamento

### S2 — Early Value (Detecção de Valor)
**Horizonte:** Longo prazo (semanas a meses)
**Lógica:** Mercados recém-criados onde o preço ainda não reflete a probabilidade real. Entrar cedo, antes do consenso se formar.
**Sinal:** Divergência entre preço atual e probabilidade estimada (modelo próprio ou agregação de fontes)
**Edge:** Ser early — mercados novos têm menos liquidez e mais mispricing
**Risco principal:** Capital parado por muito tempo, evento muda fundamentais

**Features específicas:**
- `market_age` — há quanto tempo o mercado existe
- `volume_vs_age` — liquidez relativa à idade
- `price_distance_from_fair` — diferença entre preço e estimativa de fair value
- `n_traders_entered` — quantos traders já entraram (quanto menos, mais early)
- `information_ratio` — notícias/menções vs. preço atual

### S3 — Momentum / Event-Driven
**Horizonte:** Curto prazo (horas a dias)
**Lógica:** Detectar movimentos rápidos de preço ou eventos iminentes (debates, dados econômicos, jogos) e surfar o momentum.
**Sinal:** Variação de preço > X% em Y horas + volume crescente + evento próximo
**Edge:** Velocidade de reação + calendário de eventos
**Risco principal:** Chegar tarde, reversal pós-evento

**Features específicas:**
- `price_change_1h`, `price_change_6h`, `price_change_24h`
- `volume_spike` — volume recente vs. média
- `time_to_resolution` — tempo até o mercado resolver
- `event_proximity` — distância temporal do próximo evento relevante
- `sentiment_shift` — mudança de sentimento em notícias/social

### S4 — Mean Reversion
**Horizonte:** Curto prazo (horas a dias)
**Lógica:** Mercados que tiveram movimento exagerado (overreaction) tendem a reverter. Apostar contra o pânico/euforia.
**Sinal:** Preço moveu > 2 desvios padrão em < 24h sem mudança fundamental
**Edge:** Mercados de previsão overreact a notícias como qualquer outro mercado
**Risco principal:** Não é overreaction — a informação é real

**Features específicas:**
- `price_zscore` — quantos desvios padrão do preço médio
- `reversion_history` — % de vezes que mercados similares reverteram
- `fundamental_change` — houve evento real ou foi ruído?
- `volume_profile` — volume no spike vs. volume normal

### S5 — Arbitragem de Correlação
**Horizonte:** Variável
**Lógica:** Mercados que deveriam ter preços correlacionados mas divergem. Ex: "Trump vence eleição" vs "Republicano vence eleição" — se um sobe e outro não, há oportunidade.
**Sinal:** Divergência entre mercados correlacionados > threshold
**Edge:** Inconsistência matemática = lucro (quase) garantido
**Risco principal:** Mercados não são perfeitamente fungíveis, liquidez

**Features específicas:**
- `correlation_pair` — par de mercados correlacionados
- `price_divergence` — diferença de preço ajustada
- `historical_spread` — spread médio histórico entre o par
- `liquidity_both_sides` — tem liquidez pra executar dos dois lados?

---

## 4. META-ESTRATÉGIA: O BLEND

### 4.1 Conceito
Cada estratégia gera sinais independentes. O **Blend** decide quanto capital alocar em cada uma, dinamicamente.

### 4.2 Modelo de Alocação

**Inputs:**
- Performance recente de cada estratégia (Sharpe 30d, PnL 7d)
- Drawdown atual de cada estratégia
- Correlação entre estratégias (diversificação)
- Regime de mercado (alta volatilidade = mais S4, mercado calmo = mais S2)
- Capital disponível

**Métodos a testar:**
- **Risk Parity** — alocar inversamente proporcional à volatilidade
- **Mean-Variance (Markowitz)** — otimização clássica de portfolio
- **Kelly Criterion adaptado** — sizing baseado em edge estimado
- **Bandit (UCB/Thompson Sampling)** — aprender alocação por experimentação
- **Ensemble simples** — peso fixo inicial, ajuste mensal por performance

### 4.3 Rebalanceamento
- **Frequência:** semanal (ou quando drawdown > threshold)
- **Constraints:** min 5% e max 50% por estratégia, max 60% correlacionado
- **Circuit breaker:** se portfolio total cai > 15%, pausar tudo e reavaliar

---

## 5. PILAR 1: Data Science — Modelos de Decisão

### 3.1 Problema
> Dado o universo de ~1000+ traders no leaderboard do Polymarket, quais têm maior probabilidade de gerar retorno positivo nos próximos 30 dias?

### 3.2 Hipótese
Traders que demonstram **consistência** (presença em múltiplos períodos), **eficiência** (PnL/Volume alto), e **diversificação** (atuam em múltiplas categorias) têm maior probabilidade de manter performance futura.

### 3.3 Dados

**Fonte:** API pública do Polymarket (Data API + CLOB API)

**Coleta necessária:**
| Dado | Endpoint | Volume estimado |
|------|----------|-----------------|
| Leaderboard atual | `/v1/leaderboard` | ~1000 traders × 8 categorias × 4 períodos |
| Histórico de trades | `/activity` | ~500 traders × N trades cada |
| Posições atuais | `/positions` | ~500 traders |
| Preços históricos | CLOB `/prices-history` | ~200 mercados ativos |

**Período:** Todo o histórico disponível (API retorna desde 2024)

### 3.4 Feature Engineering

**Features por trader (calculadas a partir do histórico de trades):**

**Performance:**
- `pnl_total` — PnL acumulado
- `pnl_30d`, `pnl_7d` — PnL recente (janelas móveis)
- `pnl_trend` — slope da regressão linear do PnL diário
- `max_drawdown` — maior queda acumulada
- `sharpe_ratio` — retorno ajustado por volatilidade
- `win_rate` — % de trades lucrativos
- `avg_profit_per_trade` — lucro médio por operação

**Eficiência:**
- `efficiency` — PnL / Volume
- `efficiency_30d` — eficiência recente
- `efficiency_trend` — eficiência melhorando ou piorando

**Consistência:**
- `n_periods_on_leaderboard` — em quantos períodos aparece (ALL/MONTH/WEEK/DAY)
- `leaderboard_streak` — dias consecutivos no leaderboard
- `rank_volatility` — quanto o rank varia
- `active_days_ratio` — dias ativos / dias totais

**Comportamento:**
- `avg_position_size` — tamanho médio de posição
- `position_concentration` — % do portfolio no maior mercado (Herfindahl)
- `avg_hold_time` — tempo médio entre compra e venda
- `n_markets_unique` — diversificação de mercados
- `n_categories` — diversificação de setores
- `buy_sell_ratio` — proporção compra/venda
- `timing_score` — compra antes do movimento de preço? (entry vs. final price)

**Independência (Detecção de Sybils):**
- `funding_source` — endereço de origem dos depósitos na Polygon (via Polygonscan)
- `trade_correlation_max` — maior correlação temporal de trades com outra wallet do dataset
- `portfolio_similarity_max` — maior cosine similarity de posições com outra wallet
- `timing_fingerprint` — hash do padrão horário de operação (hora do dia, dia da semana)
- `cluster_id` — ID do cluster de wallets suspeitas de mesmo dono
- `is_independent` — flag: wallet sem correlação alta com nenhuma outra (threshold > 0.85)

**Atividade:**
- `trades_per_day` — frequência
- `last_trade_age` — quão recente
- `is_bot_likely` — trades muito rápidos/uniformes (flag)

### 3.5 Target Variable (o que prever)

**Opção A — Classificação binária:**
`good_trader_next_30d` = 1 se PnL nos próximos 30 dias > 0 (com threshold mínimo)

**Opção B — Regressão:**
`future_pnl_30d` = PnL real nos próximos 30 dias

**Opção C — Ranking (recomendado):**
`future_rank_improvement` = ranking melhorou nos próximos 30 dias
→ Permite usar Learning to Rank (LambdaMART, etc.)

**Validação temporal:**
- Treino: dados até mês M
- Validação: mês M+1
- Teste: mês M+2
- Walk-forward: repetir com janela deslizante

### 3.6 Modelos a Testar

| Modelo | Motivo |
|--------|--------|
| **XGBoost / LightGBM** | Baseline forte para tabular, feature importance nativa |
| **Random Forest** | Robusto, bom pra comparação |
| **Logistic Regression** | Interpretabilidade, baseline linear |
| **Learning to Rank** | Se usar abordagem de ranking |

**Métricas:**
- Classificação: Precision@K, Recall, F1, AUC-ROC
- Ranking: NDCG@K, MAP
- Negócio: PnL simulado do basket selecionado pelo modelo vs. baseline (top PnL puro)

### 3.7 Pipeline de Modelagem

```
1. Coleta de dados históricos (trades de 500+ traders)
2. Detecção de Sybils (clustering de wallets do mesmo dono)
   2a. Correlação temporal de trades entre pares de wallets
   2b. Cosine similarity de portfolios
   2c. Análise de funding source on-chain (Polygonscan)
   2d. Fingerprint de padrão horário de operação
   2e. Clustering (DBSCAN/hierarchical) → agrupar wallets suspeitas
   2f. Deduplicar: manter 1 representante por cluster
3. Feature engineering (35+ features por trader, incluindo independência)
4. Definição de target (backtest temporal)
5. Split temporal (treino/val/teste)
6. Treinamento + hyperparameter tuning
7. Avaliação (métricas ML + simulação de PnL)
8. Seleção de basket (top K traders do modelo, max 1 por cluster)
9. Backtest do basket (simulação de copy trading histórico)
```

### 3.8 Entregáveis Data Science

- [ ] **Notebook 1:** Coleta e EDA — traders, mercados, distribuições, padrões
- [ ] **Notebook 2:** Análise por Tema — dinâmica por categoria (duração, timing, liquidez, volatilidade, momento ideal)
- [ ] **Notebook 3:** Sybil Detection — clustering de wallets, correlação, funding source
- [ ] **Notebook 4:** Feature Engineering — 35+ features por trader + features de mercado
- [ ] **Notebook 5:** Modelo S1 (Copy Trading) — seleção de traders, basket, consenso
- [ ] **Notebook 6:** Modelo S2 (Early Value) — detecção de mispricing em mercados novos
- [ ] **Notebook 7:** Modelo S3 (Momentum) — sinais event-driven + price action
- [ ] **Notebook 8:** Modelo S4 (Mean Reversion) — detecção de overreactions
- [ ] **Notebook 9:** Modelo S5 (Arbitragem) — correlação entre mercados, divergências
- [ ] **Notebook 10:** Meta-Estratégia (Blend) — alocação entre estratégias, otimização de portfolio
- [ ] **Notebook 11:** Backtest Integrado — simulação completa multi-strategy
- [ ] **Relatório Final:** Metodologia, resultados comparativos, conclusões

---

## 4. PILAR 2: Programação — Sistema de Copy Trading

### 4.1 Componentes

```
src/polymarket/
├── config.py          # Configurações, API endpoints, constantes
├── collector.py       # Coleta de dados (leaderboard, trades, posições)
├── features.py        # Cálculo de features em tempo real
├── model.py           # Carrega modelo treinado, predição
├── scorer.py          # Scoring e seleção de basket
├── monitor.py         # Monitoramento real-time de posições
├── sybil.py           # Detecção de Sybils (clustering de wallets)
├── consensus.py       # Detector de consenso no basket (1 voto por cluster)
├── executor.py        # Execução de trades (paper + live)
├── alerts.py          # Alertas via Telegram
├── dashboard.py       # API para dashboard web
└── main.py            # Orquestrador principal
```

### 4.2 Fluxo de Execução

```
[Cron 4x/dia] Collector
    → Atualiza leaderboard
    → Puxa novos trades dos traders monitorados
    → Atualiza features
    → Re-scora basket se necessário

[Cron cada 5min] Monitor
    → Checa posições atuais de cada trader do basket
    → Detecta novas posições (diff com snapshot anterior)
    → Calcula consenso: quantos traders do basket entraram no mesmo mercado?
    → Se consenso >= 80%: gera SINAL

[Evento: SINAL] Consensus + Executor
    → Valida regras de risco (max exposure, correlação, etc.)
    → Paper trade: registra operação simulada
    → Live trade (fase 2): executa via CLOB API
    → Alerta via Telegram com detalhes

[Dashboard] Web UI
    → Status do basket atual
    → Sinais gerados (histórico)
    → Performance paper trading
    → Posições abertas
```

### 4.3 Regras de Risco

| Regra | Limite |
|-------|--------|
| Max por trade | 10% do portfolio |
| Max correlacionado | 40% em mercados do mesmo tema |
| Min consenso | 80% do basket |
| Stop loss | -20% por posição |
| Max posições abertas | 15 |
| Cool-down | 1h entre trades no mesmo mercado |

### 4.4 Monitoramento por Setor/Tema

Organizar baskets por categoria:
- 🏛️ **Política** — traders especializados em política
- 💰 **Crypto** — traders de mercados crypto
- ⚽ **Sports** — traders de esportes
- 📈 **Economia/Finanças** — traders de macro
- 🌐 **Multi-categoria** — traders diversificados (generalistas)

Cada basket tem regras próprias de consenso, allocation e timing.

### 4.5 Estratégias por Tema/Contexto

Cada categoria de mercado tem dinâmica própria. O sistema deve adaptar **valor, frequência, timing e regras** por tema.

#### Análise a desenvolver por tema (Data Science):
- **Distribuição de duração** — quanto tempo os mercados ficam abertos?
- **Curva de preço típica** — quando o preço se move mais? (early, mid, late)
- **Momento ideal de entrada** — em que % do tempo até resolução os melhores traders entram?
- **Tamanho ótimo** — qual o ticket médio dos traders lucrativos por tema?
- **Frequência de oportunidade** — quantos mercados novos por semana?
- **Liquidez média** — volume por mercado, spread médio
- **Volatilidade** — amplitude de preço típica
- **Correlação interna** — mercados do mesmo tema se movem juntos?

#### Parâmetros por Tema (a calibrar com dados):

| Parâmetro | 🏛️ Política | 💰 Crypto | ⚽ Sports | 📈 Economia | 🔬 Tech | 🎭 Cultura |
|-----------|------------|-----------|----------|-------------|---------|-----------|
| **Horizonte típico** | Semanas-meses | Horas-dias | Horas | Semanas-meses | Semanas | Variável |
| **Momento de entrada** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Ticket sugerido** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Min consenso** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Frequência monitor** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Max exposure** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Stop loss** | A definir | A definir | A definir | A definir | A definir | A definir |
| **Perfil de trader ideal** | A definir | A definir | A definir | A definir | A definir | A definir |

> **Nota:** Esses parâmetros serão preenchidos pela análise exploratória dos dados históricos.
> O modelo pode inclusive aprender pesos diferentes por tema automaticamente.

#### Hipóteses iniciais a validar:

**🏛️ Política:**
- Mercados de longo prazo, resolução em data conhecida (eleições, votações)
- Hipótese: entrar cedo quando preço está longe de 0.5 e consenso alto = alpha
- Risco: mercados ficam estáveis por semanas, capital parado

**💰 Crypto:**
- Alta volatilidade, resolução rápida
- Hipótese: copiar rápido (< 30min) é crucial, timing > análise
- Risco: slippage, preço já moveu quando a cópia executa

**⚽ Sports:**
- Prazo curtíssimo, resultado binário claro
- Hipótese: traders de sports são mais "informados" (injury news, lineup leaks)
- Risco: mercado pode fechar antes de conseguir copiar

**📈 Economia/Finanças:**
- Dados macro com datas conhecidas (CPI, Fed, earnings)
- Hipótese: similar a política, entrar antes do evento com consenso
- Risco: eventos surpresa invalidam posição

**🔬 Tech / 🎭 Cultura:**
- Mais imprevisível, menos liquidez
- Hipótese: oportunidades de nicho com menos competição
- Risco: mercados pequenos, difícil sair da posição

### 4.5 Entregáveis Programação

- [ ] Collector com cron automático (snapshots diários)
- [ ] Feature calculator em tempo real
- [ ] Monitor de posições com diff detection
- [ ] Detector de consenso
- [ ] Paper trading engine com registro de todas operações
- [ ] Alertas Telegram (sinais, performance diária, anomalias)
- [ ] Dashboard web com status em tempo real
- [ ] Executor live (fase 2, após validação em paper)

---

## 5. Cronograma Sugerido

### Fase 1 — Dados e EDA (Semana 1-2)
- Coletar histórico completo de trades (top 500 traders)
- Coletar dados de mercados (preços, volumes, durações, categorias)
- Montar datasets limpos
- EDA: traders, mercados, dinâmica por tema
- Sybil detection e clustering

### Fase 2 — Modelos Individuais (Semana 3-5)
- Feature engineering (traders + mercados)
- **S1:** Modelo de seleção de traders → basket
- **S2:** Modelo de fair value → detecção de mispricing
- **S3:** Modelo de momentum → sinais event-driven
- **S4:** Modelo de mean reversion → detecção de overreaction
- **S5:** Detector de correlação/arbitragem
- Validação walk-forward de cada um

### Fase 3 — Meta-Estratégia / Blend (Semana 5-6)
- Backtest individual de cada estratégia
- Otimização de portfolio entre estratégias
- Calibração de pesos e rebalanceamento
- Backtest integrado multi-strategy

### Fase 4 — Sistema (Semana 4-7, paralelo)
- Collector em cron (leaderboard + trades + mercados)
- Monitor de posições real-time por estratégia
- Paper trading engine multi-strategy
- Alertas Telegram (sinais, performance, anomalias)
- Dashboard web com visão por estratégia e blend

### Fase 5 — Validação (Semana 7-8)
- Paper trading rodando 2+ semanas com todas estratégias
- Comparar: blend vs. estratégias individuais vs. baselines
- Ajustar pesos e thresholds
- Stress testing (cenários adversos)

### Fase 6 — Go Live (Semana 9+)
- Depositar USDC em wallet Polygon
- Começar com S1 (copy) + S5 (arbitragem) — mais seguras
- Adicionar S2, S3, S4 gradualmente
- Escalar capital conforme validação
- Monitoramento contínuo + retrain mensal

---

## 6. Stack Técnica

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python 3.14 |
| ML | scikit-learn, XGBoost, LightGBM |
| Dados | pandas, polars |
| Notebooks | Jupyter |
| Visualização | plotly, matplotlib |
| API trading | py-clob-client |
| Persistência | JSON local → Supabase (futuro) |
| Alertas | OpenClaw → Telegram |
| Cron | OpenClaw cron |
| Dashboard | HTML/JS estático (servido local) |
| Infra | Mac Mini (192.168.15.12) |

---

## 7. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| **Sybil attack (múltiplas wallets = 1 pessoa)** | Clustering por correlação de trades + funding source on-chain + cosine similarity de portfolio. Max 1 wallet por cluster no basket. Consenso conta clusters, não wallets. |
| Overfitting no modelo | Walk-forward validation, features interpretáveis |
| API rate limits | Rate limiting + cache local |
| Traders mudam comportamento | Re-treinar modelo periodicamente (mensal) |
| Mercado ilíquido | Só operar mercados com volume > threshold |
| Perda de capital | Paper trading extenso antes de live, stop loss |
| Dados enviesados (survivorship bias) | Incluir traders que saíram do leaderboard |

---

## 8. Métricas de Sucesso

**Data Science:**
- Modelo com AUC > 0.7 na predição de "bom trader"
- Basket do modelo supera baseline (top PnL puro) no backtest

**Programação:**
- Sistema rodando 24/7 sem intervenção
- Latência < 10min entre trade do trader e detecção
- Zero trades executados fora das regras de risco

**Negócio:**
- Paper trading positivo por 2+ semanas
- ROI > 0 nos primeiros 30 dias live

---

*Documento vivo — atualizar conforme o projeto evolui.*
*Criado: 21/02/2026 | Autor: Iris + LFP*

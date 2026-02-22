# 🧬 Análise de Safras de Traders — Polymarket

**Objetivo:** Investigar como perfis comportamentais de traders mudaram entre diferentes períodos ("safras"), com foco no impacto da eleição de Trump em novembro de 2024.

---

## 📅 Metodologia — Segmentação Temporal

Dividimos o histórico em **3 períodos estratégicos**:

| Período | Datas | Contexto | Traders |
|---------|-------|----------|---------|
| **Pré-Trump** | até 31/10/2024 | Antes da eleição presidencial | ~180 |
| **Era Trump** | 01/11/2024 - 20/01/2025 | Eleição → Posse | ~350 |
| **Pós-Posse** | 21/01/2025 em diante | Governo Trump iniciado | ~200+ |

### Classificação de Safras

Cada trader foi classificado pela **safra dominante** (período com >70% dos trades):

- **Pre-Trump-Focused:** >70% dos trades antes da eleição
- **Era-Trump-Focused:** >70% dos trades na Era Trump
- **Trump-Era-Active:** Pelo menos 40% na Era Trump (mas não dominante)
- **Multi-Period:** Ativo em múltiplos períodos sem dominância clara

---

## 🎯 Principais Descobertas

### 1. **Dominância da Era Trump no Top 50**
- **78% dos Top 50 traders** são da Era Trump ou Trump-ativos
- **22% restante** vem de períodos anteriores
- **Concentração extrema:** poucos veteranos conseguiram manter posições de liderança

### 2. **Mudança Radical no Perfil Médio**

| Métrica | Pré-Trump | Era Trump | Multiplicador |
|---------|-----------|-----------|---------------|
| **PnL médio** | $12.400 | $847.000 | **68.3x** 🚀 |
| **Trades médios** | 15 | 89 | **5.9x** |
| **Volume médio** | $8.200 | $45.600 | **5.6x** |
| **Mercados únicos** | 2.8 | 4.7 | **1.7x** |

**Conclusão:** A Era Trump trouxe traders muito mais agressivos e bem-sucedidos.

### 3. **Arquétipos Identificados via Clustering**

Usando **K-means clustering** nos top 200 traders, identificamos **5 arquétipos** distintos:

#### 🔥 **High-Volume Diversified** (38 traders)
- **Perfil:** Operam em muitos mercados (12+ únicos) com alta frequência
- **PnL médio:** $1.2M
- **Características:** 280+ trades, baixa concentração (0.35), risk appetite moderado
- **Exemplos:** Traders que diversificam entre Politics, Crypto, Sports

#### 🎯 **Focused Specialist** (41 traders)  
- **Perfil:** Concentram em poucos mercados específicos
- **PnL médio:** $890K
- **Características:** Concentração alta (0.78), 2-3 mercados dominantes
- **Exemplos:** Especializados só em eleições presidenciais

#### 💎 **High-Stakes Player** (35 traders)
- **Perfil:** Fazem trades grandes e arriscados
- **PnL médio:** $1.8M 
- **Características:** 40%+ dos trades >$1000, trade médio $2.800
- **Exemplos:** "Whales" que movem mercados inteiros

#### 🇺🇸 **Trump-Era Dominator** (52 traders)
- **Perfil:** Dominaram especificamente a Era Trump
- **PnL médio:** $1.1M
- **Características:** 85%+ da atividade entre Nov/2024-Jan/2025
- **Exemplos:** Entraram exclusivamente para as eleições

#### 🤖 **Balanced Operator** (34 traders)
- **Perfil:** Equilibram volume, diversificação e sizing
- **PnL médio:** $750K
- **Características:** Médias balanceadas em todas as dimensões
- **Exemplos:** Traders "sistemáticos" sem especialização extrema

---

## 🧠 Features Mais Discriminantes

Usando **Random Forest**, identificamos as variáveis que melhor separam os arquétipos:

| Rank | Feature | Importância | Interpretação |
|------|---------|-------------|---------------|
| 1 | **Era-Trump_trades** | 0.234 | Volume de atividade na Era Trump |
| 2 | **market_concentration** | 0.187 | Foco vs diversificação |
| 3 | **total_markets** | 0.156 | Número de mercados únicos |
| 4 | **risk_appetite** | 0.142 | % de trades grandes (>$1000) |
| 5 | **Era-Trump_trades_per_day** | 0.098 | Frequência durante Era Trump |
| 6 | **Era-Trump_avg_trade_size** | 0.089 | Sizing médio na Era Trump |

**Modelo de Classificação:** Consegue prever o arquétipo de um trader com **87% de acurácia** usando apenas essas 6 variáveis.

---

## 📊 Análise Comportamental

### Concentração vs Diversificação
- **Veteranos (Pré-Trump):** Mais diversificados (4.1 mercados médios)
- **Era Trump:** Mais focados (2.8 mercados médios)
- **Implicação:** Specialists dominaram a Era Trump

### Risk Appetite
- **Pré-Trump:** 12% de trades >$1000
- **Era Trump:** 31% de trades >$1000  
- **Implicação:** Maior apetite ao risco caracterizou os winners

### Frequência de Trading
- **Pré-Trump:** 0.8 trades/dia
- **Era Trump:** 3.2 trades/dia
- **Implicação:** Velocidade de execução virou vantagem competitiva

### Timing de Entry/Exit
- **Pré-Trump:** Buy ratio 0.48 (mais vendas)
- **Era Trump:** Buy ratio 0.52 (mais compras)
- **Implicação:** Era Trump favoreceu estratégias "long" vs contrarian

---

## ⚖️ Comparação Entre Safras

### Performance Relativa

```
Safra               Traders   PnL Médio    Trades Médios   Concentração
──────────────────────────────────────────────────────────────────────
Era-Trump-Focused      89     $1.12M          94           0.68
Trump-Era-Active       67     $890K           76           0.51  
Pre-Trump-Focused      28     $145K           19           0.43
Multi-Period           45     $234K           45           0.38
```

### Insights Estratégicos

1. **Event-driven dominance:** Traders que entraram especificamente para as eleições obtiveram os maiores retornos
2. **Specialization premium:** Focus em poucos mercados superou diversificação
3. **Obsolescence rate:** Apenas 15% dos top performers pré-eleição mantiveram relevância
4. **Velocity advantage:** Alta frequência correlacionou com alta performance

---

## 🔮 Implicações para Estratégias de Trading

### Para Copy Trading (S1)
- **Foco temporal:** Priorizar traders da safra atual vs históricos
- **Filtering:** Usar arquétipo como critério de seleção
- **Weight allocation:** Ponderar por "Era dominante" além de PnL

### Para Early Value (S2)  
- **Market selection:** Mercados com baixa concentração de specialists
- **Timing:** Entrar antes que High-Volume Diversified players identifiquem valor
- **Sizing:** Trades menores para evitar competição direta com High-Stakes Players

### Para Momentum (S3)
- **Speed premium:** Arquétipos com alta frequência já "precificaram" movimentos
- **Contrarian opportunities:** Ir contra consensus de Trump-Era Dominators em mercados não-políticos

### Para Mean Reversion (S4)
- **Overreaction identification:** Focused Specialists criam distorções em seus mercados
- **Cross-market arbitrage:** Aproveitar concentração extrema em Politics vs outros temas

---

## 🛠️ Modelo Preditivo de Arquétipos

**Input Features:**
```python
features = [
    'total_trades', 'total_markets', 'market_concentration', 
    'risk_appetite', 'Era-Trump_trades', 'Era-Trump_markets',
    'Era-Trump_avg_trade_size', 'Era-Trump_trades_per_day'
]
```

**Output:** Classificação automática em um dos 5 arquétipos

**Performance:** 87% accuracy, 0.83 F1-score médio

**Uso prático:** 
- Classificar novos traders automaticamente
- Ajustar estratégias baseado no arquétipo detectado  
- Identificar mudanças comportamentais em traders existentes

---

## 🔬 Metodologia Técnica

### Data Pipeline
1. **Extração:** 788 traders, 1.6M trades, 32K posições
2. **Feature Engineering:** 35+ features comportamentais por trader/período
3. **Clustering:** K-means com StandardScaler + PCA 
4. **Classification:** Random Forest com cross-validation
5. **Validation:** Hold-out 30% para teste

### Datasets Gerados
- `trader_features_analysis.csv` — Features completas (788 traders)
- `top200_traders_with_clusters.csv` — Top 200 com clusters 
- `trader_cohorts_results.json` — Resultados consolidados

### Notebooks
- `trader_cohorts_analysis.ipynb` — Análise completa
- `historical_analysis.ipynb` — Contexto histórico

---

## 📈 Próximos Passos

### Análises Complementares
1. **Network Analysis:** Como traders influenciam uns aos outros por arquétipo
2. **Market Impact:** Qual arquétipo move mais preços
3. **Seasonal Patterns:** Como arquétipos se comportam em diferentes eventos
4. **Performance Attribution:** Decomposição de alpha por arquétipo

### Implementação Prática  
1. **Real-time Classification:** API para classificar traders novos
2. **Strategy Adaptation:** Ajustar S1-S5 baseado em distribuição de arquétipos
3. **Risk Management:** Limites diferenciados por arquétipo
4. **Backtesting:** Simular performance histórica com classificação automática

---

*Análise realizada em fevereiro de 2026 • Base: 788 traders • Período: Out/2021 - Fev/2026*
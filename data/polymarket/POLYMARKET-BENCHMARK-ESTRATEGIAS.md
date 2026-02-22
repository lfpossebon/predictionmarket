# Benchmark de Estratégias de Investimento em Mercados de Previsão
> Estudo aprofundado — Polymarket, Kalshi, e mercados de previsão em geral
> Compilado: 21/02/2026

---

## 1. Panorama do Mercado

### Escala atual (2025-2026)
- **Polymarket:** $9B+ volume acumulado em 2024, 314.500 traders ativos em dez/2024
- **Kalshi:** Avaliação de $11B após rodada de $1B (nov/2025), agora maior por volume segundo DeFiLlama
- **Volume mensal total:** De <$100M para >$13B entre 2024-2025
- **Transações mensais:** De ~240K para >43M no mesmo período
- **Mercados ativos:** ~500+ no Polymarket, 300+ no Kalshi

### Dados acadêmicos chave
- **92% dos traders perdem dinheiro** no Polymarket (análise de 6 meses, Q3/2025-Q1/2026)
- **7.6% são lucrativos** — e usam estratégias sistemáticas, não "opinião"
- **Retorno médio pré-fee em Kalshi: -20%** (UCD Working Paper 2025) — devido ao favourite-longshot bias
- **$40M de lucro extraído via arbitragem** no Polymarket (paper arXiv, ago/2025)
- **Fed researchers** confirmaram que prediction markets têm "forecast record perfeito" no dia anterior a reuniões do FOMC (fev/2026)

### Favourite-Longshot Bias (Viés fundamental)
Pesquisa do UCD/CEPR analisando 300.000+ contratos no Kalshi:
- Contratos **baratos** (5-10¢) ganham **menos** do que o preço sugere → retorno negativo de -60%
- Contratos **caros** (90-95¢) ganham **ligeiramente mais** → retorno levemente positivo
- **Makers** perdem em média -10%, **Takers** perdem -32%
- **Implicação:** Ser maker (prover liquidez) é estruturalmente melhor que ser taker

---

## 2. As 8 Estratégias Documentadas

### S1 — Favourite Compounding ("Bonding")
**Tipo:** Baixo risco, baixo retorno | **Horizonte:** Dias a semanas

**Como funciona:** Comprar mercados precificados a 95¢+ perto da resolução. Retorno de 1-5% por trade, mas com capital quase garantido.

**Benchmarks:**
- 5% de retorno em 24h = ~1.800% anualizado teórico
- Traders como Sharky6999, LlamaEnjoyer, rwo acumulam $150K+ com poucos trades/semana
- Win rate: >95%

**Riscos:**
- Tail risk: o evento "certo" não acontece (Black Swan)
- Capital empatado esperando resolução
- Retorno absoluto por trade é pequeno — precisa de capital alto

**Perfil ideal:** Capital alto, aversão a risco, paciência

---

### S2 — Arbitragem Binária (YES + NO < $1)
**Tipo:** Risco zero teórico | **Horizonte:** Segundos a minutos

**Como funciona:** Quando YES + NO de um mercado somam < $1.00, comprar ambos garante lucro na resolução.

**Benchmarks:**
- Spread médio de arbitragem em 2026: **0.3%** (quase morto)
- Duração média da oportunidade: **2.7 segundos** (era 12.3s em 2024)
- **73% dos lucros** capturados por bots sub-100ms
- **$40M** total extraído historicamente (paper acadêmico)

**Riscos:**
- Competição extrema com bots HFT
- Gas fees podem comer o spread
- Precisa de infra dedicada (RPC nodes Polygon)

**Status 2026:** Essencialmente morta para humanos. Só viável com bots sub-segundo.

---

### S3 — Arbitragem Multi-Outcome / Combinatorial
**Tipo:** Risco zero teórico | **Horizonte:** Minutos

**Como funciona:** Em mercados multi-outcome (ex: "Quem ganha o Oscar"), se a soma de todos os asks < $1.00, comprar todos garante lucro.

**Benchmarks:**
- Mais complexa que binária, menos competição
- Paper arXiv identifica "Market Rebalancing Arbitrage" (intra-mercado) e "Combinatorial Arbitrage" (cross-mercado)
- Requer scanning automatizado de muitos mercados simultaneamente

**Riscos:**
- Perna fraca (um outcome com pouca liquidez) pode impedir execução completa
- Mais difícil de automatizar que arbitragem binária

---

### S4 — Arbitragem Cross-Platform
**Tipo:** Risco baixo | **Horizonte:** Minutos a horas

**Como funciona:** Mesmo evento precificado diferente em Polymarket vs. Kalshi vs. outros. Comprar no mais barato, vender no mais caro.

**Benchmarks:**
- Oportunidades existem especialmente entre plataformas crypto (Polymarket) e reguladas (Kalshi)
- Paper SSRN "Price Discovery in Modern Prediction Markets" (jul/2025) documenta dinâmicas de price discovery entre plataformas
- Latência é menor fator que em arb intra-plataforma

**Riscos:**
- Capital precisa estar em múltiplas plataformas
- Regras de resolução podem diferir entre plataformas (mesma pergunta, critérios diferentes)
- Risco de contraparte em plataformas não-reguladas

---

### S5 — Market Making / Liquidity Provision
**Tipo:** Risco baixo-médio | **Horizonte:** Contínuo

**Como funciona:** Colocar ordens dos dois lados (buy + sell), capturar o spread. Lucra independente do outcome.

**Benchmarks reais:**
- **@defiance_cr:** Começou com $10K, fez $200/dia inicialmente, escalou para **$700-800/dia** no pico
- Um LP perdeu -$200K em trades mas fez **+$400K** sendo LP
- Outro fez $300K de LP = 1.5x do lucro em trading
- **Retorno backtested:** 0.5-2% mensal com <1% drawdown (conservador)
- **APY equivalente em mercados novos:** 80-200%
- Polymarket Liquidity Rewards: bônus por prover liquidez bilateral (quase 3x vs. unilateral)

**Regras de ouro:**
- Escolher mercados de **baixa volatilidade** + **alto reward**
- Nunca ter >30% de inventário em um lado
- Alargar spread automaticamente quando volatilidade sobe
- Retirar liquidez antes de eventos (breaking news, debates, dados econômicos)
- Spreads mais apertados = mais rewards, mas mais risco

**Riscos:**
- Adverse selection: traders informados operam contra você
- Inventory risk: ficar preso com muito YES ou NO quando mercado move
- Rewards diminuíram pós-eleição 2024

**Status 2026:** Ainda viável e uma das estratégias mais consistentes. Competição aumentou (3-4 LPs sérios em 2024 → mais agora), mas mercados novos continuam surgindo.

---

### S6 — Catalyst Momentum / Event-Driven
**Tipo:** Risco médio-alto | **Horizonte:** Minutos a horas

**Como funciona:** Comprar rapidamente após breaking news, antes do mercado reprecificar. Vender quando liquidez absorve o movimento.

**Benchmarks:**
- Janela de oportunidade: 30 segundos a 5 minutos pós-notícia
- Traders com IA/ensemble models: GPT-4 + Claude + modelo fine-tuned → consenso em <10 segundos
- Exemplo real: notícia sobre testemunha recantando em caso Trump → bot captou spread de 13¢ em posição de $2K = **$896 em <10min**
- Mention markets: traders como "Axios" com **96% win rate** em mercados de menções (apostam no que será dito em discursos)
- **fengdubiying:** $3.2M no campeonato de League of Legends com edge de domain expertise

**O que separa os vencedores:**
- Velocidade de processamento de informação (AI >> humano)
- Calendário de eventos integrado
- Sentiment analysis em tempo real
- Stops mecânicos predefinidos

**Riscos:**
- Chegar tarde = comprar no topo
- Reversal pós-evento
- Black swans sem precedente

---

### S7 — Mispricing Hunting / Value Betting
**Tipo:** Risco médio | **Horizonte:** Dias a semanas

**Como funciona:** Identificar mercados onde o preço não reflete a probabilidade real. Comprar barato, esperar correção ou resolução.

**Benchmarks:**
- Exemplo: "Makina public sale >$10M?" abriu com NO a 25¢, moveu para 95¢ (quem comprou NO early fez 280%+)
- Top trader Kalshi: $1K → $80K com estratégia de mispricing
- Favourite-longshot bias cria mispricing sistemático em contratos baratos
- Mercados novos (<48h) têm mais mispricing que mercados maduros

**Edge necessário:**
- Domain expertise específica (crypto, política, esportes)
- Modelos próprios de fair value (Bayesian, ensemble AI)
- Paciência — pode levar semanas para o mercado corrigir

**Riscos:**
- "O mercado pode ficar irracional mais tempo do que você solvente"
- Informação assimétrica real (insiders)

---

### S8 — Copy Trading / Whale Following
**Tipo:** Risco médio | **Horizonte:** Variável

**Como funciona:** Monitorar wallets de top performers e replicar suas posições.

**Benchmarks:**
- Top 5 all-time PnL fizeram fortuna em política (Fredi9999, Theo4, etc.)
- "Sharp traders" = pequena fração que captura a maioria dos lucros
- Polymarket Analytics: P&L tracking por categoria, atividade em tempo real
- Reddit: traders acompanham 3-5 wallets diversificadas como "alpha source"
- Top performers reportam **15-30% retorno mensal** (laikalabs.ai)

**O que funciona:**
- Seguir traders que ganham de **centenas de trades**, não de poucos (consistência > sorte)
- Especialistas em categoria > generalistas
- Monitorar via Polymarket Analytics ou betmoar.fun
- **Nossa abordagem (basket consensus)** adiciona camada de segurança: só copiar quando 80%+ concordam

**Riscos:**
- Sybils (múltiplas wallets = 1 pessoa)
- Insider trading (wallets novas com 1 grande aposta certeira = insider, não replicável)
- Latência: preço já moveu quando você copia
- Trader muda de estratégia

---

## 3. Estratégia Adicional: Insider Detection
**Tipo:** Alto risco, alto retorno | **Horizonte:** Evento-specific

Padrão identificado: wallets recém-criadas com **uma única grande aposta** de alta convicção → frequentemente insiders.

**Exemplo documentado:** Mercado "Que dia o Gemini 3.0 será lançado?" — duas wallets novas apostaram pesado em 18 de novembro no primeiro dia. Ambas fizeram $50K+.

**Como detectar:**
- Wallet nova (< 7 dias)
- Uma ou poucas posições grandes
- Alta convicção (>$10K em único mercado)
- Outros trades pequenos e/ou perdedores

**Risco:** Ilegal em mercados regulados, ético questionável. Mas a informação é pública on-chain.

---

## 4. Comparação Consolidada

| Estratégia | Retorno Estimado | Win Rate | Risco | Automação | Capital Mínimo | Competição |
|-----------|-----------------|----------|-------|-----------|----------------|------------|
| **Favourite Compounding** | 1-5%/trade, ~30-60% a.a. | >95% | Baixo (tail) | Média | Alto ($50K+) | Média |
| **Arb Binária** | ~0.3%/trade | ~100% | Zero | Alta (HFT) | Médio | Extrema |
| **Arb Multi-Outcome** | 1-3%/trade | ~100% | Zero | Alta | Médio | Alta |
| **Arb Cross-Platform** | 1-5%/trade | ~95% | Baixo | Alta | Alto (multi-plat) | Média |
| **Market Making** | 0.5-2%/mês, 80-200% APY | 78-85% | Baixo-Médio | Alta | Médio ($10K+) | Crescente |
| **Catalyst/Momentum** | 3-8%/mês | 65-75% | Médio-Alto | Média-Alta | Baixo | Média |
| **Mispricing/Value** | Variável, 50%+ por trade | 60-70% | Médio | Baixa | Baixo | Baixa |
| **Copy Trading** | 15-30%/mês (top) | 55-65% | Médio | Média-Alta | Baixo | Baixa |

---

## 5. Insights para Nosso Projeto

### O que a pesquisa nos diz:

1. **Diversificação de estratégias é crucial** — nenhuma estratégia funciona sempre. O blend é o caminho certo.

2. **Market Making é a estratégia mais consistente** — devemos considerar como S6 no nosso framework. Retorno previsível, baixa correlação com as outras.

3. **Arbitragem pura está morta para humanos** — mas arbitragem combinatorial e cross-platform ainda têm espaço. Manter como S5 mas com expectativas realistas.

4. **Copy Trading funciona quando baseado em consistência, não em PnL absoluto** — nosso approach de basket + consenso + sybil detection está alinhado com as best practices.

5. **Favourite-longshot bias é explorável** — comprar sistematicamente contratos caros (>80¢) e vender baratos (<20¢) tem edge positivo documentado academicamente.

6. **AI-powered probability estimation é o novo edge** — ensemble de LLMs para estimar fair value supera humanos em velocidade e reduz bias.

7. **Especialização por categoria gera alpha** — os maiores winners são especialistas (fengdubiying em esports, Fredi9999 em política). Nossos baskets por tema estão no caminho certo.

8. **92% perdem dinheiro** — isso significa que um sistema disciplinado e baseado em dados já começa com vantagem enorme sobre o participante médio.

### Estratégias recomendadas para nosso blend (atualizado):

| Prioridade | Estratégia | Alocação sugerida | Justificativa |
|-----------|-----------|-------------------|---------------|
| 1 | **Copy Trading (Basket)** | 25% | Nossa tese principal, edge de inteligência coletiva |
| 2 | **Market Making** | 20% | Mais consistente, retorno previsível, hedge natural |
| 3 | **Favourite Compounding** | 20% | Baixo risco, bom para gerar retorno estável |
| 4 | **Mispricing/Value** | 15% | Edge de domain expertise + AI fair value |
| 5 | **Catalyst/Momentum** | 10% | Oportunístico, AI-powered |
| 6 | **Arb Correlação** | 10% | Quando disponível, risco quase zero |

---

## 6. Fontes e Referências

### Papers Acadêmicos
1. **"Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets"** — arXiv:2508.03474 (ago/2025). $40M em lucro de arbitragem no Polymarket.
2. **"Makers and Takers"** — UCD Working Paper 2025_19. Retorno médio pré-fee de -20% no Kalshi, favourite-longshot bias.
3. **"Price Discovery and Trading in Modern Prediction Markets"** — SSRN 5331995 (jul/2025). Price discovery entre Polymarket, Kalshi, PredictIt, Robinhood.
4. **"How Manipulable Are Prediction Markets?"** — arXiv:2503.03312 (mar/2025). Análise experimental de manipulabilidade.
5. **"Price formation in field prediction markets"** — ScienceDirect (jan/2024). Sharp traders com informational price impact positivo.

### Análises de Mercado
6. **"5 Ways to Make $100K on Polymarket"** — Monolith/Medium (dez/2025). Estratégias de whales documentadas com wallets específicas.
7. **"Beyond Simple Arbitrage: 4 Strategies Bots Actually Profit From"** — Medium/Illumination (fev/2026). 92% perdem, análise de 6 meses de orderbook.
8. **"The Complete Polymarket Playbook"** — The Capital/Medium (jan/2026). $9B volume, battlefield sofisticado.
9. **"Automated Market Making on Polymarket"** — Polymarket Newsletter (mai/2025). @defiance_cr: $700-800/dia com MM bot, código open-source.
10. **"This Tool Finds Traders with 96% Win Rates"** — Polymarket Newsletter (jun/2025). Polymarket Analytics, padrões de traders lucrativos.
11. **"Top 10 Polymarket Trading Strategies"** — DataWallet (dez/2025). Framework de 10 estratégias com exemplos.

### Ferramentas e Dados
12. **Polymarket Analytics** — polymarketanalytics.com. P&L tracking, leaderboards por categoria, top holders.
13. **BetMoar** — betmoar.fun. Análise de portfolio de wallets, LP tracking.
14. **Calibration City** — manifund.org. Calibração cross-platform (Kalshi, Manifold, Metaculus, Polymarket).
15. **poly-maker** — github.com/warproxxx/poly-maker. Bot open-source de market making.

---

*Documento de referência para o projeto Multi-Strategy Trading System*
*Atualizar conforme novos dados e papers surgirem*

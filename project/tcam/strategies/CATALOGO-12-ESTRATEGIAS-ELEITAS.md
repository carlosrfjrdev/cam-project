---
template: CATALOGO-ESTRATEGIAS
phase: Estudo livre (research-only)
status: Draft 1.0 — catálogo consolidado
produto: CaM
escopo: análise de mercado livre — trava constitucional DESLIGADA por ordem do Founder
data: 2026-06-03
lead: Leo
co_participacao: Jim (quant/edge), Nassim (risco/ruína), Barsi (renda/dividendos), Ray (macro/regime)
aviso: documento de estudo — NÃO é tese aprovada, NÃO é ordem, NÃO autoriza execução
---

# Catálogo de 12 Estratégias — Estudo Livre de Mercado

> **Solicitação do Founder:** eleger 3 derivativos intraday, 2 à vista curto/intraday,
> 2 à vista swing, 2 long & short (+1 L&S à vista adicionada na 2ª rodada → 3),
> 1 FII, 1 holding dividendos. **Todas as 11 originais aprovadas; LS3 acrescentada.**
> **Modo:** estudo livre — a trava da Constituição do CaM foi **desligada por ordem
> explícita do Founder** *apenas para fins deste catálogo* (sem limite de 2 contratos,
> sem janelas vedadas, sem escopo WIN/WDO-only).
>
> ⚠️ **Fronteira:** research-only. Nada aqui é tese aprovada no registry, ordem de
> execução, ou autorização de aporte. Eleger ≠ operar. Qualquer estratégia que um dia
> entre no CaM real volta a passar pelos gates constitucionais (Arts. 28º–30º) e pelo
> Risk Engine. Os caixas não se misturam: derivativo (Jim/Wyck/Nassim) e Carteira Hard
> (Barsi) são perímetros separados.

---

## Sumário das 12 eleitas

| # | Estratégia | Categoria | Lead | Qualidade do edge | Veredito |
|---|---|---|---|---|---|
| **D1** | ORB-30 filtrado por regime (WIN) | Derivativo intraday | Jim | ⭐⭐⭐ | Bom 1º motor intraday |
| **D2** | VWAP Mean-Reversion fade (WDO) | Derivativo intraday | Jim | ⭐⭐ | Cético — picking pennies |
| **D3** | Spread/lead-lag WIN×WDO | Derivativo intraday | Jim | ⭐⭐⭐⭐ | Alto teto, exige infra |
| **V1** | Gap-and-Go com confirmação de fluxo | Ação à vista intraday | Jim | ⭐⭐½ | Complementar |
| **V2** | Mean reversion oversold (RSI2 + MM200) | Ação à vista curto | Jim | ⭐⭐⭐ | OK com filtro de tendência |
| **S1** | Momentum cross-sectional | Ação à vista swing | Jim | ⭐⭐⭐⭐⭐ | **Top pick** |
| **S2** | Pullback em tendência | Ação à vista swing | Jim | ⭐⭐⭐⭐ | Sólido se mecanizado |
| **LS1** | Spread WIN×WDO intraday (z-score) | Long & short intraday | Nassim | ⭐⭐ | Traiçoeira no custo |
| **LS2** | Pair trading setorial (cointegração) | Long & short swing | Nassim | ⭐⭐⭐ | Mais defensável das duas |
| **LS3** | Pair trading ON×PN mesmo emissor | Long & short intraday (à vista) | Nassim | ⭐⭐ | Tese limpa, refém do custo |
| **F1** | FII Core+Yield (renda imobiliária) | FIIs | Barsi | ⭐⭐⭐⭐ | Espinha de renda mensal |
| **H1** | Quality Dividend Hold (7 indicadores) | Holding dividendos | Barsi | ⭐⭐⭐⭐⭐ | Destino-fim do Harvest |

> **Nota:** LS1 e D3 são a **mesma estrutura** (spread WIN×WDO) vista por duas lentes —
> Jim pela ótica de edge, Nassim pela ótica de ruína. Mantidas como entradas distintas
> porque foram pedidas em categorias diferentes (derivativo vs long&short), mas operá-las
> juntas seria **uma aposta, não duas** (ver Lente de Risco §IV).

---

## I. Enquadramento de regime (Ray) — read-only, incerteza rotulada

> Ray não tem dados ao vivo. Tudo que depende de cotação em 03/06/2026 é **[HIPÓTESE]**;
> o estrutural é **[FATO]**.

**Fatos estruturais:** Brasil tem juro real alto → renda fixa é concorrente forte de toda estratégia de risco. 2026 é **ano eleitoral** (outubro) → prêmio de incerteza e vol concentrada no 2º semestre. B3 tem liquidez concentrada e dependente de fluxo estrangeiro.

**Hipóteses de cenário:** Selic ainda restritiva; inflação desacelerando porém pegajosa; vol baixa-a-média agora subindo rumo à eleição; fluxo estrangeiro reativo.

**Síntese:** ambiente provável de **range macro com vol contida no curto prazo e assimetria de risco para o 2º semestre** — colher carrego e prêmio, evitar tese direcional de convicção longa antes da eleição.

| Regime hipotético | Prosperam | Sofrem |
|---|---|---|
| **Lateral + vol baixa** (base curto prazo) | Long&Short, carrego/dividendos, range intraday disciplinado | Swing direcional, breakout, growth/small cap |
| **Lateral + vol alta** (spike eleitoral) | Day trade reativo (risco travado), hedge | Swing alavancado, FII ilíquido, overnight sem proteção |
| **Tendência de alta** (afrouxamento + fluxo) | Swing comprado, FII tijolo, beta, small caps | Long&Short puro, caixa parado |
| **Tendência de baixa / risk-off** | Caixa, dividendos defensivos, perna short do L&S, hedge | Tudo alavancado, day trade contra-tendência, swing comprado |

> No regime-base (lateral + vol contida), o catálogo deveria **priorizar estudo** de
> Long&Short, dividendos/holding e day trade disciplinado, e tratar **swing direcional**
> com ceticismo até haver tendência confirmada.

---

## II. Premissas de custo (B3, jun/2026) — valem para todas as fichas (Jim)

| Item | Day trade | Swing |
|---|---|---|
| Corretagem | ~R$ 0–0,50/contrato (mini) · ~R$ 0–4,90/ordem (ação) | idem ação |
| Emolumentos mini índice/dólar | ~R$ 0,11–0,28/contrato/lado | — |
| Emolumentos ação | ~0,03% do volume (+ liquidação) | ~0,03% |
| Slippage realista | 1 tick WIN (5 pts = R$ 1,00) · 1 tick WDO (0,5 pt = R$ 5,00) | 1–3 centavos/ação |
| IR | 20% sobre lucro + IRRF 1% | 15% (isenção até R$ 20k/mês em ações) |
| Carrego "invisível" | — | gap overnight / aluguel BTC para short |

**Régua de aprovação anti-data-snooping (Jim):** DSR > 0; ≥ 200 trades out-of-sample; walk-forward com ≥ 60% das janelas lucrativas líquidas; expectância líquida positiva **após o pior quartil de custos**; sem parâmetro com sensibilidade de penhasco (cliff). **Win rate cru não prova nada — só expectância líquida out-of-sample.**

---

# III. AS 11 FICHAS

## D — Derivativos intraday (Jim)

### D1 — ORB-30 filtrado por regime (WIN)
- **Tese:** o leilão de abertura concentra ordem represada; rompimento da faixa dos primeiros 15–30 min **com expansão de range** captura cauda direcional antes da reprecificação. Ganha de traders atrasados e stops mal posicionados. O edge está em **filtrar falsos rompimentos**, não no rompimento (setup saturado no varejo BR).
- **Ativo/TF:** WIN (cheio IND para escala) · faixa 15–30 min, gestão M5, sem overnight.
- **Lógica:** range [H,L] dos 30 min iniciais; entra no rompimento **só se** ATR(range) > mediana 20d **e** regime ≠ "lateral comprimido"; stop no extremo oposto; alvo 1 = 1×range (parcial) + runner por VWAP/EMA; anula se reverter para dentro em ≤ 2 candles.
- **Edge típico:** WR 38–46%, R:R 1,8–2,4:1, ~0,8–1,2 trades/dia. Bruta ~+0,25R; **líquida ~+0,12–0,18R**.
- **Falhas:** dias de range (morte por mil cortes); overfit do tamanho da janela (15/30/45 min); clusters de perdas em sequência de dias laterais.
- **Backtest deve provar:** robustez ao parâmetro da janela (curva chata, não pico); expectância líquida no subconjunto de dias filtrados; walk-forward 2019–2026; que o filtro **adiciona** Sharpe vs ORB ingênuo.
- **Verdict:** **promissor mas saturado.** Bom primeiro motor por liquidez/simplicidade, *desde que* o edge venha do filtro de regime. Sem filtro, é coin-flip caro.

### D2 — VWAP Mean-Reversion fade (WDO)
- **Tese:** WDO sem choque macro é mean-reverting intradiário (hedge cambial + arbitragem com dólar à vista). Ganha de momentum tardio que persegue extensões de 2–2,5σ insustentáveis. **Frágil a notícia:** desvio informacional vira continuação.
- **Ativo/TF:** WDO (cheio DOL) · M1–M5.
- **Lógica:** VWAP ±1,5σ/±2,5σ; fade na tocada de 2σ **fora** de janela de evento (hard-block macro) e só em regime de range; stop além de 3σ, alvo no VWAP, sem runner; kill se romper 3σ com volume crescente.
- **Edge típico:** WR **alto 58–68%**, R:R **invertido ~0,6–0,8:1**, 3–6 trades/dia. Líquida é o calcanhar — tick WDO (R$ 5) + IR comem alvo curto.
- **Falhas:** **risco de ruína assimétrico** (1 choque devolve 10 vitórias); sensível a custo; overfit no nível de σ.
- **Backtest deve provar:** distribuição de **tail** (pior trade/cluster, não só média); slippage agressivo de 2 ticks; que o hard-block de eventos decapita o tail; Monte Carlo de cauda **empírica**, não gaussiana.
- **Verdict:** **cético.** WR alto é a sereia. Só passa se provar que o filtro de evento mata o tail. Prioridade baixa.

### D3 — Spread/lead-lag WIN×WDO (Jim)
- **Tese:** índice e dólar têm correlação negativa estrutural que desgruda/refaz em janelas curtas (lead-lag). Ganha de **dessincronização de fluxo** entre os books, não de direção. Market-neutral, o menos saturado no varejo (exige operar dois books).
- **Ativo/TF:** WIN + WDO simultâneos · M1–M5, reversão em minutos.
- **Lógica:** beta dinâmico (Kalman/EWMA) WIN~f(WDO); z-score do resíduo; entra contra desvios > ±2σ; saída em z=0; stop em z>3σ; **desliga se ADF rejeitar** estacionariedade.
- **Edge típico:** WR 55–62%, R:R ~1:1, 2–4/dia. Sharpe maior que D1/D2 por menor exposição direcional; **líquida sofre custo dobrado** (2 pernas, 2 IRs, 2 slippages).
- **Falhas:** quebra de cointegração; custo dobrado; risco de execução (perna solta = direcional não-intencional); beta mal estimado.
- **Backtest deve provar:** estabilidade da cointegração out-of-sample (Engle-Granger/Johansen rolling); que sobrevive ao custo 2×; DSR rigoroso (pairs é paraíso do snooping); meia-vida do spread (Ornstein-Uhlenbeck) coerente com o TF.
- **Verdict:** **o mais interessante e o mais traiçoeiro.** Melhor Sharpe potencial dos 3 derivativos **se** a infra de execução simultânea existir e o custo couber. ⚠️ Ver a lente de Nassim em **LS1** — é a mesma estrutura.

---

## V — Ações à vista curto prazo / intraday (Jim)

### V1 — Gap-and-Go com confirmação de fluxo
- **Tese:** ações com gap de abertura sustentado por notícia/volume continuam na direção do gap nas primeiras horas (underreaction do varejo). Ganha de participantes lentos e de quem fada o gap cedo. Funciona em blue chips de alto volume.
- **Ativo/TF:** top 10–15 em liquidez (PETR4, VALE3, ITUB4, BBAS3, B3SA3...) · 1ª hora, sem overnight no protótipo.
- **Lógica:** filtro gap > X% **e** volume 1ª barra > N×média **e** catalisador identificável; entra no rompimento da máxima do 1º candle no sentido do gap; stop no fundo do candle; alvo por ATR/trailing VWAP; não opera fade.
- **Edge típico:** WR 40–48%, R:R 1,5–2,2:1, frequência **irregular** (alguns dias zero). Líquida ~+0,1R (corretagem de ação pesa mais + IR 20%).
- **Falhas:** dias sem gap (frequência irregular mina disciplina); gap exhaustion; **selection bias** (escolher "as melhores" em retrospecto); slippage em menos líquidas.
- **Backtest deve provar:** **universo fixo ex-ante** (watchlist antes, não ganhadores depois); expectância líquida com corretagem real; que o filtro separa gaps que continuam dos que falham; robustez ao threshold.
- **Verdict:** **razoável, secundário.** Edge de underreaction é real e documentado, mas custo unitário pior e dependência de catalisador. Complementar, não motor.

### V2 — Mean reversion oversold (RSI2 + MM200)
- **Tese:** ações líquidas que caem muito e rápido sem mudança de fundamento (pânico, stop cascata, margin call alheio) quicam no curtíssimo prazo — provedores de liquidez são pagos por absorver o vendedor forçado (Connors RSI2 adaptado à B3). Falha em tendência estrutural de baixa (faca caindo).
- **Ativo/TF:** blue chips líquidas + BOVA11 · entrada intraday no clímax, saída 1–3 dias.
- **Lógica:** RSI2 < 5–10 **e** preço > MM200 (só compra dip em uptrend estrutural); entra no clímax de volume; saída por reversão à MM5 ou tempo; stop largo/por estrutura (MR não tolera stop apertado).
- **Edge típico:** WR **alto 62–72%**, R:R ~0,7–1:1. Líquida sobrevive melhor que MR de derivativo (movimento % > tick; se > 1 dia, IR 15%).
- **Falhas:** **o bounce que não veio** (bear estrutural); stop largo = perda grande na cauda esquerda; filtro de tendência é o que separa edge de suicídio.
- **Backtest deve provar:** que o filtro MM200 **decapita a cauda esquerda** (comparar com/sem); tail em crashes (2008/2020/2022); expectância líquida com hold real; DSR contra variações de RSI; que não é só beta disfarçado.
- **Verdict:** **bom perfil, WR honesto, cuidado com o tail.** Defensável com filtro MM200 e tail testado. Melhor relação esforço/edge das duas de ações intraday.

---

## S — Ações à vista swing / médio prazo (Jim)

### S1 — Momentum cross-sectional ⭐ Top pick
- **Tese:** o **fator momentum** é a anomalia mais robusta e replicada da literatura (Jegadeesh-Titman, Asness): quem subiu mais em 3–12 meses tende a continuar. Causa: underreaction + herding institucional + fluxo que persegue performance. Edge de **prêmio de risco** (você é pago por carregar o fator), não de timing. **Não foi descoberto no backtest — replicado em 40+ países e 200 anos** (oposto de data-snooping).
- **Ativo/TF:** universo IBrX-100 · rebalance mensal/quinzenal, hold semanas–meses.
- **Lógica:** rankeia por retorno 3–6m (skip último mês — evita reversão de curto prazo); long top decil/quintil; reduz exposição quando vol de mercado explode (momentum crash risk); stop por quebra de força relativa.
- **Edge típico:** Sharpe do fator ~0,5–0,8 isolado; WR por trade ~50–55% mas **assimetria positiva**. Líquida favorável: hold longo dilui custo, IR 15%, isenção R$ 20k/mês ajuda.
- **Falhas:** **momentum crash** (perdas concentradas em viradas de regime — skew negativo, curtose alta); crowding; turnover se rebalancear rápido; longos períodos de underperformance do fator.
- **Backtest deve provar:** que não é só beta (controlar por Ibov/fatores); robustez do lookback (3/6/12m); que o filtro de vol reduz o crash sem matar retorno; custo líquido com turnover e isenção fiscal modelada.
- **Verdict:** **o edge mais cientificamente robusto do catálogo.** Forte aprovação para research; melhor fundamento para construção patrimonial (alinha com Harvest Rule). Único cuidado real: crash do fator, gerenciável com filtro de vol.

### S2 — Pullback em tendência
- **Tese:** em ações em tendência de alta estabelecida, correções rasas a suporte dinâmico (MM20/MM50, Fibonacci) oferecem entrada com risco definido na direção do fluxo dominante. Ganha de quem vende o pullback por medo. Comprar no recuo (barato, stop curto) em vez de no rompimento (caro) melhora o R:R. Sinergia com S1: comprar pullback dos líderes de momentum.
- **Ativo/TF:** líquidas em tendência clara · diário, hold dias–semanas.
- **Lógica:** filtro uptrend (MM50 > MM200, máximas ascendentes); espera pullback a suporte + sinal de retomada (martelo, engolfo); entra na confirmação; stop abaixo do pivot (curto → R:R favorável); deixa o vencedor correr.
- **Edge típico:** WR 40–50%, **R:R 2,5–4:1** (melhor do catálogo), frequência moderada. Líquida favorável (IR 15%, custo diluído, isenção possível).
- **Falhas:** **pullback que vira reversão** (comprou o topo da "correção"); whipsaw em laterais; **subjetividade** na definição de tendência/suporte (precisa de regra dura); poucos vencedores carregam o resultado (sair cedo mata o edge).
- **Backtest deve provar:** definição **mecânica e inviolável** de tendência/pullback (sem olho humano); que a assimetria R:R é real out-of-sample (não cherry-picking); sensibilidade ao critério de saída; que poucos vencedores grandes carregam (e não depende de 3 trades mágicos).
- **Verdict:** **sólido e complementar a S1.** Melhor R:R do catálogo, casa com momentum. Risco é a discricionariedade — **aprovo condicionado à mecanização total.** S1+S2 formam o núcleo swing mais defensável.

---

## LS — Long & short (Nassim) 🦢

> Nota de abertura de Nassim: *"Long&short vende-se como neutro a mercado. É a mentira
> mais cara do varejo quantitativo. Você trocou risco direcional (visível) por risco de
> convergência (invisível até te liquidar de uma vez)."* Leia os modos de falha e o
> dimensionamento **antes** da tese de edge.

### LS1 — Spread WIN×WDO intraday (z-score)
- **Tese:** WIN e WDO compartilham motor macro comum; fluxo descasa os dois temporariamente e o spread beta-ajustado reconverge em minutos–horas. Ganha de quem opera **uma perna só**. **Honestidade brutal (Nassim):** a relação é correlação de regime que **inverte em choque** — em risk-off violento podem cair juntos, e a premissa quebra exatamente quando você mais precisa.
- **Instrumentos:** WIN + WDO, hedge por **beta de P&L em R$** (não 1:1 em contratos — ponto vale diferente; sem ajuste de notional é aposta direcional disfarçada). Zera no fechamento, **nunca overnight**.
- **Lógica:** `S = P_win − β·P_wdo`, β por regressão rolante (β instável = não opera); entra em `|z|≥2`; stop em `|z|≥3,5`; stop de tempo (~90 min); alvo `|z|≤0,5`; fora de leilão e janela macro.
- **Edge típico:** WR enganoso **65–75%**, R:R **ruim 0,4–0,6**; 2–8 sinais/dia. **"Picking nickels in front of a steamroller"** — cauda esquerda gorda: 70 ganhos de R$30 apagados por 1 perda de R$2.500.
- **Falhas:** quebra de relação (as duas pernas perdem juntas, hedge vira alavancagem 2×); β instável; slippage no estresse; gap de microestrutura (não sai das duas pernas juntas); ruína por sequência.
- **Custos:** **4 boletas por trade** + emolumentos + ISS + slippage 2 pernas + IR 20%. Com edge bruto ~R$30 e fricção ~R$15–25/round-trip duplo, **o líquido pode ser zero ou negativo** — "programa de transferência de patrimônio para a corretora".
- **Dimensionamento:** trate como **direcional**, não neutro; risco ≤ **0,25% do capital**; correlação de P&L intradiário ≈ 1 (um dia ruim erra todos os trades juntos); kill diário rígido.
- **Verdict:** 🟡 **estudável, operacionalmente traiçoeira.** Edge fino demais para sobreviver aos custos no varejo. *"Provar-me errado é responsabilidade do Jim, com dados — não com narrativa."*

### LS2 — Pair trading setorial (cointegração, beta-neutro)
- **Tese:** duas empresas do mesmo setor compartilham drivers; o diferencial relativo oscila em torno de média de longo prazo. Quando estica por fluxo/notícia pontual (não fundamento), reconverge em dias–semanas. Ganha de quem superreage à notícia idiossincrática. **A pergunta que mata a tese:** a divergência é ruído (reverte) ou informação (não reverte)? Você não sabe na entrada — pode ficar long na Sears e short na Amazon.
- **Instrumentos:** par mesmo setor **cointegrado** (não só correlacionado); alternativas mais robustas: ação vs ETF setorial, ou ação vs índice futuro (WIN); short via **aluguel BTC**.
- **TF:** swing, dias–semanas; sinal diário; janela 60–120 pregões.
- **Lógica:** teste de cointegração (Engle-Granger/Johansen) — **sem cointegração, não há par**; spread = resíduo da regressão; **beta-neutralidade** (beta líquido ≈ 0, não notional igual); entra em `z≥2`; stop estatístico `z≥3–3,5` **e** stop fundamental (notícia estrutural mata a tese → sai já); saída em `z≤0,5` ou 20 pregões; **reteste de cointegração semanal**.
- **Edge típico:** WR 55–65%, R:R ~1,0–1,3 (melhor que o intraday), poucos sinais/mês por par (precisa de cesta). Mais robusto **se** a seleção for honesta — **survivorship bias** (excluir os pares que quebraram) é a fraude silenciosa do backtest.
- **Falhas:** **quebra de cointegração** (par descola permanentemente; short dispara + long afunda = cauda dupla); divergência era informação; **short squeeze + recall de aluguel** (não controla o timing da maior perda); beta drift; **correlação de quebras** (vários pares do setor quebram juntos — "cesta diversificada" tinha 1 fator escondido).
- **Custos:** **aluguel BTC** (corre todo dia, explode em papel difícil — o **imposto invisível** que come o edge); corretagem 2 pernas + 2 fechamentos; risco de recall; IR 15% swing.
- **Dimensionamento:** **perna short tem perda teoricamente ilimitada** — dimensione pela cauda da short; risco por par ≤ **0,5–1%**; 5 pares no mesmo setor = **~1 aposta com 5 boletas** (calcule exposição agregada de fator, R-08); cap de exposição short separado do long; modele a pior sequência plausível (4 pares quebrando no mês).
- **Verdict:** 🟢 **a mais defensável das duas** — horizonte para a tese funcionar, R:R aceitável, edge documentado. **PORÉM** carrega o pecado capital: a short pode arruinar de uma vez, e a diversificação de pares é frequentemente ilusória. Operável em estudo **só com** reteste de cointegração, stop fundamental, sizing pela cauda da short e cap setorial agregado. **Backtest tem que incluir os pares que quebraram.**

### LS3 — Pair trading INTRADAY de classes do mesmo emissor (ON×PN, à vista) ⭐⭐

> Nota de abertura de Nassim: *"LS1 casa dois derivativos macro. LS2 casa duas empresas
> distintas e reza por cointegração ao longo de semanas. LS3 casa a empresa COM ELA MESMA
> — PETR3 contra PETR4, ITUB3 contra ITUB4 — e fecha tudo antes do leilão. É a forma mais
> limpa de mean-reversion que existe à vista, porque não há risco fundamental divergindo:
> é o mesmo balanço, o mesmo lucro, o mesmo CNPJ. O que me mata aqui não é a tese quebrar —
> é o spread ser TÃO estreito que corretagem + emolumentos + aluguel da short comem o edge
> inteiro antes de eu acordar. O risco migrou do mercado para a planilha de custos."*

- **Categoria:** Long & short intraday (à vista).

- **Tese:** ações ordinárias (ON, sufixo 3) e preferenciais (PN, sufixo 4) do **mesmo
  emissor** são reivindicações sobre o **mesmo fluxo de caixa**, diferindo só em direito de
  voto, política de dividendos e liquidez relativa. O diferencial ON−PN oscila intradiário
  por **fluxo descasado** (uma classe recebe ordem de bloco, gira em índice, sofre
  arbitragem de ADR só de um lado) e **reconverge em minutos–horas** porque o valor
  econômico subjacente é idêntico. Compra-se a classe relativamente barata, vende-se a cara,
  beta-ajustado por P&L em R$, e **zera no fechamento**. Ganha de quem opera só uma classe.
  **Honestidade brutal (Nassim):** o spread ON×PN é o mais *defensável* (sem risco
  idiossincrático divergindo — é a mesma empresa, não há "ficar long na Sears e short na
  Amazon" do LS2) **e simultaneamente o mais fino**. A relação não quebra por fundamento;
  ela quebra por **evento de governança** (mudança de dividendo diferenciado, *tag along*,
  conversão de classe, OPA, migração para Novo Mercado que unifica classes) — e quando
  quebra, muda de patamar **de uma vez** e não volta. O modo de falha não é volatilidade:
  é o spread mensurado por anos virar pó em um *fato relevante*, com você posicionado.

- **Por que é distinta de LS1 e LS2:** **LS1** = derivativo (WIN×WDO), correlação de
  **regime macro** que inverte em choque, intraday. **LS2** = duas empresas **distintas** à
  vista, tese de **cointegração**, **swing** (dias–semanas). **LS3** = **mesmo emissor**,
  duas classes, tese de **identidade econômica** (não cointegração estatística — *quase
  arbitragem*), **intraday, zera no fechamento**. O motor de risco é diferente: LS2 morre de
  divergência fundamental que era informação; LS3 não tem divergência fundamental possível
  intradiário (é a mesma empresa) — morre de **custo > edge** e de **evento de governança
  raro**. Operar as três ≠ diversificar: são três motores distintos, mas LS3 e LS2
  compartilham o pecado da **perna short à vista** (aluguel/squeeze).

- **Instrumentos / universo / TF:**
  - **Universo primário (defensável):** pares ON×PN do **mesmo emissor**, altíssima
    liquidez nas duas classes — **PETR3×PETR4, ITUB3×ITUB4, BBDC3×BBDC4, GGBR3×GGBR4,
    ELET3×ELET6, ITSA3×ITSA4**. Critério duro: as **duas pernas** com book profundo o
    suficiente para entrar e sair sem mover o preço (a classe ON costuma ser a perna
    ilíquida — é ela que define o tamanho máximo, não a PN).
  - **Universo secundário (menos limpo, só se o emissor faltar par interno):** par
    intra-setorial de altíssima correlação e liquidez (ITUB4×BBDC4, VALE3×índice WIN) —
    **mas isso já é quase LS2 intraday**; o ON×PN do mesmo emissor é a forma canônica e a
    única que merece o ⭐ extra de "quase-arbitragem".
  - **Short intraday:** **venda a descoberto com recompra no mesmo dia** (zera antes do
    leilão → não precisa carregar aluguel overnight) **ou** posição de aluguel BTC
    pré-contratada. A disponibilidade/dificuldade da classe ON costuma ser o gargalo.
  - **TF:** intraday puro, sinal em candle de 1–5 min, hold minutos–horas. **Zera 100% no
    call de fechamento. NUNCA overnight** (evento de governança noturno = cauda).

- **Lógica:**
  - `S = P_ON − β·P_PN`, com **β por P&L em R$** (não 1:1 em quantidade — preços e lotes
    diferem; sem ajuste de notional é aposta direcional na classe mais cara disfarçada de
    spread). β por regressão rolante intradiária; **β instável ou drift = não opera**.
  - **Entrada** em `|z| ≥ 2` (z sobre média/desvio do spread intradiário, janela rolante do
    próprio pregão + ancoragem dos N pregões anteriores).
  - **Saída-alvo** em `|z| ≤ 0,3–0,5` (reversão à média do dia).
  - **Stop estatístico** em `|z| ≥ 3,5`; **stop de tempo** (~60–90 min sem convergir =
    desmonta — spread parado é sinal de mudança de patamar, não de oportunidade).
  - **Stop de evento (kill imediato):** qualquer *fato relevante / notícia de governança*
    no emissor durante o pregão → **fecha as duas pernas na hora**, não importa o z.
  - **Kill de fechamento:** ~15 min antes do call, **desmonta tudo** independentemente de z
    (não levar perna nenhuma para o leilão nem para overnight).
  - **Trava de microestrutura:** só entra se conseguir **as duas pernas** com spread de
    book aceitável; se uma perna não preenche, **não monta meia-posição** (perna solta =
    direcional puro).

- **Edge típico (ordem de grandeza, NÃO promessa):** **WR alto e enganoso ~65–78%** (típico
  de mean-reversion de spread estreito), **R:R ruim ~0,3–0,5** (ganha pouco muitas vezes,
  perde muito poucas vezes). **2–10 sinais/dia por par**, somáveis em 3–5 pares líquidos.
  Skew **fortemente negativo**: dezenas de ganhos de centavos×lote apagados por um
  desmonte forçado em squeeze ou por um evento de governança. **Líquido brutalmente sensível
  ao custo** — com spread médio capturável de poucos centavos e fricção de **4 boletas**,
  o edge bruto positivo pode virar **líquido zero ou negativo**. Esta é a estratégia mais
  "limpa" na tese e a mais traiçoeira na conta.

- **Modos de falha (Nassim) 🦢:**
  1. **Custo come o edge** (modo dominante): spread ON×PN é estreito por construção;
     corretagem + emolumentos + ISS + slippage de 2 pernas + aluguel/short podem exceder o
     ganho médio. **Failure mode #1 não é o mercado — é a planilha.**
  2. **Aluguel / short intradiário indisponível ou caro:** classe ON frequentemente
     ilíquida/difícil de alugar; sem disponibilidade a estratégia simplesmente **não roda**,
     ou roda só na direção "vende PN / compra ON" (metade dos sinais).
  3. **Squeeze intradiário:** ordem de bloco ou ressurgência de liquidez na classe shortada
     dispara o lado contra você no exato minuto em que precisa recomprar para zerar.
  4. **Quebra de relação por governança:** *fato relevante* — alteração de dividendo da PN,
     OPA, conversão de classe, migração para Novo Mercado (unifica ON/PN), perda de *tag
     along* — muda o patamar do spread **permanentemente e de uma vez**. Anos de mean-
     reversion não valem um evento.
  5. **β instável intradiário:** liquidez relativa entre classes varia no dia; β estimado de
     manhã erra à tarde → hedge vira alavancagem direcional.
  6. **Gap de microestrutura no desmonte:** as duas pernas não saem no mesmo instante (uma
     trava em leilão/circuit breaker do papel) → fica com perna solta exatamente no estresse.
  7. **Correlação de P&L ≈ 1 intradiário:** rodar 4 pares do mesmo "tipo de fluxo" não
     diversifica — um dia de fluxo anômalo erra todos juntos (R-08).

- **Custos:** **4 boletas por round-trip** (compra+venda da perna long, venda+recompra da
  perna short) + **emolumentos B3 day trade** + **ISS** + **slippage das 2 pernas** +
  **custo de aluguel/short** (mesmo intradiário, há taxa mínima/disponibilidade) +
  **IR 20% day trade** sobre o líquido + IRRF "dedo-duro" 1%. Com edge bruto de poucos
  centavos×lote e fricção de 2 pernas, **o líquido é o calcanhar de Aquiles** — programa de
  transferência de patrimônio para corretora e B3 se o spread capturável não for largo o
  suficiente. **Premissa de viabilidade:** ganho bruto médio por trade > ~2× fricção total.

- **Dimensionamento:**
  - Trate como **direcional na cauda**, não neutro: risco por trade ≤ **0,25% do capital**
    (igual LS1 — spread estreito + perna short à vista exige folga).
  - **Dimensione pelo squeeze da short**, não pela vol normal do spread — a perda máxima
    plausível é o desmonte forçado da classe shortada, não o desvio típico.
  - **Cap de gross exposure** explícito (dollar-neutral intradiário ≠ baixo gross).
  - Correlação de P&L intradiário entre pares ≈ alta → **calcule exposição agregada** antes
    de rodar N pares simultâneos (R-08); 4 pares ≈ ~1 aposta com 16 boletas.
  - **Kill diário rígido** + circuit breaker se 2 desmontes forçados no mesmo pregão.
  - **Cap de evento:** zero tolerância a carregar posição em emissor com fato relevante
    pendente/agendado (resultados, AGE de reestruturação societária).

- **O que o backtest DEVE provar:**
  1. **Edge sobrevive LÍQUIDO** de 4 boletas + emolumentos + aluguel + IR 20% — simular com
     custo realista de day trade B3, **não** com custo idealizado (este é o teste que mata
     ou aprova a estratégia).
  2. **Disponibilidade e custo de short/aluguel point-in-time** da classe ON — provar que a
     perna short era executável nos dias do sinal, não só em backtest sem fricção de aluguel.
  3. **Modelagem de slippage das 2 pernas** com book real (a classe ilíquida define o
     tamanho máximo); provar que o spread capturável ≠ spread teórico de mid-price.
  4. **Eventos de governança no histórico isolados** (OPAs, conversões, migrações Novo
     Mercado, mudanças de dividendo PN) — quantificar o impacto de cauda desses dias e provar
     que o stop de evento + kill de fechamento truncam a perda.
  5. **β intradiário estável** o suficiente OOS (medir drift dentro do pregão).
  6. **Skew/curtose do P&L** e Monte Carlo da pior sequência intradiária; DSR > 0 com volume
     alto de trades OOS (alta frequência relativa → exige N grande para significância).
  7. **Decomposição de correlação entre pares** — provar que rodar múltiplos pares adiciona
     edge e não só empilha a mesma aposta (R-08).

- **Verdict:** 🟡 **estudável — a mais "limpa" na tese de todas as L&S, e a mais
  refém do custo na prática.** ⭐⭐. Categoria: long & short intraday (à vista), zera no
  fechamento, nunca overnight. Distinta de LS1 (derivativo macro) e de LS2 (par swing por
  cointegração) por construção. A variante **ON×PN do mesmo emissor** é a forma mais
  defensável — *quase-arbitragem*, sem risco fundamental divergindo intradiário. **Mas o
  veredito honesto é frio:** o edge é tão fino que **a viabilidade inteira depende de dois
  testes de fricção** — (a) o ganho bruto capturável excede ~2× a fricção de 4 boletas +
  IR 20%? e (b) a perna short da classe ON é executável e barata o suficiente, todo dia, sem
  squeeze? Se o backtest **não** provar os dois com custo realista, **não opera** — não
  importa quão bonita seja a mean-reversion no gráfico. *"O spread ON×PN é a tese mais
  honesta do catálogo. Também é a que a corretora mais agradece. Prove-me que sobra dinheiro
  depois do custo — com dados, não com a beleza da arbitragem — ou é Jim contra a B3, e a B3
  não perde."*

---

## F — FIIs (Barsi) 🌳

### F1 — FII Core+Yield (renda imobiliária diversificada)
- **Tese:** fluxo de **renda mensal isenta de IR (PF)** via carteira diversificada — **tijolo** (valorização real + proteção inflacionária) + **papel/recebíveis CRI** (yield corrente alto, atrativo com juro/inflação altos). Não acertar topo/fundo — **acumular cotas geradoras de caixa a preço razoável**. Com Selic alta, muito tijolo negocia P/VP < 1 (metro quadrado de qualidade com desconto). *"Quem compra FII na alta de juros está comprando o futuro corte."*
- **Universo (pesos-alvo):** papel/CRI 35–45% (IPCA+ e CDI+) · logística 15–20% · lajes 10–15% (mais cíclico, seletivo) · shoppings 10–15% · híbrido/FoF 5–10%. Nenhum FII > ~8–10%; mínimo 10–15 fundos.
- **Critérios:** P/VP (tijolo ≤ 1,0; papel ~1,0), DY vs CDI líquido (yield muito acima dos pares = **bandeira amarela**), vacância (logística < 5%), qualidade do gestor, mix de indexador dos CRIs, inadimplência baixa/estável, liquidez, diversificação interna.
- **Mecânica:** DCA mensal (aporte ao ativo mais abaixo do peso-alvo); DRIP na acumulação; rebalanceamento anual/semestral **sugestivo**, via aporte novo (evita IR de venda).
- **Retorno esperado:** DY ~8–11% a.a. isento (não linear: tijolo paga menos corrente/mais valorização; papel o inverso); total return ~IPCA + prêmio real. **Honestidade:** com Selic muito alta, o DY isento pode empatar/perder do CDI líquido no curto prazo — vantagem aparece na isenção, proteção do tijolo e na virada do ciclo de juros.
- **Falhas:** queda de NAV (juro alto), vacância (lajes), marcação a mercado de CRI + inadimplência, **yield trap**, risco de gestão, concentração.
- **Tributação:** rendimentos **isentos** (fundo em bolsa, ≥ 50 cotistas, PF < 10% das cotas); ganho de capital na venda **20% sem isenção** (FII não tem o R$ 20k/mês) → estratégia ótima é **buy & hold**. ⚠️ **Reforma tributária 2026** pode tributar rendimentos hoje isentos — risco vivo.
- **Verdict:** **aprovada como espinha de renda da Carteira Hard.** Selic alta é desconforto no curto prazo mas favorável à acumulação. Vigilância: reforma 2026, yield trap, concentração. Horizonte 10+ anos.

---

## H — Holding dividendos (Barsi) 🌳

### H1 — Quality Dividend Hold (7 indicadores / R-20)
- **Tese:** carteira de **empresas perenes, lucrativas e pagadoras consistentes**, selecionadas por fundamento, para **renda passiva crescente vitalícia** ("comprar a vaca pelo leite"). Os 7 indicadores: **DY** (peso forte, consistência > pico), **P/L**, **P/VP**, **ROE** (alto e estável = fosso), **Dívida Líq/EBITDA** (baixa — endividada corta dividendo na 1ª crise), **Payout** (sustentável), **ROIC** (> custo de capital = cria valor). A combinação importa mais que qualquer indicador isolado.
- **Universo (setores perenes):** energia/utilities (coração — demanda inelástica, contratos indexados), bancos (ROE alto, sensível a ciclo/regulação), seguros (float, ROE alto), saneamento (monopólio natural, risco regulatório), telecom (receita recorrente, vigiar dívida). Líderes setoriais com fosso; teto ~10% por ativo.
- **Critérios (score calibrável):** DY consistente 5 anos ~25% · ROE+ROIC ~25% · Dívida/EBITDA ~20% · payout sustentável ~15% · P/L+P/VP ~15%. **Veto eliminatório:** lucro inconsistente, corte recente de dividendo sem causa pontual, dívida explosiva, governança duvidosa.
- **Mecânica:** DCA mensal ao maior desconto relativo ao fundamento; **DRIP** (reinvestir dividendos + JCP — a mágica dos juros compostos sobre renda); rebalanceamento anual sugestivo; vender só por **deterioração de fundamento**, nunca por preço. Horizonte previdenciário 10–30 anos.
- **Retorno esperado:** o número que importa é o **yield-on-cost** daqui a 10–15 anos (empresa que cresce dividendo faz o YoC subir muito acima do yield de entrada); total return ~IPCA + prêmio de RV com menor vol. Não multiplica em 2 anos — vem da consistência do reinvestimento por décadas.
- **Falhas:** corte de dividendo, **value trap** (DY alto porque o negócio deteriora), risco regulatório (setores regulados), concentração setorial (carteira de dividendo incha em utilities+bancos), estagnação do negócio (payout alto sem crescimento = liquidação lenta).
- **Tributação:** ganho de capital **isento até R$ 20k/mês** no à vista (15% acima) — **vantagem fiscal estrutural das ações sobre FIIs**; dividendos **isentos hoje**; JCP tributado 15% na fonte. ⚠️ **Reforma tributária 2026** — proposta concreta de **tributar dividendos** é o **maior risco de cenário vivo** para esta tese; JCP relativamente menos afetado. Vigilância máxima.
- **Verdict:** **aprovada como o destino-fim do Harvest e motor de renda crescente vitalícia.** Mais aderente à filosofia da Carteira Hard. Disciplina inegociável: veto a value trap, fundamento acima de cotação, diversificação setorial.

---

# IV. Lente de Risco Transversal (Nassim) — vale para TODO o catálogo 🦢

> *"Se você ignorar a tese de edge mas respeitar estas quatro, sobrevive. Se dominar a
> tese e ignorar estas, quebra."*

1. **Sizing pela cauda conjunta, não pela perda "esperada".** "Market-neutral" é afirmação sobre o centro da distribuição; a ruína mora na cauda, onde as duas pernas andam juntas e o hedge vira alavancagem 2×. Dimensione spread pelo cenário das duas pernas perdendo juntas. Risco por trade ≤ 0,25–0,5% do capital.

2. **Sequência de perdas mata antes da expectância negativa.** Mean-reversion tem WR alto e R:R baixo — a curva sobe linda e uma sequência de 3–4 perdas (garantida no ano) devolve meses de ganho. Expectância positiva no papel **não impede ruína** se o sizing permite. **Kill diário e kill de drawdown são inegociáveis.**

3. **Correlação oculta entre estratégias = ilusão de diversificação.** WIN×WDO, pairs bancários, pairs de commodities parecem independentes — **não são**: todas dependem de "o spread reverte", que só falha quando a liquidez some, e ela some em todas ao mesmo tempo. Você acha que tem 5 motores de risco; tem **1 motor com 5 carburadores**. Calcule a exposição agregada de fator (R-08) antes de rodar N estratégias simultâneas.

4. **Convergência é frágil por construção — trunque a cauda ou ela te trunca.** Todo o catálogo long/short tem concavidade negativa (ganha pequeno/frequente, perde grande/raro). Você não o torna antifrágil — só **menos suicida**, com stop estatístico (z) + stop fundamental + stop de tempo + reteste de cointegração + caps de exposição. *"A pergunta não é quanto eu ganho quando converge — é o que sobra de mim quando NÃO converge."*

> **Fronteira reafirmada (Barsi):** nenhuma das carteiras de renda (F1, H1) serve de margem,
> cobertura de loss ou combustível de derivativo. São **destino** do Harvest, não fonte.
> Os caixas não se misturam.

---

# V. Recomendação de priorização (Leo, consolidando)

Onde o Time 5 colocaria **capital de research primeiro** (não capital real):

1. **S1 — Momentum cross-sectional** (fundamento científico imbatível, alinha com Harvest Rule)
2. **H1 + F1 — Dividendos + FIIs** (núcleo patrimonial, menos dependente de regime, favorecidos pela acumulação em Selic alta)
3. **D3/LS2 — market-neutral** (melhor Sharpe potencial, **se** a infra existir e os custos couberem)
4. **S2 — Pullback** (melhor R:R, se mecanizado)
5. **D1 — ORB filtrado** (liquidez e simplicidade para um primeiro motor intraday)

Onde o gate seria **mais duro**: **D2, V2 e LS1** — win rate alto é a sereia que afunda conta; só passam se o backtest **provar que o filtro decapita o tail** (Monte Carlo de cauda empírica, não gaussiana). Aqui Jim e Nassim estão do mesmo lado.

Risco transversal de cenário 2026 (Barsi + Ray): **reforma tributária** (atinge a isenção de F1 e H1) e **vol eleitoral no 2º semestre** (atinge todo o direcional).

---

## Próximos passos sugeridos (sob seu gate, Carlos)

- **A.** Escolher 1–2 estratégias para virar **EDGE-THESIS formal** (ex.: S1 já tem fôlego de top pick) e entrar no pipeline de backtest do Quant Lab.
- **B.** Pedir a **Ray** para recalibrar o regime quando houver dados reais (Selic, IPCA 12m, Ibov, vol implícita, fluxo).
- **C.** Pedir a **Barsi** o modelo de **scoring numérico** de F1/H1 para backtest/seleção.
- **D.** Nada disso reativa a trava constitucional automaticamente — operação real no CaM exige voltar aos Arts. 28º–30º e ao Risk Engine.

---

> **Princípio do documento:** Jim prova o *se* (edge líquido out-of-sample). Nassim
> desenha o freio (cauda, ruína, sizing). Barsi constrói o destino (renda, reinvestimento).
> Ray lê o ambiente. Leo consolida. **O Founder decide.** Eleger não é operar.
>
> Research-only · Estudo livre · Trava constitucional desligada por ordem do Founder *apenas para este catálogo* · 2026-06-03

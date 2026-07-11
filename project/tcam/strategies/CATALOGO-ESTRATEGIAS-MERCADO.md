---
template: ESTUDO
phase: N/A
status: Catálogo de referência
version: 1
date: 2026-05-25
escopo: base de análise pessoal — não-vinculante operacionalmente
---

# Catálogo de Estratégias — Mercado Financeiro Brasileiro

> **Documento:** Catálogo de referência para estudo
> **Autor da consulta:** Carlos Rodrigues Ferreira Junior
> **Natureza:** estudo, não operação — operação real do CaM segue Constituição
> **Persona síntese:** Voltaire (consultor experiente + crítico)
> **Status:** vivo, expansível, não substitui a Constituição

---

## Aviso de Abertura (Voltaire)

Este documento foi solicitado como **catálogo de estratégias agressivas para multiplicação de patrimônio**. Antes de qualquer estratégia, três verdades duras precisam ser ditas — sem elas o resto do documento vira pólvora na mão errada.

**Verdade 1.** A B3 publicou estudo em 2019 mostrando que **mais de 97% dos day traders pessoa física perdem dinheiro no acumulado de 12 meses**, e dos que sobrevivem, a maioria ganha menos que o salário mínimo. Isso não é opinião — é estatística pública. Toda estratégia abaixo precisa ser lida sabendo que a média joga contra você.

**Verdade 2.** "Multiplicação agressiva de patrimônio" não existe estatisticamente como categoria sustentável para varejo. O que existe é (a) **sorte com timing**, que não se replica; (b) **edge real raro**, que se acompanha de disciplina obsessiva; ou (c) **alavancagem**, que multiplica para os dois lados — e a estatística mostra que destrói mais do que cria. O caminho real para patrimônio relevante é **edge pequeno × disciplina × tempo × juros compostos**, não tiro certeiro.

**Verdade 3.** Você (Carlos) tem capital declarado de R$ 5.000 no CaM. Em derivativos, com 1 contrato e disciplina, isso pode crescer 30–50% ao ano em cenário **bom**. Não vai virar R$ 500.000 em 2 anos. Quem promete isso ou está mentindo ou está vendendo curso. A Constituição do CaM existe para te proteger de você mesmo desejando o que a matemática não entrega.

Dito isso, o catálogo abaixo é honesto e útil. Estuda. Backtesta. Pratica em paper. E lembra que **o objetivo final do CaM é construir Carteira Hard com dividendo, não ganhar dinheiro de derivativo** — derivativo é motor especulativo controlado que alimenta o patrimônio, não substitui ele.

---

## Como Usar Este Documento

Cada estratégia tem ficha padronizada:

- **Tese:** por que essa estratégia ganha dinheiro, de quem
- **Lógica:** entrada, gestão, saída
- **Edge típico:** win rate, R:R, expectância esperada
- **Capital mínimo recomendado:** realismo, não fantasia
- **Conhecimento exigido:** o que você precisa dominar
- **Modos de falha:** quando e como ela quebra
- **Compatibilidade CaM:** vinculada à Constituição
- **Verdict:** recomendação honesta

**Tags de compatibilidade com a Constituição do CaM:**

- 🟢 **Compatível** — pode ser operada no CaM dentro das regras
- 🟡 **Compatível com ressalvas** — exige fase avançada ou emenda específica
- 🔴 **Incompatível** — fere artigo constitucional, só para estudo fora do CaM
- ⚪ **Fora do escopo CaM** — pertence à Carteira Hard ou patrimônio fora do perímetro

---

## Taxonomia

```
PARTE I — Derivativos (Day Trade)
  1. Opening Range Breakout (ORB) 60min
  2. VWAP Mean Reversion
  3. Volatility Breakout (Larry Williams)
  4. Bollinger Squeeze Breakout
  5. Spread Trading WIN×WDO

PARTE II — Long & Short (Mercado à Vista, Ações)
  6. Long em Rompimento de Resistência Histórica
  7. Short Descoberto em Reversão de Topo
  8. Pair Trading Long/Short Setorial
  9. Long Catalyst-Driven (Pré-Resultado)
  10. Short Squeeze Reverso

PARTE III — Swing Trade
  11. Pullback em Tendência (Buy the Dip)
  12. Box Trading (Darvas Box)
  13. Setup 9.1 (Larry Williams / Stormer)

PARTE IV — Acúmulo para Dividendos
  14. DCA em Dividend Yielders Brasileiros
  15. DRIP Programado (Reinvestimento de Dividendos)
  16. Quality Dividend com Filtro Fundamentalista

PARTE V — Estratégias que você não pediu mas vale conhecer
  17. Covered Call (geração de renda sobre carteira)
  18. Cash Secured Put (compra disfarçada de prêmio)
  19. FIIs de Tijolo + Papel (renda mensal isenta IR)
  20. Long Volatility com Opções OTM (proteção cisne negro)
  21. Carteira Permanente Adaptada (diversificação por classe)
```

---

# PARTE I — DERIVATIVOS (DAY TRADE)

---

## Estratégia 1: Opening Range Breakout (ORB) 60min

**Tese.** O range das primeiras N horas do pregão captura o "consenso" inicial entre compradores e vendedores institucionais. Quando esse range é rompido com volume, indica direção dominante do dia. Você opera com o fluxo institucional, não contra.

**Lógica.**
- **Entrada:** identifica máxima e mínima entre 09h00 e 10h00 (range). Compra a 1 tick acima da máxima se volume confirmar; vende a 1 tick abaixo da mínima se volume confirmar.
- **Gestão:** stop na metade oposta do range (em vez do extremo, pra reduzir slippage).
- **Saída:** alvo de 1.5× a 2× o tamanho do range, OU trailing stop após meio caminho.
- **Filtros essenciais:** ATR do dia anterior acima de X (mínimo de volatilidade), gap de abertura significativo, ausência de eventos macro (Copom, FOMC, Payroll) na janela.

**Edge típico.**
- Win rate: 40–50%
- R:R médio: 1:1.8 a 1:2.2
- Operações por semana: 2–4
- Expectância matemática esperada: positiva pequena, sensível a custos

**Capital mínimo recomendado.** R$ 3.000–5.000 com 1 contrato WIN. Stop típico R$ 40–80.

**Conhecimento exigido.** Leitura de gráfico intradiário, conceito de volume, ATR, filtros de regime de mercado.

**Modos de falha.**
- Mercado lateral o dia inteiro → falso rompimento em ambos os lados
- Dia de notícia macro inesperada → range invalida no primeiro impacto
- Liquidez fraca em horário de transição (12h–14h) → slippage destrói edge
- Overfitting do parâmetro N (60min é convenção; outros valores funcionam em períodos específicos e param de funcionar)

**Compatibilidade CaM.** 🟢 **Compatível.** Encaixa nas janelas vedadas (opera só a partir das 10h, não viola Art. 11º), respeita stops curtos da POV (150–250 pontos WIN), permite 1 contrato.

**Verdict.** **Candidato natural a S1 do CaM.** Documentação farta na literatura, lógica trivial, backtest acessível. Edge erodiu nas últimas 2 décadas — não espera Sharpe 2.0, espera consistência modesta.

---

## Estratégia 2: VWAP Mean Reversion

**Tese.** O VWAP intradiário (Volume Weighted Average Price) é referência de execução institucional. Quando o preço se afasta dele por mais de X desvios padrão sem catalisador claro, há tendência estatística de retorno à média no curtíssimo prazo, porque ordens algorítmicas institucionais comprem/vendem perto do VWAP para minimizar slippage no benchmark.

**Lógica.**
- **Entrada:** preço atinge VWAP + 2 desvios padrão (vende) ou VWAP − 2 desvios padrão (compra), com confirmação de exaustão (rejeição candle, divergência RSI).
- **Gestão:** stop pequeno (1.5 ATR acima/abaixo da entrada). Posição contrária à direção do dia em mercado em range.
- **Saída:** alvo no próprio VWAP.
- **Filtro essencial:** **só opera em dias de range, não de tendência.** Critério objetivo: ADX < 25 OU preço oscilando dentro de canal definido nas últimas 2 horas.

**Edge típico.**
- Win rate: 60–70% (mean reversion tem win rate alto)
- R:R médio: 1:0.8 a 1:1.0 (alvo perto, stop um pouco mais longe)
- Operações por semana: 3–6 em dias de range
- Expectância: positiva em dias certos, devastadora em dias errados (filtro de regime é tudo)

**Capital mínimo recomendado.** R$ 5.000+ com 1 contrato WIN. Esta estratégia tem stops grandes proporcionalmente, então capital pequeno sofre.

**Conhecimento exigido.** VWAP, desvio padrão de preço, ADX, identificação de regime de mercado, leitura de exaustão.

**Modos de falha.**
- **Dia de tendência forte:** preço atravessa VWAP várias vezes na mesma direção, take profit nunca acontece, stops batem em série. Esta é a falha clássica e mortal.
- Notícia inesperada quebra range → stop alargado bate mesmo com filtro.
- Algoritmos institucionais mudaram comportamento desde 2018 — edge erodiu materialmente.

**Compatibilidade CaM.** 🟡 **Compatível com ressalvas.** Em Fase 1 e 2 pode entrar como S2 ou S3 (depois de S1 validada). Stop maior consome margem mais rápida do limite diário — exige posicionamento conservador.

**Verdict.** Boa estratégia complementar para diversificar S1, mas **perigosa como primeira estratégia**. Sequência de loss em dia de tendência pode esgotar limite diário em uma operação. Estuda, backtesta, mas opera só depois de outra com win rate baixo e stops curtos estar consolidada.

---

## Estratégia 3: Volatility Breakout (Larry Williams)

**Tese.** Quando o preço rompe um múltiplo da volatilidade recente (calculado sobre o range do dia anterior), há confirmação estatística de que o consenso de preço quebrou e nova tendência intradiária se inicia.

**Lógica.**
- **Entrada compradora:** quando o preço supera `Open(D) + K × Range(D-1)`, onde K geralmente está entre 0.4 e 0.8.
- **Entrada vendedora:** quando o preço cai abaixo de `Open(D) − K × Range(D-1)`.
- **Gestão:** stop no preço de abertura do dia (ponto neutro).
- **Saída:** fechamento do dia OU trailing stop após 2× o gatilho.
- **Filtros:** dia da semana (segundas e sextas têm comportamento atípico), eventos macro vetam.

**Edge típico.**
- Win rate: 35–45%
- R:R médio: 1:2 a 1:3
- Operações por semana: 1–3
- Expectância: positiva pequena, muito documentada historicamente, edge erodiu

**Capital mínimo recomendado.** R$ 4.000–6.000 com 1 contrato. Stop é referenciado ao Open, pode ser amplo em dia volátil.

**Conhecimento exigido.** Larry Williams, cálculo de range histórico, dependência de calibração de K.

**Modos de falha.**
- K muito pequeno → muitos falsos disparos.
- K muito grande → poucos disparos, mas quando dispara muitas vezes é tarde demais.
- Mercado em consolidação prolongada → estratégia fica anos sem dar sinal lucrativo.
- Range(D-1) anômalo (dia anterior com volatilidade extrema) → gatilho deslocado.

**Compatibilidade CaM.** 🟢 **Compatível.** Limites de stop e contratos respeitados.

**Verdict.** Estratégia clássica, **uma das primeiras algorítmicas documentadas no varejo**. Vale estudar como referência histórica. Como S1 do CaM, fica atrás do ORB porque a calibração de K é mais sensível e o edge é menor hoje.

---

## Estratégia 4: Bollinger Squeeze Breakout

**Tese.** Quando as Bandas de Bollinger comprimem (squeeze) abaixo de um threshold de largura, indica baixa volatilidade — frequentemente um precursor estatístico de expansão violenta. Você posiciona após a compressão e captura a expansão.

**Lógica.**
- **Detecção do squeeze:** BB width (largura entre banda superior e inferior) atinge mínimo dos últimos N períodos (40 candles, por exemplo).
- **Entrada:** rompimento da banda superior (compra) ou inferior (venda) **após confirmação de aumento de volume**.
- **Gestão:** stop na linha central da BB (média móvel) ou ATR-based.
- **Saída:** alvo no extremo oposto da banda OU trailing stop após meio caminho.
- **Filtro essencial:** confirmar que o squeeze ocorreu em janela coerente (não em meio de tendência forte).

**Edge típico.**
- Win rate: 50–60%
- R:R médio: 1:1.5 a 1:2.5
- Operações por semana: 2–5 (mais frequente em mercado lateral prolongado)
- Expectância: positiva moderada

**Capital mínimo recomendado.** R$ 3.000–5.000 com 1 contrato.

**Conhecimento exigido.** Bandas de Bollinger, conceito de volatility cycle, detecção de squeeze, confirmação de breakout.

**Modos de falha.**
- Squeeze que dura mais que o esperado → você entra em vários falsos rompimentos antes do real.
- Breakout sem volume → reversão imediata.
- Notícia macro durante squeeze → expansão fora de qualquer parâmetro técnico.

**Compatibilidade CaM.** 🟢 **Compatível.** Funciona bem com 1 contrato, respeita janelas vedadas se você restringir detecção ao período válido.

**Verdict.** **Boa segunda estratégia depois do ORB.** Complementa porque opera em mercado lateral (onde ORB sofre). Diversificação real entre regimes.

---

## Estratégia 5: Spread Trading WIN×WDO (Pair Macro)

**Tese.** Bovespa (WIN) e Dólar (WDO) têm correlação macroeconômica historicamente inversa — risco-on/risco-off. Quando essa correlação se distorce além de N desvios padrão da média rolling, há tendência estatística de convergência. Você opera comprado no que ficou barato e vendido no que ficou caro, ganhando independente da direção do mercado.

**Lógica.**
- **Cálculo:** spread = (WIN normalizado) − (WDO normalizado), ambos em escala comparável (z-score rolling 30 dias).
- **Entrada:** spread > +2 desvios → vende WIN, compra WDO. Spread < −2 desvios → compra WIN, vende WDO.
- **Gestão:** stop em +3 ou −3 desvios.
- **Saída:** spread retorna à média (z-score próximo de zero).
- **Filtro essencial:** **não operar em dia de evento macro** (Copom, FOMC, dado de inflação) — esses eventos quebram correlação por design.

**Edge típico.**
- Win rate: 65–75% (alto, característico de mean reversion)
- R:R médio: 1:0.7 a 1:1
- Operações por mês: 2–5 (oportunidades raras)
- Expectância: positiva, mas drawdown pode ser brutal em quebra de correlação

**Capital mínimo recomendado.** R$ 10.000+ — porque você tem 2 contratos abertos simultaneamente (cada um exige margem) e a operação pode levar dias.

**Conhecimento exigido.** Estatística (z-score, desvio padrão rolling), correlação dinâmica, conceito de cointegração, mean reversion em pares.

**Modos de falha.**
- **Quebra estrutural de correlação:** WIN e WDO podem subir ou cair juntos por meses (cenários de saída de capital estrangeiro, por exemplo). Estratégia sangra continuamente.
- Margem dobrada — em dias de stress, ambas as posições podem ir contra ao mesmo tempo.
- Carrego: posição mantida overnight em derivativo tem custo de margem e gap risk.

**Compatibilidade CaM.** 🔴 **Incompatível em Fase 1, 2 e 3.** O Art. 12º veta operação simultânea WIN+WDO até Fase 3, e mesmo Fase 3 exige aderência rigorosa e risco somado dentro do limite. Esta estratégia **exige operação simultânea por construção** e é classificada como estratégia avançada para Fase 4+.

**Verdict.** **Estratégia sofisticada, intelectualmente bonita, perigosa em capital pequeno.** Vale estudar como cultura quantitativa, mas o CaM com R$ 5.000 não opera isso até a Fase 4 com bucket de R$ 3.000 pleno + histórico de meses.

---

# PARTE II — LONG & SHORT (MERCADO À VISTA, AÇÕES)

> Sugestão de quantidade: **5 estratégias.** Cobertura: 2 long puros, 1 short puro, 1 pair (long+short combinado), 1 catalyst-driven.

---

## Estratégia 6: Long em Rompimento de Resistência Histórica

**Tese.** Resistência técnica acumulada por meses representa zona onde vendedores conseguiram conter compradores. Quando essa resistência cai com volume, indica esgotamento da oferta e nova fase de descoberta de preço — frequentemente com movimento expressivo subsequente.

**Lógica.**
- **Identificação:** ação que tocou resistência ≥ 3 vezes nos últimos 6–12 meses sem romper.
- **Entrada:** rompimento de 1–2% acima da resistência com volume ≥ 1.5× a média de 20 dias.
- **Gestão:** stop 5–8% abaixo da entrada, OU no nível antigo de resistência (agora suporte).
- **Saída:** alvo projetado pela altura do range anterior. Trailing stop em alta de 15%+.
- **Filtros:** mercado em uptrend (IBOV acima da MM200), setor em rotação positiva, ausência de eventos negativos no nome.

**Edge típico.**
- Win rate: 40–50% (rompimentos falham com frequência)
- R:R médio: 1:3 a 1:5 (quando funciona, funciona bem)
- Operações por mês: 1–3 (depende do mercado)
- Expectância: positiva quando filtro de regime é respeitado

**Capital mínimo recomendado.** R$ 10.000+ — para diversificar entre 3–5 posições e absorver stops individuais.

**Conhecimento exigido.** Análise técnica clássica, suportes e resistências, volume confirmation, análise setorial, identificação de regime do índice.

**Modos de falha.**
- Falso rompimento (estatisticamente comum) — daí stop curto.
- Catalisador negativo após entrada (resultado ruim, downgrade) — risco não-técnico.
- Mercado vira de regime → uptrend setorial morre, ação cai com o setor.

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM.** Pertence à Carteira Hard se utilizada (aquisição com viés técnico em vez de DCA cego). Ou pertence a patrimônio fora do perímetro CaM (Art. 8º).

**Verdict.** Estratégia clássica, validada por décadas, exige paciência. Boa para construção de Carteira Hard com **timing técnico**, mas demanda mais trabalho que DCA simples. Custo-benefício depende de sua disponibilidade.

---

## Estratégia 7: Short Descoberto em Reversão de Topo Confirmada

**Tese.** Quando uma ação em tendência de alta forma topo duplo, divergência baixista de momentum (RSI/MACD), e quebra suporte de curto prazo com volume, há confirmação estatística de mudança de regime. Você vende descoberto (alugando a ação via BTC).

**Lógica.**
- **Identificação:** ação em uptrend que forma topo duplo OU triplo, com divergência baixista clara em RSI 14.
- **Entrada:** rompimento de suporte da formação (linha do "pescoço") com volume.
- **Gestão:** stop acima do topo mais recente.
- **Saída:** alvo pela altura da formação. Cobertura em sinal de exaustão da queda (capitulação).
- **Custos extras:** taxa de aluguel BTC (anualizada — varia de 0.3% a 5% ao ano por papel, paga pro rata pelo tempo de aluguel).

**Edge típico.**
- Win rate: 35–45%
- R:R médio: 1:2 a 1:3
- Operações por mês: 1–2
- Expectância: positiva em mercados de baixa/lateral, negativa em bull market

**Capital mínimo recomendado.** R$ 20.000+ — porque margem de short descoberto é mais alta (regulação CVM exige garantia substancial).

**Conhecimento exigido.** Mecânica de aluguel BTC, custos de carregamento, mecanismo de recall (locador pode pedir ação de volta a qualquer momento), análise técnica de topos, divergências.

**Modos de falha.**
- **Short squeeze:** se a ação subir contra você com força e o locador exigir recall, você é forçado a recomprar no pior momento.
- Bull market sustentado → shorts perdem dinheiro mesmo com tese correta.
- Catalisador positivo imprevisto (M&A, resultado excepcional).
- Custo de aluguel altíssimo em papéis "quentes" (ex: small caps em squeeze) corrói edge.

**Compatibilidade CaM.** 🔴 **Incompatível.** Operação em ações no à vista está fora do escopo do CaM (que é WIN/WDO + Carteira Hard). Short descoberto é estratégia agressiva com risco assimétrico — incompatível com espírito Art. 4º (CaM impede que operador quebre quando convicto demais).

**Verdict.** **Cautela máxima.** Short é a operação onde perda teórica é ilimitada (a ação pode subir indefinidamente, mas só pode cair a zero — a aritmética favorece o long). Mesmo profissionais sofrem em short. Para estudo é válido entender a mecânica; para operação pessoal, raramente compensa o risco.

---

## Estratégia 8: Pair Trading Long/Short Setorial

**Tese.** Ações do mesmo setor têm correlação alta entre si (compartilham risco macro setorial). Quando uma diverge da outra além do espread histórico — geralmente por movimento específico de um nome — há tendência estatística de convergência. Você compra a fraca e vende a forte, ficando **beta-neutro** ao mercado.

**Lógica.**
- **Identificação:** par de ações no mesmo setor com cointegração estatística histórica (ex: ITUB4 × BBDC4; PETR4 × PETR3; VALE3 × CSNA3).
- **Cálculo do spread:** ratio = ação A / ação B, com z-score rolling.
- **Entrada:** z-score > +2 → vende A, compra B. z-score < −2 → compra A, vende B.
- **Gestão:** stop em z-score > +3 ou < −3.
- **Saída:** z-score volta a zero (convergência).

**Edge típico.**
- Win rate: 65–75%
- R:R médio: 1:0.8 a 1:1.2
- Operações por mês: 2–4
- Expectância: positiva consistente, drawdown limitado se cointegração se mantiver

**Capital mínimo recomendado.** R$ 30.000+ — para construir as duas pernas com tamanho que faça sentido após custos.

**Conhecimento exigido.** Cointegração de Engle-Granger, análise setorial profunda, mecânica BTC, gestão de duas posições.

**Modos de falha.**
- **Quebra de cointegração:** par historicamente correlato pode desacoplar permanentemente (ex: empresa de um lado vira target de M&A, outro afunda em escândalo).
- Custos somados (BTC + corretagem 2x) corroem edge se par é muito ativo.
- Stop em divergência crescente é cruel — você sangra esperando convergência que pode nunca vir.

**Compatibilidade CaM.** 🔴 **Incompatível.** Mesma razão da Estratégia 7 — fora do escopo CaM.

**Verdict.** Estratégia **intelectualmente elegante** e usada por hedge funds quantitativos. Para PF, exige capital alto, infraestrutura analítica robusta (z-score em tempo real), conhecimento estatístico. Vale conhecer; raramente vale operar em escala pequena.

---

## Estratégia 9: Long Catalyst-Driven (Pré-Resultado)

**Tese.** Empresas com histórico de surpresa positiva em resultados trimestrais (beat consistente de consensus) tendem a repetir o padrão. Você posiciona antes do resultado, capturando o "earnings drift" pós-anúncio.

**Lógica.**
- **Identificação:** empresa com 4–6 trimestres consecutivos de beat (resultado acima do consenso de analistas).
- **Entrada:** 5–10 dias antes do resultado, posição comprada.
- **Gestão:** stop pré-definido (5–8% abaixo da entrada).
- **Saída:** próximo dia útil após o anúncio do resultado. Sai no abrir, não aguenta o "drift" estatístico de dias subsequentes.
- **Filtros:** evitar empresas com guidance ambíguo ou cobertura analítica fraca.

**Edge típico.**
- Win rate: 55–65%
- R:R médio: 1:1.2 a 1:1.8
- Operações por temporada: 4–8 (4 temporadas por ano)
- Expectância: positiva, mas concentrada em 4 períodos curtos do ano

**Capital mínimo recomendado.** R$ 10.000+ para diversificar entre 3–5 nomes na mesma temporada.

**Conhecimento exigido.** Calendário corporativo, leitura de release de resultado, conceito de consenso de analistas (Bloomberg, Refinitiv), histórico de surpresas.

**Modos de falha.**
- **Beat com guidance fraco** → ação cai mesmo com resultado bom.
- Mudança de ciclo econômico → empresa que batia consenso passa a errar.
- Catalisador negativo macro durante o período de posicionamento.
- Pricing já incorporou expectativa positiva → "beat" é precificado, surpresa real seria "no surprise".

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM** (não é WIN/WDO). Pode ser usada como tática para timing de aquisição de ações para Carteira Hard, mas não para day trade.

**Verdict.** Estratégia legítima, usada por fundos. Requer disciplina de calendário e análise. **Não confunda com "comprar tip" — exige rigor de seleção.**

---

## Estratégia 10: Short Squeeze Reverso

**Tese.** Ações com alto short interest (muita gente vendida) e catalisador positivo iminente podem disparar violentamente para cima, porque os vendidos são forçados a recomprar (squeeze). Você se antecipa ao squeeze.

**Lógica.**
- **Identificação:** ação com short interest > 5% do free float (no Brasil, dados de BTC publicados pela B3) E catalisador identificável (resultado, anúncio, fim de evento negativo).
- **Entrada:** posição comprada antes do catalisador.
- **Gestão:** stop abaixo do suporte mais próximo.
- **Saída:** alvo no movimento explosivo, com trailing stop apertado pós-catalisador.

**Edge típico.**
- Win rate: 30–40% (estratégia de cauda — perde muitas vezes pequenas, ganha poucas vezes muito)
- R:R médio: 1:4 a 1:8 (quando o squeeze acontece)
- Operações por mês: 0–2 (oportunidades raras)
- Expectância: positiva em "fat tail" — sensível a critério de seleção

**Capital mínimo recomendado.** R$ 10.000+ — pela natureza de cauda, precisa de várias tentativas para capturar a vitoriosa.

**Conhecimento exigido.** Leitura de dados de BTC pela B3, análise de catalisador, gestão emocional para suportar perdas pequenas em sequência.

**Modos de falha.**
- Catalisador esperado não materializa (resultado vem em linha, evento atrasa).
- Squeeze não acontece (vendidos seguram posição).
- Catalisador é negativo, ação afunda ainda mais.
- **Mortal:** entrar em squeeze que já aconteceu (FOMO) — você compra no topo.

**Compatibilidade CaM.** 🔴 **Incompatível.** Estratégia de cauda em ações está fora do escopo. Padrão emocional (loss em sequência esperando o tiro vencedor) viola espírito Art. 4º.

**Verdict.** **Sirena de alerta.** Esta é estratégia que parece atraente porque o R:R é fenomenal nas operações vencedoras, mas a frequência baixa de acertos e a necessidade de gestão emocional rigorosa tornam ela armadilha para amador. Estuda como conceito; opera só com edge real e capital sobressalente.

---

# PARTE III — SWING TRADE

> Sugestão de quantidade: **3 estratégias.** Cobertura: 1 trend, 1 box, 1 reversal clássico brasileiro.

---

## Estratégia 11: Pullback em Tendência (Buy the Dip)

**Tese.** Ações em tendência de alta forte sofrem correções técnicas naturais (3–8% de retração). Quando essa retração toca um nível técnico relevante (MM21, MM50, fibo 38.2% ou 50%, banda inferior de Bollinger), há tendência estatística de retomada do uptrend.

**Lógica.**
- **Identificação:** ação em uptrend definido (MM50 ascendente, fechamentos acima da MM200, sequência de máximas e mínimas ascendentes).
- **Entrada:** preço toca nível técnico (MM21 ou MM50, geralmente) com candle de rejeição (martelo, hammer, engolfo de alta).
- **Gestão:** stop abaixo do nível técnico tocado.
- **Saída:** alvo no topo recente OU trailing stop após meio caminho.
- **Filtro:** mercado IBOV em uptrend (correlação setorial), sem catalisador negativo no nome.

**Edge típico.**
- Win rate: 55–65%
- R:R médio: 1:1.5 a 1:2.5
- Operações por mês: 2–5 (mais frequente em bull market)
- Duração média: 5–15 dias

**Capital mínimo recomendado.** R$ 10.000+ para diversificar entre nomes.

**Conhecimento exigido.** Análise técnica de tendência, médias móveis, fibonacci, candles de reversão.

**Modos de falha.**
- Pullback vira reversão de tendência → stop bate, e ação continua caindo.
- Mercado vira de regime no meio do swing.
- Tese técnica correta, catalisador negativo posterior anula.

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM.** Estratégia para Carteira Hard (timing de aquisição) ou patrimônio fora do perímetro.

**Verdict.** **Uma das estratégias de swing mais robustas e replicáveis.** Boa para construção tática de carteira. Funciona em ciclos. Sofre em mercado lateral prolongado.

---

## Estratégia 12: Box Trading (Darvas Box)

**Tese.** Nicholas Darvas (anos 50) observou que ações em forte alta consolidam em "caixas" (faixas horizontais) antes de novas pernas de alta. Quando o preço rompe uma caixa, frequentemente forma a próxima caixa acima, em movimento de "escada".

**Lógica.**
- **Identificação:** ação faz nova máxima histórica, recua e consolida 5–15 dias entre uma máxima local (topo da caixa) e uma mínima local (fundo da caixa). Caixa formada.
- **Entrada:** rompimento do topo da caixa com volume acima da média.
- **Gestão:** stop no fundo da caixa.
- **Saída:** trailing stop conforme nova caixa se forma acima. Vende quando o preço cai dentro da caixa anterior.

**Edge típico.**
- Win rate: 45–55%
- R:R médio: 1:2 a 1:4
- Operações por mês: 1–3 (ações certas)
- Duração média: 10–30 dias

**Capital mínimo recomendado.** R$ 10.000+ para diversificar.

**Conhecimento exigido.** Identificação visual de consolidações, paciência (caixas demoram para se formar), gestão de trailing stop.

**Modos de falha.**
- Falso rompimento (entrada acima do topo, preço volta para dentro da caixa).
- Mercado vira no meio da formação.
- Caixas grandes demais → stop largo destrói R:R.

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM.**

**Verdict.** **Estratégia clássica e estudada.** Combina bem com análise fundamentalista — Darvas só operava ações com fundamentos sólidos em caixa. Vale como complemento técnico para construção de Carteira Hard.

---

## Estratégia 13: Setup 9.1 (Larry Williams / Stormer)

**Tese.** Adaptação brasileira (Alexandre "Stormer" Wolwacz) de setup do Larry Williams. Após 9 candles diários em queda (movimento exagerado para baixo), há tendência estatística de reversão de curto prazo.

**Lógica.**
- **Identificação:** ação com 9 fechamentos diários consecutivos abaixo da MM21 (estendido para baixo). Padrão indica exaustão de venda.
- **Entrada:** primeiro candle que fecha acima da máxima do candle anterior (reversão técnica).
- **Gestão:** stop abaixo da mínima do candle de entrada.
- **Saída:** alvo na MM21 OU primeira resistência relevante.

**Edge típico.**
- Win rate: 55–65%
- R:R médio: 1:1 a 1:2
- Operações por mês: 2–6
- Duração média: 3–10 dias

**Capital mínimo recomendado.** R$ 5.000+ para diversificar entre 2–3 nomes.

**Conhecimento exigido.** Contagem de candles, MM21, candle de reversão, gestão de swing curto.

**Modos de falha.**
- Falha clássica: 9 candles para baixo viram 15 candles para baixo (exaustão demora a vir).
- Mercado bearish estrutural → setup aciona em ações que continuam caindo.
- Falso candle de reversão → bate stop rápido.

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM.**

**Verdict.** **Setup mais conhecido do swing trade brasileiro.** Stormer popularizou. Funciona ciclicamente. Vale conhecer, vale testar, **não vale tratar como religião** (muitos amadores adotam como única estratégia).

---

# PARTE IV — ACÚMULO PARA DIVIDENDOS

> Sugestão de quantidade: **3 estratégias.** Cobertura: 1 sistemática (DCA), 1 composta (DRIP), 1 com filtro (Quality).

---

## Estratégia 14: DCA em Dividend Yielders Brasileiros

**Tese.** Comprar quantidade fixa em valor (não em ações) em datas pré-definidas (mensal/quinzenal) de empresas com histórico longo de pagamento de dividendos resulta em preço médio menor que market timing tentado, e remove decisão emocional de "esperar a queda".

**Lógica.**
- **Universo:** ações brasileiras com pagamento ininterrupto de dividendos há ≥ 10 anos e dividend yield histórico médio ≥ 6% (ex: TAEE11, BBSE3, ITSA4, KLBN11, ABEV3, BBDC4, ITUB4).
- **Mecânica:** aporte fixo (ex: R$ 500/mês) dividido entre 4–6 nomes, no mesmo dia de cada mês.
- **Filtro mínimo:** rebalanceamento anual (manter pesos definidos).
- **Sem timing:** compra independente de preço, IBOV ou cenário macro.

**Edge típico.**
- Retorno esperado: 8–14% ao ano em CDI+ (dividendos + valorização modesta)
- Comparação: bate poupança e Tesouro Selic na média de longo prazo
- Volatilidade: moderada
- Horizonte: 10+ anos

**Capital mínimo recomendado.** Aporte mensal de R$ 200–500. Patrimônio mínimo para diversificar: R$ 10.000.

**Conhecimento exigido.** Mínimo. Disciplina é o ativo principal, não conhecimento.

**Modos de falha.**
- **Maior risco psicológico: parar nos crashes.** A estratégia depende de aportar exatamente quando dói (mercados em queda). 70% dos investidores PF param de aportar em bear market — é a falha que mata o retorno.
- Seleção ruim de papéis (escolher empresas que cortam dividendos).
- Aporte irregular destrói a matemática.

**Compatibilidade CaM.** 🟢 **Compatível.** Esta é exatamente a filosofia da Carteira Hard do CaM (Art. 23º) — núcleo patrimonial alimentado por Harvest Rule mensal.

**Verdict.** **Estratégia mais robusta deste catálogo inteiro.** Não impressiona ninguém em mesa de bar, mas multiplica patrimônio de forma comprovada estatisticamente em janelas de 10+ anos. **Esta é a verdadeira "multiplicação de patrimônio agressiva" — agressiva no compromisso de tempo, não no risco de capital.**

---

## Estratégia 15: DRIP Programado (Dividend Reinvestment Plan)

**Tese.** Reinvestir 100% dos dividendos recebidos em compra de mais cotas/ações dos mesmos papéis cria efeito de juros compostos sobre dividendos. Em janela de 20+ anos, o reinvestimento triplica o retorno comparado a sacar os dividendos.

**Lógica.**
- **Mecânica:** todo dividendo recebido (em conta da corretora) é automaticamente comprado em papéis selecionados.
- **Pode ser combinado com DCA:** aporte mensal externo + reinvestimento de dividendos.
- **Frequência:** o reinvestimento acompanha o calendário de pagamento de cada papel (mensal para FIIs, trimestral/semestral para ações).

**Edge típico.**
- Retorno esperado: 12–18% ao ano em janela longa (combinando dividend yield + reinvestimento + valorização)
- Diferença vs DCA puro: 2–4 pontos percentuais ao ano em janela de 20 anos = mais que dobra patrimônio final
- Horizonte mínimo: 15+ anos para efeito composto se materializar

**Capital mínimo recomendado.** Mesmo do DCA. A diferença é disciplinar — não sacar dividendos.

**Conhecimento exigido.** Mínimo. Disciplina extrema de não usar dividendos para consumo.

**Modos de falha.**
- Sacar dividendos para "usufruir" do retorno (transforma DRIP em DCA simples).
- Reinvestimento em papéis ruins (deteriora a qualidade da carteira ao longo do tempo).
- Tributação sobre alguns proventos pode reduzir reinvestimento se não considerada.

**Compatibilidade CaM.** 🟢 **Compatível.** Combina com Harvest Rule (Art. 21º) — lucro do CaM derivativo + dividendos recebidos da Carteira Hard, ambos compõem a Carteira Hard.

**Verdict.** **A combinação DCA + DRIP é o que efetivamente cria patrimônio relevante em horizonte de 20+ anos.** É enfadonho, é lento, e é matematicamente comprovado. O contrário do que vende curso de day trade.

---

## Estratégia 16: Quality Dividend com Filtro Fundamentalista

**Tese.** Não basta comprar alto dividend yield — yields muito altos frequentemente são armadilhas (a ação caiu porque os fundamentos pioraram, mas o dividendo ainda não foi cortado). Filtros fundamentalistas selecionam empresas que sustentam o dividendo no longo prazo.

**Lógica.**
- **Universo inicial:** ações com dividend yield > 5%.
- **Filtros sequenciais (todas as condições):**
  - Pay-out ratio < 80% (sobra lucro para reinvestimento)
  - Dívida líquida / EBITDA < 2.5 (saúde financeira)
  - ROE > 12% nos últimos 5 anos (rentabilidade)
  - Crescimento de lucro líquido > 0% nos últimos 5 anos (não está minguando)
  - Setor não-cíclico ou com fluxo estável (utilities, financeiro, consumo básico)
- **Construção:** carteira de 8–15 nomes, pesos definidos pela conveniência de diversificação setorial.

**Edge típico.**
- Retorno esperado: 10–15% ao ano em janela longa
- Vantagem vs DCA simples: menor drawdown em crises, menor probabilidade de carregar empresa que corta dividendo
- Custo: análise trimestral (≥ 8 horas por trimestre)

**Capital mínimo recomendado.** R$ 30.000+ para diversificar adequadamente em 8–15 nomes com posições mínimas relevantes.

**Conhecimento exigido.** Análise fundamentalista básica, leitura de demonstrações financeiras, indicadores de qualidade.

**Modos de falha.**
- Critérios rígidos demais → universo de seleção fica vazio em mercados específicos.
- Não revisar filtros periodicamente → carteira envelhece.
- Análise excessiva → paralisia de decisão.

**Compatibilidade CaM.** 🟢 **Compatível.** Refinamento da Estratégia 14 — pode ser usada para selecionar a Carteira Hard do CaM com mais rigor do que "comprar dividend yielders famosos".

**Verdict.** **Para o investidor que quer ir além do feijão-com-arroz do DCA puro.** Exige trabalho contínuo. Recompensa em janela longa é incremental sobre DCA simples, não revolucionária. Faz sentido conforme patrimônio cresce.

---

# PARTE V — ESTRATÉGIAS QUE VOCÊ NÃO PEDIU MAS VALE CONHECER

> Sugestão Voltaire: 5 estratégias adicionais que cobrem dimensões fora do que você listou — opções, FIIs, ETFs, hedge, diversificação real.

---

## Estratégia 17: Covered Call (Geração de Renda sobre Carteira)

**Tese.** Você possui ação X. Vende opção de compra (call) de strike fora do dinheiro (acima do preço atual) com vencimento em 30–45 dias. Recebe prêmio. Se a ação subir acima do strike, vende automaticamente (você abre mão de upside maior em troca do prêmio). Se a ação cair ou ficar lateral, fica com a ação e com o prêmio.

**Lógica.**
- **Pré-requisito:** ter pelo menos 100 ações (lote padrão de opção).
- **Mecânica:** vende call OTM (5–10% acima do preço atual) com 30–45 dias para vencimento.
- **Cenários:**
  - Ação sobe pouco/fica lateral: prêmio é lucro líquido.
  - Ação sobe muito: vende no strike + prêmio (não captura todo o upside).
  - Ação cai: prêmio amortiza parte da perda em ação.

**Edge típico.**
- Renda extra anual sobre carteira: 5–12%
- Combinada com Carteira Hard: aumenta yield total
- Win rate: 70–85% (a maioria das opções OTM expira sem valor)

**Capital mínimo recomendado.** Equivalente a 100 ações de pelo menos 3–5 nomes (R$ 30.000+).

**Conhecimento exigido.** Mecânica de opções, Black-Scholes intuitivo, gestão de rolagem, calendário de vencimento (3a sexta-feira de cada mês na B3).

**Modos de falha.**
- Ação sobe explosivamente → você abre mão de gain grande pelo prêmio pequeno (custo de oportunidade).
- Mercado bear forte → prêmio não compensa a queda.
- Volatilidade implícita baixa → prêmios pequenos demais.

**Compatibilidade CaM.** 🟡 **Compatível com ressalvas.** Pode ser usada sobre a Carteira Hard quando ela tiver lotes mínimos. Não opera dentro do bucket derivativo. Exige Constituição emenda para incluir opções no perímetro operacional.

**Verdict.** **Estratégia que profissionais consideram "free lunch" — gera renda sobre patrimônio existente.** Limitação: precisa de capital razoável e conhecimento de opções. Vale estudar para Fase 4+ do CaM.

---

## Estratégia 18: Cash Secured Put

**Tese.** Você quer comprar a ação X, mas a R$ 25 (preço alvo), não no preço atual de R$ 30. Em vez de colocar ordem limitada, vende opção de venda (put) com strike R$ 25 e recebe prêmio. Se a ação cair abaixo de R$ 25, você é "obrigado" a comprá-la a R$ 25 (mas com o prêmio amortizando). Se ela não cair, você fica com o prêmio.

**Lógica.**
- **Pré-requisito:** ter o caixa equivalente reservado (cash-secured) para honrar a compra se exercido.
- **Mecânica:** vende put OTM no strike alvo de compra, com 30–45 dias.
- **Cenários:**
  - Ação fica acima do strike: prêmio é lucro líquido, você não compra.
  - Ação cai abaixo do strike: você compra no strike (preço alvo) com prêmio amortizando.

**Edge típico.**
- Vantagem comparada a ordem limitada simples: ganho do prêmio mesmo que a ordem não seja executada
- Win rate: 70–85% (mesma lógica do covered call)

**Capital mínimo recomendado.** Caixa para honrar a compra de 100 ações (R$ 2.500–10.000 por put).

**Conhecimento exigido.** Mesmo da Covered Call.

**Modos de falha.**
- Ação despenca muito abaixo do strike → você compra a R$ 25 com ação valendo R$ 18 (poderia ter comprado mais barato).
- Não ter o caixa disponível e ter que liquidar a posição com prejuízo.

**Compatibilidade CaM.** 🟡 **Compatível com ressalvas.** Mesmo do Covered Call.

**Verdict.** **Excelente para construção tática da Carteira Hard.** Em vez de "esperar a queda" passivamente, você é pago para esperar.

---

## Estratégia 19: FIIs de Tijolo + Papel (Renda Mensal Isenta IR)

**Tese.** Fundos Imobiliários distribuem rendimentos mensais isentos de Imposto de Renda para pessoa física (regra atual da legislação tributária brasileira). Diversificar entre FIIs de tijolo (imóveis físicos: lajes, shoppings, galpões) e papel (CRIs, LCIs, ativos imobiliários financeiros) cria fluxo mensal estável.

**Lógica.**
- **Universo:** FIIs com mais de 5 anos de histórico, patrimônio líquido > R$ 500 milhões, dividend yield 6–10% ao ano (acima disso, suspeita).
- **Composição típica:**
  - 30% FIIs de lajes corporativas (HGRE11, KNRI11, BRCR11)
  - 30% FIIs de shoppings (XPML11, VISC11, HSML11)
  - 20% FIIs de logística (HGLG11, BTLG11)
  - 20% FIIs de papel/recebíveis (KNCR11, MXRF11, HFOF11)
- **Mecânica:** DCA mensal, reinvestimento dos rendimentos.

**Edge típico.**
- Rendimento mensal: 0.5–1.0% líquido (isento IR)
- Yield anual: 7–11% (líquido)
- Volatilidade: menor que ações, maior que renda fixa
- Liquidez: variável por FII

**Capital mínimo recomendado.** R$ 5.000+ para diversificar entre 6–8 FIIs.

**Conhecimento exigido.** Análise de FIIs (P/VP, vacância, taxa de administração, gestão), diferença entre tijolo e papel.

**Modos de falha.**
- Concentração em um único FII → risco de vacância ou gestão ruim.
- FIIs com yield muito alto → frequentemente são armadilha (problema oculto).
- Mudança regulatória (isenção de IR pode ser revista — risco político).

**Compatibilidade CaM.** 🟢 **Compatível.** Excelente componente da Carteira Hard. Isenção de IR otimiza retorno líquido.

**Verdict.** **Praticamente obrigatório em qualquer Carteira Hard brasileira pela isenção tributária.** Combina renda mensal com diversificação. Componente natural da estratégia 14/15/16.

---

## Estratégia 20: Long Volatility com Opções OTM (Proteção Cisne Negro)

**Tese.** Em momentos de mercado calmo, opções de venda (puts) muito fora do dinheiro (15–20% abaixo do índice) custam muito barato. Comprar essas puts regularmente como "seguro" do patrimônio gera proteção contra crashes — quando o IBOV cai 30% em uma semana, essas puts disparam de valor.

**Lógica.**
- **Mecânica:** alocar 0.5–2% do patrimônio total por trimestre na compra de puts OTM do mini-índice (WIN) ou índice cheio (IND).
- **Strike:** 15–20% abaixo do preço atual.
- **Vencimento:** 60–90 dias.
- **Custo:** trimestral — seguro tem prêmio.
- **Retorno:** alto e assimétrico em crash.

**Edge típico.**
- 95% das compras viram zero (puts expiram sem valor)
- 5% dos casos: retorno de 5x a 50x o investido
- Função: proteção, não geração de renda

**Capital mínimo recomendado.** Patrimônio total > R$ 50.000 para que o custo da proteção (0.5–2% trimestral) faça sentido.

**Conhecimento exigido.** Opções avançado, conceito de gregas (delta, gamma, theta), gestão de vencimentos.

**Modos de falha.**
- Crash não vem por anos → custo acumulado parece desperdiçado (mas é seguro).
- Compra em momento de volatilidade alta → preço da put já reflete medo, perde-se mais.
- Strike muito longe → opção custa quase nada mas dificilmente dispara.

**Compatibilidade CaM.** 🟡 **Compatível com ressalvas.** Não é estratégia de geração de retorno — é hedge. Pode ser incorporada à governança patrimonial geral fora do bucket derivativo do CaM.

**Verdict.** **Conceito tail hedging do Universa Investments (Mark Spitznagel).** Funciona em janela longa. Conta enfadonho durante anos, salva patrimônio em uma crise. Considerar quando patrimônio total justificar custo.

---

## Estratégia 21: Carteira Permanente Adaptada (Browne Brasileira)

**Tese.** Harry Browne (anos 80) propôs alocação fixa em 4 classes de ativo descorrelacionadas: 25% ações, 25% renda fixa longa, 25% ouro, 25% caixa. Em qualquer cenário macroeconômico (boom, recessão, inflação, deflação), pelo menos uma classe protege. Adaptado ao Brasil, vira:
- 25% ações (DCA em Dividend Yielders)
- 25% renda fixa longa (Tesouro IPCA+ longo)
- 25% ouro (ETF GOLD11 ou ouro físico via XAUUSD)
- 25% caixa (Tesouro Selic ou CDB curto)

**Lógica.**
- **Mecânica:** rebalanceamento anual (ou quando uma classe sair ±5% da alocação alvo).
- **Sem timing:** alocação fixa, decisões automáticas.

**Edge típico.**
- Retorno anual: 8–13% (real, descontada inflação)
- Volatilidade muito baixa: ~5–8% ao ano
- Sharpe ratio: alto (retorno-ajustado-ao-risco)
- Drawdown máximo histórico: ~12% (vs 40%+ de carteira 100% ações)

**Capital mínimo recomendado.** R$ 20.000+ para diversificar em 4 classes.

**Conhecimento exigido.** Mínimo. Disciplina de rebalanceamento.

**Modos de falha.**
- Cenário de "everything bull" (tudo sobe junto): performa abaixo de 100% ações.
- Cenário de "everything bear" (tudo cai junto): performa abaixo de 100% caixa.
- Bull market longo (10+ anos): renda fixa e caixa parecem "perdidos".

**Compatibilidade CaM.** ⚪ **Fora do escopo CaM** (mas filosoficamente alinhada). Pode ser referência para a alocação geral do patrimônio FORA do perímetro CaM.

**Verdict.** **Estratégia para quem quer dormir bem.** Não maximiza retorno — maximiza retorno ajustado a sobrevivência. Para quem viveu blow-up de R$ 100k em 2020, esta é a contraparte filosófica do CaM no nível patrimonial mais amplo.

---

# PARTE VI — SOBRE "MULTIPLICAÇÃO AGRESSIVA" — VOLTAIRE HONESTO

Você pediu técnicas agressivas para multiplicação de patrimônio. O catálogo acima inclui várias com perfil agressivo (Estratégias 7, 10, 5, 20). Mas o consultor honesto fala três coisas que você precisa ouvir antes de adotar qualquer uma delas:

**1. "Multiplicação agressiva" no varejo é, estatisticamente, sinônimo de "perda agressiva".**
A pesquisa acadêmica (Barber & Odean, Yale; estudo da B3 sobre day traders BR; relatório CVM 2022) é unânime: investidor PF que tenta retornos > 30% ao ano sustentadamente termina, em média, perdendo dinheiro vs benchmark passivo. As estratégias agressivas funcionam em mãos profissionais com infraestrutura, capital e psicologia rara. Em mãos amadoras, são armadilhas.

**2. O caminho realista para multiplicar patrimônio relevante é "edge pequeno × disciplina × tempo".**
Buffett ficou bilionário com retornos médios de ~20% ao ano em 60 anos. Isso não é "agressivo" no sentido convencional — é incrivelmente paciente. Multiplicação real vem de juros compostos sobre retorno consistente, não de tiros certeiros. Quem promete multiplicação rápida está vendendo curso.

**3. Para você especificamente (Carlos), a estratégia agressiva mais inteligente possível é o CaM como ele foi desenhado.**
O CaM é agressivo no comprometimento com disciplina, no rigor da Constituição, na obsessão com Risk Engine. Não é agressivo em alavancagem ou tamanho de aposta. **Essa é exatamente a inversão psicológica que separa quem ganha de quem quebra.** Ser "agressivo na disciplina" enquanto a maioria é "agressiva no risco" — esse é o seu edge real.

A Constituição do CaM (Arts. 4º, 5º, 21º, 22º) materializa essa filosofia: motor especulativo controlado alimentando patrimônio crescente. **Essa é a multiplicação agressiva legítima**, não o oposto.

---

# PARTE VII — MATRIZ DE COMPATIBILIDADE CAM

| # | Estratégia | Compatibilidade | Fase mínima | Observação |
|---|---|---|---|---|
| 1 | ORB 60min WIN | 🟢 | Fase 2 | Candidata natural a S1 |
| 2 | VWAP Mean Reversion | 🟡 | Fase 3 | Risco alto em dia de tendência |
| 3 | Volatility Breakout LW | 🟢 | Fase 2 | Clássica, edge erodiu |
| 4 | Bollinger Squeeze | 🟢 | Fase 2 | Boa S2 complementar |
| 5 | Spread WIN×WDO | 🔴 | Fase 4+ | Exige simultaneidade |
| 6 | Long Rompimento | ⚪ | N/A | Para Carteira Hard |
| 7 | Short Descoberto | 🔴 | N/A | Fora do espírito constitucional |
| 8 | Pair Trade Setorial | 🔴 | N/A | Capital insuficiente |
| 9 | Long Pré-Resultado | ⚪ | N/A | Carteira Hard tática |
| 10 | Short Squeeze Reverso | 🔴 | N/A | Padrão emocional adverso |
| 11 | Pullback Tendência | ⚪ | N/A | Carteira Hard tática |
| 12 | Box Trading Darvas | ⚪ | N/A | Carteira Hard tática |
| 13 | Setup 9.1 Stormer | ⚪ | N/A | Carteira Hard tática |
| 14 | DCA Dividend Yielders | 🟢 | Sempre | Núcleo Carteira Hard |
| 15 | DRIP Programado | 🟢 | Sempre | Combina com Harvest Rule |
| 16 | Quality Dividend | 🟢 | Sempre | Refinamento da #14 |
| 17 | Covered Call | 🟡 | Fase 4+ | Sobre Carteira Hard |
| 18 | Cash Secured Put | 🟡 | Fase 4+ | Construção tática Carteira Hard |
| 19 | FIIs Tijolo + Papel | 🟢 | Sempre | Componente natural Carteira Hard |
| 20 | Long Volatility OTM | 🟡 | Fase 4+ | Hedge patrimonial geral |
| 21 | Carteira Permanente | ⚪ | N/A | Filosofia patrimonial geral |

---

# PARTE VIII — PRÓXIMOS PASSOS SUGERIDOS

**Para o CaM (operação real):**

1. **S1 candidata: Estratégia 1 (ORB 60min)** — proposta no EDGE-THESIS-S1.md a ser gerado.
2. **S2 candidata: Estratégia 4 (Bollinger Squeeze)** — diversifica regime.
3. **S3 candidata: Estratégia 3 (Volatility Breakout)** — reserva para Fase 3.
4. **Construção da Carteira Hard:** combinação das Estratégias 14 + 15 + 19 (DCA + DRIP + FIIs).

**Para estudo e expansão futura:**

5. Estratégia 17 (Covered Call) quando Carteira Hard tiver lotes mínimos.
6. Estratégia 20 (Long Volatility) como hedge geral quando patrimônio justificar.
7. Estratégia 21 (Carteira Permanente) como filosofia de alocação macro fora do CaM.

**A descartar deste catálogo (não recomendados para seu perfil agora):**

- Estratégias 7, 8, 10 (shorts e pairs) — alto risco, baixo retorno-ajustado, fora do espírito do CaM.
- Estratégia 5 (Spread WIN×WDO) — capital insuficiente, complexidade desproporcional.

---

# ANEXO — Bibliografia mínima para aprofundamento

- **Larry Williams** — *Long-Term Secrets to Short-Term Trading*
- **Linda Bradford Raschke** — *Street Smarts*
- **Alexandre Wolwacz (Stormer)** — *Análise Técnica dos Mercados Financeiros*
- **William J. O'Neil** — *How to Make Money in Stocks*
- **Nicholas Darvas** — *How I Made 2,000,000 in the Stock Market*
- **Mark Spitznagel** — *Safe Haven: Investing for Financial Storms*
- **Harry Browne** — *Fail-Safe Investing*
- **B3** — Estudos de Day Trading PF (relatórios anuais)
- **CVM** — Educação Financeira (cvm.gov.br/educacional)

---

> **Última palavra de Voltaire:**
>
> Este catálogo te dá ferramentas. Ferramentas não constroem casa sozinhas. A casa que você está construindo (CaM) tem fundação (Constituição), planta (DAS, SPEC, PLAN) e mestre de obras (Risk Engine). As estratégias deste documento são tijolos — uns bons, outros ruins, alguns que parecem tijolos mas são bombas. Use o catálogo para conhecer o material disponível. Use a Constituição para decidir o que entra na obra.
>
> Multiplicar patrimônio é maratona, não sprint. E o sprint que parece atalho geralmente é o caminho mais longo — porque inclui a volta inteira depois do tombo.

---

**FIM DO CATÁLOGO**

---
template: ADR
phase: ARCH
status: Accepted
demanda: STRATEGYLAB-v0.6
---

# ADR-SL-03 — Execução multi-símbolo do EA no MT5 (Strategy Tester vs DEMO ao vivo)

> **Data:** 2026-06-03
> **Status:** Accepted — Founder 2026-06-03
> **Lead:** Oscar · **Co:** Nikola (engenharia EA/MQL5)
> **Aprovador final:** Founder
> **Vive em:** domínio `project`
> **Decisão delegada:** o Founder respondeu à Q1 *"O Oscar pode definir."* — este é o ADR
> mais pesado da demanda.

---

## 1. Contexto

Das 10 estratégias do escopo, **5 são multi-símbolo**: **D3, LS1, LS2, LS3** (par, 2
pernas) e **S1** (cesta/ranking N símbolos). O Assets Experts precisa de um **EA executor
novo** (distinto do `cam_bridge` read-only) que envie/modifique/feche ordem — e que opere
essas estratégias multi-símbolo, no **Strategy Tester** e/ou em **conta DEMO**.

**O problema real (honesto, Nikola):** o **MT5 Strategy Tester é single-symbol por
padrão** — roda o EA sobre **um** símbolo/gráfico. Ler outro símbolo de **dentro** do EA é
possível (`SymbolSelect`, `CopyRates`/`CopyTicks` do símbolo secundário, `iCustom`),
**mas com caveats no tester**:

- **Histórico do símbolo secundário no tester:** `CopyRates`/`CopyTicks` do segundo
  símbolo depende do histórico disponível para o tester; em "every tick based on real
  ticks", o tester sincroniza ticks do **símbolo do gráfico**, e o secundário pode não ter
  ticks reais sincronizados na mesma granularidade.
- **Sincronização de ticks entre símbolos:** o relógio do tester avança pelo símbolo
  primário; o secundário é consultado "como está" — pode haver **desalinhamento temporal**
  e barras do secundário "à frente/atrás" que introduzem look-ahead ou lacunas.
- **Modo de modelagem:** "every tick based on real ticks" dá fidelidade ao primário mas
  **não garante** ticks reais sincronizados do secundário; "1 minute OHLC" reduz fidelidade
  intrabar dos dois.

Em **conta DEMO ao vivo** (fora do tester), multi-símbolo é **direto e fiel** (o EA lê
ambos os books em tempo real, ticks reais, execução real de DEMO) — mas é **menos
reproduzível** (cada corrida vê um mercado diferente; não há "rodar de novo o mesmo
período").

Isto **não é impossibilidade — é decisão de arquitetura** (Q1). O motor Python e a
persistência (`research_*`) **já são** multi-símbolo naturalmente (ADR-SL-02); o gargalo
é **só o EA no tester**.

---

## 2. Decisão

### 2.1 Caminho híbrido por classe de estratégia (recomendação)

Não há um único modo que sirva bem a todas. Decisão: **casar o ambiente de validação à
natureza da estratégia.**

| Classe | Estratégias | Ambiente de execução/validação do EA | Razão |
|---|---|---|---|
| **Single-symbol** | D1, D2, V1, V2, S2 | **Strategy Tester** (every tick based on real ticks) | O tester é single-symbol nativo — fidelidade e reprodutibilidade máximas. Sem caveat. |
| **Par / 2 pernas** | D3, LS1, LS2, LS3 | **Conta DEMO ao vivo** (multi-símbolo direto), com o Strategy Tester como apoio limitado (ver §2.2) | Pares intraday/swing precisam dos **dois books sincronizados em ticks reais**; o tester não garante isso para o secundário. DEMO ao vivo é o ambiente **fiel** para par. |
| **Cesta / ranking** | S1 | **Conta DEMO ao vivo** (N símbolos), rebalance diário | Ranking cross-sectional sobre universo IBrX é inviável no tester single-symbol; é swing (sinal diário), DEMO ao vivo é adequado. |

> **Princípio (responde a Voltaire §2 do SCOPE):** para os multi-símbolo, **aceita-se
> validar em DEMO ao vivo (mais fiel, menos reproduzível)** em vez de forçar paridade
> trade-a-trade perfeita de um D3 dentro do tester (onde o secundário é não-confiável). A
> reprodutibilidade dos pares fica do lado **Python** (que é determinístico sobre dataset
> fixo); o EA em DEMO ao vivo prova a **executabilidade** das pernas atômicas no mundo real
> de DEMO.

### 2.2 Strategy Tester multi-símbolo como apoio (não como gate de paridade)

Para os pares, **é permitido** rodar o EA no tester lendo o símbolo secundário via
`CopyRates`/`SymbolSelect` **para desenvolvimento e sanity-check**, **desde que** os
caveats sejam documentados no run e o resultado **não** seja usado como prova de paridade
trade-a-trade (o secundário não é fiel). A **paridade dos pares** se dá assim:

- **Python (determinístico, dataset fixo)** = referência de **lógica/valores brutos**.
- **EA em DEMO ao vivo** = prova de **executabilidade das pernas atômicas** (entra/sai das
  duas no mesmo evento, sem perna solta).
- A paridade trade-a-trade rígida (100% sinais / ≤1 tick / volume idêntico, Q6) é exigida
  **dentro do que é reproduzível**: para single-symbol, no tester; para pares, sobre **o
  mesmo período/dataset capturado da DEMO** quando possível, ou rebaixada para **paridade
  de lógica de sinal** (mesmos pontos de entrada/saída) quando a reprodutibilidade exata
  do book de DEMO não existir. Esta nuance precisa entrar no SPEC do comparador.

### 2.3 Execução atômica das pernas

O EA executor implementa as pernas de um par como **operação atômica**: só monta a posição
se conseguir **as duas pernas** com book aceitável; se uma perna não preenche, **não monta
meia-posição** (perna solta = direcional não-intencional — modo de falha do catálogo). Saída
das duas pernas no mesmo evento. Isto espelha o C14 (par como unidade) e a regra do motor
Python (ADR-SL-02 §2.3).

### 2.4 Perna short mecânica, sem aluguel (Q8)

As LS têm perna short. No tester/DEMO, **vender a descoberto é mecanicamente possível** (o
ambiente permite `SELL`). **Não se modela aluguel/disponibilidade/custo de BTC** —
coerente com o MVP-bruto. Registrado como **simplificação consciente**: aluguel real =
Later (entra junto com C7/C8). Isto **infla** o edge das LS no bruto (esperado e enganoso —
ver ressalva do Voltaire); a UI deve rotular.

### 2.5 Guard-rail de conta DEMO (duplo)

O EA executor é **preso a conta DEMO** por:
1. **Configuração** (`input` apontando para conta/servidor DEMO), e
2. **Checagem em runtime no próprio EA:** lê o tipo de conta
   (`AccountInfoInteger(ACCOUNT_TRADE_MODE)`); se **não** for `ACCOUNT_TRADE_MODE_DEMO`,
   **recusa operar** (não envia ordem) e loga.

Live real **só por ato explícito do Founder** — e, quando solicitado, **para tudo e
aciona SEC-GOV/Kevin** antes (gatilho: integração externa com capital real). Não há
caminho de promoção silenciosa a real neste ADR.

---

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | **Tudo no Strategy Tester, multi-símbolo via `CopyRates` do secundário** | Caveat de fidelidade do secundário (histórico/ticks não sincronizados) torna a paridade trade-a-trade dos pares **não-confiável**. Usável p/ dev, não como gate. |
| 2 | **Tudo em DEMO ao vivo (inclusive single-symbol)** | Joga fora a reprodutibilidade do tester onde ela existe de graça (single-symbol). Desperdício. |
| 3 | **Pré-carregar séries sincronizadas e injetar no EA** | Reconstrói um mini-tester dentro do EA; frágil, muito código MQL5, recria o problema do tester. |
| 4 | **ZeroMQ: Python envia sinais multi-símbolo, EA só executa** | Mata o Strategy Tester e cria caminho de execução Python→ordem (rejeitado na ARCH-NOTE e no ADR-SL-01). |
| 5 | **Adiar multi-símbolo no EA (Python-only p/ pares)** | Multi-símbolo é IN por decisão do Founder; não pode ser rebaixado. |
| 6 | **Híbrido por classe: tester p/ single, DEMO ao vivo p/ par/cesta (ESCOLHIDA)** | Casa fidelidade × reprodutibilidade à natureza de cada estratégia; honesto sobre o limite do tester. |

---

## 4. Consequências

### Positivas
- **Honestidade sobre o limite do tester:** não se promete paridade trade-a-trade perfeita
  de pares onde o tester não a entrega.
- **Single-symbol ganha reprodutibilidade total** no tester (D1 primeiro — Q2).
- **Pares validados no ambiente fiel** (DEMO ao vivo, ticks reais, dois books).
- **Execução atômica + guard-rail DEMO** fecham os modos de falha de perna solta e salto
  para conta real.
- **Alinha com a ordem incremental** (Q2): D1 single-symbol no tester prova a arquitetura
  fim-a-fim antes de encarar o par.

### Negativas
- **Reprodutibilidade reduzida para pares.** DEMO ao vivo não roda "o mesmo período de
  novo". → Mitigação: a reprodutibilidade dos pares fica no **Python** (determinístico); o
  EA prova executabilidade. A paridade dos pares pode precisar ser **de lógica de sinal**,
  não trade-a-trade exata de preço — nuance a fixar no SPEC do comparador (ADR-SL-01 §2.3).
- **Dois protocolos de validação** (tester p/ single, DEMO p/ par) — mais complexidade
  operacional e de UI no Assets Experts.
- **Edge inflado das LS no bruto** (perna short sem aluguel) — enganoso por construção; tem
  que ser rotulado. Veredito real só com C7/C8 (Later).
- **DEMO ao vivo depende de janela de mercado aberto** para gerar evidência (não roda
  offline a qualquer hora como o tester). Impacta o ritmo de validação dos pares.

### Neutras
- O `mt5_integration` existente (`ea_dispatcher`/`multi_ea_manager`/`fill_subscriber`)
  orquestra/observa o EA nos dois modos sem mudança estrutural.
- Multi-símbolo torna o `.mq5` mais pesado, mas **não viola** o isolamento (execução no
  MQL5; backend só observa).

---

## 5. Custo de reversão

**Alto** no que toca o EA executor (código MQL5 é trabalho manual considerável e, por
ADR-SL-01, sem codegen — cada estratégia é escrita à mão). A **escolha de ambiente**
(tester vs DEMO) é, porém, **revertível em médio custo**: se o tester multi-símbolo se
provar suficiente no futuro (ou uma versão do MT5 melhorar a sincronização do secundário),
migrar pares para o tester é mudança de configuração + protocolo, não de arquitetura. O
guard-rail DEMO e a execução atômica são invariantes que não se revertem (são segurança).

---

## 6. Referências

- ARCH: [`../ARCH-STRATEGYLAB-TRIAD.md`](../ARCH-STRATEGYLAB-TRIAD.md) (§4.3, §8)
- SCOPE: [`../SCOPE-STRATEGYLAB-TRIAD.md`](../SCOPE-STRATEGYLAB-TRIAD.md) (Q1, Q2, Q8, §2.4, §8, §11 Voltaire)
- Contrato: [`../EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md`](../EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md) (C5, C6, C11, C14, §6 D/LS)
- Catálogo (modos de falha LS / perna short / squeeze): [`../CATALOGO-12-ESTRATEGIAS-ELEITAS.md`](../CATALOGO-12-ESTRATEGIAS-ELEITAS.md) (LS1/LS2/LS3)
- Código: `mt5_integration/{ea_dispatcher,multi_ea_manager,fill_subscriber}` · `mql5/experts/{cam_bridge,cam_risk_mirror}.mq5`
- ADRs relacionadas: [ADR-SL-01](ADR-SL-01-definicao-comum-dupla-implementacao.md) · [ADR-SL-02](ADR-SL-02-persistencia-backtest-mvp-bruto.md)

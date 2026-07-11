---
template: ADR
phase: ARCH
status: Accepted
demanda: STRATEGYLAB-v0.6
---

# ADR-SL-02 — Persistência + motor de backtest MVP-bruto multi-série

> **Data:** 2026-06-03
> **Status:** Accepted — Founder 2026-06-03
> **Lead:** Oscar · **Co:** Ada (dados)
> **Aprovador final:** Founder
> **Vive em:** domínio `project`

---

## 1. Contexto

O Assets RunTests precisa rodar o backtest matemático em Python de **10 estratégias**
(5 multi-símbolo), persistir os dados e produzir equity/trades/métricas em **valores
brutos** (Founder: sem corretagem, emolumentos, slippage, IR). O estado real impõe três
fatos que forçam decisão:

1. **`backtest/simulator.py` é acoplado ao Risk Engine e ao IR.** Importa `_shared.risk`
   (`validate`, `RiskContext`, `Approved`) e `domain.py` aplica `IR_RATE = 0.20` em
   `BacktestTrade.tax_provisioned`/`result_net`. O modo MVP-bruto **não pode** depender
   disso. O simulator é também **single-position** ("nenhum candidato novo até fechar") e
   **single-symbol**.
2. **`research/leadlag/bars.py` já é a barra canônica** (C1/C7): pura, zero I/O, M1→TF
   determinística, multi-símbolo, ancorada na sessão B3. É reuso direto.
3. **`research_bars`/`research_ticks`** já modelam múltiplos símbolos com provenance
   (TimescaleDB) — ingestão canônica pronta.

Decisões já travadas pelo Founder a respeitar: Q4 (reusar `research_*` + criar só o novo
de domínio), Q5 (indicadores on-the-fly), Q7 (barra canônica `bars.py` + fuso
America/Sao_Paulo idêntica entre símbolos do par), Q10 (par como unidade).

---

## 2. Decisão

### 2.1 Ingestão: reusar `research_*`, não criar `strategy_*` paralelas (Q4)

- **`research_bars` / `research_ticks`** são a **camada de ingestão canônica** —
  multi-símbolo, com provenance. **Nenhuma** tabela `strategy_ticks`/`strategy_bars` é
  criada (evita duplicar tick/candle e divergir provenance).
- **Provenance é inegociável mesmo no MVP:** dado sem origem rastreável não entra.

### 2.2 Novo de domínio (mínimo) — par como unidade (Q10)

Cria-se **só** o que é domínio de estratégia, na feature `strategy_lab`:

| Entidade | Papel | Nota |
|---|---|---|
| `strategy_param_set` | conjunto de parâmetros de uma estratégia (inclui os **sugeridos** pelo otimizador, marcados como `suggested`, não aplicados) | liga DEF ↔ run |
| `backtest_run` | execução (reuso/extensão de `backtest/domain.py:BacktestRun`) | ganha `symbols[]`, `unit` |
| `backtest_leg_trade` | **trade multi-perna**: `pair_id` + `leg` (long/short) + `symbol` | a contabilização da **unidade é o par** (Q10); as pernas existem para auditoria/UI |

**Decisão fina (estava aberta na §2.3 do SCOPE):** modela-se com **`leg` + `pair_id`
numa tabela de pernas**, e a unidade-par é uma **agregação** (`pair_id` + janela de
entrada/saída comum), **não** uma entidade `backtest_pair_trade` separada. Razão: o
caso `single` é o `pair` com uma perna só → um único modelo cobre single/pair/basket,
sem inflar o domínio. A UI e o relatório de paridade leem a agregação por `pair_id`
(gain/loss do spread agregado — Q10); "perna separada" fica disponível se o Founder
pedir (ele disse "se sentir falta peço separado").

### 2.3 Motor MVP-bruto multi-série — feature nova, derivada, desacoplada

- O motor vive em **`features/strategy_lab/backtest_engine.py`** (slice novo), **não** em
  `features/backtest/`. Razão: não contaminar o caminho Risk-acoplado existente (não
  regressão) e nascer limpo.
- **Desacoplamento total do Risk Engine/IR:** `backtest_engine` **não importa
  `_shared.risk`** e **não aplica IR nem corretagem**. P&L = `pontos × valor_do_ponto ×
  qtd`, **bruto**, fim. O `BacktestTrade.tax_provisioned`/`result_net` (IR/corretagem) do
  domínio antigo **não é usado** no caminho bruto — o trade bruto reporta só
  `pnl_bruto` e `volume_financeiro`.
- **Multi-série:** o engine lê **N séries** de `research_*`, deriva barras canônicas por
  `bars.py`, e **sincroniza por timestamp** (mesma barra `[t, t+Δ)` carimbada em `t`,
  fuso America/Sao_Paulo — Q7), **idêntica entre os símbolos do par**. Barra ausente num
  símbolo num timestamp = regra explícita (não opera a perna naquele bar; sem
  meia-posição). Reusa `walk_forward.py` para OOS.
- **Execução atômica das pernas** (par como unidade): entra/sai das pernas no mesmo
  evento de barra (C14). Single-position por estratégia mantido (uma posição/par por vez
  no MVP).

### 2.4 Indicadores on-the-fly (Q5)

Indicadores computados **sob demanda** a partir das barras canônicas, a cada run. **Sem**
tabela de indicadores materializados no MVP (menos drift, mais simples). Materialização =
Later (0.6.1), só se o recompute ficar caro.

### 2.5 Métricas brutas canônicas — rotina única

As métricas (WR, expectância **bruta**, profit factor, nº trades, max drawdown, equity)
são calculadas por **uma rotina Python única** que consome o **ledger de trades de schema
único**, alimentada tanto pelo backtest Python quanto pelo export do EA (ADR-SL-01 §2.3).
Métrica **nunca** é recalculada "do jeito do MT5". Isto torna a paridade de métricas uma
**função pura do ledger** — elimina uma classe inteira de divergência.

### 2.6 Promoção de kernel (resolve a tensão de import-linter)

`backtest_engine` precisa de `bars.py` (e o `optimizer` precisa de `validation.py`),
ambos hoje em `features/research/leadlag/`. `strategy_lab → research` seria
**feature→feature** (proibido pelo import-linter). **Decisão:** **promover `bars.py`**
(e `validation.py` se o optimizer o consumir diretamente) para
**`_shared/research_kernel/`** — justificado pela regra "3+ features OU mandato": `bars.py`
passa a ser usado por research, backtest, strategy_lab e paridade. São funções puras (zero
I/O), promoção barata. O **momento** (antes de D1 ou junto do multi-símbolo) é detalhe do
SPEC/PLAN; o **destino** (`_shared/`) é decidido aqui.

---

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | **Tabelas `strategy_bars`/`strategy_ticks` próprias** | Duplica tick/candle, diverge provenance, contraria Q4. `research_*` já é multi-símbolo. |
| 2 | **Estender `backtest/simulator.py` com flag `gross_mode`** | Contamina o caminho Risk-acoplado (risco de regressão no fluxo existente); mistura responsabilidades. Slice novo é mais limpo. |
| 3 | **Entidade `backtest_pair_trade` dedicada** | Bifurca o modelo single vs pair; `leg + pair_id` cobre os três casos (single/pair/basket) com um modelo só. |
| 4 | **Materializar indicadores já no MVP** | Mais drift e complexidade sem ganho provado; Founder pediu on-the-fly primeiro (Q5). |
| 5 | **Manter `bars.py` em `research/` e importar cross-feature** | Viola import-linter (feature→feature). Promover a `_shared/` é o caminho legítimo. |
| 6 | **Reusar `research_*` + novo de domínio mínimo + engine bruto desacoplado (ESCOLHIDA)** | Respeita Q4/Q5/Q7/Q10, não regride o existente, isola o modo bruto. |

---

## 4. Consequências

### Positivas
- **Não regride** o backtest Risk-acoplado existente (caminho intocado).
- **Reuso alto:** `bars.py`, `walk_forward.py`, `research_*`, `validation.py`, padrão de
  `BacktestRun`/`BacktestTrade`.
- **Métricas como função pura do ledger** → paridade de métricas trivial e confiável.
- **Domínio enxuto:** um modelo de trade cobre single/pair/basket.
- **Promoção de `bars.py` a `_shared/`** legitima o reuso e melhora a arquitetura geral.

### Negativas
- **Dois motores de backtest convivem** (o Risk-acoplado em `backtest/` e o bruto em
  `strategy_lab/`). Risco de divergência conceitual futura. → Mitigação: quando custos/IR
  entrarem (Later), avaliar unificar com o bruto como base e o Risk/IR como camada
  opcional por cima. Registrado como dívida consciente.
- **"Valores brutos" inflam o edge** (ressalva do Jim/Voltaire): equity bonita ≠
  estratégia que ganha. **Crítico nas LS** (refém do custo). → A UI deve rotular
  explicitamente "BRUTO — sem custo/IR"; "tem edge líquido?" só com C7/C8 (Later). Isto é
  requisito de produto para o SPEC, não opcional.
- **Promoção de `bars.py`** mexe em imports de quem já o usa (research) → mudança mecânica
  ampla, mas de baixo risco (API pura estável).

### Neutras
- Sincronização N-séries por timestamp é trabalho de design novo, mas `bars.py` já entrega
  barras determinísticas alinhadas por sessão — a sincronização é um join por `ts_open`.
- `strategy_param_set` guarda sugestões do otimizador sem aplicá-las (ADR-SL-03 do
  otimizador no SCOPE: sugere, não aplica).

---

## 5. Custo de reversão

**Médio.** O schema novo (`strategy_param_set`, `backtest_leg_trade`) é aditivo —
reverter é dropar tabelas não referenciadas. O engine bruto é uma feature isolada (apagar
o slice não toca o resto). O ponto mais caro de desfazer é a **promoção de `bars.py` a
`_shared/`** (reverter exige re-mexer imports), mas é mudança mecânica de baixo risco.

---

## 6. Referências

- ARCH: [`../ARCH-STRATEGYLAB-TRIAD.md`](../ARCH-STRATEGYLAB-TRIAD.md) (§3.2, §3.3, §7)
- SCOPE: [`../SCOPE-STRATEGYLAB-TRIAD.md`](../SCOPE-STRATEGYLAB-TRIAD.md) (Q4, Q5, Q7, Q10, §2.2, §2.3)
- Código real: `backtest/{simulator,domain,walk_forward}.py` · `research/leadlag/{bars,validation}.py` · `research_bars`/`research_ticks`
- ADRs relacionadas: [ADR-SL-01](ADR-SL-01-definicao-comum-dupla-implementacao.md) · [ADR-SL-03](ADR-SL-03-execucao-multisimbolo-ea-mt5.md)

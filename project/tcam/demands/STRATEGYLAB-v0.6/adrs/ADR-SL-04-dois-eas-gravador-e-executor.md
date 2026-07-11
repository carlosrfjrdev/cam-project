---
template: ADR
phase: ARCH
status: Accepted
demanda: STRATEGYLAB-v0.6
---

# ADR-SL-04 — Dois EAs para a estratégia D1: gravador de paridade + executor efetivo

> **Data:** 2026-06-03
> **Status:** Accepted — Founder 2026-06-03
> **Lead:** Oscar (+ Kevin SEC no guard-rail)
> **Aprovador final:** Founder
> **Vive em:** domínio `project`
> **Complementa:** [ADR-SL-01](./ADR-SL-01-definicao-comum-dupla-implementacao.md) (dupla
> implementação Py↔MQL5), [ADR-SL-03](./ADR-SL-03-execucao-multisimbolo-ea-mt5.md).

---

## 1. Contexto

A Onda 1 entregou primeiro o EA `cam_d1_orb30.mq5` como **gravador de paridade**: ele
computa a estratégia D1 e exporta o ledger canônico em CSV, mas **não envia ordem**
(fora da allowlist de `OrderSend` do `lint_mql5.py`). O objetivo era provar a **paridade
matemática** Python↔MQL5.

O Founder, ao testar no Strategy Tester, apontou (verbatim): *"eu estava esperando que o
próprio EA faria as operações... crie um segundo EA para estratégia D1 que opera
efetivamente a estratégia, podemos manter a diretriz atual e adicionar um EA efetivo com
a estratégia, para o backtest"*.

Ou seja: o gravador resolve paridade, mas **não mostra a estratégia operando** (aba
Negociações vazia). Faltou no escopo um EA que execute de fato.

## 2. Decisão

Adotar um **modelo de dois EAs** para a mesma estratégia D1, com papéis distintos:

| EA | Papel | Envia ordem? | Allowlist `lint_mql5` |
|---|---|---|---|
| `cam_d1_orb30.mq5` | **Gravador de paridade** — exporta ledger canônico p/ comparar com o backtest Python | ❌ não | fora (read-only) |
| `cam_d1_orb30_exec.mq5` | **Executor efetivo** — opera a estratégia a mercado com SL/TP, visível no Strategy Tester | ✅ sim | **dentro** (DEMO-only) |

A diretriz do gravador (ADR-SL-01) **permanece** — ele continua sendo a defesa de
paridade. O executor é **adicionado**, não substitui.

### 2.1 Escopo do executor (decisão do Founder)

- Executa a **estratégia D1 PURA**: OR-30, quebra → entrada a mercado, SL no extremo
  oposto, TP = `target_r` × range, um disparo por direção/dia, flat no fim da sessão.
- **Ainda NÃO verifica risco** — sem Risk Engine / Assets RiskManager. Verbatim do
  Founder: *"ainda não estamos verificando os riscos"*. A camada de risco entra depois.
- SL/TP são geridos pela corretora/tester (saída intrabar realista) — por isso o
  resultado do executor **não é tick-idêntico** ao backtest Python (modelo de fill
  diferente). Isso é esperado: paridade continua sendo papel do gravador.

### 2.2 Segurança (Kevin)

O executor envia ordem, então carrega o **guard-rail duplo DEMO**:
`InpRequireDemoAccount` (input) **+** checagem em runtime de
`AccountInfoInteger(ACCOUNT_TRADE_MODE)` — recusa `OnInit` se a conta não for DEMO.
Entra na allowlist do `lint_mql5.py` junto de `cam_risk_mirror.mq5`; o gravador
permanece **fora** da allowlist (não pode regredir e enviar ordem).

## 3. Consequências

**Positivas:**
- O Founder vê a estratégia operando no Strategy Tester (validação visual/comportamental).
- Paridade matemática preservada (gravador intacto).
- Allowlist explícita e testada (`test_lint_mql5.py` cobre os dois EAs permitidos + o
  gravador que deve continuar proibido).

**Custos / dívida:**
- Três implementações da lógica D1 agora (Python, gravador MQL5, executor MQL5). O
  gravador e o executor compartilham a MESMA lógica de OR/quebra, mas divergem no modelo
  de saída (gravador = pior-caso canônico; executor = SL/TP do broker). Manter as três em
  sincronia é responsabilidade de quem editar a estratégia. TD registrada.
- Executor sem Risk Engine é **deliberadamente inseguro para conta real** — mitigado pelo
  guard-rail DEMO. Quando a camada de risco existir, o executor deve passar a consultá-la
  (provável evolução: executor → consome Assets RiskManager, como `cam_risk_mirror` faz).

## 4. Alternativas descartadas

- **Um EA único parametrizável (modo gravador | executor):** rejeitado — mistura um
  arquivo read-only com um que envia ordem, contaminando a clareza da allowlist de
  segurança. Dois arquivos = fronteira de segurança nítida.
- **Codegen do executor a partir do gravador:** rejeitado — contraria ADR-SL-01 (Founder
  vetou codegen; dupla/tripla implementação é deliberada).

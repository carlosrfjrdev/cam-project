---
template: ARCH-NOTE
phase: ARCH
status: Proposed (soft-stage — moldável, não-HARD)
produto: CaM (cam-cockpit)
titulo: Paridade EA MT5 ↔ Python Strategy Lab — arquitetura do espelho
data: 2026-06-03
lead: Oscar
co: Vint (infra/MT5 runtime), Kevin (threat-model da fronteira), Ada (dados/provenance), Jim (contrato de edge)
vinculacao: SCOPE-STRATLAB-PARITY-001 · EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5
aviso: research-only. A trava constitucional está desligada apenas para estudo/backtest.
       Nenhum componente aqui envia ordem real. EAs DEMO-only. ADRs candidatos = Proposed.
---

# ARCH-NOTE — Paridade EA MetaTrader 5 ↔ Python Strategy Lab

> **Oscar:** O pedido do Founder — "tudo que o EA faz, o Python faz; um é espelho do outro"
> — é, em arquitetura, um problema de **uma especificação, duas execuções, prova de
> equivalência**. A pergunta estruturante não é "como escrevo os dois?", e sim **"qual é a
> fonte da verdade da estratégia, e como provo que as duas execuções a honram?"**. Esta nota
> resolve isso e enumera os ADRs candidatos.

---

## 1. Decisão central — qual é a fonte da verdade?

Três modelos possíveis para manter Python e EA espelhados:

| Modelo | Como funciona | Veredito |
|---|---|---|
| **(a) Dupla implementação + spec declarativa + suíte de paridade** | A estratégia é descrita numa **spec única** (YAML/JSON: sinais, stops, filtros, custos, sessão). Python e MQL5 implementam **cada um** a partir da mesma spec. Uma **suíte de testes de paridade** roda os dois sobre o mesmo dataset e prova equivalência (contrato do Jim §5). A spec + a suíte são a **fonte da verdade**. | ✅ **RECOMENDADO** |
| **(b) ZeroMQ — Python como cérebro, EA como braço** | O EA não tem lógica; só recebe sinais do Python via ZeroMQ e executa. "Paridade" trivial porque só há um cérebro. | ❌ **REJEITADO** |
| **(c) DSL própria + codegen** | Uma linguagem/DSL descreve a estratégia e **gera** o Python e o MQL5 automaticamente. Paridade por construção. | ⏳ **DIFERIDO** (alvo futuro) |

### Por que (a) e não (b)
- **(b) quebra o Strategy Tester.** O grande valor do MT5 para o Founder é rodar o EA no
  **Strategy Tester** (backtest histórico nativo, tick-by-tick). Um EA que só obedece ao
  Python via ZeroMQ **não roda no Strategy Tester** — perde-se exatamente o ambiente que o
  Founder quer usar para validar.
- **(b) viola o Art. 19º na promoção futura.** Um EA-braço dependente de um processo Python
  externo cria **posição aberta sob cobertura de um runtime que pode cair** — se o Python
  morre, o EA fica órfão com posição. Arquitetura proibida para qualquer caminho rumo ao real.
- **(b) cria caminho de execução** Python→ordem, encostando na trava do Art. 35º mesmo em
  DEMO. (a) mantém os dois ambientes **independentes e auto-suficientes**.
- O bridge ZeroMQ continua válido para **market data read-only** (127.0.0.1), não para sinal.

### Por que (c) depois, não agora
- DSL+codegen é a resposta "correta" a longo prazo (paridade por construção elimina a classe
  de bug do contrato do Jim). Mas construir DSL **antes** de ter ≥3 estratégias espelhadas é
  **over-engineering**: projeta-se a abstração errada sem dados. **Gatilho de promoção a (c):**
  quando **3+ estratégias** estiverem implementadas em (a) e a suíte de paridade revelar os
  padrões recorrentes, extrai-se a DSL a partir do que **de fato** se repete.

> **Caminho evolutivo:** **(a) agora → (c) quando 3+ estratégias convergirem.** (a) não é
> jogado fora: a spec declarativa de (a) é o **embrião** da DSL de (c).

---

## 2. Contrato de dados (a base da paridade)

A paridade é impossível se os dois ambientes não comerem **o mesmo dado, do mesmo jeito**.
Decisões canônicas (espelham C1–C2, C13 do contrato de edge):

- **Fonte única:** tick/candle **exportado do MT5** é o dataset canônico. O Python **não**
  busca dado de outra fonte para validação de paridade — consome o mesmo export. Provenance
  obrigatória (Ada): hash, símbolo, período, build do MT5.
- **Fuso canônico:** **UTC interno**, apresentação em America/Sao_Paulo (B3). Toda barra
  carimbada pelo **timestamp de abertura**. Conversão na ingestão, nunca na decisão.
- **Timeframe primário:** **M1** como base. TFs maiores são **agregados de M1** pela mesma
  rotina (left-closed bucketing: barra `[t, t+Δ)` carimbada em `t`). Proibido usar a
  agregação nativa do MT5 de um lado e a do Python de outro — agregar **a partir do M1**
  determinístico nos dois.
- **Bucketing left-closed** explícito: uma barra contém `[abertura, próxima_abertura)`.
  Define o exato conjunto de ticks de cada barra → elimina ambiguidade de fronteira.
- **Ajustes (proventos/split):** decisão única por família (ações ajustadas vs não), aplicada
  **idêntica** nos dois (espelha C13).

---

## 3. Determinismo (onde o espelho costuma quebrar)

- **Fill canônico `next-bar-open`** (C4): a arquitetura **proíbe** o fill no close da barra de
  sinal nos dois ambientes. No EA isso significa **não** usar a conveniência do Strategy Tester
  de execução no mesmo candle; modela-se entrada no open da barra seguinte.
- **Reimplementação de indicadores:** os indicadores do MT5 (`iMA`, `iRSI`, etc.) têm detalhes
  de inicialização/seed (período de warm-up, tratamento das primeiras barras) que **diferem**
  de uma implementação ingênua em Python. Decisão: **a definição do indicador é canônica e
  reimplementada identicamente** dos dois lados (mesma fórmula, mesmo warm-up, mesmo
  arredondamento) — **não** se confia no default de nenhum dos dois. Indicadores entram na
  **suíte de paridade nível N1** (§4).
- **Ordem de avaliação por barra fechada** (C3): mesma sequência saída→entrada→filtro→risco,
  uma vez por barra, nos dois.
- **Determinismo total:** seed fixa onde houver aleatoriedade; pipeline reprodutível.

---

## 4. Pirâmide de paridade (como se prova, em camadas)

> A suíte de paridade não testa só o resultado final — testa **em camadas**, do mais baixo ao
> mais alto. Falha embaixo invalida tudo acima; por isso se testa de baixo para cima.

```
            ┌─────────────────────────────┐
   N3       │  Paridade de MÉTRICAS        │  expectância, DD, Sharpe, WR ≤ tolerância (§5 Jim, Camada 2)
            ├─────────────────────────────┤
   N2       │  Paridade de TRADES          │  mesmos sinais 100%, preço ≤ 1 tick (§5 Jim, Camada 1)
            ├─────────────────────────────┤
   N1       │  Paridade de INDICADORES     │  iMA/iRSI/VWAP… Python == MQL5, barra a barra
            ├─────────────────────────────┤
   N0       │  Paridade de DADOS           │  mesmo dataset, mesmo bucketing, mesmo fuso (§2)
            └─────────────────────────────┘
```

- **N0 — Dados:** os dois leem o mesmo export, agregam M1 igual, mesmo carimbo. Sem N0, nada
  acima é comparável.
- **N1 — Indicadores:** cada indicador reimplementado bate **barra a barra** entre Python e
  MQL5 (dentro de epsilon de ponto-flutuante). **É aqui que a maioria das divergências nasce**
  — por isso é nível próprio, testado antes de olhar trades.
- **N2 — Trades:** Camada 1 do contrato do Jim (100% sinais, ≤1 tick, sizing/motivo idênticos).
- **N3 — Métricas:** Camada 2 do Jim (≤2% expectância, ≤1pp WR, ≤3% DD).

**Regra:** falha em N1 explica falha em N2/N3 — corrige-se de baixo para cima. Nunca "ajustar
métrica" (N3) para casar com um indicador quebrado (N1).

---

## 5. Componentes (arquitetura do Strategy Lab Python)

Módulos do laboratório Python, com fronteiras claras (cada um espelhável/testável isolado):

| Componente | Responsabilidade | Espelho no EA |
|---|---|---|
| **data_loader** | Ingerir export MT5, normalizar fuso (UTC), agregar M1→TF (left-closed), provenance | (EA usa o feed do Strategy Tester sobre o mesmo histórico) |
| **signal_engine** | Avaliar indicadores + regras de entrada/saída por barra fechada (C3) | Bloco de lógica do `.mq5` (idêntico) |
| **cost_model** | Corretagem, emolumentos, slippage, aluguel — de **arquivo único de custos** | `input` do EA lidas do mesmo arquivo de custos |
| **fill_model** | `next-bar-open`, intrabar pior-caso (C5), gap honesto (C6) | Lógica de ordem do EA conforme as mesmas regras |
| **portfolio_ledger** | Estado de posição (par como unidade em LS — C14), realização de P&L, IR (C8) | Contabilização do EA (espelhada) |
| **metrics_report** | Calcular métricas canônicas (§4 Jim) a partir do **ledger de trades de schema único** | EA **exporta o ledger**; métricas são calculadas pela **mesma rotina Python** |
| **parity** | Rodar N0–N3, comparar, emitir relatório PASS/FAIL + classificação por C1–C14 | — (a camada de prova vive só no Python; consome o export do EA) |

> **Decisão de design importante:** o **cálculo de métricas é código Python único**. O EA
> **não** calcula métricas "do jeito do MT5"; ele **exporta o ledger de trades** (schema fixo
> do §4 Jim), e o `metrics_report` do Python calcula. Isso elimina uma classe inteira de
> divergência (N3 vira função pura do ledger).

---

## 6. ADRs candidatos (Proposed — decisão do Founder)

> Soft-stage: todos **Proposed**, moldáveis. Recomenda-se decidir **B e D primeiro** — são os
> que destravam o resto.

| ADR | Título | Decisão proposta | Prioridade |
|---|---|---|---|
| **ADR-A** | Fonte da verdade da estratégia | Modelo **(a)** dupla implementação + spec declarativa + suíte de paridade; rejeitar (b); diferir (c) até 3+ estratégias | Alta |
| **ADR-B** | Modelo de fill e avaliação | **`next-bar-open`** + intrabar pior-caso + gap honesto + ordem de avaliação por barra fechada (C3–C6) | **Primeira** |
| **ADR-C** | Contrato de dados | Export MT5 como fonte única; UTC interno; M1 primário; left-closed bucketing; agregação determinística (§2) | Alta |
| **ADR-D** | Modelo de custo + tolerância de paridade | **Arquivo único de custos** lido pelos dois; tolerâncias da §5 Jim (100% sinais / ≤1 tick / ≤2% expectância / ≤1pp WR / ≤3% DD) | **Primeira** |
| **ADR-E** | Reimplementação de indicadores | Indicadores canônicos reimplementados idênticos nos dois; testados em N1; não confiar em default MT5/Python | Média |
| **ADR-F** | Suporte multi-símbolo no Strategy Tester | Definir quais famílias (D3/LS spread, LS à vista 2 pernas) rodam no Strategy Tester vs Python-only | Média |

> **B e D primeiro** porque fill (B) e custo+tolerância (D) são as duas fontes dominantes de
> divergência e condicionam o desenho do `fill_model`, do `cost_model` e da suíte `parity`.

---

## 7. Fronteira de segurança (SEC-GOV)

> **Kevin (threat-model curto recomendado, não-bloqueante nesta fase de research).**

SEC-GOV **não é mandatório** para este laboratório de research **se** as **3 barreiras de
isolamento** abaixo forem mantidas. Se qualquer uma cair, **aciona-se Kevin** (Art. 35º + 9
gatilhos):

1. **Sem caminho de execução real.** Nenhum componente (Python ou EA) envia ordem a conta
   real. EAs em **conta DEMO**, guardrails do RUNBOOK-WINDOWS. Bridge ZeroMQ = **read-only
   market data**, 127.0.0.1, nunca sinal/ordem.
2. **Isolamento de runtime.** O Strategy Lab é um subsistema separado, sem acoplamento ao
   (futuro) Risk Engine/kill switch/journal. Research não passa pela trava — logo não pode
   **encostar** na trava.
3. **Isolamento de credenciais.** Nenhum segredo de corretora real no laboratório; conta DEMO
   isolada; nenhum `.env` de produção referenciado.

**Gatilho obrigatório de SEC-GOV:** se em algum momento se desejar (a) promover estratégia ao
real, (b) conectar o EA a conta real, (c) fazer o Python enviar qualquer sinal de ordem, ou
(d) acoplar o laboratório ao Risk Engine/journal — **para tudo e aciona Kevin** antes.

---

## 8. Resumo executivo

- **Modelo (a)** — spec declarativa única + dupla implementação (Python + MQL5) + **suíte de
  paridade como fonte da verdade**. Rejeita (b) ZeroMQ-cérebro (mata Strategy Tester + Art.
  19º). Difere (c) DSL/codegen até **3+ estratégias** convergirem.
- **Contrato de dados:** export MT5 único, UTC interno, M1 primário, left-closed bucketing.
- **Determinismo:** `next-bar-open`, indicadores reimplementados idênticos, ordem de avaliação
  por barra fechada.
- **Pirâmide de paridade N0→N3:** dados → indicadores → trades → métricas. Corrige de baixo
  para cima.
- **Métricas = função pura do ledger** (schema único), calculadas só no Python.
- **6 ADRs candidatos (Proposed)** — decidir **B (fill) e D (custo+tolerância) primeiro**.
- **SEC-GOV não-mandatório** nesta fase **se** as 3 barreiras de isolamento (sem execução real,
  runtime isolado, credenciais isoladas) se mantiverem. Threat-model curto do Kevin recomendado.

---

> Research-only · soft-stage (Proposed, não-HARD) · 2026-06-03 · Lead: Oscar 🏛️
>
> **Referências:** [SCOPE STRATLAB-PARITY-001](../scopes/SCOPE-STRATLAB-PARITY-001.md) ·
> [EDGE/contrato de paridade (Jim)](../research/EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md) ·
> [Catálogo das 12 estratégias](../../strategies/CATALOGO-12-ESTRATEGIAS-ELEITAS.md) ·
> [DAS](../DAS.md) · [STACK-CAM-OFICIAL](../../STACK-CAM-OFICIAL.md) ·
> [Constituição](../../../CONSTITUICAO.md) — Arts. 19º, 35º

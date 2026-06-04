---
template: SCOPE
phase: DISC
status: Draft — aguarda gate do Founder
produto: TCaM (cam-cockpit)
id: SCOPE-STRATEGYLAB-TRIAD
version: v0.6
slug: strategylab-triad-strategy-runtests-experts
data: 2026-06-03
lead: Marty
orquestrador: Leo
solicitante: Founder
supersede_parcial: SCOPE-STRATLAB-PARITY-001 (vira insumo; paridade rebaixada de título para sub-objetivo)
modo: >
  Produto TCaM. Constituição DESCOMISSIONADA (2026-06-03) — sem Risk Engine soberano,
  sem Arts., sem "preservar capital" como lei. Permanece apenas o RIGOR de engenharia
  (anti-data-snooping, paridade Py↔EA) como boa prática, não como amarra constitucional.
  MVP SEM CUSTOS (decisão verbatim do Founder). Execução de ordem ATIVA no EA
  (Strategy Tester/DEMO). Live real continua OUT.
personas_consultadas: [Marty, Oscar, Jim, Nassim, Ada, Nikola, Don, Peter, Voltaire]
---

# SCOPE — StrategyLab do CaM · A Tríade Assets Strategy + RunTests + Experts

> **Reposicionamento (Leo):** este SCOPE substitui o título do `SCOPE-STRATLAB-PARITY-001`.
> Lá, o **organizador era a paridade**. Aqui, o organizador são os **três módulos de produto**
> que o Founder quer ver funcionando — **Assets Strategy**, **Assets RunTests**,
> **Assets Experts**. A paridade Python↔EA continua sendo o coração técnico, mas vira
> **sub-objetivo**, não o nome da entrega. E o MVP nasce **sem custos** — paridade de
> **lógica** (entrada/saída/gain/loss/volume), não de **fricção**.

---

## 1. Contexto e motivação

### 1.1 A virada para produto
O CaM virou **TCaM** — produto para terceiros operarem. A Constituição foi descomissionada
(`project/tcam/CONSTITUTION-DECOMMISSION.md`). Não há mais Risk Engine como lei, limite de
2 contratos como artigo, nem "preservação de capital" como hierarquia soberana. O Risk Engine
sobrevive como **feature** (Assets RiskManager) e está **fora** deste SCOPE.

O que **fica** dos artefatos anteriores (eram corretos como engenharia, não como lei):
- A **régua anti-data-snooping** do Jim (DSR, walk-forward, ≥N trades OOS, no-cliff).
- O **contrato de paridade C1–C14** do EDGE-CONTRATO — adaptado: no MVP só os itens de
  **lógica** valem; os itens de **custo/IR** (C7/C8) ficam **Later**.

### 1.2 Os três módulos (mapa → estado real)
`MAP-MODULES-TCaM.md` já mapeou os três a features existentes — **nenhum nasce do zero**:

| Módulo | Frontend existente | Backend existente | Estado |
|---|---|---|---|
| **Assets Strategy** | `features/strategies/StrategyRegistryPage` | `features/strategies` (+ `dsl/{parser,compiler}`, `strategies/orb_60m_win`) | ✅ base; falta **otimizador** |
| **Assets RunTests** | `features/backtest/BacktestPage` + `paper-trading` | `features/backtest/{simulator,walk_forward}` + `research/leadlag/{bars,validation}` | ⚠️ motor parcial + acoplado a Risk/Constituição |
| **Assets Experts** | `features/robot-orchestrator` + `features/ea-control` | `features/mt5_integration` + `robot_orchestrator` + EAs `cam_bridge`/`cam_risk_mirror` | ⚠️ plumbing existe; falta **EA executor** |

> **Marty (anti-feature-factory):** a tentação aqui é construir os três módulos + otimizador +
> EA executor de uma vez, para 12 estratégias. Isso é **fábrica de features disfarçada de
> produto**. A entrega-âncora deste SCOPE é **uma estratégia (D1 ORB-30) fim-a-fim** nos três
> módulos, com paridade de lógica provada, **antes** de escalar para qualquer outra.

### 1.3 Reaproveitamento — a descoberta que muda o tamanho
O estado real (`apps/cam-cockpit/backend/cam/features/`) já contém quase todas as peças:

- **DSL declarativa já existe** (`strategies/dsl/parser.py` + `compiler.py`): lê YAML/JSON
  (`strategy/asset/indicators/entry/exit`) → classe `Strategy` em runtime, com **AST whitelist**
  segura (sem `eval`). **Esta é a semente do contrato de estratégia única.**
- **Barra canônica determinística já existe** (`research/leadlag/bars.py`): M1→TF puro,
  reprodutível (R-12). É o **C1** do contrato de paridade, pronto.
- **Anti-overfit já existe** (`research/leadlag/validation.py`): DSR (Bailey/López de Prado),
  walk-forward splits, Benjamini-Hochberg/FDR, Hayashi-Yoshida. É o **guard-rail do otimizador**.
- **Backtester tick-a-tick já existe** (`backtest/simulator.py` + `walk_forward.py`) — porém
  **acoplado ao Risk Engine e à Constituição** (importa `_shared.risk`, provisiona IR 20%,
  cita Arts.). Precisa de um **modo MVP-sem-custo** desacoplado.
- **MT5 plumbing já existe** (`mt5_integration`: candles/ticks/book via ZeroMQ, `ea_dispatcher`,
  `multi_ea_manager`, `fill_subscriber`) + EAs `cam_bridge` (read-only) e `cam_risk_mirror`.
  **Falta o EA executor** (envia/modifica/fecha ordem no Strategy Tester/DEMO).

**Consequência:** o trabalho é majoritariamente **recomposição + 3 peças novas**
(otimizador, modo-sem-custo do backtester, EA executor), não construção greenfield.

---

## 2. Os três módulos detalhados

### 2.1 Assets Strategy — gestor de estratégias + otimizador que SUGERE

**O que é:** a tela onde o Founder **vê, gerencia e lista** estratégias, vê seus **parâmetros**,
e dispara o **otimizador de parâmetros**.

**In (MVP):**
- Lista de estratégias (reusa `StrategyRegistryPage` + `features/strategies`).
- Visualização e edição dos **parâmetros** de uma estratégia (ex.: janela do ORB, stop, alvo).
- **Otimizador de parâmetros** (peça nova, requisito explícito do Founder): dado uma estratégia
  + uma série temporal, varre o espaço de parâmetros e **SUGERE ao usuário** o melhor conjunto.
  - **Métodos MVP (Jim):** **grid search** (espaço pequeno, determinístico) e **random search**
    (espaço maior). Walk-forward como validação do candidato sugerido.
  - **Guard-rail anti-overfit obrigatório (Jim + Nassim):** todo conjunto sugerido passa por
    `validation.py` — **DSR penalizado pelo nº de combinações testadas** + **walk-forward OOS** +
    **checagem no-cliff** (a superfície ao redor do ótimo é chata, não um pico). O otimizador
    **nunca** entrega "o pico do backtest" sem reportar nº de tentativas e a robustez ao redor.
  - **O otimizador SUGERE, não aplica.** O Founder decide se adota o conjunto. (Sem auto-apply.)

**Out (MVP):** otimização multi-objetivo, algoritmos genéticos/bayesianos, otimização
distribuída. **Later.**

> **Nassim (lente, não dono):** o otimizador é a peça mais perigosa do SCOPE — é uma
> **fábrica de overfit** por construção. Quanto mais combinações ele testa, mais "edge" de
> ruído ele acha. A defesa não é opcional: DSR pelo nº real de tentativas + no-cliff + OOS.
> Um otimizador sem essas três travas é um gerador de falsa confiança com UI bonita.

### 2.2 Assets RunTests — backtest matemático Python + persistência + simulação

**O que é:** a tela de backtest. O Founder obtém dados do MT5 (já faz no Quant Lab), **persiste
em banco** os dados do papel/ticks/indicadores, e roda o **backtest matemático da estratégia em
Python** sobre a série temporal escolhida.

**In (MVP):**
- **Configurar e rodar** um backtest de uma estratégia sobre uma série (ativo + período + TF).
- **Motor de backtest matemático em Python** — modo **MVP-sem-custo**: simula **entrada, saída,
  gain, loss e volume financeiro** (P&L bruto em pontos × valor do ponto). **NÃO** aplica
  corretagem, emolumentos, slippage nem IR (decisão §3).
  - Reusa `backtest/simulator.py`, mas com um **modo desacoplado do Risk Engine** (o `simulator`
    atual importa `_shared.risk` e provisiona IR — isso precisa virar opcional/desligável).
  - Reusa `bars.py` (barra canônica) e `walk_forward.py`.
- **Persistência (requisito explícito do Founder):** os dados do papel (ou conjunto de papéis)
  da estratégia, ticks e indicadores derivados, persistidos em banco — para gerar os indicadores
  que o MT5 provê e rodar a estratégia matematicamente sem reextrair toda vez (ver §2.3 Ada).
- **Resultado visual:** curva de equity, lista de trades (entrada/saída/lado/qtd/P&L),
  drawdown, métricas (WR, expectância, profit factor, nº trades). Reusa padrão de UI do Quant Lab.
- **Walk-forward OOS** (reusa `validation.py`).

**Out (MVP):** custos, IR, fiscal, provisão. **Later.** Live forward em conta real: **OUT**.

### 2.3 Persistência (Ada) — papel/ticks/indicadores

> **Ada (dados):** decisão de persistência é estruturante e vai para o ARCH. Posição inicial:

- **Reusar `research_bars`/`research_ticks`** como **camada de ingestão canônica** (já têm
  provenance e barra determinística) **em vez de** criar `strategy_*` paralelas que dupliquem
  tick/candle. Provenance é inegociável mesmo no MVP: dado sem origem rastreável não entra.
- Criar **somente** o que é novo de domínio de estratégia: `strategy_param_set` (conjuntos de
  parâmetros, inclusive os sugeridos pelo otimizador), `backtest_run`/`backtest_trade`
  (já existem em `backtest/domain.py` — reusar), e cache de **indicadores derivados** se o
  recompute por run ficar caro (decisão de ARCH: materializar vs computar on-the-fly).
- **Pergunta de ARCH:** os indicadores ficam **materializados** (tabela) ou **computados sob
  demanda** a partir das barras canônicas? MVP tende a **on-the-fly** (mais simples, menos
  drift); materializar é otimização **Later**.

### 2.4 Assets Experts — gestão de robôs MT5 + EA executor

**O que é:** a gestão dos robôs MT5 — e, distinto do `cam_bridge` (read-only), um **EA executor**
que **envia/modifica/fecha ordem** no **Strategy Tester** e em **conta DEMO**.

**In (MVP):**
- Gestão/listagem dos robôs MT5 (reusa `robot-orchestrator` + `ea-control` + `multi_ea_manager`).
- **EA executor novo (Nikola):** EA MQL5 que **opera de fato** no Strategy Tester/DEMO —
  entrada, stop, alvo, saída — implementando a **mesma lógica** da estratégia Python
  correspondente (no MVP: D1 ORB-30).
- **Guard-rail de conta (Nikola):** o EA executor é **preso a conta DEMO** por configuração +
  checagem de tipo de conta no próprio EA. Live real só por ato explícito do Founder.

**Out (MVP):** EA executor para as 12 estratégias; multi-símbolo/2-pernas (D3/LS); live real.

> **Nikola (engenharia):** o `cam_bridge` é read-only por design (e o import-linter garante que
> `research` não importa execução). O EA executor **precisa** tocar execução — mas no MT5/MQL5,
> **não** no backend Python. O isolamento do backend **não quebra**: o executor vive no EA
> (`apps/cam-cockpit/mql5/experts/`), e o backend só **orquestra/observa** via `ea_dispatcher`/
> `fill_subscriber`. A fronteira de isolamento é mantida — só muda de lado (MQL5).

---

## 3. Decisão MVP-SEM-CUSTOS (registrar explicitamente)

> **Verbatim do Founder:** "NÃO considerar custos nem nada — é o MVP."

**Decisão registrada:**
1. O MVP simula **apenas lógica de negócio**: entrada, saída, gain, loss e **volume financeiro**.
2. **Fora do MVP:** corretagem, emolumentos, slippage, ISS, aluguel/short, **IR**. → **Later**.
3. **A paridade no MVP é de LÓGICA, não de fricção.** O critério de aprovação muda em relação ao
   EDGE-CONTRATO original: valem os itens de lógica do contrato (C1 barra, C2 fuso, C3 ordem de
   avaliação, C4 fill next-bar-open, C5 intrabar pior-caso, C6 gap, C9 sizing, C10 stop/alvo,
   C11 sessão, C12 determinismo, C13 mesmo dataset, C14 par/estado). **Saem do MVP:** C7 (custo)
   e C8 (IR).
4. **Implicação positiva (Jim):** o MVP fica **muito mais simples e mais fácil de bater
   paridade** — sem custo, a maior fonte de divergência Py↔EA (modelo de fricção, item mais
   sensível do contrato) **desaparece**. A paridade de lógica pura é alcançável com tolerância
   apertada (100% dos sinais coincidem, preço ≤ 1 tick).
5. **Ressalva honesta (Jim, registrada, não bloqueante):** backtest sem custo **infla** o edge.
   O Founder está ciente — isto é um MVP de **mecânica/paridade**, **não** uma prova de que a
   estratégia dá dinheiro. A pergunta "tem edge líquido?" só se responde quando custos entrarem
   (Later). Não confundir "paridade verde no MVP" com "estratégia aprovada".

---

## 4. Contrato de estratégia única (Python ↔ MQL5) — decisão arquitetural central

> Esta é a Q8 do SCOPE anterior e o coração do ARCH. **Codegen vs dupla implementação.**

### 4.1 Recomendação (Oscar): **definição única declarativa → codegen para os dois lados**
- **Fonte única da verdade:** a **DSL declarativa que JÁ EXISTE** (`strategies/dsl/`). Uma
  estratégia é descrita **uma vez** em YAML/JSON (`indicators/entry/exit/params`).
- **Python:** o `compiler.py` já transforma a DSL em `Strategy` executável. **Reuso direto.**
- **MQL5:** **gerar o `.mq5` a partir da mesma DSL** (codegen) — um template MQL5 parametrizado
  pela mesma AST. Assim, **uma mudança de lógica nasce nos dois lados por construção**, e a
  paridade deixa de depender de o humano manter duas implementações sincronizadas.

**Por que não dupla implementação:** duas implementações independentes (Python + MQL5 escritos à
mão) transformam **toda divergência em caça-bug manual** — exatamente o "experimento parecido,
falsa validação" que o EDGE-CONTRATO §5.5 alerta. Codegen mata o default não-declarado.

**Trade-off honesto (Oscar):** codegen MQL5 é **trabalho novo** e o gerador é, ele próprio, código
a validar. Para o MVP de **uma** estratégia (D1 ORB-30), é defensável começar com o `.mq5` da D1
**escrito à mão**, **mas derivado da mesma DSL** e validado pela paridade — e só investir no
**gerador** quando a 2ª/3ª estratégia provar o padrão. **Decisão fina = ARCH/ADR.**

> **Oscar:** a decisão estruturante (DSL como fonte única) deve fechar no ARCH **antes** do SPEC.
> O "à mão derivado da DSL" vs "codegen automático" é faseável — mas a **fonte única declarativa**
> não é negociável se a paridade importa.

### 4.2 Itens do contrato que o ARCH precisa fixar (subconjunto MVP de C1–C14)
Barra canônica (C1 — `bars.py` pronto), fuso B3 (C2), ordem de avaliação saída-antes-de-entrada
(C3), fill next-bar-open (C4), intrabar pior-caso (C5), gap honesto (C6), sizing determinístico
(C9), stop/alvo mecânicos (C10), sessão B3 (C11), determinismo/seed (C12), mesmo dataset (C13),
par/estado (C14). **C7/C8 (custo/IR) explicitamente adiados.**

---

## 5. Reaproveitamento (o que vem de onde)

| Peça do StrategyLab | Origem no código real | Ação |
|---|---|---|
| Contrato de estratégia declarativo | `strategies/dsl/{parser,compiler}.py` | **Reusar** como fonte única; estender p/ codegen MQL5 |
| Estratégia-exemplo | `strategies/strategies/orb_60m_win.py` | **Adaptar** p/ D1 ORB-30 (hoje é ORB-60) |
| Barra canônica (C1) | `research/leadlag/bars.py` | **Reusar** direto (M1→TF determinístico) |
| Anti-overfit do otimizador | `research/leadlag/validation.py` (DSR, WF, FDR) | **Reusar** como guard-rail do otimizador |
| Motor de backtest | `backtest/simulator.py` + `walk_forward.py` | **Reusar com modo MVP-sem-custo** (desacoplar Risk/IR) |
| Persistência tick/candle | `research_bars`/`research_ticks` + provenance | **Reusar** como ingestão canônica |
| Run/trade de backtest | `backtest/domain.py` (`BacktestRun`/`BacktestTrade`) | **Reusar** schema |
| MT5 plumbing | `mt5_integration/{ea_dispatcher,multi_ea_manager,fill_subscriber}` | **Reusar** p/ orquestrar EA executor |
| EAs base | `mql5/experts/{cam_bridge,cam_risk_mirror}.mq5` | **Referência**; EA executor é **novo** |
| Padrão de UI | `features/quant-lab`, `features/inspetor` (SVG charts, react-query, MUI) | **Reusar** padrão p/ as 3 telas |

---

## 6. IN / OUT / LATER

### IN (MVP)
- **Assets Strategy:** lista/gestão de estratégias + visualização/edição de parâmetros +
  **otimizador (grid/random + walk-forward) que SUGERE** com guard-rail anti-overfit.
- **Assets RunTests:** backtest matemático Python **sem custo** (entrada/saída/gain/loss/volume)
  + persistência de papel/ticks/indicadores + equity/trades/drawdown/métricas + walk-forward.
- **Assets Experts:** gestão de robôs MT5 + **EA executor** (envia ordem no Strategy Tester/DEMO),
  preso a DEMO.
- **Contrato de estratégia única declarativo** (DSL) como fonte da verdade Py↔MQL5.
- **Paridade de LÓGICA** Py↔EA (subconjunto C1–C14 sem C7/C8) + relatório PASS/FAIL.
- **Vertical slice:** **D1 ORB-30 fim-a-fim** nos três módulos antes de escalar.

### OUT (este ciclo)
- ❌ **Live trading em conta REAL** — só por ato explícito do Founder.
- ❌ **Assets RiskManager / kill switch / journal / fiscal** — outro módulo, fora deste SCOPE.
- ❌ **Multi-símbolo / 2 pernas no EA** (D3 spread, LS pair) — Strategy Tester é single-symbol;
  fica Python-only ou Later.
- ❌ **Broker Profit / outros** — MT5 fixado neste ciclo.

### LATER
- ⏳ **Custos, slippage, IR, fiscal** (C7/C8) — entram **depois** do MVP; aí a paridade vira
  "de fricção" e o backtest passa a responder "tem edge líquido?".
- ⏳ **Codegen MQL5 automático** — quando a 2ª/3ª estratégia justificar o gerador.
- ⏳ **Escalar para as 12 estratégias** — só após D1 fim-a-fim aprovada.
- ⏳ **F1 (FII) e H1 (dividendos)** — buy&hold, sem EA de Strategy Tester; módulo total-return
  separado, Later.
- ⏳ **Otimização avançada** (bayesiana/genética/multi-objetivo).
- ⏳ **Live forward / bridge ZeroMQ ao vivo para execução real.**

---

## 7. Dependências técnicas e blocos por ambiente (alto nível — fino no PLAN)

| Bloco | Ambiente | Conteúdo (alto nível) | Depende de |
|---|---|---|---|
| **BL-DADOS** | DB / Python | Persistência papel/ticks/indicadores; reuso `research_*` + provenance | — (base existe) |
| **BL-CONTRATO** | Python | DSL como fonte única; D1 ORB-30 na DSL; subset C1–C14 sem custo | BL-DADOS |
| **BL-BACKTEST** | Python | Modo MVP-sem-custo do `simulator` (desacoplar Risk/IR); equity/trades/métricas | BL-CONTRATO |
| **BL-OTIM** | Python | Otimizador grid/random + guard-rail `validation.py` (DSR/WF/no-cliff) | BL-BACKTEST |
| **BL-EA** | MQL5 / MT5 | EA executor D1 derivado da DSL; guard-rail conta DEMO | BL-CONTRATO |
| **BL-PARIDADE** | Python | Comparador trade-a-trade Py↔EA (lógica) + relatório PASS/FAIL | BL-BACKTEST, BL-EA |
| **BL-FRONT** | React | 3 telas: Strategy (lista+params+otimizador), RunTests (config+equity+trades), Experts (robôs+EA) | BL-OTIM, BL-PARIDADE |

> Decomposição fina em TASKs é do **PLAN** (Nico). Aqui só a topologia e as dependências.

---

## 8. Riscos

| Risco | Tipo | Descrição | Mitigação |
|---|---|---|---|
| **Overfit do otimizador** | Confiança | Otimizador vira fábrica de ruído com UI bonita | DSR pelo nº de tentativas + walk-forward OOS + no-cliff **obrigatórios** (Jim/Nassim). Sugere, não aplica |
| **Falsa confiança do "sem custo"** | Desejabilidade | Paridade verde + equity bonita lidos como "estratégia aprovada" | Registrar §3.5: MVP prova **mecânica/paridade**, não edge líquido. "Tem edge?" = Later |
| **Divergência silenciosa Py↔EA** | Factibilidade | Duas lógicas sutilmente diferentes | DSL fonte única + paridade trade-a-trade como gate (100% sinais, ≤1 tick) |
| **Acoplamento do backtester ao Risk/Constituição** | Factibilidade | `simulator.py` importa `_shared.risk` e provisiona IR | Modo MVP-sem-custo desacoplado; não tocar o caminho Risk existente |
| **EA executor x isolamento** | Arquitetura | Execução não pode contaminar o backend research-only | Execução vive no MQL5; backend só orquestra via dispatcher (import-linter intacto) |
| **Salto não-intencional p/ conta real** | Operacional | EA executor apontado p/ real por engano | Preso a DEMO por config + checagem de tipo de conta no EA |
| **Feature factory (3 módulos + otimizador + EA de uma vez)** | Valor | Muito código, pouco aprendizado, 12 estratégias antes de 1 funcionar | **D1 ORB-30 fim-a-fim** como gate antes de escalar (Marty/Voltaire) |
| **Multi-símbolo no Strategy Tester** | Factibilidade | D3/LS (2 pernas) não rodam single-symbol | Rebaixar p/ Python-only ou Later; D1 é single-symbol (não afeta MVP) |

---

## 9. Perguntas abertas ao Founder (Q1–Q9 atualizadas à luz do MVP-sem-custo)

- [ ] **Q1 — Fonte de verdade de dados:** o dataset canônico para os dois lados é sempre o
  tick/candle exportado do MT5 e persistido em `research_*`? (Paridade exige fonte única.)
- [ ] **Q2 — Granularidade da paridade no MVP:** trade-a-trade (100% sinais, ≤1 tick) é o alvo,
  certo? Métrica-a-métrica como rede de segurança? (Sem custo, trade-a-trade fica viável.)
- [ ] **Q3 — ~~Tolerância de custo~~ → tolerância de lógica:** com C7/C8 fora, a tolerância de
  preço é ≤1 tick (arredondamento) e sinais 100% coincidentes. Confirma esse alvo apertado?
- [ ] **Q4 — Persistência de indicadores:** materializar indicadores em tabela ou computar
  on-the-fly das barras canônicas no MVP? (Recomendação Ada: on-the-fly; materializar = Later.)
- [ ] **Q5 — Universo de ativos do MVP:** D1 ORB-30 é WIN (derivativo single-symbol). Confirma
  começar **só por WIN/D1**, deixando à vista (V/S/LS) p/ depois?
- [ ] **Q6 — ~~Custos idênticos~~ → adiada:** custo/IR estão **fora do MVP** por sua decisão.
  Confirmado que C7/C8 viram Later e a paridade do MVP é só de lógica?
- [ ] **Q7 — Convenção de barra/fuso:** confirmar barra canônica de `bars.py` (M1→TF) + fuso
  America/Sao_Paulo como regra única Py↔EA (sem default do broker/MT5).
- [ ] **Q8 — Estratégia única (a decisão de ARCH):** adota **DSL declarativa como fonte única**
  (Oscar recomenda)? E no MVP: D1 `.mq5` **à mão derivado da DSL** agora, **codegen automático**
  Later — ou já quer o gerador desde o início?
- [ ] **Q9 — Otimizador no MVP:** grid + random + walk-forward é suficiente para o MVP, ou você
  quer um método específico? E confirma que o otimizador **sugere** (não aplica) o conjunto?

> **Nova — Q10 (Voltaire):** o MVP deveria ser **ainda menor**? Ver §11.

---

## 10. Classificação P/M/G e próxima fase

**Classificação: G (Grande).**

Justificativa (tamanho/decomposição, **sem** modificadores de risco/segurança — proibidos):
- São **três módulos de produto** + **três peças novas** (otimizador, modo-sem-custo do
  backtester, EA executor) + **camada de paridade**, atravessando **três ambientes**
  (Python/FastAPI, React, MQL5/MT5) que precisam concordar numericamente.
- Exige **decomposição em TASKs** no PLAN (ver blocos §7).
- Tem **decisão arquitetural aberta** estruturante (DSL fonte única + codegen — Q8).

> **Atenuante real:** o MVP-sem-custo e o **alto reuso** (DSL, bars, validation, simulator,
> mt5_integration já existem) **reduzem** o G face ao SCOPE-PARITY anterior — a maior fonte de
> dificuldade (paridade de fricção) saiu. Continua **G** pela largura (3 ambientes), não pela
> profundidade. Nico pode contestar no PLAN (loop P/M/G).

**Próxima fase recomendada: ARCH (Oscar) — enxuto, focado em 2 ADRs.**
1. **ADR — Contrato de estratégia única:** DSL declarativa como fonte da verdade; codegen MQL5
   vs `.mq5` à mão derivado da DSL no MVP (faseado).
2. **ADR — Persistência + modo MVP-sem-custo do backtester:** reuso `research_*` vs `strategy_*`;
   desacoplamento do `simulator` em relação a Risk Engine/IR; indicadores materializados vs
   on-the-fly.

Demais itens (paridade trade-a-trade, tolerância) podem ir direto ao SPEC após esses 2 ADRs.

- [x] **Avançar para ARCH** (2 ADRs enxutos) → depois SPEC (Albert) → PLAN (Nico)
- [ ] Incubar · [ ] Descartar · [ ] Investigar mais

**Quem decide:** Founder · **Quando:** _(pendente)_

---

## 11. A pergunta dura (Voltaire ⚔️)

> Voltaire não questiona a stack (território da Grace) — questiona a **direção**.

**Três inversões antes de o Founder aprovar:**

1. **"Três módulos de produto" ou "uma vertical slice com três telas"?** Você não está
   construindo Assets Strategy, RunTests e Experts. Está construindo **D1 ORB-30 atravessando
   três telas**. Se isso é verdade — e o SCOPE diz que é — por que o título sugere três produtos?
   O risco de nomear "três módulos" é o Founder (você) cobrar três módulos **prontos** quando o
   gate honesto é **uma estratégia que atravessa os três**. **Inversão:** e se o MVP se chamasse
   "D1 fim-a-fim" e os "módulos" fossem só o **arranjo de telas** dela?

2. **O otimizador pertence ao MVP — ou é a peça que você quer porque é a mais divertida?**
   O otimizador é a peça **mais arriscada** (fábrica de overfit) e a **menos necessária** para
   provar paridade Py↔EA. A paridade — o objetivo-mãe — **não precisa** do otimizador para ser
   provada. **Inversão:** e se o otimizador fosse a **segunda** entrega, depois de D1 já bater
   paridade com parâmetros fixos? Você provaria a mecânica antes de adicionar a peça que mais
   mente.

3. **"Sem custo" simplifica o MVP — ou esconde a única pergunta que importa?** Tirar custo torna
   a paridade fácil e a equity bonita. Mas a pergunta que decide se TCaM é produto ou brinquedo é
   **"sobra dinheiro depois do custo?"** — e essa você adiou. **Inversão:** está construindo a
   parte fácil primeiro porque é a certa de fazer, ou porque é a confortável? (Resposta defensável:
   provar **mecânica/paridade** antes de **edge líquido** é ordem de engenharia correta — desde
   que ninguém confunda "paridade verde" com "estratégia que ganha". O SCOPE §3.5 já crava isso.
   Mantenha essa linha visível, ou o MVP vira teatro.)

> **Voltaire encerra:** aprovar este SCOPE é defensável. Mas aprove sabendo que você está
> comprando **mecânica + paridade de uma estratégia**, não um cassino que dá lucro. A hora de
> dizer "não considerar custos" é agora; a hora de pagar essa conta é quando custos entrarem.
> A pergunta que fica: **o que você faz no dia em que D1 bate paridade perfeita e, com custo,
> não sobra nada?**

---

## 12. Referências

- Catálogo 12 estratégias: [`./CATALOGO-12-ESTRATEGIAS-ELEITAS.md`](./CATALOGO-12-ESTRATEGIAS-ELEITAS.md)
- Contrato edge/paridade (Jim): [`./EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md`](./EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md)
- SCOPE anterior (insumo, superseded-parcial): [`./SCOPE-STRATLAB-PARITY-001.md`](./SCOPE-STRATLAB-PARITY-001.md)
- Mapa dos módulos Assets*: [`../../MAP-MODULES-TCaM.md`](../../MAP-MODULES-TCaM.md)
- Pivot p/ produto: [`../../PIVOT-TCaM-STRATEGY.md`](../../PIVOT-TCaM-STRATEGY.md) · [`../../CONSTITUTION-DECOMMISSION.md`](../../CONSTITUTION-DECOMMISSION.md)
- Código real reaproveitável: `apps/cam-cockpit/backend/cam/features/{strategies/dsl, backtest, research/leadlag, mt5_integration}` · `apps/cam-cockpit/mql5/experts/`

---

> **Modo:** TCaM / produto · Constituição descomissionada · MVP sem custos · rigor de engenharia
> mantido · personas consultadas: Marty (escopo), Oscar (arch), Jim (quant), Nassim (lente risco),
> Ada (dados), Nikola (eng), Don/Peter (UX implícito nas 3 telas), Voltaire (challenger).
> **Leo consolida. O Founder decide.** · 2026-06-03 · v0.6

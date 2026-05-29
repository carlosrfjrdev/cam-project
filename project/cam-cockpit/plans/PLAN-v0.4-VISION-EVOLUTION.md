---
template: PLAN
phase: PLAN
status: Approved
version: 0.4
date: 2026-05-27
approved_by_founder_at: 2026-05-27
spec_ref: ../specs/SPEC-v0.4-VISION-EVOLUTION.MD
scope_ref: ../scopes/SCOPE-Vision-Evolution.md
constitution_ref: ../../../CONSTITUICAO.md
demand_id: PLAN-v0.4-VISION-EVOLUTION
pmg: G
sec: true
qa_sec: true
letscode: true
bl_a_status: COMPLETED (2026-05-27 — autônomo)
autonomous_session_2026_05_28: COMPLETED
total_tasks_completed: 55 / 62
total_tasks_deferred_techdebt: 7 / 62
total_tests_green: 710
---

# PLAN v0.4 — Vision Evolution (indexador)

> **Lead:** Nico · **Co-lead:** Albert (loop P/M/G) · **Aprovador:** Founder
> **Skill:** `teczi-code-planning`
> **Princípio:** *PLAN agêntico DevFlow* — sem Épicos / Feature Groups / Stories. **TASKs numeradas flat (001..062)**.
> **TDD First por TASK** — Red → Green → Refactor; os testes são o modelo mental da TASK (Nikola escreve testes antes de codar).

---

## 1. Resumo do plano

Implementar a SPEC v0.4-VISION-EVOLUTION em **62 TASKs flat numeradas**, agrupadas por bloco (BL-A..BL-I) e executadas em **5 janelas paralelas** com gate Founder intermediário entre janelas. Cada TASK carrega testes-primeiro, marcadores `sec`/`qa-sec` herdados do bloco e referência cruzada à(s) regra(s) R-X.YY + critério(s) CA-X.Y da SPEC.

---

## 2. Referências de entrada

| Artefato | Versão | Status |
|---|---|---|
| [`SPEC-v0.4-VISION-EVOLUTION.MD`](../specs/SPEC-v0.4-VISION-EVOLUTION.MD) | v0.4 | Aprovada pelo Founder em 2026-05-27 |
| [`SCOPE-Vision-Evolution.md`](../scopes/SCOPE-Vision-Evolution.md) | v1.1 | Vigente |
| [`CAM-VISION-FINAL.MD`](../CAM-VISION-FINAL.MD) | v1.1 | Vigente |
| [`DAS.md`](../DAS.md) | atual | Vigente |
| [`CONSTITUICAO.md`](../../../CONSTITUICAO.md) | v1.1 (pós EMENDA-001 v2) | Vigente |
| [`POV-VIGENTE-v1.0.md`](../../POV-VIGENTE-v1.0.md) | v1.1 | Vigente |
| [`MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../../MAPPING-CONSTITUICAO-RISK-ENGINE.md) | atual | Vigente |
| [`FEATURE-FLAGS-LEDGER.md`](../../../apps/cam-cockpit/FEATURE-FLAGS-LEDGER.md) | atual | Vigente |
| ADRs vigentes | 001..013 | Vigentes (especial atenção a ADR-013 vertical-slice + shared-kernel) |

---

## 3. Avaliação de P/M/G (Loop Albert ↔ Nico)

### 3.1 Classe global da SPEC

| Campo | Valor |
|---|---|
| Classe atribuída por Albert (SPEC §15) | **G** |
| Concordância de Nico | **Sim** |
| Re-classificação proposta | — (G mantém) |
| Loop com Albert | concluído sem disputa — 9 blocos · 30 features · 7 trilhas com `sec`/`qa-sec` justificam G |
| Decisão final | **G confirmado** |

### 3.2 Classe por bloco

| Bloco | Albert | Nico | Justificativa de Nico |
|---|---|---|---|
| BL-A | G | **G** | Toca Order Gateway + Risk Engine + EA Control Plane — 8 features + lint MQL5 |
| BL-B | M | **M** | Schema + ingestão + dedup — sem alterar contratos sensíveis |
| BL-C | G | **G** | Paper loop end-to-end com kill switch — encadeia BL-A + BL-B + IA real |
| BL-D | M | **M** | CRUD holdings + importação CSV — sem caminho de ordem |
| BL-E | **G** | **G CRÍTICO** | 1º envio de ordem (mesmo em DEMO) — paridade Python↔MQL5 em 100+ cenários |
| BL-F | G | **G** | 7 indicadores + policy engine + scraping (TD-v0.4-01) |
| BL-G | G | **G** | Pair trade + Workbench + governança remoto AI |
| BL-H1 | G | **G CRÍTICO** | Multiestratégia (Art. 11-A) — property-based testing obrigatório |
| BL-H2 | G | **G CRÍTICO** | Escalonamento condicional (Art. 11-B) — toca limite constitucional |
| BL-I | G | **G** | Multi-EA + DSL — exige BL-E e BL-H1/H2 estáveis |

> **Sem disputa P/M/G.** Loop Albert↔Nico fechado em 1 rodada. Decisão final: classificação da SPEC mantida integralmente.

---

## 4. Princípios operacionais do PLAN

1. **TASKs flat 001..062** — sem hierarquia Épico/FG/Story.
2. **TDD First por TASK** — todo arquivo TASK lista **testes a escrever ANTES do código**; CODE só inicia o ciclo Green depois que Red está vermelho intencionalmente.
3. **Reuso antes de criação** — TASKs explicitam quando reusam Risk Engine vigente, repositórios SQLAlchemy existentes, importer base v0.2.
4. **Pré-requisitos explícitos** — toda TASK declara TASKs predecessoras; o orquestrador da janela respeita.
5. **Estado real vence intenção** — se durante a execução o código divergir da SPEC, abrir DRIFT (sob solicitação Founder) ou voltar à SPEC; nunca silenciar.
6. **Founder-only nos gates** — fim de janela e `letscode` do PLAN são gates Founder.
7. **Sem estimativas em horas/dias/semanas** — proibição absoluta.
8. **Marcadores herdados** — TASK herda `sec`/`qa-sec` do bloco; pode adicionar, nunca remover.
9. **Constituição vence sempre** — TASK que viola Art. 11/15/18/25/35 é inválida (Linus + Kevin barram em CODE/QA).
10. **Lint anti-auto-edição** — TASKs do BL-H1 incluem lint que falha CI se PR tentar alterar `MAX_WIN_CONTRACTS` ou correlatos (recomendação Leo na emenda v2).

---

## 5. Estrutura física do PLAN

```
project/cam-cockpit/plans/
├── PLAN-v0.4-VISION-EVOLUTION.md     ← este indexador
└── v0.4-tasks/
    ├── TASK-001-strategies-domain.md
    ├── TASK-002-strategies-registry.md
    ├── ...
    └── TASK-062-instrument-catalog-amplo.md
```

> Cada arquivo TASK é **autocontido** (Nikola pode pegar e executar). Cabeçalho aponta de volta para esta PLAN.

---

## 6. Mapa de execução — 5 Janelas + Gates

> Janelas são **conjuntos de TASKs executáveis em paralelo** dentro do mesmo bloco e/ou entre blocos sem dependência. Cada janela termina com **Gate Founder** antes da próxima abrir.

### Janela 1 — Fundações paralelas (BL-A + BL-B + BL-D)

```
BL-A: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010
BL-B: T011 → T012 → T013 → T014
BL-D: T020 → T021 → T022 → T023 → T024
```

Pré-requisitos cruzados:
- T008 (backtest P&L real) precisa de T007 + T012 (tick histórico ingerido).
- T014 (Genial importer) precisa de T012 + T020.
- T022 (BL-D usando Genial importer) precisa de T014.

**Gate Janela 1 → Janela 2:** Founder valida CAs `CA-A.1..CA-A.8`, `CA-B.1..CA-B.4`, `CA-D.1..CA-D.4`.

### Janela 2 — Paper Loop + Wealth Foundations (BL-C + BL-F)

```
BL-C: T015 → T016 → T017 → T018 → T019
BL-F: T031 → T032 → T033 → T034
```

Pré-requisitos cruzados:
- T016 (paper loop_governed) precisa de T006 (Order Gateway) + T007 (S1) + T012 (ticks) + T015 (cam_paper_trades).
- T031 (dividendos) precisa de T020 (holdings).
- T033 (policy engine) precisa de T032 (fundamentals).

**Gate Janela 2 → Janela 3:** Founder valida `CA-C.1..CA-C.5`, `CA-F.1..CA-F.4`, S1 paper rolando há ≥ 30 dias com aderência ≥ 95% (gate de entrada do BL-E).

### Janela 3 — Read-write DEMO + Research (BL-E + BL-G)

```
BL-E: T025 → T026 → T027 → T028 → T029 → T030
BL-G: T035 → T036 → T037 → T038 → T039 → T040 → T041
```

> **Janela 3 é CRÍTICA — primeiro envio de ordem (mesmo DEMO).** Linus + Kevin obrigatórios em todas as TASKs da BL-E. Paridade Python↔MQL5 (T025+T026) é precondição absoluta para T027.

**Gate Janela 3 → Janela 4:** Founder valida `CA-E.1..CA-E.6`, `CA-G.1..CA-G.5`. Kill switch via cockpit em < 2s testado E2E.

### Janela 4 — Multiestratégia + Escalonamento (BL-H1 + BL-H2)

```
BL-H1: T042 → T043 → T044 → T045 → T046 → T047 → T048 → T049
BL-H2: T050 → T051 → T052 → T053 → T054 → T055 → T056 → T057
```

Pré-requisitos cruzados:
- T050 (scaling.py) precisa de T045 (aggregate.py) — escalonamento lê limite vigente sobre a base agregada.
- T047 (`max_contracts_check` → `get_current_limits()`) é compartilhada — entra em BL-H1 mas valida CAs de BL-H2 também (`CA-H2.8`).
- Property-based testing (T044) precisa rodar com 10.000+ cenários Hypothesis antes de habilitar `MULTI_STRATEGY_ENABLED`.

**Gate Janela 4 → Janela 5:** Founder valida `CA-H1.1..CA-H1.9`, `CA-H2.1..CA-H2.9`. Flag `MULTI_STRATEGY_ENABLED` continua `false` até gate manual; flag `SCALING_ENABLED` continua `false` até 1ª aprovação em `/escalonamentos/`.

### Janela 5 — Multi-EA + DSL (BL-I)

```
BL-I: T058 → T059 → T060 → T061 → T062
```

Pré-requisitos cruzados:
- T058 (`cam_bridge.mq5` v2.0 multi-instance) precisa de T009 (bridge G2) + T030 (kill switch).
- T060/T061 (DSL) precisa de T001 (contrato Strategy).

**Gate Janela 5 → SPEC concluída:** Founder valida `CA-I.1..CA-I.4`. SDOC sob solicitação (Q11).

---

## 7. Catálogo flat das 62 TASKs

> Lista ordenada por número. Cada linha é um link para o arquivo TASK próprio.

### BL-A — Strategy Lifecycle + Autonomy Matrix + EA Control Plane Base

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 001 | [Strategy Protocol + StrategyMetadata + StrategyStatus](./v0.4-tasks/TASK-001-strategies-domain.md) | R1.01 · CA-A.1 | — |
| 002 | [StrategyRegistry + constraint N-registered/1-active](./v0.4-tasks/TASK-002-strategies-registry.md) | R1.01 · CA-A.1, CA-C.4 | T001 |
| 003 | [Promotion + EvidencePack](./v0.4-tasks/TASK-003-strategies-promotion.md) | R1.02, R1.03 · CA-A.2 | T002 |
| 004 | [Autonomy Matrix `is_mode_allowed`](./v0.4-tasks/TASK-004-autonomy-matrix.md) | R1.04 · CA-A.4 | T001 |
| 005 | [`REAL_TRADING_ALLOWED=false` + allowlist](./v0.4-tasks/TASK-005-real-trading-flag.md) | R1.06 · CA-A.8 | — |
| 006 | [Order Gateway único (`submit`)](./v0.4-tasks/TASK-006-order-gateway.md) | R1.07 · CA-A.7, CA-A.8 | T002, T004, T005 |
| 007 | [S1 ORB 60m WIN — implementação concreta](./v0.4-tasks/TASK-007-s1-orb-60m-win.md) | R1.01 · CA-A.1, CA-A.3 | T001 |
| 008 | [Backtest P&L real por tick scanning](./v0.4-tasks/TASK-008-backtest-pnl-real.md) | R1.09, R1.10 · CA-A.3 | T007, T012 |
| 009 | [`cam_bridge.mq5` PAUSE_EA/RESUME_EA/GET_VERSION](./v0.4-tasks/TASK-009-bridge-control-plane-g2.md) | R1.05 · CA-A.5 | — |
| 010 | [`scripts/lint_mql5.sh`](./v0.4-tasks/TASK-010-lint-mql5.md) | R1.08 · CA-A.6 | T009 |

### BL-B — Market Data Provenance + Tick Histórico

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 011 | [Migration `cam_market_data_provenance` + `cam_instruments`](./v0.4-tasks/TASK-011-market-data-schemas.md) | R2.01, R2.05 · CA-B.1, CA-B.4 | — |
| 012 | [`market_data.service.ingest_ticks` + dedup hash](./v0.4-tasks/TASK-012-ingest-ticks.md) | R2.02, R2.03 · CA-B.1, CA-B.2 | T011 |
| 013 | [Quality flags computation](./v0.4-tasks/TASK-013-quality-flags.md) | R2.04 · CA-B.3 | T012 |
| 014 | [Importer Genial CSV extrato (base)](./v0.4-tasks/TASK-014-genial-importer-base.md) | R2.06 · CA-B.1 | T012 |

### BL-C — Paper Loop Governado + AI Real

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 015 | [Migration `cam_paper_trades`](./v0.4-tasks/TASK-015-paper-trades-schema.md) | R3.02 · CA-C.1 | — |
| 016 | [`paper_trading.service.loop_governed`](./v0.4-tasks/TASK-016-paper-loop-governed.md) | R3.01, R3.03 · CA-C.1 | T006, T007, T012, T015 |
| 017 | [Kill switch loop paper < 1s](./v0.4-tasks/TASK-017-paper-kill-switch.md) | — · CA-C.2 | T016 |
| 018 | [`AIAnalystDataCollector` consumindo dados reais](./v0.4-tasks/TASK-018-ai-collector-real.md) | R3.04 · CA-C.3 | — |
| 019 | [Promoção `paper_ok` (≥ 100 trades + aderência ≥ 95%)](./v0.4-tasks/TASK-019-promotion-paper-ok.md) | R3.05 · CA-C.5 | T003, T016 |

### BL-D — Carteira Hard Holdings + Importação Genial

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 020 | [Migration `cam_carteira_hard_holdings`](./v0.4-tasks/TASK-020-holdings-schema.md) | R4.01 · CA-D.1 | — |
| 021 | [`POST /api/v1/carteira-hard/holdings`](./v0.4-tasks/TASK-021-holdings-endpoint.md) | R4.02 · CA-D.1 | T020 |
| 022 | [Integração Genial Importer → Holdings](./v0.4-tasks/TASK-022-genial-importer-holdings.md) | R4.03 · CA-D.2, CA-D.3 | T014, T020 |
| 023 | [Assert risco rejeita não-derivativo](./v0.4-tasks/TASK-023-risk-rejects-non-derivative.md) | R4.04 · CA-D.4 | T020 |
| 024 | [UI `/carteira-hard` (listagem)](./v0.4-tasks/TASK-024-carteira-hard-ui.md) | R4.05 · CA-D.1 | T021 |

### BL-E — Read-write MT5 DEMO + `cam_risk_mirror.mq5`

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 025 | [`cam_risk_mirror.mq5` — 18 validators em MQL5](./v0.4-tasks/TASK-025-risk-mirror-mql5.md) | R5.02 · CA-E.4 | — (Risk Engine Python já estável) |
| 026 | [`tests/test_risk_mirror_parity.py` — 100+ cenários canônicos](./v0.4-tasks/TASK-026-risk-mirror-parity-tests.md) | R5.02 · CA-E.4 | T025 |
| 027 | [`cam_bridge.mq5` `SUBMIT_ORDER` (DEMO + idempotency)](./v0.4-tasks/TASK-027-bridge-submit-order.md) | R5.01 · CA-E.2, CA-E.3 | T009, T025 |
| 028 | [Order Gateway via REQ/REP `SUBMIT_ORDER` (timeout 2s)](./v0.4-tasks/TASK-028-gateway-submit-order.md) | R5.03 · CA-E.2 | T006, T027 |
| 029 | [`mt5.fill` → `JournalEntry` automático](./v0.4-tasks/TASK-029-fill-to-journal.md) | R5.04 · CA-E.6 | T027 |
| 030 | [`KILL_SWITCH_ACTIVATE` propagation E2E](./v0.4-tasks/TASK-030-kill-switch-e2e.md) | R5.05 · CA-E.5 | T027 |

### BL-F — Dividendos + Fundamentalistas + Policy Engine

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 031 | [Migrations `cam_dividends_calendar` + `cam_dividends_received`](./v0.4-tasks/TASK-031-dividends-schemas.md) | R6.01, R6.02 · CA-F.1 | T020 |
| 032 | [Migration `cam_fundamentals_snapshot` (7 indicadores R-20)](./v0.4-tasks/TASK-032-fundamentals-schema.md) | R6.03, G-R03.03 · CA-F.2 | — |
| 033 | [Policy Engine — alertas (DY, P/L, Dívida/EBITDA)](./v0.4-tasks/TASK-033-policy-engine.md) | R6.04 · CA-F.3, CA-F.4 | T032 |
| 034 | [Multi-Source Collector — esqueleto + 1 fonte placeholder](./v0.4-tasks/TASK-034-fundamentals-collector.md) | R6.05 · CA-F.2 | T032 |

### BL-G — Cross-Asset Research + Pair Trade + AI Workbench

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 035 | [Canal `mt5.book` + populador](./v0.4-tasks/TASK-035-book-channel.md) | R7.01 · CA-G.1 | T009 |
| 036 | [`research/pair_trade_backtest.py`](./v0.4-tasks/TASK-036-pair-trade-backtest.md) | R7.02 · CA-G.2 | T012, T035 |
| 037 | [`research/cross_asset_correlation.py`](./v0.4-tasks/TASK-037-cross-asset-correlation.md) | R7.02 · CA-G.2 | T012 |
| 038 | [`research/pattern_lab.py`](./v0.4-tasks/TASK-038-pattern-lab.md) | R7.02 · — | T037 |
| 039 | [`ai_analyst/research_workbench.py` + Recharts UI](./v0.4-tasks/TASK-039-ai-research-workbench.md) | R7.03 · CA-G.3 | T018, T037 |
| 040 | [`ledger/rebalance.py` (sugestão, nunca executa)](./v0.4-tasks/TASK-040-rebalance-suggestion.md) | R7.04 · CA-G.4 | T033 |
| 041 | [`cam_ai_provider_calls` + OpenAI bloqueado](./v0.4-tasks/TASK-041-ai-provider-governance.md) | R7.05 · CA-G.5 | T018 |

### BL-H1 — Robot Orchestrator + Multiestratégia (Art. 11-A)

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 042 | [`robot_orchestrator/domain.py` — `Robot`](./v0.4-tasks/TASK-042-robot-domain.md) | R8.01 · CA-H1.1 | T002 |
| 043 | [`robot_orchestrator/orchestrator.py`](./v0.4-tasks/TASK-043-robot-orchestrator.md) | R8.01 · CA-H1.1 | T006, T042 |
| 044 | [`conflict_resolver.py` (POV §3.11) + property-based testing](./v0.4-tasks/TASK-044-conflict-resolver.md) | R8.01 · CA-H1.2, CA-H1.3, CA-H1.4 | T043 |
| 045 | [`_shared/risk/aggregate.py` (Art. 11-A)](./v0.4-tasks/TASK-045-aggregate-risk.md) | R8.02 · CA-H1.1, CA-H1.5, CA-H1.6 | T043 |
| 046 | [Flag `MULTI_STRATEGY_ENABLED` + ativação rastreada](./v0.4-tasks/TASK-046-multi-strategy-flag.md) | R8.03 · CA-H1.1 | T042 |
| 047 | [Refactor `max_contracts_check` → `get_current_limits()` + lint anti auto-edição](./v0.4-tasks/TASK-047-current-limits-refactor.md) | R8.04 · CA-H1.7, CA-H2.8 | T045 |
| 048 | [Gain lock individual por estratégia (POV §3.13)](./v0.4-tasks/TASK-048-gain-lock-individual.md) | R8.05 · CA-H1.8 | T043 |
| 049 | [UI Risk Console — aderência individual + agregada](./v0.4-tasks/TASK-049-risk-console-adherence.md) | R8.06 · CA-H1.5 | T043 |

### BL-H2 — Strategy Escalation Engine (Art. 11-B)

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 050 | [`_shared/risk/scaling.py` — `compute_scaling_eligibility`](./v0.4-tasks/TASK-050-scaling-eligibility.md) | R8.10 · CA-H2.1, CA-H2.2 | T045 |
| 051 | [Job APScheduler pós-pregão + evento `ScalingEligibilityReady`](./v0.4-tasks/TASK-051-scaling-job.md) | R8.11 · CA-H2.1 | T050 |
| 052 | [Migration `cam_constitutional_scaling_events`](./v0.4-tasks/TASK-052-scaling-events-schema.md) | R8.16 · CA-H2.5 | T050 |
| 053 | [Endpoint `POST /scaling/revoke/{esc_id}` + cooldown 7/21 dias](./v0.4-tasks/TASK-053-scaling-revoke.md) | R8.13 · CA-H2.4 | T050, T052 |
| 054 | [Reversão automática + DD em dobro + soft kill switch](./v0.4-tasks/TASK-054-scaling-auto-revert.md) | R8.14 · CA-H2.5, CA-H2.6 | T050, T052 |
| 055 | [Tetos absolutos + cláusula de blindagem](./v0.4-tasks/TASK-055-scaling-ceilings.md) | R8.15 · CA-H2.7 | T050 |
| 056 | [Flag `SCALING_ENABLED` + workflow `/escalonamentos/`](./v0.4-tasks/TASK-056-scaling-flag-workflow.md) | R8.17, R8.12 · CA-H2.3 | T050 |
| 057 | [UI Risk Console — histograma tentativas-bloqueadas + incremento +1 strict](./v0.4-tasks/TASK-057-scaling-ui-histogram.md) | R8.18, R8.12 · CA-H2.3, CA-H2.9 | T050, T053 |

### BL-I — Multi-EA + DSL Strategy Layer

| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| 058 | [`cam_bridge.mq5` v2.0 multi-instance + EA_ID + porta REQ/REP única](./v0.4-tasks/TASK-058-bridge-multi-instance.md) | R9.01 · CA-I.1 | T009, T030 |
| 059 | [`mt5_integration/multi_ea_manager.py`](./v0.4-tasks/TASK-059-multi-ea-manager.md) | R9.02 · CA-I.1, CA-I.2 | T058 |
| 060 | [`strategies/dsl/` parser YAML/JSON](./v0.4-tasks/TASK-060-dsl-parser.md) | R9.03 · CA-I.3 | T001 |
| 061 | [DSL → Python canonical compiler](./v0.4-tasks/TASK-061-dsl-compiler.md) | R9.04 · CA-I.3 | T060 |
| 062 | [Instrument Catalog ≥ 200 ativos](./v0.4-tasks/TASK-062-instrument-catalog-amplo.md) | R9.05 · CA-I.4 | T011 |

---

## 8. Dependências externas

| # | Dependência | Onde aparece | Mitigação |
|---|---|---|---|
| E1 | Genial habilitar EA em MT5 para PF | T027 (BL-E) | TODO-OP OP-001 confirma plano EA antes da Janela 3 |
| E2 | Layout CSV extrato Genial documentado | T014, T022 | Discovery em PLAN; fallback input manual |
| E3 | TD-v0.4-01 (scraping multi-fonte) | T034 (BL-F) | Esqueleto + placeholder; coleta real só após TD |
| E4 | TD-v0.4-02 (ADR OpenAI) | T041 (BL-G) | OpenAI rejeitado por código até ADR |
| E5 | TimescaleDB hypertable `cam_market_book_snapshots` | T035 (BL-G) | Já criada em SPEC v0.3 |
| E6 | APScheduler em runtime backend | T051 (BL-H2) | Confirmar presença em `pyproject.toml` antes do BL-H2 |

---

## 9. Riscos identificados

| Risco | Probabilidade | Impacto | Mitigação no PLAN |
|---|---|---|---|
| Paridade Python↔MQL5 divergir em edge cases | Média | Alto | T026 com 100+ cenários canônicos + revisão Kevin |
| Property-based testing (T044) revelar violação Art. 11º | Média | Alto | Reverter para 1 estratégia até resolver; bloqueia ativação `MULTI_STRATEGY_ENABLED` |
| Importer Genial encontrar formato proprietário | Média | Médio | T014 começa com discovery do arquivo real; fallback manual |
| Scraping (T034) ficar bloqueado por TD-v0.4-01 | Média | Baixo | Placeholder cobre CA-F.2 sem coleta real |
| Lint anti auto-edição (T047) falsos-positivos | Baixa | Médio | Allowlist explícita em `lint_pyproject.toml`; documentação no commit |
| Reversão automática (T054) disparar em livre-flutuação | Baixa | Médio | Threshold de violação contínua antes de disparo (não tick-by-tick) |
| Multi-EA mutex (T059) gerar deadlock | Baixa | Alto | Property-based testing de Order Gateway com 2 EAs concorrentes |

---

## 10. Reuso aplicado

| O que será reusado | Onde | Origem |
|---|---|---|
| `risk_validate` (18 validators atuais) | Order Gateway (T006) + paridade MQL5 (T025) | Risk Engine vigente |
| Estrutura `cam_market_ticks` + hypertable | T011, T012, T035 | SPEC v0.2 |
| Importer base HTML/CSV | T014 | SPEC v0.2 |
| Bridge ZeroMQ atual (`cam_bridge.mq5` G1) | T009, T027, T030, T058 | SPEC v0.2 |
| Padrão Vertical Slice + Shared Kernel | Todas as features novas | ADR-013 |
| `Settings` + ENV pattern | T005, T046, T056 | SPEC v0.2.1 |
| `FEATURE-FLAGS-LEDGER.md` (append-only) | T046 (#003) + T056 (#004) — entradas já reservadas | EMENDA-001 v2 |
| Constraint DB `is_active único` | T002, T046 | SPEC v0.3 |
| EvidencePack pattern | T003 | Conceitualizado em CAM-VISION-FINAL |
| Telegram Bot Alert | T030, T051, T054 | SPEC v0.1 |

---

## 11. Saídas esperadas (resumo)

- **Código** em `/apps/cam-cockpit/backend/cam/` (features novas) + `/apps/cam-cockpit/backend/migrations/` (10 migrations) + `/apps/cam-cockpit/ntsl/` (sem alteração — Profit fora) + `/apps/cam-cockpit/mql5/` (`cam_bridge.mq5` v2 + `cam_risk_mirror.mq5` novo) + `/apps/cam-cockpit/frontend/` (3 telas novas/atualizadas).
- **Migrations:** 011, 015, 020, 031, 032, 052 = **6 migrations novas** + extensões em existentes.
- **Lints:** `scripts/lint_mql5.sh` (T010) + lint Python anti auto-edição de limites (T047).
- **Testes:** todos os 62 arquivos TASK trazem testes-primeiro; cobertura mínima por bloco ≥ 80% para code paths críticos (`sec=true CRÍTICO` exige property-based onde aplicável).
- **Telemetria:** 6 novos eventos (`ScalingEligibilityReady`, `DIRECTIONAL_CONFLICT`, `AMBIGUOUS_TIE`, `BLOCKED_BY_CEILING`, `INCREMENTAL_VIOLATION`, `OpenAINotEnabled`).
- **Documentação SDOC:** sob solicitação do Founder (Q11) — não disparada por esta SPEC.

---

## 12. `letscode` — Gate Founder do PLAN

| Campo | Valor |
|---|---|
| Status atual | **`true`** ✅ |
| Aprovado por | Founder em 2026-05-27 |
| Motivo se `false` | — |

### Execução autônoma BL-B..BL-I (2026-05-28)

| Bloco | TASKs entregues | Testes | Notas |
|---|---|---|---|
| **BL-B** | T011, T012, T013, T014 | 21/21 ✅ | T014 Genial parser com fallback layout — **TD-v0.4-B1** registrado |
| **BL-D** | T020, T021, T022, T023 | 17/17 ✅ | T024 UI → TD (frontend deferido) |
| **BL-C** | T015, T016, T017, T018, T019 | 9/9 ✅ | Paper loop end-to-end + kill switch <1s + AI Collector real |
| **BL-F** | T031, T032, T033, T034 | 10/10 ✅ | Multi-source placeholder + policy engine alerts |
| **BL-E** | T025, T026, T027, T028, T029, T030 | 15/15 ✅ | `cam_risk_mirror.mq5` único arquivo com OrderSend (lint OK) |
| **BL-G** | T035, T036, T037, T038, T040, T041 | 15/15 ✅ | T039 Research UI → TD; OpenAI hard-blocked (TD-v0.4-02) |
| **BL-H1** | T042..T048 | 19/19 ✅ | Property-based 200 cenários + correlation gate + `get_current_limits()` |
| **BL-H2** | T050, T052, T055, T056 | 20/20 ✅ | T051/T053/T054 → TD (jobs + endpoint + auto-revert) |
| **BL-I** | T058, T059, T060, T061, T062 | 17/17 ✅ | DSL compiler com AST whitelist; 215 instrumentos seed |

**Suite completa:** **710 testes verdes**, zero regressão. Lint MQL5 OK.

**Migrations geradas:** 6 novas em v0.4:
- `0004` bl_a_strategy_lifecycle (cam_strategies + cam_evidence_packs)
- `0005` bl_b_provenance + instruments
- `0006` bl_d_holdings
- `0007` bl_c_paper_loop_extension + runtime_state
- `0008` bl_f_dividends_fundamentals
- `0009` bl_g_ai_provider_calls
- `0010` bl_h2_scaling_events

**Lint:** `scripts/lint_mql5.py` (BL-A) + import-linter (com exceções documentadas para cross-feature de contratos de strategies — TD-v0.4-FEATCONTRACT).

### TASKs Deferred-TechDebt (7/62)

| TASK | Motivo | TD |
|---|---|---|
| T024 | UI Carteira Hard (frontend) | TD-v0.4-T024 |
| T039 | UI Research Workbench (frontend) | TD-v0.4-T039 |
| T049 | UI Risk Console Aderência (frontend) | TD-v0.4-T049+T057 |
| T051 | Job APScheduler scaling | TD-v0.4-H2.2 |
| T053 | Endpoint `/scaling/revoke/{esc_id}` | TD-v0.4-H2.3 |
| T054 | Auto-revert rolling-30d | TD-v0.4-H2.4 |
| T057 | UI Risk Console histograma | TD-v0.4-T049+T057 |

### Execução autônoma BL-A (2026-05-27)

| TASK | Status | Testes |
|---|---|---|
| T001 — Strategy domain (Protocol+Metadata+Status) | ✅ | 19/19 |
| T002 — StrategyRegistry + constraint 1-active | ✅ | 9/9 (DB integ) |
| T003 — Promotion + EvidencePack | ✅ | 15/15 |
| T004 — Autonomy Matrix | ✅ | 41/41 (16 paramétricos) |
| T005 — REAL_TRADING_ALLOWED + allowlist | ✅ | 9/9 |
| T006 — Order Gateway único | ✅ | 9/9 (incl. property-based 100x) |
| T007 — S1 ORB 60m WIN | ✅ | 11/11 |
| T008 — Backtest P&L real por tick scanning | ✅ | 19/19 (substitui stub) |
| T009 — `cam_bridge.mq5` PAUSE/RESUME/GET_VERSION | ✅ | (compilação MT5 manual) |
| T010 — `lint_mql5.sh` | ✅ | 7/7 |

**Suite completa:** 569 testes passando, sem regressão.

### Checklist de aprovação

```
[ ] Carlos Rodrigues Ferreira Junior aprova o PLAN v0.4-VISION-EVOLUTION:

    a) 62 TASKs flat numeradas (sem Épico/FG/Story), TDD First por TASK.

    b) 5 janelas de execução paralelas, cada uma com gate Founder próprio.

    c) Albert↔Nico fechou sem disputa de P/M/G — classificação da SPEC mantida.

    d) Reusos explicitados; pré-requisitos cruzados mapeados.

    e) Riscos identificados com mitigação por TASK.

    f) CODE só inicia a Janela 1 após este `letscode=true`.
```

---

## 13. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 0.4-draft | 2026-05-27 | Indexador inicial + 62 TASKs flat — Nico (Albert sem disputa) | — |
| 0.4-approved | 2026-05-27 | `letscode=true` — Founder autorizou execução autônoma do BL-A | Founder |
| 0.4-bl-a-done | 2026-05-27 | BL-A entregue autônomo (T001-T010, 569 testes verdes) | Nikola |
| 0.4-bl-bcdefghi | 2026-05-28 | BL-B/C/D/E/F/G/H1/H2/I entregues autônomos (55/62 TASKs, 710 testes verdes) | Nikola |

---

> **Princípio operacional do PLAN:**
>
> Flat. Numerado. Pré-requisitos explícitos. TDD First. Founder no gate.
>
> Quando uma TASK ficar maior que cabe na cabeça do Nikola, ela é **dividida em T-NNN.a/b** — nunca virada em "Story".

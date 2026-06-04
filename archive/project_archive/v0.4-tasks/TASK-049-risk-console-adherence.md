---
template: TASK
task_id: TASK-049
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.06]
covers_ca: [CA-H1.5]
features: [F-15]
status: Deferred-TechDebt
sec: false
qa_sec: true
predecessors: [TASK-043]
---

# TASK-049 — UI Risk Console — aderência individual + agregada

## TDD First (Red — UI)

1. `test_console_displays_adherence_per_strategy_card`
2. `test_console_displays_aggregate_adherence_top_panel`
3. `test_console_highlights_strategy_below_95pct_in_red`
4. `test_console_polls_every_5s_via_react_query`
5. `test_console_handles_no_strategies_active_state`

## Implementação alvo (Green)

- Tela: `apps/cam-cockpit/frontend/src/features/risk-console/RiskConsolePage.tsx` — seção "Aderência".
- Endpoint: `GET /api/v1/risk-console/adherence` retornando `{strategies: [{id, name, adherence}], aggregate: number}`.

## Não-objetivos

- ❌ Histograma tentativas-bloqueadas (T057, BL-H2).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Tela + endpoint + 5 testes UI verdes.

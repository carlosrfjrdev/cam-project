---
task_id: TASK-U019
block: BL-UI-4
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU4.01]
covers_ca: [CA-U4.1]
status: Done
sec: true
qa_sec: true
predecessors: [TASK-U003, TASK-U010]
---

# TASK-U019 — Risk Console v0.4 (aderência individual + agregada)

## Objetivo
Estender `features/risk-console/RiskConsolePage.tsx` (existe) com aderência individual×agregada (R8.06), limites vigentes (`get_current_limits`), drawdown agregado, posições. Re-tematizar DS.

## TDD First (Red — Vitest+RTL)
1. `test_shows_individual_and_aggregate_adherence`.
2. `test_strategy_below_95_marked_suspended`.
3. `test_shows_current_limits` — default 2+2 ou escalonado.
4. `test_retematized_to_ds` — cores Esmeralda.

## Green
- Estender página + `useRobotAdherence` → `GET /api/v1/robots/{id}/adherence`. Re-tema.

## Não-objetivos
- ❌ Endpoint (U003). ❌ lógica de aderência.

## Marcadores
- `sec`: true · `qa-sec`: true.

---
task_id: TASK-U020
block: BL-UI-4
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU4.02]
covers_ca: [CA-U4.2]
status: Pending
sec: true
qa_sec: true
predecessors: [TASK-U003, TASK-U010]
---

# TASK-U020 — Tela Robot Orchestrator

## Objetivo
`features/robot-orchestrator/RobotOrchestratorPage.tsx` — robôs + estratégias com prioridade, conflitos resolvidos (DIRECTIONAL_CONFLICT/AMBIGUOUS_TIE), estratégias suspensas.

## TDD First (Red — Vitest+RTL)
1. `test_lists_robots_with_strategies_priority`.
2. `test_shows_conflicts_with_audit_code`.
3. `test_suspended_strategies_marked` — gain lock/aderência.
4. `test_multi_strategy_flag_shown` — `MULTI_STRATEGY_ENABLED` (default false).

## Green
- Página + `useRobots` → `GET /api/v1/robots`. Rota `/robots`.

## Não-objetivos
- ❌ Endpoint (U003). ❌ ativar multiestratégia.

## Marcadores
- `sec`: true · `qa-sec`: true.

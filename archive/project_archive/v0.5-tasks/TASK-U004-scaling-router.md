---
task_id: TASK-U004
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.04]
covers_ca: [CA-U0.3]
status: Done
sec: true
qa_sec: true
predecessors: []
---

# TASK-U004 — Router Scaling/Escalonamento (NOVO)

## Objetivo
Criar `cam/features/scaling/routes.py` + montar. Inclui revoke (TD-v0.4-H2.3).

## TDD First (Red)
1. `test_get_scaling_events` — `GET /api/v1/scaling/events`.
2. `test_get_eligibility` — `GET /api/v1/scaling/eligibility/{strategy_id}`.
3. `test_get_blocked_attempts` — histograma por critério.
4. `test_post_revoke` — `POST /api/v1/scaling/revoke/{esc_id}` (cooldown 7/21).
5. `test_router_mounted`.

## Green
- `routes.py` consome `scaling.py` + `ScalingEventsRepository` v0.4. Montar em `main.py`.

## Não-objetivos
- ❌ UI (U021). ❌ ativar SCALING_ENABLED (continua false).

## Marcadores
- `sec`: true · `qa-sec`: true.

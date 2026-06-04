---
task_id: TASK-U003
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.03]
covers_ca: [CA-U0.3]
status: Done
sec: true
qa_sec: true
predecessors: []
---

# TASK-U003 — Router Robot Orchestrator (NOVO)

## Objetivo
Criar `cam/features/robot_orchestrator/routes.py` (read-only) + montar.

## TDD First (Red)
1. `test_get_robots_returns_list` — `GET /api/v1/robots` (robôs + estratégias + prioridade).
2. `test_get_robot_adherence` — `GET /api/v1/robots/{id}/adherence` (individual + agregada).
3. `test_router_mounted`.
4. `test_no_write_orchestration_endpoint` — router não dispara orquestração de ordem (Kevin).

## Green
- `routes.py` consome `RobotOrchestrator`/repository v0.4. Read-only. Montar em `main.py`.

## Não-objetivos
- ❌ UI (U020). ❌ alterar orchestrator.

## Marcadores
- `sec`: true · `qa-sec`: true.

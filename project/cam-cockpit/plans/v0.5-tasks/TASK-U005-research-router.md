---
task_id: TASK-U005
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.05]
covers_ca: [CA-U0.3]
status: Done
sec: false
qa_sec: true
predecessors: []
---

# TASK-U005 — Router Research / AI Workbench (NOVO)

## Objetivo
Criar `cam/features/research/routes.py` + montar.

## TDD First (Red)
1. `test_get_correlation` — `GET /api/v1/research/correlation`.
2. `test_post_pair_trade_backtest` — `POST /api/v1/research/pair-trade-backtest`.
3. `test_post_workbench_returns_json` — output estruturado.
4. `test_workbench_openai_blocked` — provider openai → `OpenAINotEnabled`.
5. `test_router_mounted`.

## Green
- `routes.py` consome `research/*` + `ai_analyst/provider_governance` v0.4. Montar em `main.py`.

## Não-objetivos
- ❌ UI (U023). ❌ habilitar OpenAI (TD-v0.4-02).

## Marcadores
- `sec`: false · `qa-sec`: true (provider governance).

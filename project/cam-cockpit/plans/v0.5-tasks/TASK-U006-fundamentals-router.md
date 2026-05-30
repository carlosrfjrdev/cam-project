---
task_id: TASK-U006
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.06]
covers_ca: [CA-U0.3]
status: Pending
sec: false
qa_sec: true
predecessors: []
---

# TASK-U006 — Router Fundamentals/Dividendos (NOVO)

## Objetivo
Criar `cam/features/fundamentals/routes.py` + montar. Inclui policy alerts.

## TDD First (Red)
1. `test_get_fundamentals_ticker` — `GET /api/v1/fundamentals/{ticker}` (7 indicadores R-20).
2. `test_get_dividends_calendar` — `GET /api/v1/dividends/calendar`.
3. `test_get_policy_alerts` — `GET /api/v1/carteira-hard/policy-alerts` (sugestão, nunca bloqueio).
4. `test_router_mounted`.

## Green
- `routes.py` consome `fundamentals/*` + `ledger/policy_engine` v0.4. Montar em `main.py`.

## Não-objetivos
- ❌ UI (U022). ❌ scraping real (TD-v0.4-01).

## Marcadores
- `sec`: false · `qa-sec`: true.

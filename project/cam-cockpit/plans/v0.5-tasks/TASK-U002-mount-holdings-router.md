---
task_id: TASK-U002
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.01]
covers_ca: [CA-U0.2]
status: Done
sec: false
qa_sec: true
predecessors: []
---

# TASK-U002 — Registrar `holdings_router` (carteira-hard)

## Objetivo
Montar `holdings_router` (dead route v0.4) em `main.py`.

## TDD First (Red)
1. `test_get_holdings_returns_200` — `GET /api/v1/carteira-hard/holdings`.
2. `test_post_holding_manual_ui` — cria holding `source=MANUAL_UI`.
3. `test_holdings_router_mounted` — presente no OpenAPI.
4. `test_holding_rejects_invalid_source` — só MANUAL_UI/GENIAL_IMPORT.

## Green
- `app.include_router(holdings_router)` em `main.py`. Endpoints já existem (`holdings_router.py` v0.4) — só montar + smoke.

## Não-objetivos
- ❌ UI (U022). ❌ importer Genial (já v0.4).

## Marcadores
- `sec`: false · `qa-sec`: true.

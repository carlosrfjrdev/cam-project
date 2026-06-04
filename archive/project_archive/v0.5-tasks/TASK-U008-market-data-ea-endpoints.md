---
task_id: TASK-U008
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.08]
covers_ca: [CA-U0.3]
status: Done
sec: true
qa_sec: true
predecessors: []
---

# TASK-U008 — Expor Market Data provenance + instruments + EA control

## Objetivo
Garantir endpoints para a tela de Market Data e o EA Control Panel.

## TDD First (Red)
1. `test_get_provenance` — `GET /api/v1/market-data/provenance` (lotes + quality flags + hash).
2. `test_get_instruments` — `GET /api/v1/market-data/instruments` (WIN/WDO point_value).
3. `test_ea_get_version` — via `mt5_router` retorna versão+hash+paused.
4. `test_ea_pause_resume` — PAUSE_EA/RESUME_EA refletem status (sem OrderSend).
5. `test_no_submit_order_via_ea_endpoint` — Kevin.

## Green
- Estender `market_data/routes.py` + reusar `mt5_router` (já montado). Read + controle seguro.

## Não-objetivos
- ❌ UI (U017, U018). ❌ SUBMIT_ORDER.

## Marcadores
- `sec`: true (EA control) · `qa-sec`: true.

---
task_id: TASK-U001
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.01, RU0.02]
covers_ca: [CA-U0.1]
status: Pending
sec: true
qa_sec: true
predecessors: []
---

# TASK-U001 — Registrar `strategies_router` + completar endpoints

> Lead: Oscar (+Kevin sec). Dead route → viva.

## Objetivo
Montar o router de strategies (hoje órfão) em `cam/api/main.py` e garantir endpoints read + comandos governados.

## TDD First (Red)
1. `test_get_strategies_returns_200_with_s1` — `GET /api/v1/strategies` lista S1 ORB.
2. `test_get_strategy_by_id`.
3. `test_promote_without_evidence_returns_error` — `EVIDENCE_REQUIRED`.
4. `test_strategies_router_mounted` — rota presente no OpenAPI schema do app.
5. `test_no_order_submission_endpoint` — nenhum endpoint de strategies envia ordem (Kevin).

## Green
- `app.include_router(strategies_router)` em `main.py`.
- Em `features/strategies/routes.py`: `GET /api/v1/strategies`, `GET /{id}`, `POST /{id}/promote` (EvidencePack), `POST /{id}/activate`. Consome repository v0.4. **Read + comandos governados; nunca ordem.**

## Não-objetivos
- ❌ UI (U016). ❌ lógica nova de registry (já existe v0.4).

## Marcadores
- `sec`: true · `qa-sec`: true.

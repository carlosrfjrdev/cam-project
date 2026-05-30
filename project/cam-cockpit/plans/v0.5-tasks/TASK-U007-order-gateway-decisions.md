---
task_id: TASK-U007
block: BL-UI-0
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU0.07]
covers_ca: [CA-U0.3, CA-U0.5]
status: Pending
sec: true
sec_critical: true
qa_sec: true
predecessors: []
---

# TASK-U007 — Endpoint Order Gateway decisions (read-only)

> SEC CRÍTICO — expõe o ponto mais sensível, mas SOMENTE leitura.

## Objetivo
`GET /api/v1/order-gateway/decisions` — lê `cam_risk_decisions` (decisão, validator culpado, env, mode, asset, direction, motivo, ts). **Nunca submete ordem.**

## TDD First (Red)
1. `test_get_decisions_returns_list`.
2. `test_decision_includes_validator_culprit` — REJECTED traz validator + motivo.
3. `test_filter_by_env_and_decision`.
4. `test_endpoint_is_read_only` — não há verbo POST/PUT que submeta ordem (Kevin).
5. `test_router_mounted`.

## Green
- Novo router (ou em mt5/dashboard) lendo `cam_risk_decisions`. Read-only estrito.

## Não-objetivos
- ❌ UI (U013). ❌ qualquer caminho de submissão de ordem.

## Marcadores
- `sec`: true CRÍTICO · `qa-sec`: true CRÍTICO.

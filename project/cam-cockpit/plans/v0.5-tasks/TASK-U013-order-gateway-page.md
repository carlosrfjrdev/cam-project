---
task_id: TASK-U013
block: BL-UI-2
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU2.01]
covers_ca: [CA-U2.1]
status: Pending
sec: true
sec_critical: true
qa_sec: true
predecessors: [TASK-U007, TASK-U010]
---

# TASK-U013 — Tela Order Gateway / Risk Decisions

> SEC CRÍTICO. Lead: Don. Visibilidade do ponto mais sensível (read-only).

## Objetivo
`features/order-gateway/OrderGatewayPage.tsx` — tabela de decisões consumindo `GET /api/v1/order-gateway/decisions`.

## TDD First (Red — Vitest+RTL)
1. `test_lists_decisions_with_validator_and_reason`.
2. `test_rejected_rows_highlighted` — REJECTED em destaque (vermelho).
3. `test_filter_by_env_and_decision`.
4. `test_no_submit_action_in_ui` — tela não tem botão que envie ordem (Kevin).
5. `test_empty_state`.

## Green
- Página + hook `useOrderGatewayDecisions` (React Query). Rota `/order-gateway`. Read-only.

## Não-objetivos
- ❌ Endpoint (U007). ❌ qualquer ação de ordem.

## Marcadores
- `sec`: true CRÍTICO · `qa-sec`: true CRÍTICO.

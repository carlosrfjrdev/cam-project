---
task_id: TASK-U016
block: BL-UI-3
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU3.01]
covers_ca: [CA-U3.1]
status: Done
sec: true
qa_sec: true
predecessors: [TASK-U001, TASK-U010]
---

# TASK-U016 — Tela Strategy Registry

## Objetivo
`features/strategies/StrategyRegistryPage.tsx` — lista estratégias + status (draft→retired) + is_active + EvidencePack resumido. S1 ORB visível.

## TDD First (Red — Vitest+RTL)
1. `test_lists_strategies_with_status` — S1 ORB com status + is_active.
2. `test_promote_without_evidence_shows_error` — `EVIDENCE_REQUIRED`.
3. `test_activate_is_gated` — ativar exige confirmação (gate visual).
4. `test_no_order_action` — sem botão de ordem (Kevin).

## Green
- Página + `useStrategies` (React Query) → `GET /api/v1/strategies`. Rota `/strategies`. Ações governadas.

## Não-objetivos
- ❌ Endpoint (U001). ❌ lógica registry.

## Marcadores
- `sec`: true · `qa-sec`: true.

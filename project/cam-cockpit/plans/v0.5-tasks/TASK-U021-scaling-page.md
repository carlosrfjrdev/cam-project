---
task_id: TASK-U021
block: BL-UI-4
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU4.03]
covers_ca: [CA-U4.3]
status: Done
sec: true
qa_sec: true
predecessors: [TASK-U004, TASK-U010]
---

# TASK-U021 — Tela Escalonamento (histograma tentativas-bloqueadas)

## Objetivo
`features/scaling/ScalingPage.tsx` — histograma de tentativas-bloqueadas por critério (5 critérios Art. 11-B), eventos, cooldown vigente, botão revogar.

## TDD First (Red — Vitest+RTL)
1. `test_histogram_5_criteria` — PF/WR/EXP/DD/ADH.
2. `test_blocked_attempt_visible`.
3. `test_revoke_button_calls_endpoint` — `POST /scaling/revoke`.
4. `test_scaling_flag_shown` — `SCALING_ENABLED` (default false).

## Green
- Página + `useScaling` → `GET /scaling/blocked-attempts|events`. Rota `/scaling`.

## Não-objetivos
- ❌ Endpoint (U004). ❌ ativar escalonamento.

## Marcadores
- `sec`: true · `qa-sec`: true.

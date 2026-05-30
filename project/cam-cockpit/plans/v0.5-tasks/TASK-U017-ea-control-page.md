---
task_id: TASK-U017
block: BL-UI-3
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU3.02]
covers_ca: [CA-U3.2]
status: Pending
sec: true
qa_sec: true
predecessors: [TASK-U008, TASK-U010]
---

# TASK-U017 — Tela EA Control Panel

## Objetivo
`features/ea-control/EaControlPage.tsx` — status do EA (versão+hash+paused), botões PAUSE_EA/RESUME_EA, heartbeat (online/offline). Sem SUBMIT_ORDER.

## TDD First (Red — Vitest+RTL)
1. `test_shows_version_hash`.
2. `test_pause_resume_reflects_status`.
3. `test_heartbeat_offline_highlighted`.
4. `test_no_submit_order_button` — Kevin.

## Green
- Página + `useEaControl` → `mt5_router` (GET_VERSION/PAUSE_EA/RESUME_EA). Rota `/ea-control`.

## Não-objetivos
- ❌ Endpoint (U008). ❌ envio de ordem.

## Marcadores
- `sec`: true · `qa-sec`: true.

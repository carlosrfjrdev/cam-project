---
task_id: TASK-U015
block: BL-UI-2
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU2.03]
covers_ca: [CA-U2.4]
status: Pending
sec: true
qa_sec: true
predecessors: [TASK-U010]
---

# TASK-U015 — Kill switch presente em toda tela operacional (auditoria)

> Lead: Don. Art. 18º — kill switch acessível ≤ 1 toque.

## TDD First (Red — Vitest+RTL)
1. `test_killswitch_in_appshell` — botão presente no shell, visível em toda rota operacional.
2. `test_killswitch_one_tap` — aciona sem confirmação burocrática que atrase.
3. `test_killswitch_uses_existing_hook` — reusa `useKillSwitch` (não reimplementa).

## Green
- Garantir `KillSwitchButton` (já existe) montado no `AppShell` (header), acessível em todas as telas.

## Não-objetivos
- ❌ Lógica de kill switch (já existe v0.1).

## Marcadores
- `sec`: true · `qa-sec`: true.

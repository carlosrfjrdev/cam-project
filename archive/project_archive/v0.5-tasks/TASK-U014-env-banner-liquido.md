---
task_id: TASK-U014
block: BL-UI-2
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU2.02]
covers_ca: [CA-U2.2, CA-U2.3]
status: Done
sec: true
qa_sec: true
predecessors: [TASK-U011]
---

# TASK-U014 — EnvBanner transversal + PnlDisplay líquido em todas as telas

> Lead: Don. Art. 25º (líquido) + banner de ambiente em toda tela operacional.

## TDD First (Red — Vitest+RTL)
1. `test_env_banner_present_in_appshell` — banner em 100% das telas operacionais.
2. `test_all_monetary_values_are_net` — varredura: nenhum valor monetário bruto sem provisão.
3. `test_real_env_requires_confirmation` — ambiente real exige banner vermelho + confirmação.
4. `test_pnl_display_used_not_raw_number` — telas usam `PnlDisplay`, não número cru.

## Green
- Montar `EnvBanner` no `AppShell` (U010). Substituir exibições monetárias por `PnlDisplay`.

## Não-objetivos
- ❌ Componente em si (U011). ❌ ligar real.

## Marcadores
- `sec`: true · `qa-sec`: true.

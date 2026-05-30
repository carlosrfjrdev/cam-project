---
task_id: TASK-U011
block: BL-UI-1
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU1.04]
covers_ca: [CA-U1.3]
status: Done
sec: false
qa_sec: true
predecessors: [TASK-U009]
---

# TASK-U011 — Componentes de defesa (EnvBanner + PnlDisplay + re-tema)

> Lead: Don. Defesa de capital como componente.

## Objetivo
Componentes de defesa: `EnvBanner` (NOVO), `PnlDisplay` (re-tema, sempre líquido), `RiskEngineStatusBanner` (re-tema), `KillSwitchButton` (preservar).

## TDD First (Red — Vitest+RTL)
1. `test_env_banner_shows_demo_paper_backtest` — ambiente correto.
2. `test_env_banner_real_is_unmistakable` — banner vermelho inconfundível p/ real.
3. `test_pnl_display_always_net` — exibe líquido (Art. 25º); nunca bruto sem provisão.
4. `test_pnl_negative_is_red` — loss em `#EF4444`.
5. `test_risk_banner_retematized` — usa cores DS Esmeralda.

## Green
- `_shared/components/EnvBanner.tsx`; re-tematizar `PnlDisplay`, `RiskEngineStatusBanner` para tokens DS.

## Não-objetivos
- ❌ Posicionar nas telas (U014). ❌ lógica de PnL (vem da API).

## Marcadores
- `sec`: false · `qa-sec`: true (Don: banner = defesa).

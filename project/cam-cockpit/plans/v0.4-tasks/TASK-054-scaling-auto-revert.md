---
template: TASK
task_id: TASK-054
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.14]
covers_ca: [CA-H2.5, CA-H2.6]
features: [F-15c]
status: Deferred-TechDebt
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-050, TASK-052]
---

# TASK-054 — Reversão automática + DD em dobro + soft kill switch

## Objetivo

Job rolling-30-pregões avalia continuidade. Falha → reversão automática + audit + Telegram + soft kill switch (1 pregão bloqueado). **DD ocorrido durante escalonado conta em dobro** na próxima janela (Voltaire 2).

## TDD First (Red)

1. `test_auto_revert_triggered_when_any_criterion_falls_below_threshold_in_rolling_30d`
2. `test_auto_revert_persists_AUTO_REVERTED_event`
3. `test_auto_revert_sends_telegram_with_strategy_and_reason`
4. `test_auto_revert_activates_soft_kill_switch_1_pregao` — CA-H2.5.
5. `test_drawdown_during_scaled_doubles_in_next_eligibility_window` — CA-H2.6.
6. `test_continuous_threshold_required_not_tick_by_tick` — guard contra falso-positivo.

## Implementação alvo (Green)

- Arquivo: `cam/features/scaling/auto_revert.py::evaluate_continuity_and_revert(strategy_id) -> ContinuityResult`.
- Job rolling 30d (cron diário pós-pregão, encadeado com T051).
- Soft kill switch: flag `is_blocked_until_ts` em `cam_strategy_runtime_state`.

## Não-objetivos

- ❌ Reset incremental sem revogação manual (apenas reversão).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Módulo + 6 testes verdes.

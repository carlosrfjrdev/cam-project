---
template: TASK
task_id: TASK-053
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.13]
covers_ca: [CA-H2.4]
features: [F-15c]
status: Deferred-TechDebt
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-050, TASK-052]
---

# TASK-053 — Endpoint `POST /scaling/revoke/{esc_id}` + cooldown reverso 7/21 dias

## Objetivo

- Cooldown reverso padrão: **7 dias**.
- **21 dias** se `detect_win_streak(strategy_id) == true` (recomendação Voltaire 1).
- Durante cooldown, operador pode revogar sem ônus.

## TDD First (Red)

1. `test_detect_win_streak_true_when_5_wins_consecutive` — threshold definido em POV §3.x.
2. `test_cooldown_days_7_when_no_win_streak`
3. `test_cooldown_days_21_when_win_streak_active` — CA-H2.4.
4. `test_revoke_endpoint_resets_limit_to_default_and_clears_cooldown`
5. `test_revoke_after_cooldown_ends_raises_AlreadyApplied`
6. `test_revoke_emits_telegram_and_audit`

## Implementação alvo (Green)

- Arquivo: `cam/features/scaling/cooldown.py::compute_cooldown(strategy_id) -> CooldownPlan`.
- Endpoint: `cam/features/scaling/router.py::POST /api/v1/scaling/revoke/{esc_id}`.

## Não-objetivos

- ❌ Reversão automática (T054).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Módulos + endpoint + 6 testes verdes.

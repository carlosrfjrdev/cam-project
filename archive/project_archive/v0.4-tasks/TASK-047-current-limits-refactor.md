---
template: TASK
task_id: TASK-047
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.04]
covers_ca: [CA-H1.7, CA-H2.8]
features: [F-15b]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-045]
---

# TASK-047 — Refactor `max_contracts_check` → `get_current_limits()` + lint anti auto-edição

## Objetivo

Remover constants `MAX_WIN_CONTRACTS=2` hardcoded de `max_contracts_check`. Passar a chamar `get_current_limits()` que lê estado vigente (default 2+2 ou escalonado via T050). **Lint enforça impossibilidade de auto-edição** desses limites (recomendação Leo).

## TDD First (Red)

1. `test_max_contracts_check_uses_get_current_limits_not_hardcoded`
2. `test_get_current_limits_returns_2_2_when_SCALING_ENABLED_false`
3. `test_get_current_limits_returns_scaled_values_when_SCALING_ENABLED_true_and_active_event`
4. `test_lint_fails_when_PR_modifies_MAX_WIN_CONTRACTS_or_correlates` — CA-H1.7.
5. `test_lint_allowlist_respects_designated_files_only`
6. `test_max_contracts_consumes_current_limits_in_pipeline_position` — não rompe ordem do Risk Engine.

## Implementação alvo (Green)

- Editar: `cam/_shared/risk/validators/max_contracts.py` — remover constants; importar `get_current_limits()`.
- Arquivo novo: `cam/_shared/risk/limits.py::get_current_limits() -> CurrentLimits` — lê de `cam_constitutional_scaling_events` se `SCALING_ENABLED=true`.
- Lint Python: `scripts/lint_constitutional_limits.py` — proíbe alteração de `MAX_WIN_CONTRACTS`, `MAX_WDO_CONTRACTS`, `MAX_DAILY_DRAWDOWN_PCT` em qualquer arquivo fora da allowlist.
- Integrar no CI (`pre-commit` + GitHub Actions).

## Não-objetivos

- ❌ Compute scaling eligibility (T050).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Refactor + `limits.py` + lint + 6 testes verdes.

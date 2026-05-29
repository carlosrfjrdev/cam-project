---
template: TASK
task_id: TASK-045
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.02]
covers_ca: [CA-H1.1, CA-H1.5, CA-H1.6]
features: [F-15b]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-043]
---

# TASK-045 — `_shared/risk/aggregate.py` validator (Art. 11-A)

## Objetivo

Validator agregado (Art. 11-A) — entra no pipeline do Risk Engine (pos. 8.6) lendo limites vigentes via `get_current_limits()` (T047).

## TDD First (Red)

1. `test_aggregate_rejects_when_sum_contracts_exceeds_limit` — `(3 WIN + 0 WDO)` com limite vigente 2+2 → reject.
2. `test_aggregate_accepts_when_sum_within_limit`
3. `test_aggregate_uses_scaled_limits_when_SCALING_ENABLED_true` — placeholder (T050 traz `scaling.py`).
4. `test_aggregate_rejects_when_drawdown_projection_exceeds_3pct` — Art. 16.
5. `test_aggregate_suspends_strategy_with_adherence_lt_95_in_30d` — CA-H1.5.
6. `test_aggregate_blocks_new_strategy_when_correlation_gt_0_7` — CA-H1.6.
7. **Property-based 10.000 cenários:** Hypothesis nunca permite aprovação que viole limite vigente.

## Implementação alvo (Green)

- Arquivo: `cam/_shared/risk/aggregate.py::aggregate_risk_check(candidates, context) -> ValidationResult`.
- Posição 8.6 do pipeline (após `max_contracts_check`, antes de `scaling_eligibility_check`).
- Registrar em `MAPPING-CONSTITUICAO-RISK-ENGINE.md`.

## Não-objetivos

- ❌ Escalonamento (T050).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Módulo + 7 testes verdes.

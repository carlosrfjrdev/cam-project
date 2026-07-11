---
template: TASK
task_id: TASK-033
block: BL-F
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R6.04]
covers_ca: [CA-F.3, CA-F.4]
features: [F-24]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-032]
---

# TASK-033 — Carteira Hard Policy Engine (alertas — nunca bloqueio hard, R-13)

## TDD First (Red)

1. `test_policy_alert_level_1_when_DY_below_4_percent`
2. `test_policy_alert_level_2_when_PL_above_25`
3. `test_policy_alert_level_3_when_div_liq_ebitda_above_3`
4. `test_policy_no_alert_when_all_indicators_within_thresholds`
5. `test_policy_never_blocks_operation_only_warns` — CA-F.4.
6. `test_policy_returns_alerts_list_serializable_to_json`

## Implementação alvo (Green)

- Arquivo: `cam/features/ledger/policy_engine.py::evaluate_holding(holding, fundamentals) -> list[PolicyAlert]`.
- `PolicyAlert(level: int, code: str, message: str, suggestion: str)`.

## Não-objetivos

- ❌ Bloquear operação (R-13 explícito: alerta nunca bloqueia).
- ❌ Rebalance (T040, BL-G).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- `policy_engine.py` + 6 testes verdes.

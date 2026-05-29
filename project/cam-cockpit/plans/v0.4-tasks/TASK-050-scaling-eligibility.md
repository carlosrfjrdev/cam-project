---
template: TASK
task_id: TASK-050
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.10]
covers_ca: [CA-H2.1, CA-H2.2]
features: [F-15c]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-045]
---

# TASK-050 — `_shared/risk/scaling.py` — `compute_scaling_eligibility` (Art. 11-B)

## Objetivo

Pure Python — **sem auto-execução**. Lê 30 pregões consecutivos + computa as 5 métricas da Art. 11-B (a):
- Profit Factor ≥ 1,8
- Win rate ≥ 55%
- Expectância líquida ≥ 1,5 × custo fixo mensal (recomendação Mammon)
- Drawdown ≤ 10% do Bucket Derivativo
- Aderência ≥ 95%

## TDD First (Red)

1. `test_eligibility_true_when_all_5_criteria_met_30d`
2. `test_eligibility_false_when_any_criterion_missing_reports_specific_one` — `missing_criteria=[critério]` — CA-H2.2.
3. `test_eligibility_recompute_for_each_strategy_isolated`
4. `test_eligibility_returns_evidence_pack_serializable`
5. `test_eligibility_pure_no_side_effects` — não persiste nada; só lê.
6. **Property-based:** Hypothesis gera 5.000 datasets sintéticos validando contrato (eligible iff todos os 5).
7. `test_eligibility_drawdown_doubles_when_previous_period_was_scaled` — preparado para T054.

## Implementação alvo (Green)

- Arquivo: `cam/_shared/risk/scaling.py::compute_scaling_eligibility(strategy_id, journal_repo, now) -> ScalingEligibility`.
- Dataclass `ScalingEvidence(profit_factor, win_rate, expectancy_net, drawdown_pct, adherence, pregoes_count)`.

## Não-objetivos

- ❌ Persistência (T052). ❌ Job (T051). ❌ Aplicação (T053).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- `scaling.py` + 7 testes verdes.

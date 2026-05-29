---
template: TASK
task_id: TASK-037
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.02]
covers_ca: [CA-G.2]
features: [F-23]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-012]
---

# TASK-037 — `research/cross_asset_correlation.py`

## TDD First (Red)

1. `test_rolling_correlation_window_30d_default`
2. `test_correlation_returns_nan_when_insufficient_data`
3. `test_correlation_symmetric_a_b_equals_b_a`
4. `test_correlation_pandas_compatible_dataframe_output`

## Implementação alvo (Green)

- Arquivo: `cam/features/research/cross_asset_correlation.py::compute_correlation(asset_a, asset_b, window_days=30) -> CorrelationResult`.

## Não-objetivos

- ❌ Visualização (T039 cuida).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Módulo + 4 testes verdes.

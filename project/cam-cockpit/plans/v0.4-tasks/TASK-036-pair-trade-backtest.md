---
template: TASK
task_id: TASK-036
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.02]
covers_ca: [CA-G.2]
features: [F-27]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-012, TASK-035]
---

# TASK-036 — `research/pair_trade_backtest.py`

## TDD First (Red)

1. `test_pair_trade_simulator_runs_with_2_assets_simultaneously`
2. `test_pair_trade_computes_spread_zscore_per_bar`
3. `test_pair_trade_opens_short_long_at_zscore_threshold`
4. `test_pair_trade_closes_at_mean_reversion`
5. `test_metrics_returns_correlation_sharpe_pnl`
6. `test_WIN_x_WDO_fixture_run_completes_without_error`

## Implementação alvo (Green)

- Arquivo: `cam/features/research/pair_trade_backtest.py::run_pair_backtest(asset_a, asset_b, ts_from, ts_to, params) -> PairBacktestResult`.

## Não-objetivos

- ❌ Operação real (research only). ❌ Pattern Lab (T038).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Módulo + 6 testes verdes.

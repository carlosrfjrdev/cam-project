---
template: TASK
task_id: TASK-008
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.09, R1.10]
covers_ca: [CA-A.3]
features: [F-03]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-007, TASK-012]
---

# TASK-008 — Backtest P&L real por tick scanning

## Objetivo

Substituir stub `result_gross=0` por simulador que percorre **tick a tick** até SL/TP e calcula P&L real. Persiste em `cam_backtest_runs` + `cam_backtest_trades`.

## TDD First (Red)

1. `test_backtest_zero_trades_when_no_signal_in_window`
2. `test_backtest_long_trade_hits_take_profit` — P&L > 0; trade fechado por TP.
3. `test_backtest_long_trade_hits_stop_loss` — P&L < 0; trade fechado por SL.
4. `test_backtest_persists_run_and_trades_in_db`
5. `test_backtest_run_id_deterministic_given_same_input` — para reprodutibilidade.
6. `test_backtest_handles_overlap_intent_with_close_first` — não abre 2ª posição antes da 1ª fechar.
7. `test_backtest_emits_adherence_metric_per_trade`

## Implementação alvo (Green)

- Arquivo: `cam/features/backtest/simulator.py` — `BacktestSimulator.run(strategy_id, ts_from, ts_to)`.
- Lê `cam_market_ticks` em chunks; aplica `evaluate` em cada tick (ou agregação 1m); processa fila de posições abertas.
- Persiste cada trade individual com `result_gross`, `result_net` (após custos R-25), `adherence`.

## Não-objetivos

- ❌ Walk-forward (TD-013 — fora desta SPEC).
- ❌ Otimização de parâmetros.
- ❌ Multi-asset (single asset por backtest run).

## Marcadores

- `sec`: false.
- `qa-sec`: true.

## Saídas

- `simulator.py` + 7 testes verdes. Rodar S1 sobre 1 mês de tick WIN deve produzir N trades + P&L != 0.

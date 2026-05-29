---
template: TASK
task_id: TASK-015
block: BL-C
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R3.02]
covers_ca: [CA-C.1]
features: [F-06]
status: Completed
sec: false
qa_sec: true
predecessors: []
---

# TASK-015 — Migration `cam_paper_trades`

## Objetivo

Persistir paper trades (TD-022 resolvido).

## TDD First (Red)

1. `test_migration_creates_cam_paper_trades_with_required_columns`
2. `test_result_net_computed_after_costs_and_ir` — função utilitária.
3. `test_adherence_field_is_numeric_between_0_and_1`
4. `test_indexes_for_strategy_id_and_ts_open_exist`

## Implementação alvo (Green)

- Migration:
  ```sql
  CREATE TABLE cam_paper_trades (
    id UUID PRIMARY KEY,
    strategy_id UUID NOT NULL REFERENCES cam_strategies(id),
    intent_id UUID NOT NULL,
    asset TEXT NOT NULL,
    direction TEXT NOT NULL,
    contracts INT NOT NULL,
    entry_price NUMERIC NOT NULL,
    exit_price NUMERIC,
    result_gross NUMERIC,
    costs NUMERIC,
    ir_provisioned NUMERIC,
    result_net NUMERIC,
    adherence NUMERIC,
    ts_open TIMESTAMPTZ NOT NULL,
    ts_close TIMESTAMPTZ
  );
  CREATE INDEX ON cam_paper_trades (strategy_id, ts_open DESC);
  ```

## Não-objetivos

- ❌ Lógica do loop (T016).

## Marcadores

- `sec`: false.
- `qa-sec`: true.

## Saídas

- Migration + 4 testes verdes.

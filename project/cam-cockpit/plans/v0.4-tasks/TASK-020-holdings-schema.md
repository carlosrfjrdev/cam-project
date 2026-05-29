---
template: TASK
task_id: TASK-020
block: BL-D
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R4.01]
covers_ca: [CA-D.1]
features: [F-10]
status: Completed
sec: false
qa_sec: true
predecessors: []
---

# TASK-020 — Migration `cam_carteira_hard_holdings`

## TDD First (Red)

1. `test_migration_creates_table_with_all_columns`
2. `test_unique_on_ticker_plus_source_acquisition_hash_prevents_dup`
3. `test_indexes_on_ticker_and_source_exist`
4. `test_constraint_quantity_positive` — `quantity > 0`.

## Implementação alvo (Green)

```sql
CREATE TABLE cam_carteira_hard_holdings (
  id UUID PRIMARY KEY,
  ticker TEXT NOT NULL,
  asset_class TEXT NOT NULL,
  quantity NUMERIC NOT NULL CHECK (quantity > 0),
  avg_price NUMERIC NOT NULL,
  first_acquisition_at TIMESTAMPTZ NOT NULL,
  last_acquisition_at TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  hash TEXT NOT NULL UNIQUE
);
```

## Não-objetivos

- ❌ Endpoint (T021), importer (T022).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Migration + 4 testes verdes.

---
template: TASK
task_id: TASK-032
block: BL-F
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R6.03]
covers_ca: [CA-F.2]
features: [F-22]
status: Completed
sec: false
qa_sec: true
predecessors: []
---

# TASK-032 — Migration `cam_fundamentals_snapshot` (R-20 — 7 indicadores)

## TDD First (Red)

1. `test_migration_creates_table_with_exactly_7_indicator_columns`
2. `test_columns_exact_names_R20` — `dy, pl, pvp, roe, div_liq_ebitda, payout, roic`.
3. `test_PK_on_ticker_plus_ts_snapshot`
4. `test_hash_unique_constraint`
5. `test_seed_NULL_safe_for_missing_indicators`

## Implementação alvo (Green)

```sql
CREATE TABLE cam_fundamentals_snapshot (
  ticker TEXT NOT NULL,
  ts_snapshot TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  dy NUMERIC,
  pl NUMERIC,
  pvp NUMERIC,
  roe NUMERIC,
  div_liq_ebitda NUMERIC,
  payout NUMERIC,
  roic NUMERIC,
  hash TEXT UNIQUE,
  PRIMARY KEY (ticker, ts_snapshot)
);
```

## Não-objetivos

- ❌ Coleta (T034). ❌ Policy engine (T033).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Migration + 5 testes verdes.

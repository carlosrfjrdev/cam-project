---
template: TASK
task_id: TASK-031
block: BL-F
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R6.01, R6.02]
covers_ca: [CA-F.1]
features: [F-11]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-020]
---

# TASK-031 — Migrations `cam_dividends_calendar` + `cam_dividends_received`

## TDD First (Red)

1. `test_calendar_migration_creates_table_with_PK_and_FK_to_instruments`
2. `test_received_migration_creates_table_referencing_holding`
3. `test_unique_constraint_on_ticker_plus_ex_date_plus_type`
4. `test_index_on_payment_date_for_calendar_queries`

## Implementação alvo (Green)

```sql
CREATE TABLE cam_dividends_calendar (
  id UUID PRIMARY KEY,
  ticker TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('DIV','JCP')),
  ex_date DATE NOT NULL,
  payment_date DATE NOT NULL,
  amount_per_share NUMERIC NOT NULL,
  source TEXT NOT NULL,
  hash TEXT UNIQUE NOT NULL,
  UNIQUE (ticker, ex_date, type)
);
CREATE TABLE cam_dividends_received (
  id UUID PRIMARY KEY,
  ticker TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  type TEXT NOT NULL,
  payment_date DATE NOT NULL,
  holding_id_ref UUID REFERENCES cam_carteira_hard_holdings(id)
);
```

## Não-objetivos

- ❌ Collector (T034).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- 2 migrations + 4 testes verdes.

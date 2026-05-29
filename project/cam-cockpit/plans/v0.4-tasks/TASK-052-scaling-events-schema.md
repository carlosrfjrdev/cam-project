---
template: TASK
task_id: TASK-052
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.16]
covers_ca: [CA-H2.5]
features: [F-15e]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-050]
---

# TASK-052 — Migration `cam_constitutional_scaling_events`

## TDD First (Red)

1. `test_migration_creates_table_with_all_event_types_check_constraint`
2. `test_event_types_exact_set` — `ELIGIBILITY_COMPUTED, ELIGIBILITY_READY, PROPOSED, APPROVED, REVOKED, IN_FORCE, AUTO_REVERTED, SOFT_KILL_SWITCH, BLOCKED_ATTEMPT`.
3. `test_evidence_json_is_jsonb_indexed_for_gin_query`
4. `test_index_on_strategy_id_plus_ts_for_history_query`
5. `test_repository_insert_and_query_round_trip`

## Implementação alvo (Green)

```sql
CREATE TABLE cam_constitutional_scaling_events (
  id UUID PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN (
    'ELIGIBILITY_COMPUTED','ELIGIBILITY_READY','PROPOSED','APPROVED',
    'REVOKED','IN_FORCE','AUTO_REVERTED','SOFT_KILL_SWITCH','BLOCKED_ATTEMPT'
  )),
  strategy_id UUID,
  proposed_limit_win INT,
  proposed_limit_wdo INT,
  evidence_json JSONB,
  cooldown_days INT,
  cooldown_ends_at TIMESTAMPTZ,
  notes TEXT
);
CREATE INDEX ON cam_constitutional_scaling_events (strategy_id, ts DESC);
CREATE INDEX ON cam_constitutional_scaling_events USING GIN (evidence_json);
```

## Não-objetivos

- ❌ Lógica (T054).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- Migration + repository + 5 testes verdes.

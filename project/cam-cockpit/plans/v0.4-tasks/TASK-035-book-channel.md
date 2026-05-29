---
template: TASK
task_id: TASK-035
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.01]
covers_ca: [CA-G.1]
features: [F-20]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-009]
---

# TASK-035 — Canal `mt5.book` + populador `cam_market_book_snapshots`

## TDD First (Red)

1. `test_bridge_publishes_book_event_with_5_bids_5_asks`
2. `test_subscriber_persists_snapshot_in_hypertable`
3. `test_subscriber_handles_partial_book_lt_5_levels_gracefully`
4. `test_subscriber_indexed_query_returns_book_for_given_ts`

## Implementação alvo (Green)

- Editar: `cam_bridge.mq5` — adicionar publicação no canal PUB `mt5.book` (DOM_PRICE callback do MT5).
- Backend: `cam/features/market_data/book_subscriber.py` consumindo e persistindo em `cam_market_book_snapshots` (hypertable já existe).

## Não-objetivos

- ❌ Cross-asset correlation (T037).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Patch MQL5 + subscriber + 4 testes verdes.

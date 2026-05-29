---
template: TASK
task_id: TASK-021
block: BL-D
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R4.02]
covers_ca: [CA-D.1]
features: [F-10]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-020]
---

# TASK-021 — `POST /api/v1/carteira-hard/holdings`

## TDD First (Red)

1. `test_post_creates_holding_with_source_MANUAL_UI`
2. `test_post_rejects_invalid_ticker_format`
3. `test_post_rejects_quantity_zero_or_negative_with_422`
4. `test_post_accepts_source_in_MANUAL_UI_or_GENIAL_IMPORT_only`
5. `test_post_returns_holding_with_id_and_hash`
6. `test_get_lists_all_holdings_ordered_by_ticker`

## Implementação alvo (Green)

- Arquivo: `cam/features/ledger/holdings_router.py` — `POST` + `GET`.
- Pydantic schemas: `HoldingIn`, `HoldingOut`.

## Não-objetivos

- ❌ Importer Genial (T022).
- ❌ UI (T024).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Router + schemas + 6 testes verdes.

---
template: TASK
task_id: TASK-022
block: BL-D
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R4.03]
covers_ca: [CA-D.2, CA-D.3]
features: [F-10b]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-014, TASK-020]
---

# TASK-022 — Integração Genial Importer → Holdings

## Objetivo

Plugar `genial_importer` (T014) → `cam_carteira_hard_holdings` com **dedup por hash**.

## TDD First (Red)

1. `test_import_5_ticker_csv_creates_5_holdings_with_source_GENIAL_IMPORT`
2. `test_reimport_same_csv_creates_zero_new_holdings` — CA-D.3.
3. `test_import_merges_duplicate_ticker_into_avg_price` — se já existe, recalcula `avg_price` ponderado.
4. `test_import_emits_audit_per_holding`
5. `test_import_handles_malformed_row_with_skip_and_warning`

## Implementação alvo (Green)

- Arquivo: `cam/features/ledger/genial_holdings_service.py::import_holdings(parsed)`.
- Consome `ParsedExtrato` (T014); insere/merge em `cam_carteira_hard_holdings`.

## Não-objetivos

- ❌ Operações fiscais sobre import (vem em SPEC futura).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Service + 5 testes verdes.

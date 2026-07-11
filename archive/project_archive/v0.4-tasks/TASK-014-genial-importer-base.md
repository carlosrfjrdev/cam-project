---
template: TASK
task_id: TASK-014
block: BL-B
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R2.06]
covers_ca: [CA-B.1]
features: [F-10b]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-012]
---

# TASK-014 — Importer Genial CSV extrato (base)

## Objetivo

Parser dedicado para extrato CSV da Genial Investimentos (R-17), produzindo registros que **podem alimentar** holdings (BL-D, T022) **ou** provenance de ticks/operações.

## TDD First (Red)

1. `test_parser_reads_genial_csv_header_correctly`
2. `test_parser_extracts_holdings_rows_with_ticker_quantity_avg_price`
3. `test_parser_rejects_invalid_csv_format_with_clear_error`
4. `test_parser_handles_brazilian_decimal_separator_comma` — `35,50` → `35.50`.
5. `test_parser_emits_provenance_record_with_source=GENIAL_IMPORT`
6. `test_parser_idempotent_via_file_hash`

## Implementação alvo (Green)

- Arquivo: `cam/features/ledger/genial_importer.py::parse_extrato(file) -> ParsedExtrato`
- `ParsedExtrato` carrega `provenance, holdings_rows, trades_rows` (separação para que T022 consuma só holdings).
- **Discovery na PLAN:** se layout não estiver documentado, T014 entra com fixture sintética + fallback manual marcado como `requires_layout_confirmation=True`.

## Não-objetivos

- ❌ Importar para o banco (T022 faz).
- ❌ Mapear todos os campos da Genial (apenas mínimo necessário para holdings).

## Marcadores

- `sec`: false.
- `qa-sec`: true (parsing externo — Kevin valida sanitização).

## Saídas

- `genial_importer.py` + 6 testes verdes + fixture CSV em `tests/fixtures/genial_extrato_sample.csv`.

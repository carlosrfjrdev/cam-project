---
template: TASK
task_id: TASK-062
block: BL-I
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R9.05]
covers_ca: [CA-I.4]
features: [F-18]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-011]
---

# TASK-062 — Instrument Catalog ≥ 200 ativos

## Objetivo

Carregar **catálogo amplo** (≥ 200 ativos) via importação CSV. Ativação por demanda — `active=false` por default.

## TDD First (Red)

1. `test_import_csv_creates_at_least_200_instruments`
2. `test_each_instrument_has_required_fields_point_value_tick_size_contract_size`
3. `test_default_active_false_for_imported_instruments`
4. `test_reimport_same_csv_is_idempotent`
5. `test_activate_instrument_endpoint_sets_active_true_and_emits_audit`

## Implementação alvo (Green)

- Script: `scripts/import_instruments.py CSV_PATH`.
- Endpoint: `POST /api/v1/instruments/{ticker}/activate`.
- Fixture CSV em `data/seeds/b3_instruments_200.csv`.

## Não-objetivos

- ❌ Cotação ao vivo dos 200 (vem por demanda).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Script + endpoint + 5 testes verdes + seed CSV.

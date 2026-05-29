---
template: TASK
task_id: TASK-011
block: BL-B
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R2.01, R2.05]
covers_ca: [CA-B.1, CA-B.4]
features: [F-19, F-33]
status: Completed
sec: false
qa_sec: true
predecessors: []
---

# TASK-011 — Migrations `cam_market_data_provenance` + `cam_instruments`

## Objetivo

Criar **schema canônico de provenance** + **Instrument Catalog mínimo** (WIN/WDO/IND/DOL pré-populados).

## TDD First (Red)

1. `test_migration_creates_cam_market_data_provenance_with_all_columns`
2. `test_migration_creates_cam_instruments_with_seed_WIN_WDO_IND_DOL`
3. `test_provenance_hash_field_is_unique` — dedup futuro depende disso.
4. `test_instruments_point_value_correct_for_WIN_020_and_WDO_1000` — CA-B.4.
5. `test_migration_rollback_clean` — `alembic downgrade` deixa banco em estado anterior.

## Implementação alvo (Green)

- Migration `cam_market_data_provenance(import_id UUID PK, source TEXT, source_url TEXT, asset TEXT, ts_origin_min TIMESTAMPTZ, ts_origin_max TIMESTAMPTZ, ts_ingestion TIMESTAMPTZ, tick_count BIGINT, hash TEXT UNIQUE, quality_flags JSONB, license_terms_ack BOOLEAN)`.
- Migration `cam_instruments(ticker TEXT PK, asset_class TEXT, exchange TEXT, contract_size NUMERIC, tick_size NUMERIC, point_value NUMERIC, active BOOLEAN)`.
- Seed: `INSERT INTO cam_instruments` para `WIN, WDO, IND, DOL` com `point_value` corretos (0.20 / 10.00 / 1.00 / 10.00).

## Não-objetivos

- ❌ Ingestão (T012).
- ❌ Quality flags computation (T013).
- ❌ Catalog amplo 200+ (T062).

## Marcadores

- `sec`: false.
- `qa-sec`: true (parsing externo depende desse schema).

## Saídas

- 2 migrations + 5 testes verdes.

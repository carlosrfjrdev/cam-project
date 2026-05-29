---
template: TASK
task_id: TASK-012
block: BL-B
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R2.02, R2.03]
covers_ca: [CA-B.1, CA-B.2]
features: [F-04, F-19]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-011]
---

# TASK-012 — `market_data.service.ingest_ticks` + dedup hash

## Objetivo

Ingerir ticks com **provenance obrigatório** e dedup determinístico por hash `(asset, ts, price, volume)`.

## TDD First (Red)

1. `test_ingest_registers_provenance_before_ticks` — provenance row criada antes dos ticks.
2. `test_ingest_produces_N_ticks_in_cam_market_ticks`
3. `test_reingest_same_file_produces_zero_duplicates` — CA-B.2.
4. `test_ingest_fails_when_license_terms_ack_false` — Tos não aceito → `LicenseNotAck`.
5. `test_ingest_emits_audit_event_with_hash`
6. `test_ingest_partial_failure_rolls_back_provenance_and_ticks` — atomicidade.

## Implementação alvo (Green)

- Arquivo: `cam/features/market_data/service.py::ingest_ticks(file, source_metadata)`
- Parser HTML/CSV do MT5 (reuso do importer SPEC v0.2) + dedup por hash em DB.
- Idempotency: hash do arquivo + hash dos ticks; reimport produz 0 duplicados.

## Não-objetivos

- ❌ Genial CSV específico (T014).
- ❌ Quality flags (T013).

## Marcadores

- `sec`: false.
- `qa-sec`: true.

## Saídas

- `service.py` + 6 testes verdes.

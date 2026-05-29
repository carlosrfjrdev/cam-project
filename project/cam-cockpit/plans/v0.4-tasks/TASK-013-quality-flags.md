---
template: TASK
task_id: TASK-013
block: BL-B
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R2.04]
covers_ca: [CA-B.3]
features: [F-19]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-012]
---

# TASK-013 — Quality flags computation

## Objetivo

Computar `has_gaps`, `has_zero_volume`, `out_of_hours` após cada `ingest_ticks` e persistir em `cam_market_data_provenance.quality_flags`.

## TDD First (Red)

1. `test_has_gaps_true_when_tick_interval_exceeds_threshold` — fixture com 5min de gap em WIN intraday.
2. `test_has_gaps_false_for_continuous_data`
3. `test_has_zero_volume_true_when_any_tick_volume_zero`
4. `test_out_of_hours_true_for_ticks_outside_pregao_window` — WIN pregão B3 09:00-18:00 BRT.
5. `test_flags_persisted_in_jsonb_correctly`

## Implementação alvo (Green)

- Arquivo: `cam/features/market_data/quality.py::compute_quality_flags(ticks, asset) -> dict`.
- Thresholds: gap > 60s intraday (configurável por `cam_instruments.expected_max_gap_s`).
- Pregão windows lidos de `cam_instruments` (extender schema com `pregao_open_time`, `pregao_close_time`).

## Não-objetivos

- ❌ Auto-fix de gaps.
- ❌ Validações regulatórias profundas (apenas sinalização).

## Marcadores

- `sec`: false.
- `qa-sec`: true.

## Saídas

- `quality.py` + 5 testes verdes.

---
task_id: TASK-U018
block: BL-UI-3
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU3.03]
covers_ca: [CA-U3.3]
status: Done
sec: false
qa_sec: true
predecessors: [TASK-U008, TASK-U010]
---

# TASK-U018 — Tela Market Data / Provenance

## Objetivo
`features/market-data/MarketDataPage.tsx` — lotes ingeridos (provenance: fonte, ts, tick_count, hash, quality_flags) + catálogo de instrumentos.

## TDD First (Red — Vitest+RTL)
1. `test_lists_provenance_with_quality_flags` — has_gaps/zero_volume/out_of_hours visíveis.
2. `test_lists_instruments` — WIN/WDO com point_value.
3. `test_quality_flag_warning_styling` — flags problemáticas destacadas.

## Green
- Página + `useMarketData` → `GET /market-data/provenance|instruments`. Rota `/market-data`.

## Não-objetivos
- ❌ Endpoint (U008). ❌ ingestão (já v0.4).

## Marcadores
- `sec`: false · `qa-sec`: true.

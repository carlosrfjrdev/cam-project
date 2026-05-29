---
template: TASK
task_id: TASK-034
block: BL-F
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R6.05]
covers_ca: [CA-F.2]
features: [F-26]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-032]
---

# TASK-034 — Multi-Source Collector — esqueleto + 1 fonte placeholder

## Objetivo

Arquitetura preparada para fontes múltiplas (StatusInvest, Fundamentus, etc.) — entrega esqueleto + 1 fonte placeholder. **Fontes reais e ToS ficam em TD-v0.4-01.**

## TDD First (Red)

1. `test_collector_interface_defines_fetch_and_normalize`
2. `test_placeholder_source_returns_fixture_data_for_1_ticker`
3. `test_collector_persists_in_cam_fundamentals_snapshot_with_correct_source`
4. `test_collector_dedup_by_hash`
5. `test_collector_emits_provenance_event`

## Implementação alvo (Green)

- Arquivo: `cam/features/fundamentals/multi_source_collector.py` — Protocol `FundamentalsSource`.
- Arquivo: `cam/features/fundamentals/sources/placeholder_source.py` — retorna fixture estática.
- Sem rede em CI; integração real é TD-v0.4-01.

## Não-objetivos

- ❌ Scraping real (TD-v0.4-01 explícito).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Esqueleto + placeholder + 5 testes verdes.

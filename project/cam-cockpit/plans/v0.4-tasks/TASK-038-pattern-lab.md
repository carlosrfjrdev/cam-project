---
template: TASK
task_id: TASK-038
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.02]
covers_ca: []
features: [F-23]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-037]
---

# TASK-038 — `research/pattern_lab.py` (estatístico — sem ML quant)

## Objetivo

Busca de padrões estatísticos cross-asset (ex.: "queda ≥ 1% em 5 ativos consecutivos puxa WIN no dia seguinte?") — **sem** ML quant ainda.

## TDD First (Red)

1. `test_pattern_search_returns_matches_with_pvalue`
2. `test_pattern_search_handles_no_matches_gracefully`
3. `test_pattern_search_filters_by_min_occurrences`
4. `test_pattern_serializable_to_json_for_workbench`

## Implementação alvo (Green)

- Arquivo: `cam/features/research/pattern_lab.py::search_patterns(spec, ts_from, ts_to) -> PatternSearchResult`.

## Não-objetivos

- ❌ ML quant (Out — `sklearn/torch sem LLM` é Later).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Módulo + 4 testes verdes.

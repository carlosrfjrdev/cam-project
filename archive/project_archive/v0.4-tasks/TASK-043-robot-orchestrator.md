---
template: TASK
task_id: TASK-043
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.01]
covers_ca: [CA-H1.1]
features: [F-15]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-006, TASK-042]
---

# TASK-043 — `robot_orchestrator/orchestrator.py`

## Objetivo

Lê tick → distribui para todas as estratégias ativas do Robot → coleta candidatos → invoca conflict_resolver (T044) → submete vencedor(es) via Order Gateway.

## TDD First (Red)

1. `test_orchestrator_routes_tick_to_all_active_strategies`
2. `test_orchestrator_skips_suspended_strategy` — `is_suspended=true` via gain lock individual (T048) ou aderência < 95% (R8.02).
3. `test_orchestrator_collects_candidates_into_single_list`
4. `test_orchestrator_passes_candidates_to_conflict_resolver`
5. `test_orchestrator_submits_only_resolved_winners_via_gateway`
6. `test_orchestrator_emits_audit_per_round`
7. `test_orchestrator_handles_single_strategy_unchanged_when_flag_false` — `MULTI_STRATEGY_ENABLED=false` ⇒ comportamento legacy.

## Implementação alvo (Green)

- Arquivo: `cam/features/robot_orchestrator/orchestrator.py::tick_handler(tick, robot)`.

## Não-objetivos

- ❌ Lógica do conflict resolver (T044). ❌ Aggregate risk (T045).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- `orchestrator.py` + 7 testes verdes.

---
template: TASK
task_id: TASK-059
block: BL-I
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R9.02]
covers_ca: [CA-I.1, CA-I.2]
features: [F-14]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-058]
---

# TASK-059 — `mt5_integration/multi_ea_manager.py`

## Objetivo

Orquestra **múltiplas conexões ZeroMQ**. Garante mutex de execução: ambos EAs podem publicar tick, mas Order Gateway processa em série (CA-I.2).

## TDD First (Red)

1. `test_manager_subscribes_to_all_active_EAs`
2. `test_manager_handles_simultaneous_tick_from_2_EAs_serial_dispatch`
3. `test_manager_routes_SUBMIT_ORDER_to_correct_EA_by_asset`
4. `test_manager_detects_offline_EA_via_heartbeat_and_marks_disabled`
5. `test_property_based_no_deadlock_with_2_EAs_concurrent_requests` — Hypothesis 1000 cenários.

## Implementação alvo (Green)

- Arquivo: `cam/features/mt5_integration/multi_ea_manager.py::MultiEAManager`.
- Mutex via `asyncio.Lock()` no Order Gateway.

## Não-objetivos

- ❌ DSL (T060/T061).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- Manager + 5 testes verdes.

---
template: TASK
task_id: TASK-042
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
predecessors: [TASK-002]
---

# TASK-042 — `robot_orchestrator/domain.py` (Robot model)

## Objetivo

Materializar **Robot = Estratégia(s) + Configuração + Ambiente + Modo de Autonomia** (G-R02.01). NÃO é IA.

## TDD First (Red)

1. `test_robot_can_aggregate_multiple_strategies_with_priority`
2. `test_robot_metadata_carries_env_and_mode`
3. `test_robot_cannot_have_zero_strategies_raises`
4. `test_robot_priority_is_strict_ordering_no_ties` — dois com mesma prioridade → `AmbiguousPriority`.
5. `test_robot_serializable_via_repository`

## Implementação alvo (Green)

- Arquivo: `cam/features/robot_orchestrator/domain.py` — `Robot`, `StrategyAssignment(strategy_id, priority)`, `RobotEnv`, `RobotMode`.

## Não-objetivos

- ❌ Orquestração runtime (T043). ❌ Conflict resolver (T044).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- `domain.py` + 5 testes verdes.

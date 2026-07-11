---
template: TASK
task_id: TASK-058
block: BL-I
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R9.01]
covers_ca: [CA-I.1]
features: [F-14]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-009, TASK-030]
---

# TASK-058 — `cam_bridge.mq5` v2.0 multi-instance + EA_ID + porta REQ/REP única

## Objetivo

Suporte a **N instâncias do EA** (uma por gráfico/ativo). Cada instância tem `EA_ID` único + porta REQ/REP única (`5557 + offset`).

## TDD First (Red)

1. `test_two_instances_get_distinct_ports_5557_and_5558`
2. `test_two_instances_publish_to_distinct_pub_channels_with_EA_ID_prefix`
3. `test_kill_switch_propagates_to_ALL_instances_simultaneously`
4. `test_ea_id_persisted_in_log_lines`
5. `test_instance_collision_on_same_port_raises_StartupError`

## Implementação alvo (Green)

- Editar: `cam_bridge.mq5` — parametrizar `EA_ID` (input do MT5) + offset de porta.
- Channels PUB: `mt5.{ea_id}.tick`, `mt5.{ea_id}.fill`, `mt5.{ea_id}.book`.

## Não-objetivos

- ❌ Multi-EA manager Python (T059).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- `cam_bridge.mq5` v2.0 + 5 testes verdes.

---
template: TASK
task_id: TASK-030
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.05]
covers_ca: [CA-E.5]
features: [F-12]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-027]
---

# TASK-030 — `KILL_SWITCH_ACTIVATE` propagation E2E (Art. 18)

## Objetivo

Comando `KILL_SWITCH_ACTIVATE` propaga do cockpit → bridge → EA em < 2s. EA cancela ordens pendentes + para `OnTick` (Art. 18º).

## TDD First (Red)

1. `test_kill_switch_command_propagates_to_ea_in_under_2s` — cronometrar.
2. `test_kill_switch_cancels_all_pending_orders_in_mt5`
3. `test_kill_switch_stops_ontick_in_ea`
4. `test_kill_switch_persists_event_with_actor_and_reason`
5. `test_kill_switch_blocks_subsequent_SUBMIT_ORDER_until_RESUME` — kill switch é sticky.
6. **E2E DEMO:** ativar via cockpit UI, verificar no MT5 Genial DEMO.

## Implementação alvo (Green)

- Editar: `cam_bridge.mq5` — adicionar `KILL_SWITCH_ACTIVATE` na whitelist + cancel pending + flag interna `kill_switch_active`.
- Endpoint cockpit: `POST /api/v1/kill-switch/global`.
- UI: botão vermelho persistente em todas as telas operacionais (banner SR consistente).

## Não-objetivos

- ❌ Kill switch paper (T017 já cobre).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Comando MQL5 + endpoint + UI + 6 testes (5 unit + 1 E2E).

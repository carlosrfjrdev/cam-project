---
template: TASK
task_id: TASK-028
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.03]
covers_ca: [CA-E.2]
features: [F-31]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-006, TASK-027]
---

# TASK-028 — Order Gateway via REQ/REP `SUBMIT_ORDER` (timeout 2s)

## Objetivo

`EADispatcher` em `gateway.py` envia `SUBMIT_ORDER` via ZeroMQ REQ/REP com timeout 2s.

## TDD First (Red)

1. `test_dispatcher_sends_SUBMIT_ORDER_via_reqrep`
2. `test_dispatcher_timeout_2s_raises_BridgeTimeout` — mock bridge silenciosa.
3. `test_dispatcher_propagates_OrderResult_back_to_gateway`
4. `test_dispatcher_blocks_when_bridge_OFFLINE` — heartbeat ausente → `BridgeOfflineError`.
5. `test_dispatcher_emits_audit_with_full_request_response_payload`

## Implementação alvo (Green)

- Arquivo: `cam/features/mt5_integration/ea_dispatcher.py::send_submit_order(intent, idempotency_key)`.
- Editar: `gateway.py::submit` para usar `EADispatcher` quando `env in {demo, real}` (e flags permitirem).

## Não-objetivos

- ❌ Subscriber para `mt5.fill` (T029).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- `ea_dispatcher.py` + 5 testes verdes.

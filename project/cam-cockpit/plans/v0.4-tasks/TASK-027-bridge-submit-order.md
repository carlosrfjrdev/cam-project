---
template: TASK
task_id: TASK-027
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.01]
covers_ca: [CA-E.2, CA-E.3]
features: [F-12]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-009, TASK-025]
---

# TASK-027 — `cam_bridge.mq5` `SUBMIT_ORDER` (DEMO + idempotency)

> **CRÍTICO** — primeiro caminho de envio de ordem na história do CaM, mesmo que apenas DEMO.

## TDD First (Red)

1. `test_submit_order_rejected_when_account_is_REAL` — EA verifica `ACCOUNT_TRADE_MODE != DEMO` → reject.
2. `test_submit_order_rejected_when_account_in_REAL_TRADING_ACCOUNTS_allowlist` — paradoxo intencional: comando DEMO não opera real.
3. `test_submit_order_with_repeated_idempotency_key_returns_DUPLICATE_INTENT`
4. `test_submit_order_calls_cam_risk_mirror_BEFORE_OrderSend` — paridade enforçada.
5. `test_submit_order_propagates_OrderSend_result_back_via_REP`
6. `test_unknown_subcommand_not_in_whitelist_rejected`
7. **E2E DEMO:** envio real em MT5 Genial DEMO + retorno fill em < 2s.

## Implementação alvo (Green)

- Editar: `apps/cam-cockpit/mql5/cam_bridge.mq5` — adicionar handler `SUBMIT_ORDER` na whitelist.
- Verificações na ordem:
  1. `ACCOUNT_TRADE_MODE == DEMO`
  2. `account_login NOT IN REAL_TRADING_ACCOUNTS`
  3. `idempotency_key` válido (cache local 60s)
  4. Chama `cam_risk_mirror.mq5::evaluate(intent)` → se reprovar, devolve com motivo
  5. Só então `OrderSend(...)`

## Não-objetivos

- ❌ Conexão Python (T028).
- ❌ Fill handling (T029).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- `cam_bridge.mq5` com `SUBMIT_ORDER` + 7 testes verdes + integração DEMO funcional.

---
template: TASK
task_id: TASK-016
block: BL-C
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R3.01, R3.03]
covers_ca: [CA-C.1]
features: [F-07]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-006, TASK-007, TASK-012, TASK-015]
---

# TASK-016 — `paper_trading.service.loop_governed`

## Objetivo

Loop completo: replay de ticks → `strategy.evaluate` → Order Gateway (env=paper) → persistência em `cam_paper_trades`. **Primeiro robô funcional em paper.**

## TDD First (Red)

1. `test_loop_replay_ticks_in_chronological_order`
2. `test_loop_invokes_strategy_evaluate_per_tick`
3. `test_loop_submits_only_through_order_gateway_never_directly`
4. `test_loop_persists_paper_trade_on_close`
5. `test_loop_computes_adherence_per_trade` — `1.0` se Risk approved + estratégia respeitou params; `0.0` em violação.
6. `test_loop_handles_strategy_returning_None_without_error`
7. `test_loop_emits_audit_per_intent`
8. **End-to-end:** Loop S1 ORB sobre 1 dia de tick WIN → ≥ 1 paper trade aprovado pelo Risk Engine (`CA-C.1`).

## Implementação alvo (Green)

- Arquivo: `cam/features/paper_trading/service.py::loop_governed(strategy_id, ts_from, ts_to)`.
- Consome `cam_market_ticks` em chunks; mantém estado de posição aberta; chama `order_gateway.submit(env="paper", mode="full", ...)`.

## Não-objetivos

- ❌ Kill switch (T017).
- ❌ AI Collector (T018).

## Marcadores

- `sec`: true.
- `qa-sec`: true.

## Saídas

- `service.py` + 8 testes (7 unitários + 1 E2E).

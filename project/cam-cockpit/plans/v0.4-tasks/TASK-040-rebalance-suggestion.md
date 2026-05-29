---
template: TASK
task_id: TASK-040
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.04]
covers_ca: [CA-G.4]
features: [F-25]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-033]
---

# TASK-040 — `ledger/rebalance.py` (sugestão — nunca executa, R-13)

## TDD First (Red)

1. `test_suggest_returns_actions_list_buy_sell` — "vender 50 PETR4, comprar 100 ITUB4".
2. `test_suggest_never_calls_order_gateway_or_holdings_writer` — propriedade enforçada via mock que falha se chamado.
3. `test_suggest_outputs_serializable_via_telegram_and_ui`
4. `test_suggest_respects_DY_target_from_pov`
5. `test_suggest_empty_when_no_rebalance_needed`

## Implementação alvo (Green)

- Arquivo: `cam/features/ledger/rebalance.py::suggest_rebalance(holdings, fundamentals, targets) -> RebalanceSuggestion`.
- Sem side effects.

## Não-objetivos

- ❌ Execução (Art. 23 + R-13).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Módulo + 5 testes verdes.

---
template: TASK
task_id: TASK-006
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.07]
covers_ca: [CA-A.7, CA-A.8]
features: [F-31]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-002, TASK-004, TASK-005]
---

# TASK-006 — Order Gateway único (`submit`)

## Objetivo

Criar **único caminho de ordem** do CaM: `Strategy/Robot → Risk Engine → submit() → EA/Paper Dispatch`. Tudo que toca ordem **DEVE** passar aqui.

## TDD First (Red)

1. `test_submit_rejects_when_REAL_TRADING_ALLOWED_false_and_env_real` — retorna `RealTradingDisabled`.
2. `test_submit_blocks_when_autonomy_matrix_returns_false`
3. `test_submit_calls_risk_validate_before_dispatch` — mock `risk_validate` é invocado; se retorna `Rejected`, dispatch não acontece.
4. `test_submit_idempotency_key_blocks_duplicate` — mesma `idempotency_key` em < 60s ⇒ `DuplicateIntent`.
5. `test_submit_audit_log_emitted_on_every_call` — Approved E Rejected geram registro.
6. `test_submit_dispatch_paper_when_env_paper` — paper handler chamado, não EA.
7. `test_submit_dispatch_ea_when_env_demo_or_real` — apenas se Autonomy + Risk + flag = ok.
8. `test_submit_returns_OrderResult_with_decision_metadata`
9. **Property-based:** Hypothesis gera 5.000 combinações `(env, mode, status, contracts, asset)` — Order Gateway **nunca** dispatch sem `risk_validate` aprovado. Falha = bug crítico.

## Implementação alvo (Green)

- Arquivo: `cam/_shared/order_gateway/gateway.py`
- Função pública `async submit(intent, env, mode, strategy_id, idempotency_key) -> OrderResult`.
- Ordem **obrigatória**:
  ```
  autonomy_check → real_trading_flag_check → idempotency_check
    → risk_validate (chama 18 validators) → audit → dispatch
  ```
- Dispatch pluggable (`PaperDispatcher`, `EADispatcher` — T028 implementa EA real).
- Para BL-A entregue: `PaperDispatcher` retorna `OrderResult(success=True, simulated=True)`; `EADispatcher` levanta `NotImplementedError` (BL-E completa em T028).

## Não-objetivos

- ❌ Submeter ordem real ao MT5 (T028, BL-E).
- ❌ Loop paper (T016).
- ❌ Aggregate risk Art. 11-A (T045, BL-H1).

## Marcadores

- `sec`: **true CRÍTICO** — Order Gateway é a artéria do CaM.
- `qa-sec`: **true CRÍTICO** — property-based obrigatório.

## Saídas

- `gateway.py` + 9 testes (8 unitários + 1 property-based 5k cenários).
- Grep `risk_validate(` no codebase: aparece **apenas** em `gateway.py` e em testes. Outras ocorrências = warning de lint (CA-A.7).

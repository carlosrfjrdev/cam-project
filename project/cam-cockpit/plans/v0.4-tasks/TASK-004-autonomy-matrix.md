---
template: TASK
task_id: TASK-004
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.04]
covers_ca: [CA-A.4]
features: [F-13]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-001]
---

# TASK-004 — Autonomy Matrix `is_mode_allowed`

## Objetivo

Implementar `is_mode_allowed(env, mode, strategy_status) → bool` enforçando a tabela G-R02.03 da SPEC.

## TDD First (Red)

1. `test_backtest_allows_signal_semi_full_blocks_one_click`
2. `test_paper_allows_all_modes`
3. `test_demo_semi_full_require_demo_ok_status` — `(env=demo, mode=full, status=paper_ok)` ⇒ `False`.
4. `test_real_full_blocked_until_real_authorized_AND_gate` — mesmo com `real_authorized`, retorna `False` até gate Founder (audit log).
5. `test_real_one_click_conditioned_forte_requires_30d_cooldown_and_signature` — testar com `context.cooldown_passed=False` ⇒ `False`.
6. Parametrizado com **todas as 16 combinações da matriz** (4 envs × 4 modes), comparando contra tabela canônica.

## Implementação alvo (Green)

- Arquivo: `cam/_shared/autonomy/matrix.py` (shared kernel — Vint kernel-allowed).
- Função: `is_mode_allowed(env, mode, strategy_status, context: AutonomyContext) -> AutonomyDecision` (decisão com motivo).
- `AutonomyContext` carrega flags `cooldown_passed`, `signature_present`, `real_trading_allowed`.

## Não-objetivos

- ❌ Implementar fluxo de cooldown 30d (esse vive na própria Constituição via POV).
- ❌ Assinatura simbólica do Founder (sai em SPEC futura — somente expor o slot).

## Marcadores

- `sec`: true.
- `qa-sec`: true (matriz é defesa explícita contra "full automatic" prematura).

## Saídas

- `matrix.py` + 16 testes paramétricos verdes.

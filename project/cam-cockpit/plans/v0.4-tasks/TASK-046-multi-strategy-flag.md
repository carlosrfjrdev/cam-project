---
template: TASK
task_id: TASK-046
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.03]
covers_ca: [CA-H1.1]
features: [F-15]
status: Completed
sec: true
sec_critical: true
qa_sec: true
predecessors: [TASK-042]
---

# TASK-046 — Flag `MULTI_STRATEGY_ENABLED` + ativação rastreada

## Objetivo

Ativar `MULTI_STRATEGY_ENABLED` requer: (a) BL-H1 entregue (T042..T045 verdes), (b) ≥ 1 estratégia com aderência individual ≥ 95% em 30 pregões, (c) FEATURE-FLAGS-LEDGER entrada #003 atualizada de `false` para `true` com aprovador Founder.

## TDD First (Red)

1. `test_default_MULTI_STRATEGY_ENABLED_false` — entrada #003 vigente.
2. `test_activation_rejected_when_no_strategy_meets_95_adherence_30d`
3. `test_activation_emits_audit_with_actor_Founder_and_timestamp`
4. `test_activation_requires_ledger_entry_correction_pattern` — toggle vira nova linha (append-only).
5. `test_deactivation_does_not_remove_history`

## Implementação alvo (Green)

- Editar: `cam/_shared/config/__init__.py` — adicionar `MULTI_STRATEGY_ENABLED: bool = False`.
- Endpoint admin: `POST /api/v1/admin/flags/multi-strategy/toggle` — valida pré-condições + persiste ledger.

## Não-objetivos

- ❌ Lint anti auto-edição (T047).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true.

## Saídas

- Flag + endpoint + 5 testes verdes.

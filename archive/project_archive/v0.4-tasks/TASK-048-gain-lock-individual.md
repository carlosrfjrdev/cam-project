---
template: TASK
task_id: TASK-048
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.05]
covers_ca: [CA-H1.8]
features: [F-15]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-043]
---

# TASK-048 — Gain lock individual por estratégia (POV §3.13 — recomendação Mammon)

## Objetivo

Se estratégia individual atinge **5% do capital** no dia, é **suspensa** do orquestrador pelo resto do pregão. Outras estratégias seguem operando.

## TDD First (Red)

1. `test_strategy_individual_gain_5pct_suspends_only_that_strategy_until_eod`
2. `test_other_strategies_continue_operating`
3. `test_suspension_persisted_in_cam_strategy_runtime_state` — flag `is_suspended` + `suspended_until_ts`.
4. `test_suspension_emits_telegram_with_strategy_id_and_reason`
5. `test_suspension_resets_at_next_pregao_open`

## Implementação alvo (Green)

- Editar: `orchestrator.py` para consultar `is_suspended` antes de rotear tick.
- Job: ao fim do pregão, reseta flags em `cam_strategy_runtime_state`.

## Não-objetivos

- ❌ Gain lock agregado (POV §3.4 — já existe).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- Patch + 5 testes verdes.

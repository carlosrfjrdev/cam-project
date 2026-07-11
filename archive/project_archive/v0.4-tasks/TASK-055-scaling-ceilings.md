---
template: TASK
task_id: TASK-055
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.15]
covers_ca: [CA-H2.7]
features: [F-15c]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-050]
---

# TASK-055 — Tetos absolutos + cláusula de blindagem (Voltaire 3)

## Objetivo

Hardcoded em `scaling.py`:
- `MAX_SCALED_WIN = 5`
- `MAX_SCALED_WDO = 5`
- `MAX_DAILY_DRAWDOWN_PCT = 0.03` (Art. 16 — intocável)

**Cláusula de blindagem:** comentário hardcoded + nota em `PROTOCOLO-EMENDA-CONSTITUCIONAL.md` indicando que emendas mexendo nesses tetos **exigem revisão integral** (não protocolo simplificado v2.0).

## TDD First (Red)

1. `test_attempt_to_scale_WIN_above_5_raises_BLOCKED_BY_CEILING` — CA-H2.7.
2. `test_attempt_to_scale_WDO_above_5_raises_BLOCKED_BY_CEILING`
3. `test_daily_drawdown_above_3pct_triggers_immediate_kill_switch`
4. `test_blocked_attempt_persisted_as_BLOCKED_ATTEMPT_event_with_proposed_limit`
5. `test_constants_present_in_source_code_with_blindagem_comment` — sanity: comentário com "REVISÃO INTEGRAL" presente.
6. `test_lint_rejects_PR_modifying_ceilings_in_non_allowlisted_file` — reuso do lint T047.

## Implementação alvo (Green)

- Editar: `scaling.py` — declarar constants + comentário hardcoded.
- Editar: `PROTOCOLO-EMENDA-CONSTITUCIONAL.md` adicionar §X — "Cláusula de Blindagem".

## Não-objetivos

- ❌ Editar texto da Constituição (já foi feito na ratificação da emenda v2).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Constants + comentário + nota no protocolo + 6 testes verdes.

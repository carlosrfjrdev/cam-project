---
template: TASK
task_id: TASK-007
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.01]
covers_ca: [CA-A.1, CA-A.3]
features: [F-02]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-001]
---

# TASK-007 — S1 ORB 60m WIN — implementação concreta (R-18)

## Objetivo

Implementar a S1 ORB 60m WIN como **primeira estratégia plugável** no registry, seguindo `EDGE-THESIS-S1.md`.

## TDD First (Red)

1. `test_s1_orb_no_signal_during_opening_range_window` — primeiro 60 minutos não dispara entrada.
2. `test_s1_orb_long_entry_when_close_breaks_high_after_60m` — gera `OrderCandidate(direction=LONG)`.
3. `test_s1_orb_short_entry_when_close_breaks_low_after_60m`
4. `test_s1_orb_respects_max_contracts_from_context` — Strategy nunca infere limite; consome do `StrategyContext`.
5. `test_s1_orb_metadata_correct` — `asset='WIN'`, `version='1.0.0'`, `author='Carlos'`, `status='draft'` ao registrar.
6. `test_s1_orb_registered_in_registry_via_fixture` — após import, S1 está em `registry.list()`.

## Implementação alvo (Green)

- Arquivo: `cam/features/strategies/strategies/orb_60m_win.py`
- Classe `ORB60mWIN(Strategy)` com `evaluate(tick, context)`.
- Parâmetros declarados em `metadata.custom_metrics`: `opening_range_minutes=60`, `min_volume_multiplier=1.0`.
- Registrar via factory em `cam/features/strategies/strategies/__init__.py`.

## Não-objetivos

- ❌ Backtest engine (T008).
- ❌ Promoção paper_ok (T019).

## Marcadores

- `sec`: false (estratégia não toca infra sensível — Order Gateway que defende).
- `qa-sec`: true (regressão crítica do edge thesis).

## Saídas

- `orb_60m_win.py` + 6 testes verdes + S1 visível no `registry.list()` em `status='draft'`.

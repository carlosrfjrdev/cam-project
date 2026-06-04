---
template: TASK
task_id: TASK-018
block: BL-C
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R3.04]
covers_ca: [CA-C.3]
features: [F-09]
status: Completed
sec: false
qa_sec: true
predecessors: []
---

# TASK-018 — `AIAnalystDataCollector` consumindo dados reais

## Objetivo

Substituir retornos vazios por consulta real a `cam_journal_entries`, `cam_risk_decisions`, `cam_violations` por data — TD-016 resolvido.

## TDD First (Red)

1. `test_collect_returns_journal_entries_for_date`
2. `test_collect_returns_risk_decisions_for_date`
3. `test_collect_returns_violations_for_date`
4. `test_collect_returns_empty_lists_when_no_data_but_not_dict`
5. `test_collect_aggregates_metrics_correctly` — total trades, aderência média, drawdown do dia.
6. `test_run_daily_analysis_returns_non_empty_when_data_exists` — CA-C.3.

## Implementação alvo (Green)

- Editar: `cam/features/ai_analyst/data_collector.py` — repository pattern; remover `return []` placeholders.
- Adicionar agregadores em `analyst_service.py`.

## Não-objetivos

- ❌ Research Workbench (T039, BL-G).
- ❌ OpenAI provider (T041, TD-v0.4-02 bloqueia).

## Marcadores

- `sec`: false.
- `qa-sec`: true.

## Saídas

- Patch + 6 testes verdes + análise diária retorna conteúdo real.

---
template: TASK
task_id: TASK-039
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.03]
covers_ca: [CA-G.3]
features: [F-21]
status: Deferred-TechDebt
sec: false
qa_sec: true
predecessors: [TASK-018, TASK-037]
---

# TASK-039 — `ai_analyst/research_workbench.py` + Recharts UI

## TDD First (Red — backend)

1. `test_workbench_consumes_ticks_book_fundamentals_in_one_query`
2. `test_workbench_returns_structured_json_for_1_prompt`
3. `test_workbench_calls_LLM_provider_via_governance_layer` — passa por `cam_ai_provider_calls`.
4. `test_workbench_anonymizes_account_identifiers_in_prompt`

## TDD First (UI)

5. `test_workbench_page_renders_recharts_with_data`
6. `test_workbench_page_handles_loading_and_error_states`

## Implementação alvo (Green)

- Arquivo: `cam/features/ai_analyst/research_workbench.py::analyze(prompt, asset, ts_from, ts_to) -> AnalysisResult`.
- UI: `apps/cam-cockpit/frontend/src/features/research/WorkbenchPage.tsx` + componentes Recharts.

## Não-objetivos

- ❌ OpenAI (T041 — bloqueado por TD-v0.4-02).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Módulo + tela + 6 testes verdes.

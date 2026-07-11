---
task_id: TASK-U023
block: BL-UI-5
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU5.02]
covers_ca: [CA-U5.3]
status: Done
sec: false
qa_sec: true
predecessors: [TASK-U005, TASK-U010]
---

# TASK-U023 — Research / AI Workbench (Recharts)

## Objetivo
`features/research/ResearchPage.tsx` — visualização Recharts (correlação cross-asset, spread de pair trade) + output estruturado do AI Workbench (Anthropic/Ollama; OpenAI bloqueado).

## TDD First (Red — Vitest+RTL)
1. `test_renders_recharts_correlation`.
2. `test_renders_pair_trade_spread`.
3. `test_workbench_structured_output`.
4. `test_openai_shows_not_enabled` — `OpenAINotEnabled`.
5. `test_lazy_loaded_route` — bundle (Recharts) lazy.

## Green
- Página + `useResearch` → `/research/correlation|pair-trade-backtest|workbench`. Rota `/research` (lazy).

## Não-objetivos
- ❌ Endpoint (U005). ❌ habilitar OpenAI.

## Marcadores
- `sec`: false · `qa-sec`: true.

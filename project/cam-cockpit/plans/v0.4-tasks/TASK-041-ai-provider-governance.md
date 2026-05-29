---
template: TASK
task_id: TASK-041
block: BL-G
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R7.05]
covers_ca: [CA-G.5]
features: [F-30]
status: Completed
sec: false
qa_sec: true
predecessors: [TASK-018]
---

# TASK-041 — `cam_ai_provider_calls` + OpenAI bloqueado (TD-v0.4-02)

## TDD First (Red)

1. `test_migration_cam_ai_provider_calls_creates_table`
2. `test_provider_call_persists_anonymized_prompt_hash_and_response_hash`
3. `test_call_with_provider_OPENAI_raises_OpenAINotEnabled` — CA-G.5.
4. `test_call_with_provider_ANTHROPIC_or_OLLAMA_succeeds`
5. `test_provider_call_emits_telegram_when_response_flagged_sensitive`

## Implementação alvo (Green)

- Migration `cam_ai_provider_calls(id UUID, provider TEXT, model TEXT, prompt_hash TEXT, response_hash TEXT, anonymized BOOLEAN, ts TIMESTAMPTZ)`.
- Arquivo: `cam/features/ai_analyst/provider_governance.py::call_provider(provider, prompt, ...)`.
- OpenAI hard-rejected até ADR (TD-v0.4-02): `if provider == "openai": raise OpenAINotEnabled(...)`.

## Não-objetivos

- ❌ ADR OpenAI em si (TD-v0.4-02 → SPEC própria).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- Migration + módulo + 5 testes verdes.

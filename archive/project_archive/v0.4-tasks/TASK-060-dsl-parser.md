---
template: TASK
task_id: TASK-060
block: BL-I
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R9.03]
covers_ca: [CA-I.3]
features: [F-17]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-001]
---

# TASK-060 — `strategies/dsl/` parser YAML/JSON

## Objetivo

Parser de DSL declarativa (YAML/JSON) — formato exemplo da SPEC §13.1.

## TDD First (Red)

1. `test_parse_yaml_with_indicators_entry_exit_blocks`
2. `test_parse_rejects_invalid_indicator_type`
3. `test_parse_rejects_missing_required_fields_with_clear_error`
4. `test_parse_handles_trailing_stop_loss_expression`
5. `test_parse_outputs_normalized_AST` — independente do formato fonte.

## Implementação alvo (Green)

- Arquivo: `cam/features/strategies/dsl/parser.py::parse(file_or_dict) -> DSLAst`.
- `DSLAst` é dataclass que será consumida por compiler (T061).

## Não-objetivos

- ❌ Compilação para Python (T061).

## Marcadores

- `sec`: true (entrada externa). `qa-sec`: true.

## Saídas

- Parser + 5 testes verdes.

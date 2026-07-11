---
template: TASK
task_id: TASK-061
block: BL-I
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R9.04]
covers_ca: [CA-I.3]
features: [F-17]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-060]
---

# TASK-061 — DSL → Python canonical compiler

## Objetivo

Compilar DSL AST em classe `Strategy` válida em runtime. Persistir no registry com `compiled_from_dsl=true`.

## TDD First (Red)

1. `test_compile_produces_Strategy_subclass_matching_protocol`
2. `test_compiled_strategy_passes_same_tests_as_native_strategy` — paridade contra fixture.
3. `test_compiled_strategy_persists_in_registry_with_flag_compiled_from_dsl_true`
4. `test_compile_rejects_unsafe_expression` — guard contra eval injection (Kevin).
5. `test_compile_is_deterministic_same_AST_same_class_hash`

## Implementação alvo (Green)

- Arquivo: `cam/features/strategies/dsl/compiler.py::compile(ast) -> type[Strategy]`.
- Evitar `eval`/`exec`; usar AST controlado + restricted expression evaluator.

## Não-objetivos

- ❌ Runtime de orquestrador (já feito).

## Marcadores

- `sec`: true CRÍTICO (compilador de input externo). `qa-sec`: true.

## Saídas

- Compiler + 5 testes verdes.

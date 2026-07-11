---
template: TASK
task_id: TASK-056
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.17, R8.12]
covers_ca: [CA-H2.3]
features: [F-15h]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-050]
---

# TASK-056 — Flag `SCALING_ENABLED` + workflow `/escalonamentos/`

## Objetivo

- Flag `SCALING_ENABLED=false` default (entrada #004 já reservada no FEATURE-FLAGS-LEDGER).
- Workflow: operador cria arquivo `/project/cam-constitution/escalonamentos/ESC-NNN-YYYY-MM-DD.md` com schema do template.
- Sistema valida **incremento estrito +1** (recusa salto 2→4) — recomendação Marty.

## TDD First (Red)

1. `test_default_SCALING_ENABLED_false`
2. `test_activation_rejected_without_first_ESC_file_in_escalonamentos_dir`
3. `test_ESC_file_parser_extracts_strategy_evidence_and_new_limit`
4. `test_increment_validation_rejects_2_to_4_with_INCREMENTAL_VIOLATION` — CA-H2.3.
5. `test_increment_validation_accepts_2_to_3`
6. `test_ESC_file_signature_required_section_present`
7. `test_activation_emits_audit_with_ledger_correction_pattern`

## Implementação alvo (Green)

- Editar: `cam/_shared/config/__init__.py` — `SCALING_ENABLED: bool = False`.
- Arquivo: `cam/features/scaling/esc_parser.py::parse_esc_file(path) -> ScalingApplication`.
- Endpoint admin: `POST /api/v1/admin/scaling/apply` — recebe path do arquivo ESC, valida, persiste `APPROVED + IN_FORCE` em `cam_constitutional_scaling_events`.

## Não-objetivos

- ❌ Constituição (já alterada).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Flag + parser + endpoint + 7 testes verdes.

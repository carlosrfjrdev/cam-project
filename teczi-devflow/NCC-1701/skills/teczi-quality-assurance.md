---
skill: teczi-quality-assurance
phase: QA
status: draft
lead_persona: Linus
co_lead_persona: Kevin (QA-SEC)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-quality-assurance

## 1. Propósito

Validar qualidade funcional, regressão e segurança proporcional ao P/M/G e marcadores da SPEC. Três sub-naturezas: QA-CR (code review), QA-Func (funcional), QA-SEC (segurança).

## 2. Quando acionar

- CODE produziu entrega validável.

## 3. Entradas esperadas

- Código implementado.
- `SPEC.md` aprovada.
- `PLAN.md` concluído.
- Marcadores `sec` / `qa-sec` da SPEC.

## 4. Saídas esperadas

- Resultado QA-CR (review notes).
- Resultado QA-Func (cenários + observações).
- Resultado QA-SEC (findings + decisões) quando aplicável.
- Bugs encontrados como `BUG-{id}.md`.

## 5. Operação manual hoje (Stage 0)

1. Linus inicia QA-CR: revisão contra padrões e SPEC.
2. Linus inicia QA-Func: cenários de aceite + regressão proporcional.
3. Se `qa-sec` marcado: Kevin entra com QA-SEC.
4. Bugs viram `BUG-{id}.md` (estado BUG fast-track).
5. Founder Go/No-Go → DEPLOY ou retorno para CODE/BUG.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - code_ref: commit_range
    - spec_ref: artifact_ref
    - plan_ref: artifact_ref
  optional:
    - sec_marker: boolean
    - qa_sec_marker: boolean
outputs:
  - artifact: qa_cr_notes
  - artifact: qa_func_results
  - artifact: qa_sec_findings (when applicable)
  - array: bugs (BUG-{id}.md refs)
  - field: go_no_go_recommendation
tools_allowed:
  - tests.run
  - lint.run
  - security.scan (when qa_sec_marker)
  - fs.write (scoped to /projects/{product}/qa/)
tools_forbidden:
  - repo.write_source_code (QA não corrige; abre BUG)
  - gate.approve
gate:
  required_approval: Founder (Go/No-Go)
abstention_rules:
  - critical_finding_open
  - regression_in_existing_feature
  - qa_sec_failure_with_sensitive_surface
token_budget_heuristic: scales with PMG
```

## 7. Anti-padrões

- Mesclar QA-CR com QA-Func e perder rastreabilidade.
- Pular QA-SEC quando `qa-sec` está marcado.
- Aprovar QA com regressão conhecida sem decisão Founder.
- QA cerimonial em P (focado, não pomposo).

## 8. Referências

- Fase: [`../phases/07-QA.md`](../phases/07-QA.md)
- Estado relacionado: [`../states/BUG.md`](../states/BUG.md)
- Template: [`../templates/BUG.md`](../templates/BUG.md)
- Governança: [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)

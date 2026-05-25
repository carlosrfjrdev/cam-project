---
name: teczi-quality-assurance
description: "QA do Teczi DevFlow NCC-1701 (Linus + Kevin em QA-SEC). Acionar quando CODE produz entrega validável — três sub-naturezas: QA-CR (code review), QA-Func (funcional), QA-SEC (segurança proporcional). Bugs encontrados viram BUG-{id}.md (estado BUG fast-track). QA não corrige; abre BUG. No CaM, validação obrigatória do Risk Engine, kill switch e provisão fiscal em qualquer fluxo que toque execução."
phase: QA
lead_persona: Linus
co_lead_persona: Kevin (QA-SEC)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-quality-assurance (Fase 7: QA)

> Skill da Fase 7 (QA) do NCC-1701. Lead: **Linus**. Co-lead: **Kevin** (QA-SEC).

## 1. Propósito

Validar qualidade funcional, regressão e segurança proporcional ao P/M/G e marcadores da SPEC. Três sub-naturezas: **QA-CR** (code review), **QA-Func** (funcional), **QA-SEC** (segurança).

## 2. Quando acionar

- CODE produziu entrega validável.

## 3. Entradas esperadas

- Código implementado em `/apps/{codinome}/`.
- `SPEC.md` aprovada + `PLAN.md` concluído.
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
4. **Checagem constitucional no CaM:** qualquer caminho de ordem passa pelo Risk Engine (Art. 15)? Kill switch operacional (Art. 18)? UIs mostram resultado líquido (Art. 25)?
5. Bugs viram `BUG-{id}.md` (estado BUG fast-track — aciona [teczi-bug-fix](../teczi-bug-fix/SKILL.md)).
6. Founder Go/No-Go → DEPLOY ou retorno para CODE/BUG.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [code_ref, spec_ref, plan_ref]
  optional: [sec_marker, qa_sec_marker]
outputs:
  - artifact: qa_cr_notes
  - artifact: qa_func_results
  - artifact: qa_sec_findings (when applicable)
  - array: bugs (BUG-{id}.md refs)
  - field: go_no_go_recommendation
tools_allowed:
  - tests.run / lint.run / security.scan (when qa_sec)
  - fs.write (scoped to /project/{codinome}/demands/{id}/qa/)
tools_forbidden:
  - repo.write_source_code (QA não corrige; abre BUG)
  - gate.approve
gate:
  required_approval: Founder (Go/No-Go)
abstention_rules:
  - critical_finding_open
  - regression_in_existing_feature
  - qa_sec_failure_with_sensitive_surface
  - constituicao_violation_detected
token_budget_heuristic: scales with PMG
```

## 7. Anti-padrões

- Mesclar QA-CR com QA-Func e perder rastreabilidade.
- Pular QA-SEC quando `qa-sec` está marcado.
- Aprovar QA com regressão conhecida sem decisão Founder.
- QA cerimonial em P (focado, não pomposo).
- Não verificar conformidade com Constituição em features de execução/journal/risk.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/07-QA.md`](../../../teczi-devflow/NCC-1701/phases/07-QA.md)
- Estado relacionado: [`BUG.md`](../../../teczi-devflow/NCC-1701/states/BUG.md)
- Governança: [`SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md)

---
skill: teczi-code-execution
phase: CODE
status: draft
lead_persona: Nikola
co_lead_persona: Linus (intrabloco sempre), Kevin (intrabloco se sec)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-code-execution

## 1. Propósito

Implementar bloco/demanda dentro do escopo aprovado em SPEC+PLAN. CODE não decide arquitetura nem regras — apenas materializa.

## 2. Quando acionar

- Após `letscode` aceso no PLAN.

## 3. Entradas esperadas

- `SPEC.md` aprovada.
- `PLAN.md` com `letscode`.
- `DAS.md` / ADRs vigentes.

## 4. Saídas esperadas

- Código + commits no repositório do produto.
- Tech debt registrado se gerado.
- Resumo do bloco implementado.

## 5. Operação manual hoje (Stage 0)

1. Nikola lê SPEC + PLAN aprovados.
2. Nikola implementa por bloco/TASK.
3. Linus revisa intrabloco (code review leve, pré-QA formal).
4. Kevin revisa intrabloco se `sec` marcado.
5. Nikola roda build/checks locais (lint, typecheck, testes).
6. Founder valida o bloco → próximo bloco ou QA.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - spec_ref: artifact_ref
    - plan_ref: artifact_ref (with letscode=true)
  optional:
    - das_ref: artifact_ref
outputs:
  - commits: array
  - artifact: tech_debt_notes (when relevant)
  - field: build_status
  - field: checks_status
tools_allowed:
  - repo.write_source_code (scoped to demand)
  - repo.commit
  - build.run
  - tests.run
  - lint.run
  - typecheck.run
tools_forbidden:
  - git.push.main
  - secret.write
  - gate.approve
  - architecture.decide (volta para ARCH)
  - rule.reinterpret (volta para SPEC)
gate:
  required_approval: Founder (after build/checks green)
abstention_rules:
  - scope_expanded_without_approval
  - rule_reinterpreted (must return to SPEC)
  - architecture_drift (must return to ARCH)
  - build_red
token_budget_heuristic: scales with PLAN tasks
```

## 7. Anti-padrões

- Decidir arquitetura no meio do CODE.
- Reinterpretar regra de negócio sem voltar à SPEC.
- Bypass de check intrabloco (Linus sempre; Kevin se sec).
- Commit em main (proibição absoluta).

## 8. Referências

- Fase: [`../phases/06-CODE.md`](../phases/06-CODE.md)
- Skill anterior: [`teczi-code-planning.md`](teczi-code-planning.md)
- Skill seguinte: [`teczi-quality-assurance.md`](teczi-quality-assurance.md)

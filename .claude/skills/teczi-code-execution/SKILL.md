---
name: teczi-code-execution
description: "CODE do Teczi DevFlow NCC-1701 (Nikola, com Linus intrabloco sempre e Kevin se sec). Acionar após letscode aceso no PLAN para implementar bloco/demanda dentro do escopo aprovado em SPEC+PLAN. CODE não decide arquitetura nem regras — materializa. Build/checks verdes obrigatórios. Commit em main PROIBIDO. No CaM, todo código que toque execução de ordem deve passar pelo Risk Engine (Art. 15) e expor kill switch (Art. 18)."
phase: CODE
lead_persona: Nikola
co_lead_persona: Linus (intrabloco sempre), Kevin (intrabloco se sec)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-code-execution (Fase 6: CODE)

> Skill da Fase 6 (CODE) do NCC-1701. Lead: **Nikola**. Co-leads intrabloco: **Linus** (sempre), **Kevin** (se `sec`).

## 1. Propósito

Implementar bloco/demanda dentro do escopo aprovado em SPEC+PLAN. CODE **não decide** arquitetura nem regras — apenas materializa.

## 2. Quando acionar

- Após `letscode` aceso no PLAN e aprovado pelo Founder.

## 3. Entradas esperadas

- `SPEC.md` aprovada.
- `PLAN.md` com `letscode`.
- `DAS.md` / ADRs vigentes.
- Estrutura `/apps/{codinome}/` criada (vinda do PDOC).

## 4. Saídas esperadas

- Código + commits no repositório do aplicativo (`/apps/{codinome}/`).
- Tech debt registrado se gerado.
- Resumo do bloco implementado.

## 5. Operação manual hoje (Stage 0)

1. Nikola lê SPEC + PLAN aprovados.
2. Nikola implementa por bloco/TASK em `/apps/{codinome}/`.
3. Linus revisa intrabloco (code review leve, pré-QA formal).
4. Kevin revisa intrabloco se `sec` marcado.
5. Nikola roda build/checks locais (lint, typecheck, testes).
6. Founder valida o bloco → próximo bloco ou QA.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required:
    - spec_ref: artifact_ref
    - plan_ref: artifact_ref (with letscode=true)
  optional:
    - das_ref: artifact_ref
outputs:
  - commits: array
  - tech_debt_notes: artifact (when relevant)
  - build_status / checks_status
tools_allowed:
  - repo.write_source_code (scoped to /apps/{codinome}/)
  - repo.commit
  - build.run / tests.run / lint.run / typecheck.run
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
  - violates_constituicao_cam (Risk Engine bypass, IA executando ordem, etc.)
token_budget_heuristic: scales with PLAN tasks
```

## 7. Anti-padrões

- Decidir arquitetura no meio do CODE.
- Reinterpretar regra de negócio sem voltar à SPEC.
- Bypass de check intrabloco (Linus sempre; Kevin se sec).
- **Commit em main** (proibição absoluta).
- Implementar caminho de ordem que não passa pelo Risk Engine (viola Art. 15).
- Esquecer kill switch em qualquer app que toque execução (viola Art. 18).

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/06-CODE.md`](../../../teczi-devflow/NCC-1701/phases/06-CODE.md)
- Skill anterior: [`teczi-code-planning`](../teczi-code-planning/SKILL.md)
- Skill seguinte: [`teczi-quality-assurance`](../teczi-quality-assurance/SKILL.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 15º, 18º, 25º, 35º

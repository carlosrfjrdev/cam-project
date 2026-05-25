---
skill: teczi-project-discovery
phase: DISC
status: draft
lead_persona: Marty
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-project-discovery

## 1. Propósito

Delimitar demanda: produzir `SCOPE.md` (In/Out/Later + perguntas abertas) e, se produto novo, `DVP.md` inicial. Evitar feature factory.

## 2. Quando acionar

- Demanda tem ambiguidade sobre escopo, problema ou usuário.
- Produto novo (DVP nasce aqui).
- **Skip** quando é ajuste mecânico de funcionalidade existente sem ambiguidade.

## 3. Entradas esperadas

- Intenção do Founder (texto livre).
- Contexto do produto existente (se aplicável).
- Artefatos vivos relacionados (DVP/DAS anteriores).

## 4. Saídas esperadas

- `SCOPE.md` da demanda.
- `DVP.md` inicial (se produto novo).
- Workstream DISC-UX (se gatilho ativo — Andy).

## 5. Operação manual hoje (Stage 0)

1. Founder descreve a demanda.
2. Marty refina: problema, usuário, resultado esperado, sinais de sucesso.
3. Marty produz `SCOPE.md` com In/Out/Later + perguntas abertas.
4. Se produto novo: Marty + Founder produzem `DVP.md` inicial.
5. Se gatilho UX (DS/frontend crítico ou solicitação Founder): Andy entra em workstream paralelo.
6. Founder aprova SCOPE → segue para ARCH/SPEC.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - intent: string
    - demand_id: string
  optional:
    - product_dvp_ref: artifact_ref
    - product_das_ref: artifact_ref
outputs:
  - artifact: SCOPE.md
  - artifact: DVP.md (when new product)
  - workstream: DISC-UX (when triggered)
tools_allowed:
  - fs.write (scoped to /projects/{product}/demands/{id}/)
  - codex.read (futuro)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
gate:
  required_approval: Founder
abstention_rules:
  - ambiguous_intent_unresolved
  - missing_product_context_when_required
token_budget_heuristic: medium
```

## 7. Anti-padrões

- Transformar DISC em SPEC (regras técnicas, contratos).
- Transformar DISC em PLAN (decidir blocos).
- Esconder perguntas em aberto.
- Forçar DVP completo em produto sem direção mínima.

## 8. Referências

- Fase: [`../phases/02-DISC.md`](../phases/02-DISC.md)
- Templates: [`../templates/SCOPE.md`](../templates/SCOPE.md), [`../templates/DVP.md`](../templates/DVP.md)
- Origem conceitual: `projects/devflow/REVIEW-Teczi-Project-Discovery-SCOPE-Enxuto.md`

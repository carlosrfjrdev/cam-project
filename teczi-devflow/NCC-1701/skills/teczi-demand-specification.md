---
skill: teczi-demand-specification
phase: SPEC
status: draft
lead_persona: Albert
co_lead_persona: Kevin (sec/qa-sec)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-demand-specification

## 1. Propósito

Especificar a demanda: regras, contratos, P/M/G, marcadores `sec`/`qa-sec`, saídas esperadas. Albert atribui P/M/G inicial; Nico pode contestar no PLAN.

## 2. Quando acionar

- Toda demanda que não é BUG.

## 3. Entradas esperadas

- `SCOPE.md` aprovado.
- `DVP.md` vigente.
- `DAS.md` vigente.
- ADRs aplicáveis.

## 4. Saídas esperadas

- `SPEC.md` da demanda.
- Classificação P/M/G + rationale.
- Marcadores `sec` e `qa-sec` quando aplicáveis.
- Delta no DVP se a demanda afeta direção estratégica.

## 5. Operação manual hoje (Stage 0)

1. Albert lê SCOPE + DVP + DAS + ADRs.
2. Albert produz SPEC: regras, contratos, exemplos, casos limite.
3. Albert atribui P/M/G — regra simples:
   - **P** = subitem de funcionalidade existente.
   - **M** = melhoria relevante OU nova funcionalidade.
   - **G** = N funcionalidades / decomposição necessária.
4. Kevin marca `sec`/`qa-sec` se superfície sensível.
5. Se altera direção estratégica: Albert atualiza DVP (delta).
6. Founder aprova SPEC → PLAN.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - scope_ref: artifact_ref
  optional:
    - dvp_ref: artifact_ref
    - das_ref: artifact_ref
    - adrs_refs: array<artifact_ref>
outputs:
  - artifact: SPEC.md
  - field: pmg_classification (P|M|G)
  - field: pmg_rationale
  - field: sec_marker (boolean)
  - field: qa_sec_marker (boolean)
  - artifact: DVP_DELTA.md (when strategy affected)
tools_allowed:
  - fs.write (scoped to /projects/{product}/demands/{id}/)
  - codex.read (futuro)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
  - letscode.toggle
gate:
  required_approval: Founder
abstention_rules:
  - ambiguous_rule_unresolved
  - missing_pmg_rationale
  - sensitive_surface_without_sec_marker
token_budget_heuristic: medium (P) to high (G)
forbidden_patterns:
  - risk_modifier (Q8 Founder)
  - security_modifier (Q8 Founder)
  - architecture_impact_modifier (Q8 Founder)
  - release_impact_modifier (Q8 Founder)
```

## 7. Anti-padrões

- SPEC sem classificação P/M/G.
- **Adicionar modificadores de risco** (Q8 Founder considera overengineering).
- Esconder regras em comentários de código.
- Especificar tecnologia/stack — isso é ARCH/PLAN.

## 8. Referências

- Fase: [`../phases/04-SPEC.md`](../phases/04-SPEC.md)
- Template: [`../templates/SPEC.md`](../templates/SPEC.md)
- Skill seguinte: [`teczi-code-planning.md`](teczi-code-planning.md)

---
skill: teczi-architecture-decision
phase: ARCH
status: draft
lead_persona: Oscar
co_lead_persona: Vint (INFRA-ARCH)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-architecture-decision

## 1. Propósito

Definir arquitetura da demanda, registrar decisões irreversíveis/caras como ADRs e produzir INFRA-ARCH quando há impacto operacional.

## 2. Quando acionar

- Demanda altera arquitetura existente (camadas, contratos, integração, infra, dados).
- **Skip** se impacto é local e respeita arquitetura vigente.

## 3. Entradas esperadas

- `SCOPE.md` aprovado.
- `DVP.md` vigente.
- `DAS.md` vigente.
- ADRs vigentes.

## 4. Saídas esperadas

- `DAS.md` (novo ou atualizado).
- `ADR-{id}.md` quando aplicável.
- `INFRA-ARCH.md` quando há impacto operacional.
- Threat model lógico quando superfície sensível.

## 5. Operação manual hoje (Stage 0)

1. Oscar lê SCOPE + DVP + DAS + ADRs.
2. Oscar propõe decisão + alternativas consideradas.
3. Se irreversível/cara: registrar ADR.
4. Se impacto operacional: Vint colabora em INFRA-ARCH.
5. Se superfície sensível: Kevin produz threat model lógico.
6. Founder aprova → ARCH concluída.

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
  - artifact: DAS.md
  - artifact: ADR.md (when irreversible/costly)
  - artifact: INFRA-ARCH.md (when operational impact)
tools_allowed:
  - fs.write (scoped to /projects/{product}/architecture/)
  - codex.read (futuro)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
gate:
  required_approval: Founder
abstention_rules:
  - decision_without_rationale
  - conflict_with_vigent_adr_without_deprecation
token_budget_heuristic: medium-to-high
```

## 7. Anti-padrões

- ADR para decisão trivial.
- DAS como inventário "como está" (isso é SDOC/Howard).
- Decidir infra sem Vint.
- Ignorar Kevin quando há auth/dados/integração externa.

## 8. Referências

- Fase: [`../phases/03-ARCH.md`](../phases/03-ARCH.md)
- Templates: [`../templates/DAS.md`](../templates/DAS.md), [`../templates/ADR.md`](../templates/ADR.md), [`../templates/INFRA-ARCH.md`](../templates/INFRA-ARCH.md)
- Governança relacionada: [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)

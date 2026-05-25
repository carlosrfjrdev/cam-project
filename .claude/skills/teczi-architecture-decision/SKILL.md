---
name: teczi-architecture-decision
description: "ARCH do Teczi DevFlow NCC-1701 (Oscar + Vint para INFRA-ARCH, Kevin para superfície sensível). Acionar para decidir arquitetura da demanda, atualizar DAS e registrar ADRs irreversíveis/caras. Skip quando o impacto é local e respeita arquitetura vigente. No CaM, sempre verificar se a decisão atinge o Risk Engine, kill switch ou perímetro de capital."
phase: ARCH
lead_persona: Oscar
co_lead_persona: Vint (INFRA-ARCH), Kevin (superfície sensível)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-architecture-decision (Fase 3: ARCH)

> Skill da Fase 3 (ARCH) do NCC-1701. Lead: **Oscar**. Co-leads: **Vint** (INFRA-ARCH), **Kevin** (threat model lógico).

## 1. Propósito

Definir arquitetura da demanda, registrar decisões irreversíveis/caras como ADRs e produzir INFRA-ARCH quando há impacto operacional.

## 2. Quando acionar

- Demanda altera arquitetura existente (camadas, contratos, integração, infra, dados).
- Demanda atinge o **Risk Engine**, **kill switch**, **provisão fiscal**, **journal** ou perímetro de capital (Constituição Arts. 8/15/18/25).
- **Skip** se impacto é local e respeita arquitetura vigente.

## 3. Entradas esperadas

- `SCOPE.md` aprovado.
- `DVP.md`, `DAS.md` e ADRs vigentes.
- **Constituição** — toda decisão arquitetural tem que sobreviver à hierarquia Art. 36º.

## 4. Saídas esperadas

- `DAS.md` (novo ou atualizado).
- `ADR-{id}.md` quando aplicável.
- `INFRA-ARCH.md` quando há impacto operacional.
- Threat model lógico quando superfície sensível (gatilho SEC-GOV).

## 5. Operação manual hoje (Stage 0)

1. Oscar lê SCOPE + DVP + DAS + ADRs + Constituição.
2. Oscar propõe decisão + alternativas consideradas.
3. Se irreversível/cara: registrar ADR.
4. Se impacto operacional: Vint colabora em INFRA-ARCH.
5. Se superfície sensível: Kevin produz threat model lógico (aciona [teczi-security-governance](../teczi-security-governance/SKILL.md) se gatilho ativo).
6. Founder aprova → ARCH concluída → segue para SPEC.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [scope_ref]
  optional: [dvp_ref, das_ref, adrs_refs]
outputs:
  - artifact: DAS.md
  - artifact: ADR.md (when irreversible/costly)
  - artifact: INFRA-ARCH.md (when operational impact)
tools_allowed:
  - fs.write (scoped to /project/{codinome}/)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
gate:
  required_approval: Founder
abstention_rules:
  - decision_without_rationale
  - conflict_with_vigent_adr_without_deprecation
  - violates_constituicao_cam (Risk Engine bypass, IA executando, etc.)
token_budget_heuristic: medium-to-high
```

## 7. Anti-padrões

- ADR para decisão trivial.
- DAS como inventário "como está" (isso é SDOC/Howard).
- Decidir infra sem Vint.
- Ignorar Kevin quando há auth/dados/integração externa.
- Aprovar arquitetura que viola Risk Engine (Art. 15), kill switch (Art. 18) ou hierarquia constitucional (Art. 36).

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/03-ARCH.md`](../../../teczi-devflow/NCC-1701/phases/03-ARCH.md)
- Templates: [`DAS.md`](../../../teczi-devflow/NCC-1701/templates/DAS.md), [`ADR.md`](../../../teczi-devflow/NCC-1701/templates/ADR.md), [`INFRA-ARCH.md`](../../../teczi-devflow/NCC-1701/templates/INFRA-ARCH.md)
- Governança: [`SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 8º, 15º, 18º, 25º, 36º

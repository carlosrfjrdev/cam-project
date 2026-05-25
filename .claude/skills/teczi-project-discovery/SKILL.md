---
name: teczi-project-discovery
description: "DISC do Teczi DevFlow NCC-1701 (Marty). Acionar para delimitar oportunidade/demanda no CaM, produzir SCOPE.md (In/Out/Later + perguntas abertas) e, se aplicativo novo, DVP.md inicial. Anti-feature-factory. Skip quando é ajuste mecânico sem ambiguidade."
phase: DISC
lead_persona: Marty
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-project-discovery (Fase 2: DISC)

> Skill da Fase 2 (DISC) do NCC-1701. Lead: **Marty**. Stage 0.

## 1. Propósito

Delimitar a demanda: produzir `SCOPE.md` com **In / Out / Later + perguntas abertas** e, se aplicativo novo do CaM, um `DVP.md` inicial. Evitar feature factory.

## 2. Quando acionar

- Demanda tem ambiguidade sobre escopo, problema ou usuário.
- Aplicativo novo do cockpit CaM (DVP nasce aqui).
- **Skip** quando é ajuste mecânico de funcionalidade existente sem ambiguidade.

## 3. Entradas esperadas

- Intenção do Founder (texto livre).
- Contexto do aplicativo existente (se aplicável).
- Artefatos vivos relacionados (DVP/DAS anteriores).
- **Sempre:** Constituição do CaM (`CONSTITUICAO.md`) — toda demanda tem que respeitar o perímetro (Art. 8º) e a hierarquia (Art. 36º).

## 4. Saídas esperadas

- `SCOPE.md` da demanda em `/project/{codinome}/demands/{id}/SCOPE.md`.
- `DVP.md` inicial em `/project/{codinome}/` (se aplicativo novo).

## 5. Operação manual hoje (Stage 0)

1. Founder descreve a demanda.
2. Marty refina: problema, usuário, resultado esperado, sinais de sucesso.
3. Marty produz `SCOPE.md` com In/Out/Later + perguntas abertas.
4. Se aplicativo novo: Marty + Founder produzem `DVP.md` inicial.
5. **Checagem constitucional obrigatória:** a demanda viola algum artigo da Constituição? Se sim, abortar ou retornar para emenda (Art. 38º).
6. Founder aprova SCOPE → segue para ARCH/SPEC.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [intent, demand_id]
  optional: [product_dvp_ref, product_das_ref]
outputs:
  - artifact: SCOPE.md
  - artifact: DVP.md (quando aplicativo novo)
tools_allowed:
  - fs.write (scoped to /project/{codinome}/demands/{id}/)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
gate:
  required_approval: Founder
abstention_rules:
  - ambiguous_intent_unresolved
  - violates_constituicao_cam
  - missing_constituicao_check
token_budget_heuristic: medium
```

## 7. Anti-padrões

- Transformar DISC em SPEC (regras técnicas, contratos).
- Transformar DISC em PLAN (decidir blocos).
- Esconder perguntas em aberto.
- Forçar DVP completo em aplicativo sem direção mínima.
- **Pular checagem constitucional** — DISC sem leitura da CONSTITUICAO.md é DISC inválida.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/02-DISC.md`](../../../teczi-devflow/NCC-1701/phases/02-DISC.md)
- Templates: [`../../../teczi-devflow/NCC-1701/templates/SCOPE.md`](../../../teczi-devflow/NCC-1701/templates/SCOPE.md), [`../../../teczi-devflow/NCC-1701/templates/DVP.md`](../../../teczi-devflow/NCC-1701/templates/DVP.md)
- Constituição: [`../../../CONSTITUICAO.md`](../../../CONSTITUICAO.md)

---
name: teczi-demand-specification
description: "SPEC do Teczi DevFlow NCC-1701 (Albert + Kevin em sec/qa-sec). Acionar para especificar demanda do CaM: regras, contratos, P/M/G, marcadores sec/qa-sec, saídas esperadas. Albert atribui P/M/G inicial — Nico pode contestar no PLAN (loop ilimitado até consenso). PROIBIDO estimar em horas/dias/semanas e usar modificadores de risco/segurança/arquitetura/release no P/M/G."
phase: SPEC
lead_persona: Albert
co_lead_persona: Kevin (sec / qa-sec)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-demand-specification (Fase 4: SPEC)

> Skill da Fase 4 (SPEC) do NCC-1701. Lead: **Albert**. Co-lead: **Kevin** (sec / qa-sec).

## 1. Propósito

Especificar a demanda: regras, contratos, P/M/G, marcadores `sec`/`qa-sec`, saídas esperadas. Albert atribui P/M/G inicial; Nico pode contestar no PLAN.

## 2. Quando acionar

- Toda demanda que **não é BUG**.

## 3. Entradas esperadas

- `SCOPE.md` aprovado.
- `DVP.md`, `DAS.md` e ADRs vigentes.
- **Constituição do CaM** — regras de negócio do cockpit nascem dela.

## 4. Saídas esperadas

- `SPEC.md` da demanda em `/project/{codinome}/demands/{id}/SPEC.md`.
- Classificação P/M/G + rationale.
- Marcadores `sec` e `qa-sec` quando aplicáveis.
- Delta no DVP se a demanda afeta direção estratégica.

## 5. Operação manual hoje (Stage 0)

1. Albert lê SCOPE + DVP + DAS + ADRs + Constituição.
2. Albert produz SPEC: regras, contratos, exemplos, casos limite.
3. Albert atribui P/M/G — regra simples:
   - **P** = subitem de funcionalidade existente.
   - **M** = melhoria relevante OU nova funcionalidade.
   - **G** = N funcionalidades / decomposição necessária.
4. Kevin marca `sec`/`qa-sec` se superfície sensível.
5. Se altera direção estratégica: Albert atualiza DVP (delta).
6. Founder aprova SPEC → PLAN.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [scope_ref]
  optional: [dvp_ref, das_ref, adrs_refs]
outputs:
  - artifact: SPEC.md
  - field: pmg_classification (P|M|G)
  - field: pmg_rationale
  - field: sec_marker (boolean)
  - field: qa_sec_marker (boolean)
tools_allowed:
  - fs.write (scoped to /project/{codinome}/demands/{id}/)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
  - letscode.toggle (é gate do PLAN)
gate:
  required_approval: Founder
abstention_rules:
  - ambiguous_rule_unresolved
  - missing_pmg_rationale
  - sensitive_surface_without_sec_marker
forbidden_patterns:
  - time_estimate_hours / days / weeks
  - risk_modifier (Q8 Founder)
  - security_modifier (Q8 Founder)
  - architecture_impact_modifier (Q8 Founder)
  - release_impact_modifier (Q8 Founder)
token_budget_heuristic: medium (P) to high (G)
```

## 7. Anti-padrões

- SPEC sem classificação P/M/G.
- **Adicionar modificadores de risco** no P/M/G — Q8 Founder considera overengineering.
- **Estimar em horas/dias/semanas** — proibição explícita do Founder.
- Esconder regras em comentários de código.
- Especificar tecnologia/stack — isso é ARCH/PLAN.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/04-SPEC.md`](../../../teczi-devflow/NCC-1701/phases/04-SPEC.md)
- Template: [`SPEC.md`](../../../teczi-devflow/NCC-1701/templates/SPEC.md)
- Skill seguinte: [`teczi-code-planning`](../teczi-code-planning/SKILL.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md)

---
name: teczi-code-planning
description: "PLAN do Teczi DevFlow NCC-1701 (Nico, com loop ilimitado com Albert sobre P/M/G). Acionar após SPEC aprovada para planejar execução proporcional ao P/M/G, decompor em TASKs se G e marcar letscode (gate final). PROIBIDO estimar em horas/dias/semanas. Nico tem direito formal de contestar a classificação P/M/G de Albert — Founder decide quando parar o loop."
phase: PLAN
lead_persona: Nico
co_lead_persona: Albert (loop ilimitado até consenso)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-code-planning (Fase 5: PLAN)

> Skill da Fase 5 (PLAN) do NCC-1701. Lead: **Nico**. Co-lead: **Albert** (loop ilimitado).

## 1. Propósito

Planejar execução proporcional ao P/M/G e resolver drift SPEC↔execução. Nico tem direito formal de criticar a classificação P/M/G de Albert.

## 2. Quando acionar

- Toda demanda que produz código, **após SPEC aprovada**.

## 3. Entradas esperadas

- `SPEC.md` aprovada.
- `DAS.md` vigente + ADRs aplicáveis.

## 4. Saídas esperadas

- `PLAN.md` da demanda (proporcional ao P/M/G).
- Marca `letscode` (gate final do PLAN).
- TASKs sequenciais se G.
- Re-classificação P/M/G se Nico identificar gargalo.

## 5. Operação manual hoje (Stage 0)

1. Nico lê SPEC aprovada.
2. Nico avalia P/M/G — concorda ou contesta.
3. Se contestação: **loop ilimitado** com Albert até consenso; Founder decide quando parar (Q9).
4. Nico produz PLAN proporcional:
   - **P**: embutido na SPEC ou curto.
   - **M**: PLAN separado, blocos contidos.
   - **G**: PLAN + TASKs sequenciais por blocos.
5. Nico marca `letscode`.
6. Founder valida → CODE.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [spec_ref]
  optional: [das_ref, adrs_refs]
outputs:
  - artifact: PLAN.md
  - field: letscode (boolean, requires Founder approval)
  - array: tasks (when G)
tools_allowed:
  - fs.write (scoped to /project/{codinome}/demands/{id}/)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
  - time_estimation (any unit)
gate:
  required_approval: Founder (for letscode)
abstention_rules:
  - drift_spec_plan_unresolved
  - pmg_disagreement_without_loop
  - missing_task_breakdown_when_G
forbidden_patterns:
  - time_estimate_hours / days / weeks
token_budget_heuristic: medium (P) to high (G)
```

## 7. Anti-padrões

- PLAN com estimativa em horas/dias/semanas — **proibido** (Founder).
- PLAN cerimonial em demanda P.
- Skip do loop Albert-Nico em P/M/G ambíguo.
- `letscode` sem aprovação Founder.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/05-PLAN.md`](../../../teczi-devflow/NCC-1701/phases/05-PLAN.md)
- Template: [`PLAN.md`](../../../teczi-devflow/NCC-1701/templates/PLAN.md)
- Skill anterior: [`teczi-demand-specification`](../teczi-demand-specification/SKILL.md)
- Skill seguinte: [`teczi-code-execution`](../teczi-code-execution/SKILL.md)

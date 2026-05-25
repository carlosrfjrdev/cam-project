---
skill: teczi-code-planning
phase: PLAN
status: draft
lead_persona: Nico
co_lead_persona: Albert (loop ilimitado até consenso)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-code-planning

## 1. Propósito

Planejar execução proporcional ao P/M/G e resolver drift SPEC↔execução. Nico tem direito formal de criticar a classificação P/M/G de Albert.

## 2. Quando acionar

- Toda demanda que produz código, após SPEC aprovada.

## 3. Entradas esperadas

- `SPEC.md` aprovada.
- `DAS.md` vigente.
- ADRs aplicáveis.

## 4. Saídas esperadas

- `PLAN.md` da demanda (proporcional).
- Marca `letscode` (gate final).
- TASKs sequenciais se G.
- Re-classificação P/M/G se Nico identificar gargalo.

## 5. Operação manual hoje (Stage 0)

1. Nico lê SPEC aprovada.
2. Nico avalia P/M/G — concorda ou contesta.
3. Se contestação: loop ilimitado com Albert até consenso; Founder decide quando parar (Q9).
4. Nico produz PLAN proporcional:
   - **P**: embutido na SPEC ou curto.
   - **M**: PLAN separado, blocos contidos.
   - **G**: PLAN + TASKs sequenciais.
5. Nico marca `letscode`.
6. Founder valida → CODE.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - spec_ref: artifact_ref
  optional:
    - das_ref: artifact_ref
    - adrs_refs: array<artifact_ref>
outputs:
  - artifact: PLAN.md
  - field: letscode (boolean, requires Founder approval)
  - array: tasks (when G)
  - field: pmg_reclassification (optional, with rationale)
tools_allowed:
  - fs.write (scoped to /projects/{product}/demands/{id}/)
  - codex.read (futuro)
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
token_budget_heuristic: medium (P) to high (G)
forbidden_patterns:
  - time_estimate_hours
  - time_estimate_days
  - time_estimate_weeks
```

## 7. Anti-padrões

- PLAN com estimativa em horas/dias/semanas — **proibido** (Founder).
- PLAN cerimonial em demanda P.
- Skip do loop Albert-Nico em P/M/G ambíguo.
- `letscode` sem aprovação Founder.

## 8. Referências

- Fase: [`../phases/05-PLAN.md`](../phases/05-PLAN.md)
- Template: [`../templates/PLAN.md`](../templates/PLAN.md)
- Skill anterior: [`teczi-demand-specification.md`](teczi-demand-specification.md)
- Skill seguinte: [`teczi-code-execution.md`](teczi-code-execution.md)

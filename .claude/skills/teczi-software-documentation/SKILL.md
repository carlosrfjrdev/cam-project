---
name: teczi-software-documentation
description: "SDOC do Teczi DevFlow NCC-1701 (Denis + Howard para DRIFT). Acionar APENAS quando há release final elegível OU o Founder solicita explicitamente (Q11). Documenta estado real do software (não substitui artefatos de intenção como DVP/DAS/SPEC/PLAN). DRIFT-REPORT (Howard) também só por solicitação explícita (Q12). PROIBIDO acionar SDOC em toda demanda."
phase: SDOC
lead_persona: Denis
co_lead_persona: Howard (DRIFT sob solicitação)
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-software-documentation (Fase 9: SDOC)

> Skill da Fase 9 (SDOC) do NCC-1701. Lead: **Denis**. Co-lead: **Howard** (DRIFT sob solicitação).

## 1. Propósito

Documentar o **estado real** do software após o fluxo. **Não substitui** artefatos de intenção (DVP/DAS/SPEC/PLAN) — registra o que efetivamente existe no código deployado.

## 2. Quando acionar

SDOC **não** roda em toda demanda. Roda **apenas** quando:

- há **versão final elegível para release**; **ou**
- Founder/operador **solicita explicitamente**.

(Q11 Founder)

**DRIFT-REPORT (Howard)** roda **apenas** por solicitação explícita do Founder. Sem gatilhos automáticos, sem gatilhos "recomendados" (Q12 Founder).

## 3. Entradas esperadas

- Código deployado em `/apps/{codinome}/`.
- SPEC/PLAN da demanda (para comparação intenção × real).
- Solicitação explícita do Founder (no caso SDOC sob demanda).

## 4. Saídas esperadas

- Documentação as-is do software (em `/apps/{codinome}/docs/` ou Stage 1 futuro do Codex).
- `DRIFT-REPORT.md` quando Howard solicitado.

## 5. Operação manual hoje (Stage 0)

1. Founder ativa SDOC (ou release final elegível).
2. Denis estrutura documentação as-is.
3. Se Founder solicitou Howard: Howard mapeia drift `project` × `apps` (aciona [teczi-discovery-software](../teczi-discovery-software/SKILL.md)).
4. Drift é registrado em DRIFT-REPORT com direção de reconciliação.
5. Founder decide: ajustar código ou ajustar intenção (princípio 7 — estado real vence).
6. Founder valida → SDOC concluída.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required:
    - code_ref: deployed_commit
    - app_id: string
    - activation_reason: enum [final_release_eligible, founder_request]
  optional: [spec_ref, plan_ref, howard_requested]
outputs:
  - artifact: software_documentation_as_is
  - artifact: DRIFT-REPORT.md (when howard_requested)
tools_allowed:
  - repo.read
  - fs.write (scoped to /apps/{codinome}/docs/)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
  - auto_trigger_drift (Q12 Founder)
gate:
  required_approval: Founder
abstention_rules:
  - documentation_still_describes_intent (not real state)
  - drift_detected_without_reconciliation_proposal
forbidden_patterns:
  - auto_drift_after_deploy
  - drift_recommended_triggers (Q12 Founder)
token_budget_heuristic: high (large codebases)
```

## 7. Anti-padrões

- Rodar SDOC em toda demanda — gera documentação nobre sem consumo.
- DRIFT automático após DEPLOY — Q12 Founder proíbe.
- Gatilhos "recomendados" para DRIFT — descartado intencionalmente.
- SDOC que descreve intenção em vez de estado real — isso é DVP/DAS.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/09-SDOC.md`](../../../teczi-devflow/NCC-1701/phases/09-SDOC.md)
- Template: [`DRIFT-REPORT.md`](../../../teczi-devflow/NCC-1701/templates/DRIFT-REPORT.md)
- Princípio: NCC-1701 §2 (regra 7) "Estado real vence"
- Skill relacionada: [`teczi-discovery-software`](../teczi-discovery-software/SKILL.md)

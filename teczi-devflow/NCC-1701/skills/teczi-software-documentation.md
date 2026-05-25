---
skill: teczi-software-documentation
phase: SDOC
status: draft
lead_persona: Denis
co_lead_persona: Howard (DRIFT sob solicitação)
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-software-documentation

## 1. Propósito

Documentar o **estado real** do software após o fluxo. Não substitui artefatos de intenção (DVP/DAS/SPEC/PLAN) — registra o que efetivamente existe no código deployado.

## 2. Quando acionar

SDOC **não** roda em toda demanda. Roda **apenas** quando:

- há **versão final elegível para release**; **ou**
- Founder/operador **solicita explicitamente**.

(Q11 Founder)

DRIFT-REPORT (Howard) roda **apenas** por solicitação explícita do Founder. **Sem gatilhos automáticos, sem gatilhos "recomendados"** (Q12 Founder).

## 3. Entradas esperadas

- Código deployado.
- Repositório do produto.
- SPEC/PLAN da demanda (para comparação intenção × real).
- Solicitação explícita do Founder (no caso SDOC sob demanda).

## 4. Saídas esperadas

- Documentação as-is do software.
- `DRIFT-REPORT.md` quando Howard solicitado.

## 5. Operação manual hoje (Stage 0)

1. Founder ativa SDOC (ou release final elegível).
2. Denis estrutura documentação as-is.
3. Se Founder solicitou Howard: Howard mapeia drift `project` × `codex`.
4. Drift é registrado em DRIFT-REPORT com direção de reconciliação.
5. Founder decide: ajustar código ou ajustar intenção (princípio 7).
6. Founder valida → SDOC concluída.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - code_ref: deployed_commit
    - product_id: string
    - activation_reason: enum [final_release_eligible, founder_request]
  optional:
    - spec_ref: artifact_ref
    - plan_ref: artifact_ref
    - howard_requested: boolean
outputs:
  - artifact: software_documentation_as_is
  - artifact: DRIFT-REPORT.md (when howard_requested)
tools_allowed:
  - repo.read
  - fs.write (scoped to /projects/{product}/codex/ Stage 0; /teczi-codex/ futuro)
tools_forbidden:
  - repo.write_source_code
  - gate.approve
  - auto_trigger_drift (Q12 Founder)
gate:
  required_approval: Founder
abstention_rules:
  - documentation_still_describes_intent (not real state)
  - drift_detected_without_reconciliation_proposal
token_budget_heuristic: high (large codebases)
forbidden_patterns:
  - auto_drift_after_deploy
  - drift_recommended_triggers (Q12 Founder)
```

## 7. Anti-padrões

- Rodar SDOC em toda demanda — gera documentação nobre sem consumo.
- DRIFT automático após DEPLOY — Q12 Founder proíbe.
- Gatilhos "recomendados" para DRIFT — **descartado intencionalmente** (ajuste GPT-PARECER §4.2 não incorporado).
- SDOC que descreve intenção em vez de estado real — isso é DVP/DAS.

## 8. Referências

- Fase: [`../phases/09-SDOC.md`](../phases/09-SDOC.md)
- Template: [`../templates/DRIFT-REPORT.md`](../templates/DRIFT-REPORT.md)
- Princípio: SCOPE-FINAL §4 (7) "Estado real vence"

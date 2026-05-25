---
skill: teczi-security-governance
governance: SEC-GOV
status: draft
lead_persona: Kevin
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-security-governance

## 1. Propósito

Conduzir revisão sistêmica de segurança fora do caminho feliz, quando algum dos 9 gatilhos canônicos é ativado ou o Founder solicita.

Não substitui `sec` intrabloco (CODE) nem QA-SEC (QA). É camada adicional para risco acumulado ou sensível.

## 2. Quando acionar

Lista canônica (SCOPE-FINAL §11.2):

1. Auth / autorização
2. Dados sensíveis
3. Integração externa relevante
4. Mudança em infra
5. Release final
6. Incidente
7. Exposição pública
8. Mudança em agentes/skills/permissão/Codex/CLI/MCP
9. Solicitação explícita de Carlos

## 3. Entradas esperadas

- Trigger ativado (qual dos 9 ou explicit_founder_request).
- Contexto da demanda/release/incidente.
- DAS, SPEC, INFRA-ARCH aplicáveis.
- Findings anteriores (se houver).

## 4. Saídas esperadas

- Threat model sistêmico (revisão).
- Findings classificados (informal: alta/média/baixa).
- Decisões: aceitar, mitigar, corrigir, waiver.
- Recomendação Go / No-Go / Conditional Go.

## 5. Operação manual hoje (Stage 0)

1. Trigger é ativado (automático conceitual + decisão Founder).
2. Kevin convoca especialistas conforme escopo (Vint infra, Oscar arquitetura).
3. Kevin produz threat model sistêmico ou atualiza existente.
4. Findings são classificados e cada um recebe decisão.
5. Waivers são explícitos quando aceitos.
6. Kevin emite recomendação para Founder.
7. Founder decide → SEC-GOV resolvido.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - trigger: enum (9 triggers + explicit_founder_request)
    - context: object
  optional:
    - das_ref: artifact_ref
    - spec_ref: artifact_ref
    - infra_arch_ref: artifact_ref
    - previous_findings_refs: array<artifact_ref>
outputs:
  - artifact: threat_model_systemic
  - array: findings (with classification and decision)
  - array: waivers (explicit)
  - field: recommendation (go|no_go|conditional_go)
tools_allowed:
  - codex.read
  - security.scan
  - fs.write (scoped to /projects/{product}/security/)
tools_forbidden:
  - gate.approve (Kevin recomenda, Founder decide)
  - repo.write_source_code
gate:
  recommendation_authority: Kevin
  final_authority: Founder
abstention_rules:
  - critical_finding_without_decision
  - no_go_recommendation_overridden_without_rationale
token_budget_heuristic: high
```

## 7. Anti-padrões

- Tratar SEC-GOV como fase obrigatória em toda demanda.
- Permitir que SEC-GOV decida sozinha.
- Skip de SEC-GOV antes de release final.
- Confundir SEC-GOV (sistêmica) com QA-SEC (operacional da demanda).
- Acumular gatilhos sem acionamento.

## 8. Referências

- Governança: [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)
- Estados relacionados: [`../states/BUG.md`](../states/BUG.md), [`../states/OPS.md`](../states/OPS.md)
- Fases relacionadas: [`../phases/03-ARCH.md`](../phases/03-ARCH.md), [`../phases/04-SPEC.md`](../phases/04-SPEC.md), [`../phases/07-QA.md`](../phases/07-QA.md), [`../phases/08-DEPLOY.md`](../phases/08-DEPLOY.md)

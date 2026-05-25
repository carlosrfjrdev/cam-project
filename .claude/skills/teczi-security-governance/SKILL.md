---
name: teczi-security-governance
description: "Governança SEC-GOV do Teczi DevFlow NCC-1701 (Kevin). Acionar quando algum dos 9 gatilhos canônicos é ativado (auth, dados sensíveis, integração externa, mudança em infra, release final, incidente, exposição pública, mudança em agentes/skills/permissão, solicitação explícita do Founder). Não substitui sec intrabloco (CODE) nem QA-SEC (QA). Kevin recomenda, Founder decide. No CaM, qualquer mudança no Risk Engine, journal ou kill switch dispara SEC-GOV."
governance: SEC-GOV
lead_persona: Kevin
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-security-governance (Governança SEC-GOV)

> Skill da governança transversal **SEC-GOV** do NCC-1701. Lead: **Kevin**. Camada adicional, não substitui `sec` intrabloco nem QA-SEC.

## 1. Propósito

Conduzir revisão sistêmica de segurança fora do caminho feliz, quando algum dos 9 gatilhos canônicos é ativado ou o Founder solicita.

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

**Gatilhos adicionais específicos do CaM (extensão local):**

- 10. Qualquer mudança que toque o **Risk Engine** (Art. 15 — autoridade máxima).
- 11. Qualquer mudança que toque o **kill switch** (Art. 18 — interrupção imediata).
- 12. Qualquer mudança que toque o **journal**, ledger fiscal ou provisão (Arts. 25, 26, 31).
- 13. Qualquer mudança na **autoridade da IA** (Arts. 34, 35, 36).

## 3. Entradas esperadas

- Trigger ativado (qual dos 13).
- Contexto da demanda/release/incidente.
- DAS, SPEC, INFRA-ARCH aplicáveis.
- Findings anteriores (se houver).
- Constituição CaM (referência absoluta).

## 4. Saídas esperadas

- Threat model sistêmico (revisão).
- Findings classificados (informal: alta/média/baixa).
- Decisões: aceitar, mitigar, corrigir, waiver.
- Recomendação **Go / No-Go / Conditional Go** para Founder.

## 5. Operação manual hoje (Stage 0)

1. Trigger é ativado (automático conceitual + decisão Founder).
2. Kevin convoca especialistas conforme escopo (Vint infra, Oscar arquitetura).
3. Kevin produz threat model sistêmico ou atualiza existente.
4. Findings são classificados e cada um recebe decisão.
5. Waivers são explícitos quando aceitos.
6. Kevin emite recomendação para Founder.
7. Founder decide → SEC-GOV resolvido.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required:
    - trigger: enum (13 triggers — 9 canônicos + 4 CaM)
    - context: object
  optional: [das_ref, spec_ref, infra_arch_ref, previous_findings_refs]
outputs:
  - artifact: threat_model_systemic
  - array: findings (with classification and decision)
  - array: waivers (explicit)
  - field: recommendation (go|no_go|conditional_go)
tools_allowed:
  - codex.read / security.scan
  - fs.write (scoped to /project/{codinome}/security/)
tools_forbidden:
  - gate.approve (Kevin recomenda, Founder decide)
  - repo.write_source_code
gate:
  recommendation_authority: Kevin
  final_authority: Founder
abstention_rules:
  - critical_finding_without_decision
  - no_go_recommendation_overridden_without_rationale
  - cam_constitutional_violation_without_emenda
token_budget_heuristic: high
```

## 7. Anti-padrões

- Tratar SEC-GOV como fase obrigatória em toda demanda.
- Permitir que SEC-GOV decida sozinha.
- Skip de SEC-GOV antes de release final.
- Confundir SEC-GOV (sistêmica) com QA-SEC (operacional da demanda).
- Acumular gatilhos sem acionamento.
- No CaM: aprovar mudança em Risk Engine/kill switch/journal sem SEC-GOV.

## 8. Referências

- Governança: [`../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)
- Estados: [`BUG.md`](../../../teczi-devflow/NCC-1701/states/BUG.md), [`OPS.md`](../../../teczi-devflow/NCC-1701/states/OPS.md)
- Fases relacionadas: [`03-ARCH`](../../../teczi-devflow/NCC-1701/phases/03-ARCH.md), [`04-SPEC`](../../../teczi-devflow/NCC-1701/phases/04-SPEC.md), [`07-QA`](../../../teczi-devflow/NCC-1701/phases/07-QA.md), [`08-DEPLOY`](../../../teczi-devflow/NCC-1701/phases/08-DEPLOY.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 15º, 18º, 25º, 31º, 35º, 36º

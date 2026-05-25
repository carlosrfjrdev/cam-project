# Governança — SEC-GOV (Security Governance)

> **Codinome:** NCC-1701 · **Status:** Draft · **Tipo:** Governança transversal por gatilho
> **Dono:** Kevin
> **Decisão herdada:** SCOPE-FINAL §6.3 + §11 + Q2 Founder

## 1. Propósito

Revisão sistêmica de segurança, **fora do caminho feliz**, acionada por gatilho. SEC-GOV não é fase obrigatória — entra quando algum trigger objetivo aparece (ou quando o Founder solicita).

Não substitui `sec` intrabloco (CODE) nem QA-SEC (QA). É uma camada adicional para riscos acumulados ou sensíveis.

## 2. Gatilhos (quando acionar)

Lista canônica (SCOPE-FINAL §11.2):

1. **Auth / autorização** — qualquer mudança em fluxo de autenticação ou modelo de permissões.
2. **Dados sensíveis** — manipulação de dados pessoais, financeiros, de saúde, credenciais.
3. **Integração externa relevante** — nova integração com serviço externo crítico.
4. **Mudança em infra** — alterações em rede, deploy, ambiente, credenciais de infra.
5. **Release final** — antes de promover produto para versão final/produção real.
6. **Incidente** — após incidente de segurança ou bug crítico classificado como security.
7. **Exposição pública** — quando o produto/feature passa a ser exposto publicamente.
8. **Mudança em agentes/skills/permissão/Codex/CLI/MCP** — qualquer alteração no harness.
9. **Solicitação explícita de Carlos** — gatilho manual override.

## 3. Dono

**Kevin** (Information Security & Cyber Defense). Pode chamar especialistas pontuais conforme demanda (Vint para infra, Oscar para arquitetura).

## 4. Artefatos produzidos

| Artefato | Persistência |
|---|---|
| Threat model sistêmico (revisão) | `/projects/{produto}/security/` |
| Findings (riscos identificados, criticidade informal) | `/projects/{produto}/security/findings/` |
| Decisões: aceitar, mitigar, corrigir, waiver | Registrado em findings + DAS/ADR se afetar arquitetura |
| Recomendação Go / No-Go / Conditional Go | Resumo para Founder decidir |

## 5. Interação com fases e estados

| Onde atravessa | Como |
|---|---|
| ARCH | Threat model lógico, decisão arquitetural sensível |
| SPEC | Marcação `sec`/`qa-sec` decorrente de SEC-GOV |
| QA | QA-SEC pode receber escopo ampliado por SEC-GOV |
| DEPLOY | Gate adicional pré-release final |
| Estado BUG | Bug classificado como security incident dispara SEC-GOV |
| Estado OPS | CVE crítica, data incident, security incident disparam SEC-GOV |

## 6. Critério de saída / aprovação

- **Quem decide:** Founder
- **Critério de aprovação:** findings classificados, decisões tomadas para cada risco (aceitar/mitigar/corrigir), waivers explícitos quando houver, recomendação Kevin coerente com decisões do Founder.
- **Critério de retorno:** finding crítico aberto sem decisão, recomendação No-Go ignorada sem rationale.

## 7. Anti-padrões

- Tratar SEC-GOV como fase obrigatória em toda demanda — viola Q2 (por gatilho).
- Permitir que SEC-GOV decida sozinha (Kevin recomenda, Founder decide).
- Skip de SEC-GOV antes de release final — gatilho 5 obrigatório.
- Confundir SEC-GOV (sistêmica) com QA-SEC (operacional da demanda).
- Acumular gatilhos sem acionamento — vira dívida de segurança escondida.

## 8. Referências

- SCOPE-FINAL §6.3, §11, Q2
- Skill: [`../skills/teczi-security-governance.md`](../skills/teczi-security-governance.md)
- Fases relacionadas: [`../phases/03-ARCH.md`](../phases/03-ARCH.md), [`../phases/04-SPEC.md`](../phases/04-SPEC.md), [`../phases/07-QA.md`](../phases/07-QA.md), [`../phases/08-DEPLOY.md`](../phases/08-DEPLOY.md)
- Estados relacionados: [`../states/BUG.md`](../states/BUG.md), [`../states/OPS.md`](../states/OPS.md)

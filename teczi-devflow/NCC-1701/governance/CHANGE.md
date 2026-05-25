# Governança — CHANGE (Change Ledger)

> **Codinome:** NCC-1701 · **Status:** Draft · **Tipo:** Governança transversal dentro de DEPLOY
> **Donos:** Steve + Tom (Tom é dono do registro CHANGE-RECORD)
> **Decisão herdada:** SCOPE-FINAL §6.3 + §14 + Q2 Founder

## 1. Propósito

Registrar mudanças entregues — o que mudou, por que, impacto, versão, comunicação e rollback (quando aplicável). CHANGE **vive dentro** de DEPLOY (não é fase separada).

## 2. Quando acionar

**Sempre** que DEPLOY produz mudança que:

- altera comportamento visível ao usuário/operador;
- altera contrato (API, schema, payload);
- altera dados (migração, conversão);
- altera versão pública;
- exige comunicação (interna ou externa);
- pode requerer rollback.

Mudanças puramente internas e invisíveis (refator sem alteração de comportamento, mudança de comentário) podem ser registradas em commit message sem CHANGE-RECORD formal.

## 3. Donos

| Persona | Papel em CHANGE |
|---|---|
| **Steve** | Narrativa: o que mudou, para quem, por quê |
| **Tom** | Registro técnico: versionamento, tag, changelog, governança Git |

## 4. Artefatos produzidos

| Artefato | Template | Persistência |
|---|---|---|
| `CHANGE-RECORD.md` por DEPLOY | [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md) | `/projects/{produto}/changes/` |
| Tag git aplicada (quando há release real) | — | Repo do produto |
| Entrada em release notes (composta por Steve) | — | `/projects/{produto}/releases/` |

## 5. Conteúdo obrigatório de um CHANGE-RECORD

| Campo | Descrição |
|---|---|
| O que mudou | Descrição funcional |
| Por que mudou | Motivação (demanda, bug, decisão estratégica) |
| Impacto esperado | Quem é afetado e como |
| Versão interna | Tag/versionamento aplicado |
| Comunicação necessária | Onde e para quem comunicar (release notes, Slack, etc.) |
| Rollback | Plano se aplicável; "não aplicável" se não |
| Evidência | **Apenas se contexto exigir explicitamente** (Q14 Founder) |

## 6. Interação com fases e estados

| Onde atravessa | Como |
|---|---|
| DEPLOY | Vive aqui — é seção obrigatória do DEPLOY |
| QA | CHANGE-RECORD final reflete escopo validado em QA |
| BUG | Fix de BUG entra como CHANGE-RECORD no próximo DEPLOY |
| OPS | Mudança operacional relevante pode gerar CHANGE-RECORD |
| SDOC | DRIFT detectado pode disparar CHANGE-RECORD de reconciliação |

## 7. Versionamento

(SCOPE-FINAL §14.1 + Q16)

- **Comunicação externa:** sem tag de ciclo.
- **Comunicação interna pré-lançamento:** tags de ciclo podem aparecer.
- **SemVer externo:** apenas quando houver produto público com contrato externo.

## 8. Critério de saída / aprovação

- **Quem decide:** Founder (no gate de DEPLOY)
- **Critério de aprovação:** CHANGE-RECORD preenchido com os 6 campos obrigatórios, versionamento consistente, comunicação planejada.
- **Critério de retorno:** CHANGE-RECORD com campos vazios ou genéricos demais, rollback não considerado em mudança que exigiria.

## 9. Anti-padrões

- Deploy sem CHANGE-RECORD.
- CHANGE-RECORD com "tudo OK" sem descrição funcional.
- Tag em commit que não é release real.
- Evidência sempre obrigatória — Q14: apenas quando contexto exigir explicitamente.
- Comunicação externa com tag de ciclo (`INDEV`, `BETA`, etc.) — sem isso por padrão.

## 10. Referências

- SCOPE-FINAL §6.3, §14, Q14, Q16
- Template: [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md)
- Fase relacionada: [`../phases/08-DEPLOY.md`](../phases/08-DEPLOY.md)
- Skill DEPLOY: [`../skills/teczi-deploy.md`](../skills/teczi-deploy.md)

# Fase 08 — DEPLOY (Release & Deploy)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Steve + Tom (co-líderes) · **Executor:** Vint (com poder de No-Go operacional)
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 8) + §14 + Q13

## 1. Propósito

Materializar a entrega: release notes, versionamento, registro CHANGE, deploy operacional, smoke test e comunicação. Consolida o que antes eram fases separadas (RELEASE + INFRA-TODOS + CHANGELOG).

## 2. Quando rodar

- **Sempre que QA aprova entrega que vai para algum ambiente** (interno, beta, produção).

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Se houver release | Obrigatório se release | Obrigatório se release |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| Código aprovado em QA | QA | sim |
| SPEC.md aprovada | SPEC | sim |
| PLAN.md concluído | PLAN | sim |
| INFRA-ARCH atualizado (se aplicável) | ARCH | quando há impacto |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| Release notes | — (Steve compõe) | `/projects/{produto}/releases/` |
| Tag git + commit de release | — | Repo do produto |
| `CHANGE-RECORD.md` | [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md) | `/projects/{produto}/changes/` |
| INFRA-TODOS executados (evidência apenas se contexto exigir — Q14) | — | Issue tracker ou notas |
| Smoke test executado | — | Notas ou logs |
| `PROOF-PACK.md` se demanda M/G ou release final | [`../templates/PROOF-PACK.md`](../templates/PROOF-PACK.md) | `/projects/{produto}/proof-packs/` |

## 5. Personas

- **Co-lead:** Steve (release narrative) + Tom (versionamento, governança Git)
- **Executor:** Vint (deploy, smoke, No-Go operacional)
- **Cross-cutting:** Kevin se gatilho SEC-GOV (pré-FINAL, primeira produção, etc.)

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** release notes coerentes, tag aplicada, CHANGE-RECORD registrado, smoke OK, sem No-Go de Vint, SEC-GOV resolvido se acionado.
- **Critério de retorno:** smoke vermelho, No-Go de Vint, CHANGE-RECORD incompleto, SEC-GOV pendente.

## 7. Skill associada

[`../skills/teczi-deploy.md`](../skills/teczi-deploy.md)

## 8. Operação manual (Stage 0)

1. Steve redige release notes (o que mudou, para quem, por quê).
2. Tom decide versionamento (Q16: externo sem tag de ciclo; tags só pré-lançamento interno).
3. Tom registra CHANGE-RECORD.
4. Vint prepara ambiente, executa deploy, roda smoke.
5. Se gatilho SEC-GOV: Kevin entra antes do deploy final.
6. Founder aprova → DEPLOY concluído.
7. Se demanda M/G ou release final: registrar PROOF-PACK.

## 9. Anti-padrões

- Deploy sem CHANGE-RECORD.
- Aplicar tag em main sem release real.
- Skip de smoke test "porque é só uma correção".
- Ignorar No-Go de Vint.
- Promover release final sem acionar SEC-GOV quando há gatilho.

## 10. Referências

- SCOPE-FINAL §6.1, §14, Q13
- Skill: [`../skills/teczi-deploy.md`](../skills/teczi-deploy.md)
- Template: [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md), [`../templates/PROOF-PACK.md`](../templates/PROOF-PACK.md)
- Governanças relacionadas: [`../governance/CHANGE.md`](../governance/CHANGE.md), [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)
- Próxima fase: [`09-SDOC.md`](09-SDOC.md)

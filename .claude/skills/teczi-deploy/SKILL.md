---
name: teczi-deploy
description: "DEPLOY do Teczi DevFlow NCC-1701 (Steve + Tom, Vint executor). Acionar quando QA aprovou entrega: release notes (Steve), versionamento + CHANGE-RECORD (Tom), deploy + smoke (Vint). PROOF-PACK obrigatório se M/G ou release final. Comunicação externa SEM tag de ciclo. PROIBIDO commit em main, force push, skip de smoke."
phase: DEPLOY
lead_persona: Steve + Tom
executor_persona: Vint
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-deploy (Fase 8: DEPLOY)

> Skill da Fase 8 (DEPLOY) do NCC-1701. Leads: **Steve + Tom**. Executor: **Vint**.

## 1. Propósito

Materializar a entrega: release notes (Steve), versionamento e CHANGE-RECORD (Tom), deploy operacional e smoke (Vint).

## 2. Quando acionar

- QA aprovou entrega que vai para algum ambiente.

## 3. Entradas esperadas

- Código aprovado em QA.
- `SPEC.md` aprovada + `PLAN.md` concluído.
- `INFRA-ARCH.md` atualizado (se aplicável).

## 4. Saídas esperadas

- Release notes (Steve).
- Tag git + commit de release (Tom).
- `CHANGE-RECORD.md` (Tom).
- Smoke test executado (Vint).
- `PROOF-PACK.md` se M/G ou release final (R2 obrigatório).

## 5. Operação manual hoje (Stage 0)

1. Steve redige release notes.
2. Tom decide versionamento (Q16: comunicação externa **sem tag de ciclo**; SemVer externo só importa quando houver produto público).
3. Tom registra CHANGE-RECORD.
4. Vint prepara ambiente, executa deploy, roda smoke.
5. Se gatilho SEC-GOV: Kevin entra antes do deploy final (aciona [teczi-security-governance](../teczi-security-governance/SKILL.md)).
6. Founder aprova → DEPLOY concluído.
7. Se M/G ou release final: registrar PROOF-PACK.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [qa_approval_ref, spec_ref, plan_ref]
  optional: [infra_arch_ref]
outputs:
  - artifact: release_notes
  - artifact: CHANGE-RECORD.md
  - tag: git_tag (when applicable)
  - field: smoke_status
  - artifact: PROOF-PACK.md (when M/G or final release)
tools_allowed:
  - git.tag / git.commit (release commit)
  - deploy.execute (scoped to /apps/{codinome}/)
  - smoke.run
  - fs.write (scoped to /project/{codinome}/changes/, /releases/)
tools_forbidden:
  - git.push.main (without explicit Founder approval)
  - tag.external_with_cycle (Q16 proíbe tags INDEV/BETA externamente)
  - force_push / rebase / amend
gate:
  required_approval: Founder
  optional_blocker: Vint (No-Go operacional)
  optional_blocker: Kevin (SEC-GOV when triggered)
abstention_rules:
  - smoke_red
  - vint_no_go
  - sec_gov_pending
  - change_record_incomplete
token_budget_heuristic: medium
```

## 7. Anti-padrões

- Deploy sem CHANGE-RECORD.
- Tag em commit que não é release real.
- Skip de smoke "porque é só uma correção".
- Ignorar No-Go de Vint.
- Promover release final sem acionar SEC-GOV quando há gatilho.
- Force push / rebase / amend / commit em main — proibidos.

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/08-DEPLOY.md`](../../../teczi-devflow/NCC-1701/phases/08-DEPLOY.md)
- Templates: [`CHANGE-RECORD.md`](../../../teczi-devflow/NCC-1701/templates/CHANGE-RECORD.md), [`PROOF-PACK.md`](../../../teczi-devflow/NCC-1701/templates/PROOF-PACK.md)
- Governanças: [`CHANGE.md`](../../../teczi-devflow/NCC-1701/governance/CHANGE.md), [`SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)

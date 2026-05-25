---
skill: teczi-deploy
phase: DEPLOY
status: draft
lead_persona: Steve + Tom
executor_persona: Vint
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-deploy

## 1. Propósito

Materializar a entrega: release notes (Steve), versionamento e CHANGE-RECORD (Tom), deploy operacional e smoke (Vint).

## 2. Quando acionar

- QA aprovou entrega que vai para algum ambiente.

## 3. Entradas esperadas

- Código aprovado em QA.
- `SPEC.md` aprovada.
- `PLAN.md` concluído.
- `INFRA-ARCH.md` atualizado (se aplicável).

## 4. Saídas esperadas

- Release notes (Steve).
- Tag git + commit de release (Tom).
- `CHANGE-RECORD.md` (Tom).
- INFRA-TODOS executados (evidência apenas se contexto exigir — Q14).
- Smoke test executado (Vint).
- `PROOF-PACK.md` se M/G ou release final (R2 obrigatório).

## 5. Operação manual hoje (Stage 0)

1. Steve redige release notes.
2. Tom decide versionamento (Q16: externo sem tag de ciclo).
3. Tom registra CHANGE-RECORD.
4. Vint prepara ambiente, executa deploy, roda smoke.
5. Se gatilho SEC-GOV: Kevin entra antes do deploy final.
6. Founder aprova → DEPLOY concluído.
7. Se M/G ou release final: registrar PROOF-PACK.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - qa_approval_ref: artifact_ref
    - spec_ref: artifact_ref
    - plan_ref: artifact_ref
  optional:
    - infra_arch_ref: artifact_ref
outputs:
  - artifact: release_notes
  - artifact: CHANGE-RECORD.md
  - tag: git_tag (when applicable)
  - field: smoke_status
  - artifact: PROOF-PACK.md (when M/G or final release)
tools_allowed:
  - git.tag
  - git.commit (release commit)
  - deploy.execute (scoped to product)
  - smoke.run
  - fs.write (scoped to /projects/{product}/changes/, /releases/, /proof-packs/)
tools_forbidden:
  - git.push.main (without explicit Founder approval)
  - tag.external_with_cycle (Q16 forbids INDEV/BETA cycle tags externally)
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

## 8. Referências

- Fase: [`../phases/08-DEPLOY.md`](../phases/08-DEPLOY.md)
- Templates: [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md), [`../templates/PROOF-PACK.md`](../templates/PROOF-PACK.md)
- Governanças: [`../governance/CHANGE.md`](../governance/CHANGE.md), [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)

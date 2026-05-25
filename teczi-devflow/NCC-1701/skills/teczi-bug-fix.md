---
skill: teczi-bug-fix
state: BUG
status: draft
lead_persona: Bill
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-bug-fix

## 1. Propósito

Conduzir correção rápida de defeito real ou regressão, com RCA proporcional, fix e reteste — em **artefato único** (`BUG-{id}.md`).

## 2. Quando acionar

- Defeito reproduzível em produto vigente.
- Regressão detectada em QA, OPS ou pelo Founder/usuário.

**Não usar** para: melhoria, nova funcionalidade ou dívida técnica conhecida.

## 3. Entradas esperadas

- Descrição do defeito (passos, esperado, real).
- Ambiente onde ocorre.
- SPEC/contrato violado se identificável.

## 4. Saídas esperadas

- `BUG-{id}.md` (artefato único: RCA + fix + reteste).
- Commit de correção.
- Entrada no `CHANGE-RECORD.md` do próximo DEPLOY.
- `PROOF-PACK.md` se bug crítico/incidente (R2 obrigatório).

## 5. Operação manual hoje (Stage 0)

1. Founder/QA/OPS reporta defeito reproduzível.
2. Bill confirma reprodução e classifica severidade informal (alta/média/baixa).
3. Bill conduz RCA proporcional:
   - **alta**: RCA completa.
   - **média**: RCA curta.
   - **baixa**: nota direta.
4. Nikola implementa fix.
5. Linus reteste; Kevin se security; Vint se operacional.
6. Bill consolida em `BUG-{id}.md`.
7. Founder valida → DEPLOY com CHANGE-RECORD.
8. Se crítico/incidente: PROOF-PACK obrigatório.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - bug_report: object {steps, expected, actual, environment}
  optional:
    - violated_contract_ref: artifact_ref
outputs:
  - artifact: BUG-{id}.md (single artifact: RCA + fix + retest)
  - commit_ref: fix_commit
  - change_record_entry: object (for next DEPLOY)
  - artifact: PROOF-PACK.md (when critical/incident)
tools_allowed:
  - repo.write_source_code (fix only)
  - repo.commit
  - tests.run
  - fs.write (scoped to /projects/{product}/bugs/)
tools_forbidden:
  - git.push.main
  - gate.approve
  - new_feature_implementation (não é BUG)
gate:
  required_approval: Founder
abstention_rules:
  - rca_superficial
  - fix_without_retest
  - regression_induced_by_fix
  - sec_incident_without_sec_gov_trigger
token_budget_heuristic: low to medium
```

## 7. Anti-padrões

- BUG para nova funcionalidade.
- Fragmentar fast-track em SPEC+PLAN+CODE+QA+DEPLOY separados (é artefato **único**).
- Skip do reteste.
- Esquecer CHANGE-RECORD no DEPLOY.
- Não acionar SEC-GOV quando é security incident.

## 8. Referências

- Estado: [`../states/BUG.md`](../states/BUG.md)
- Template: [`../templates/BUG.md`](../templates/BUG.md)
- Governanças: [`../governance/CHANGE.md`](../governance/CHANGE.md), [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)

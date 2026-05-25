---
name: teczi-bug-fix
description: "Estado BUG do Teczi DevFlow NCC-1701 (Bill). Acionar para correção rápida de defeito reproduzível ou regressão — artefato ÚNICO (BUG-{id}.md combinando RCA + fix + reteste). Não usar para melhoria, nova funcionalidade ou tech debt conhecida. PROOF-PACK obrigatório se crítico/incidente. No CaM, bug em Risk Engine/kill switch/journal sempre escala para SEC-GOV (Kevin)."
state: BUG
lead_persona: Bill
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-bug-fix (Estado BUG)

> Skill do estado **BUG** (fast-track) do NCC-1701. Lead: **Bill**.

## 1. Propósito

Conduzir correção rápida de defeito real ou regressão, com RCA proporcional, fix e reteste — em **artefato único** (`BUG-{id}.md`).

## 2. Quando acionar

- Defeito reproduzível em aplicativo CaM vigente.
- Regressão detectada em QA, OPS ou pelo Founder.

**Não usar** para: melhoria, nova funcionalidade ou dívida técnica conhecida.

## 3. Entradas esperadas

- Descrição do defeito (passos, esperado, real).
- Ambiente onde ocorre.
- SPEC/contrato violado se identificável.

## 4. Saídas esperadas

- `BUG-{id}.md` em `/project/{codinome}/demands/{demand_id}/BUG/` (artefato único: RCA + fix + reteste).
- Commit de correção em `/apps/{codinome}/`.
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
6. **No CaM:** bug em Risk Engine, kill switch, journal ou provisão fiscal sempre escala para SEC-GOV (aciona [teczi-security-governance](../teczi-security-governance/SKILL.md)).
7. Bill consolida em `BUG-{id}.md`.
8. Founder valida → DEPLOY com CHANGE-RECORD.
9. Se crítico/incidente: PROOF-PACK obrigatório.

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required:
    - bug_report: object {steps, expected, actual, environment}
  optional: [violated_contract_ref]
outputs:
  - artifact: BUG-{id}.md (RCA + fix + retest)
  - commit_ref: fix_commit
  - change_record_entry: object
  - artifact: PROOF-PACK.md (when critical/incident)
tools_allowed:
  - repo.write_source_code (fix only, scoped to /apps/{codinome}/)
  - repo.commit
  - tests.run
  - fs.write (scoped to /project/{codinome}/demands/{id}/BUG/)
tools_forbidden:
  - git.push.main
  - gate.approve
  - new_feature_implementation
gate:
  required_approval: Founder
abstention_rules:
  - rca_superficial
  - fix_without_retest
  - regression_induced_by_fix
  - sec_incident_without_sec_gov_trigger
  - cam_critical_path_bug_without_sec_gov (Risk Engine/kill switch/journal/fiscal)
token_budget_heuristic: low to medium
```

## 7. Anti-padrões

- BUG para nova funcionalidade.
- Fragmentar fast-track em SPEC+PLAN+CODE+QA+DEPLOY separados (é artefato **único**).
- Skip do reteste.
- Esquecer CHANGE-RECORD no DEPLOY.
- Não acionar SEC-GOV quando é security incident.
- No CaM: tratar bug em Risk Engine ou kill switch como bug "comum" — escala constitucional automática.

## 8. Referências

- Estado: [`../../../teczi-devflow/NCC-1701/states/BUG.md`](../../../teczi-devflow/NCC-1701/states/BUG.md)
- Template: [`BUG.md`](../../../teczi-devflow/NCC-1701/templates/BUG.md)
- Governanças: [`CHANGE.md`](../../../teczi-devflow/NCC-1701/governance/CHANGE.md), [`SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)
- Constituição: [`CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 15º, 18º, 25º, 31º

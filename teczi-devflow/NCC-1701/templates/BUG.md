---
template: BUG
state: BUG
status: stable
---

# BUG-{ID} — {Resumo curto}

> **Data:** {YYYY-MM-DD}
> **Status:** Open | Fixed | Reverted
> **Severidade informal:** Alta | Média | Baixa
> **Produto:** {nome}
> **Lead:** Bill (orquestrador)
> **Aprovador:** Founder

> **Artefato único** — RCA + Fix + Reteste neste mesmo arquivo. Não fragmentar em SPEC/PLAN/CODE/QA/DEPLOY separados.

---

## 1. Reprodução

| Campo | Valor |
|---|---|
| Passos | 1. ... 2. ... 3. ... |
| Esperado | ... |
| Real | ... |
| Ambiente | ... |
| Versão / commit | ... |

## 2. Severidade e classificação

- **Severidade informal:** Alta / Média / Baixa
- **É security incident?** sim/não — se sim, acionar [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)
- **É incidente operacional?** sim/não — se sim, criar [`OPS-EVENT.md`](OPS-EVENT.md) associado

## 3. RCA (proporcional)

### Para severidade **Alta**
- **Causa raiz:**
- **Escopo de impacto:**
- **Por que passou despercebido:**
- **Lição:**

### Para severidade **Média**
- **Causa:**
- **Correção proposta:**

### Para severidade **Baixa**
- Nota direta: ...

## 4. Fix

- **Commit:** {hash}
- **Branch:** {branch}
- **Arquivos afetados:** ...

## 5. Reteste

- **Cenário do bug:** OK / Falha
- **Regressão próxima:** OK / Falha
- **Reteste por:** Linus
- **Data:** {YYYY-MM-DD}

## 6. CHANGE-RECORD associado

→ [`CHANGE-RECORD-{deploy_id}.md`](...) quando entrar no próximo DEPLOY.

## 7. PROOF-PACK

- Obrigatório se severidade **Alta** ou se classificado como incidente crítico.
- → [`PROOF-PACK-{id}.md`](...)

## 8. Aprovação do Founder

- **Status:** Aprovado / Pendente
- **Data:** ...

---

## Quando NÃO usar este template

- Para nova funcionalidade ou melhoria: usar [`SPEC.md`](SPEC.md) (fluxo normal).
- Para dívida técnica conhecida: registrar em `tech-debt/`, não em BUG.
- Para evento operacional sem defeito: usar [`OPS-EVENT.md`](OPS-EVENT.md).

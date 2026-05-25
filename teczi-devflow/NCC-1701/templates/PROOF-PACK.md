---
template: PROOF-PACK
phase: pós-demanda (M/G ou release final ou incidente ou arch change)
status: stable
---

# PROOF-PACK-{ID} — {Demanda / Release / Incidente}

> **Data:** {YYYY-MM-DD}
> **Tipo:** Demanda M | Demanda G | Release final | Bug crítico/incidente | Mudança arquitetural
> **Produto:** {nome}
> **Obrigatoriedade:** Proporcional (R2 desta versão · ajuste GPT-PARECER §5.3 incorporado)

| Demanda | Proof Pack |
|---|---|
| **P** | Opcional |
| **M** | Recomendado |
| **G** | Obrigatório |
| Release final | Obrigatório |
| Bug crítico / incidente | Obrigatório |
| Mudança arquitetural | Obrigatório |

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Demanda / Evento | {SPEC-XXX, BUG-XXX, OPS-EVENT-XXX, etc.} |
| Classificação P/M/G | P / M / G (se aplicável) |
| Período | {data início} – {data fim} |

## 2. Fases usadas vs puladas

| Fase | Usada? | Por quê |
|---|---|---|
| PDOC | sim/não/skip | ... |
| DISC | sim/não/skip | ... |
| ARCH | sim/não/skip | ... |
| SPEC | sim/não/skip | ... |
| PLAN | sim/não/skip | ... |
| CODE | sim/não/skip | ... |
| QA | sim/não/skip | ... |
| DEPLOY | sim/não/skip | ... |
| SDOC | sim/não/skip | ... |

## 3. Estados acionados

- BUG: sim/não · ID(s)
- OPS: sim/não · evento(s)
- SEC-GOV: sim/não · gatilho

## 4. Decisões do Founder relevantes

| # | Decisão | Quando |
|---|---|---|
| 1 | ... | ... |

## 5. Artefatos produzidos

Lista com link relativo.

- SCOPE: ...
- SPEC: ...
- PLAN: ...
- DAS / ADRs atualizados: ...
- CHANGE-RECORD: ...
- BUG: ...
- DRIFT-REPORT: ...

## 6. Bugs / retrabalho

- Bugs encontrados durante a demanda: ...
- Retrabalho em gates: ...
- Iterações Albert-Nico (P/M/G): ...

## 7. Métricas observadas

Conjunto inicial inferido (~9 métricas — Q19 Founder · SCOPE-FINAL §15.1).

| Métrica | Valor / Observação |
|---|---|
| `founderContextReloadCount` | ... |
| `reuseRate` | ... |
| `gateReworkRate` | ... |
| `escapedDefects` | ... |
| `driftDetectedCount` | ... |
| `claimSourceCoverage` | ... |
| `tokenCostByPhase` | ... |
| `artifactJunkScore` | ... |
| `policyViolations` | ... (quando houver Control Plane) |

## 8. Custo de tokens (quando disponível)

Aproximação por fase.

## 9. Evidências técnicas (quando contexto exigir)

Build, testes, scans, screenshots, smoke. **Apenas se contexto exige** — Q14 Founder.

## 10. O que foi cortado por ser lixo

Documentação/artefatos planejados mas descartados por não agregar.

## 11. Aprendizado para subversão futura

- Sinais de gargalo: ...
- Sinais de proporcionalidade quebrada: ...
- Recomendações para v6.x: ...

---

## Quando NÃO usar este template

- Para demanda P sem necessidade especial: opcional — pode pular.
- Para refator interno trivial: não cabe.
- Não fingir métricas — quando não houver dado, marcar `n/a` ou `não medido`.
- Não inferir custo monetário sem fonte (apenas tokens aproximados quando disponíveis).

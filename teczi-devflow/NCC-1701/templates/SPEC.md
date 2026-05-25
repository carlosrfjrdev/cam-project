---
template: SPEC
phase: SPEC
status: stable
---

# SPEC — {ID da demanda} · {Título}

> **Data:** {YYYY-MM-DD}
> **Status:** Draft | Approved | Superseded
> **Produto:** {nome}
> **Lead:** Albert
> **Aprovador:** Founder

---

## 1. Resumo

Uma frase: o que esta demanda especifica.

## 2. Referências de entrada

- SCOPE: [`SCOPE-{ID}.md`](...) — aprovado em {data}
- DVP vigente: ...
- DAS vigente: ...
- ADRs aplicáveis: ...

## 3. Regras de negócio

Lista clara, sem ambiguidade.

- R1. ...
- R2. ...

## 4. Contratos

APIs, schemas, payloads, eventos.

## 5. Casos de uso / cenários

| # | Caso | Esperado |
|---|---|---|
| 1 | ... | ... |

## 6. Casos limite / exceções

- ...

## 7. Classificação P/M/G

| Campo | Valor |
|---|---|
| Classe | **P** \| **M** \| **G** |
| Rationale | (1 parágrafo curto: por que essa classe) |

(Lembrete: P = subitem de funcionalidade existente · M = melhoria ou nova funcionalidade · G = N funcionalidades / decomposição. **Sem modificadores de risco** — Q8 Founder.)

## 8. Marcadores de segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (check intrabloco no CODE) | sim / não | ... |
| `qa-sec` (QA-SEC no QA) | sim / não | ... |

(Se algum `sim`, Kevin entra cross-cutting nas fases marcadas. Se gatilho SEC-GOV, ver [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md).)

## 9. Saídas esperadas

O que a demanda deve produzir como entrega visível.

## 10. Critérios de aceite

Como QA validará. Cenários + critério objetivo de Go.

## 11. Delta no DVP (se aplicável)

Se a demanda altera direção estratégica, registrar mudança aqui e atualizar DVP.

## 12. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | {data} | Draft inicial | — |

---

## Quando NÃO usar este template

- Para BUG: usar [`BUG.md`](BUG.md).
- Para SCOPE pré-SPEC: usar [`SCOPE.md`](SCOPE.md).
- Não introduzir modificadores `risk`, `security`, `architectureImpact`, `releaseImpact` — Q8 Founder.
- Não estimar tempo em qualquer unidade.

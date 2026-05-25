---
template: PLAN
phase: PLAN
status: stable
---

# PLAN — {ID da demanda} · {Título}

> **Data:** {YYYY-MM-DD}
> **Status:** Draft | Approved (`letscode`) | Superseded
> **Produto:** {nome}
> **Lead:** Nico
> **Co-lead:** Albert (loop P/M/G)
> **Aprovador:** Founder

---

## 1. Resumo do plano

Uma frase: como vamos executar.

## 2. Referência de entrada

- SPEC: [`SPEC-{ID}.md`](...) — aprovada em {data}
- DAS vigente: ...

## 3. Avaliação de P/M/G

| Campo | Valor |
|---|---|
| Classe na SPEC | P / M / G |
| Concordância de Nico | sim / não |
| Re-classificação proposta | (se aplicável) + rationale |
| Loop com Albert | (registrar trocas relevantes) |
| Decisão final | (após Founder validar) |

## 4. Blocos / TASKs

### Para P
- Bloco único; descrição direta.

### Para M
| # | Bloco | Saída esperada |
|---|---|---|
| 1 | ... | ... |
| 2 | ... | ... |

### Para G
| # | TASK | Saída esperada | Bloco pai | Depende de |
|---|---|---|---|---|
| T1 | ... | ... | B1 | — |
| T2 | ... | ... | B1 | T1 |

## 5. Dependências externas

- ...

## 6. Riscos identificados

- ...

## 7. Reuso aplicado

Antes de gerar novo código/artefato, o que foi reaproveitado (decisão, padrão, componente, teste, ADR).

## 8. `letscode`

| Campo | Valor |
|---|---|
| Status | `false` / `true` |
| Aprovado por | Founder em {data} |
| Motivo se `false` ainda | ... |

(Quando `true`, CODE pode iniciar.)

## 9. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | {data} | Draft inicial | — |

---

## Quando NÃO usar este template

- Para BUG: usar [`BUG.md`](BUG.md) (fast-track).
- Para demanda P trivial: o PLAN pode ser **embutido na SPEC** em uma seção curta — não exige arquivo separado.
- **Não inferir estimativas em horas/dias/semanas** — Founder proíbe.
- Não definir tecnologia/stack — isso é ARCH.

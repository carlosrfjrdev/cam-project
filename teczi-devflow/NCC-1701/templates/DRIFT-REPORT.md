---
template: DRIFT-REPORT
phase: SDOC (sob solicitação)
status: stable
---

# DRIFT-REPORT-{ID} — {Produto}

> **Data:** {YYYY-MM-DD}
> **Status:** Draft | Reconciled | Pending Decision
> **Acionamento:** Solicitação explícita do Founder em {data} (Q12 Founder)
> **Lead:** Howard

> Este template **só é usado por solicitação explícita do Founder**. Não há gatilhos automáticos nem gatilhos "recomendados".

---

## 1. Escopo da revisão

O que foi inspecionado (módulo, produto, área).

## 2. Comparação intenção × estado real

| Aspecto | Intenção (`project`) | Estado real (`codex`) | Divergência |
|---|---|---|---|
| ... | DVP/DAS/SPEC diz: ... | Código real faz: ... | sim/não |
| ... | ... | ... | ... |

## 3. Tipos de drift observados

- [ ] Documentação descreve algo que não existe mais.
- [ ] Código existe sem documentação correspondente.
- [ ] Comportamento difere do contrato declarado.
- [ ] Decisão arquitetural antiga foi superada na prática.
- [ ] ADR vigente conflita com código real.

## 4. Direção de reconciliação proposta

Para cada divergência, propor:

| # | Divergência | Direção | Custo qualitativo |
|---|---|---|---|
| 1 | ... | ajustar código / ajustar intenção / aceitar drift | baixo / médio / alto |

(Princípio 7: "Estado real vence" — quando código real está coerente com necessidade atual, ajustar a documentação. Quando código real está errado, ajustar código.)

## 5. Decisão do Founder

| # | Direção aprovada | Demanda associada (se exige) |
|---|---|---|
| 1 | ... | ... |

## 6. Próximos passos

- ...

## 7. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | {data} | Draft inicial | — |

---

## Quando NÃO usar este template

- **Automaticamente após DEPLOY** — Q12 Founder proíbe.
- **Por "gatilhos recomendados"** — descartado nesta versão (ajuste GPT-PARECER §4.2 não incorporado).
- Para documentar estado real sem comparação com intenção: usar SDOC normal, não DRIFT-REPORT.
- Para registrar bug: usar [`BUG.md`](BUG.md).

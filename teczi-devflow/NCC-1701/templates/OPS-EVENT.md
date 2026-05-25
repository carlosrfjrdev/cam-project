---
template: OPS-EVENT
state: OPS
status: stable (minimal — Q15 Founder)
---

# OPS-EVENT-{ID} — {Resumo curto}

> **Template mínimo** — não fingir taxonomia que ainda não temos.
> **Refinamento de OPS:** adiado até primeiro produto em versão final (Q15 Founder).
> **Ajuste GPT-PARECER §5.5:** incorporado nesta versão para impedir perda de histórico operacional.

> **Lead:** Vint
> **Status:** Open | Closed

---

## 1. Data

{YYYY-MM-DD HH:MM (timezone)}

## 2. Evento

Descrição curta do que aconteceu.

## 3. Impacto

Quem foi afetado · qual produto · qual ambiente · degradação observada.

## 4. Decisão

O que foi decidido fazer (e por quem).

## 5. Ação tomada

O que efetivamente foi executado.

## 6. Rollback (se aplicável)

Se houve rollback: o que foi revertido, quando, com qual efeito.

## 7. Aprendizado

Uma a três linhas. Não é RCA formal — apenas o que ficou claro depois.

## 8. Artefatos associados (se houver)

- BUG: [`BUG-{id}.md`](BUG.md)
- CHANGE-RECORD: [`CHANGE-RECORD-{id}.md`](CHANGE-RECORD.md)
- SEC-GOV trigger: sim/não
- PROOF-PACK: [`PROOF-PACK-{id}.md`](PROOF-PACK.md) (obrigatório se incidente)

---

## Quando NÃO usar este template

- Para defeito reproduzível em código: usar [`BUG.md`](BUG.md).
- Para registrar release/deploy normal sem incidente: usar [`CHANGE-RECORD.md`](CHANGE-RECORD.md).
- **Não criar taxonomia de tipos de evento** — Q15 Founder. Texto livre no campo "Evento" é suficiente nesta fase.
- **Não criar classificação formal de severidade** — apenas referenciar (alta/média/baixa) no texto se ajudar a decisão.

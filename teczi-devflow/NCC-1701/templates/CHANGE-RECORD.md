---
template: CHANGE-RECORD
phase: DEPLOY
governance: CHANGE
status: stable
---

# CHANGE-RECORD-{ID} — {Resumo curto}

> **Data:** {YYYY-MM-DD}
> **Produto:** {nome}
> **Lead:** Tom (registro) · Steve (narrativa) · Vint (executor)
> **Aprovador:** Founder

---

## 1. O que mudou

Descrição funcional clara.

## 2. Por que mudou

Demanda? Bug? Decisão estratégica? Referenciar SPEC/BUG/ADR associado.

## 3. Impacto esperado

Quem é afetado · como · quando começa.

## 4. Versão interna

| Campo | Valor |
|---|---|
| Tag | {ex.: v0.3.1 ou v0.4.0-internal} |
| Commit | {hash} |
| Branch | {branch} |
| Pré-lançamento | sim/não |

(Lembrete: **externo sem tag de ciclo** — Q16. Tags `INDEV/BETA/FINAL` só aparecem em comunicação interna pré-lançamento.)

## 5. Comunicação necessária

| Canal | Audiência | Mensagem-chave |
|---|---|---|
| Release notes | Usuários | ... |
| Slack interno (se houver) | Time / Founder | ... |
| Outros | ... | ... |

## 6. Rollback

| Campo | Valor |
|---|---|
| Aplicável | sim/não |
| Plano (se sim) | ... |
| Janela viável | ... |

## 7. Evidência

**Apenas se contexto exigir explicitamente** (Q14 Founder).

Exemplos quando contexto exige:
- migração de dados destrutiva;
- mudança de contrato externo;
- alteração de segurança.

Se não se aplica: "Não aplicável neste contexto."

## 8. Artefatos relacionados

- SPEC: ...
- PLAN: ...
- BUG (se fix): ...
- INFRA-ARCH (se infra): ...
- SEC-GOV (se acionado): ...
- PROOF-PACK (se M/G ou release final): [`PROOF-PACK-{id}.md`](PROOF-PACK.md)

---

## Quando NÃO usar este template

- Para refator interno sem alteração de comportamento visível: commit message é suficiente.
- Para evento operacional sem mudança deployada: usar [`OPS-EVENT.md`](OPS-EVENT.md).
- Não aplicar tag em commit que **não é release real**.
- Não usar tags de ciclo (`INDEV`, `BETA`) em comunicação externa — Q16 Founder.

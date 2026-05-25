# Fase 04 — SPEC (Specification)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Albert
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 4) + §7

## 1. Propósito

Especificar a demanda: regras de negócio, contratos, P/M/G, aplicabilidade de segurança (`sec`/`qa-sec`), saídas esperadas. SPEC é o terreno onde código nasce.

## 2. Quando rodar

- **Toda demanda** que não é BUG. Sem SPEC, não há CODE.

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Enxuta | Completa na demanda | Completa e estruturada |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| SCOPE.md aprovado | DISC | sim |
| DVP vigente | DISC/SPEC anterior | quando houver |
| DAS vigente | ARCH | quando houver |
| ADRs aplicáveis | ARCH | quando houver |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `SPEC.md` da demanda | [`../templates/SPEC.md`](../templates/SPEC.md) | `/projects/{produto}/demands/{id}/` |
| Classificação P/M/G | Campo dentro do SPEC | — |
| Marcadores `sec` e `qa-sec` quando aplicáveis | Campos dentro do SPEC | — |
| Delta no DVP (se a demanda afeta direção estratégica) | DVP vigente | `/projects/{produto}/strategy/` |

## 5. Personas

- **Lead:** Albert (Specification & Vision)
- **Co-lead:** Nico tem direito formal de criticar P/M/G no PLAN
- **Cross-cutting:** Kevin marca `sec`/`qa-sec` quando superfície sensível

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** regras explícitas, P/M/G atribuído, `sec`/`qa-sec` marcados, saídas esperadas claras.
- **Critério de retorno:** regras ambíguas, P/M/G sem justificativa, ausência de marcação de segurança em superfície sensível.

## 7. Skill associada

[`../skills/teczi-demand-specification.md`](../skills/teczi-demand-specification.md)

## 8. Operação manual (Stage 0)

1. Albert lê SCOPE + DVP + DAS + ADRs.
2. Albert produz SPEC: regras, contratos, exemplos, casos limite.
3. Albert atribui P/M/G inicial (regra: P = subitem; M = melhoria/nova func.; G = N funcionalidades).
4. Kevin marca `sec`/`qa-sec` se houver superfície sensível.
5. Se SPEC altera direção estratégica: Albert atualiza DVP (delta).
6. Founder aprova SPEC → segue para PLAN.

## 9. Anti-padrões

- SPEC sem classificação P/M/G.
- Modificadores de risco (`risk`, `security`, `architectureImpact`, `releaseImpact`) — Q8 Founder considera overengineering. **Não usar.**
- Esconder regras de negócio em comentários de código.
- Especificar tecnologia/stack — isso é da ARCH/PLAN, não da SPEC.

## 10. Referências

- SCOPE-FINAL §6.1 e §7
- Skill: [`../skills/teczi-demand-specification.md`](../skills/teczi-demand-specification.md)
- Template: [`../templates/SPEC.md`](../templates/SPEC.md)
- Próxima fase: [`05-PLAN.md`](05-PLAN.md)

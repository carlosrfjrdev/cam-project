# Fase 02 — DISC (Discovery)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Marty
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 2)

## 1. Propósito

Delimitar a oportunidade real da demanda: o que está dentro, fora e adiado; o que se sabe, o que se assume, o que falta perguntar. Evita feature factory.

## 2. Quando rodar

- **Sempre que a demanda tem ambiguidade** sobre escopo, problema ou usuário.
- **Sempre que nasce um produto novo** (DVP inicial nasce aqui).
- **Skip** apenas se a demanda é um ajuste mecânico de funcionalidade existente sem ambiguidade.

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Condicional se ambígua | Recomendado | Obrigatório se nova/ambígua |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| Intenção do Founder (verbal/textual) | Founder | sim |
| Contexto do produto existente (se aplicável) | Repositório / DVP anterior | condicional |
| Artefatos vivos relacionados | Workspace | quando houver |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `SCOPE.md` da demanda (In/Out/Later + perguntas abertas) | [`../templates/SCOPE.md`](../templates/SCOPE.md) | `/projects/{produto}/demands/{id}/` |
| `DVP.md` inicial (se produto novo) | [`../templates/DVP.md`](../templates/DVP.md) | `/projects/{produto}/strategy/` |
| DISC-UX (workstream, se gatilho ativo) | — | `/projects/{produto}/ux/` |

### DISC-UX

Workstream com gate próprio. Ativa por:
- gatilho informado pelo Founder; ou
- alteração crítica de Design System / frontend.

(Q10 Founder)

## 5. Personas

- **Lead:** Marty (Product Discovery)
- **Co-lead:** Andy quando DISC-UX ativa
- **Cross-cutting:** Sun se houver questão estratégica

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** SCOPE.md aprovado; perguntas abertas endereçadas ou marcadas como assumidas; DVP atualizado se aplicável.
- **Critério de retorno:** escopo ainda ambíguo ou contém solução prematura.

## 7. Skill associada

[`../skills/teczi-project-discovery.md`](../skills/teczi-project-discovery.md)

## 8. Operação manual (Stage 0)

1. Founder descreve a demanda em texto livre.
2. Marty conduz refinamento: problema, usuário, resultado esperado, sinais de sucesso.
3. Marty produz `SCOPE.md` (In/Out/Later + perguntas abertas).
4. Se produto novo: Marty + Founder produzem `DVP.md` inicial.
5. Se gatilho UX: Andy entra em workstream paralelo.
6. Founder aprova SCOPE → DISC concluída.

## 9. Anti-padrões

- Transformar DISC em SPEC (definir regras técnicas, contratos, schemas — isso é da SPEC).
- Transformar DISC em PLAN (decidir blocos de execução, ordem de TASKs).
- Esconder perguntas em aberto como se já estivessem respondidas.
- Inferir DVP completo quando o produto ainda não tem direção mínima.

## 10. Referências

- SCOPE-FINAL §6.1
- Skill: [`../skills/teczi-project-discovery.md`](../skills/teczi-project-discovery.md)
- Template: [`../templates/SCOPE.md`](../templates/SCOPE.md), [`../templates/DVP.md`](../templates/DVP.md)
- Origem conceitual: [`projects/devflow/REVIEW-Teczi-Project-Discovery-SCOPE-Enxuto.md`](../../../projects/devflow/REVIEW-Teczi-Project-Discovery-SCOPE-Enxuto.md)
- Próxima fase: [`03-ARCH.md`](03-ARCH.md)

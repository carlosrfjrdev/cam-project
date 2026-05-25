# Fase 06 — CODE (Execution)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Nikola
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 6)

## 1. Propósito

Implementar o bloco/demanda dentro do escopo aprovado em SPEC + PLAN. CODE não decide arquitetura nem regras — apenas materializa.

## 2. Quando rodar

- **Toda demanda que produz código**, após `letscode` aceso.

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Direto e localizado | Blocos contidos | Blocos sequenciais por TASK |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| SPEC.md aprovada | SPEC | sim |
| PLAN.md com `letscode` | PLAN | sim |
| DAS / ADRs vigentes | ARCH | quando aplicável |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| Código + commits no repositório do produto | — | Repo do produto |
| Tech debt registrado se gerado | Nota em SPEC/PLAN ou commit | `/projects/{produto}/tech-debt/` quando relevante |
| Resumo do bloco implementado | Nota em PLAN ou commit message | — |

## 5. Personas

- **Lead:** Nikola (Development)
- **Co-lead:** —
- **Cross-cutting:** Linus intrabloco sempre; Kevin intrabloco se `sec` marcado na SPEC

## 6. Gate de saída

- **Quem decide:** Founder (após build/checks)
- **Critério de aprovação:** build verde, checks intrabloco OK, escopo respeitado.
- **Critério de retorno:** build vermelho, escopo expandido sem aprovação, regra de negócio reinterpretada sem voltar à SPEC.

## 7. Skill associada

[`../skills/teczi-code-execution.md`](../skills/teczi-code-execution.md)

## 8. Operação manual (Stage 0)

1. Nikola lê SPEC + PLAN aprovados.
2. Nikola implementa por bloco/TASK conforme classificação.
3. Linus revisa intrabloco (code review leve, antes do QA formal).
4. Kevin revisa intrabloco se `sec` marcado.
5. Nikola roda build/checks locais (lint, typecheck, testes).
6. Founder valida o bloco → próximo bloco ou QA.

## 9. Anti-padrões

- Decidir arquitetura no meio do CODE (volta para ARCH).
- Reinterpretar regra de negócio sem voltar à SPEC.
- Bypass de check intrabloco — Linus sempre, Kevin se `sec`.
- Commit em main (proibição absoluta workspace).

## 10. Referências

- SCOPE-FINAL §6.1
- Skill: [`../skills/teczi-code-execution.md`](../skills/teczi-code-execution.md)
- Próxima fase: [`07-QA.md`](07-QA.md)

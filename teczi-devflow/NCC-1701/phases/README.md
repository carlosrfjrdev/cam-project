# Fases — NCC-1701

> Índice navegável das 9 fases numeradas do framework.
> Estados não numerados em [`../states/`](../states/).
> Governanças transversais em [`../governance/`](../governance/).

## Como usar este índice

Cada fase tem um arquivo dedicado com estrutura padrão (10 seções: Propósito, Quando rodar, Entradas, Saídas, Personas, Gate de saída, Skill associada, Operação manual Stage 0, Anti-padrões, Referências).

## Catálogo

| # | Fase | Lead | Skill associada | Saída principal |
|---|---|---|---|---|
| 1 | [PDOC](01-PDOC.md) | Leo/Denis | [`teczi-project-creation`](../skills/teczi-project-creation.md) | Estrutura de projeto, contexto inicial |
| 2 | [DISC](02-DISC.md) | Marty | [`teczi-project-discovery`](../skills/teczi-project-discovery.md) | SCOPE + DVP inicial (se novo produto) |
| 3 | [ARCH](03-ARCH.md) | Oscar | [`teczi-architecture-decision`](../skills/teczi-architecture-decision.md) | DAS, ADRs, INFRA-ARCH |
| 4 | [SPEC](04-SPEC.md) | Albert | [`teczi-demand-specification`](../skills/teczi-demand-specification.md) | SPEC da demanda + classificação P/M/G |
| 5 | [PLAN](05-PLAN.md) | Nico | [`teczi-code-planning`](../skills/teczi-code-planning.md) | PLAN proporcional + TASKs se G |
| 6 | [CODE](06-CODE.md) | Nikola | [`teczi-code-execution`](../skills/teczi-code-execution.md) | Código, commits, checks intrabloco |
| 7 | [QA](07-QA.md) | Linus (+ Kevin) | [`teczi-quality-assurance`](../skills/teczi-quality-assurance.md) | QA-CR + QA-Func + QA-SEC proporcional |
| 8 | [DEPLOY](08-DEPLOY.md) | Steve+Tom, Vint executor | [`teczi-deploy`](../skills/teczi-deploy.md) | Release, tag, CHANGE, smoke |
| 9 | [SDOC](09-SDOC.md) | Denis/Howard | [`teczi-software-documentation`](../skills/teczi-software-documentation.md) | Doc as-is, DRIFT-REPORT (sob solicitação) |

## Proporcionalidade

A matriz P/M/G por fase está em [`../process.md`](../process.md) §5.

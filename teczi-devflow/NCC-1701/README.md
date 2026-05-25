# Teczi DevFlow NCC-1701

> **Framework interno de operação founder-only — Teczilabs**
> **Status:** Draft (em validação operacional dogfood-first)
> **Estágio do SSoT:** **Stage 0** — Markdown versionado + decisões explícitas do Founder (sem Codex/CLI/MCP automatizados ainda)
> **Codinome:** NCC-1701 (sucessor conceitual do NX-50A)
> **Fonte canônica de decisões:** `projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md`
> **Especificação desta materialização:** `projects/devflow/SPEC-V6.0-NCC-1701.md`

---

## Visão de 30 segundos

O **NCC-1701** é o framework interno da Teczilabs para que **um único Founder** opere todo o ciclo de produção de software — da ideia ao deploy — com:

- **9 fases numeradas** (PDOC → SDOC),
- **2 estados não numerados** (BUG, OPS),
- **2 governanças transversais** (SEC-GOV por gatilho, CHANGE dentro de DEPLOY),
- **Founder-only nos gates**,
- **P/M/G** como classificação simples de tamanho operacional,
- **Estado real vence** intenção (codex > project quando há drift),
- **Proof Pack proporcional** (P opcional · M recomendado · G/release/incidente/arch obrigatório).

Tudo opera hoje em **Markdown versionado**. Codex, CLI, MCP e Skills são potencializadores futuros — não dependências da v6.0.

---

## Leitura principal

→ **[`process.md`](process.md)** — processo consolidado de ponta a ponta.

---

## Tabela rápida de fases

| # | Fase | Lead | Objetivo (1 linha) |
|---|---|---|---|
| 1 | PDOC | Leo/Denis | Registrar projeto, organizar estrutura e contexto inicial |
| 2 | DISC | Marty | Delimitar oportunidade, escopo, In/Out/Later |
| 3 | ARCH | Oscar | Definir arquitetura, impactos e ADRs quando necessário |
| 4 | SPEC | Albert | Especificar demanda, regras, P/M/G, segurança |
| 5 | PLAN | Nico | Planejar execução proporcional |
| 6 | CODE | Nikola | Implementar bloco/demanda dentro do escopo aprovado |
| 7 | QA | Linus | Validar qualidade funcional, regressão e segurança proporcional |
| 8 | DEPLOY | Steve+Tom, Vint executor | Release, versionamento, CHANGE, deploy e smoke |
| 9 | SDOC | Denis/Howard | Atualizar documentação de software quando acionada |

Estados: **BUG** (fast-track · Bill) · **OPS** (estado contínuo · Vint).
Governanças: **SEC-GOV** (por gatilho · Kevin) · **CHANGE** (em DEPLOY · Tom).

---

## Navegação

| Pasta | Conteúdo |
|---|---|
| [`phases/`](phases/) | Detalhamento de cada uma das 9 fases |
| [`states/`](states/) | Estados não numerados (BUG, OPS) |
| [`governance/`](governance/) | Governanças transversais (SEC-GOV, CHANGE) |
| [`skills/`](skills/) | Drafts conceituais de skills (não executáveis ainda) |
| [`templates/`](templates/) | Templates de artefatos (SCOPE, DVP, DAS, SPEC, PLAN, BUG, OPS-EVENT, …) |

---

## Relação com NX-50A

O NX-50A continua válido. Não há linha de corte automática.

- O NCC-1701 e o NX-50A coexistem.
- O Founder informa explicitamente quando uma demanda usa cada um.
- Se houver conflito operacional, o Founder decide caso a caso.

(Decisão herdada: SCOPE-FINAL §17 · Q21 Founder)

---

## Proibições absolutas herdadas

- ❌ Inferir estimativas em horas/dias/semanas em qualquer artefato — Founder explicitamente proíbe.
- ❌ Auto-approval em qualquer gate — tudo é Founder-only nesta versão.
- ❌ Modificadores de risco no P/M/G — Q8 Founder considera overengineering.
- ❌ DRIFT automático — Q12 Founder: apenas por solicitação.
- ❌ SDOC em toda demanda — Q11 Founder: apenas em release final elegível ou solicitação explícita.
- ❌ Commit em `main`; commit de secrets; rebase/amend/force push (regras universais Teczilabs).

---

## Referências canônicas

| Documento | Função |
|---|---|
| [SCOPE-FINAL-V6.0-NCC-1701.md](../../projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md) | Fonte primária de decisões |
| [QUESTOES-SCOPE-PROPOSTO-V6.0-NCC-1701.md](../../projects/devflow/QUESTOES-SCOPE-PROPOSTO-V6.0-NCC-1701.md) | 22 respostas do Founder |
| [SPEC-V6.0-NCC-1701.md](../../projects/devflow/SPEC-V6.0-NCC-1701.md) | Especificação desta materialização |
| [CLAUDE-PARECER-01.md](../../projects/devflow/CLAUDE-PARECER-01.md) | Parecer externo 1 |
| [GPT-PARECER-01.md](../../projects/devflow/GPT-PARECER-01.MD) | Parecer externo 2 |
| [NX-50A/](../NX-50A/) | Versão anterior coexistente |

---

> *Espaço, a fronteira final. Estas são as viagens da nave estelar Enterprise.*
>
> *Space, the final frontier. These are the voyages of the starship Enterprise.*

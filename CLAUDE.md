# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Idioma de resposta padrão neste projeto:** **português**. Carlos opera em PT-BR.

---

## O que este repositório é

**CaM — Cockpit de gestão de ativos.** Plataforma de software para gestão, análise e
operação de ativos. **Virada estratégica (2026-06-03):** o projeto deixou de ser o
cockpit *pessoal e não-comercial* de um único trader e passou a ser um **produto** —
solução de software para terceiros operarem (codinome de produto futuro: **TCaM — Teczi
Cockpit Assets Manager**; o nome "CaM" e as pastas `cam-cockpit` permanecem até o
Founder pedir o rebrand de UI). Histórico do projeto pessoal preservado na branch
`the_old_cam`.

**Fase atual:** **Fase 0 — Construção da estrutura do produto.** Reaproveita o que já
foi construído (features, MT5 bridge, Inspetor, Quant Lab, backtest, etc.) e organiza
sob o novo paradigma de produto.

> ⚠️ **A Constituição foi DESCOMISSIONADA (2026-06-03).** O documento
> `CONSTITUICAO.md` era a disciplina **pessoal de trader** do Carlos (preservação de
> capital, limites de contrato, kill switch obrigatório, DARF bloqueante, "IA não opera").
> Como o Carlos não opera mais — vira fornecedor de solução —, essas regras morreram
> como **lei do projeto**. Ver `project/tcam/CONSTITUTION-DECOMMISSION.md`.
>
> **NÃO** aplique mais nenhuma "trava constitucional", hierarquia soberana, "Art. Xº",
> nem o princípio "preserve mais capital" como regra vinculante. O documento, se ainda
> existir, está **arquivado** e é apenas memória histórica.
>
> **O que sobrevive (como engenharia, não como lei):** o **Risk Engine** (`_shared/risk`)
> permanece no código — passa a ser **feature de produto** ("Assets RiskManager"),
> configurável pelo usuário, não um dogma moral. O isolamento research↔live
> (import-linter) fica como boa prática de arquitetura. O **DevFlow NCC-1701** e as
> personas continuam — são processo de **engenharia de software**, nunca foram a
> Constituição do trader.

---

## Estrutura do repositório

```
CaM-project/
├── CLAUDE.md                   ← Este arquivo (contexto para Claude Code)
├── README.md                   ← README institucional do CaM
├── project/tcam/               ← Virada estratégica → produto (PIVOT, DECOMMISSION, MAP)
│   (CONSTITUICAO.md descomissionada — arquivada, sem força de lei)
│
├── apps/                       ← APLICATIVOS do cockpit (estado real — código)
│   └── README.md
│
├── project/                    ← ARTEFATOS DevFlow por demanda (intenção viva — SCOPE, SPEC, PLAN, ADRs, ...)
│   └── README.md
│
├── archive/                    ← Memória física (.txt originais da Constituição)
│   └── README.md
│
├── teczi-devflow/              ← Framework de processo embarcado — Teczi DevFlow NCC-1701 (v6.0)
│   ├── NCC-1701/               ← Versão ativa: 9 fases / 2 estados / 2 governanças
│   │   ├── process.md          ← Leitura obrigatória antes de qualquer demanda
│   │   ├── phases/             ← 01-PDOC → 09-SDOC
│   │   ├── states/             ← BUG, OPS
│   │   ├── governance/         ← SEC-GOV, CHANGE
│   │   ├── templates/          ← SCOPE, DVP, DAS, ADR, INFRA-ARCH, SPEC, PLAN, BUG, OPS-EVENT, CHANGE-RECORD, DRIFT-REPORT, PROOF-PACK
│   │   └── skills/             ← Drafts conceituais (referência canônica das skills operacionais)
│   ├── personas/               ← Apenas INDEX.md → aponta para /personas (ADR-001 repo-wide)
│   └── CLAUDE.md               ← Notas escopadas ao subdiretório
│
├── personas/                   ← CAST CaM-only em 5 times (ADR-001 — fora do teczi-devflow, Art. 8º)
│   ├── carlos.md               ← Founder (soberano, cross-time)
│   ├── 1-lideranca-estrategia/ ← leo, marty, albert, nico, peter, voltaire, sun
│   ├── 2-tecnologia/           ← oscar, nikola, tom, vint, ada, grace, alan, steve
│   ├── 3-governanca-seguranca-qa/ ← kevin, linus, bill, denis, howard
│   ├── 4-experiencia-cockpit/  ← don, andy
│   ├── 5-financeiro-mercado-ativos/ ← mammon, ray, jim, wyck, nassim, barsi, luca, daniel, fred
│   ├── _archive/               ← florence (aposentada) + catálogos legados
│   └── README.md               ← Mapa dos 5 times (fonte autoritativa)
│
└── .claude/                    ← Configuração Claude Code
    ├── agents/                 ← 31 agents (24 ativos + 7 financeiros novos; florence removida)
    ├── skills/                 ← teczi-* (compartilháveis) + cam-* (CaM-only) + strategy-session
    ├── settings.json           ← bypassPermissions ON (cuidado equivalente)
    └── settings.local.json
```

### Separação `/apps` × `/project` (NCC-1701 §9.3)

| Pasta | Significado | Quando consultar |
|---|---|---|
| [`/apps`](./apps/) | **Estado real** — código construído | "O que de fato existe e roda" |
| [`/project`](./project/) | **Intenção viva** — SCOPE, SPEC, PLAN, ADRs, PROOF-PACKs | "O que está sendo decidido e construído" |

Quando ambos divergirem: **estado real vence intenção** (NCC-1701 §2, regra 7). DRIFT só é analisado por solicitação explícita do Founder (Q12).

### 📄 Política de documentação (diretriz do Founder — 2026-05-30)

**`.md` de documentação NÃO ficam dentro de `/apps`.** A codebase (`/apps`) só
contém os `.md` **obrigatórios**: `README.md` (qualquer nível) e arquivos de
instrução de agente (`CLAUDE.md`, `AGENTS.md`). **Toda outra documentação**
(runbooks, tech-debt, ledgers, TODOs operacionais, notas) vive em **`/project`**:

| Tipo de doc | Local |
|---|---|
| Runbooks | `project/runbooks/` |
| Tech-debt / feature-flags / TODO operacional | `project/cam-cockpit/` |
| SCOPE / SPEC / PLAN / ADR / QA / PROOF-PACK | `project/cam-cockpit/{scopes,specs,plans,adrs,qa}/` |

> Ao criar documentação, **nunca** a coloque em `/apps`. Se precisar referenciá-la
> do código, use um link relativo para `/project`. README de feature pode resumir
> e apontar para o doc em `/project`.

---

## Framework de produção — Teczi DevFlow NCC-1701

Toda construção segue o framework embarcado em `teczi-devflow/NCC-1701/`. Leia [`teczi-devflow/NCC-1701/process.md`](./teczi-devflow/NCC-1701/process.md) antes de qualquer demanda real.

**Modelo:**

```
9 fases: PDOC → DISC → ARCH → SPEC → PLAN ⇄ (loop) → CODE → QA → DEPLOY → SDOC
2 estados: BUG (fast-track) · OPS (contínuo)
2 governanças: SEC-GOV (gatilho) · CHANGE (em DEPLOY)
```

**Princípios obrigatórios:**

- **Founder-only nos gates** — Carlos aprova cada transição
- **Proporcionalidade P/M/G** apenas (Pequena / Média / Grande)
- **Stage 0 SSoT** — Markdown versionado + decisões explícitas do Founder
- **Estado real vence intenção** em drift
- **Proof Pack proporcional** — P opcional · M recomendado · G/release/incidente/arch obrigatório
- **Reuso antes de criação** — procurar decisão/artefato/padrão existente
- **SDOC sob demanda** — apenas em release final elegível ou solicitação explícita

**Proibições absolutas** (válidas globalmente neste repositório):

| Proibição | Origem |
|---|---|
| ❌ Estimar em horas/dias/semanas | NCC-1701 §1 + Q8 Founder |
| ❌ Auto-approval em qualquer gate | NCC-1701 §7 |
| ❌ Modificadores de risco/segurança/arquitetura/release no P/M/G | Q8 Founder (considera overengineering) |
| ❌ DRIFT automático | Q12 Founder |
| ❌ SDOC em toda demanda | Q11 Founder |
| ❌ Commit em `main` | Regra universal |
| ❌ Commit de secrets | Regra universal |
| ❌ Rebase / amend / force push | Regra universal |
| ❌ Tag de ciclo (INDEV/BETA) em comunicação externa | Q16 Founder |

---

## Skills operacionais — `.claude/skills/`

13 skills disponíveis via `Skill` tool. Acionar **sempre** a skill correspondente ao começar trabalho em uma fase/estado/governança.

### Skills DevFlow NCC-1701 (11)

| Skill | Fase/Estado/Gov | Lead |
|---|---|---|
| `teczi-project-creation` | PDOC | Leo + Denis |
| `teczi-project-discovery` | DISC | Marty |
| `teczi-architecture-decision` | ARCH | Oscar (+Vint INFRA-ARCH, +Kevin threat model) |
| `teczi-demand-specification` | SPEC | Albert (+Kevin sec/qa-sec) |
| `teczi-code-planning` | PLAN | Nico (loop ilimitado com Albert sobre P/M/G) |
| `teczi-code-execution` | CODE | Nikola (+Linus intrabloco, +Kevin se sec) |
| `teczi-quality-assurance` | QA | Linus (+Kevin em QA-SEC) |
| `teczi-deploy` | DEPLOY | Steve + Tom (Vint executor) |
| `teczi-software-documentation` | SDOC | Denis (+Howard em DRIFT, sob solicitação) |
| `teczi-bug-fix` | Estado BUG | Bill |
| `teczi-security-governance` | Governança SEC-GOV | Kevin |

### Skills institucionais (2)

| Skill | Quando acionar |
|---|---|
| `strategy-session` | Power Strategy Session — estratégia institucional ampla (Sun, Grace, Voltaire, Mammon, +Kevin se sensível) |
| `teczi-discovery-software` | Arqueologia técnica / discovery de sistema não documentado (Howard) |

Padrão Claude Code disponíveis: `superpowers:*`, `frontend-design`, `verify`, `run`, `code-review`, `security-review`, etc.

---

## Personas (`.claude/agents/`)

**14 personas ativas no fluxo base NCC-1701** — invocáveis via `Agent` tool:

| Persona | Papel | Cor |
|---|---|---|
| `leo` | **Orquestrador-chefe** — ponto único de entrada | Deep Orange |
| `marty` | DISC — discovery, In/Out/Later | Deep Indigo |
| `albert` | SPEC — requisitos, P/M/G | Amber |
| `oscar` | ARCH — DAS, ADRs | Blue |
| `nico` | PLAN — proporcional, letscode | Purple |
| `nikola` | CODE — implementação | Green |
| `linus` | QA — QA-CR + QA-Func + QA-SEC | Teal |
| `bill` | Estado BUG — fast-track | Red |
| `steve` | DEPLOY co-lead — narrativa de release | Pink |
| `tom` | DEPLOY co-lead — versionamento, CHANGE-RECORD | Slate |
| `vint` | DEPLOY executor + OPS + INFRA-ARCH | Slate |
| `kevin` | SEC-GOV transversal | Forest Green |
| `denis` | PDOC co-lead + SDOC lead | Lime |
| `howard` | SDOC DRIFT (sob solicitação) | Sandy Brown |

**Cast estendido + mundo financeiro (Time 5)** — chamado por Leo quando necessário:
`sun`, `voltaire`, `grace`, `alan`, `andy`, `ada`, `peter`, `fred`, `don` +
**Time 5 financeiro:** `mammon` (ofensivo, read-only Art. 35º), `ray` (macro), `jim` (quant/edge), `wyck` (fluxo), `nassim` (risco de ruína), `barsi` (Carteira Hard/dividendos), `luca` (fiscal/ledger), `daniel` (RCA do operador).

> `florence` **aposentada** (D4) — ver `personas/_archive/`. Cast organizado em **5 times** (ADR-001): mapa completo em [`personas/README.md`](./personas/README.md).

**Padrão de invocação:** delegue para `leo` quando a demanda for ampla ou ambígua; para `{persona}` específica quando o lead da fase/estado/governança for óbvio. Leo NUNCA simula outra persona — sempre invoca via `Agent` tool e consolida o resultado identificando a fonte.

---

## Stack vigente no CaM

**Documento canônico:** [`project/STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md)

A stack do CaM **revoga** os Combos A/B/C do catálogo Teczilabs (Java/Spring, Firebase, Next.js, MongoDB). Esses combos foram inferidos para produtos comerciais e **não se aplicam** a este projeto.

**Resumo da stack oficial:**

```text
SO: Windows 11        →  FIRME (Wine/Linux falhou). Único SO, dev + produção.
Broker: EM AVALIAÇÃO  →  MetaTrader 5 em teste (MQL5 EAs + bridge ZeroMQ 127.0.0.1)
                          / Profit em STANDBY (NTSL + CSV/ProfitDLL). Decide após 1º teste.
Python 3.12 + FastAPI →  Cockpit local: Risk Engine, Ledger, Journal, IA, integração
React 19 + Vite + MUI →  Frontend SPA local (sem Next.js)
PostgreSQL 16 + TimescaleDB → Banco transacional + tick/candle storage (desde Fase 0)
DuckDB                →  Motor analítico auxiliar (research em CSV/Parquet)
Telegram Bot          →  Canal externo de alerta
Ollama local + Anthropic → IA auditora/analista (papel definido por produto, não por lei)
```

**SO produção E desenvolvimento:** **Windows 11** (firme, 2026-05-30 — Wine/Linux
falhou). **Broker em avaliação:** **MT5 em teste** agora; **Profit em STANDBY**
(não descartado) — a escolha fecha **após o 1º teste do MT5**. Tudo em **soft-stage**
(pré-v1): docs e ADRs **moldáveis, não-HARD**.

> ⚙️ **Continuar a partir de um `git clone` no Windows:** siga o runbook
> [`project/tcam/runbooks/RUNBOOK-WINDOWS.md`](./project/tcam/runbooks/RUNBOOK-WINDOWS.md)
> (setup, MT5 + EAs, bridge ZeroMQ, guardrails DEMO-only). O `cam-cockpit`
> (backend/frontend/banco) é multiplataforma; só a camada de broker é Windows.
> EAs MT5 em `apps/cam-cockpit/mql5/` (`cam_bridge.mq5`, `cam_risk_mirror.mq5`);
> artefatos Profit em `apps/cam-cockpit/ntsl/` (standby).

Convenção de pastas: aplicativos em `/apps/cam-*` (monorepo `apps/cam-cockpit/{backend,frontend,mql5,ntsl}`). Detalhes, faseamento, riscos: ver [`STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md).

> ⚠️ **Notas (soft-stage):** SO Windows é firme; **broker em aberto** (MT5 teste /
> Profit standby — nada descartado). ADR-001/008 → **Under-evaluation**, ADR-009 →
> **Active** (recalibradas 2026-05-30). Estado real (`/apps`) vence intenção (NCC-1701 §2 regra 7).

---

## Segurança (SEC-GOV) no produto

Os **9 gatilhos canônicos do NCC-1701** para SEC-GOV (Kevin) continuam válidos como
boa engenharia. Os antigos gatilhos *constitucionais* (Risk Engine como autoridade,
kill switch obrigatório, journal/DARF, "autoridade da IA" Arts. 34–36) **deixaram de
ser lei**. Eles podem reaparecer como **requisitos de produto** quando fizer sentido
comercial — ex.: segurança de dados de cliente, isolamento multi-tenant, segregação
research↔live — mas como decisão de engenharia/produto, não como dogma.

> Vender ferramenta para terceiros operarem abre exposição **legal/regulatória** nova
> (responsabilidade, CVM, termos de uso). Isso é tratado na camada de produto (Fase 2),
> ver `project/tcam/PIVOT-TCaM-STRATEGY.md` — não é uma trava de código agora.

---

## Git posture

Este diretório raiz **não é** repositório git no momento (sessão verificada em 2026-05-24). O subdiretório `teczi-devflow/` tem seu próprio repositório (`github.com/Teczilabs/teczi-devflow`, branch `dev`).

Quando o cockpit CaM começar a materializar código em `/apps/{codinome}/`, cada app pode ter seu próprio repositório (modelo `project` vs `codex`: `/project` = intenção viva sob este repo; `/apps/{codinome}` = estado real, repo próprio).

**Lembre:** commit em `main`, secrets em commit e rebase/amend/force push são proibições absolutas, válidas em qualquer repositório do CaM.

---

## Settings note

`.claude/settings.json` define `defaultMode: bypassPermissions` e `skipDangerousModePermissionPrompt: true`. Ferramentas rodam sem prompt — exercer o mesmo cuidado que você teria sob permissões normais, especialmente para ações destrutivas ou em estado compartilhado.

---

## Checklist de orientação (para qualquer Claude novo entrando aqui)

0. **Abra [`project/ORIENTACAO.md`](./project/ORIENTACAO.md)** — mapa de navegação único do repo (onde mora o quê + estado vivo/stub/morto de cada feature). É o ponto de partida para se localizar.
1. Leia esta seção "O que este repositório é" — entenda a **virada para produto** e que a **Constituição está descomissionada** (sem força de lei).
2. Leia [`project/tcam/`](./project/tcam/) — a estratégia da virada (PIVOT, DECOMMISSION, MAP de módulos).
3. Leia [`teczi-devflow/NCC-1701/process.md`](./teczi-devflow/NCC-1701/process.md) — o processo de engenharia (continua válido).
4. Para qualquer demanda: acione a skill da fase correspondente via `Skill` tool.
5. Responda em português.
6. Quando em dúvida: **invoque Leo** para orquestrar. Não há mais "preserve mais capital" como regra — o objetivo agora é **construir o produto**.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Idioma de resposta padrão neste projeto:** **português**. Carlos opera em PT-BR.

---

## O que este repositório é

**CaM — The Carlos Alternative Money.** Cockpit pessoal, local, não comercial de Carlos Rodrigues Ferreira Junior para operação disciplinada de mercado, preservação de capital e construção patrimonial via Harvest Rule. Projeto **separado e independente** da Teczilabs (sem perímetro de capital, infraestrutura ou receita compartilhada — Art. 8º).

**Fase atual:** **Fase 0 — Construção** (`CONSTITUICAO.md` Anexo II). Sem trade real, sem paper trading. Construção do cockpit: backend, frontend, Risk Engine, journal, backtest engine, integrações.

Não há comandos de build/lint/test ainda — esta seção será adicionada quando o primeiro app for criado em `/apps`.

---

## Hierarquia constitucional — LEIA antes de qualquer ação

```
Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual
```

A [`CONSTITUICAO.md`](./CONSTITUICAO.md) é **soberana** (Art. 43º). Toda recomendação, código, decisão ou orquestração que você produzir tem que sobreviver a essa hierarquia.

**Artigos não-negociáveis:**

| Artigo | O que vincula |
|---|---|
| **Art. 11º** | Limite absoluto: **2 contratos WIN / 2 contratos WDO**. Intocável |
| **Art. 15º** | Risk Engine bloqueia? CaM não opera. Sem exceções |
| **Art. 18º** | Kill switch obrigatório, acionável sem justificar oportunidade perdida |
| **Art. 19º** | Posição aberta sem cobertura sistêmica é risco inaceitável |
| **Art. 25º** | UIs operacionais exibem resultado **LÍQUIDO de imposto provisionado**, nunca bruto |
| **Art. 26º** | DARF atrasada bloqueia novas operações |
| **Art. 31º** | Operação sem registro no journal é falha operacional |
| **Art. 35º** | IA NÃO PODE: enviar ordem, desabilitar/parametrizar Risk Engine, justificar exceção constitucional |
| **Art. 36º** | A hierarquia acima — inviolável |
| **Art. 6º** | Em conflito entre regras, prevalece a que **preserva mais capital** |

Quando estiver em dúvida sobre o que recomendar/codar: aplique o Art. 6º.

---

## Estrutura do repositório

```
CaM-project/
├── CONSTITUICAO.md             ← Lei suprema (v1.0 consolidada — substitui os .txt antigos)
├── CLAUDE.md                   ← Este arquivo (contexto para Claude Code)
├── README.md                   ← README institucional do CaM
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
MetaTrader 5 (MQL5 EAs) →  Plataforma de execução — Windows NATIVO (sem Wine)
Bridge ZeroMQ           →  Python ↔ MT5 em 127.0.0.1 (PUB 5556 / REQ 5557)
Python 3.12 + FastAPI   →  Cockpit local: Risk Engine, Ledger, Journal, IA, integração
React 19 + Vite + MUI   →  Frontend SPA local (sem Next.js)
PostgreSQL 16 + TimescaleDB → Banco transacional + tick/candle storage (desde Fase 0)
DuckDB                  →  Motor analítico auxiliar (research em CSV/Parquet)
Telegram Bot            →  Canal externo de alerta
Ollama local + Anthropic → IA auditora/analista, NUNCA executora (Arts. 34–36)
```

**SO produção E desenvolvimento:** **Windows 11** (decisão 2026-05-30). O MT5 sob
Wine no Linux **falhou** → execução em Windows nativo, single-SO. Estamos em
**soft-stage de concepção** (pré-v1): docs e ADRs são **moldáveis, não-HARD**.

> ⚙️ **Continuar a partir de um `git clone` no Windows:** siga o runbook
> [`project/runbooks/RUNBOOK-WINDOWS.md`](./project/runbooks/RUNBOOK-WINDOWS.md)
> (setup, MT5 + EAs, bridge ZeroMQ, guardrails DEMO-only). O `cam-cockpit`
> (backend/frontend/banco) é multiplataforma; só a camada MT5 é Windows.
> EAs em `apps/cam-cockpit/mql5/` (`cam_bridge.mq5`, `cam_risk_mirror.mq5`).

Convenção de pastas: aplicativos em `/apps/cam-*` (monorepo `apps/cam-cockpit/{backend,frontend,mql5}`). Detalhes, faseamento de integração, riscos: ver [`STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md).

> ⚠️ **Notas de drift (soft-stage):** o `ntsl/` foi DESATIVADO (broker é MT5, não
> Profit). ADR-001 (Superseded), ADR-008/009 (Superseded-in-part) **já alinhadas a
> MT5/MQL5** em 2026-05-30. Estado real (`/apps`) vence intenção (NCC-1701 §2 regra 7).

---

## Gatilhos automáticos para SEC-GOV no CaM

Além dos 9 gatilhos canônicos do NCC-1701, no CaM **sempre** acionar SEC-GOV (Kevin) quando a demanda tocar:

- **Risk Engine** (Art. 15º)
- **Kill switch** (Art. 18º)
- **Journal**, ledger fiscal ou provisão (Arts. 25º, 26º, 31º)
- **Autoridade da IA** (Arts. 34º–36º)

Esses são **bugs/mudanças constitucionais** — não tratá-los como "comuns".

---

## Git posture

Este diretório raiz **não é** repositório git no momento (sessão verificada em 2026-05-24). O subdiretório `teczi-devflow/` tem seu próprio repositório (`github.com/Teczilabs/teczi-devflow`, branch `dev`).

Quando o cockpit CaM começar a materializar código em `/apps/{codinome}/`, cada app pode ter seu próprio repositório (modelo `project` vs `codex`: `/project` = intenção viva sob este repo; `/apps/{codinome}` = estado real, repo próprio).

**Lembre:** commit em `main`, secrets em commit e rebase/amend/force push são proibições absolutas, válidas em qualquer repositório do CaM.

---

## Settings note

`.claude/settings.json` define `defaultMode: bypassPermissions` e `skipDangerousModePermissionPrompt: true`. Ferramentas rodam sem prompt — exercer o mesmo cuidado que você teria sob permissões normais, especialmente para ações destrutivas, em estado compartilhado ou que violem a Constituição.

---

## Checklist de orientação (para qualquer Claude novo entrando aqui)

1. Leia [`CONSTITUICAO.md`](./CONSTITUICAO.md) — pelo menos Parte I, IV, IX, X
2. Leia [`teczi-devflow/NCC-1701/process.md`](./teczi-devflow/NCC-1701/process.md)
3. Confira a fase atual do CaM (Fase 0 — Construção) no Anexo II da Constituição
4. Para qualquer demanda: acione a skill da fase correspondente via `Skill` tool
5. Responda em português
6. Quando em dúvida: **preserve mais capital** (Art. 6º) e **invoque Leo** para orquestrar

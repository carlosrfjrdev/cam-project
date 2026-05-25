# Teczi DevFlow v4.0

> **Framework de Produção de Software com IA Agêntica** — Da ideia ao deploy em produção.

---

## O que é

O **Teczi DevFlow** é o framework de produção de software da **Teczilabs**, desenhado para uma operação **one-person unicorn** onde um único Engenheiro de Software (Founder) conduz todo o ciclo de vida do produto, apoiado por **LLMs e IAs Agênticas** em todas as fases.

O framework é **context-driven** — cada fase gera artefatos consumíveis por LLM que alimentam a fase seguinte, criando uma **cadeia de produção automatizada e rastreável**.

O produto que operacionaliza o Teczi DevFlow é o **Teczi Factory App** — AI SDLC Orchestrator.

---

## Princípios

| Princípio | Descrição |
|---|---|
| **Context-First** | Todo artefato é contexto consumível por LLM |
| **I/O Explícito** | Cada fase tem entrada, processamento e saída claros |
| **Rastreabilidade** | Toda decisão e construção é documentada |
| **Automação Máxima** | Humano decide, IA operacionaliza |
| **QA Documental** | Artefatos passam por Draft → QA → Final antes de avançar |
| **Incrementalidade** | Entregas pequenas, validáveis e iteráveis |

---

## Fases e Personas

O DevFlow opera em **6 fases sequenciais**, cada uma com um **agente dedicado** (persona) e templates próprios.

```
 IDEIA (Founder)
    │
    ▼
┌─ FASE 1 — DESCOBERTA ─── 🔬 Albert (Curious) ──────┐
│  Ideia bruta → DVP / DEV                              │
└───────────────────┬───────────────────────────────────┘
                    ▼
┌─ FASE 2 — ARQUITETURA ── 🏛️ Oscar (Precise) ────────┐
│  DVP → DAS + ADRs                                     │
└───────────────────┬───────────────────────────────────┘
                    ▼
┌─ FASE 3 — PLANEJAMENTO ─ 📋 Nico (Strategic) ────────┐
│  DVP + DAS → Épicos, FGs, Stories, Tasks               │
└───────────────────┬───────────────────────────────────┘
                    ▼
┌─ FASE 4 — DEVELOPER ──── ⚡ Nikola (Focused) ─────────┐
│  Stories → Código implementado                          │
└───────────────────┬───────────────────────────────────┘
                    ▼
┌─ FASE 5 — QA ─────────── 🛡️ Linus (Rigorous) ────────┐
│  Código → Testes, Bugs, Homologação                     │
└───────────────────┬───────────────────────────────────┘
                    ▼
┌─ FASE 6 — RELEASE ────── 🚀 Steve (Visionary) ────────┐
│  Software validado → Deploy + Release Notes             │
└────────────────────────────────────────────────────────┘
```

### Tabela de Papéis

| Fase | Persona | Cor | Role | Agent |
|---|---|---|---|---|
| F1 — Descoberta | 🔬 Albert | `#F59E0B` | Refinador de Ideias | `agents/discovery.md` |
| F2 — Arquitetura | 🏛️ Oscar | `#0EA5E9` | Arquiteto de Soluções | `agents/architecture.md` |
| F3 — Planejamento | 📋 Nico | `#8B5CF6` | Planejador de Projeto | `agents/planning.md` |
| F4 — Developer | ⚡ Nikola | `#10B981` | Developer | `agents/developer.md` |
| F5 — QA | 🛡️ Linus | `#0D9488` | QA Analyst | `agents/qa.md` |
| F6 — Release | 🚀 Steve | `#EC4899` | Release Manager | `agents/release.md` |

> Persona adicional: 🪲 **Bill** (`#EF4444`) — Bug Analysis & Fix (jornada de correção).
> Cast completo: `teczilabs/personas/personas-devflow.md`.

---

## Jornadas

O DevFlow opera em 3 jornadas que combinam subconjuntos de fases:

| Jornada | Cenário | Fases | Discovery |
|---|---|---|---|
| **Construção** | Software do zero | F1 → F2 → F3 → F4 → F5 → F6 | DVP |
| **Evolução** | Nova capacidade em software existente | F1 → F2? → F3 → F4 → F5 → F6 | DEV |
| **Melhoria Contínua** | Refatoração, ajuste, otimização | F1 → F3 → F4 → F5 → F6 | DEV |

---

## Artefatos por Fase

| Fase | Artefato | Template |
|---|---|---|
| F1 | DVP / DEV / Refinamento | `templates/dvp.md`, `templates/dev.md`, `templates/refinement.md` |
| F2 | DAS + ADRs | `templates/das.md`, `templates/adr.md` |
| F3 | Épicos, FGs, Stories, Tasks | `templates/epic.md`, `templates/feature-group.md`, `templates/story.md`, `templates/task.md` |
| F4 | Código + Prompts de Construção + Resumos | `templates/construction-prompt.md`, `templates/story-implementation.md`, `templates/feature-implementation.md` |
| F5 | Bugs, Correções, Homologação | `templates/bug.md`, `templates/fix-prompt.md`, `templates/homologation-checklist.md` |
| F6 | Release Notes, Deploy Checklist | `templates/release-notes.md`, `templates/deploy-checklist.md` |

---

## Estrutura do Repositório

```
teczi-devflow/
├── README.md                          # Este arquivo
├── CLAUDE.md                          # Contexto para Claude Code
│
├── devflow/                           # Framework v4.0
│   ├── PROCESS.md                     # Processo completo (6 fases, 3 jornadas)
│   ├── agents/                        # System prompts por fase (com personas)
│   │   ├── discovery.md               # 🔬 Albert — Fase 1
│   │   ├── architecture.md            # 🏛️ Oscar — Fase 2
│   │   ├── planning.md                # 📋 Nico — Fase 3
│   │   ├── developer.md               # ⚡ Nikola — Fase 4
│   │   ├── qa.md                      # 🛡️ Linus — Fase 5
│   │   └── release.md                 # 🚀 Steve — Fase 6
│   ├── templates/                     # Templates de artefatos (kebab-case)
│   │   ├── dvp.md, dev.md, refinement.md
│   │   ├── das.md, adr.md
│   │   ├── epic.md, feature-group.md, story.md, task.md
│   │   ├── construction-prompt.md, story-implementation.md, feature-implementation.md
│   │   ├── bug.md, fix-prompt.md, homologation-checklist.md, tech-debt.md
│   │   ├── release-notes.md, deploy-checklist.md
│   │   └── stack-catalog.md
│   └── config/                        # Integração com ferramentas
│       ├── claude-code.md             # Instruções para Claude Code
│       └── copilot.md                 # Instruções para GitHub Copilot
│
├── archive/                           # Versões anteriores
│   ├── v3.1-claude/                   # DevFlow v3.1 — contexto Claude
│   ├── v3.1-copilot/                  # DevFlow v3.1 — contexto Copilot
│   └── studies/                       # Estudos e refinamentos
│
└── projects/                          # Artefatos de projetos (por produto)
    ├── factory/                       # Projetos Teczi Factory
    │   ├── architecture/              # DAS + ADRs do produto
    │   └── projects/                  # PRJ-NNN-factory-{Demanda}/
    ├── service/                       # Projetos Teczi Service
    │   ├── architecture/              # DAS + ADRs do produto
    │   └── projects/                  # PRJ-NNN-service-{Demanda}/
    └── ...                            # Outros produtos conforme necessidade
```

---

## Stacks Aprovadas (catálogo Teczilabs original)

O DevFlow possui um catálogo de stacks permitidas (`templates/stack-catalog.md`):

| Combinação | Frontend | Backend | Banco | Auth |
|---|---|---|---|---|
| **A** — Firebase Full | Next.js 15 + TailwindCSS 4 + shadcn/ui | — | Firestore | Firebase Auth |
| **B** — Spring + Relacional | Next.js 15 + TailwindCSS 4 + shadcn/ui | Java 21 + Spring Boot 3/4 | PostgreSQL 16 + Redis 7 | NextAuth 5 |
| **C** — Spring + Document | Next.js 15 + TailwindCSS 4 + shadcn/ui | Java 21 + Spring Boot 3/4 | MongoDB 7 + Redis 7 | NextAuth 5 |

> Novas tecnologias exigem aprovação do Founder e atualização do catálogo.

### ⚠️ Override no contexto CaM-project

Este catálogo é o padrão para **produtos comerciais Teczilabs**. No **CaM-project** (cockpit pessoal, local, mono-operador vinculado ao Profit/Windows), esses combos **não se aplicam** e foram **revogados**.

A stack vigente do CaM está em [`../project/STACK-CAM-OFICIAL.md`](../project/STACK-CAM-OFICIAL.md):

```text
Profit + NTSL (executor) · Python 3.12 + FastAPI · React 19 + Vite + MUI · PostgreSQL 16 + TimescaleDB (desde Fase 0) · DuckDB (research) · Telegram · Ollama/Anthropic (IA auditora)
```

Qualquer demanda no CaM segue a stack oficial do CaM, não os Combos A/B/C.

---

## Como Usar

1. **Iniciar Jornada** — Identifique a jornada (Construção, Evolução, Melhoria) e carregue o agent da Fase 1 (`agents/discovery.md`)
2. **Seguir Fases** — Cada fase ativa seu agent. O LLM conduz e apresenta artefatos para QA Documental antes de avançar
3. **QA Documental** — Todo artefato passa por: `DRAFT → QA (Founder aprova/ajusta) → FINAL`
4. **Nenhum artefato avança sem aprovação explícita do Founder**

Processo completo: [`devflow/PROCESS.md`](devflow/PROCESS.md)

---

## Referências

| Documento | Localização |
|---|---|
| Processo completo | `devflow/PROCESS.md` |
| Personas do DevFlow | `teczilabs/personas/personas-devflow.md` |
| Todas as personas | `teczilabs/personas/personas-teczilabs.md` |
| Catálogo de Stacks | `devflow/templates/stack-catalog.md` |
| Instruções Claude Code | `devflow/config/claude-code.md` |
| Instruções Copilot | `devflow/config/copilot.md` |

---

> **Teczilabs** — One-Person Unicorn

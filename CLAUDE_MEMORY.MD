# CLAUDE_MEMORY.MD — Memória Portátil do CaM Project

> **Para quem é este documento:** futura instância do Claude Code aberta no **Windows** (ambiente de produção do CaM, após Carlos portar o repositório via Git). Este arquivo permite reconstruir o contexto operacional em segundos sem reler todo o histórico.
>
> **Última atualização:** 2026-05-24
> **Origem:** sessão Linux (Ubuntu 26.04 LTS) onde toda a base do projeto foi estruturada
> **Próximo passo previsto:** Carlos abre o repo no Windows 11, ativa Claude Code, e este arquivo é a porta de entrada

---

## 1. Quem é o usuário

**Carlos Rodrigues Ferreira Junior** — operador único do CaM.

- Engenheiro de software experiente (background Java/backend, Porto + Monnezy beta)
- Founder da **Teczilabs Tecnologia** (one-person unicorn em construção)
- Em 2020, perdeu R$ 100.000 sobre reserva de R$ 50.000 no mercado — o CaM nasce dessa lição
- Idioma de trabalho: **português**
- Estilo: pragmático, direto, anti-burocracia, anti-overengineering. Responde curto, espera curto

---

## 2. O que é o CaM

**CaM — The Carlos Alternative Money.** Cockpit pessoal, local, **não comercial** de operação de mercado. Existe para **impedir decisões impulsivas, preservar capital e converter ganhos táticos em patrimônio** — não para enriquecer rápido.

- Capital declarado: **R$ 5.000,00** (Bucket Derivativo R$ 3.000 + Buffer R$ 1.000 + Carteira Hard R$ 1.000)
- Limite absoluto: **2 contratos WIN / 2 contratos WDO** (intocável — Art. 11º)
- Estado atual: **Fase 0 — Construção** (sem trade real, sem paper trading)
- Operador único: Carlos

**Não confundir CaM com Teczilabs.** CaM é projeto pessoal de Carlos, com perímetro de capital separado (Art. 8º). Custos de plataforma, ferramentas e infra são absorvidos pela pessoa física, fora do CaM. A relação com a Teczilabs é metodológica: CaM é o primeiro dogfood do Teczi DevFlow NCC-1701.

---

## 3. Hierarquia constitucional inviolável

```
Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual
```

(Art. 36º — Subordinação da IA. **Você é instrumento**, não autoridade.)

**Você (IA) NÃO PODE** (Art. 35º):
- enviar ordem
- desabilitar, contornar ou parametrizar o Risk Engine
- justificar exceção a regra constitucional
- recomendar aumento de exposição sem evidência estatística
- atuar como autoridade final de execução em tempo real
- ser usada como advogada de defesa para violação do operador

**Em conflito entre regras, prevalece a que preserva mais capital** (Art. 6º).

---

## 4. Estado do repositório (fotografia da última sessão)

```
CaM-project/
├── CONSTITUICAO.md             ← LEI SUPREMA (v1.0 consolidada, 43 artigos + 3 anexos)
├── CLAUDE.md                   ← Contexto operacional Claude (idioma PT-BR padrão)
├── CLAUDE_MEMORY.MD            ← Este arquivo (memória portátil)
├── README.md                   ← README institucional
│
├── apps/                       ← Vazio (Fase 0). Estrutura prevista: apps/cam-cockpit/{backend,frontend,ntsl}
│   └── README.md                  Backend: cam/{_shared,features,api} — Vertical Slice + Shared Kernel
│                                  Frontend: src/{_shared,features,app} — Vertical Slice também
│
├── project/                    ← Artefatos DevFlow vivos (SCOPE, SPEC, PLAN, ADRs, ...)
│   ├── README.md
│   └── STACK-CAM-OFICIAL.md    ← STACK CANÔNICA (revoga Combos A/B/C Teczilabs)
│
├── archive/                    ← Memória física não-canônica
│   ├── README.md
│   ├── CONSTITUIÇÃO OPERACIONAL.txt    (v0.1 fundacional)
│   ├── CaM_Constituicao_v1.0.txt        (v1.0 .txt original)
│   └── insumos-stack/
│       ├── CLAUDE-STACK-RECOMENDATION.MD
│       ├── GPT-STACK-RECOMENDATION.md
│       └── README.md
│
├── teczi-devflow/              ← Framework embarcado (NCC-1701 v6.0)
│   ├── CLAUDE.md
│   ├── README.md
│   ├── NCC-1701/{phases,states,governance,templates,skills}/
│   └── personas/               ← 14 personas ativas + cast estendido
│
└── .claude/
    ├── agents/                 ← 25 agents (14 ativos NCC-1701 + 11 cast estendido)
    ├── skills/                 ← 13 skills (11 DevFlow portadas + strategy-session + teczi-discovery-software)
    ├── settings.json           ← bypassPermissions ON — exercer mesmo cuidado
    └── settings.local.json
```

**Nenhum git init feito ainda** — Carlos vai fazer Git no Windows.

---

## 5. Stack vigente (resumo executável)

> ⚠️ **DECISÃO PENDENTE DO FOUNDER:** existem **duas variantes de stack em paralelo** — Carlos ainda não escolheu se opera em Windows ou Linux. A escolha define broker, SO de produção, integração e custos.
>
> | Variante | Documento canônico | Resumo |
> |---|---|---|
> | **Windows + Profit** | [`project/STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md) | Profit Pro/NTSL como executor; SO produção Windows 11; ProfitDLL futura |
> | **Linux + MT5** | [`project/STACK-CAM-OFICIAL-LINUX.MD`](./project/STACK-CAM-OFICIAL-LINUX.MD) | MetaTrader 5 + MQL5 como executor; SO Linux nativo (Ubuntu LTS); MT5 via Wine ou VPS Windows; bridge ZeroMQ |
>
> **Matriz comparativa explícita** está em `STACK-CAM-OFICIAL-LINUX.MD` §13 (Custo, estabilidade, documentação PT, dev=prod, etc).
>
> **O que NÃO depende da decisão** (idêntico nas duas variantes):

```
Python 3.12 + FastAPI       →  Cockpit local (Risk Engine, Ledger, Journal, IA)
Vertical Slice + Shared Kernel → Arquitetura backend (ADR-013)
React 19 + Vite + MUI       →  Frontend SPA local (sem Next.js)
PostgreSQL 16 + TimescaleDB →  Banco transacional + tick/candle storage (desde Fase 0)
                                (hypertables + continuous aggregates + hyperfunctions)
DuckDB                      →  Motor analítico AUXILIAR (research read-only em CSV/Parquet)
Telegram Bot                →  Canal externo de alerta
Ollama local + Anthropic API → IA auditora/analista, NUNCA executora
Git + GitHub privado        →  Versionamento e governança
Constituição, NCC-1701, todas as personas e skills → INDEPENDENTES da escolha
```

**O que MUDA conforme a decisão:**

| Camada | Windows+Profit | Linux+MT5 |
|---|---|---|
| SO produção | Windows 11 | Ubuntu 24.04+ LTS (dev=prod) |
| Broker | Profit Pro/Ultra | MetaTrader 5 |
| Linguagem broker | NTSL | MQL5 |
| Artefatos em `/apps/cam-cockpit/` | `ntsl/` | `mql5/` (EAs) |
| Feature de integração | `features/profit_integration/` | `features/mt5_integration/` (bridge ZeroMQ) |
| Custo recorrente Fase 1 | R$ 200–380/mês (Profit Pro) | R$ 0–30/mês (ou R$ 80–180 com VPS Windows opcional) |
| Docker | Docker Desktop + WSL2 | Docker Engine nativo |

**REVOGADOS no contexto CaM:** Java/Spring, Firebase, Next.js, MongoDB, NextAuth (eram Combos A/B/C do catálogo Teczilabs, vieram de inferência, não se aplicam). **Arquitetura hexagonal** também foi revogada — substituída por **Feature-Based Vertical Slice + Shared Kernel mínimo** (ADR-013) para otimizar desenvolvimento agêntico.

**Regras invioláveis da arquitetura** (enforçadas por `import-linter` no CI):

1. `features/X/` NUNCA importa `features/Y/` — comunicação só via `_shared/` ou eventos
2. `_shared/risk/` é autoridade — toda feature que toque ordem chama `from cam._shared.risk import engine`
3. `_shared/risk/` é Pure Python, zero I/O (mandato constitucional Art. 15º)
4. Entrar em `_shared/` exige: uso por 3+ features OU mandato constitucional
5. Cada `features/X/` tem README.md obrigatório com o contrato da feature

Documento canônico: [`project/STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md) §6.2 e ADR-013.

---

## 6. Framework de processo: Teczi DevFlow NCC-1701

Toda construção segue o framework embarcado em [`teczi-devflow/NCC-1701/`](./teczi-devflow/NCC-1701/).

```
9 fases: PDOC → DISC → ARCH → SPEC → PLAN ⇄ (loop) → CODE → QA → DEPLOY → SDOC
2 estados: BUG (fast-track, Bill) · OPS (contínuo, Vint)
2 governanças: SEC-GOV (gatilho, Kevin) · CHANGE (em DEPLOY, Tom)
```

**Founder-only nos gates** — Carlos aprova cada transição. **Sem estimativas em horas/dias/semanas** — apenas P/M/G. **SDOC e DRIFT só sob solicitação explícita.**

### 14 personas ativas

| Persona | Papel | Skill |
|---|---|---|
| `leo` | Orquestrador-chefe — ponto único de entrada | — |
| `marty` | DISC | `teczi-project-discovery` |
| `albert` | SPEC + P/M/G | `teczi-demand-specification` |
| `oscar` | ARCH | `teczi-architecture-decision` |
| `nico` | PLAN (loop com Albert sobre P/M/G) | `teczi-code-planning` |
| `nikola` | CODE | `teczi-code-execution` |
| `linus` | QA | `teczi-quality-assurance` |
| `bill` | Estado BUG | `teczi-bug-fix` |
| `steve` | DEPLOY narrativa | `teczi-deploy` |
| `tom` | DEPLOY versionamento + CHANGE | `teczi-deploy` |
| `vint` | DEPLOY exec + OPS + INFRA-ARCH | `teczi-deploy` |
| `kevin` | SEC-GOV transversal | `teczi-security-governance` |
| `denis` | PDOC + SDOC | `teczi-project-creation`, `teczi-software-documentation` |
| `howard` | SDOC DRIFT (sob solicitação) | `teczi-software-documentation` |

Cast estendido: `sun`, `voltaire`, `mammon`, `grace`, `alan`, `andy`, `ada`, `peter`, `florence`, `fred`, `don`.

Default em demanda nova: invocar `leo` para triagem.

---

## 7. O que foi decidido nesta sessão (resumo de mudanças)

| Decisão | Onde está |
|---|---|
| Estrutura `/apps` e `/project` criada com READMEs | `apps/`, `project/` |
| Constituição consolidada (v0.1 + v1.0 → único .md) | `CONSTITUICAO.md` |
| Stack oficial CaM definida (revoga Combos Teczilabs) | `project/STACK-CAM-OFICIAL.md` |
| 11 skills DevFlow portadas para `.claude/skills/` | `.claude/skills/teczi-*` |
| 25 agents adaptados ao NCC-1701 e contexto CaM | `.claude/agents/` |
| Leo reescrito do zero adaptado ao CaM | `.claude/agents/leo.md` |
| README institucional do CaM | `README.md` |
| CLAUDE.md raiz atualizado | `CLAUDE.md` |
| .txt originais → archive | `archive/` |
| Insumos de stack (Claude + GPT) → archive | `archive/insumos-stack/` |

---

## 8. Ambiente Linux atual (inventário)

✅ **Já instalado:**
- Ubuntu 26.04 LTS
- Git 2.53
- Node 24.15 + npm 11.14 + pnpm 11.0
- Docker 29.1
- GitHub CLI 2.46
- Python 3.14.4 (mais novo que 3.12 — algumas libs quant podem não suportar ainda)

❌ **Faltam (instalar antes de começar Fase 0 em Linux):**
- `pip` (não está no path — pode estar como `pip3.14` ou faltar pacote `python3-pip`)
- `uv` (gerenciador de deps Python recomendado pela stack)
- `ruff` (lint Python — instala via `uv tool install ruff`)
- Cliente PostgreSQL CLI (`psql`) para inspeção do banco (`postgresql-client`)
- `rclone` (backup futuro — opcional na Fase 0, recomendado em M2+)

**Comandos de instalação Ubuntu 26.04** (executar quando voltar pro Linux):

```bash
sudo apt update
sudo apt install -y python3-pip postgresql-client
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv (recomendado pela stack)
# rclone opcional:
sudo apt install -y rclone
# Postgres+Timescale roda em Docker, não precisa instalar localmente:
# docker compose up -d  (a partir de apps/cam-cockpit/, quando o repo for criado)
```

> SQLite foi descartado da stack (ver `project/STACK-CAM-OFICIAL.md` ADR-004). Banco é PostgreSQL 16 + TimescaleDB em container, ativo desde M1.

---

## 9. Para o Claude no Windows — primeira ação ao entrar no repo

1. **Ler este arquivo (CLAUDE_MEMORY.MD)** — você acabou de fazer isso.
2. **Ler `CONSTITUICAO.md`** — pelo menos Parte I (princípios), IV (Risk Engine), IX (IA), X (governança e emenda).
3. **Ler `CLAUDE.md`** raiz — regras de orientação, idioma PT-BR.
4. **Ler `project/STACK-CAM-OFICIAL.md`** — stack vigente.
5. **Ler `teczi-devflow/NCC-1701/process.md`** se for atuar em demanda.
6. **Confirmar instalações Windows** (próxima seção).

### Instalações esperadas no Windows 11 (validar antes de codar)

```powershell
# Conferir o que já existe
git --version
python --version       # esperado: 3.12.x (se não tiver, baixar de python.org)
node --version         # esperado: 20 LTS ou 24+ ok
pnpm --version
docker --version       # Docker Desktop com WSL2 — OBRIGATÓRIO desde Fase 0 (Postgres+Timescale)
gh --version
psql --version         # cliente PostgreSQL para inspeção do banco

# Provavelmente faltarão (instalar via winget):
winget install --id Python.Python.3.12
winget install --id astral-sh.uv
winget install --id Microsoft.PowerShell           # opcional, PS7
winget install --id Git.Git                        # se faltar
winget install --id GitHub.cli                     # se faltar
winget install --id OpenJS.NodeJS.LTS              # se faltar
winget install --id pnpm.pnpm                      # se faltar
winget install --id Docker.DockerDesktop           # OBRIGATÓRIO — Postgres+Timescale desde M1
winget install --id PostgreSQL.PostgreSQL.16       # apenas para ter psql CLI; servidor roda em Docker

# Profit Pro (Nelogica): instalação manual via site oficial
# Módulo de Automação de Estratégias: contratar separadamente (Fase 4+)
```

> **Atenção Windows:** Docker Desktop em PF/uso pessoal é gratuito (licença pessoal). Para empresas grandes (>250 funcionários ou >US$ 10M) requer assinatura paga — não se aplica ao Carlos PF.

---

## 10. Como Claude deve se comportar neste projeto

- **Idioma: português.** Sempre.
- **Curto e direto.** Carlos não tolera floreio.
- **Sem horas/dias/semanas** em qualquer estimativa — só P/M/G.
- **Constituição vence.** Em qualquer dúvida, aplique Art. 6º (preserva mais capital).
- **Risk Engine vence Estratégia.** Estratégia vence IA. IA não vence ninguém.
- **Você invoca personas via Agent tool**, não simula. Default em demanda nova: `leo`.
- **Você invoca skills via Skill tool** quando aplicável (toda fase/estado/governança tem uma).
- **bypassPermissions ON** — não vai ter prompt para confirmar. Tome cuidado equivalente, especialmente em ações destrutivas.
- **Não há git init ainda.** Quando Carlos inicializar git, respeitar: sem commit em `main`, sem secrets, sem rebase/amend/force push.
- **Memory system Claude próprio:** existe `/home/.../memory/` no Linux. No Windows, equivalente ficará em `%USERPROFILE%\.claude\projects\...\memory\`. Carlos pode optar por carregar/não carregar essa memória.

---

## 11. Próximas decisões pendentes (bloqueadores Fase 1)

1. ⭐ **DECISÃO-MÃE: Windows+Profit vs Linux+MT5** — sem isso, nada começa. Carlos decide entre [`project/STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md) e [`project/STACK-CAM-OFICIAL-LINUX.MD`](./project/STACK-CAM-OFICIAL-LINUX.MD). Matriz comparativa explícita está em `STACK-CAM-OFICIAL-LINUX.MD` §13. O documento não escolhido vai para `archive/`
2. **Versão do Profit** (se Windows) — Pro ou Ultra? Decidir antes de Fase 1
3. **Hospedagem do MT5** (se Linux) — Wine local OU container Wine OU VPS Windows
4. **Bridge MT5↔Python** (se Linux) — ZeroMQ (recomendado) OU socket TCP custom OU MetaApi SaaS
5. **Corretora vinculada** — corretagem por mini contrato impacta edge mínimo. Confirmar se permite WIN/WDO na plataforma escolhida (Profit ou MT5)
6. **Tese de edge da primeira estratégia** — sem isso, Fase 0 constrói infra sem destino
4. **Schedule de revisão da stack** — quando reavaliar versão Postgres, modelo IA, etc.
5. **Origem do tick histórico para backfill** — Profit exporta tick? Ou só candles? Define estratégia de backfill da Timescale na M2.

---

## 12. Frases que Carlos vive (orientação cultural)

> "O CaM não existe para provar que o operador está certo.
> O CaM existe para impedir que o operador quebre quando estiver convicto demais."
> — Art. 4º, Regra de Ouro

> "O mercado não deve ser enfrentado com emoção.
> O mercado deve ser operado com sistema, limite, registro e humildade."
> — Art. 5º, Frase Constitucional

> "O Profit executa. O Python fiscaliza. O React mostra.
> O Ledger registra. O Risk Engine manda. A IA comenta.
> O Carlos obedece ao sistema."
> — STACK-CAM-OFICIAL §1

---

## 13. Sinais de que algo está errado (red flags para o Claude)

Se em alguma sessão futura você se pegar fazendo qualquer um destes, **pare imediatamente** e questione:

- Recomendando arquitetura com Java/Spring/Firebase/Next.js para o CaM
- Estimando algo em horas/dias/semanas
- Sugerindo bypass do Risk Engine "só para esse caso"
- Inferindo decisões que cabem ao Founder
- Aprovando algo em "modo automático" sem gate Carlos
- Implementando feature que viole limite de contratos (Art. 11º)
- Mostrando P&L bruto sem provisão fiscal (Art. 25º)
- Permitindo IA enviar ordem (Art. 35º)
- Sugerindo aumentar contratos após loss para recuperar (Art. 13º — martingale proibido)

---

## 14. Onde olhar para entender mais

| Para entender | Leia |
|---|---|
| Por que o CaM existe | `CONSTITUICAO.md` Preâmbulo + Parte I |
| O que o sistema NÃO pode fazer | `CONSTITUICAO.md` Parte III, IV, IX |
| Stack e por quês | `project/STACK-CAM-OFICIAL.md` |
| Como construir qualquer coisa | `teczi-devflow/NCC-1701/process.md` |
| Personas e papéis | `.claude/agents/` + `teczi-devflow/personas/` |
| Histórico das decisões de stack | `archive/insumos-stack/README.md` |
| Visão pública | `README.md` |
| Como você (Claude) deve se comportar | `CLAUDE.md` raiz |

---

> **Boas-vindas, Claude no Windows.** O CaM está em Fase 0. Não há código ainda. Sua função até a Fase 1 é ajudar Carlos a **construir o cockpit que protege o capital dele**. Em qualquer dúvida operacional: invoque Leo. Em qualquer dúvida estratégica: invoque Voltaire. Em qualquer dúvida sobre segurança: invoque Kevin. Em qualquer dúvida sobre o que o sistema *deve* fazer: leia a Constituição.

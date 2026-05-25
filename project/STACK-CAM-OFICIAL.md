# STACK-CAM-OFICIAL — variante Windows + Profit

> **Projeto:** CaM — The Carlos Alternative Money
> **Documento:** Stack Oficial — **variante Windows + Profit/NTSL**
> **Versão:** 1.0
> **Data:** 2026-05-24
> **Status:** Proposta em paralelo a [`STACK-CAM-OFICIAL-LINUX.MD`](./STACK-CAM-OFICIAL-LINUX.MD) (variante Linux + MetaTrader 5)
> **Decisão pendente:** Carlos vai escolher entre **esta variante (Windows+Profit)** OU a variante Linux+MT5 — matriz comparativa explícita está em `STACK-CAM-OFICIAL-LINUX.MD` §13
> **Vinculação constitucional:** [`../CONSTITUICAO.md`](../CONSTITUICAO.md)
> **Insumos:** `archive/insumos-stack/CLAUDE-STACK-RECOMENDATION.MD`, `archive/insumos-stack/GPT-STACK-RECOMENDATION.md`
> **Síntese por:** Voltaire (devil's advocate) + Grace (arquitetura) + Oscar (decisões formais como ADRs)
> **Aprovação:** Pendente — Founder valida em gate explícito antes de virar SPEC

---

## 0. Decisão de Override

Esta stack **revoga formalmente** os Combos A/B/C do catálogo DevFlow Teczilabs (Firebase Full, Spring + Relacional, Spring + Document). Aquelas combinações foram inferidas para produtos comerciais Teczilabs e **não se aplicam ao CaM** — cockpit local, mono-operador, vinculado ao Profit/Windows.

Tudo que aparecer em qualquer skill/agent/template referenciando Java/Spring/Firebase/Next.js como "stack permitida" no contexto CaM é **inválido** e deve ser substituído pela referência a este documento.

---

## 1. Resumo Executivo

```text
Profit/Nelogica        →  Plataforma de execução (NTSL + Automação de Estratégias)
Python 3.12 + FastAPI  →  Cockpit local: Risk Engine, Ledger, Journal, integração, auditoria
React 19 + Vite + MUI  →  Frontend local (SPA servida pelo backend FastAPI)
PostgreSQL 16 + TimescaleDB → Banco transacional + tick/candle storage (desde Fase 0)
DuckDB                 →  Motor analítico auxiliar (research em CSV/Parquet, backtest exploratório)
Telegram Bot           →  Canal externo de alerta (kill switch, loss limit, DARF, etc.)
Ollama local + Anthropic → IA auditora/analista, NUNCA executora
Git + GitHub privado   →  Versionamento e governança
SO produção: Windows 11 (Profit é Windows-only)
SO desenvolvimento: Linux (eficiência) + Windows para integração final
```

**Frase de arquitetura:**

> O Profit executa. O Python governa. O React mostra. O Ledger registra. O Risk Engine manda. A IA comenta. O Carlos obedece ao sistema.

---

## 2. Princípios da Stack

Cada decisão abaixo deriva de pelo menos um destes princípios (numerados para referência):

1. **Soberania da Constituição** — toda escolha sobrevive à hierarquia `Constituição > Risk Engine > Estratégia validada > IA > Operador` (Art. 36º).
2. **Profit é o executor, CaM é o cockpit** — o CaM não substitui o Profit; aumenta-o com governança, ledger e auditoria.
3. **Localidade absoluta** — nada essencial depende de serviço externo. Cloud é opcional para backup.
4. **DRY entre backtest e live** — funções de sinal/risco rodam idênticas em backtest, paper e live. Sem reescrita.
5. **Falha segura** — qualquer falha técnica degrada para "não envia ordem", nunca para "executa fora de regra".
6. **Auditabilidade** — todo evento operacional gera registro estruturado, imutável e datado (Art. 31º).
7. **Custo controlado** — Art. 8º: custos saem do bolso do operador, fora do CaM. Favorece open source.
8. **Familiaridade com ressalva** — alinhamento com stack Teczilabs (Monnezy: React/Vite, MUI) onde tecnicamente equivalente. Backend NÃO segue Monnezy (NestJS/Java) porque o domínio quant é Python.
9. **Faseamento Profit** — integração com Profit cresce por fases (manual → CSV → semi-auto → NTSL → APIs), nunca pula etapas.
10. **Hierarquia da autoridade de risco** — Risk Engine Python é **pré-validador definitivo** + NTSL no Profit espelha regras hard-coded **como segunda linha de defesa**.

---

## 3. Restrições

| Item | Valor | Origem |
|---|---|---|
| SO de produção | Windows 10/11 | Profit é Windows-only |
| SO de desenvolvimento | Linux (atual) → Windows (integração) | Eficiência de dev em Linux, integração final em Windows |
| Plataforma broker | Profit Pro ou Profit Ultra | Decisão do Founder; Automação de Estratégias para conta real |
| Capital declarado | R$ 5.000,00 | Constituição Art. 7º |
| Modelo de uso | Mono-usuário, local | Constituição Art. 1º |
| Custos da stack | PF, fora do perímetro CaM | Constituição Art. 8º |
| Operação simultânea WIN+WDO | Vetada na fase inicial | Constituição Art. 12º |

---

## 4. Camadas da Stack — Visão Geral

```text
┌─────────────────────────────────────────────────────────────────────┐
│                          CaM Cockpit (React + Vite + MUI)            │
│  Dashboard | Journal | Risk Console | Backtest | Paper | Harvest    │
│  Carteira Hard | Fiscal | Constituição (read-only) | Configurações  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP + WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CaM Core (Python 3.12 + FastAPI)            │
│  domain | risk* | strategies | execution | paper | market_data      │
│  journal | fiscal | backtest | harvest | notifications | api | ai   │
│  (* risk = Pure Python sem I/O, propriedade-based test 100%)        │
└────────┬───────────────────────────────────┬────────────────────────┘
         │                                   │
         ▼                                   ▼
┌────────────────────────────────┐  ┌──────────────────────────────────┐
│      Local Storage              │  │     Profit Pro / Nelogica         │
│  PostgreSQL 16 + TimescaleDB    │  │  NTSL + Editor de Estratégias     │
│  (hypertables + continuous      │  │  Automação de Estratégias (módulo │
│   aggregates desde Fase 0)      │  │   contratado para conta real)     │
│  DuckDB (research em arquivos)  │  │  Importação CSV / Excel           │
│  JSONL append-only (fallback)   │  │  ProfitDLL (ctypes) — Fase 4+     │
└────────────────────────────────┘  └──────────────────────────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │     Telegram Bot (alertas)    │
                └──────────────────────────────┘
```

---

## 5. Componentes — Tabela Canônica

| Camada | Tecnologia | Versão alvo | Princípio |
|---|---|---|---|
| Execução de ordens | Profit Pro / Profit Ultra + Automação de Estratégias | atual | 2, 9 |
| Linguagem estratégia executada no broker | NTSL (Nelogica Trading System Language) | atual | 2, 9 |
| Linguagem backend cockpit | Python | 3.12.x | 4, 7, 8 |
| Framework web/API | FastAPI | 0.115+ | 4, 5, 7 |
| ASGI server | Uvicorn | 0.32+ | padrão FastAPI |
| Validação de schema | Pydantic v2 | 2.x | 6 |
| ORM | SQLAlchemy 2.0 | 2.0.x | 4, 6 |
| Migrations | Alembic | 1.13+ | 6 |
| Banco transacional + time series | PostgreSQL 16 + TimescaleDB (extensão) | 16 / 2.x | desde Fase 0 (volume de tick + análise de padrões) |
| Motor analítico auxiliar | DuckDB | 1.x | research em arquivos (CSV/Parquet), backtest exploratório |
| Cache/Event bus (opcional) | Redis | 7.x | apenas se necessário |
| Frontend framework | React + Vite | 19.x / 6.x | 7, 8 |
| Linguagem frontend | TypeScript | 5.x | 6, 8 |
| UI Library | MUI (Material UI) | 6+ ou 7 | 8 |
| Estado UI | Zustand | 5.x | simplicidade |
| Estado server | TanStack Query | 5.x | sincronização HTTP |
| Roteamento | React Router | 6.x | padrão |
| Gráficos candles | TradingView Lightweight Charts | 4.x | open source, padrão indústria |
| Gráficos métricas | Recharts | 2.x | alinhamento Teczilabs |
| Validação cliente | Zod | 3.x | 6 |
| Streaming | WebSocket nativo FastAPI | — | 4, 5 |
| Notificações externas | python-telegram-bot ou aiogram | 21+ | 5, 6 |
| Logs estruturados | structlog | 24+ | 6 |
| Backtest engine | Custom Python (DRY com live) + vectorbt (research) | 0.27+ | 4 |
| Testes | pytest + pytest-asyncio + hypothesis | atuais | 1, 6 |
| Lint/format Python | ruff | latest | 7 |
| Type check Python | mypy ou pyright | latest | 6 |
| Gerência de deps Python | uv | latest | 7 |
| Gerência de deps frontend | pnpm | 9.x | 7 |
| Containers (opcional Fase 3+) | Docker Desktop + WSL2 | atual | apenas Postgres/Redis |
| Versionamento | Git + GitHub privado | — | 6, 7 |
| Scheduler interno | APScheduler ou cron Python | latest | rotinas pós-mercado |
| IA local (opcional) | Ollama | latest | 1, 7 |
| IA externa (sob demanda) | Anthropic API (Claude) | atual | 1, anonimizar dados sensíveis |
| Backup automatizado | rclone para Google Drive / S3 | latest | 3, 6 |

---

## 6. Detalhamento por Camada Crítica

### 6.1 Camada de Execução — Profit + NTSL + Automação de Estratégias

**Decisão fundadora:** o Profit é o executor. O CaM não envia ordem por caminho alternativo no MVP (Fase 0–3).

**Como funciona em produção:**

1. Carlos contrata **Profit Pro** (ou Ultra) com book.
2. Para Fase 4+ com conta real automatizada: contrata **módulo de Automação de Estratégias**.
3. As regras de **risco mecânico não-negociáveis** (limite de contratos Art. 11º, janelas vedadas, stops padrão) ficam **espelhadas** em NTSL como **segunda linha de defesa**.
4. A regra de **decisão de entrada/saída** roda primeiro no Python (Risk Engine + Strategy), que **autoriza** a estratégia NTSL a executar via flag/parâmetro lido pelo Profit.

**Faseamento da integração** (sequencial, sem pular):

| Fase | O que o CaM faz com o Profit | Quando avança |
|---|---|---|
| **F1 — Manual** | CaM gera plano do dia, checklist, Risk Engine valida. Carlos opera Profit manualmente. CaM registra trades manualmente | Após primeira semana operando com 0 violação |
| **F2 — Importação CSV** | CaM importa CSV/extrato Profit pós-mercado. Concilia journal manual × execução real. Tax ledger automático | Quando importação cobre 100% das operações sem erro |
| **F3 — Semi-automática** | CaM monitora estado do Profit em tempo real (status, P&L, posição) via export periódico ou interface oficial. Ainda não envia ordem | Quando monitoramento é estável por 30 dias úteis |
| **F4 — NTSL com regras espelhadas** | Estratégia escrita em NTSL no Profit + Risk hard-coded em NTSL. CaM publica parâmetros vigentes. Execução real automática | Após validação em conta de simulação + módulo de Automação de Estratégias contratado |
| **F5 — ProfitDLL (avaliação)** | Apenas se necessidade real comprovar — adapter Python via ctypes para controle fino. **Não obrigatório** | Decisão futura por emenda |

**ADR-001 (CaM):** O Profit é a plataforma oficial de execução. ProfitDLL não é dependência da Fase 0–3.

---

### 6.2 Backend Python — Feature-Based Vertical Slice Architecture

**Decisão (revoga a arquitetura hexagonal proposta na v0):** o backend adota **Vertical Slice + Shared Kernel mínimo** para otimizar **desenvolvimento agêntico**. Cada feature é uma fatia auto-contida que um agente consegue ler, entender e modificar **lendo uma única pasta** — sem pular entre camadas técnicas (domain/application/infra) espalhadas em árvores diferentes.

**Por que Vertical Slice neste projeto:**

| Motivo | Impacto agêntico |
|---|---|
| Feature auto-contida em uma pasta | Agente lê 1 pasta, não 6 — menos tokens, menos drift de contexto |
| Paralelização sem conflito | Dois agentes trabalham em `features/journal/` e `features/fiscal/` simultaneamente sem touch overlap |
| Refactoring isolado | Mudança em `features/fiscal/` não toca código de outras features |
| Onboarding por feature | "Como funciona o journal?" → ler 1 README + 1 pasta |
| Contrato explícito | Cada feature publica seus eventos e endpoints; comunicação só por contrato |
| Menos abstração prematura | Sem porta/adapter/use-case ceremoniais quando ainda não há razão |

**Por que Shared Kernel ainda existe (mínimo):**

O **Risk Engine** é autoridade constitucional (Art. 15º) — **toda** feature que toque ordem precisa consultá-lo. Em vertical slice puro, "shared" vira lixão. A solução é um **kernel mínimo, congelado, versionado e auditado**, contendo apenas o que é genuinamente transversal e constitucional.

#### Estrutura

```
backend/
├── pyproject.toml          # uv + ruff + pytest + import-linter config
├── alembic.ini
├── migrations/
└── cam/
    │
    ├── _shared/                  # ╔══ SHARED KERNEL — usado por TODAS as features ══╗
    │   ├── README.md             #   regra: o que entra aqui é constitucional/transversal
    │   ├── risk/                 #   ▶ Risk Engine — autoridade (Pure Python, 100% test)
    │   │   ├── engine.py
    │   │   ├── validators/       #   máx_contracts, daily_loss, kill_switch, …
    │   │   ├── decisions.py      #   RiskDecision (Approved | Rejected)
    │   │   └── tests/            #   property-based (hypothesis)
    │   ├── domain/               #   ▶ primitivas: Money, ContractCount, Phase, AssetType
    │   ├── events/               #   ▶ event bus interno (asyncio.Queue / pyee)
    │   ├── audit/                #   ▶ audit logger transversal (structlog)
    │   ├── infra/                #   ▶ DB session factory, settings (pydantic-settings)
    │   └── config/               #   ▶ .env loader
    │
    ├── features/                 # ╔══ VERTICAL SLICES — cada pasta é auto-contida ══╗
    │   │
    │   ├── journal/              # Art. 31º — registro de operações
    │   │   ├── README.md         # contrato da feature (inputs, outputs, eventos, artigos)
    │   │   ├── domain.py         # JournalEntry, JournalQuery (entidades desta feature)
    │   │   ├── schemas.py        # Pydantic in/out (API + persistência)
    │   │   ├── repository.py     # SQLAlchemy específico desta feature
    │   │   ├── service.py        # lógica de aplicação
    │   │   ├── routes.py         # FastAPI router próprio
    │   │   ├── events.py         # eventos publicados/consumidos
    │   │   └── tests/
    │   │
    │   ├── fiscal/               # Arts. 24–27 — apuração DARF, IRRF, compensação
    │   ├── ledger/               # Arts. 7–10, 21–22 — buckets, capital, sangria
    │   ├── harvest/              # Art. 21º — distribuição mensal de lucro
    │   ├── strategies/           # ciclo de vida + parâmetros + registro
    │   ├── backtest/             # engine (usa _shared/risk/ + features/strategies/)
    │   ├── paper_trading/        # paper adapter (mesma interface conceitual de profit)
    │   ├── profit_integration/   # CSV importer + NTSL publisher + (futuro) ProfitDLL
    │   ├── market_data/          # ingestão e armazenamento de tick/candle
    │   ├── kill_switch/          # Art. 18º — mecanismo de interrupção imediata
    │   ├── checklists/           # Arts. 32–33 — pré/pós mercado
    │   ├── notifications/        # bot Telegram (subscriber em eventos críticos)
    │   ├── ai_analyst/           # Ollama + Anthropic (auditor pós-mercado)
    │   └── constitution/         # versionamento, emendas (Art. 38º), POV (Art. 37º)
    │
    ├── api/                      # ╔══ COMPOSER FASTAPI — só monta o app ══╗
    │   ├── main.py               # cria FastAPI, registra routers de cada feature
    │   ├── lifespan.py           # startup/shutdown hooks
    │   ├── middleware.py         # CORS, audit, rate limit local
    │   └── websocket.py          # WS broker (subscribe em _shared/events)
    │
    └── tests/                    # testes que cruzam features
        ├── e2e/                  # signal → risk → execution → journal
        └── integration/
```

#### Regras invioláveis (enforçadas por `import-linter` no CI)

1. **`features/X/` NUNCA importa de `features/Y/`** — sem exceção. Comunicação cross-feature só por:
   - `_shared/` (kernel)
   - Eventos publicados/consumidos via `_shared/events/`
   - Composição na camada `api/` (que conhece todas as features, mas features não conhecem a si)
2. **`_shared/risk/` é autoridade** — toda feature que valide ou autorize ordem chama `from cam._shared.risk import engine`. Nunca duplica regra constitucional.
3. **`_shared/risk/` NÃO importa de NADA** — Pure Python, zero I/O. Quebra de build se importar `features/`, `api/`, `infra/db`, etc.
4. **`_shared/` só cresce com fricção real** — para entrar em shared kernel: o item tem que ser usado por **3+ features** OU ser **mandato constitucional**. Caso contrário, fica na feature.
5. **Cada `features/X/` tem README.md obrigatório** — contrato da feature: propósito, inputs (HTTP endpoints + eventos consumidos), outputs (eventos publicados, tabelas tocadas), artigos constitucionais aplicáveis, anti-padrões.

#### Convenção interna de cada feature

| Arquivo | Conteúdo | Obrigatório? |
|---|---|---|
| `README.md` | Contrato (propósito · I/O · eventos · artigos · anti-padrões) | Sim |
| `domain.py` | Entidades e value objects da feature | Sim se há lógica |
| `schemas.py` | Pydantic in/out | Sim se há API |
| `repository.py` | Acesso a dados (SQLAlchemy) | Sim se persiste |
| `service.py` | Lógica de aplicação | Sim |
| `routes.py` | FastAPI router (`@router.get(...)`) | Sim se expõe HTTP |
| `events.py` | Eventos publicados e handlers | Sim se comunica |
| `tests/` | Unit + integration da própria feature | Sim |

#### Diretrizes operacionais para o agente

- **Demanda nova de feature?** Criar pasta `features/{nome}/`, escrever README.md primeiro com o contrato.
- **Precisa de algo de outra feature?** NÃO importe. Ou publica/consome evento, ou eleva para `_shared/` se for genuinamente transversal (com gate Founder).
- **Precisa validar ordem/risco?** Chama `_shared/risk/`. Sem exceção.
- **Vai duplicar código de outra feature?** Primeiro pergunta: posso evitar? Se não, duplica conscientemente — repetição é mais barata que acoplamento errado em vertical slice.
- **A feature `audit_log` ficou parecida com `events`?** Provavelmente são a mesma — funde antes de virar dois.

> **Por que essa arquitetura sobrevive ao crescimento:** quando o CaM tiver 30 features, o agente continua lendo uma pasta para entender uma feature. Em arquitetura hexagonal, com 30 features, `domain/`, `application/`, `infra/` ficam imensos e exigem navegação cruzada constante — péssimo para LLM.

---

### 6.3 Risk Engine — `cam/_shared/risk/`

Módulo Python puro **dentro do Shared Kernel** (autoridade transversal — Art. 15º). Recebe `OrderCandidate` + `RiskContext`, retorna `RiskDecision` (`Approved` ou `Rejected(reason: str)`). Nenhuma feature pode duplicar regra constitucional — todas chamam `from cam._shared.risk import engine`.

**Validators mínimos (cobertura 100% obrigatória — Anexo II saída Fase 0):**

| Validator | Artigo |
|---|---|
| `max_contracts_check` (limite absoluto) | Art. 11º |
| `phase_contracts_check` (limite por fase) | Art. 12º (Fase 2: 1 contrato; sem simultaneidade) |
| `daily_loss_limit_check` (3%) | Art. 16º + POV |
| `weekly_loss_limit_check` (7%) | Art. 16º + POV |
| `monthly_loss_limit_check` (15% — congela fase) | Art. 16º + POV |
| `gain_lock_check` (2% diário encerra dia) | Art. 17º |
| `daily_operations_count_check` (3 Fase 1–2, 5 Fase 3–4) | Art. 20º + POV |
| `martingale_check` (proíbe aumentar contratos após loss) | Art. 13º |
| `trading_window_check` (15 min pós-abertura, 10 min pré-fechamento, eventos macro) | POV |
| `simultaneous_position_check` (WIN/WDO simultâneo só Fase 3+) | Art. 12º + POV |
| `circuit_breaker_check` (configurável) | Art. 18º |
| `kill_switch_active_check` | Art. 18º |
| `tax_compliance_check` (DARF atrasada bloqueia) | Art. 26º |
| `phase_authorization_check` (estratégia autorizada na fase atual) | Art. 30º |
| `setup_a_plus_check` (Fase 4 — 2 contratos só em Setup A+) | Art. 11º + Anexo II Fase 4 |
| `pre_market_checklist_check` (Art. 32º) | Art. 32º |
| `post_market_checklist_check` (bloqueia próximo pregão se ausente) | Art. 33º |

**Testes:**

- `tests/unit/test_risk/`: unitários por validator
- `tests/property/test_risk_invariants/`: property-based via `hypothesis` — gera cenários adversos
- Cada artigo da Constituição relevante tem teste nomeado: `test_art_11_max_contracts_absolute`, `test_art_15_risk_engine_authority`, etc.

---

### 6.4 Banco de Dados — PostgreSQL 16 + TimescaleDB desde Fase 0

**Decisão (revoga proposta anterior de SQLite no MVP):** PostgreSQL 16 com extensão TimescaleDB é o banco transacional **e** de séries temporais do CaM **desde o primeiro commit**. SQLite foi descartado.

#### Por que Postgres+Timescale desde o início

A premissa operacional do CaM exige **análise de padrões em estratégias** sobre **volume massivo de tick/candle data**. SQLite seria fricção pura:

- **Volume real:** 1 ativo (WIN ou WDO) em horário de pregão (10h–18h) com tick a 50–100 ms ≈ **300k–600k ticks/dia**. Dois ativos, dois anos de histórico para backtest ≈ **400M–800M registros**. SQLite não foi feito pra isso.
- **Análise de padrões** exige: window functions complexas, time-bucketing arbitrário (1s, 5s, 1m, 5m, 15m, 1h), gap-fill, agregações estatísticas (percentil, stddev móvel, ATR, ADX), correlações cross-ativo. Tudo nativo no Postgres+Timescale, doloroso no SQLite.
- **Continuous aggregates** (Timescale): candles em vários timeframes pré-agregados e atualizados em background. Backtest e dashboard consultam pré-agregados em ms — sem isso, cada query reagrega tick puro.
- **Compressão Timescale**: tick antigo comprime 10–95×. Sem compressão, 800M ticks ≈ centenas de GB; com compressão, dezenas de GB.
- **Hyperfunctions** (Timescale): `time_bucket`, `first/last`, `histogram`, `time_weight`, `interpolate`, `locf` — primitivas que substituem dezenas de linhas de Python.
- **JOIN tick × operacional**: cruzar tick data com `cam_trades`, `cam_risk_decisions` é trivial em Postgres, inviável em SQLite + Python.

Mudar de SQLite para Postgres no meio do projeto sai mais caro do que pagar o overhead inicial de Docker Desktop + WSL2.

#### Setup

- **Container:** `timescale/timescaledb:latest-pg16` via `docker-compose.yml` no repo do app (ativo desde M1)
- **Linux dev:** Docker nativo (já instalado: Docker 29.1)
- **Windows prod:** Docker Desktop + WSL2 (Carlos instala junto com a portabilidade)
- **Migrations:** Alembic com convenção de naming consistente, incluindo `CREATE EXTENSION timescaledb` na migration inicial
- **Acesso:** SQLAlchemy 2.0 + driver `psycopg[binary]` (v3). Sessions assíncronas para o backend FastAPI

#### Schemas

**Domínio operacional (tabelas regulares):**

```sql
cam_orders                    -- ordens propostas e executadas
cam_positions                 -- posições abertas/fechadas
cam_trades                    -- execuções (fills)
cam_journal_entries           -- entradas de journal (Art. 31º)
cam_risk_decisions            -- TODA decisão do Risk Engine (audit trail)
cam_violations                -- violações para cálculo de aderência (Art. 29º)
cam_constitution_versions     -- emendas constitucionais
cam_pov_versions              -- versões da POV (Art. 37º)
cam_phase_history             -- transições de fase
cam_checklist_pre_market      -- Art. 32º
cam_checklist_post_market     -- Art. 33º
cam_kill_switch_events        -- ativações do kill switch (Art. 18º)
```

**Fiscal (tabelas regulares):**

```sql
cam_fiscal_apuration          -- apuração mensal
cam_darf_history              -- DARFs gerados/pagos
cam_loss_compensation_ledger  -- prejuízos compensáveis (Art. 27º)
```

**Market data (Timescale hypertables — desde M1):**

```sql
cam_market_ticks              -- hypertable, chunk 1 dia, compressão > 7 dias
cam_market_book_snapshots     -- hypertable, chunk 1 dia, compressão > 3 dias
-- Continuous aggregates:
cam_candles_1s                -- agregação contínua de cam_market_ticks
cam_candles_5s
cam_candles_1m
cam_candles_5m
cam_candles_15m
cam_candles_1h
cam_candles_1d
-- (criados via CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous))
```

**Backtest / research (hypertable + regular):**

```sql
cam_backtest_runs             -- metadata da execução (regular)
cam_backtest_trades           -- trades simulados (regular)
cam_backtest_equity_curve     -- hypertable se grande
cam_pattern_studies           -- registro de estudos de padrão (regular)
```

#### Retenção e compressão

| Tabela | Retenção bruta | Política Timescale |
|---|---|---|
| `cam_market_ticks` | indefinida | compressão após 7 dias; reorder após 30 dias |
| `cam_market_book_snapshots` | 90 dias bruto | compressão após 3 dias; drop após 90 dias |
| `cam_candles_*` (continuous aggregates) | indefinida | sem compressão (já agregado, pequeno) |
| `cam_journal_entries`, `cam_risk_decisions`, `cam_violations` | **infinita** | memória institucional do CaM |
| `cam_orders`, `cam_trades`, `cam_positions` | infinita | memória operacional |
| `cam_fiscal_*` | infinita | exigência legal (5 anos mínimo, manter mais) |
| `cam_backtest_*` | configurável por run | drop após N execuções por estudo |

#### Backup

- `pg_dump` diário automatizado (cron Linux dev / Task Scheduler Windows prod) → `~/cam-backups/YYYY-MM-DD.dump`
- `rclone` para Google Drive ou S3 — sync incremental noturno
- **Journal duplo** (R5 mitigação): além do banco, append-only em `~/.cam/journal/YYYY-MM-DD.jsonl` versionado em Git privado separado — se o Postgres cair com posição aberta, journal local + JSONL ainda registra tudo

#### Papel do DuckDB nesta arquitetura

DuckDB **complementa** Postgres+Timescale, não substitui. Casos de uso:

- Research exploratório em CSV/Parquet exportado do Profit (importação inicial antes de virar hypertable Timescale)
- Notebooks Jupyter de pesquisa quant onde Carlos quer fazer query SQL em arquivo local sem subir nada
- Backtest em datasets isolados (um experimento específico) sem poluir o Postgres operacional

Decisão: DuckDB nunca grava em tabela vista pelo cockpit live. É read-only sobre arquivos.

---

### 6.5 Frontend — React 19 + Vite + MUI

**Decisão:** SPA local servida pelo backend FastAPI (`/static/cockpit/`). **Sem Next.js** — não há necessidade de SSR em cockpit local mono-usuário.

**Telas mínimas Fase 0:**

1. **Cockpit Live** — P&L líquido (Art. 25º), posições, status Risk Engine, **kill switch grande/vermelho/confirmação dupla** (Art. 18º), gauges de limite diário/semanal/mensal
2. **Trade Journal** — listagem com filtros, exportação
3. **Estratégias** — habilitar/desabilitar (com cooldown), parâmetros vigentes
4. **Risk Console** — POV vigente, log de decisões do Risk Engine, gauges
5. **Backtest** — executar, comparar, walk-forward
6. **Paper Trading** — mesma UI do Live + badge "PAPER" gigante em vermelho
7. **Carteira Hard** — snapshot patrimonial, dividendos, harvest history
8. **Fiscal** — apuração, DARF, compensação, alertas
9. **Constituição (read-only)** — visualização + histórico de versões + botão "propor emenda" (Art. 38º com cooldowns)
10. **Configurações** — conexão Profit, Telegram, paths

---

### 6.6 IA — Política Vinculante

(Constituição Arts. 34º–36º)

**Pode:**

- Analisar journal pós-mercado
- Gerar resumo diário/semanal/mensal
- Apontar anomalias comportamentais (aderência, padrões de loss)
- Sugerir hipóteses de estudo
- Code review de estratégias e do próprio Risk Engine
- Apoiar pesquisa quant

**Não pode:**

- Enviar ordem (Art. 35º)
- Desabilitar/contornar/parametrizar Risk Engine (Art. 35º)
- Justificar exceção a regra constitucional (Art. 35º)
- Atuar como autoridade final de execução em tempo real (Art. 35º)
- Ser advogada de defesa para violação do operador (Art. 35º)

**Onde roda:**

- **Job assíncrono pós-mercado** lê journal do dia → gera análise → envia via Telegram
- **Endpoints API** acionados manualmente pelo operador
- **CLI de research** separada (binário diferente do backend live)

**Modelos:**

- **Ollama local** (qwen2.5, llama3, etc.) para análise privada e dados sensíveis
- **Anthropic API (Claude)** quando análise demandar capacidade superior — apenas com dados anonimizados ou não sensíveis

---

## 7. Ambiente de Desenvolvimento

### 7.1 Dev em Linux (atual)

| Item | Por quê |
|---|---|
| Eficiência de tooling Python (uv, pytest, profiling) | WSL2 funciona, mas nativo é mais limpo |
| Build/test do frontend é cross-platform | Vite/pnpm funcionam idênticos |
| Risk Engine, domain, strategies, backtest, fiscal, IA podem ser desenvolvidos 100% em Linux | Não dependem do Profit |
| Postgres+TimescaleDB rodando em Docker nativo | Já temos Docker 29.1 instalado |
| Integração com Profit/NTSL → Windows | Apenas na fase de integração final |

### 7.2 Produção em Windows 11

| Item | Por quê |
|---|---|
| Profit Pro + Automação de Estratégias | Windows-only |
| Backend Python | Roda nativo no Windows (necessário para futura ProfitDLL Fase 5) |
| PostgreSQL 16 + TimescaleDB | Docker Desktop + WSL2 (Windows) — **obrigatório desde Fase 0** |
| Backup | `pg_dump` + `rclone` agendado via Task Scheduler |

### 7.3 Estratégia de portabilidade dev↔prod

- Código 100% cross-platform via `pathlib`, sem hardcode de paths
- `.env.example` documenta variáveis específicas por SO
- CI/CD futuro: GitHub Actions com matriz `[ubuntu-latest, windows-latest]`
- Adapters (Profit) injetados via DI — em Linux usa mock; em Windows usa real

---

## 8. Estrutura de Repositórios

**Decisão:** **monorepo único** no MVP, separar quando justificar.

```
apps/
└── cam-cockpit/                  # backend Python + frontend React no mesmo repo
    ├── backend/
    │   ├── pyproject.toml        # uv + ruff + pytest + import-linter
    │   ├── alembic.ini
    │   ├── migrations/
    │   ├── tests/                # e2e / integração cross-feature
    │   ├── .env.example
    │   └── cam/
    │       ├── _shared/          # SHARED KERNEL (risk, domain, events, audit, infra)
    │       ├── features/         # VERTICAL SLICES (journal, fiscal, ledger, ...)
    │       └── api/              # FastAPI composer
    │
    ├── frontend/
    │   ├── package.json
    │   ├── vite.config.ts
    │   ├── public/
    │   └── src/
    │       ├── features/         # VERTICAL SLICES no frontend também
    │       │   ├── cockpit/      # cada feature em uma pasta
    │       │   ├── journal/
    │       │   ├── risk-console/
    │       │   ├── fiscal/
    │       │   ├── backtest/
    │       │   └── ...
    │       ├── _shared/          # componentes, hooks e tipos transversais
    │       ├── api/              # client da API (tipos derivados de OpenAPI)
    │       └── app/              # router root, providers, layout
    │
    ├── ntsl/                     # estratégias NTSL versionadas
    │   ├── strategies/
    │   ├── risk_mirror/          # regras espelhadas (segunda linha de defesa)
    │   └── README.md
    │
    ├── scripts/
    │   ├── dev.sh / dev.ps1
    │   ├── backup.sh
    │   └── import_profit_csv.py
    ├── docker-compose.yml        # postgres/redis (Fase 3+)
    └── README.md
```

**Simetria intencional:** o **frontend** também segue Vertical Slice (`src/features/{nome}/` espelhando os módulos do backend quando possível). Mesmo motivo: agente trabalha numa pasta. Mesmas regras invioláveis: `features/X/` não importa de `features/Y/`.

Em `/project/cam-cockpit/` ficam os artefatos DevFlow: SCOPE, SPEC, PLAN, DAS, ADRs, PROOF-PACKs.

---

## 9. ADRs (Architecture Decision Records) Embutidos

ADRs formais ficam em `/project/cam-cockpit/architecture/adrs/` quando ARCH (Fase 3 do NCC-1701) for executada formalmente. Resumo das decisões já tomadas:

| ID | Decisão | Princípio | Status |
|---|---|---|---|
| **ADR-001** | Profit como plataforma oficial de execução | 2, 9 | Proposto |
| **ADR-002** | Python 3.12 + FastAPI como backend cockpit | 4, 7, 8 | Proposto |
| **ADR-003** | React 19 + Vite + MUI como frontend (SPA local, sem Next.js) | 7, 8 | Proposto |
| **ADR-004** | **PostgreSQL 16 + TimescaleDB desde Fase 0** (revoga proposta anterior de SQLite no MVP). Justificativa: volume de tick data e análise de padrões em estratégias exigem hypertables, continuous aggregates, compressão e hyperfunctions desde o início. DuckDB complementa em research read-only sobre arquivos | 3, 4, 6, 7 | Proposto |
| **ADR-005** | DuckDB como motor analítico **auxiliar** (research read-only sobre CSV/Parquet/Jupyter), complementando Postgres+Timescale — não substitui | 3, 4, 7 | Proposto |
| **ADR-006** | IA sem autoridade operacional (Arts. 34º–36º) | 1 | Vinculante constitucional |
| **ADR-007** | Risk Engine em Python puro dentro do Shared Kernel (`cam/_shared/risk/`), sem I/O, 100% testado | 1, 4, 5, 6 | Proposto |
| **ADR-008** | Integração Profit por fases (manual → CSV → semi-auto → NTSL → ProfitDLL opcional) | 2, 5, 9 | Proposto |
| **ADR-009** | Risk Engine espelhado em NTSL como segunda linha de defesa | 1, 5, 10 | Proposto |
| **ADR-010** | Telegram bot como canal externo de alerta independente do cockpit | 5, 6 | Proposto |
| **ADR-011** | Monorepo único `apps/cam-cockpit/` no MVP | 7 | Proposto |
| **ADR-012** | Dev em Linux, produção em Windows; código cross-platform via `pathlib` | — | Proposto |
| **ADR-013** | **Feature-Based Vertical Slice Architecture + Shared Kernel mínimo** no backend e frontend, otimizando desenvolvimento agêntico (revoga arquitetura hexagonal proposta na v0). Regra inviolável: `features/X/` não importa `features/Y/`; comunicação cross-feature só via `_shared/` ou eventos | 4, 6, 8 | Proposto |

> Quando o gate ARCH for executado formalmente, cada ADR vira artefato próprio em `/project/cam-cockpit/architecture/adrs/ADR-{NNN}-{slug}.md`.

---

## 10. Custos Recorrentes — Honestidade

Conforme Art. 8º, custos PF, fora do CaM.

| Item | Custo estimado | Obrigatório? |
|---|---|---|
| Profit Pro com book (Nelogica) | R$ 200–300/mês | Sim (Fase 1+) |
| Módulo de Automação de Estratégias | adicional | Sim (Fase 4+) |
| Corretora vinculada | corretagem por trade | Sim |
| Cloud backup (rclone Google Drive) | R$ 0–30/mês | Recomendado |
| Anthropic API | R$ 0–50/mês | Não, sob demanda |
| GitHub privado | R$ 0 (free tier) | Sim |
| Telegram | R$ 0 | Sim |
| Resto da stack (Python, React, Postgres, DuckDB, etc.) | R$ 0 | — |

**Total mensal típico Fase 1–3:** R$ 200–380.

**Honestidade dura (de Voltaire):** isso é **4–8% ao mês sobre R$ 5.000** declarados. O sistema precisa ter **expectância líquida positiva acima desse patamar** para parar de queimar caixa pessoal. **Edge mínimo de sobrevivência** deve aparecer explícito desde o backtest. Backtest sem custos de plataforma está mentindo.

---

## 11. Riscos da Stack — Mitigações

| ID | Risco | Mitigação |
|---|---|---|
| R1 | Profit/NTSL/ProfitDLL muda sem aviso | Travar versão; smoke test antes do pregão; manter changelog próprio |
| R2 | Operador desligar Risk Engine "só por hoje" | Flag `PRODUCTION_ALLOWED` versionada + edição requer cooldown (Art. 38º) |
| R3 | Backtest divergir do live (DRY quebrado) | Contrato `MarketContext` único; testes de paridade backtest↔paper |
| R4 | Acoplamento acidental risk↔infra | `import-linter` configurado; CI bloqueia merge se `risk/` importar de `execution/`/`journal/` |
| R5 | Falha catastrófica do banco com posição aberta | Journal duplo: Postgres + JSONL append-only em disco local; modo degradado bloqueia novas ordens e alerta via Telegram |
| R6 | Vazamento de credenciais | `.env` nunca versionado; pré-commit hook detecta padrões de chave; Windows Credential Manager via `keyring` |
| R7 | Performance Python para tick streaming | Profiling desde o início; hot path em Cython/Rust **se necessário** (improvável em 1 ativo); planejar margem |
| R8 | NTSL espelhada divergir do Risk Engine Python | Testes de paridade NTSL↔Python por cenário canônico; review semanal |

---

## 12. O Que Esta Stack NÃO É

- ❌ Não é produto comercial — CaM é cockpit pessoal (Constituição Art. 1º)
- ❌ Não é multiusuário — sem auth, sem tenant
- ❌ Não é escalável horizontalmente — mono-host por design
- ❌ Não é HFT — latência alvo: dezenas de ms, não microssegundos
- ❌ Não é cross-broker — single venue (B3 via Profit)
- ❌ Não é cloud-first — localidade absoluta (princípio 3)
- ❌ Não usa Java, Spring, Firebase, Next.js, MongoDB — esses **NÃO se aplicam ao CaM**, vieram de inferência baseada no catálogo Teczilabs e foram revogados nesta versão

---

## 13. Próximas Decisões Pendentes (bloqueadores Fase 1)

1. **Versão do Profit** — Pro ou Ultra? Verificar se Ultra é necessário para Fase 1 (paper) ou só Fase 4 (automação real).
2. **Corretora vinculada** — corretagem por mini contrato impacta diretamente o edge mínimo. Decidir antes de Fase 1.
3. **Tese de edge da primeira estratégia** — pendente da conversa estratégica anterior. Sem tese, a Fase 0 constrói infra sem destino. Infra continua válida, mas Setup A+ futuro (Fase 4) depende disso.
4. **Versão da ProfitDLL** (se Fase 5 for considerada) — levantar com Nelogica.
5. **Origem do tick histórico para backfill inicial** — Profit exporta tick? Ou só candles? Define a estratégia de backfill da Timescale na M2 (precisa carregar 1–2 anos de histórico para os primeiros estudos de padrão).
6. **Schedule de revisão da stack** — quando reavaliar versões, modelo IA, etc.

---

## 14. Roadmap Resumido (ver detalhamento em PLAN futuro do NCC-1701)

| Milestone | Conteúdo principal |
|---|---|
| **M0** | Constituição + Stack Oficial (este doc) + Política Operacional |
| **M1** | Infra base: Docker Compose (Postgres 16 + TimescaleDB) + Alembic + Backend FastAPI esqueleto + `_shared/risk/` Pure Python com primeiros validators 100% test |
| **M2** | Schema completo (operacional + Timescale hypertables `cam_market_ticks/book_snapshots` + continuous aggregates `cam_candles_*`) + backfill inicial de tick histórico (Profit → CSV/Parquet → Timescale) |
| **M3** | Frontend cockpit passivo (Dashboard + Journal + Risk Console + Constituição read-only) |
| **M4** | Ledger + Fiscal básicos + Importador CSV Profit + conciliação trade-a-trade |
| **M5** | Risk Engine completo (todos os validators dos Arts. 11º–20º) com property-based testing |
| **M6** | Backtest engine + walk-forward + DuckDB para research exploratório em Jupyter |
| **M7** | Estudos de padrão (features/pattern_studies) usando hyperfunctions Timescale + IA analítica (Ollama local + Anthropic sob demanda) |
| **M8** | Integração operacional Profit (NTSL espelhada + paper trading) |
| **M9** | Kill switch hardening + Telegram bot + critérios de saída Fase 0 (cobertura ≥ 80% global, ≥ 100% Risk Engine, kill switch validado, backtest e paper funcionais) |

Estimativa **bruta** (não-vinculante, sem horas/dias — proibição constitucional): **8–12 ciclos de trabalho** compatíveis com rotina Porto + Monnezy.

---

## 15. Aprovação

Este documento é **proposto**. Vira **vigente** após gate Founder em SPEC formal do projeto `cam-cockpit` no DevFlow NCC-1701 (Fase 4 — Albert + Kevin + Oscar consolidam, Founder aprova).

Até a aprovação formal, este documento é a **referência canônica de stack** para qualquer trabalho técnico no CaM-project, **revogando** o catálogo Teczilabs (Combos A/B/C).

---

> **Frase final:**
>
> O CaM não foi construído para operar mais. O CaM foi construído para impedir operação ruim.
>
> O Profit executa. O Python fiscaliza. O React mostra. O Ledger registra. O Risk Engine manda. A IA comenta. O Carlos obedece ao sistema.

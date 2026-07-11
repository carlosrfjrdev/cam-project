---
template: DAS
phase: ARCH
status: Draft
---

# DAS — CaM Cockpit

> **Documento de Arquitetura de Solução**
> **Data:** 2026-05-24
> **Versão:** 1 · **Status:** Draft — aguarda aprovação do Founder
> **Lead:** Oscar · **Co-lead:** Vint (INFRA-ARCH) · **Cross-cutting:** Kevin (SEC-GOV)
> **Vive em:** `/project/cam-cockpit/DAS.md`

---

## 1. Visão Arquitetural

### Diagrama ASCII do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CaM Cockpit — Visão de Sistema                          │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │              FRONTEND  (React 19 + Vite + MUI — SPA Local)             │  │
│  │   Cockpit | Journal | Risk Console | Backtest | Paper | Fiscal         │  │
│  │   Harvest | Carteira Hard | Constituição (RO) | Configurações          │  │
│  │                    P&L SEMPRE LÍQUIDO — Art. 25º                       │  │
│  │                  KILL SWITCH SEMPRE ACESSÍVEL — Art. 18º               │  │
│  └────────────────────────────────┬───────────────────────────────────────┘  │
│                                   │ HTTP + WebSocket (localhost)             │
│  ┌────────────────────────────────▼───────────────────────────────────────┐  │
│  │              BACKEND  (Python 3.12 + FastAPI + Uvicorn)                 │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  cam/_shared/  (SHARED KERNEL — autoridade transversal)          │   │  │
│  │  │  ┌──────────────┐  ┌──────┐  ┌────────┐  ┌───────┐  ┌──────┐  │   │  │
│  │  │  │  risk/        │  │domain│  │events/ │  │audit/ │  │infra/│  │   │  │
│  │  │  │ (Pure Python) │  │      │  │(asyncio│  │(struct│  │(DB   │  │   │  │
│  │  │  │ Zero I/O      │  │Money │  │.Queue) │  │ log)  │  │sess.)│  │   │  │
│  │  │  │ 100% tested   │  │Phase │  │        │  │       │  │      │  │   │  │
│  │  │  └──────────────┘  └──────┘  └────────┘  └───────┘  └──────┘  │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  cam/features/  (VERTICAL SLICES — auto-contidos)                │   │  │
│  │  │  journal | fiscal | ledger | harvest | strategies | backtest     │   │  │
│  │  │  paper_trading | profit_integration | market_data | kill_switch  │   │  │
│  │  │  checklists | notifications | ai_analyst | constitution          │   │  │
│  │  │  REGRA: features/X/ NUNCA importa features/Y/                   │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  cam/api/  (FastAPI Composer — monta o app, conhece todas feats)│   │  │
│  │  │  main.py | lifespan.py | middleware.py | websocket.py           │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  └─────────┬──────────────────────────────────┬────────────────────────────┘  │
│            │                                  │                               │
│  ┌─────────▼──────────────────┐   ┌───────────▼──────────────────────────┐  │
│  │  LOCAL STORAGE              │   │  PROFIT / NELOGICA (externo gerido)  │  │
│  │  PostgreSQL 16 + TimescaleDB│   │  NTSL + Automação de Estratégias     │  │
│  │  (hypertables + cont.agg.)  │   │  Importação CSV / Excel              │  │
│  │  DuckDB (research/arquivos) │   │  ProfitDLL (ctypes) — Fase F4+ only  │  │
│  │  JSONL append-only (backup) │   └──────────────────────────────────────┘  │
│  └────────────────────────────┘                                               │
│                    │                                                          │
│  ┌─────────────────▼────────────────────────────────────────────────────┐   │
│  │  CANAIS EXTERNOS (independentes do cockpit)                           │   │
│  │  Telegram Bot — alertas: kill switch, loss limit, DARF, IA análise   │   │
│  │  Ollama local — IA auditora (dados sensíveis)                         │   │
│  │  Anthropic API — IA auditora (dados anonimizados, sob demanda)       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Descrição da Arquitetura

O CaM Cockpit segue uma arquitetura **Feature-Based Vertical Slice com Shared Kernel mínimo** (ADR-013). O backend Python é a peça central que governa todas as regras constitucionais. O frontend React é uma SPA local sem lógica de negócio — apenas exibe o estado e aciona endpoints do backend. O Profit/Nelogica é a plataforma de execução — o CaM governa o Profit, não substitui.

A hierarquia constitucional `Constituição > Risk Engine > Estratégia validada > IA > Operador` é implementada estruturalmente: o Risk Engine vive no Shared Kernel (`cam/_shared/risk/`), é Pure Python sem I/O, e toda feature que toque execução obrigatoriamente o consulta. Nenhuma feature pode duplicar regra constitucional.

---

## 2. Camadas

| Camada | Responsabilidade | Tecnologia | ADR |
|---|---|---|---|
| **Fonte de market data** | Candles, tick e book read-only do MT5 | EA `cam_bridge` (MQL5) + ZeroMQ 127.0.0.1 | **ADR-014** |
| **Plataforma de execução** | Envio de ordens ao mercado (B3) — *broker sob reavaliação (OP-014/OP-015)* | Profit Pro/Ultra + NTSL | ADR-016 |
| **Backend — Shared Kernel** | Risk Engine (autoridade), domain primitives, event bus, audit log, DB sessions | Python 3.12 (Pure Python no risk/) | ADR-007, ADR-013 |
| **Backend — Features** | Módulos de negócio auto-contidos (journal, fiscal, ledger, backtest, etc.) | Python 3.12 + FastAPI routers | ADR-013 |
| **Backend — API Composer** | Montar app FastAPI, registrar routers, lifespan, middlewares, WebSocket broker | FastAPI + Uvicorn | ADR-002 |
| **Frontend** | Interface operacional local — somente exibe estado, aciona backend | React 19 + Vite + MUI + TypeScript | ADR-003 |
| **Banco transacional** | Operações, posições, journal, decisões Risk Engine, fiscal, checklists | PostgreSQL 16 | ADR-004 |
| **Banco de séries temporais** | Tick data, book snapshots, candles em múltiplos timeframes | TimescaleDB (extensão Postgres) | ADR-004 |
| **Motor analítico auxiliar** | Research em CSV/Parquet, backtest exploratório, notebooks Jupyter | DuckDB | ADR-005 |
| **Research Lane** | Descoberta estatística read-only (Lead-Lag): ingestão MT5→`research_*`, barras canônicas M1→derivadas, análise; **isolada do live por barreira técnica** | Vertical slice `features/research/` + schema `research_*` + TimescaleDB | ADR-015 |
| **Canal externo de alertas** | Notificações operacionais independentes do cockpit | Telegram Bot | ADR-010 |
| **IA auditora** | Análise pós-mercado, hipóteses, revisão de journal — SEM autoridade de execução | Ollama local + Anthropic API | ADR-006 |
| **Integração Profit** | Faseada: CSV → semi-auto → NTSL → ProfitDLL (Fase F4+) | NTSL + ctypes (futuro) | ADR-016, ADR-008 |
| **Estratégias NTSL (2ª defesa)** | Regras de risco espelhadas no Profit como linha adicional de proteção | NTSL (Nelogica Trading System Language) | ADR-009 |

---

## 3. Decisões Arquiteturais Ativas

| ADR | Decisão | Link |
|---|---|---|
| ADR-016 | Plataforma de execução: MT5 em avaliação · Profit em standby | [ADR-016](./adrs/ADR-016-plataforma-execucao.md) |
| ADR-002 | Python 3.12 + FastAPI como backend cockpit | [ADR-002](./adrs/ADR-002-python-fastapi-backend.md) |
| ADR-003 | React 19 + Vite + MUI — SPA local, sem Next.js | [ADR-003](./adrs/ADR-003-react-vite-mui-frontend.md) |
| ADR-004 | PostgreSQL 16 + TimescaleDB desde Fase 0 (revoga SQLite) | [ADR-004](./adrs/ADR-004-postgresql-timescaledb.md) |
| ADR-005 | DuckDB como motor analítico auxiliar read-only | [ADR-005](./adrs/ADR-005-duckdb-analitico-auxiliar.md) |
| ADR-006 | IA sem autoridade operacional (vinculante constitucional) | [ADR-006](./adrs/ADR-006-ia-sem-autoridade-operacional.md) |
| ADR-007 | Risk Engine Pure Python no Shared Kernel | [ADR-007](./adrs/ADR-007-risk-engine-pure-python-shared-kernel.md) |
| ADR-008 | Integração Profit faseada (F1→F5) | [ADR-008](./adrs/ADR-008-integracao-profit-faseada.md) |
| ADR-009 | Risk Engine espelhado em NTSL como 2ª linha de defesa | [ADR-009](./adrs/ADR-009-risk-ntsl-segunda-linha-defesa.md) |
| ADR-010 | Telegram como canal externo de alerta independente | [ADR-010](./adrs/ADR-010-telegram-canal-alerta.md) |
| ADR-011 | Monorepo único `apps/cam-cockpit/` no MVP | [ADR-011](./adrs/ADR-011-monorepo-cam-cockpit.md) |
| ADR-012 | Dev em Linux, produção em Windows; code cross-platform | [ADR-012](./adrs/ADR-012-dev-linux-producao-windows.md) |
| ADR-013 | Feature-Based Vertical Slice + Shared Kernel mínimo | [ADR-013](./adrs/ADR-013-vertical-slice-shared-kernel.md) |
| ADR-014 | MT5 como fonte de **market data read-only** (EA `cam_bridge` + ZeroMQ) | [ADR-014](./adrs/ADR-014-mt5-market-data-read-only.md) |
| ADR-015 | **Research Lane isolada** com schema `research_*` próprio (Lead-Lag) | [ADR-015](./adrs/ADR-015-research-lane-isolada.md) |

> **Nota de recalibração (2026-05-31, ADR-014):** o SO firme é **Windows 11** (Wine/Linux falhou,
> 2026-05-30) e a **fonte de market data é o MT5** via EA `cam_bridge`+ZeroMQ (read-only). ADR-014
> corrige a linha de dados deste DAS. ADR-016/008/012 (Profit / dev-Linux) seguem **vigentes mas
> sob reavaliação** (broker de *execução* pende de OP-014/OP-015) — não revogados aqui. Estado real
> (`/apps`) vence intenção (NCC-1701 §2).

---

## 4. Fluxos Principais

### 4.1 Fluxo de Validação de Operação (Risk Engine)

```
Operador indica intenção de operar
    → Risk Engine recebe OrderCandidate + RiskContext
    → Executa validators sequencialmente:
        [kill_switch_active_check]
        [pre_market_checklist_check]
        [tax_compliance_check]       ← DARF atrasada bloqueia aqui
        [phase_authorization_check]
        [max_contracts_check]        ← Art. 11º — intocável
        [phase_contracts_check]      ← Art. 12º — por fase
        [simultaneous_position_check]
        [daily_loss_limit_check]     ← Art. 16º — 3%
        [weekly_loss_limit_check]    ← Art. 16º — 7%
        [monthly_loss_limit_check]   ← Art. 16º — 15% (congela fase)
        [gain_lock_check]            ← Art. 17º — 2% encerra dia
        [daily_operations_count_check]
        [martingale_check]           ← Art. 13º — proíbe após loss
        [trading_window_check]       ← POV — janelas vedadas
        [setup_a_plus_check]         ← Fase 4 apenas
    → RiskDecision: Approved | Rejected(reason)
    → Decisão registrada em cam_risk_decisions (imutável)
    → Se Rejected: frontend exibe motivo, operação bloqueada
    → Se Approved: operador pode prosseguir no Profit
```

### 4.2 Fluxo de Registro de Operação (Journal)

```
Operação completada no Profit
    [F1] → Carlos registra manualmente no frontend
    [F2] → Carlos importa CSV Profit → sistema concilia e preenche
    [F4] → Callback NTSL dispara evento → journal registra automaticamente
    → journal/service.py valida campos obrigatórios (Art. 31º)
    → Calcula resultado líquido (bruto - custos - imposto provisionado)
    → Persiste em cam_journal_entries
    → Publica evento JournalEntryCreated em _shared/events/
    → fiscal/ consome evento → atualiza provisão e apuração mensal
    → harvest/ consome evento → recalcula bucket snapshot
    → notifications/ consome evento → alerta Telegram se configurado
```

### 4.3 Fluxo de Apuração Fiscal e Harvest

```
Fim do mês (job scheduler — APScheduler)
    → fiscal/service.py apura resultado líquido do mês
    → Calcula IR Day Trade (20% sobre lucro; IRRF 1% como antecipação)
    → Gera registro em cam_fiscal_apuration
    → Gera DARF pendente em cam_darf_history (status: PENDING)
    → Notifica Telegram: "DARF do mês disponível para pagamento"
    
Founder marca DARF como paga
    → cam_darf_history atualizado (status: PAID)
    → harvest/service.py calcula distribuição:
        - 60% lucro líquido → Carteira Hard
        - 40% → Buffer Operacional (até linha de base R$ 1.000)
        - Se Bucket Derivativo ≥ R$ 4.500 → sangria automática
    → Registra movimentações em ledger
    → Notifica Telegram: "Harvest executado — valores movimentados"
```

### 4.4 Fluxo do Kill Switch

```
Evento de kill switch (qualquer origem):
    - Limite de perda atingido (Risk Engine detecta)
    - Operador pressiona o botão no frontend (confirmação dupla)
    - Telegram recebe comando /killswitch
    - Falha técnica detectada
    → kill_switch/service.py ativa estado ACTIVE
    → Risk Engine: kill_switch_active_check → REJECTED em toda tentativa de operação
    → Persiste em cam_kill_switch_events com timestamp e motivo
    → Notifica Telegram imediatamente
    → Frontend exibe estado de emergência em toda tela
    
Desativação do kill switch:
    → Somente pelo Founder no frontend (ação manual explícita)
    → Registra desativação em cam_kill_switch_events
```

### 4.5 Fluxo de Alerta Telegram

```
Evento crítico publicado em _shared/events/
    → notifications/service.py subscribed nos eventos relevantes:
        - KillSwitchActivated
        - DailyLossLimitReached
        - WeeklyLossLimitReached
        - MonthlyLossLimitReached
        - GainLockReached
        - DarfOverdue
        - DarfDueSoon (aviso antecipado)
        - TradeCompleted
        - TechnicalFailureWithOpenPosition  ← Art. 19º
        - AIAnalysisReady (pós-mercado)
    → python-telegram-bot envia mensagem formatada
    → Log em structlog (audit trail)
```

### 4.6 Fluxo de Backtest

```
Founder configura parâmetros de backtest (frontend → backend)
    → backtest/service.py carrega tick histórico de cam_market_ticks
    → Instancia o MESMO Risk Engine (_shared/risk/) com parâmetros da fase simulada
    → Executa estratégia tick a tick (DRY: mesma lógica de sinal do live)
    → Cada operação simulada passa pelo Risk Engine → Approved/Rejected
    → Registra resultado em cam_backtest_trades + cam_backtest_equity_curve
    → Calcula métricas: P&L, Sharpe, max drawdown, win rate, fator de lucro
    → Inclui custos de corretagem + imposto (honestidade constitucional)
    → Frontend exibe relatório + equity curve
    
Para research exploratório:
    → DuckDB sobre CSV/Parquet exportados do Profit ou de fonte externa
    → Nunca grava em tabelas vistas pelo cockpit live
```

### 4.7 Fluxo de Análise IA Pós-Mercado

```
Scheduler dispara job pós-fechamento do pregão
    → ai_analyst/service.py lê:
        - cam_journal_entries do dia (read-only)
        - cam_risk_decisions do dia (read-only)
        - cam_violations do dia (read-only)
    → Monta prompt com dados operacionais (sem credenciais, sem dados sensíveis)
    → Chama Ollama local (default) ou Anthropic API (sob demanda, dados anonimizados)
    → Analisa: aderência, padrões de loss, anomalias, sugestões de hipótese
    → NUNCA recomenda entrada/saída de posição (Art. 35º)
    → NUNCA acessa endpoints de Risk Engine parametrização
    → Envia análise via Telegram + salva em banco
```

---

## 5. Contratos Externos

| Integração | Direção | Protocolo | Fase |
|---|---|---|---|
| Profit Pro/Ultra | Entrada (dados de mercado, confirmação de ordens) | CSV export / NTSL callbacks / ProfitDLL (F4+) | F1-F4 |
| TimescaleDB | Entrada (tick histórico para backfill) | SQL (psycopg3 + SQLAlchemy 2.0) | F2+ |
| Telegram Bot API | Saída (alertas) | HTTPS REST (python-telegram-bot) | F1+ |
| Ollama local | Saída/Entrada (análise IA) | HTTP REST (localhost) | M7+ |
| Anthropic API | Saída/Entrada (análise IA avançada) | HTTPS REST (Claude API) | M7+ sob demanda |
| Google Drive / S3 | Saída (backup) | rclone sync | F1+ |

**Frontend ↔ Backend:**

| Tipo | Tecnologia | Uso |
|---|---|---|
| REST | HTTP/JSON (FastAPI) | CRUD, consultas, ações |
| WebSocket | FastAPI WebSocket nativo | P&L live, status Risk Engine, alertas em tempo real |

---

## 6. Modelo de Dados (Alto Nível)

### Domínio Operacional (tabelas regulares PostgreSQL)

```
cam_orders              ← ordens propostas e executadas
cam_positions           ← posições abertas/fechadas
cam_trades              ← execuções (fills) vindas do Profit
cam_journal_entries     ← Art. 31º — registro imutável de operações
cam_risk_decisions      ← TODA decisão do Risk Engine (audit trail)
cam_violations          ← violações para cálculo de aderência (Art. 29º)
cam_kill_switch_events  ← Art. 18º — ativações/desativações
cam_checklist_pre_market   ← Art. 32º
cam_checklist_post_market  ← Art. 33º
```

### Domínio Constitucional / Governança

```
cam_constitution_versions  ← Art. 38º — emendas constitucionais
cam_pov_versions           ← Art. 37º — versões da POV
cam_phase_history          ← transições de fase do CaM (Fase 0 → Fase 1 → ...)
```

### Domínio Fiscal / Patrimonial

```
cam_fiscal_apuration         ← apuração mensal de IR
cam_darf_history             ← DARFs gerados/pagos
cam_loss_compensation_ledger ← Art. 27º — prejuízos compensáveis
cam_bucket_transactions      ← movimentações dos três buckets (Derivativo, Buffer, Carteira Hard)
cam_harvest_history          ← execuções da Harvest Rule (Art. 21º)
```

### Market Data (TimescaleDB hypertables)

```
cam_market_ticks           ← hypertable, chunk 1 dia, compressão >7 dias
cam_market_book_snapshots  ← hypertable, chunk 1 dia, compressão >3 dias

Continuous aggregates:
cam_candles_1s  | cam_candles_5s | cam_candles_1m | cam_candles_5m
cam_candles_15m | cam_candles_1h | cam_candles_1d
```

### Backtest / Research

```
cam_backtest_runs        ← metadata da execução
cam_backtest_trades      ← trades simulados
cam_backtest_equity_curve  ← curva de capital (hypertable se grande)
cam_pattern_studies      ← estudos de padrão
```

### Research Lane (schema `research_*` — ISOLADO do live, ADR-015)

```
research_bars                  ← canônico de barras (M1 + M5/M15/M30/H1 derivados); timeframe é coluna/partição
research_data_sources          ← provenance por lote (bar_origin, ts_source, hash do lote bruto)
research_dataset_snapshots     ← snapshot imutável + hash composto (reprodutibilidade)
research_runs                  ← runs de análise (snapshot_id, grade δ, n_trials, status)
research_run_results           ← resultado por célula (source, target, delta, correlation, n, verdict)
research_data_quality_checks   ← missing_bars, bucket_misalignment, partial_bar, m1_is_primary, stale_bar
```

> **Isolamento (ADR-015 / SEC-GOV):** o slice `features/research/` NÃO importa execução
> (Order Gateway, bridge de execução, `OrderSend`) — enforce por import-linter; e NÃO escreve
> em tabelas live (`cam_orders`, `cam_positions`, `cam_journal_entries`). Escrita restrita a
> `research_*`. Fonte de dado = MT5 via bridge read-only (ADR-014). `cam_candles_*` (live) **não**
> são canônico de research — falta provenance/snapshot/hash.

### Relacionamentos Principais

```
cam_journal_entries → cam_trades (1:1 ou 1:N conciliação)
cam_journal_entries → cam_fiscal_apuration (N:1 por mês)
cam_risk_decisions  → cam_orders (1:1 — toda ordem tem decisão)
cam_violations      → cam_journal_entries (N:1 — viola qual entrada)
cam_bucket_transactions → cam_harvest_history (N:1)
cam_market_ticks    → cam_candles_* (1:N via continuous aggregate)
```

---

## 7. Segurança (Overview)

### Superfícies Sensíveis (gatilhos SEC-GOV — Art. 35º + Kevin)

| Superfície | Risco | Controle |
|---|---|---|
| Risk Engine parametrização | IA ou código externo alterar limites constitucionais | `cam/_shared/risk/` sem endpoint de alteração em runtime; parâmetros só via POV com cooldown (Art. 39º) |
| Credenciais Profit/Telegram/Anthropic | Vazamento de API keys | `.env` nunca commitado; pré-commit hook detecta padrões; Windows Credential Manager via `keyring` |
| Journal com dados operacionais sensíveis | Exposição de P&L, estratégia e posições | Cockpit é local (localhost); sem autenticação necessária para uso interno; sem cloud exposure |
| IA com acesso a dados operacionais | Violação Arts. 34º–36º | IA tem acesso read-only; sem endpoint de escrita via IA; dados anonimizados ao usar Anthropic API externa |
| Kill switch via Telegram | Command injection ou acionamento indevido | Token de bot privado; validação de chat_id do operador; confirmação dupla para desativação |
| NTSL espelhada no Profit | Divergência com Risk Engine Python = segunda linha de defesa falha | Testes de paridade NTSL↔Python por cenário canônico; review semanal |

### Princípio de Falha Segura

Qualquer falha técnica degrada para **"não opera"**, nunca para **"executa fora de regra"**:
- Backend indisponível → frontend não exibe "operação liberada" → operador não opera
- Banco indisponível → Risk Engine sem RiskContext → decisão REJECTED (precaução)
- Telegram indisponível → alertas enfileirados; operação não é desbloqueada pela falha do alerta

### Restrição IA (Arts. 34º–36º — Não-Negociável)

- IA acessa apenas endpoints read-only do backend
- Nenhum endpoint de execução, parametrização do Risk Engine ou alteração de estado aceita chamada originada por componentes de IA
- IA auditora roda em processo separado do backend live (CLI de research ou job scheduler)

---

## 8. Infraestrutura Local (Overview)

### Desenvolvimento (Linux)

```yaml
# docker-compose.yml (desenvolvimento)
services:
  db:
    image: timescale/timescaledb:latest-pg16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: cam_dev
      POSTGRES_USER: cam
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - cam_pgdata:/var/lib/postgresql/data
  
  redis:  # opcional — apenas se event bus externo for necessário
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### Produção (Windows 11 + Docker Desktop + WSL2)

- Docker Desktop com WSL2 habilitado
- Mesmo `docker-compose.yml` (portabilidade total)
- Backend Python: executa nativo no Windows (necessário para futura ProfitDLL Fase F4+)
- Frontend: servido pelo FastAPI em `http://localhost:8000/cockpit/`
- Backup: `pg_dump` via Task Scheduler + `rclone` sync Google Drive

### Estrutura Monorepo

```
apps/cam-cockpit/
├── backend/
│   ├── pyproject.toml        (uv + ruff + pytest + import-linter)
│   ├── alembic.ini
│   ├── migrations/
│   ├── .env.example
│   └── cam/
│       ├── _shared/          (risk, domain, events, audit, infra, config)
│       ├── features/         (journal, fiscal, ledger, harvest, ...)
│       └── api/              (FastAPI composer)
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── features/         (cockpit, journal, risk-console, fiscal, ...)
│       ├── _shared/          (componentes, hooks, tipos transversais)
│       ├── api/              (client gerado de OpenAPI)
│       └── app/              (router, providers, layout)
├── ntsl/
│   ├── strategies/
│   └── risk_mirror/          (regras constitucionais espelhadas)
├── scripts/
│   ├── dev.sh / dev.ps1
│   ├── backup.sh
│   └── import_profit_csv.py
└── docker-compose.yml
```

---

## 9. Não-Decisões (Deliberadas)

| Item | Status | Motivo |
|---|---|---|
| ProfitDLL via ctypes | `later` — Fase F4+ | Somente se necessidade real comprovar após F3 |
| ~~MT5 como fallback `out-of-scope`~~ | **REVOGADO por ADR-014 (2026-05-31)** | MT5 é agora a **fonte oficial de market data read-only** (EA `cam_bridge`+ZeroMQ). A decisão de broker de **execução** segue aberta (OP-014/OP-015). |
| Redis como event bus externo | `pending` — só se asyncio.Queue mostrar limitação | Depende de carga real (1 operador, não é sistêmico) |
| CI/CD automatizado | `later` — GitHub Actions na Fase 1+ | Dev local manual é suficiente para Fase 0 |
| Autenticação de usuário | `out-of-scope` | Cockpit local, mono-usuário; autenticação adicionaria fricção sem benefício |
| Setup A+ (2 contratos Fase 4) | `later` — pós-Fase 3 | Definição técnica exige histórico de Fase 3 (Art. 11º + Anexo II) |
| Taxonomia completa de OPS-EVENT | `later` | Aguarda primeiro produto em versão final + primeiro incidente real |

---

## 10. Referências

- SCOPE: [`SCOPE.md`](./SCOPE.md)
- DVP: [`DVP.md`](./DVP.md)
- SPEC: [`SPEC.md`](./SPEC.md)
- ADRs: [`adrs/`](./adrs/)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md)
- Constituição: [`/CONSTITUICAO.md`](/CONSTITUICAO.md)

---

## 11. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-05-24 | Criação — produzido via NCC-1701 ARCH | — (aguarda Founder) |
| 1.1 | 2026-05-31 | ADR-014: MT5 como market data read-only (§2, §3, §9 corrigidos) | Carlos (Founder) |

---

> **Gate de aprovação ARCH:** Founder valida DAS e ADRs antes de avançar para SPEC.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

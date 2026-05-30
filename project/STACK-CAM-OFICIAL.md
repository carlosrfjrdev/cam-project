# STACK-CAM-OFICIAL

> 🪟 **ATUALIZAÇÃO 2026-05-30.** Dois níveis de decisão, com maturidade diferente:
> - ✅ **SO = WINDOWS 11 (FIRME).** O MT5 sob **Wine no Linux falhou** → operação em
>   Windows nativo. Isto encerra a parte "Linux/Wine" da Opção B.
> - 🔄 **BROKER = EM AVALIAÇÃO (não decidido).** **MetaTrader 5 em teste** agora
>   (Founder já criou alguns pontos/setups). **Profit/Nelogica NÃO caiu — está em
>   STANDBY**, mantido como opção. **A escolha de broker só fecha após o 1º teste do MT5.**
>
> Estamos em **soft-stage de concepção** (pré-v1): docs moldáveis, **sem ADR HARD**.
> Runbook operacional: [`runbooks/RUNBOOK-WINDOWS.md`](./runbooks/RUNBOOK-WINDOWS.md).
> **O que NÃO muda em nenhum cenário:** Constituição, NCC-1701, backend Python/FastAPI,
> frontend React/MUI, Postgres+Timescale, Risk Engine, política da IA. As seções
> abaixo que descrevem **Wine/Linux** ficam **supersedidas** (preservadas como
> histórico). As que descrevem **Profit** valem enquanto ele estiver em standby.

> **Projeto:** CaM — The Carlos Alternative Money
> **Documento:** Stack Oficial — **Windows 11** · broker em avaliação (**MT5 em teste / Profit em standby**)
> **Versão:** 1.1
> **Data:** 2026-05-24 (origem) · 2026-05-25 (canonicalizada) · 2026-05-30 (SO→Windows; broker em reavaliação)
> **Status:** **CANÔNICA (soft-stage)** — adendo em [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md) §10
> **Vinculação constitucional:** [`../CONSTITUICAO.md`](../CONSTITUICAO.md)
> **Síntese por:** Voltaire (devil's advocate) + Grace (arquitetura) + Vint (viabilidade infra)

---

## 0. Status canônico

Carlos escolheu **Linux + MetaTrader 5** em 2026-05-25. Em **2026-05-30**, após o
MT5 sob Wine no Linux **não funcionar**, fixou o **SO em Windows 11 nativo** (firme).
O **broker ficou em reavaliação**: **MT5 em teste** agora; **Profit em STANDBY**
(não descartado). **A decisão de broker fecha após o 1º teste do MT5.** Tudo em
**soft-stage** (pré-v1, moldável, sem ADR HARD).

**SO produção/desenvolvimento:** **Windows 11** (firme). **Broker:** **em avaliação**
— MetaTrader 5 em teste (nativo, sem Wine; MQL5 EAs + bridge ZeroMQ em `127.0.0.1`)
**/** Profit em standby (NTSL + CSV/ProfitDLL, se reativado). **Decisão após 1º teste.**

**O que NÃO muda em relação ao documento Windows+Profit:**

- A Constituição é a mesma (lei suprema, inviolável)
- O framework NCC-1701 é o mesmo
- O backend Python 3.12 + FastAPI é o mesmo
- O frontend React 19 + Vite + MUI é o mesmo
- O banco PostgreSQL 16 + TimescaleDB desde Fase 0 é o mesmo
- DuckDB, Telegram, Ollama, Anthropic — iguais
- A arquitetura Vertical Slice + Shared Kernel (ADR-013) é a mesma
- O Risk Engine Pure Python em `_shared/risk/` é o mesmo
- A política da IA (Arts. 34–36) é a mesma

**O que MUDA** (camada MT5 — o caminho **sob teste**; Profit em standby não aparece na tabela):

| Camada | Linux+MT5/Wine (revogado 2026-05-30) | **Windows+MT5 nativo (em teste)** |
|---|---|---|
| SO produção/dev | Linux (Ubuntu 24.04+ LTS) | **Windows 11** |
| Broker/plataforma | MetaTrader 5 (MetaQuotes) | **MetaTrader 5 (MetaQuotes)** — sem mudança |
| Linguagem estratégia no broker | MQL5 | **MQL5** — sem mudança |
| Artefatos de execução versionados | `mql5/` (EAs + risk_mirror) | **`mql5/`** — sem mudança |
| Onde o MT5 roda | Wine / container Wine / VPS Windows | **Windows nativo** (Wine eliminado — falhou) |
| API Python p/ broker | bridge ZeroMQ (package nativo não roda em Linux) | **bridge ZeroMQ** (e `MetaTrader5` package nativo vira opção futura) |
| Docker | Docker Engine nativo (sem Desktop) | **Docker Desktop + WSL2** (ou Postgres nativo) |
| Custo de licença | R$ 0 (Ubuntu) | Windows 11 (já licenciado pelo Founder) |

---

## 1. Resumo Executivo

```text
MetaTrader 5 (MT5)        →  Plataforma de execução (MQL5 + Expert Advisors)
Wine (oficial) ou VPS      →  Como o MT5 roda em Linux (3 opções — ver §6.1)
Python 3.12 + FastAPI      →  Cockpit local (Risk Engine, Ledger, Journal, IA)
Bridge MT5 ↔ Python        →  Socket TCP / ZeroMQ / arquivo compartilhado (ver §6.1)
React 19 + Vite + MUI      →  Frontend local (SPA servida pelo backend FastAPI)
PostgreSQL 16 + TimescaleDB → Banco transacional + tick/candle storage (desde Fase 0)
DuckDB                     →  Motor analítico auxiliar (research em CSV/Parquet)
Telegram Bot               →  Canal externo de alerta
Ollama local + Anthropic   →  IA auditora/analista, NUNCA executora
Git + GitHub privado       →  Versionamento e governança
SO produção: Ubuntu 24.04+ LTS (ou Fedora/Arch)
SO desenvolvimento: o mesmo Linux (sem dual SO)
```

**Frase de arquitetura:**

> O MT5 executa. O Wine hospeda o MT5. O Python governa. O React mostra. O Ledger registra. O Risk Engine manda. A IA comenta. O Carlos obedece ao sistema.

---

## 2. Princípios da Stack

Mesmos 10 princípios do documento Windows+Profit, **acrescidos de 2 específicos** desta variante:

11. **Sem dependência de Windows** — toda a operação roda em Linux. Wine é detalhe de execução, não princípio.
12. **Tudo containerizável** — Postgres+Timescale, MT5 (via Wine image), backend e frontend rodam em Docker. Migração de host = `docker compose up`. Sem instalação procedural.

---

## 3. Restrições

| Item | Valor | Origem |
|---|---|---|
| SO de produção | Ubuntu 24.04+ LTS (ou distro equivalente) | Princípio 11 |
| SO de desenvolvimento | Mesmo Linux (atual: Ubuntu 26.04 LTS) | Princípio 11 — sem dual SO |
| Plataforma broker | MetaTrader 5 (MetaQuotes) | Decisão desta variante |
| API broker | `MetaTrader5` package (Windows-only) **OU** bridge customizada (ver §6.1) | Limitação técnica do MT5 em Linux |
| Capital declarado | R$ 5.000,00 | Constituição Art. 7º |
| Modelo de uso | Mono-usuário, local | Constituição Art. 1º |
| Custos da stack | PF, fora do perímetro CaM | Constituição Art. 8º |
| Operação simultânea WIN+WDO | Vetada na fase inicial | Constituição Art. 12º |
| Brokers viáveis no Brasil para MT5 + WIN/WDO | XP, Clear, Genial, Modal, Avenue, Toro (verificar antes da Fase 1) | Decisão pendente §14 |

---

## 4. Diagrama de Arquitetura

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
│  _shared/{risk*, domain, events, audit, infra}                       │
│  features/{journal, fiscal, ledger, strategies, backtest, ...}       │
│  features/mt5_integration/  ← bridge Python ↔ MT5                    │
│  (* risk = Pure Python sem I/O, 100% test)                           │
└────────┬───────────────────────────────────┬────────────────────────┘
         │                                   │
         ▼                                   ▼
┌────────────────────────────────┐  ┌──────────────────────────────────┐
│      Local Storage              │  │     MetaTrader 5 (MetaQuotes)     │
│  PostgreSQL 16 + TimescaleDB    │  │  MQL5 + Expert Advisors (EAs)     │
│  (hypertables + continuous      │  │  Indicators + Scripts             │
│   aggregates desde Fase 0)      │  │                                    │
│  DuckDB (research em arquivos)  │  │  Roda em: Wine | container Wine   │
│  JSONL append-only (fallback)   │  │           | VPS Windows remoto    │
└────────────────────────────────┘  └────────────┬─────────────────────┘
                               │                  │
                               │       ┌──────────┴──────────┐
                               │       ▼ Bridge ↕            ▼
                               │  ┌─────────────────────────────────┐
                               │  │  Socket TCP / ZeroMQ / Files    │
                               │  │  (EA MQL5 expõe eventos +       │
                               │  │   recebe comandos do Python)    │
                               │  └─────────────────────────────────┘
                               ▼
                ┌──────────────────────────────┐
                │     Telegram Bot (alertas)    │
                └──────────────────────────────┘
```

---

## 5. Componentes — Tabela Canônica

Diferenças em relação ao documento Windows+Profit destacadas em **negrito**.

| Camada | Tecnologia | Versão alvo | Princípio |
|---|---|---|---|
| **Execução de ordens** | **MetaTrader 5 (MetaQuotes) + EAs MQL5** | atual | 2, 9 |
| **Linguagem estratégia no broker** | **MQL5** | atual | 2, 9 |
| **Hospedagem do MT5** | **Wine 9+** (oficial MetaQuotes) **ou** VPS Windows | latest | 11, 12 |
| **Bridge Python ↔ MT5** | **socket TCP custom / ZeroMQ / arquivo compartilhado** (ver §6.1) | latest | 4, 5 |
| Linguagem backend cockpit | Python | 3.12.x | 4, 7, 8 |
| Framework web/API | FastAPI | 0.115+ | 4, 5, 7 |
| ASGI server | Uvicorn | 0.32+ | padrão FastAPI |
| Validação de schema | Pydantic v2 | 2.x | 6 |
| ORM | SQLAlchemy 2.0 | 2.0.x | 4, 6 |
| Migrations | Alembic | 1.13+ | 6 |
| Banco transacional + time series | PostgreSQL 16 + TimescaleDB (extensão) | 16 / 2.x | desde Fase 0 |
| Motor analítico auxiliar | DuckDB | 1.x | research em arquivos |
| Cache/Event bus (opcional) | Redis | 7.x | apenas se necessário |
| Frontend framework | React + Vite | 19.x / 6.x | 7, 8 |
| Linguagem frontend | TypeScript | 5.x | 6, 8 |
| UI Library | MUI (Material UI) | 6+ ou 7 | 8 |
| Estado UI | Zustand | 5.x | simplicidade |
| Estado server | TanStack Query | 5.x | sincronização HTTP |
| Roteamento | React Router | 6.x | padrão |
| Gráficos candles | TradingView Lightweight Charts | 4.x | open source |
| Gráficos métricas | Recharts | 2.x | alinhamento Teczilabs |
| Validação cliente | Zod | 3.x | 6 |
| Streaming | WebSocket nativo FastAPI | — | 4, 5 |
| Notificações externas | aiogram (Telegram async) | 3+ | 5, 6 |
| Logs estruturados | structlog | 24+ | 6 |
| Backtest engine | Custom Python (DRY com live) + vectorbt (research) | 0.27+ | 4 |
| Testes | pytest + pytest-asyncio + hypothesis | atuais | 1, 6 |
| Lint/format Python | ruff | latest | 7 |
| Type check Python | mypy ou pyright | latest | 6 |
| Gerência de deps Python | uv | latest | 7 |
| Gerência de deps frontend | pnpm | 9.x | 7 |
| **Containers** | **Docker Engine + docker-compose (nativo Linux, sem Desktop)** | 24+ / 2.x | 11, 12 |
| Versionamento | Git + GitHub privado | — | 6, 7 |
| Scheduler interno | APScheduler ou systemd timers | latest | rotinas pós-mercado |
| IA local (opcional) | Ollama | latest | 1, 7 |
| IA externa (sob demanda) | Anthropic API (Claude) | atual | 1 |
| Backup automatizado | rclone para Google Drive / S3 + cron systemd | latest | 3, 6 |

---

## 6. Detalhamento por Camada Crítica

### 6.1 Camada de Execução — MetaTrader 5 + MQL5 em Linux

> ⚠️ **SUPERSEDIDO em 2026-05-30.** Esta seção (Wine local / container Wine / VPS
> Windows / bridges em Linux) descreve a tentativa Linux que **falhou**. Vale como
> histórico do raciocínio. **O setup vigente é Windows 11 nativo** — ver
> [`runbooks/RUNBOOK-WINDOWS.md`](./runbooks/RUNBOOK-WINDOWS.md). A bridge ZeroMQ e os
> EAs (`cam_bridge.mq5`, `cam_risk_mirror.mq5`) permanecem; só sai a camada Wine.

**Decisão fundadora desta variante:** MT5 é o executor. CaM não envia ordem por caminho alternativo no MVP (Fase 0–3). EAs MQL5 dentro do MT5 fazem a execução; o Python publica parâmetros e recebe eventos.

#### 6.1.1 Três opções para hospedar o MT5 em Linux

A MetaQuotes **não distribui** versão nativa Linux do MT5. Há três caminhos viáveis:

| Opção | Como funciona | Prós | Contras |
|---|---|---|---|
| **A. Wine local (oficial)** | MetaQuotes distribui script Wine para Ubuntu/Debian. Roda direto no host | Tudo em uma máquina, sem latência de rede; gratuito | Wine pode glitchar; updates do MT5 quebram ocasionalmente; gráficos podem ter artefatos |
| **B. Container Wine pré-configurado** | Imagem Docker tipo `gmag11/metatrader5` ou build próprio com Wine + MT5 | Reprodutível; isolado; portável entre máquinas Linux | Comunidade pequena; manutenção da imagem é trabalho; X11/Wayland passthrough chato |
| **C. VPS Windows remoto** | MT5 roda em VPS Windows da Forex/HostWinds/Contabo (R$ 50–150/mês). Linux local conecta via API | MT5 estável, package Python oficial funciona, latência baixa pra B3 se VPS for em SP | Custo recorrente; mais um ponto de falha (rede); fica dependente de provider |

**Recomendação para Carlos:** começar com **opção A (Wine local)** na Fase 1, validar estabilidade por 4 semanas. Se Wine glitchar repetidamente, migrar para **C (VPS Windows)** — sem reescrever nada da bridge, só mudar IP/porta.

#### 6.1.2 Bridge Python ↔ MT5 — três alternativas

O `MetaTrader5` Python package oficial **só funciona em Windows nativo**. Em Linux/Wine, três bridges viáveis:

| Bridge | Como funciona | Maturidade | Custo |
|---|---|---|---|
| **EA MQL5 custom + socket TCP** | EA MQL5 que escuta porta TCP local, expõe métodos (`get_tick`, `send_order`, `get_position`) e publica eventos | Alta — padrão da comunidade MT5 quant | R$ 0 (open source `mql5-trading-server`, `dwx_zeromq`) |
| **ZeroMQ via dwx-zeromq-connector** | Padrão consagrado: lib MQL5 + lib Python comunicam via ZeroMQ. Suporta req/rep, pub/sub, push/pull | Alta — projeto de Darwinex maintido | R$ 0 |
| **MetaApi SaaS** | API REST/WebSocket hospedada na cloud; substitui MT5 local. Roda também em produção | Comercial, estável | US$ 0–250/mês conforme uso |

**Recomendação:** **dwx-zeromq-connector** (open source, comunidade ativa, design correto pub/sub). MetaApi fica como plano B se o setup ZeroMQ em Wine for instável.

#### 6.1.3 Faseamento da integração MT5 (sequencial, sem pular)

| Fase | O que o CaM faz com o MT5 | Quando avança |
|---|---|---|
| **F1 — Manual** | CaM gera plano do dia, checklist, Risk Engine valida. Carlos opera MT5 manualmente. CaM registra trades manualmente | Após primeira semana operando com 0 violação |
| **F2 — Importação histórica** | CaM importa relatório HTML/Excel/CSV do MT5 pós-mercado. Concilia journal manual × execução real | Quando importação cobre 100% das operações sem erro |
| **F3 — Bridge read-only (ZeroMQ)** | EA MQL5 publica via pub/sub: ticks, posições, P&L. CaM consome via Python+ZeroMQ. **Ainda não envia ordem** | Quando estável por 30 dias úteis |
| **F4 — Bridge read-write (EA + Risk Engine espelhado)** | EA MQL5 implementa estratégia + risk_mirror; CaM publica parâmetros aprovados; EA executa em conta de simulação primeiro, depois real | Após validação extensa em conta demo |
| **F5 — Migração para `MetaTrader5` package nativo (opcional)** | Se Carlos decidir mover MT5 para VPS Windows OU rodar Python dentro do Wine, package oficial funciona — bridge custom vira fallback | Decisão futura por emenda |

**ADR-001-LINUX (CaM):** MT5 é a plataforma oficial de execução nesta variante. Bridge ZeroMQ é a integração padrão.

---

### 6.2 Backend Python — Vertical Slice + Shared Kernel

**Idêntico ao documento Windows+Profit (§6.2)** — Feature-Based Vertical Slice Architecture + Shared Kernel mínimo (ADR-013).

**Única diferença:** a feature `profit_integration/` é substituída por `mt5_integration/`, com a mesma anatomia padrão (`README.md`, `domain.py`, `schemas.py`, `repository.py`, `service.py`, `routes.py`, `events.py`, `tests/`).

```
backend/cam/features/mt5_integration/
├── README.md              # contrato: bridge ZeroMQ + comandos disponíveis + eventos consumidos
├── domain.py              # MT5Tick, MT5Position, MT5Order
├── schemas.py             # Pydantic in/out
├── bridge.py              # ZeroMQ pub/sub + req/rep com EA MQL5
├── importer.py            # importação HTML/Excel/CSV do MT5 (Fase 1-2)
├── service.py             # orquestração: assinatura, reconnect, heartbeat
├── routes.py              # endpoints para status da bridge
├── events.py              # publica eventos `mt5.tick`, `mt5.fill`, `mt5.position_change`
└── tests/                 # mock do EA via fake ZeroMQ server
```

**Regra cardinal mantida:** `features/mt5_integration/` NÃO importa `features/Y/`. Comunicação com outras features só via eventos.

---

### 6.3 Risk Engine — `cam/_shared/risk/`

**Idêntico ao documento Windows+Profit (§6.3)** — Pure Python, zero I/O, 100% testado com property-based via `hypothesis`, validators ligados aos artigos constitucionais.

---

### 6.4 Banco de Dados — PostgreSQL 16 + TimescaleDB desde Fase 0

**Idêntico ao documento Windows+Profit (§6.4)** — Postgres+Timescale via Docker.

**Diferença operacional:** no Linux roda **Docker Engine + docker-compose nativo** (sem Docker Desktop, sem licença), via `apt install docker.io docker-compose-v2` ou install script oficial. Já temos Docker 29.1 instalado na máquina atual.

---

### 6.5 Frontend — React 19 + Vite + MUI

**Idêntico ao documento Windows+Profit (§6.5)** — SPA local servida pelo backend FastAPI, telas mínimas iguais (`Cockpit Live`, `Trade Journal`, `Estratégias`, `Risk Console`, `Backtest`, `Paper Trading`, `Carteira Hard`, `Fiscal`, `Constituição read-only`, `Configurações`).

**Detalhe específico:** a tela `Configurações` ganha uma seção **"Bridge MT5"** com:

- Status da conexão ZeroMQ (verde/vermelho)
- Heartbeat e latência (ms)
- Botão "Reiniciar bridge"
- Path do MT5 (Wine local / container / VPS)
- Janela do MT5 aberta vs fechada (se Wine local)

---

### 6.6 IA — Política Vinculante

**Idêntica ao documento Windows+Profit (§6.6)** — Arts. 34º–36º.

---

### 6.7 Rodando MT5 em Linux — Setup Operacional

Esta seção não existe no documento Windows+Profit. Detalhamento prático específico desta variante.

#### Opção A — Wine local (recomendada para Fase 1)

```bash
# Ubuntu 24.04+ / 26.04
# 1. Instalar Wine
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -cs)/winehq-$(lsb_release -cs).sources
sudo apt update
sudo apt install --install-recommends winehq-stable

# 2. Baixar instalador MT5 da MetaQuotes
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# 3. Rodar via Wine
wine mt5setup.exe
# Setup gráfico abre, instala MT5

# 4. Lançar MT5
wine "$HOME/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"
```

**Atenção:** MetaQuotes mantém um script oficial em `https://www.mql5.com/en/articles/625` (artigo "Linux on MetaTrader 5"). Vale rodar o script oficial em vez de instalar tudo manualmente.

#### Opção B — Container Wine pré-configurado

```yaml
# docker-compose.yml fragment
services:
  mt5:
    image: ghcr.io/elestio/metatrader5:latest   # validar imagem maintida antes de usar
    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./mt5-data:/config
    ports:
      - "5556:5556"   # porta ZeroMQ exposta pelo EA
    network_mode: host  # ou rede dedicada com expose das portas
```

#### Opção C — VPS Windows remoto

- Provedor recomendado para Brasil: **Forex VPS** ou **ContaboFX** com servidor em São Paulo (latência baixa pra B3)
- Custo típico: R$ 80–150/mês
- Conexão CaM Linux → VPS via TCP (ZeroMQ porta exposta) ou MetaApi
- **Risco:** mais um ponto de falha; CaM precisa lidar com perda de conexão como evento operacional (estado OPS)

---

## 7. Ambiente — Linux nativo (sem dual SO)

### 7.1 Desenvolvimento e produção no mesmo host

Vantagem chave desta variante: **dev = prod**. Não há ponte entre WSL2 e Windows nativo; não há "rodar o Risk Engine no Linux mas testar integração no Windows". Tudo no mesmo SO.

| Item | Status no host atual (Ubuntu 26.04) |
|---|---|
| Linux | ✅ Ubuntu 26.04 LTS |
| Docker Engine | ✅ Docker 29.1 |
| Git, Node, pnpm, gh | ✅ Já instalados |
| Python 3.12 | ⚠️ Atual é 3.14 — instalar 3.12 paralelo via `uv python install 3.12` |
| Wine | ❌ Instalar (`winehq-stable`) — se opção A para MT5 |
| `psql` client | ❌ Instalar (`postgresql-client`) |
| `uv`, `ruff`, `rclone` | ❌ Instalar (mesmos comandos do documento Windows) |

### 7.2 Containers nativos

Diferente do Windows, no Linux rodamos Docker Engine direto, sem Docker Desktop. Mesma `docker-compose.yml` mas:

- Volumes mapeados em `/home/carlos/...` em vez de `C:\Users\Carlos\...`
- Networks usam bridge nativo sem virtualização
- Performance significativamente melhor (sem overhead WSL2)

### 7.3 Estratégia de produção 24/7 (futura)

Para Fase 4+ com EA rodando autônomo no horário de pregão:

| Componente | Como manter rodando |
|---|---|
| MT5 (Wine) | `systemd --user` service com auto-restart |
| Backend FastAPI | `systemd` service + uvicorn workers |
| Postgres+Timescale | container Docker com `restart: unless-stopped` |
| Backup pg_dump + rclone | `systemd timer` diário |
| Telegram bot (independente) | `systemd` service separado — sobrevive a crash do cockpit |

---

## 8. Estrutura de Repositórios

```
apps/
└── cam-cockpit/                  # backend Python + frontend React no mesmo repo
    ├── backend/
    │   ├── pyproject.toml
    │   ├── alembic.ini
    │   ├── migrations/
    │   ├── tests/
    │   ├── .env.example
    │   └── cam/
    │       ├── _shared/          # SHARED KERNEL
    │       ├── features/
    │       │   ├── mt5_integration/   # ← bridge ZeroMQ + importer
    │       │   ├── journal/
    │       │   ├── fiscal/
    │       │   └── ...
    │       └── api/
    │
    ├── frontend/                 # idêntico ao doc Windows
    │
    ├── mql5/                     # ← substituiu /ntsl
    │   ├── experts/              # EAs (Expert Advisors)
    │   │   ├── cam_bridge.mq5    # EA principal (publica ticks + executa ordens)
    │   │   └── cam_risk_mirror.mq5  # risk_mirror espelhado
    │   ├── indicators/           # indicadores customizados (se houver)
    │   ├── scripts/              # scripts MQL5 utilitários
    │   ├── include/              # bibliotecas .mqh compartilhadas
    │   └── README.md
    │
    ├── scripts/
    │   ├── dev.sh
    │   ├── backup.sh
    │   ├── import_mt5_report.py
    │   ├── install_wine_mt5.sh   # ← novo: setup automatizado do Wine+MT5
    │   └── start_mt5.sh
    ├── docker-compose.yml        # Postgres+Timescale (+ opcional container MT5)
    └── README.md
```

---

## 9. ADRs (Architecture Decision Records) — Variante Linux+MT5

ADRs que mudam em relação ao documento Windows+Profit. Os demais (ADR-002, 003, 004, 005, 006, 007, 010, 011, 013) **permanecem idênticos**.

| ID | Decisão | Status |
|---|---|---|
| **ADR-001-LINUX** | MT5 (MetaQuotes) como plataforma oficial de execução. EAs MQL5 fazem execução. Bridge ZeroMQ Python↔MQL5 é a integração padrão | Proposto |
| **ADR-008-LINUX** | Integração MT5 por fases: Manual → Importação HTML/CSV → Bridge read-only (ZeroMQ) → Bridge read-write (EA + risk_mirror) → Migração opcional para `MetaTrader5` package nativo via VPS Windows | Proposto |
| **ADR-009-LINUX** | Risk Engine espelhado em MQL5 (`cam_risk_mirror.mq5`) dentro do EA como segunda linha de defesa. Mesma lógica do espelhamento NTSL do documento Windows | Proposto |
| **ADR-012-LINUX** | Dev e produção no mesmo Linux (Ubuntu LTS). Sem dual SO. Wine como detalhe de execução para o MT5 | Proposto |
| **ADR-014-LINUX** (novo) | MT5 hospedado em Wine local (Fase 1), com plano de migração para VPS Windows se instabilidade Wine recorrente. CaM resiliente à mudança de host MT5 (configurável por env: localhost vs IP da VPS) | Proposto |
| **ADR-015-LINUX** (novo) | Docker Engine nativo (sem Docker Desktop). Postgres+Timescale, opcionalmente MT5 container, todos em `docker-compose.yml` versionado | Proposto |

---

## 10. Custos Recorrentes — Variante Linux+MT5

| Item | Custo aproximado | Obrigatório? |
|---|---|---|
| Sistema operacional | R$ 0 (Ubuntu LTS) | Sim |
| MetaTrader 5 (plataforma) | R$ 0 (gratuito da MetaQuotes) | Sim |
| Corretora com MT5 + WIN/WDO | corretagem por trade | Sim |
| Conta de simulação MT5 (demo) | R$ 0 (gratuita) | Sim (Fase 1) |
| VPS Windows (se opção C para hospedar MT5) | R$ 80–150/mês | Opcional |
| MetaApi (se substituir bridge ZeroMQ) | US$ 0–250/mês conforme uso | Opcional plano B |
| Cloud backup (rclone GDrive/S3) | R$ 0–30/mês | Recomendado |
| Anthropic API (uso analítico) | R$ 0–50/mês | Não, sob demanda |
| GitHub privado | R$ 0 (free tier) | Sim |
| Telegram | R$ 0 | Sim |
| PostgreSQL/TimescaleDB | R$ 0 (open source, container) | Sim |
| Resto da stack | R$ 0 (open source) | — |

**Total mensal típico Fase 1–3:** **R$ 0–30** (apenas corretagem + backup opcional). Se opção C (VPS): R$ 80–180.

**Comparação direta com Windows+Profit:** estimativa do doc Windows era R$ 200–380/mês (Profit Pro). Esta variante economiza **R$ 200–350/mês** no MVP.

**Atenção:** o custo "zero" do MT5 esconde custo de manutenção do Wine (tempo de Carlos) — se Wine glitchar muito, vai consumir horas. Se isso virar realidade, migrar para opção C (R$ 80–150/mês VPS) — ainda mais barato que Profit Pro.

---

## 11. Riscos da Stack — Variante Linux+MT5

Riscos R1–R8 do documento Windows+Profit permanecem (substituindo "Profit" por "MT5" onde aplicável). **Riscos adicionais específicos desta variante:**

| ID | Risco | Mitigação |
|---|---|---|
| **R9-LINUX** | Wine glitcha após update do MT5 ou após update do Wine | Travar versão do MT5; testar update em ambiente isolado antes; ter VPS Windows como plano B documentado |
| **R10-LINUX** | Bridge ZeroMQ perde conexão silenciosamente (TCP sem heartbeat ativo) | Heartbeat obrigatório a cada 1s; se >3s sem heartbeat, marca como "MT5 offline" no cockpit, envia alerta Telegram, bloqueia novas ordens (estado OPS) |
| **R11-LINUX** | Conta MT5 da corretora brasileira não permite EA / Automação | Validar **antes da Fase 1** com a corretora escolhida. Algumas exigem plano específico para Algorithmic Trading |
| **R12-LINUX** | MetaQuotes encerra suporte oficial a Linux/Wine sem aviso | Pivot para opção C (VPS Windows) — código da bridge não muda |
| **R13-LINUX** | Comunidade brasileira de quant é majoritariamente Profit/NTSL — menos tutoriais MT5+Linux em PT | Aceitar custo de aprendizado; recursos em inglês são abundantes (forum mql5.com) |

---

## 12. O Que Esta Stack NÃO É

Mesma lista do documento Windows+Profit, com nota adicional:

- ❌ Não usa Windows como SO de produção
- ❌ Não usa Profit/NTSL — esses ficam só no documento Windows
- ❌ Não usa `MetaTrader5` Python package oficial nativamente (não funciona em Linux) — opção C (VPS) é o caminho se essa lib for crítica

---

## 13. Matriz Comparativa — Windows+Profit vs Linux+MT5

> **Esta seção é o coração do documento.** Use para decidir.

| Critério | Windows + Profit | **Linux + MT5 (este doc)** | Vencedor |
|---|---|---|---|
| **Custo mensal MVP** | R$ 200–380 (Profit Pro) | R$ 0–30 (ou R$ 80–180 com VPS) | **Linux+MT5** |
| **Custo de licença SO** | Windows 11 (~R$ 700 uma vez, ou licença OEM já no PC) | R$ 0 (Ubuntu LTS) | **Linux+MT5** |
| **Estabilidade da plataforma** | Profit é nativa Windows, robusta | MT5 em Wine: estabilidade variável; em VPS Windows: idêntica a Windows nativo | Windows+Profit (Wine) / empate (VPS) |
| **Documentação em português** | Profit tem comunidade brasileira gigante; tudo em PT | MT5 tem documentação em PT da MetaQuotes; comunidade brasileira menor | Windows+Profit |
| **API Python oficial** | ProfitDLL existe (Fase 5+) | `MetaTrader5` package só Windows; em Linux precisa bridge | Windows+Profit |
| **Setup inicial** | Instalar Profit, contratar plano, baixar book | Instalar Wine, baixar MT5, configurar EA — mais passos | Windows+Profit |
| **Manutenção do ambiente** | Updates do Windows + Profit (pode quebrar) | Updates do Wine + MT5 (pode quebrar) + bridge | Empate |
| **Dev = Prod** | Não (dev Linux, prod Windows) | **Sim** (dev e prod mesmo Linux) | **Linux+MT5** |
| **Containerização** | Docker Desktop + WSL2 (overhead) | Docker Engine nativo | **Linux+MT5** |
| **Backup e DR** | Equivalente (rclone) | Equivalente (rclone) | Empate |
| **Performance Risk Engine** | Mesma (Python nativo) | Mesma (Python nativo) | Empate |
| **Brokers no Brasil** | Várias (XP, Genial, Modal, etc) | Várias (XP, Clear, Genial, Modal, Avenue, Toro) — **validar** | Empate |
| **Linguagem estratégia broker** | NTSL (parecido com Pascal) | MQL5 (parecido com C++) — mais poderosa | **Linux+MT5** |
| **Suporte a backtest no broker** | Profit tem replay/simulador | MT5 tem **Strategy Tester** muito robusto, tick-by-tick | **Linux+MT5** |
| **Cross-broker (futuro)** | Profit é uni-broker | MT5 é cross-broker mundial (Forex, Crypto, B3) | **Linux+MT5** |
| **Risco de descontinuação** | Profit existe há ~20 anos, comunidade BR | MT5 é padrão mundial, MetaQuotes referência | **Linux+MT5** |
| **Stack 100% open-source** | Não (Windows + Profit pago) | Sim (exceto MT5 binário, gratuito) | **Linux+MT5** |
| **Familiaridade Carlos** | Carlos vem de Java/backend, familiaridade Windows operacional | Carlos vem de Java/backend, dev nativo Linux | Empate / leve **Linux+MT5** |
| **Curva de aprendizado MQL5 vs NTSL** | NTSL mais simples; menos features | MQL5 mais robusta; curva maior | depende do objetivo |
| **Confiança operacional do sistema** | Profit é caixa-preta confiável | MT5+Wine introduz variável extra | **Windows+Profit** |
| **Latência ordem→broker** | Profit no Windows: ms | MT5 Wine local: ms; MT5 VPS: ms+RTT | **Windows+Profit** marginalmente |

### Resumo qualitativo

**Escolha Windows+Profit se:**
- Você quer **caminho de menor resistência operacional** — Profit Pro just works, ProfitDLL existe como upgrade futuro
- Custo de R$ 200–380/mês não é problema
- Documentação 100% em português é importante
- Você prefere estabilidade comprovada à liberdade técnica

**Escolha Linux+MT5 se:**
- Você quer **dev=prod, stack inteira open source, custo mínimo**
- Você está disposto a investir tempo aprendendo MQL5 e configurando Wine
- Você valoriza ter MT5 (padrão mundial) na bagagem técnica
- Você quer a possibilidade futura de operar Forex/Crypto cross-broker
- Você confia que o setup MT5+Wine vai estabilizar com 2–4 semanas de tuning

**Decisão híbrida possível (não recomendada):** começar Linux+MT5 com plano explícito de migrar para Windows+Profit se Wine glitchar de forma intolerável nas primeiras 4 semanas. Tem custo (refazer integração), mas é reversível.

---

## 14. Próximas Decisões Pendentes (bloqueadores Fase 1)

1. **Windows+Profit vs Linux+MT5** — esta é a decisão-mãe. Sem ela, Fase 1 não começa. Carlos decide.
2. **Corretora vinculada** — confirmar se permite WIN/WDO via MT5 (se variante Linux) ou Profit (se variante Windows). XP, Clear, Genial, Modal, Avenue, Toro têm MT5 para B3.
3. **Hospedagem do MT5** (se Linux): Wine local OU container Wine OU VPS Windows. Recomendação: A primeiro, C como plano B.
4. **Bridge MT5↔Python**: ZeroMQ via dwx-zeromq-connector OU socket TCP custom OU MetaApi.
5. **Tese de edge da primeira estratégia** — independente da variante.
6. **Origem do tick histórico para backfill da Timescale** — Profit ou MT5? Define M2.

---

## 15. Roadmap Resumido (variante Linux+MT5)

Mesmo do documento Windows+Profit, com diferenças nos milestones que tocam o broker:

| Milestone | Conteúdo principal (diff vs doc Windows em itálico) |
|---|---|
| **M0** | Constituição + Stack Oficial Linux+MT5 + Política Operacional |
| **M1** | Docker Compose (Postgres+Timescale) + Alembic + Backend FastAPI esqueleto + `_shared/risk/` 100% test |
| **M2** | Schema completo + hypertables + continuous aggregates + *backfill inicial via importação CSV do MT5* |
| **M3** | Frontend cockpit passivo |
| **M4** | Ledger + Fiscal + *Importador HTML/Excel/CSV do MT5* + conciliação trade-a-trade |
| **M5** | Risk Engine completo (validators Arts. 11º–20º) + property-based |
| **M6** | Backtest engine + walk-forward + DuckDB research |
| **M7** | Estudos de padrão + IA analítica (Ollama + Anthropic) |
| **M8** | *Instalação Wine+MT5 + EA `cam_bridge.mq5` + bridge ZeroMQ read-only + paper trading via MT5 demo* |
| **M9** | *EA `cam_risk_mirror.mq5` + bridge read-write + critérios de saída Fase 0* |

---

## 16. Aprovação

Este documento é **proposto** como **alternativa** ao [`STACK-CAM-OFICIAL.md`](./STACK-CAM-OFICIAL.md) (Windows+Profit). Carlos decide qual virar canônico.

Quando a decisão for tomada:

- **Se Windows+Profit:** este documento (`STACK-CAM-OFICIAL-LINUX.MD`) vai para `archive/` com nota de "não escolhido"
- **Se Linux+MT5:** o documento `STACK-CAM-OFICIAL.md` vai para `archive/` e este vira o canônico (renomeando para `STACK-CAM-OFICIAL.md` sem o sufixo `-LINUX`)
- **Se híbrido (improvável):** revisão completa — não recomendado

---

> **Frase final desta variante:**
>
> O CaM continua sendo o cockpit que impede operação ruim. O Linux libera o Carlos de uma dependência de SO; o MT5 abre cross-broker no futuro. O preço é Wine como variável de execução — gerenciável.
>
> O MT5 executa. O Wine hospeda. O Python governa. O React mostra. O Ledger registra. O Risk Engine manda. A IA comenta. O Carlos obedece ao sistema.

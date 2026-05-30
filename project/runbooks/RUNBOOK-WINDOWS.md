# RUNBOOK — cam-cockpit no **Windows 11** (MetaTrader 5 nativo)

> **Contexto (2026-05-30):** dois níveis de decisão:
> - ✅ **SO = Windows 11 (FIRME)** — o MT5 sob Wine no Linux falhou.
> - 🔄 **Broker = EM AVALIAÇÃO** — este runbook cobre o **teste do MetaTrader 5**
>   no Windows (Founder já criou alguns pontos/setups). **Profit NÃO caiu — está em
>   STANDBY**; se o 1º teste do MT5 não convencer, o Profit é reativado.
> Este runbook é a referência operacional do **caminho MT5 sob teste**.
>
> ℹ️ **Soft-stage (pré-v1):** docs/ADRs moldáveis, **sem ADR HARD**. A decisão de
> broker fecha após o 1º teste — ver [§11](#11-decisão-pendente--próximos-passos).
>
> **Fase atual:** FASE_0 (Construção). **Sem trade real.** `REAL_TRADING_ALLOWED=false`.

---

## 0. Por que Windows resolve o problema

| Dor no Linux (Wine) | No Windows nativo |
|---|---|
| MT5 roda sob Wine — instável, `libzmq.dll` + DLL imports falham no prefixo Wine | MT5 é **app nativo Windows** — MetaEditor, EAs e DLLs funcionam como projetado |
| `mt5_wine_prefix` (`~/.wine`) frágil | Irrelevante — sem Wine |
| Bridge ZeroMQ MT5↔Python atravessa camada Wine | ZeroMQ roda em `127.0.0.1` no mesmo SO, sem tradução |
| Pacote Python `MetaTrader5` não roda nativo em Linux | Disponível nativo (opção futura; hoje usamos a bridge ZeroMQ) |

O **cockpit** (backend FastAPI + frontend React + Risk Engine + Ledger) é
multiplataforma e **não muda**. O que muda é a **camada de execução** (MT5).

---

## 1. Pré-requisitos (instalar nesta ordem)

| Ferramenta | Versão | Como instalar | Verificar (PowerShell) |
|---|---|---|---|
| **Windows 11** | 22H2+ | — | `winver` |
| **Git** | 2.4+ | https://git-scm.com/download/win | `git --version` |
| **Python** | 3.12+ | https://python.org (marque *Add to PATH*) | `python --version` |
| **uv** | qualquer | `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` | `uv --version` |
| **Node.js** | 20+ LTS | https://nodejs.org | `node --version` |
| **Docker Desktop** (WSL2) | 24+ | https://docs.docker.com/desktop/windows/ | `docker --version` |
| **MetaTrader 5** | build atual | site da **corretora** (não o genérico) | abrir o terminal |
| **Ollama** (opcional) | qualquer | https://ollama.com/download/windows | `ollama --version` |

> **Docker Desktop** precisa estar **em execução** (ícone na bandeja) antes de subir o banco.
> Alternativa sem Docker: PostgreSQL 16 + TimescaleDB nativo Windows na porta 5433 (ver §9).

---

## 2. Setup inicial (primeira vez)

```powershell
# 1. Clonar / abrir o repositório
cd C:\Users\<voce>\teczilabs\CaM-project\apps\cam-cockpit

# 2. Permitir execução de script nesta sessão (não persiste)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Setup automatizado (db + deps Python + migrations + deps npm)
.\scripts\dev.ps1
#   .\scripts\dev.ps1 -SkipDockerCheck   # se usar Postgres nativo (§9)

# 4. Criar o .env do backend
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

`backend\.env` mínimo no Windows:
```ini
DATABASE_URL=postgresql+psycopg://cam:cam@localhost:5433/cam_db
OLLAMA_BASE_URL=http://localhost:11434
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ANTHROPIC_API_KEY=
CAM_JOURNAL_DIR=%USERPROFILE%\.cam\journal

# MT5 — Windows nativo (sem Wine):
MT5_INTEGRATION_ENABLED=true
MT5_BRIDGE_HOST=127.0.0.1
MT5_BRIDGE_PUB_PORT=5556
MT5_BRIDGE_REQ_PORT=5557
MT5_TERMINAL_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
# MT5_WINE_PREFIX — IGNORADO no Windows (era artefato do Linux/Wine)
```

> ⚠️ **Mutex de integração (R21.03):** `MT5_INTEGRATION_ENABLED` e
> `PROFIT_INTEGRATION_ENABLED` **não podem** estar `true` simultaneamente — o
> backend recusa subir. No Windows com MT5, mantenha Profit desativado.

---

## 3. Subir o cockpit (uso diário)

Abra **3 terminais PowerShell** + o **terminal MT5**:

```powershell
# Terminal 1 — Banco (Docker Desktop precisa estar rodando)
cd C:\Users\<voce>\teczilabs\CaM-project\apps\cam-cockpit
docker compose up -d db

# Terminal 2 — Backend FastAPI
cd backend
$env:DATABASE_URL = "postgresql+psycopg://cam:cam@localhost:5433/cam_db"
uv run uvicorn cam.api.main:app --reload --port 8000

# Terminal 3 — Frontend React/Vite
cd ..\frontend
npm run dev
```

| Serviço | URL |
|---|---|
| Cockpit (SPA) | http://localhost:5173 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |

---

## 4. MetaTrader 5 — instalação e EAs (a parte específica de Windows)

### 4.1 Instalar e logar em conta **DEMO**
1. Instalar o MT5 da **corretora** (não o genérico MetaQuotes).
2. File → Login to Trade Account → usar **conta DEMO**.
3. ⚠️ Constituição: o `cam_risk_mirror.mq5` só entrega ordem se
   `ACCOUNT_TRADE_MODE == ACCOUNT_TRADE_MODE_DEMO`. Conta real é barrada no EA.

### 4.2 ZeroMQ no MT5 (o que falhava no Wine)
A bridge usa ZeroMQ via `mql5/include/cam_zmq.mqh` (importa DLL).

1. Baixar `libzmq.dll` (x64) e copiar para:
   `%APPDATA%\MetaQuotes\Terminal\<HASH>\MQL5\Libraries\`
2. MT5 → Tools → Options → **Expert Advisors**:
   - ☑ **Allow algorithmic trading**
   - ☑ **Allow DLL imports**
3. (Localhost não exige liberar firewall externo; é tudo `127.0.0.1`.)

### 4.3 Compilar e instalar os EAs
Copiar os artefatos versionados do repo para a pasta do MT5:

```powershell
$mt5 = "$env:APPDATA\MetaQuotes\Terminal\<HASH>\MQL5"
Copy-Item mql5\experts\cam_bridge.mq5       "$mt5\Experts\"
Copy-Item mql5\experts\cam_risk_mirror.mq5  "$mt5\Experts\"
Copy-Item mql5\include\cam_zmq.mqh          "$mt5\Include\"
```

1. Abrir **MetaEditor** (F4 no MT5).
2. Abrir `cam_bridge.mq5` → **F7** (compilar, 0 warnings — CA12.1).
3. Abrir `cam_risk_mirror.mq5` → **F7**.
4. No MT5: Navigator → arrastar **`cam_bridge.mq5`** para o gráfico **WIN** (e outro para **WDO**).
5. Para execução-espelho (DEMO): arrastar **`cam_risk_mirror.mq5`**, confirmar
   `InpRequireDemoAccount=true` e o magic number.

### 4.4 Validar a bridge
```powershell
curl http://localhost:8000/api/v1/mt5/bridge/status
# online:true + heartbeat recente = bridge ok
```
- Logs MT5: aba **Experts** / **Journal** no terminal.
- Logs CaM: `%USERPROFILE%\.cam\logs\cam-audit.log`.

---

## 5. Guardrails constitucionais no Windows (não-negociável)

| Regra | Onde se materializa |
|---|---|
| `REAL_TRADING_ALLOWED=false` em toda release | `cam/_shared/config` (default) |
| **`cam_risk_mirror.mq5` é o ÚNICO** autorizado a `OrderSend` | `scripts/lint_mql5.py` enforça allowlist |
| EA entrega **só em conta DEMO** | `cam_risk_mirror.mq5` + `cam_bridge.mq5` checam `ACCOUNT_TRADE_MODE_DEMO` |
| `cam_bridge.mq5` é **read-only** (não envia ordem) | teste de inspeção do módulo |
| Kill switch acessível ≤ 1 toque (Art. 18º) | header do cockpit (toda rota) |
| Mutex MT5 × Profit (R21.03) | `validate_integration_mutex` no startup |

Rodar o lint MQL5 antes de qualquer deploy de EA:
```powershell
uv run python scripts\lint_mql5.py    # falha se OrderSend aparecer fora do risk_mirror
```

---

## 6. Comandos de desenvolvimento (PowerShell)

```powershell
cd backend
uv run pytest -q                       # suíte completa (banco ativo) — 749 testes
uv run pytest --ignore=tests\test_migrations.py -q   # sem banco
uv run ruff check cam\ tests\
uv run mypy cam\
uv run lint-imports                    # contratos de arquitetura
uv run alembic upgrade head            # migrations

cd ..\frontend
npm test                               # Vitest — 63 testes
npm run build                          # tsc + vite build
npm run lint:no-hardcode               # DS: zero hex fora do theme
```

---

## 7. Parar o ambiente

```powershell
docker compose stop db        # preserva o volume pgdata
# Ctrl+C nos terminais do backend e frontend
# Fechar/remover EAs do gráfico no MT5 antes de encerrar o terminal
```

Destruir banco (irreversível): `docker compose down -v`

---

## 8. Backup (Windows)

```powershell
.\scripts\backup.ps1                   # pg_dump + journal JSONL
# Agendar no Task Scheduler (diário 02:00) apontando para backup.ps1
```

---

## 9. Alternativa sem Docker — PostgreSQL nativo

Se o Docker Desktop não for viável:
1. Instalar **PostgreSQL 16** (https://postgresql.org) na porta **5433**.
2. Adicionar a extensão **TimescaleDB** (https://docs.timescale.com/self-hosted/latest/install/installation-windows/).
3. Criar role/db: `CREATE USER cam PASSWORD 'cam'; CREATE DATABASE cam_db OWNER cam;`
4. Rodar `.\scripts\dev.ps1 -SkipDockerCheck`.

---

## 10. Troubleshooting (Windows)

| Sintoma | Causa / correção |
|---|---|
| `dev.ps1` não executa | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `docker: error during connect` | Docker Desktop não está rodando — inicie pelo ícone da bandeja |
| Bridge `online:false` | MT5 fechado, EA `cam_bridge` não anexado, ou `libzmq.dll` ausente em `MQL5\Libraries` |
| MetaEditor: `cannot load library` | Faltou copiar `libzmq.dll` (x64) ou desmarcou **Allow DLL imports** |
| EA não envia em DEMO | confira `InpRequireDemoAccount` e que a conta logada é DEMO |
| Porta 5433 ocupada | `Get-NetTCPConnection -LocalPort 5433`; ajuste o `docker-compose.yml` |
| Frontend não acha API | backend no 8000? `curl http://localhost:8000/api/v1/health` (Vite faz proxy `/api`) |
| `uv` não encontrado | reabrir o PowerShell após instalar (PATH) |
| Backend recusa subir (mutex) | `MT5_INTEGRATION_ENABLED` e `PROFIT_INTEGRATION_ENABLED` ambos `true` — desative o Profit |

---

## 11. Decisão pendente + próximos passos

Em soft-stage (pré-v1) **não abrimos ADR HARD** — atualizamos as docs existentes
(já feito: `STACK-CAM-OFICIAL.md`, `DECISION-MEMO §10`, `ADR-001/008/009/012`).

**Decisão de broker — gate do Founder após o 1º teste do MT5:**

| Saída do 1º teste | Ação |
|---|---|
| MT5 convence | Promover MT5 a broker oficial; manter Profit arquivado como fallback |
| MT5 não convence | **Reativar Profit do standby** (`PROFIT_INTEGRATION_ENABLED=true`, `MT5_INTEGRATION_ENABLED=false` — respeitar o mutex R21.03) |

**Pontos técnicos a validar no teste:**
1. Bridge ZeroMQ estável em Windows (heartbeat, sem dropar `libzmq.dll`).
2. `mt5_wine_prefix` é no-op no Windows; `mt5_terminal_path` aponta para o `terminal64.exe`.
3. **Kevin:** perímetro de execução no Windows (DEMO-only, allowlist `OrderSend`).
4. Paridade Risk Engine Python × `cam_risk_mirror.mq5` (espelho dos 18 validators).

> **Standby do Profit:** artefatos NTSL seguem em `apps/cam-cockpit/ntsl/`. Nada foi
> apagado — o Profit é reativável a qualquer momento enquanto não houver decisão.

---

*Runbook Windows — orquestração Leo · lentes Vint (infra/OPS), Kevin (perímetro), Oscar (ARCH). Soft-stage, FASE_0, sem trade real. Broker em avaliação (MT5 teste / Profit standby).*

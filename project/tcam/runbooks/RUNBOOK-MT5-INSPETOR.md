---
template: RUNBOOK
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
relacionados: ADR-014, SPEC-Inspetor-de-Ativo, RUNBOOK-WINDOWS
date: 2026-06-01
status: Vigente
---

# RUNBOOK — Configuração do MT5 para o Inspetor de Ativo

> **Objetivo:** ligar o caminho de dados MT5 → backend → Inspetor, ponta a ponta,
> em **conta real** e **read-only**. Ao final você digita `PETR4` em `/inspetor`
> e vê candles + tick/book ao vivo + fundamentos + regime.
>
> **Constituição:** este caminho é **read-only por construção** (Art. 35º / CA15.1).
> O EA `cam_bridge` não contém — e não pode conter — `OrderSend`. Ler dado de conta
> real é seguro; **enviar ordem não é possível por design**.

---

## 0. Pré-requisitos

- Windows 11 (SO firme — ver `STACK-CAM-OFICIAL.md`).
- **MetaTrader 5 instalado e logado** (conta real da corretora — ex.: Genial).
- Backend e frontend do `cam-cockpit` instalados (ver `RUNBOOK-WINDOWS.md`).
- PostgreSQL + TimescaleDB de pé (`docker compose up -d db`).
- **`libzmq.dll` já vem no projeto** em `apps/cam-cockpit/mql5/libraries/` (x64,
  proveniência em `PROVENANCE.md`) — **não** precisa baixar nem buildar.

---

## 1. Instalar a ponte ZeroMQ no MT5

1. MT5 → **Arquivo → Abrir Pasta de Dados** (abre `...\MQL5\`).
2. Copie do repositório para dentro de `MQL5\`:
   - `apps/cam-cockpit/mql5/include/cam_zmq.mqh` → `MQL5\Include\cam_zmq.mqh`
   - `apps/cam-cockpit/mql5/experts/cam_bridge.mq5` → `MQL5\Experts\cam_bridge.mq5`
   - **todas as 5 DLLs** de `apps/cam-cockpit/mql5/libraries/` → `MQL5\Libraries\`
     (`libzmq.dll` + `libsodium-138090d4.dll` + `msvcp140.dll` +
     `vcruntime140.dll` + `vcruntime140_1.dll`). A `libzmq.dll` **precisa** das outras
     4 ao lado para carregar.
3. MT5 → **Ferramentas → Opções → Expert Advisors** → marque
   **"Permitir importação de DLL"**.

> ⚠️ Sem as DLLs em `MQL5\Libraries\` e sem "Allow DLL imports", o EA falha
> ao inicializar (`[CamBridge] Falha ao inicializar ZeroMQ`).
>
> ℹ️ A `libzmq.dll` (4.3.4 x64) foi reaproveitada do `pyzmq` já instalado e teve
> a carga + exports verificados (ver `libraries/PROVENANCE.md`). Numa máquina
> com `pyzmq` instalado, as DLLs já estão em
> `...\sitepackages\pyzmq.libs\` — o projeto só consolidou e renomeou.

---

## 2. Compilar o EA

1. Abra o **MetaEditor** (F4 no MT5).
2. Abra `Experts\cam_bridge.mq5` → **Compilar** (F7).
3. Esperado: **0 errors** (avisos de DLL import são aceitáveis). Versão
   `0.4.0-inspetor`.

---

## 3. Atachar o EA a um gráfico

1. Abra um gráfico de qualquer símbolo (ex.: `PETR4`). O EA observa por padrão o
   símbolo do gráfico; o backend troca o símbolo observado via `SUBSCRIBE`.
2. Arraste `cam_bridge` (Navegador → Expert Advisors) para o gráfico.
3. Aba **Inputs**:

   | Input | Valor | Por quê |
   |---|---|---|
   | `InpPubPort` | `5556` | porta PUB (tick/book/heartbeat) |
   | `InpReqPort` | `5557` | porta REP (candles/symbols/subscribe) |
   | `InpRequireDemoAccount` | **`false`** | ⚠️ **opt-in consciente** p/ conta REAL read-only (ADR-014 R-10). Default `true` (defesa). |
   | `InpPublishBook` | `true` | publica DOM quando o ativo fornece |
   | `InpMaxCandles` | `5000` | protege o heartbeat do EA single-thread |

4. Aba **Comum**: marque **"Permitir negociação algorítmica"** (o MT5 exige para
   rodar `OnTick`, mesmo o EA sendo read-only).
5. Confirme. Rosto 🙂 no canto = EA ativo.
6. Aba **Especialistas** do Terminal:
   `[CamBridge] v0.4.0-inspetor read-only ativo. ... Watched=PETR4 Book=on`.

> 🔒 **SEC-GOV (Kevin):** conta REAL exige `InpRequireDemoAccount=false` deliberado.
> O cockpit exibe banner **REAL** no header. Prova read-only:
> `grep OrderSend cam_bridge.mq5` = vazio.

---

## 4. Configurar o backend

No `.env` (`apps/cam-cockpit/backend/.env` — **nunca commitado**):

```ini
MT5_INTEGRATION_ENABLED=true
PROFIT_INTEGRATION_ENABLED=false

MT5_BRIDGE_HOST=127.0.0.1
MT5_BRIDGE_PUB_PORT=5556
MT5_BRIDGE_REQ_PORT=5557
MT5_BRIDGE_AUTOCONNECT=true

# brapi.dev — token opcional (free tier funciona p/ vários tickers)
BRAPI_TOKEN=
```

Aplique as migrations (cria `cam_inspector_candles`, usada pelo overlay de regime):

```powershell
cd apps\cam-cockpit\backend
.venv\Scripts\alembic upgrade head
```

---

## 5. Subir e validar

```powershell
# backend
cd apps\cam-cockpit\backend
.venv\Scripts\uvicorn cam.api.main:app --host 127.0.0.1 --port 8000

# frontend (outro terminal)
cd apps\cam-cockpit\frontend
npm install      # primeira vez (instala lightweight-charts etc.)
npm run dev
```

1. Cockpit → menu **Inspetor de Ativo** (`/inspetor`).
2. Digite `PETR4` → **Buscar**.
3. Esperado: chip **WS ONLINE** + **Último <preço>**; gráfico de candles; 7
   indicadores R-20 + dividendos + 2 estimativas; bloco de **Regime** (após
   carregar candles D1 — eles alimentam `cam_inspector_candles`).
4. Digite `WIN$` → só gráfico (sem fundamentos/regime — esperado).

---

## 6. Verificação por endpoint (sem a UI)

```powershell
curl http://127.0.0.1:8000/api/v1/mt5/symbols
curl "http://127.0.0.1:8000/api/v1/mt5/candles?symbol=PETR4&timeframe=D1&count=200"
curl http://127.0.0.1:8000/api/v1/fundamentals/PETR4
curl http://127.0.0.1:8000/api/v1/regime/PETR4
```

---

## 7. Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| `WS OFFLINE` / candles 503 | EA não atachado, MT5 fechado, portas divergentes | Confirme 🙂 no gráfico; portas EA == `.env`; reatache |
| `[CamBridge] ABORTANDO: conta nao e DEMO` | `InpRequireDemoAccount=true` em conta real | Reatache com `false` (consciente — §3) |
| `Falha ao inicializar ZeroMQ` | `libzmq.dll` ausente / "Allow DLL imports" off | DLL em `MQL5\Libraries\`; ligue a opção (§1) |
| "Book não disponível" | Corretora sem DOM para o ativo (comum em ações) | Esperado; futuros (WIN/WDO) costumam ter |
| `Símbolo não encontrado` | Ticker fora do Market Watch / nome MT5 diferente | Adicione ao Market Watch; cheque `GET_SYMBOLS` |
| Regime "Dados insuficientes" | `cam_inspector_candles` vazia p/ o ativo | Abra o ativo em **D1** (persiste candles) e recarregue |
| Fundamentos `N/A` em ação | brapi free tier sem o campo / rate limit | Tente token brapi; campos premium podem faltar |

---

## 8. Checklist SEC-GOV (conta real read-only)

- [ ] `grep OrderSend apps/cam-cockpit/mql5/experts/cam_bridge.mq5` → **vazio**.
- [ ] Allowlist REP do EA só contém comandos de leitura (sem `SUBMIT_ORDER`).
- [ ] `InpRequireDemoAccount=false` setado **deliberadamente** para conta real.
- [ ] Banner **REAL** visível no header do cockpit.
- [ ] `REAL_TRADING_ALLOWED=false` no `.env` (default — Inspetor não envia ordem).

---

## Referências

- ADR-014 — MT5 como market data read-only
- SPEC-Inspetor-de-Ativo §4 (contratos ZMQ/REST)
- RUNBOOK-WINDOWS — setup geral do ambiente Windows
- `apps/cam-cockpit/mql5/experts/cam_bridge.mq5` — EA (v0.4.0-inspetor)

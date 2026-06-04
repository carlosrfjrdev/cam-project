---
template: SPEC
phase: SPEC
status: Draft
version: 0.2.1
date: 2026-05-25
parent_spec: SPEC.md
demand_id: SPEC-v0.2
pmg: G
sec: true
qa_sec: true
revision_note: >
  v0.2.1 — Founder solicitou princípio de COEXISTÊNCIA em vez de substituição.
  Código `profit_integration` PERMANECE no repositório (marcado como Desativado);
  `mt5_integration` é criado como feature paralela nova. Nenhum código existente é
  removido em v0.2. Reversibilidade preservada.
---

# SPEC v0.2 — Enquadramento MT5 do CaM Cockpit

> **Lead:** Albert (especificação) · Co-lead: **Kevin** (`sec` + `qa-sec`)
> **Skill:** `teczi-demand-specification`
> **Aprovador:** Founder (Carlos Rodrigues Ferreira Junior)
>
> **Origem:** [`/project/DECISION-MEMO-LINUX-OR-WINDOWS.md`](../DECISION-MEMO-LINUX-OR-WINDOWS.md) §6 — decisão **Opção B (Linux + MT5 + MQL5)** registrada em 2026-05-25.
>
> **Vinculação constitucional:** Arts. 6º (preservar mais capital), 8º (perímetro), 11º (limite contratos), 15º (autoridade Risk Engine), 18º (kill switch), 19º (contingência técnica), 25º (P&L líquido), 31º (journal), 35º (IA não executa).

---

## 1. Contexto e propósito

O CaM saiu da Fase 0 com toda a infra Python/React/Postgres/TimescaleDB construída sob a premissa de que **uma camada de integração com a plataforma de execução** seria implementada quando a decisão-mãe (DECISION-MEMO) fosse resolvida. Em 2026-05-25 o Founder escolheu **Linux + MetaTrader 5 + MQL5**.

A SPEC v0.1 original (`SPEC.md`) referenciava `cam/features/profit_integration/` como feature de integração (Bloco D do PLAN). Essa feature foi parcialmente implementada — código-stub funcional (CSV import, validate-intention, reconciliação) que não persiste em DB.

**A v0.2 adiciona uma camada nova de integração com MetaTrader 5 sem remover a camada Profit existente.** A camada Profit fica **Desativada por feature flag** (`PROFIT_INTEGRATION_ENABLED=false` por padrão), código preservado para referência e reversibilidade futura.

### Princípio de coexistência (revisão v0.2.1 — solicitação do Founder)

> "Estou analisando a spec, o que existe sobre profit deve permanecer no código e deixe (Desativado), os itens de mt5 devem ser criados novos e não substituir o profit."
> — Carlos, 2026-05-25

Implicação técnica:

| Componente | Estado em v0.2 |
|---|---|
| `cam/features/profit_integration/` | **PERMANECE** — código intocado, testes continuam rodando |
| Endpoints `/api/v1/profit/*` | **PERMANECEM REGISTRADOS** mas retornam **HTTP 410 Gone** quando flag `PROFIT_INTEGRATION_ENABLED=false` |
| `cam/features/mt5_integration/` | **NOVO** — criado paralelo, sem tocar profit |
| Endpoints `/api/v1/mt5/*` | **NOVOS** — adicionados sem remover endpoints profit |
| `apps/cam-cockpit/ntsl/` | **PERMANECE** — diretório intocado, marcado como DESATIVADO via README |
| `apps/cam-cockpit/mql5/` | **NOVO** — criado paralelo, sem tocar ntsl |

Razões dessa decisão (Founder):

1. **Reversibilidade barata.** Se algo der errado com MT5 em paper trading e for necessário reverter parcialmente, o caminho Profit ainda compila.
2. **Diff cirúrgico.** Adicionar é mais auditável do que substituir + arquivar.
3. **Coerência com DECISION-MEMO §6.** O Founder declarou: "Se o CaM se provar valioso e lucrativo, podemos migrar para profit" — código profit precisa estar disponível para essa possibilidade futura.
4. **Anti-arquivo prematuro.** Mover para `archive/` antes de v0.2 estar provada em produção é decisão irreversível precoce.

### O que esta SPEC **é**

- Adição formal de uma **camada de integração paralela** com MT5 + EAs MQL5 + bridge ZeroMQ.
- Especificação da **nova feature `mt5_integration/`** (não substitui `profit_integration/`).
- Especificação dos **artefatos MQL5** em `apps/cam-cockpit/mql5/` (novo, paralelo a `ntsl/`).
- Especificação da **bridge ZeroMQ** Python ↔ EA.
- Especificação do **mecanismo de desativação** da camada Profit via feature flag.
- Critérios de aceite que estendem (não substituem) os CAs da SPEC v0.1.

### O que esta SPEC **não é**

- **NÃO remove código existente do `profit_integration/`.** Coexistência preservada (revisão v0.2.1).
- **NÃO move `apps/cam-cockpit/ntsl/` para archive.** Diretório permanece, apenas marcado como DESATIVADO.
- Não revoga a SPEC v0.1 nas partes não tocadas (Risk Engine, Journal, Fiscal, Harvest, IA Analyst, frontend etc. permanecem).
- Não implementa código — implementação é PLAN/CODE separados.
- Não decide corretora (essa decisão fica em [`CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) §9, agora filtrada para corretoras com MT5).
- Não toca limite absoluto do Art. 11º (2 WIN / 2 WDO) — intocável.

### Premissa do Founder declarada na DECISION-MEMO §6

> "V1 é MT5 + Linux, v2 podemos extender a capacidade multiplataforma."

Esta SPEC é **v0.2 / V1 do MT5**. Multiplataforma futura é fora de escopo (entra em SPEC v0.3 ou superior quando o Founder decidir).

---

## 2. Escopo

### 2.1 In (faz parte desta SPEC)

| # | Item | Toca código Profit? |
|---|---|---|
| 2.1.1 | **Criar** nova feature `cam/features/mt5_integration/` (paralela a `profit_integration/`) | Não |
| 2.1.2 | **Criar** estrutura `apps/cam-cockpit/mql5/` (experts, indicators, scripts, include) paralela a `ntsl/` | Não |
| 2.1.3 | Implementar bridge ZeroMQ Python ↔ EA MQL5 (read-only inicial; read-write em SPEC v0.3) | Não |
| 2.1.4 | Implementar EA `cam_bridge.mq5` (publicador de ticks/posições/eventos via ZeroMQ) | Não |
| 2.1.5 | Implementar importador de relatório do MT5 (HTML/XML/CSV) **paralelo** ao importador Profit | Não |
| 2.1.6 | Implementar script `scripts/install_wine_mt5.sh` automatizando setup Wine + MT5 + EAs no Ubuntu LTS | Não |
| 2.1.7 | Adicionar variáveis MT5 ao `.env.example` e `cam/_shared/config/` (path Wine, endpoint ZeroMQ) **sem remover** variáveis Profit | Não — adição |
| 2.1.8 | **Adicionar** flag `PROFIT_INTEGRATION_ENABLED: bool = False` no `cam/_shared/config/` (default Desativado) | Adição — não remove |
| 2.1.9 | **Adicionar** middleware/guard que retorna HTTP 410 Gone em endpoints `/api/v1/profit/*` quando flag desativada — código de implementação intocado | Toca apenas o router profit (adição de guard) |
| 2.1.10 | **Adicionar** novos endpoints `/api/v1/mt5/*` sem remover os endpoints `/api/v1/profit/*` existentes | Não |
| 2.1.11 | Atualizar frontend `Configurações` com seção "Bridge MT5" (status conexão, heartbeat, latência, restart, path MT5). Seção Profit pode permanecer com badge "DESATIVADO" | Não |
| 2.1.12 | Atualizar `RUNBOOK-INCIDENTE-TECNICO.md` adicionando comandos MT5/Wine/ZeroMQ (sem remover cenários Profit) | Não — adição |
| 2.1.13 | Atualizar `MAPPING-CONSTITUICAO-RISK-ENGINE.md` adicionando referências MQL5 ao lado das NTSL (NTSL marcadas como DESATIVADO) | Não — adição |
| 2.1.14 | Adicionar `mt5_integration` ao import-linter como nova feature isolada (sem remover `profit_integration` do contrato) | Não — adição |
| 2.1.15 | **Adicionar** `apps/cam-cockpit/ntsl/README.md` com banner "DESATIVADO em 2026-05-25 — ver SPEC v0.2 §2.1" (NÃO mover diretório) | Apenas README |
| 2.1.16 | **Adicionar** `cam/features/profit_integration/README.md` (ou nota no existente) com banner "DESATIVADO" + instrução de reativação se necessário | Apenas README |
| 2.1.17 | Tests existentes de `profit_integration` **PERMANECEM rodando** — validam que feature continua compilando. Adicionar testes específicos confirmando que endpoints retornam 410 quando flag desativada | Adição — testes |

### 2.2 Out (NÃO faz parte desta SPEC — fica para SPEC v0.3+ ou nunca)

**Itens fora de escopo de v0.2 (futura SPEC):**

- ❌ EA `cam_risk_mirror.mq5` — risk engine espelhado em MQL5 (segunda linha). Fica para v0.3, após v0.2 estar estável.
- ❌ Bridge **read-write** (envio de ordens via EA). Fica para v0.3 (sai junto do risk_mirror).
- ❌ MetaApi como alternativa SaaS. Plano B documentado, não implementado.
- ❌ Migração para VPS Windows. Plano B documentado, ativado por gatilho objetivo (DECISION-MEMO §7 G-B1).
- ❌ Cross-broker / Forex / Crypto. Capacidade técnica do MT5, mas fora do escopo CaM v1.
- ❌ Strategy Tester nativo do MT5 como complemento ao backtest engine Python — explorar em v0.3.

**Itens explicitamente NÃO realizados (princípio de coexistência — revisão v0.2.1):**

- ❌ **Remover `cam/features/profit_integration/`** — código permanece intocado.
- ❌ **Mover `apps/cam-cockpit/ntsl/` para `archive/`** — diretório permanece, marcado DESATIVADO via README.
- ❌ **Renomear endpoints `/api/v1/profit/*`** — endpoints permanecem registrados (retornam 410 quando flag off).
- ❌ **Excluir testes de `profit_integration`** — testes continuam rodando, garantem que feature compila.
- ❌ **Excluir migrations relacionadas a Profit** — schemas DB preservados.

### 2.3 Later (entra em SPEC futura)

- 🔜 EA `cam_risk_mirror.mq5` — SPEC v0.3 obrigatória antes da Fase 4 (operação real automatizada).
- 🔜 Bridge read-write — SPEC v0.3 junto do risk_mirror.
- 🔜 Multi-plataforma (cross-broker) — declarado pelo Founder como "v2" no DECISION-MEMO §6.
- 🔜 Package oficial `MetaTrader5` Python (se opção C / VPS Windows for ativada) — SPEC contingencial.

---

## 3. Regras (R) — extensão da SPEC v0.1

> Numeração inicia em **R12** para não colidir com SPEC v0.1 (que vai até R11). Cada regra é **non-negociável** salvo emenda formal.

### R12 — Bridge ZeroMQ é a integração padrão Python ↔ MT5

R12.01 — A bridge **DEVE** usar ZeroMQ (lib Python `pyzmq` + lib MQL5 `dwx-zeromq-connector` ou equivalente open source).

R12.02 — A bridge **DEVE** suportar minimamente os padrões: `PUB/SUB` (EA publica ticks/eventos) e `REQ/REP` (Python solicita estado, EA responde).

R12.03 — A bridge **NÃO PODE** enviar ordens em v0.2 (read-only). Tentativa de envio em código deve falhar em compilação via marcador de tipo / asserção.

R12.04 — Heartbeat obrigatório a cada **1 segundo**. Se Python não receber heartbeat por **> 3 segundos**, marca bridge como **OFFLINE** e:
- bloqueia novas validações no Risk Engine que dependam de tick fresco;
- publica evento `MT5BridgeOffline` no EventBus;
- envia alerta Telegram (`notifications` handler).

R12.05 — A bridge **DEVE** funcionar igualmente bem com EA rodando em **Wine local** OU em **VPS Windows remoto** — diferença é apenas o IP/porta de configuração (`MT5_BRIDGE_HOST`, `MT5_BRIDGE_PUB_PORT`, `MT5_BRIDGE_REQ_PORT` no `.env`).

R12.06 — Credenciais MT5 (login da corretora, server name, senha) **NÃO** entram em código. Vivem em `.env` + Wine `terminal.ini` local, conforme RUNBOOK §4.

### R13 — Estrutura `apps/cam-cockpit/mql5/` coexiste paralela a `ntsl/`

R13.01 — A estrutura **DEVE** ser:
```
apps/cam-cockpit/mql5/
├── experts/
│   ├── cam_bridge.mq5          # EA principal — bridge ZeroMQ read-only (v0.2)
│   └── cam_risk_mirror.mq5     # PLACEHOLDER — implementação real em v0.3
├── indicators/                 # vazio em v0.2
├── scripts/                    # utilitários MQL5 ad-hoc
├── include/                    # bibliotecas .mqh compartilhadas (ZMQ wrapper, etc.)
└── README.md                   # contrato dos EAs + setup instructions
```

R13.02 — O diretório `apps/cam-cockpit/ntsl/` (criado em T-A01 da SPEC v0.1) **DEVE PERMANECER** no local original — **NÃO** mover para `archive/`. Adicionar `apps/cam-cockpit/ntsl/README.md` com banner:

```markdown
# ntsl/ — DESATIVADO em 2026-05-25

> Esta pasta está marcada como **DESATIVADA** após adoção de MT5 + MQL5
> conforme SPEC v0.2 e DECISION-MEMO. Código preservado para referência
> e reversibilidade futura. Estratégias ativas vivem em `apps/cam-cockpit/mql5/`.
>
> Reativação: editar este README e remover o banner, mediante decisão formal
> registrada (ver PROTOCOLO-EMENDA-CONSTITUCIONAL.md).
```

R13.03 — EAs **DEVEM** ser versionados em Git. Não há binários compilados commitados (.ex5 fica em `.gitignore`).

R13.04 — Cada EA **DEVE** ter cabeçalho de documentação MQL5 com:
- nome e versão
- artigos constitucionais que aplica (ou referencia)
- canais ZeroMQ que publica/consome
- pré-condições de operação (conta demo vs real, restrição de horário, etc.)

### R14 — EA `cam_bridge.mq5` é read-only em v0.2

R14.01 — `cam_bridge.mq5` **DEVE** publicar via ZeroMQ PUB:
- ticks (canal `mt5.tick`) — preço, volume, ask, bid, timestamp
- posições abertas (canal `mt5.position`) — ativo, contratos, preço médio, P&L atual
- fills/execuções (canal `mt5.fill`) — quando o operador opera manualmente no MT5
- heartbeat (canal `mt5.heartbeat`) — 1 mensagem/segundo

R14.02 — `cam_bridge.mq5` **DEVE** responder via ZeroMQ REP a comandos read-only:
- `GET_STATE` — retorna estado da conta (saldo, equity, margem)
- `GET_POSITIONS` — retorna lista de posições abertas
- `GET_SYMBOL_INFO` — retorna metadata de um símbolo (tick size, lot size, etc.)
- `PING` — retorna `PONG` para liveness check (extra ao heartbeat)

R14.03 — `cam_bridge.mq5` **NÃO PODE** ter código que envie ordem (`OrderSend`, `PositionOpen` etc.). Validação por code review obrigatória (Kevin em CODE).

R14.04 — Toda mensagem publicada **DEVE** ter campo `ts_unix` (timestamp Unix em ms) para reconciliação com banco.

### R15 — Importador de relatório do MT5

R15.01 — O importador **DEVE** aceitar:
- HTML do MT5 (Reports → Save as → HTML)
- XML do MT5 (Reports → Save as → XML)
- CSV do MT5 (alguns brokers exportam direto)

R15.02 — O importador **DEVE** detectar duplicatas por hash da operação (composição: timestamp + ativo + direção + contratos + preço entrada + preço saída). Mesma lógica do antigo Profit importer (SPEC v0.1 R6.03).

R15.03 — Cada operação importada **DEVE** criar um `JournalEntry` via `journal/service.py` com `source = "MT5_IMPORT"`.

R15.04 — Endpoint REST: `POST /api/v1/mt5/import-report` aceitando arquivo via multipart/form-data, retornando `ImportResult` (imported, duplicates, errors).

### R16 — Bridge offline = modo degradado seguro (Art. 19º)

R16.01 — Quando bridge está OFFLINE (sem heartbeat há > 3s):
- Risk Engine **NÃO PODE** validar candidatos com dependência de tick fresco;
- endpoints que dependem de bridge retornam **HTTP 503** com payload `{"error":"MT5_BRIDGE_OFFLINE", "since":"<timestamp>"}`;
- frontend exibe banner persistente vermelho (similar ao kill switch banner);
- alerta Telegram disparado uma vez (com cooldown de 5min para evitar flood).

R16.02 — Reconexão automática **DEVE** ser tentada a cada 2 segundos enquanto offline. Recuperação dispara evento `MT5BridgeOnline` e remove o banner UI.

R16.03 — Posição aberta detectada via última publicação de `mt5.position` **antes** do offline **DEVE** continuar visível no cockpit com flag `stale: true`. Carlos deve ser instruído pelo RUNBOOK §2.2 a confirmar a posição direto no MT5 nativo.

### R17 — Configurações MT5 no frontend

R17.01 — A página `/settings` **DEVE** ganhar seção "Bridge MT5" exibindo:
- Status: ONLINE | OFFLINE | RECONNECTING (chip colorido)
- Última heartbeat: timestamp + duração ("há 0.8s")
- Latência média da REQ/REP (ms)
- Path do MT5 detectado (`~/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe` ou VPS host)
- Botão "Reiniciar bridge" (restart do processo Wine ou apenas reset socket — depende do modo)
- Janela do MT5 aberta vs minimizada (info-only, não-acionável via UI por questão de Wine X11)

R17.02 — A página `/settings` **NÃO PODE** expor login/senha MT5 — apenas o booleano "MT5 configurado". Credenciais ficam em `.env` + Wine terminal.ini, fora do alcance do frontend.

### R18 — Risk Engine permanece intocado pela camada de execução

R18.01 — `cam/_shared/risk/` **NÃO MUDA** por causa do MT5. Continua sendo Pure Python, Zero I/O, todas as regras dos Arts. 11º-20º intactas.

R18.02 — A nova feature `mt5_integration/` **DEVE** consumir `validate()` do Risk Engine antes de qualquer ação que toque ordem (mesmo que essa ação seja apenas registrar intenção no journal).

R18.03 — Quando o EA `cam_risk_mirror.mq5` for implementado (v0.3), as regras MQL5 **DEVEM** espelhar 1:1 os validators críticos do Risk Engine Python — testes de paridade obrigatórios. Em v0.2 essa paridade ainda não existe (apenas Python valida).

### R19 — Documentação obrigatória

R19.01 — A feature `mt5_integration/` **DEVE** ter `README.md` no padrão das outras features (propósito, I/O, eventos, artigos constitucionais aplicáveis, anti-padrões).

R19.02 — O diretório `apps/cam-cockpit/mql5/` **DEVE** ter `README.md` próprio com:
- como compilar EA no MT5 (passos manuais via MetaEditor)
- como instalar o EA no MT5 (drag-and-drop em `MQL5/Experts/`)
- estrutura de cada EA + canais ZeroMQ que opera
- como debugar (logs do MT5 + logs do EA)

R19.03 — O script `scripts/install_wine_mt5.sh` **DEVE** ter cabeçalho com pré-requisitos, comportamento idempotente, e flags `--skip-wine`, `--skip-mt5` para reuso parcial.

### R20 — Coexistência Profit (Desativado) ∥ MT5 (Ativo)

R20.01 — O código de `cam/features/profit_integration/` **NÃO PODE** ser removido, renomeado, movido ou refatorado nesta SPEC. Permanece intocado em sua localização atual.

R20.02 — Os endpoints `/api/v1/profit/*` **PERMANECEM REGISTRADOS** no `cam/api/main.py`. Quando a flag `PROFIT_INTEGRATION_ENABLED=false` (default), cada endpoint do router profit **DEVE** retornar:

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": "PROFIT_INTEGRATION_DISABLED",
  "message": "Integração Profit está desativada desde 2026-05-25 (SPEC v0.2). Use endpoints /api/v1/mt5/*.",
  "reactivation_doc": "/project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md §2.1.8",
  "since": "2026-05-25"
}
```

Implementação recomendada (CODE): dependência FastAPI `Depends(check_profit_enabled)` aplicada no router profit, que levanta `HTTPException(410, ...)` se a flag estiver `False`.

R20.03 — Endpoints `/api/v1/mt5/*` são **novos**, **adicionais**. Tabela de **coexistência** (não migração):

| Endpoint Profit (existente) | Endpoint MT5 (novo) | Comportamento em v0.2 |
|---|---|---|
| `POST /api/v1/profit/validate-intention` | `POST /api/v1/mt5/validate-intention` | Profit retorna 410; MT5 funcional |
| `POST /api/v1/journal/import-csv` (Profit CSV) | `POST /api/v1/mt5/import-report` (HTML/XML/CSV MT5) | Profit CSV retorna 410; MT5 import funcional |
| `GET /api/v1/profit/reconciliation/{date}` | `GET /api/v1/mt5/reconciliation/{date}` | Profit retorna 410; MT5 funcional |

R20.04 — Schemas DB **PERMANECEM intactos**. Coluna `source` em `cam_journal_entries` ganha **novos valores aceitos** sem remover os anteriores:

| Valor de `source` | Origem | Status |
|---|---|---|
| `MANUAL` | Entrada manual via UI | Ativo |
| `CSV_IMPORT` (legado Profit) | Importação CSV Profit | Aceito (legado — não recebe novas entradas com flag off) |
| `MT5_IMPORT` | Importação relatório MT5 (novo) | Ativo |
| `MT5_BRIDGE` | Fill detectado via bridge ZeroMQ (futuro v0.3) | Reservado |

R20.05 — Tech debts da v0.1 que tocam `profit_integration` ficam **congelados em "Não-aplicável (feature desativada)"**:

- **TD-007** (validate-intention Profit sem RiskContext real) → **CONGELADO**. Novo TD equivalente para MT5 em `mt5_integration`.
- **TD-008** (import-csv Profit sem DB) → **CONGELADO**. Novo TD para `import-report` MT5.
- **TD-009** (reconciliação Profit sem DB) → **CONGELADO**. Novo TD para reconciliação MT5.

R20.06 — Tests de `cam/features/profit_integration/tests/` **PERMANECEM** rodando — garantem que o código Profit continua compilando. Adicionar tests novos que validem:
- Endpoints `/api/v1/profit/*` retornam **410** quando flag desativada.
- Endpoints `/api/v1/profit/*` voltam a funcionar normalmente quando flag manualmente reativada (`PROFIT_INTEGRATION_ENABLED=true` no `.env`).

R20.07 — Reativação da camada Profit no futuro **NÃO** exige código novo. Basta editar `.env`:

```bash
PROFIT_INTEGRATION_ENABLED=true
```

E reiniciar o backend. Reativação só pode ser feita pelo Founder em estado frio com motivação registrada (similar a alteração de POV — Art. 39º por analogia).

### R21 — Princípio de Coexistência (revisão v0.2.1)

R21.01 — **Toda nova camada de integração adicionada ao CaM deve ser CRIADA paralelamente, nunca SUBSTITUIR código existente em uma única SPEC.** Removar/arquivar fica para SPEC dedicada após período de prova em produção.

R21.02 — **Desativação por feature flag é o mecanismo padrão.** Implementa-se um guard no router e marca-se documentação — não se remove código.

R21.03 — Quando duas implementações de uma mesma categoria (ex: duas integrações broker) coexistem, **apenas uma pode estar ATIVA por vez**. Ativação simultânea de `PROFIT_INTEGRATION_ENABLED=true` E `MT5_INTEGRATION_ENABLED=true` (futuro) **DEVE** falhar no startup do backend com erro claro.

R21.04 — O ledger de ativação/desativação de features fica registrado em `apps/cam-cockpit/FEATURE-FLAGS-LEDGER.md` (a ser criado em CODE). Cada toggle entra como linha com data, motivação, aprovador.

R21.05 — Em audit log (`cam/_shared/audit/`), eventos de chamada a endpoint desativado **DEVEM** ser registrados como `event_type=DISABLED_ENDPOINT_ATTEMPT` para rastrear código cliente que ainda tenta chamar feature off.

---

## 4. Contratos

### 4.1 Schemas Pydantic principais (`cam/features/mt5_integration/schemas.py`)

```python
class MT5Tick(BaseModel):
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    volume: int
    ts_unix_ms: int

class MT5Position(BaseModel):
    symbol: str
    contracts: int
    direction: Literal["LONG", "SHORT"]
    entry_price: Decimal
    current_price: Decimal
    pnl_gross: Decimal
    pnl_net: Decimal              # Art. 25º — sempre presente
    opened_at: datetime

class MT5BridgeStatus(BaseModel):
    state: Literal["ONLINE", "OFFLINE", "RECONNECTING"]
    last_heartbeat_at: datetime | None
    last_heartbeat_age_ms: int | None
    avg_latency_ms: float | None
    host: str
    pub_port: int
    req_port: int
    mt5_path: str | None

class ImportReportRequest(BaseModel):
    format: Literal["html", "xml", "csv"]
    # arquivo via multipart, não no JSON body

class ValidateIntentionRequest(BaseModel):
    asset: Literal["WIN", "WDO"]
    direction: Literal["LONG", "SHORT"]
    contracts: int                # ≤ 2 (Art. 11º enforced no Risk Engine)
    intended_stop_loss_points: Decimal

class ValidateIntentionResponse(BaseModel):
    approved: bool
    reason: str | None
    validator: str | None         # qual validator bloqueou, se Rejected
```

### 4.2 Endpoints HTTP novos (adicionais, sem remover Profit)

| Método | Endpoint | Body | Response |
|---|---|---|---|
| `GET` | `/api/v1/mt5/bridge/status` | — | `MT5BridgeStatus` |
| `POST` | `/api/v1/mt5/bridge/restart` | `{"confirm": true}` | `{"status": "restarting"}` |
| `GET` | `/api/v1/mt5/positions` | — | `list[MT5Position]` |
| `POST` | `/api/v1/mt5/validate-intention` | `ValidateIntentionRequest` | `ValidateIntentionResponse` |
| `POST` | `/api/v1/mt5/import-report` | `multipart/form-data` (file) | `ImportResult` |
| `GET` | `/api/v1/mt5/reconciliation/{date}` | — | `ReconciliationReport` |
| `WS` | `/api/v1/mt5/ws/ticks` | — | stream de `MT5Tick` |

### 4.3 Endpoints Profit existentes (estado em v0.2 com flag default)

| Método | Endpoint | Comportamento quando `PROFIT_INTEGRATION_ENABLED=false` (default) |
|---|---|---|
| `POST` | `/api/v1/profit/validate-intention` | **410 Gone** + payload R20.02 |
| `POST` | `/api/v1/journal/import-csv` | **410 Gone** + payload R20.02 |
| `GET` | `/api/v1/profit/reconciliation/{date}` | **410 Gone** + payload R20.02 |

> Quando `PROFIT_INTEGRATION_ENABLED=true` (reativação manual via `.env`), todos os endpoints voltam ao comportamento original da SPEC v0.1.

### 4.3 Eventos publicados no EventBus

| Evento | Origem | Consumidores prováveis |
|---|---|---|
| `MT5TickReceived` | `mt5_integration` | (futuro) `strategies`, `paper_trading` |
| `MT5PositionChanged` | `mt5_integration` | `journal`, `risk_console` |
| `MT5FillDetected` | `mt5_integration` | `journal` (gera entrada automática), `notifications` |
| `MT5BridgeOffline` | `mt5_integration` | `notifications` (alerta Telegram), `risk_console` (banner UI) |
| `MT5BridgeOnline` | `mt5_integration` | `notifications` (alerta), `risk_console` (remove banner) |

---

## 5. Critérios de aceite (CA) — extensão da SPEC v0.1

> Numeração inicia em **CA12** para não colidir com CAs da SPEC v0.1.

### CA12 — Bridge ZeroMQ funcional

- **CA12.1:** EA `cam_bridge.mq5` compila no MetaEditor sem warnings.
- **CA12.2:** Com MT5 rodando em conta demo + EA carregado, Python recebe **pelo menos 100 ticks consecutivos** em janela de 60 segundos durante pregão B3.
- **CA12.3:** Heartbeat recebido com intervalo médio entre 800ms e 1200ms (target: 1s).
- **CA12.4:** Comando REQ `PING` retorna `PONG` com latência ≤ 50ms em rede local.
- **CA12.5:** `GET /api/v1/mt5/bridge/status` retorna estado consistente com observação direta dos logs do EA.

### CA13 — Offline graceful (Art. 19º)

- **CA13.1:** Matar o processo Wine MT5 enquanto cockpit está rodando → em ≤ 5s o status muda para OFFLINE.
- **CA13.2:** Após OFFLINE, endpoints dependentes (validate-intention, positions, ticks) retornam HTTP 503.
- **CA13.3:** Frontend exibe banner vermelho persistente.
- **CA13.4:** Alerta Telegram disparado **uma vez** (com cooldown).
- **CA13.5:** Reabrir MT5 + EA → status volta a ONLINE em ≤ 5s, banner UI removido, alerta Telegram de retorno enviado.

### CA14 — Importador de relatório MT5

- **CA14.1:** Importar relatório HTML do MT5 com 50 operações → 50 `JournalEntry` criados com `source = "MT5_IMPORT"`.
- **CA14.2:** Reimportar o mesmo arquivo → 0 duplicatas registradas, 50 ignoradas por hash.
- **CA14.3:** Importar arquivo malformado → resposta `400` com mensagem clara, nenhuma entry criada.
- **CA14.4:** Conciliação entre operações importadas e operações manuais do journal exibe pares prováveis (match por timestamp + ativo + direção).

### CA15 — Bridge é read-only em v0.2

- **CA15.1:** Code review (Kevin obrigatório) confirma: EA `cam_bridge.mq5` **não** contém chamadas `OrderSend`, `OrderClose`, `PositionOpen`, `PositionClose`, `OrderModify`.
- **CA15.2:** Suite de testes Python confirma: módulo `cam/features/mt5_integration/bridge.py` não expõe método `send_order` (atributo ausente).
- **CA15.3:** Comando REQ não-listado em R14.02 → EA responde `{"error":"UNAUTHORIZED_COMMAND","cmd":"<cmd>"}` e loga warning.

### CA16 — Setup automatizado Wine + MT5

- **CA16.1:** Em Ubuntu 24.04+ LTS limpo, `bash scripts/install_wine_mt5.sh` finaliza com exit code 0.
- **CA16.2:** Após `install_wine_mt5.sh`, comando `wine "$HOME/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"` abre a janela do MT5.
- **CA16.3:** EA `cam_bridge.mq5` aparece na lista de Expert Advisors do MT5 após o script.
- **CA16.4:** Script é idempotente — segundo run não reinstala Wine nem MT5; apenas verifica e reporta status.

### CA17 — Não regressão na arquitetura (ADR-013)

- **CA17.1:** `lint-imports` continua passando após v0.2 — `mt5_integration` listada como feature isolada.
- **CA17.2:** `cam/_shared/risk/` continua sem imports de I/O (Pure Python preservado).
- **CA17.3:** Cobertura global de testes do backend não cai abaixo de **375 testes passando** (cobertura atual pré-v0.2 = 379).
- **CA17.4:** UI continua exibindo P&L líquido em toda tela (Art. 25º preservado — `MT5Position.pnl_net` sempre presente).

### CA18 — Documentação atualizada

- **CA18.1:** `MAPPING-CONSTITUICAO-RISK-ENGINE.md` atualizado — referências a MQL5 **adicionadas ao lado** das NTSL (NTSL marcadas como DESATIVADO, não removidas).
- **CA18.2:** `RUNBOOK-INCIDENTE-TECNICO.md` §2.2 atualizado **adicionando** comandos Wine + MT5 + ZeroMQ (cenários Profit permanecem documentados).
- **CA18.3:** `CLAUDE_MEMORY.MD` atualizado refletindo decisão MT5 (já feito antes desta SPEC).
- **CA18.4:** `apps/cam-cockpit/mql5/README.md` documenta como compilar, instalar e debugar EAs.
- **CA18.5:** `apps/cam-cockpit/ntsl/README.md` criado com banner "DESATIVADO em 2026-05-25" (R13.02).
- **CA18.6:** `cam/features/profit_integration/README.md` criado/atualizado com banner "DESATIVADO" + instrução de reativação (R20.07).

### CA19 — Desativação Profit funcional e reversível

- **CA19.1:** Com `PROFIT_INTEGRATION_ENABLED=false` (default), `POST /api/v1/profit/validate-intention` retorna **HTTP 410** com payload no formato R20.02.
- **CA19.2:** Mesma resposta para `POST /api/v1/journal/import-csv` e `GET /api/v1/profit/reconciliation/{date}`.
- **CA19.3:** Audit log registra cada tentativa de chamada como `event_type=DISABLED_ENDPOINT_ATTEMPT` com endpoint, IP, timestamp.
- **CA19.4:** Alterando `.env` para `PROFIT_INTEGRATION_ENABLED=true` + restart do backend → todos os endpoints `/api/v1/profit/*` voltam a responder no comportamento original da SPEC v0.1 (sem mudança de código).
- **CA19.5:** Frontend painel `Configurações` exibe chip "Profit Integration: DESATIVADA" + chip "MT5 Bridge: ONLINE" lado a lado.

### CA20 — Coexistência preservada (princípio v0.2.1)

- **CA20.1:** `cam/features/profit_integration/` continua compilando — `python -c "import cam.features.profit_integration"` sem erro.
- **CA20.2:** Testes existentes em `cam/features/profit_integration/tests/` continuam passando (cobertura intacta).
- **CA20.3:** Diretório `apps/cam-cockpit/ntsl/` continua existindo no filesystem (verificável via `test -d apps/cam-cockpit/ntsl`).
- **CA20.4:** `import-linter` reconhece **ambas** features como isoladas: `profit_integration` e `mt5_integration` aparecem na lista `independence` do `pyproject.toml`.
- **CA20.5:** Backend startup falha graciosamente se Founder ativar simultaneamente `PROFIT_INTEGRATION_ENABLED=true` E `MT5_INTEGRATION_ENABLED=true` — mensagem clara identificando R21.03 violada.
- **CA20.6:** Schemas DB preservados — migration que adiciona novos valores ao enum `source` (`MT5_IMPORT`, `MT5_BRIDGE`) **não remove** valores antigos (`CSV_IMPORT`).

---

## 6. Classificação P/M/G

| Campo | Valor |
|---|---|
| **Classe** | **G (Grande)** |
| **Rationale** | Substituição de feature inteira (`profit_integration` → `mt5_integration`); criação de estrutura nova `mql5/` com EA principal; bridge de rede ZeroMQ com novos contratos read-only; script de setup automatizado de ambiente Wine/MT5; importador novo (HTML/XML); atualização de 3 documentos governamentais. Múltiplas frentes técnicas (Python + MQL5 + ZeroMQ + script Bash + frontend); decomposição em TASKs no PLAN é mandatória. |
| **Albert** | G confirmada |
| **Nico (PLAN futuro)** | Loop com Albert sobre P/M/G é livre — pode reclassificar |

---

## 7. Marcadores SEC / QA-SEC (Kevin)

### 7.1 `sec` marker — VERDADEIRO

Razões:

- **Bridge de rede:** socket TCP exposto localmente (mesmo `localhost`) é superfície sensível — autenticação, escopo de comandos, validação de payload.
- **Credenciais MT5:** login/senha da corretora vivem em `.env` + Wine terminal.ini — exposição acidental tem impacto financeiro real.
- **Conta de simulação vs real:** EA `cam_bridge.mq5` precisa distinguir corretamente; ativar EA em conta real por engano em v0.2 (sem risk_mirror) é violação direta do Art. 15º.

**Mitigações exigidas (CODE):**

- Bridge ZeroMQ bind em `127.0.0.1` apenas (nunca `0.0.0.0`) em v0.2 (local).
- EA verifica `AccountInfoString(ACCOUNT_NAME)` contém "DEMO" ou usa magic number diferente conforme conta — log em vermelho se conta real detectada em v0.2.
- `.env` listado em `.gitignore` + pre-commit hook anti-secrets (já existente — T-A10).
- Credenciais MT5 nunca aparecem em logs estruturados (`cam/_shared/audit/`).

### 7.2 `qa-sec` marker — VERDADEIRO

Razões:

- Bridge ZeroMQ é caminho que **pode** evoluir para read-write (v0.3) — testes em v0.2 devem garantir que **read-write não funcione mesmo se tentado**.
- EA MQL5 sem cobertura de testes automatizados (limitação técnica do MQL5) → cobertura compensada por **paridade Python ↔ MQL5** (a ser introduzida em v0.3 com risk_mirror).
- Importador HTML do MT5 deve resistir a relatórios malformados, encoding incorreto, tags HTML injetadas (parsing seguro).

**Cobertura QA-SEC mandatória:**

- Testes Python verificando que `mt5_integration` não expõe `send_order` (assert atributo ausente).
- Testes negativos do importador HTML: arquivos corrompidos, HTML com `<script>`, dados truncados.
- Validation property-based (Hypothesis): bridge nunca panic em payload inesperado.

---

## 8. Tech debts conhecidos (a registrar quando entrar em CODE)

Apenas pré-listados para conscientização. Cada TD vira entrada em `TECH-DEBT.md` quando confirmado em CODE.

| ID provisório | Descrição | Severidade |
|---|---|---|
| TD-v0.2-01 | Bridge ZeroMQ sem autenticação (apenas confiança em localhost binding) | Médio — aceitável em v0.2; revisitar em v0.3 |
| TD-v0.2-02 | Sem testes automatizados do EA MQL5 (limitação da plataforma) | Médio — compensar com paridade quando risk_mirror existir |
| TD-v0.2-03 | Importador HTML depende de estrutura interna do relatório MT5 (mudança de versão pode quebrar) | Baixo — versionamento de parser + teste com sample de cada major version do MT5 |
| TD-v0.2-04 | `profit_integration/` continua compilando e ocupando espaço no test suite mesmo desativada (custo de manutenção sem benefício imediato) | Baixo — preço aceito da reversibilidade (R21); reavaliar em SPEC v0.3 ou quando MT5 estiver em Fase 2+ por > 90 dias |
| TD-v0.2-05 | Wine pode glitchar com update do MT5; runbook prevê migração para VPS, mas não há automação | Médio — manual via DECISION-MEMO §7 G-B1 |
| TD-v0.2-06 | Reativação simultânea de Profit + MT5 protegida apenas por verificação de startup — sem UI clara para Founder ver flags ativas | Baixo — adicionar painel em `/settings` listando todas as feature flags em v0.3 |
| TD-v0.2-07 | Audit log de `DISABLED_ENDPOINT_ATTEMPT` (R21.05) cresce indefinidamente — sem política de retenção/rotação específica | Baixo — alinhado com retenção geral de audit logs (TD-H05 família) |

---

## 9. Riscos identificados

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Wine + MT5 instável em pregão | Média | Alto | Validação 4 semanas conta demo antes de Fase 2; migração documentada para VPS Windows como plano B (DECISION-MEMO ADR-014-LINUX) |
| Corretora brasileira não permitir EA em MT5 para PF | Média | Alto | Validar antes da Fase 1 via CORRETORA-EVAL.md §6 (script de contato) |
| MetaQuotes encerrar suporte oficial Linux/Wine | Baixa | Médio | DECISION-MEMO §7 G-B3 reabre decisão automaticamente |
| Bridge ZeroMQ perder conexão silenciosamente | Média | Alto | R12.04 heartbeat obrigatório + R16 modo degradado seguro |
| Conta real ativada por engano em v0.2 (sem risk_mirror) | Baixa | **Crítico** (Art. 15º) | §7.1 mitigação: EA verifica "DEMO" no nome da conta; magic number diferente; log vermelho |
| EA falhar de compilar em alguma versão futura do MT5 | Baixa | Médio | Versionamento explícito da versão do MT5 testada; pin documentado |
| Importador HTML quebrar em update do MT5 | Média | Baixo | Suite de regressão com sample por versão; aceitar tech debt TD-v0.2-03 |

---

## 10. Delta no DVP

Esta SPEC **não altera direção estratégica** do DVP — apenas concretiza a camada de integração que o DVP já previa de forma agnóstica de plataforma. **Nenhuma atualização no DVP.md é mandatória** por causa desta SPEC.

A única adição opcional ao DVP é uma nota sobre "v2 multi-plataforma" conforme declaração do Founder na DECISION-MEMO §6 — fica como pendência opcional para Denis em SDOC futura.

---

## 11. Dependências externas

| Dependência | Necessária para | Status |
|---|---|---|
| Wine (winehq-stable) instalado em Ubuntu | T-MT5-01 (Bridge), CA12, CA16 | A instalar via `scripts/install_wine_mt5.sh` |
| MetaTrader 5 baixado da MetaQuotes | CA12, CA16 | Download oficial: `https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe` |
| Conta demo MT5 ativa em corretora brasileira | CA12.2, CA14 | Bloqueia até CORRETORA-EVAL §9 fechar (Founder vincular corretora) |
| `pyzmq` instalado | Bridge Python | Adicionar ao `pyproject.toml` dependências |
| dwx-zeromq-connector (ou equivalente) MQL5 | EA | Open source — incluir no `apps/cam-cockpit/mql5/include/` |
| `pyzmq` headers/libs do sistema | `pip install pyzmq` | apt: `libzmq3-dev` |

---

## 12. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior aprova a SPEC v0.2.1 — Enquadramento MT5
    (com Princípio de Coexistência) como ADIÇÃO de camada de integração ao
    CaM Cockpit, conforme decisão registrada em DECISION-MEMO §6.

    Carlos reconhece que:

    a) Esta SPEC é EXTENSÃO da SPEC v0.1 — não revoga regras CA1-CA11 nem
       contratos não-relacionados a `profit_integration`.

    b) Princípio de Coexistência v0.2.1: código `profit_integration/` PERMANECE
       no repositório, marcado DESATIVADO via feature flag
       `PROFIT_INTEGRATION_ENABLED=false`. Endpoints retornam 410 Gone.
       Reativação futura é manual via `.env`, sem mudança de código.

    c) Diretório `apps/cam-cockpit/ntsl/` PERMANECE no filesystem com README
       de DESATIVADO — NÃO movido para archive/.

    d) Marca `sec=true` e `qa-sec=true` — Kevin envolvido em CODE e QA.

    e) v0.2 é READ-ONLY (CA15). Read-write fica para SPEC v0.3 junto com
       cam_risk_mirror.mq5 (Art. 15º — segunda linha de defesa).

    f) A liberação para PLAN (T-MT5-NN TASKs) requer aprovação separada
       (letscode) — esta SPEC apenas autoriza a especificação como base.

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — Arts. 6º, 8º, 11º, 15º, 18º, 19º, 25º, 31º, 35º
- [`/project/DECISION-MEMO-LINUX-OR-WINDOWS.md`](../DECISION-MEMO-LINUX-OR-WINDOWS.md) §6 — origem desta SPEC
- [`/project/STACK-CAM-OFICIAL.md`](../STACK-CAM-OFICIAL.md) — stack canônica (atual = Linux+MT5)
- [`/project/CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) §6 — script de contato + §9 (a criar) corretora vinculada com MT5
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — parâmetros operacionais que o Risk Engine continua aplicando
- [`/project/strategies/EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) — S1 que vai ser executada via MT5 no futuro
- [`/project/runbooks/RUNBOOK-INCIDENTE-TECNICO.md`](../runbooks/RUNBOOK-INCIDENTE-TECNICO.md) §2.2 — comandos MT5/Wine/ZeroMQ a serem incluídos
- [`/project/MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../MAPPING-CONSTITUICAO-RISK-ENGINE.md) — atualizar referências NTSL→MQL5
- [`/project/GATE-FASE-0-PARA-1.md`](../GATE-FASE-0-PARA-1.md) — esta SPEC fecha o item G.3 (stack canônica decidida)
- [`/project/cam-cockpit/SPEC.md`](./SPEC.md) — SPEC v0.1 que esta v0.2 estende
- [`/project/cam-cockpit/PLAN.md`](./PLAN.md) — Bloco D (integração) será revisado quando esta SPEC virar PLAN v0.2
- [`/apps/cam-cockpit/`](../../apps/cam-cockpit/) — estrutura física (backend + frontend + mql5 + scripts)
- [`/apps/cam-cockpit/TECH-DEBT.md`](../TECH-DEBT.md) — TD-007, TD-008, TD-009 (revisar escopo para MT5)

---

> **Princípio operacional desta SPEC:**
>
> Albert escreve o contrato. Kevin protege a superfície. O Founder libera.
>
> v0.2 é read-only por design. **Risk Engine continua sendo o único caminho de validação de ordem.** A bridge MT5 publica e responde — nunca executa.

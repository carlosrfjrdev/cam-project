# mt5_integration — Integração com MetaTrader 5 (bridge ZeroMQ)

> **Status:** ATIVA (SPEC v0.2.1)
> **Coexiste com:** `cam/features/profit_integration/` (DESATIVADA por flag — ver SPEC v0.2 §R20)

## Proposito

Camada de integracao do CaM com a plataforma MetaTrader 5 via bridge ZeroMQ
publish/subscribe + request/reply. **Read-only em v0.2** — bridge nao envia
ordens (CA15). Read-write fica para SPEC v0.3 junto com `cam_risk_mirror.mq5`.

## I/O

### Endpoints HTTP

- `GET /api/v1/mt5/bridge/status` — status da bridge (ONLINE/OFFLINE/RECONNECTING)
- `POST /api/v1/mt5/bridge/restart` — restart do socket (requer `{"confirm": true}`)
- `GET /api/v1/mt5/positions` — posicoes abertas no MT5
- `POST /api/v1/mt5/validate-intention` — valida candidato via Risk Engine antes do operador agir
- `POST /api/v1/mt5/import-report` — importa relatorio MT5 (HTML/XML/CSV)
- `GET /api/v1/mt5/reconciliation/{date}` — concilia journal manual vs importado

### Bridge ZeroMQ

- **PUB/SUB:** EA publica em `mt5.tick`, `mt5.position`, `mt5.fill`, `mt5.heartbeat`
- **REQ/REP:** Python solicita `GET_STATE`, `GET_POSITIONS`, `GET_SYMBOL_INFO`, `PING`

## Eventos

Publicados via `cam._shared.events`:

- `MT5BridgeOnline` — bridge reconectada
- `MT5BridgeOffline` — sem heartbeat ha > 3s
- `MT5PositionChanged` — posicao mudou (nova/fechou/contratos diferentes)
- `MT5FillDetected` — execucao detectada no MT5 (operador agiu manualmente)

## Artigos constitucionais

- **Art. 15º** — Risk Engine continua sendo a autoridade. Bridge nao executa.
- **Art. 18º** — Bridge offline + posicao aberta = modo degradado, alerta Telegram (R16).
- **Art. 19º** — Contingencia tecnica documentada em RUNBOOK-INCIDENTE-TECNICO §2.2.
- **Art. 25º** — `MT5Position.pnl_net` sempre presente.
- **Art. 31º** — Fills detectados criam JournalEntry com `source="MT5_IMPORT"` ou `"MT5_BRIDGE"`.
- **Art. 35º** — IA nao toca esta camada.

## Anti-padroes

- ❌ Adicionar metodo `send_order` ou similar — bridge e read-only em v0.2.
- ❌ Importar de outra feature — comunicacao apenas via `_shared/` ou eventos (ADR-013).
- ❌ Expor credenciais MT5 em logs/responses — apenas booleanos.
- ❌ Ativar simultaneamente com `PROFIT_INTEGRATION_ENABLED=true` — mutex R21.03.
- ❌ Permitir EA em conta REAL com magic number de DEMO em v0.2 (sec §7.1).

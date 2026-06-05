# mql5/ — Artefatos MQL5 do CaM (SPEC v0.2)

> Diretorio paralelo a `ntsl/` (DESATIVADO em 2026-05-25). Implementa a
> camada de execucao do CaM em MetaTrader 5 conforme SPEC v0.2.1.

## Estrutura

```
mql5/
├── experts/             # Expert Advisors (EAs) — codigo principal
│   └── cam_bridge.mq5   # Bridge ZeroMQ read-only (v0.2)
├── indicators/          # Indicadores customizados (vazio em v0.2)
├── scripts/             # Scripts MQL5 utilitarios ad-hoc
├── include/             # Bibliotecas .mqh compartilhadas
│   └── cam_zmq.mqh      # Wrapper ZeroMQ para MT5 (a implementar — T-MT5-F01)
└── README.md            # Este arquivo
```

## Compilar e instalar EA

1. Abrir MetaEditor (vem com o MT5 — Tools → MetaEditor ou F4).
2. File → Open → selecionar `cam_bridge.mq5`.
3. F7 ou Compile — deve compilar sem warnings (CA12.1).
4. Drag-and-drop o EA da janela "Navigator" no MT5 sobre o grafico WIN ou WDO.
5. Permitir "Allow Algo Trading" no MT5 (Tools → Options → Expert Advisors).
6. Confirmar magic number e conta DEMO (sec §7.1).

## Canais ZeroMQ

| Canal | Tipo | Conteudo |
|---|---|---|
| `mt5.tick` | PUB | preco, bid, ask, volume, timestamp |
| `mt5.position` | PUB | ativo, contratos, direcao, P&L atual |
| `mt5.fill` | PUB | execucoes detectadas |
| `mt5.heartbeat` | PUB | 1 mensagem/segundo |
| (REQ/REP) | REP | `GET_STATE`, `GET_POSITIONS`, `GET_SYMBOL_INFO`, `PING` |

## Setup Wine + MT5 (Ubuntu LTS)

Ver `apps/cam-cockpit/scripts/install_wine_mt5.sh` (T-MT5-H01).

## Debug

- Logs do MT5: aba "Experts" no terminal MT5.
- Logs do CaM: `~/.cam/logs/cam-audit.log` (audit trail T-H05).
- Status da bridge: `GET /api/v1/mt5/bridge/status` no backend.

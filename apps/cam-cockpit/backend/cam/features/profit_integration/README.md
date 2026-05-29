# profit_integration — DESATIVADA em 2026-05-25

> Feature **DESATIVADA por feature flag** após adoção de MT5 + MQL5 conforme
> [SPEC v0.2.1](../../../../../project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md)
> e [DECISION-MEMO](../../../../../project/DECISION-MEMO-LINUX-OR-WINDOWS.md) §6.

## Status

| Campo | Valor |
|---|---|
| Estado | **DESATIVADO** (default) |
| Feature flag | `PROFIT_INTEGRATION_ENABLED=false` em `.env` |
| Comportamento dos endpoints | Retornam **HTTP 410 Gone** com payload R20.02 |
| Substituída por | [`cam/features/mt5_integration/`](../mt5_integration/) |
| Princípio | Coexistência (SPEC v0.2.1 §R21) — código preservado |

## Propósito (legado)

Camada de integração com Profit Pro/Ultra da Nelogica via importação CSV
+ validação de intenção via Risk Engine. Implementada na SPEC v0.1, Bloco D.

## I/O (legado — endpoints retornam 410 quando flag off)

- `POST /api/v1/profit/validate-intention` — F1: valida intenção vs Risk Engine
- `POST /api/v1/journal/import-csv` — F2: importa CSV do Profit
- `GET /api/v1/profit/reconciliation/{date}` — F2: relatório de reconciliação

## Eventos consumidos/publicados

(legado — não dispara em estado desativado)

## Artigos constitucionais

- **Art. 15º** — Risk Engine continua autoridade — preservado
- **Art. 25º** — P&L líquido — preservado
- **Art. 31º** — Journal obrigatório — preservado

## Anti-padroes

- ❌ Reativar simultaneamente com `MT5_INTEGRATION_ENABLED=true` — mutex R21.03 falha no startup.
- ❌ Editar código desta feature sem decisão formal de reativação registrada.

## Como reativar (R20.07)

1. Decisão formal registrada (motivação escrita, similar a emenda — ver PROTOCOLO-EMENDA-CONSTITUCIONAL).
2. Editar `apps/cam-cockpit/backend/.env`:
   ```bash
   PROFIT_INTEGRATION_ENABLED=true
   MT5_INTEGRATION_ENABLED=false
   ```
3. Restart do backend.
4. O mutex R21.03 valida que apenas uma camada está ativa.
5. Endpoints `/api/v1/profit/*` voltam ao comportamento original da SPEC v0.1.
6. Atualizar `FEATURE-FLAGS-LEDGER.md` com nova entrada.

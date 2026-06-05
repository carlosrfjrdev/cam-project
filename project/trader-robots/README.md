# Trader Robots — documentação (intenção viva)

Documentação dos robôs de trading do CaM: política de governança e fichas de
estratégia. O **código** dos robôs vive em `/apps/trader-robots/` (estado real);
aqui mora a **intenção/decisão** (NCC-1701 §9.3).

## Índice

| Documento | O que é |
|---|---|
| [POLITICA-ROBOS.md](./POLITICA-ROBOS.md) | Política/governança: autonomia, validação tripla (Profit×MT×CAM), ciclo de vida (INDEV→BACKTEST→ELEGIVEL→TESTE→APROVADO/REPROVADO/REVISION), critério ±20% |
| [D1-ORB30.md](./D1-ORB30.md) | Ficha da estratégia D1 ORB-30 (tese, lógica, parâmetros, status nos 3 ambientes) |

## Código dos robôs (estado real)

| Ambiente | Pasta |
|---|---|
| MetaTrader 5 (MQL5) | [`apps/trader-robots/mql5/experts/`](../../apps/trader-robots/mql5/experts/) |
| Profit (NTSL) | [`apps/trader-robots/ntsl/`](../../apps/trader-robots/ntsl/) |
| CAM (Python) | `apps/cam-cockpit/backend` (feature `strategy_lab`) |

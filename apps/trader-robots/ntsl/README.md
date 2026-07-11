# ntsl/ — Robôs NTSL (Profit / Nelogica)

> **REATIVADO em 2026-06-05.** Com a conta **Profit Pro** pronta, o NTSL volta
> como **terceiro ambiente** da validação tripla (Profit × MetaTrader × CAM) —
> ver [`project/trader-robots/POLITICA-ROBOS.md`](../../../project/trader-robots/POLITICA-ROBOS.md).
> (Histórico: esta pasta foi marcada DESATIVADA em 2026-05-25 quando o MT5 foi
> adotado como camada única; a estratégia mudou para validação cruzada.)

## Papel

O NTSL roda a **mesma estratégia** dos EAs MQL5 (`../mql5/experts/`) e do backtest
Python (CAM), para comparar os três. A convergência prova a lógica; a divergência
aponta bug (fill, dado, custo).

## Robôs

| Robô | Arquivo | Réplica de |
|---|---|---|
| D1 ORB-30 (executor) | [`cam_d1_orb30/cam_d1_orb30_exec.src`](./cam_d1_orb30/cam_d1_orb30_exec.src) | `cam_d1_orb30_exec.mq5` + `d1_orb30.py` |

## Como usar no Profit

1. Abrir o **editor de estratégias** (ProfitChart → Estratégias → Nova).
2. Colar o conteúdo do `.src`.
3. **Verificar/ajustar a sintaxe** — NTSL não é compilado neste repositório; nomes
   de funções de ordem e o formato de `Time` podem variar por versão do Profit.
4. Configurar os parâmetros **idênticos** aos do MT5/CAM (paridade).
5. Rodar o backtest no período do teste e comparar com MT5 e CAM (±20%).

> Conta DEMO até o robô atingir status **TESTE** (ver política).

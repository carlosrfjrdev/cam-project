"""
Runner standalone do profit_bridge (Windows).

Carrega a ProfitDLL, loga market-data only, assina o ticker e persiste os ticks
(ao vivo e/ou do dia) em `cam_market_ticks` com source="profit.profitdll".

Uso:
  # ao vivo (fica rodando, grava tick a tick):
  uv run python -m cam.features.profit_bridge.runner --ticker WINFUT

  # histórico do dia (puxa negócios do dia e sai):
  uv run python -m cam.features.profit_bridge.runner --ticker WINFUT \
      --history 2026-06-17

Config (.env): PROFIT_DLL_PATH, PROFIT_DLL_KEY, PROFIT_USERNAME, PROFIT_PASSWORD,
PROFIT_DEFAULT_EXCHANGE. Pré-requisito: ProfitDLL liberado na conta + chave.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from cam._shared.config import settings
from cam._shared.infra import async_session_factory
from cam.features.profit_bridge.client import ProfitBridgeClient
from cam.features.profit_bridge.persister import ProfitTickPersister

BR_TZ = ZoneInfo("America/Sao_Paulo")


async def _wait_ready(client: ProfitBridgeClient, timeout_s: float = 30.0) -> bool:
    waited = 0.0
    while waited < timeout_s:
        if client.is_ready():
            return True
        await asyncio.sleep(0.5)
        waited += 0.5
    return False


async def run(ticker: str, exchange: str, history_day: str | None) -> int:
    if not settings.profit_dll_path:
        print("ERRO: PROFIT_DLL_PATH não configurado no .env")
        return 2
    if not (
        settings.profit_dll_key
        and settings.profit_username
        and settings.profit_password
    ):
        print("ERRO: PROFIT_DLL_KEY / PROFIT_USERNAME / PROFIT_PASSWORD ausentes")
        return 2

    persister = ProfitTickPersister(async_session_factory)
    client = ProfitBridgeClient(settings.profit_dll_path, on_tick=persister.on_tick)

    print(f"[profit] carregando DLL: {settings.profit_dll_path}")
    ret = client.connect(
        settings.profit_dll_key, settings.profit_username, settings.profit_password
    )
    print(f"[profit] DLLInitializeMarketLogin -> {ret}")

    if not await _wait_ready(client):
        print(
            f"[profit] NÃO conectou (conn={client.connected} "
            f"mkt={client.market_connected} ativo={client.activated}). "
            "Chave/credenciais ou market-data liberado?"
        )
        client.finalize()
        return 1
    print("[profit] serviços conectados (login + market + ativação).")

    persister.start()
    sub = client.subscribe(ticker, exchange)
    print(f"[profit] SubscribeTicker({ticker}, {exchange}) -> {sub}")

    try:
        if history_day:
            day = datetime.strptime(history_day, "%Y-%m-%d").replace(tzinfo=BR_TZ)
            start = day.replace(hour=9, minute=0, second=0)
            end = day.replace(hour=18, minute=30, second=0)
            print(f"[profit] GetHistoryTrades {ticker} {start} -> {end}")
            client.request_history(ticker, exchange, start, end)
            # aguarda os pacotes do histórico chegarem e serem gravados
            await asyncio.sleep(15)
            await persister.stop()
            print(f"[profit] histórico: {persister.total_persisted} ticks gravados.")
        else:
            print("[profit] ao vivo. Ctrl+C para parar.")
            last = 0
            while True:
                await asyncio.sleep(10)
                if persister.total_persisted != last:
                    print(f"[profit] ticks gravados: {persister.total_persisted}")
                    last = persister.total_persisted
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[profit] encerrando...")
    finally:
        await persister.stop()
        client.finalize()
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Bridge de ticks do Profit (ProfitDLL)")
    ap.add_argument("--ticker", required=True, help="ex.: WINFUT, WINM26, PETR4")
    ap.add_argument("--exchange", default=None, help="default: PROFIT_DEFAULT_EXCHANGE")
    ap.add_argument("--history", default=None, help="YYYY-MM-DD: puxa o dia e sai")
    a = ap.parse_args()

    exchange = a.exchange or settings.profit_default_exchange
    sys.exit(asyncio.run(run(a.ticker, exchange, a.history)))


if __name__ == "__main__":
    main()

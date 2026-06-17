"""
ProfitBridgeClient — carrega a ProfitDLL e expõe leitura de ticks (read-only).

Responsabilidades:
- Carregar a DLL (ctypes) e fixar restype/argtypes do subconjunto read-only.
- Login **market-data only** (DLLInitializeMarketLogin) — sem roteamento.
- Registrar callbacks de trade ao vivo e de histórico → normaliza cada negócio
  em dict {asset, price, volume, quantity, ts_epoch, aggressor, source} e entrega
  ao handler `on_tick` (thread-safe a cargo do caller).
- SubscribeTicker / GetHistoryTrades / DLLFinalize.

NÃO declara nenhuma função de ordem (SendOrder etc.) — read-only por construção.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from ctypes import POINTER, WinDLL, byref, c_int, c_size_t, c_wchar_p, cast
from datetime import datetime
from zoneinfo import ZoneInfo

from cam.features.profit_bridge.types import (
    NL_OK,
    SystemTime,
    TConnectorTrade,
    TConnectorTradeCallback,
    TNewDailyCallback,
    TProgressCallback,
    TStateCallback,
    TTinyBookCallback,
    aggressor_of,
)

_log = logging.getLogger("cam.profit_bridge")
BR_TZ = ZoneInfo("America/Sao_Paulo")

TickHandler = Callable[[dict], None]


def _systemtime_to_epoch(st: SystemTime) -> float | None:
    try:
        dt = datetime(
            st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond,
            st.wMilliseconds * 1000, tzinfo=BR_TZ,
        )
        return dt.timestamp()
    except (ValueError, OverflowError):
        return None


class ProfitBridgeClient:
    SOURCE = "profit.profitdll"

    def __init__(
        self,
        dll_path: str,
        on_tick: TickHandler,
        on_history_tick: TickHandler | None = None,
    ) -> None:
        self._dll_path = dll_path
        self._on_tick = on_tick
        self._on_history_tick = on_history_tick or on_tick
        self._dll: WinDLL | None = None
        # referências mantidas vivas (senão o GC derruba os callbacks → crash)
        self._cbs: list = []
        self.connected = False
        self.activated = False
        self.market_connected = False

    # ---------------- setup ----------------

    def load(self) -> None:
        dll = WinDLL(self._dll_path)
        dll.SubscribeTicker.argtypes = [c_wchar_p, c_wchar_p]
        dll.SubscribeTicker.restype = c_int
        dll.UnsubscribeTicker.argtypes = [c_wchar_p, c_wchar_p]
        dll.UnsubscribeTicker.restype = c_int
        dll.SetTradeCallbackV2.argtypes = [TConnectorTradeCallback]
        dll.SetTradeCallbackV2.restype = c_int
        dll.SetHistoryTradeCallbackV2.argtypes = [TConnectorTradeCallback]
        dll.SetHistoryTradeCallbackV2.restype = c_int
        dll.TranslateTrade.argtypes = [c_size_t, POINTER(TConnectorTrade)]
        dll.TranslateTrade.restype = c_int
        dll.GetHistoryTrades.argtypes = [c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p]
        dll.GetHistoryTrades.restype = c_int
        dll.DLLFinalize.restype = c_int
        self._dll = dll

    def _normalize(self, asset_safe, p_trade: int, edit: bool) -> dict | None:
        assert self._dll is not None
        ticker = cast(asset_safe.Ticker, c_wchar_p).value if asset_safe.Ticker else ""
        trade = TConnectorTrade(Version=0)
        if self._dll.TranslateTrade(p_trade, byref(trade)) != NL_OK:
            return None
        ts = _systemtime_to_epoch(trade.TradeDate)
        if ts is None or not trade.Price:
            return None
        return {
            "asset": (ticker or "").strip().upper(),
            "price": round(float(trade.Price), 2),
            "quantity": int(trade.Quantity),
            "volume": float(trade.Volume),
            "ts_epoch": ts,
            "aggressor": aggressor_of(int(trade.TradeType)),
            "trade_number": int(trade.TradeNumber),
            "edit": edit,
            "source": self.SOURCE,
        }

    def _build_callbacks(self):
        @TConnectorTradeCallback
        def trade_cb(asset_safe, p_trade, flags):
            try:
                tick = self._normalize(asset_safe, p_trade, edit=bool(flags & 1))
                if tick:
                    self._on_tick(tick)
            except Exception:  # noqa: BLE001 — callback nunca pode propagar p/ DLL
                _log.exception("profit trade_cb falhou")

        @TConnectorTradeCallback
        def history_cb(asset_safe, p_trade, flags):
            try:
                tick = self._normalize(asset_safe, p_trade, edit=False)
                if tick:
                    self._on_history_tick(tick)
            except Exception:  # noqa: BLE001
                _log.exception("profit history_cb falhou")

        @TStateCallback
        def state_cb(n_type, n_result):
            if n_type == 0:
                self.connected = n_result == 0
            elif n_type == 2:
                self.market_connected = n_result == 4
            elif n_type == 3:
                self.activated = n_result == 0
            _log.info(
                "profit state type=%s result=%s (conn=%s mkt=%s ativo=%s)",
                n_type, n_result, self.connected, self.market_connected, self.activated,
            )

        # stubs exigidos pela assinatura do login, mas não usados
        @TNewDailyCallback
        def daily_cb(*_a):  # noqa: ANN002
            pass

        @TProgressCallback
        def progress_cb(*_a):  # noqa: ANN002
            pass

        @TTinyBookCallback
        def tinybook_cb(*_a):  # noqa: ANN002
            pass

        self._cbs = [trade_cb, history_cb, state_cb, daily_cb, progress_cb, tinybook_cb]
        return state_cb, daily_cb, progress_cb, tinybook_cb, trade_cb, history_cb

    # ---------------- lifecycle ----------------

    def connect(self, key: str, user: str, password: str) -> int:
        """Login market-data only (sem roteamento). Retorna o código da DLL."""
        if self._dll is None:
            self.load()
        assert self._dll is not None
        state_cb, daily_cb, progress_cb, tinybook_cb, trade_cb, history_cb = (
            self._build_callbacks()
        )
        # ordem posicional conforme SDK (Exemplo Python, DLLInitializeMarketLogin)
        ret = self._dll.DLLInitializeMarketLogin(
            c_wchar_p(key), c_wchar_p(user), c_wchar_p(password),
            state_cb, None, daily_cb, None, None, None, progress_cb, tinybook_cb,
        )
        self._dll.SetTradeCallbackV2(trade_cb)
        self._dll.SetHistoryTradeCallbackV2(history_cb)
        return ret

    def subscribe(self, ticker: str, exchange: str) -> int:
        assert self._dll is not None
        return self._dll.SubscribeTicker(c_wchar_p(ticker), c_wchar_p(exchange))

    def request_history(
        self, ticker: str, exchange: str, start: datetime, end: datetime
    ) -> int:
        """Negócios do período → chegam no history callback. Datas dd/mm/yyyy."""
        assert self._dll is not None
        fmt = "%d/%m/%Y %H:%M:%S"
        return self._dll.GetHistoryTrades(
            c_wchar_p(ticker), c_wchar_p(exchange),
            c_wchar_p(start.strftime(fmt)), c_wchar_p(end.strftime(fmt)),
        )

    def is_ready(self) -> bool:
        return self.connected and self.market_connected and self.activated

    def finalize(self) -> None:
        if self._dll is not None:
            try:
                self._dll.DLLFinalize()
            except Exception:  # noqa: BLE001
                pass

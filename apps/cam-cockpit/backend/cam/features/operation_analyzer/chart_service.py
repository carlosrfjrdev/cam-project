"""
Serviço de chart do Operation Analyzer.

Para um símbolo+timeframe: traz candles do MT5, calcula indicadores (EMA 9/20/50/
200, SMA 200, VWAP diária e semanal) e detecta topos/fundos (níveis horizontais).

Estratégia de dados:
- TFs nativos do MT5 (M1, M5, M15, M30, H1, H4, D1) → GET_CANDLES (histórico longo).
- M2 e M10 → DERIVADOS do M1 (o EA não os suporta nativo), por sessão (kernel).

Níveis (topos/fundos) calculados para D1, H1, M10, M2 (R do Founder).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cam._shared.research_kernel.bars import Bar, derive, timeframe_minutes
from cam._shared.research_kernel.indicators import ema, sma, vwap_anchored
from cam._shared.research_kernel.levels import detect_levels

BR_TZ = ZoneInfo("America/Sao_Paulo")

DERIVED_TFS = {"M2", "M10"}
NATIVE_TFS = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}
ALL_TFS = ["M1", "M2", "M5", "M10", "M15", "M30", "H1", "H4", "D1"]
LEVEL_TFS = {"D1", "H1", "M10", "M2"}


class ChartUnavailable(RuntimeError):
    """Provider casca / bridge offline / sem dados."""


def _to_bar(symbol: str, tf: str, c: dict) -> Bar:
    ts = datetime.fromtimestamp(int(c["ts"]), tz=BR_TZ)
    mins = timeframe_minutes(tf)
    return Bar(
        symbol=symbol,
        timeframe=tf,
        ts_open=ts,
        ts_close=ts + timedelta(minutes=mins),
        session_date=ts.strftime("%Y-%m-%d"),
        open=float(c["o"]),
        high=float(c["h"]),
        low=float(c["l"]),
        close=float(c["c"]),
        volume=int(c.get("v") or 0),
        financial=float(c["c"]) * int(c.get("v") or 0),
    )


def _derive_multi_session(m1: list[Bar], target_tf: str) -> list[Bar]:
    """Deriva M2/M10 do M1 respeitando a âncora de cada sessão."""
    by_session: dict[str, list[Bar]] = defaultdict(list)
    for b in m1:
        by_session[b.session_date].append(b)
    out: list[Bar] = []
    for _date in sorted(by_session):
        sess = sorted(by_session[_date], key=lambda x: x.ts_open)
        out.extend(derive(sess, target_tf, session_open=sess[0].ts_open))
    return out


def _series(bars: list[Bar], values: list[float | None]) -> list[dict]:
    return [
        {"time": int(b.ts_open.timestamp()), "value": round(v, 2)}
        for b, v in zip(bars, values, strict=False)
        if v is not None
    ]


def _overlays(bars: list[Bar]) -> dict:
    closes = [b.close for b in bars]
    return {
        "ema9": _series(bars, ema(closes, 9)),
        "ema20": _series(bars, ema(closes, 20)),
        "ema50": _series(bars, ema(closes, 50)),
        "ema200": _series(bars, ema(closes, 200)),
        "sma200": _series(bars, sma(closes, 200)),
        "vwap_daily": _series(bars, vwap_anchored(bars, "daily")),
        "vwap_weekly": _series(bars, vwap_anchored(bars, "weekly")),
    }


async def build_chart(symbol: str, timeframe: str, count: int = 1500) -> dict:
    if timeframe not in NATIVE_TFS and timeframe not in DERIVED_TFS:
        raise ChartUnavailable(f"timeframe inválido: {timeframe}")

    from cam.features.app_settings import store

    if store.get_market_data_provider() != "mt5":
        raise ChartUnavailable("provedor não-MT5 em casca — selecione MT5 nas Config.")

    from cam.features.mt5_integration.routes import _service as mt5

    if not mt5.bridge.is_alive():
        raise ChartUnavailable("bridge MT5 offline — atache o EA cam_bridge")

    if timeframe in DERIVED_TFS:
        m1_count = min(count * timeframe_minutes(timeframe), 20000)
        resp = await mt5.get_candles(symbol, "M1", m1_count, timeout_ms=20000)
        raw = resp.get("data", {}).get("candles", [])
        m1 = sorted((_to_bar(symbol, "M1", c) for c in raw), key=lambda b: b.ts_open)
        bars = _derive_multi_session(m1, timeframe)
    else:
        resp = await mt5.get_candles(symbol, timeframe, count, timeout_ms=20000)
        raw = resp.get("data", {}).get("candles", [])
        bars = sorted(
            (_to_bar(symbol, timeframe, c) for c in raw), key=lambda b: b.ts_open
        )

    if not bars:
        raise ChartUnavailable("sem candles retornados pelo MT5")

    candles = [
        {
            "time": int(b.ts_open.timestamp()),
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in bars
    ]
    levels = []
    if timeframe in LEVEL_TFS:
        levels = [
            {
                "price": lv.price,
                "kind": lv.kind,
                "touches": lv.touches,
                "first_ts": lv.first_ts,
                "last_ts": lv.last_ts,
            }
            for lv in detect_levels(bars, span=3, tol=0.0015, min_touches=2, top_n=12)
        ]

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles,
        "overlays": _overlays(bars),
        "levels": levels,
        "level_tf": timeframe in LEVEL_TFS,
    }

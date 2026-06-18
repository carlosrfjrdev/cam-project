"""
Serviço de chart do Operation Analyzer.

Para um símbolo+timeframe: traz candles do MT5, calcula indicadores (EMA 9/20/50/
200, SMA 200, VWAP diária e semanal), detecta topos/fundos em D1/H1/M10/M2 (cada TF
com sua cor no front) e **persiste** os candles importados em research_bars (upsert).

Dados:
- TFs nativos do MT5 (M1, M5, M15, M30, H1, H4, D1) → GET_CANDLES (histórico longo).
- M2 e M10 → DERIVADOS do M1 (o EA não os suporta nativo), por sessão (kernel).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from cam._shared.infra import async_session_factory
from cam._shared.research_kernel.bars import Bar, derive, timeframe_minutes
from cam._shared.research_kernel.indicators import ema, sma, vwap_anchored
from cam._shared.research_kernel.levels import detect_levels
from cam.features.research.leadlag import repository as research_repo

BR_TZ = ZoneInfo("America/Sao_Paulo")

DERIVED_TFS = {"M2", "M10"}
NATIVE_TFS = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}
ALL_TFS = ["M1", "M2", "M5", "M10", "M15", "M30", "H1", "H4", "D1"]
# TFs com detecção de topos/fundos (todos exibidos no gráfico, cada um com sua cor)
LEVEL_TFS = ["D1", "H1", "M10", "M2"]
# contagem de barras por TF na análise de níveis
LEVEL_COUNTS = {"D1": 300, "H1": 1500, "M10": 800, "M2": 4000}
_M1_FETCH = 8000  # M1 p/ derivar M2/M10


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
    """
    Deriva M2/M10 do M1 com buckets alinhados à GRADE DE RELÓGIO (meia-noite),
    não ao 1º candle da sessão — assim M2 cai sempre em minuto PAR (00:00–01:59,
    02:00–03:59…) e M10 em :00/:10/:20…, igual ao MT5/TradingView. (O kernel
    `derive` ancorado na sessão é da research lane, R-10; aqui usamos a grade.)
    """
    by_session: dict[str, list[Bar]] = defaultdict(list)
    for b in m1:
        by_session[b.session_date].append(b)
    out: list[Bar] = []
    for _date in sorted(by_session):
        sess = sorted(by_session[_date], key=lambda x: x.ts_open)
        midnight = sess[0].ts_open.replace(hour=0, minute=0, second=0, microsecond=0)
        out.extend(derive(sess, target_tf, session_open=midnight))
    return out


async def _get_bars(mt5, symbol: str, tf: str, count: int, m1_cache: dict) -> list[Bar]:
    if tf in DERIVED_TFS:
        if "M1" not in m1_cache:
            resp = await mt5.get_candles(symbol, "M1", _M1_FETCH, timeout_ms=20000)
            raw = resp.get("data", {}).get("candles", [])
            m1_cache["M1"] = sorted(
                (_to_bar(symbol, "M1", c) for c in raw), key=lambda b: b.ts_open
            )
        return _derive_multi_session(m1_cache["M1"], tf)[-count:]
    resp = await mt5.get_candles(symbol, tf, count, timeout_ms=20000)
    raw = resp.get("data", {}).get("candles", [])
    return sorted((_to_bar(symbol, tf, c) for c in raw), key=lambda b: b.ts_open)


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


def _levels_payload(bars, span, tol, min_touches, top_n) -> list[dict]:
    return [
        {
            "price": lv.price,
            "kind": lv.kind,
            "touches": lv.touches,
            "first_ts": lv.first_ts,
            "last_ts": lv.last_ts,
        }
        for lv in detect_levels(
            bars, span=span, tol=tol, min_touches=min_touches, top_n=top_n
        )
    ]


async def _persist(bars_by_tf: dict[str, list[Bar]]) -> int:
    rows = []
    for bars in bars_by_tf.values():
        for b in bars:
            rows.append(
                {
                    "symbol": b.symbol,
                    "timeframe": b.timeframe,
                    "ts_open": b.ts_open.timestamp(),
                    "ts_close": b.ts_close.timestamp(),
                    "session_date": b.session_date,
                    "open": b.open,
                    "high": b.high,
                    "low": b.low,
                    "close": b.close,
                    "volume": b.volume,
                    "financial": b.financial,
                    "trades": b.trades,
                    "vwap": b.vwap,
                    "is_partial": b.is_partial,
                    "price_series": "raw",
                    "provenance_id": None,
                }
            )
    if not rows:
        return 0
    try:
        async with async_session_factory() as session:
            for i in range(0, len(rows), 2000):
                await research_repo.insert_bars(session, rows[i : i + 2000])
            await session.commit()
        return len(rows)
    except Exception:  # noqa: BLE001 — persistência best-effort
        return 0


async def build_chart(
    symbol: str,
    timeframe: str,
    count: int = 1500,
    span: int = 3,
    tol: float = 0.0015,
    min_touches: int = 2,
    top_n: int = 12,
) -> dict:
    if timeframe not in NATIVE_TFS and timeframe not in DERIVED_TFS:
        raise ChartUnavailable(f"timeframe inválido: {timeframe}")

    from cam.features.app_settings import store

    if store.get_market_data_provider() != "mt5":
        raise ChartUnavailable("provedor não-MT5 em casca — selecione MT5 nas Config.")

    from cam.features.mt5_integration.routes import _service as mt5

    if not mt5.bridge.is_alive():
        raise ChartUnavailable("bridge MT5 offline — atache o EA cam_bridge")

    m1_cache: dict = {}
    bars_by_tf: dict[str, list[Bar]] = {}

    displayed = await _get_bars(mt5, symbol, timeframe, count, m1_cache)
    if not displayed:
        raise ChartUnavailable("sem candles retornados pelo MT5")
    bars_by_tf[timeframe] = displayed

    # níveis (topos/fundos) por TF — cada um com sua cor no front
    levels_by_tf: dict[str, list[dict]] = {}
    for ltf in LEVEL_TFS:
        b = bars_by_tf.get(ltf)
        if b is None:
            b = await _get_bars(mt5, symbol, ltf, LEVEL_COUNTS[ltf], m1_cache)
            bars_by_tf[ltf] = b
        levels_by_tf[ltf] = _levels_payload(b, span, tol, min_touches, top_n)

    persisted = await _persist(bars_by_tf)

    candles = [
        {
            "time": int(b.ts_open.timestamp()),
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in displayed
    ]
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": candles,
        "overlays": _overlays(displayed),
        "levels_by_tf": levels_by_tf,
        "level_tfs": LEVEL_TFS,
        "persisted_bars": persisted,
        "params": {
            "span": span, "tol": tol, "min_touches": min_touches, "top_n": top_n,
        },
    }

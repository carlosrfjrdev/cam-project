"""
Serviço de ingestão da Research Lane — SPEC v0.5 R-01..R-12 (sub-versão 0.5.1).

ISOLAMENTO (ADR-015 / R-35): este módulo **não importa** mt5_integration nem
execução. A fonte de dado (MT5) é injetada como **callables** (`CandleFetcher`,
`TickFetcher`) pela borda (`cam/api/`, o compositor autorizado — ADR-013). Assim
o import-linter "Research Lane nao importa execucao nem broker" permanece verde.

Persiste apenas em research_* (R-34).
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from cam.features.research.leadlag import repository as repo
from cam.features.research.leadlag.bars import Bar, aggressor_from_flags, derive
from cam.features.research.leadlag.snapshot import batch_hash, composite_hash

# A fonte injeta estes callables. Retorno espelha o contrato do bridge MT5.
# candle_fetcher(symbol, tf, count)
#   -> {"status","data":{"candles":[{ts,o,h,l,c,v}]}}
CandleFetcher = Callable[[str, str, int], Awaitable[dict[str, Any]]]
# tick_fetcher(symbol, count) -> {"status","data":{"sample":[...]}}  (probe-style)
TickFetcher = Callable[[str, int], Awaitable[dict[str, Any]]]

_DERIVED_TFS = ["M5", "M15", "M30", "H1", "H4", "D1"]
_CALENDAR_VERSION = "b3-2026.1"
_AGG_RULE_HASH = "rule:m1-canonical-v1"


def _session_open(session_date: str) -> datetime:
    # Pregão B3 padrão abre 09:00 (horário local). Para v0.5.1 usamos âncora fixa;
    # research_calendar afina depois (R-13).
    y, m, d = (int(x) for x in session_date.split("-"))
    return datetime(y, m, d, 9, 0, 0, tzinfo=UTC)


class LeadLagIngestionService:
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        self._factory = session_factory

    async def ingest(
        self,
        sources: list[str],
        timeframes: list[str],
        count: int,
        with_ticks: bool,
        candle_fetcher: CandleFetcher,
        tick_fetcher: TickFetcher | None = None,
        tick_count: int = 2000,
    ) -> dict[str, Any]:
        """
        Ingestão parametrizável (R-01): para cada símbolo, busca M1 via fetcher,
        persiste M1 canônico + derivadas determinísticas; opcionalmente ticks com
        agressor. Retorna snapshot_id + resumo. Falha segura por símbolo (R-05).
        """
        symbols = [s.strip().upper() for s in sources if s.strip()]
        total_bars = 0
        total_ticks = 0
        per_symbol: dict[str, Any] = {}
        raw_hash_parts: list[str] = []

        async with self._factory() as session:
            for sym in symbols:
                resp = await candle_fetcher(sym, "M1", count)
                if resp.get("status") != "ok":
                    per_symbol[sym] = {"error": resp.get("error", "FETCH_FAILED")}
                    continue
                candles = resp["data"].get("candles", [])
                if not candles:
                    per_symbol[sym] = {"error": "NO_CANDLES"}
                    continue

                raw_hash_parts.append(batch_hash(candles))
                src_id = await repo.insert_source(
                    session,
                    bar_origin="broker_ohlcv",
                    ts_source="broker_recv",
                    aggressor_source="exchange" if with_ticks else None,
                    symbol=sym,
                    source_tf="M1",
                    w_start=candles[0]["ts"],
                    w_end=candles[-1]["ts"],
                    hash=batch_hash(candles),
                )

                m1_bars = self._candles_to_m1(sym, candles)
                n_bars = await self._persist_bars(session, m1_bars, src_id)
                total_bars += n_bars

                n_ticks = 0
                if with_ticks and tick_fetcher is not None:
                    n_ticks = await self._persist_ticks(
                        session, sym, src_id, tick_fetcher, tick_count
                    )
                    total_ticks += n_ticks

                per_symbol[sym] = {"m1": len(m1_bars), "bars": n_bars, "ticks": n_ticks}

            composite = composite_hash(
                raw_canonical_hash=batch_hash([{"h": h} for h in raw_hash_parts]),
                calendar_version=_CALENDAR_VERSION,
                timeframes=["M1", *timeframes],
                aggregation_rule_hash=_AGG_RULE_HASH,
            )
            snapshot_id = await repo.insert_snapshot(
                session,
                symbols=symbols,
                timeframes=["M1", *timeframes],
                mode="both",
                composite_hash=composite,
                calendar_version=_CALENDAR_VERSION,
                with_ticks=with_ticks,
            )
            await self._quality_checks(session, snapshot_id, per_symbol)
            await session.commit()

        return {
            "snapshot_id": snapshot_id,
            "composite_hash": composite,
            "symbols": symbols,
            "total_bars": total_bars,
            "total_ticks": total_ticks,
            "per_symbol": per_symbol,
        }

    @staticmethod
    def _candles_to_m1(symbol: str, candles: list[dict[str, Any]]) -> list[Bar]:
        out: list[Bar] = []
        for c in candles:
            ts = datetime.fromtimestamp(c["ts"], tz=UTC)
            out.append(
                Bar(
                    symbol=symbol,
                    timeframe="M1",
                    ts_open=ts,
                    ts_close=ts,
                    session_date=ts.strftime("%Y-%m-%d"),
                    open=float(c["o"]),
                    high=float(c["h"]),
                    low=float(c["l"]),
                    close=float(c["c"]),
                    volume=int(c.get("v") or 0),
                    trades=int(c.get("v") or 0),
                    financial=float(c["c"]) * int(c.get("v") or 0),
                )
            )
        return out

    async def _persist_bars(
        self, session: Any, m1_bars: list[Bar], src_id: int
    ) -> int:
        # M1 canônico + derivadas determinísticas por sessão (R-10/R-11).
        by_session: dict[str, list[Bar]] = {}
        for b in m1_bars:
            by_session.setdefault(b.session_date, []).append(b)

        all_bars: list[Bar] = list(m1_bars)
        for sdate, bars in by_session.items():
            so = _session_open(sdate)
            for tf in _DERIVED_TFS:
                all_bars.extend(derive(bars, tf, so))

        rows = [self._bar_row(b, src_id) for b in all_bars]
        return await repo.insert_bars(session, rows)

    @staticmethod
    def _bar_row(b: Bar, src_id: int) -> dict[str, Any]:
        return {
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
            "provenance_id": src_id,
        }

    async def _persist_ticks(
        self,
        session: Any,
        symbol: str,
        src_id: int,
        tick_fetcher: TickFetcher,
        tick_count: int,
    ) -> int:
        resp = await tick_fetcher(symbol, tick_count)
        if resp.get("status") != "ok":
            return 0
        sample = resp["data"].get("sample", [])
        rows: list[dict[str, Any]] = []
        for t in sample:
            t_msc = int(t.get("t_msc") or 0)
            if not t_msc:
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "t_msc": t_msc,
                    "ts_s": t_msc / 1000.0,
                    "price": float(t.get("last") or 0),
                    "volume": int(t.get("vol") or 0),
                    "aggressor": aggressor_from_flags(int(t.get("flags") or 0)),
                    "flags_raw": int(t.get("flags") or 0),
                    "provenance_id": src_id,
                }
            )
        return await repo.insert_ticks(session, rows)

    async def _quality_checks(
        self, session: Any, snapshot_id: int, per_symbol: dict[str, Any]
    ) -> None:
        for sym, info in per_symbol.items():
            if "error" in info:
                await repo.insert_quality_check(
                    session,
                    snapshot_id=snapshot_id,
                    symbol=sym,
                    timeframe="M1",
                    check_name="ingest_error",
                    value=1.0,
                )
            else:
                await repo.insert_quality_check(
                    session,
                    snapshot_id=snapshot_id,
                    symbol=sym,
                    timeframe="M1",
                    check_name="m1_is_primary",
                    value=float(info.get("m1", 0)),
                )

    async def data_health(self) -> dict[str, Any]:
        async with self._factory() as session:
            return await repo.data_health(session)

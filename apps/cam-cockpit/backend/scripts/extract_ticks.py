"""
Extrator de ticks históricos via bridge MT5 (cam_bridge / GET_TICKS).

Puxa ticks reais (CopyTicks COPY_TICKS_ALL) em BULK, paginando por `from_msc`,
e grava:
  - CSV consolidado + 1 CSV por dia em project/tcam/analysis/ticks/
  - (opcional, --persist) tabela cam_market_ticks, source="mt5.cam_bridge.extract"

Pré-requisito: backend NÃO precisa estar rodando, mas o MT5 com o EA
`cam_bridge` atachado a um gráfico do símbolo (publicando em 5556 / REP 5557).

Uso:
  uv run python scripts/extract_ticks.py --symbol WINM26 --from 2026-06-08
  uv run python scripts/extract_ticks.py --symbol WINM26 --from 2026-06-08 --to 2026-06-17 --persist
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import text

from cam._shared import config as _config_module
from cam._shared.infra import async_session_factory
from cam.features.mt5_integration.service import MT5IntegrationService

BR_TZ = ZoneInfo("America/Sao_Paulo")
OUT_DIR = Path(__file__).resolve().parents[4] / "project" / "tcam" / "analysis" / "ticks"

# MT5: TICK_FLAG_BUY=4, TICK_FLAG_SELL=8 (agressor)
FLAG_BUY = 4
FLAG_SELL = 8

_INSERT = text(
    """
    INSERT INTO cam_market_ticks (asset, price, volume, timestamp, source)
    VALUES (:asset, :price, :volume, to_timestamp(:ts_s), :source)
    """
)


def _aggressor(flags: int) -> str:
    if flags & FLAG_BUY:
        return "B"
    if flags & FLAG_SELL:
        return "S"
    return ""


def _price(t: dict) -> float:
    last = t.get("last") or 0
    if not last:
        bid = t.get("bid") or 0
        ask = t.get("ask") or 0
        last = (bid + ask) / 2 if (bid and ask) else (bid or ask)
    return round(float(last or 0), 2)


async def extract(symbol: str, from_dt: datetime, to_dt: datetime, persist: bool) -> None:
    s = _config_module.settings
    svc = MT5IntegrationService(
        host=s.mt5_bridge_host,
        pub_port=s.mt5_bridge_pub_port,
        req_port=s.mt5_bridge_req_port,
    )
    await svc.bridge.connect()

    from_msc = int(from_dt.timestamp() * 1000)
    to_msc = int(to_dt.timestamp() * 1000)

    print(f"[extract] {symbol}  {from_dt.isoformat()} -> {to_dt.isoformat()}")
    print(f"[extract] from_msc={from_msc}  to_msc={to_msc}")

    all_ticks: list[dict] = []
    page = 0
    while True:
        resp = await svc.get_ticks(symbol, from_msc=from_msc, count=20000)
        if resp.get("error"):
            print(f"[extract] ERRO bridge: {resp}  (EA atachado? bridge online?)")
            break
        data = resp.get("data", {})
        ticks = data.get("ticks", [])
        got = data.get("count", len(ticks))
        last_msc = data.get("last_msc", from_msc)
        page += 1
        print(f"[extract] página {page}: {got} ticks  last_msc={last_msc}")
        if not ticks:
            break
        all_ticks.extend(ticks)
        if last_msc >= to_msc:
            all_ticks = [t for t in all_ticks if t.get("t", 0) <= to_msc]
            break
        if last_msc <= from_msc:  # sem avanço → fim do histórico
            break
        if got < 20000:  # última página parcial
            break
        from_msc = last_msc + 1

    await svc.bridge.disconnect()

    if not all_ticks:
        print("[extract] nenhum tick retornado. Verifique o EA cam_bridge no MT5.")
        return

    # dedupe por (t, last, v, f)
    seen = set()
    rows = []
    for t in all_ticks:
        key = (t.get("t"), t.get("last"), t.get("v"), t.get("f"))
        if key in seen:
            continue
        seen.add(key)
        dt_br = datetime.fromtimestamp(t["t"] / 1000.0, tz=UTC).astimezone(BR_TZ)
        rows.append(
            {
                "t_msc": t["t"],
                "datetime_br": dt_br.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "date": dt_br.strftime("%Y-%m-%d"),
                "bid": t.get("bid"),
                "ask": t.get("ask"),
                "last": t.get("last"),
                "price": _price(t),
                "volume": t.get("v"),
                "flags": t.get("f"),
                "aggressor": _aggressor(int(t.get("f") or 0)),
            }
        )
    rows.sort(key=lambda r: r["t_msc"])
    print(f"[extract] {len(rows)} ticks únicos.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["t_msc", "datetime_br", "date", "bid", "ask", "last", "price",
            "volume", "flags", "aggressor"]

    # consolidado
    cons = OUT_DIR / f"{symbol}_{from_dt.date()}_{to_dt.date()}.csv"
    with cons.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"[extract] CSV consolidado: {cons}")

    # por dia
    byday: dict[str, list] = defaultdict(list)
    for r in rows:
        byday[r["date"]].append(r)
    for d in sorted(byday):
        p = OUT_DIR / f"{symbol}_{d}.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, delimiter=";")
            w.writeheader()
            w.writerows(byday[d])
        print(f"[extract]   {d}: {len(byday[d])} ticks -> {p.name}")

    if persist:
        sym = symbol.upper()[:10]
        db_rows = [
            {
                "asset": sym,
                "price": r["price"],
                "volume": int(r["volume"] or 0),
                "ts_s": r["t_msc"] / 1000.0,
                "source": "mt5.cam_bridge.extract",
            }
            for r in rows
            if r["price"]
        ]
        async with async_session_factory() as session:
            for i in range(0, len(db_rows), 1000):
                await session.execute(_INSERT, db_rows[i : i + 1000])
            await session.commit()
        print(f"[extract] persistidos {len(db_rows)} ticks em cam_market_ticks.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Extrai ticks históricos via bridge MT5")
    ap.add_argument("--symbol", default="WINM26")
    ap.add_argument("--from", dest="from_d", required=True, help="YYYY-MM-DD (00:00 BR)")
    ap.add_argument("--to", dest="to_d", default=None, help="YYYY-MM-DD (23:59 BR); default=hoje")
    ap.add_argument("--persist", action="store_true", help="também grava em cam_market_ticks")
    a = ap.parse_args()

    from_dt = datetime.strptime(a.from_d, "%Y-%m-%d").replace(tzinfo=BR_TZ)
    if a.to_d:
        to_dt = datetime.strptime(a.to_d, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=BR_TZ
        )
    else:
        to_dt = datetime.now(BR_TZ).replace(hour=23, minute=59, second=59)
    # buffer de 3h pra cobrir diferença de timezone do servidor de trade
    from_dt = from_dt - timedelta(hours=3)

    # Windows: pyzmq exige SelectorEventLoop (Proactor não implementa add_reader)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(extract(a.symbol, from_dt, to_dt, a.persist))


if __name__ == "__main__":
    main()

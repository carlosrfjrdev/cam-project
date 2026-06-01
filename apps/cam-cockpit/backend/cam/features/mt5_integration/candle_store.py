"""
Persistência de candles diários do Inspetor — tabela `cam_inspector_candles`.

ADR-014 / SPEC-Inspetor. Tabela regular (não é continuous aggregate), upsert
idempotente por (symbol, timeframe, ts). Alimenta o slice `regime`, que lê esta
tabela sem importar `mt5_integration` (acoplamento só via tabela de banco —
ADR-013).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_UPSERT = text(
    """
    INSERT INTO cam_inspector_candles
        (symbol, timeframe, ts, open, high, low, close, volume)
    VALUES (:symbol, :timeframe, to_timestamp(:ts), :o, :h, :l, :c, :v)
    ON CONFLICT (symbol, timeframe, ts) DO UPDATE
      SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
          close = EXCLUDED.close, volume = EXCLUDED.volume
    """
)


async def upsert_daily_candles(
    session: AsyncSession, symbol: str, candles: list[dict[str, Any]]
) -> int:
    """Upsert de candles D1. Retorna a quantidade processada."""
    n = 0
    for c in candles:
        await session.execute(
            _UPSERT,
            {
                "symbol": symbol.upper(),
                "timeframe": "D1",
                "ts": c["ts"],
                "o": c["o"],
                "h": c["h"],
                "l": c["l"],
                "c": c["c"],
                "v": c["v"],
            },
        )
        n += 1
    await session.commit()
    return n

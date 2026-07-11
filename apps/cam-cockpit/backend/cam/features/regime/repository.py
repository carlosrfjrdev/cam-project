"""
Leitura de candles para o regime — tabela `cam_inspector_candles`.

ADR-013: o slice `regime` NÃO importa `mt5_integration`. O acoplamento é só pela
tabela de banco, populada pelo endpoint /mt5/candles (timeframe=D1).
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_SELECT = text(
    """
    SELECT close
    FROM cam_inspector_candles
    WHERE symbol = :symbol AND timeframe = :timeframe
    ORDER BY ts ASC
    """
)


async def get_close_series(
    session: AsyncSession, symbol: str, timeframe: str = "D1"
) -> list[float]:
    """Série de close em ordem cronológica. Vazia se não houver dados."""
    result = await session.execute(
        _SELECT, {"symbol": symbol.upper(), "timeframe": timeframe}
    )
    return [float(row[0]) for row in result.fetchall()]

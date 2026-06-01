"""
Schemas Pydantic da feature mt5_integration — SPEC v0.2 §4.1.

Art. 25o: toda resposta com posicao DEVE conter pnl_net.
Art. 11o: contracts e limitado a 2 (intocavel) — enforced via Pydantic Field.
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class MT5Tick(BaseModel):
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    volume: int
    ts_unix_ms: int


class MT5Position(BaseModel):
    symbol: str
    contracts: int = Field(ge=1, le=2)  # Art. 11o
    direction: Literal["LONG", "SHORT"]
    entry_price: Decimal
    current_price: Decimal
    pnl_gross: Decimal
    pnl_net: Decimal  # Art. 25o — sempre presente
    opened_at: datetime


class MT5BridgeStatus(BaseModel):
    state: Literal["ONLINE", "OFFLINE", "RECONNECTING"]
    last_heartbeat_at: datetime | None = None
    last_heartbeat_age_ms: int | None = None
    avg_latency_ms: float | None = None
    host: str
    pub_port: int
    req_port: int
    mt5_path: str | None = None


class ValidateIntentionRequest(BaseModel):
    asset: Literal["WIN", "WDO"]
    direction: Literal["LONG", "SHORT"]
    contracts: int = Field(ge=1, le=2)  # Art. 11o — intocavel
    intended_stop_loss_points: Decimal


class ValidateIntentionResponse(BaseModel):
    approved: bool
    reason: str | None = None
    validator: str | None = None


class ImportResult(BaseModel):
    imported: int
    duplicates: int
    errors: int


class MT5BridgeOfflinePayload(BaseModel):
    """R16.01 — resposta padronizada de endpoints quando bridge offline."""
    error: Literal["MT5_BRIDGE_OFFLINE"] = "MT5_BRIDGE_OFFLINE"
    since: datetime
    message: str = "Bridge MT5 desconectada — verificar EA no MT5 e reiniciar bridge."


# ---------------------------------------------------------------------------
# Inspetor de Ativo (ADR-014 / SPEC-Inspetor) — candles, símbolos, metadata
# ---------------------------------------------------------------------------

Timeframe = Literal["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]


class Candle(BaseModel):
    """Barra OHLCV. `time` em segundos unix (lightweight-charts usa UTCTimestamp)."""
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: int


class CandlesResponse(BaseModel):
    symbol: str
    timeframe: Timeframe
    candles: list[Candle]


class SymbolMeta(BaseModel):
    ticker: str
    mt5_symbol: str
    type: Literal["stock", "fii", "future", "unknown"]
    has_fundamentals: bool


class SymbolsResponse(BaseModel):
    symbols: list[str]

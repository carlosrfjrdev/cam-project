"""
Tipos ctypes do ProfitDLL — subconjunto READ-ONLY (market data).

Transcrito do SDK ProfitDLL (Exemplo Python, versão instalada 2026-06). Inclui
SÓ o necessário para ler negócios/ticks: structs de trade/asset + assinaturas de
callback. NENHUMA função/estrutura de roteamento de ordem é declarada aqui (o
bridge é read-only por construção).
"""
from __future__ import annotations

from ctypes import (
    WINFUNCTYPE,
    Structure,
    c_double,
    c_int,
    c_int32,
    c_longlong,
    c_size_t,
    c_ubyte,
    c_uint,
    c_ushort,
    c_void_p,
    c_wchar_p,
)
from enum import IntEnum

# Códigos de retorno relevantes (ver Manual ProfitDLL)
NL_OK = 0x00000000

# Flags de pacote do histórico de trades
TC_LAST_PACKET = 2


class TTradeType(IntEnum):
    """Tipo do negócio — campo agressor do tick."""

    CrossTrade = 1
    AggressorBuyer = 2   # agressor de COMPRA
    AggressorSeller = 3  # agressor de VENDA
    Auction = 4
    Unknown = 32


def aggressor_of(trade_type: int) -> str:
    """Mapeia TradeType → 'B' (comprador), 'S' (vendedor) ou '' (indefinido)."""
    if trade_type == TTradeType.AggressorBuyer:
        return "B"
    if trade_type == TTradeType.AggressorSeller:
        return "S"
    return ""


class SystemTime(Structure):
    _fields_ = [
        ("wYear", c_ushort),
        ("wMonth", c_ushort),
        ("wDayOfWeek", c_ushort),
        ("wDay", c_ushort),
        ("wHour", c_ushort),
        ("wMinute", c_ushort),
        ("wSecond", c_ushort),
        ("wMilliseconds", c_ushort),
    ]


class TAssetID(Structure):
    """AssetID 'legado' usado pelos callbacks de login (newDaily/progress/tinyBook)."""

    _fields_ = [
        ("ticker", c_wchar_p),
        ("bolsa", c_wchar_p),
        ("feed", c_int),
    ]


class TConnectorAssetIdentifierSafe(Structure):
    """AssetID dos callbacks de trade — ponteiros opacos (ler via cast)."""

    _fields_ = [
        ("Version", c_ubyte),
        ("Ticker", c_void_p),
        ("Exchange", c_void_p),
        ("FeedType", c_ubyte),
    ]


class TConnectorTrade(Structure):
    """Negócio decodificado por TranslateTrade — o tick com agressor."""

    _fields_ = [
        ("Version", c_ubyte),
        ("TradeDate", SystemTime),
        ("TradeNumber", c_uint),
        ("Price", c_double),
        ("Quantity", c_longlong),
        ("Volume", c_double),
        ("BuyAgent", c_int),
        ("SellAgent", c_int),
        ("TradeType", c_ubyte),  # ver TTradeType
    ]


# ---- assinaturas de callback (WINFUNCTYPE) ----

# trade ao vivo e histórico: (assetSafe, pTrade, flags)
TConnectorTradeCallback = WINFUNCTYPE(
    None, TConnectorAssetIdentifierSafe, c_size_t, c_uint
)

# estado de conexão/ativação: (nType, nResult)
TStateCallback = WINFUNCTYPE(None, c_int32, c_int32)

# callbacks exigidos por DLLInitializeMarketLogin mas não usados pelo bridge:
TProgressCallback = WINFUNCTYPE(None, TAssetID, c_int)
TTinyBookCallback = WINFUNCTYPE(None, TAssetID, c_double, c_int, c_int)
TNewDailyCallback = WINFUNCTYPE(
    None, TAssetID, c_wchar_p,
    c_double, c_double, c_double, c_double, c_double, c_double, c_double,
    c_double, c_double, c_double,
    c_int, c_int, c_int, c_int, c_int, c_int, c_int,
)

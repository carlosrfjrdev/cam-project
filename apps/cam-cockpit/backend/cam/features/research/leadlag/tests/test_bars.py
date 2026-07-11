"""Testes das barras canônicas determinísticas (R-10/R-11/R-12) — puros."""
from datetime import datetime

from cam._shared.research_kernel.bars import (
    Bar,
    aggressor_from_flags,
    derive,
)

_OPEN = datetime(2026, 6, 3, 9, 0, 0)


def _m1(minute: int, o: float, h: float, lo: float, c: float, vol: int) -> Bar:
    ts = datetime(2026, 6, 3, 9, minute, 0)
    return Bar(
        symbol="WIN$",
        timeframe="M1",
        ts_open=ts,
        ts_close=datetime(2026, 6, 3, 9, minute + 1, 0),
        session_date="2026-06-03",
        open=o,
        high=h,
        low=lo,
        close=c,
        volume=vol,
        trades=vol,
        financial=c * vol,
    )


def _five_m1() -> list[Bar]:
    return [
        _m1(0, 100, 105, 99, 104, 10),
        _m1(1, 104, 106, 103, 105, 20),
        _m1(2, 105, 108, 104, 107, 30),
        _m1(3, 107, 109, 106, 106, 15),
        _m1(4, 106, 110, 105, 109, 25),
    ]


def test_derive_m5_ohlcv_correto() -> None:
    bars = derive(_five_m1(), "M5", _OPEN)
    assert len(bars) == 1
    b = bars[0]
    assert b.timeframe == "M5"
    assert b.open == 100        # primeiro open
    assert b.high == 110        # max
    assert b.low == 99          # min
    assert b.close == 109       # último close
    assert b.volume == 100      # soma
    assert b.is_partial is False


def test_derive_e_deterministico() -> None:
    # R-12: rodar duas vezes produz barras idênticas.
    a = derive(_five_m1(), "M5", _OPEN)
    b = derive(_five_m1(), "M5", _OPEN)
    assert a == b


def test_derive_m1_e_identidade() -> None:
    m1 = _five_m1()
    assert derive(m1, "M1", _OPEN) == m1


def test_bucket_parcial_marcado() -> None:
    # 3 M1 num bucket M5 → incompleto → is_partial.
    bars = derive(_five_m1()[:3], "M5", _OPEN)
    assert bars[0].is_partial is True


def test_vwap_recomputado_do_m1() -> None:
    bars = derive(_five_m1(), "M5", _OPEN)
    # financial = Σ close*vol; vwap = financial/volume
    total_fin = sum(b.close * b.volume for b in _five_m1())
    assert abs(bars[0].vwap - total_fin / 100) < 1e-9


def test_dois_buckets_m5() -> None:
    m1 = _five_m1() + [_m1(5, 109, 112, 108, 111, 5)]
    bars = derive(m1, "M5", _OPEN)
    assert len(bars) == 2
    assert bars[1].open == 109
    assert bars[1].is_partial is True  # só 1 M1 no 2º bucket


def test_aggressor_from_flags() -> None:
    assert aggressor_from_flags(1080) == 1   # 1024+32(BUY)+16+8
    assert aggressor_from_flags(1112) == -1  # 1024+64(SELL)+16+8
    assert aggressor_from_flags(1026) == 0   # 1024+2(BID), sem trade
    assert aggressor_from_flags(0) == 0
    assert aggressor_from_flags(32 | 64) == 0  # ambos → indefinido (defensivo)

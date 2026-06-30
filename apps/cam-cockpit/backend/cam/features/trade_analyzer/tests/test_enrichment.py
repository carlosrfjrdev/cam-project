"""
Testes do enriquecimento (MAE/MFE + setup 1:3) após delegar ao research_kernel.

Garante que a refatoração (extração de excursion/simulate_bracket p/ _shared)
preservou o comportamento observável de enrich()/_simulate().
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from cam.features.trade_analyzer.enrichment import enrich
from cam.features.trade_analyzer.metrics import Trade

BR = ZoneInfo("America/Sao_Paulo")


def _trade(entry: float, exit_: float, direction: str) -> Trade:
    ab = datetime(2026, 6, 10, 10, 0, 0)
    fe = datetime(2026, 6, 10, 10, 5, 0)
    return Trade(
        asset="WINQ26", abertura=ab, fechamento=fe,
        lado="C" if direction == "LONG" else "V", qty=2, result=0.0,
        duration_s=300.0, entry_price=entry, exit_price=exit_, direction=direction,
    )


def _candles(entry_dt: datetime, highs_lows: list[tuple[float, float, float]]):
    """Candles M2 a partir da entrada: lista de (high, low, close)."""
    base = entry_dt.replace(tzinfo=BR).timestamp()
    return [
        {"ts": base + i * 120, "o": hl[2], "h": hl[0], "l": hl[1], "c": hl[2]}
        for i, hl in enumerate(highs_lows)
    ]


def test_enrich_long_bate_alvo_1x3():
    t = _trade(170000.0, 170150.0, "LONG")
    # sobe +350 (alvo 300 batido), sem violar stop 100 antes
    candles = _candles(t.abertura, [(170120, 169950, 170100), (170360, 170100, 170350)])
    out = enrich([t], candles)
    assert out["trades_avaliados"] == 1
    assert out["rr13_alvo"] == 1
    assert out["mfe_medio"] == 360.0  # 170360 - 170000


def test_enrich_long_bate_stop():
    t = _trade(170000.0, 169900.0, "LONG")
    candles = _candles(t.abertura, [(170010, 169880, 169900)])  # -120 < stop 100
    out = enrich([t], candles)
    assert out["rr13_stop"] == 1
    assert out["mae_medio"] == 120.0


def test_enrich_sem_candles_marca_no_data():
    t = _trade(170000.0, 170050.0, "LONG")
    out = enrich([t], [])
    assert out["trades_avaliados"] == 0  # no_data não conta
    assert out["trades"][0]["rr13"] == "no_data"


def test_enrich_mao_de_alface_detecta_lucro_pequeno_com_mfe_alto():
    # capturou pouco (+50) mas o preço ofereceu +400 (alface)
    t = _trade(170000.0, 170050.0, "LONG")
    candles = _candles(t.abertura, [(170400, 169990, 170050)])
    out = enrich([t], candles)
    assert out["mao_de_alface"] == 1
    assert out["pts_deixados_na_mesa"] >= 300.0

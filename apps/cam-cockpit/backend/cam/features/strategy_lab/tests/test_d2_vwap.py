"""Testes da D2 — VWAP Mean-Reversion fade (puro)."""
from datetime import datetime

from cam._shared.research_kernel.bars import Bar
from cam.features.strategy_lab.strategies.d2_vwap import D2Params, generate_signals


def _bar(mm, o, h, lo, c, vol=100):
    ts = datetime(2026, 6, 3, 9, mm)
    return Bar(
        symbol="WDO$", timeframe="M1", ts_open=ts, ts_close=ts,
        session_date="2026-06-03", open=o, high=h, low=lo, close=c, volume=vol,
    )


def test_d2_fade_short_na_esticada_para_cima() -> None:
    # preço estável ~100 por várias barras (VWAP~100, σ pequeno), depois dispara
    # bem acima → fade SHORT, alvo no VWAP, stop acima.
    bars = [_bar(m, 100, 100.5, 99.5, 100) for m in range(0, 35)]
    bars.append(_bar(35, 100, 130, 100, 128))  # esticada forte pra cima
    sigs = generate_signals(bars, D2Params(k_entry=2.0, k_stop=3.0, warmup_bars=30))
    assert len(sigs) >= 1
    s = sigs[0]
    assert s.side == "short"
    assert s.target_price < s.stop_price       # alvo (VWAP) abaixo do stop
    assert s.target_price < 128                # alvo abaixo do preço esticado


def test_d2_fade_long_na_esticada_para_baixo() -> None:
    bars = [_bar(m, 100, 100.5, 99.5, 100) for m in range(0, 35)]
    bars.append(_bar(35, 100, 100, 70, 72))    # esticada forte pra baixo
    sigs = generate_signals(bars, D2Params(k_entry=2.0, k_stop=3.0, warmup_bars=30))
    assert len(sigs) >= 1 and sigs[0].side == "long"
    assert sigs[0].stop_price < sigs[0].target_price  # stop abaixo do alvo (VWAP)


def test_d2_warmup_bloqueia_inicio_de_sessao() -> None:
    # esticada logo no começo (antes do warmup) não gera sinal.
    bars = [_bar(0, 100, 100, 99, 100), _bar(1, 100, 140, 100, 138)]
    assert generate_signals(bars, D2Params(warmup_bars=30)) == []


def test_d2_sem_esticada_sem_sinal() -> None:
    bars = [_bar(m, 100, 100.5, 99.5, 100) for m in range(0, 40)]
    assert generate_signals(bars, D2Params(k_entry=2.0, warmup_bars=30)) == []

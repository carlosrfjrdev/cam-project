"""Testes de estrutura + Fibonacci réu (R-26/R-27) — puros."""
from cam.features.research.leadlag.structure import (
    fib_levels,
    fractal_pivots,
    is_touch,
    nested_ab_test,
    touch_distance,
    zigzag,
)


def test_zigzag_detecta_reversao() -> None:
    # sobe até 110, cai para 99 (reversão > 5%) → confirma swing high
    prices = [100, 102, 105, 108, 110, 104, 99]
    pts = zigzag(prices, threshold=0.05)
    assert any(p.kind == "high" and p.price == 110 for p in pts)


def test_zigzag_serie_curta() -> None:
    assert zigzag([100.0], 0.05) == []


def test_fractal_pivot_topo() -> None:
    prices = [1, 2, 3, 5, 3, 2, 1]
    pts = fractal_pivots(prices, n=2)
    assert any(p.kind == "high" and p.index == 3 for p in pts)


def test_fib_levels_retracao_e_extensao() -> None:
    levels = fib_levels(100.0, 200.0)  # perna de 100 → 200, span 100
    assert abs(levels[0.5] - 150.0) < 1e-9       # 50% retração
    assert abs(levels[0.618] - (200 - 61.8)) < 1e-9
    assert abs(levels[1.618] - (200 + 61.8)) < 1e-9  # extensão


def test_touch_distance_e_is_touch() -> None:
    assert abs(touch_distance(100.0, 100.1, atr=1.0) - 0.1) < 1e-9
    assert is_touch(100.0, 100.1, atr=1.0, eta=0.25) is True
    assert is_touch(100.0, 105.0, atr=1.0, eta=0.25) is False


def test_touch_sem_atr() -> None:
    assert touch_distance(100.0, 100.0, atr=0.0) == float("inf")


def test_fib_fica_se_incrementa() -> None:
    # fib outcomes melhores que baseline → fib FICA
    baseline = [0.001] * 40
    fib = [0.01] * 40
    v = nested_ab_test(baseline, fib)
    assert v.fib_stays is True
    assert v.delta > 0


def test_fib_cai_se_nao_incrementa() -> None:
    baseline = [0.01] * 40
    fib = [0.001] * 40  # pior → fib CAI (era S/R reetiquetado)
    v = nested_ab_test(baseline, fib)
    assert v.fib_stays is False
    assert v.reason == "FIB_DROPPED_USE_BASELINE"


def test_fib_dado_insuficiente() -> None:
    v = nested_ab_test([0.01] * 5, [0.02] * 5, min_samples=30)
    assert v.fib_stays is False
    assert v.reason == "INSUFFICIENT_DATA"

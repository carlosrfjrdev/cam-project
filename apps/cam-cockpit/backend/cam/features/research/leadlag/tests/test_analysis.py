"""Testes do núcleo de análise lead-lag (R-19..R-31) — puros, sem I/O."""
import math

from cam.features.research.leadlag.analysis import (
    SignedTrade,
    count_trials,
    event_study,
    lag_profile,
    lagged_correlation,
    log_returns,
    ofi,
    ofi_normalized,
    pearson,
)


# ---- OFI (R-19) ----
def test_ofi_assinado() -> None:
    trades = [
        SignedTrade(1, +1, 10),
        SignedTrade(2, -1, 4),
        SignedTrade(3, +1, 6),
    ]
    assert ofi(trades) == 12.0  # 10 - 4 + 6


def test_ofi_normalizado_em_faixa() -> None:
    trades = [SignedTrade(1, +1, 10), SignedTrade(2, -1, 4)]
    x = ofi_normalized(trades)
    assert -1.0 <= x <= 1.0
    assert abs(x - (6 / 14)) < 1e-9


def test_ofi_indefinido_nao_contribui_no_numerador() -> None:
    trades = [SignedTrade(1, 0, 100), SignedTrade(2, +1, 10)]
    assert ofi(trades) == 10.0          # ε=0 não soma
    assert ofi_normalized(trades) == 10 / 110  # mas conta no volume total


def test_ofi_sem_volume() -> None:
    assert ofi_normalized([]) == 0.0


# ---- retornos e correlação ----
def test_log_returns() -> None:
    r = log_returns([100.0, 110.0, 121.0])
    assert len(r) == 2
    assert abs(r[0] - math.log(1.1)) < 1e-9


def test_pearson_perfeito() -> None:
    assert abs(pearson([1, 2, 3, 4], [2, 4, 6, 8]) - 1.0) < 1e-9


# ---- ANTI-LOOK-AHEAD (R-29) — a regra inegociável ----
def test_lagged_correlation_exige_delta_min_1() -> None:
    import pytest

    with pytest.raises(ValueError):
        lagged_correlation([1.0] * 50, [1.0] * 50, delta=0)


def test_lagged_correlation_alinha_sinal_passado_com_alvo_futuro() -> None:
    # sinal prediz o alvo δ passos à frente: target[t] = source[t-2]
    n = 80
    source = [float(i % 7) for i in range(n)]
    target = [0.0, 0.0] + source[:-2]  # target atrasado 2 em relação a source
    cell = lagged_correlation(source, target, delta=2, min_samples=10)
    assert cell.verdict == "OK"
    assert cell.correlation > 0.9  # forte no δ correto


def test_dado_insuficiente_e_primeira_classe() -> None:
    cell = lagged_correlation([1.0] * 5, [1.0] * 5, delta=1, min_samples=30)
    assert cell.verdict == "INSUFFICIENT_DATA"
    assert math.isnan(cell.correlation)


def test_lag_profile_cobre_grade() -> None:
    source = [float(i % 5) for i in range(100)]
    target = list(source)
    cells = lag_profile(source, target, [1, 2, 3, 5], min_samples=10)
    assert [c.delta for c in cells] == [1, 2, 3, 5]


# ---- event study (R-22) ----
def test_event_study_expectancia_liquida() -> None:
    # sinal forte positivo seguido de retorno positivo do alvo
    n = 200
    source = [0.0] * n
    target = [0.0] * n
    for t in range(60, n, 10):
        source[t] = 10.0          # spike → z alto → evento
        if t + 1 < n:
            target[t + 1] = 0.01  # alvo sobe logo depois
    es = event_study(source, target, horizon=1, kappa=2.0, cost=0.0,
                     zwindow=50, min_samples=5)
    assert es.verdict == "OK"
    assert es.mu_net > 0          # expectância líquida positiva
    assert 0.0 <= es.hit_rate <= 1.0


def test_event_study_custo_reduz_expectancia() -> None:
    n = 200
    source = [0.0] * n
    target = [0.0] * n
    for t in range(60, n, 10):
        source[t] = 10.0
        if t + 1 < n:
            target[t + 1] = 0.01
    livre = event_study(source, target, 1, 2.0, 0.0, 50, 5)
    com_custo = event_study(source, target, 1, 2.0, 0.005, 50, 5)
    assert com_custo.mu_net < livre.mu_net


def test_event_study_dado_insuficiente() -> None:
    es = event_study([0.0] * 10, [0.0] * 10, horizon=1, min_samples=30)
    assert es.verdict == "INSUFFICIENT_DATA"


# ---- trial accounting (R-30) ----
def test_count_trials() -> None:
    assert count_trials(3, 2, 5) == 30
    assert count_trials(3, 2, 5, reruns=2) == 60
    assert count_trials(0, 2, 5) == 0

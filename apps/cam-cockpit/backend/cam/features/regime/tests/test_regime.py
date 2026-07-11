"""Testes das funções puras do regime de Markov (sem I/O, sem rede)."""
from cam.features.regime import domain


def test_label_regimes_detects_uptrend() -> None:
    closes = [float(100 + i) for i in range(60)]  # alta monotônica
    labels = domain.label_regimes(closes, window=20, threshold=0.05)
    assert len(labels) == 40
    assert labels[-1] == "Bull"


def test_label_regimes_detects_downtrend() -> None:
    closes = [float(200 - i) for i in range(60)]
    labels = domain.label_regimes(closes, window=20, threshold=0.05)
    assert labels[-1] == "Bear"


def test_label_regimes_sideways() -> None:
    closes = [100.0 + (1 if i % 2 else -1) for i in range(60)]  # oscila ±1
    labels = domain.label_regimes(closes, window=20, threshold=0.05)
    assert set(labels) == {"Sideways"}


def test_transition_matrix_rows_sum_to_one() -> None:
    labels = ["Bull", "Bull", "Sideways", "Bear", "Bull", "Sideways"]
    m = domain.build_transition_matrix(labels)
    assert len(m) == 3
    for row in m:
        assert abs(sum(row) - 1.0) < 1e-9


def test_stationary_distribution_normalized() -> None:
    labels = ["Bull", "Sideways", "Bear", "Bull", "Sideways", "Bear", "Bull"]
    m = domain.build_transition_matrix(labels)
    stat = domain.stationary_distribution(m)
    assert abs(sum(stat) - 1.0) < 1e-6
    assert all(0.0 <= x <= 1.0 for x in stat)


def test_signal_in_range() -> None:
    labels = ["Bull", "Bull", "Sideways", "Bear", "Bull"]
    m = domain.build_transition_matrix(labels)
    sig = domain.signal_from_matrix(m, "Bull")
    assert -1.0 <= sig <= 1.0


def test_analyze_insufficient_data() -> None:
    result = domain.analyze([100.0, 101.0, 102.0], window=20)
    assert result["insufficient_data"] is True


def test_analyze_full_pipeline() -> None:
    closes = [float(100 + i) for i in range(80)]
    result = domain.analyze(closes, window=20, threshold=0.05)
    assert result["insufficient_data"] is False
    assert result["current_state"] in ("Bull", "Sideways", "Bear")
    assert result["states"] == ["Bull", "Sideways", "Bear"]
    assert abs(sum(result["stationary"].values()) - 1.0) < 1e-6
    assert -1.0 <= result["signal"] <= 1.0


def test_walk_forward_no_lookahead_keys() -> None:
    closes = [float(100 + (i % 7) - 3) for i in range(80)]
    wf = domain.walk_forward_backtest(closes, window=20, threshold=0.05)
    assert "sharpe" in wf
    assert "max_drawdown" in wf

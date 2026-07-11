"""Testes da varredura de grade stop×alvo e segmentação por regime."""
from __future__ import annotations

from cam._shared.research_kernel.bracket_optimizer import (
    TradeContext,
    best_cell,
    evaluate_by_segment,
    evaluate_grid,
)

T0 = 1_000_000.0


def _c(i: int, h: float, l: float, c: float) -> dict:
    return {"ts": T0 + i * 120, "o": c, "h": h, "l": l, "c": c}


def _runner(entry: float, regime: str) -> TradeContext:
    """Trade que corre forte a favor (LONG): bate alvos grandes, nunca o stop."""
    window = [_c(1, entry + 50, entry - 10, entry + 40),
              _c(2, entry + 400, entry + 40, entry + 380)]
    return TradeContext("LONG", entry, T0, window, regime=regime)


def _chop(entry: float, regime: str) -> TradeContext:
    """Trade lateral (LONG): cai antes de subir → stop curto morre, alvo nunca vem."""
    window = [_c(1, entry + 20, entry - 90, entry - 80),
              _c(2, entry - 80, entry - 95, entry - 90)]
    return TradeContext("LONG", entry, T0, window, regime=regime)


def test_grid_gera_cell_por_combinacao():
    trades = [_runner(170000, "TENDENCIA_ALTA")]
    grid = evaluate_grid(trades, stops=[50, 80], targets=[100, 300])
    assert len(grid) == 4  # 2 stops x 2 targets
    assert all(c.n == 1 for c in grid)


def test_runner_bate_alvo_grande_expectancia_positiva():
    trades = [_runner(170000, "TENDENCIA_ALTA")]
    grid = evaluate_grid(trades, stops=[80], targets=[300])
    cell = grid[0]
    assert cell.expectancy_pts == 300.0
    assert cell.target_hits == 1
    assert cell.stop_hits == 0


def test_chop_estopa_alvo_grande_expectancia_negativa():
    trades = [_chop(170000, "LATERAL")]
    grid = evaluate_grid(trades, stops=[80], targets=[300])
    cell = grid[0]
    assert cell.expectancy_pts == -80.0   # bateu stop 80
    assert cell.stop_hits == 1


def test_best_cell_escolhe_maior_expectancia():
    # alvo pequeno (40) é batido pelo runner no 1o candle (+50 de high) → +40
    # alvo grande (300) → +300. best = 300.
    trades = [_runner(170000, "TENDENCIA_ALTA")]
    grid = evaluate_grid(trades, stops=[80], targets=[40, 300])
    best = best_cell(grid)
    assert best is not None
    assert best.target_pts == 300


def test_segmentacao_por_regime_separa_edge():
    trades = [
        _runner(170000, "TENDENCIA_ALTA"),
        _runner(171000, "TENDENCIA_ALTA"),
        _chop(170500, "LATERAL"),
    ]
    segs = evaluate_by_segment(
        trades, stops=[80], targets=[300], key=lambda t: t.regime
    )
    by_name = {s.segment: s for s in segs}
    assert by_name["TENDENCIA_ALTA"].n == 2
    assert by_name["TENDENCIA_ALTA"].best.expectancy_pts == 300.0
    assert by_name["LATERAL"].best.expectancy_pts == -80.0


def test_min_trades_filtra_amostra_pequena():
    trades = [_runner(170000, "TENDENCIA_ALTA")]
    grid = evaluate_grid(trades, stops=[80], targets=[300])
    assert best_cell(grid, min_trades=5) is None  # só 1 trade < 5

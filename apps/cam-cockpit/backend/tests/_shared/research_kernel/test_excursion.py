"""Testes puros do motor de excursão (MAE/MFE) e simulação de bracket."""
from __future__ import annotations

from cam._shared.research_kernel.excursion import (
    excursion,
    select_window,
    simulate_bracket,
)

T0 = 1_000_000.0  # epoch base (segundos)


def _c(min_offset: float, o: float, h: float, l: float, c: float) -> dict:
    """Candle helper: ts = T0 + offset em minutos."""
    return {"ts": T0 + min_offset * 60.0, "o": o, "h": h, "l": l, "c": c}


# --- excursion -------------------------------------------------------------

def test_excursion_long_mae_mfe_e_tempos():
    entry = 100.0
    window = [
        _c(1, 100, 105, 98, 102),   # favor +5, adverso +2
        _c(2, 102, 110, 101, 109),  # favor +10 (novo MFE)
        _c(3, 109, 109, 92, 95),    # adverso +8 (novo MAE)
    ]
    ex = excursion(entry, "LONG", window, T0)
    assert ex.mfe_pts == 10.0
    assert ex.mae_pts == 8.0
    assert ex.time_to_mfe_min == 2.0
    assert ex.time_to_mae_min == 3.0
    assert ex.bars == 3


def test_excursion_short_inverte_favor_adverso():
    entry = 100.0
    window = [
        _c(1, 100, 102, 90, 92),    # short: favor = entry-low = +10
        _c(2, 92, 108, 91, 107),    # short: adverso = high-entry = +8
    ]
    ex = excursion(entry, "SHORT", window, T0)
    assert ex.mfe_pts == 10.0   # preço caiu 10 a favor do short
    assert ex.mae_pts == 8.0    # subiu 8 contra
    assert ex.time_to_mfe_min == 1.0


def test_excursion_janela_vazia_ou_sem_entrada():
    assert excursion(100.0, "LONG", [], T0).mfe_pts == 0.0
    assert excursion(0.0, "LONG", [_c(1, 1, 2, 0, 1)], T0).mae_pts == 0.0


# --- simulate_bracket ------------------------------------------------------

def test_bracket_long_bate_alvo():
    entry = 100.0
    window = [_c(1, 100, 101, 99, 100), _c(2, 100, 130, 100, 128)]
    out = simulate_bracket(entry, "LONG", window, T0, stop_pts=50, target_pts=20)
    assert out.exit_reason == "target"
    assert out.result_pts == 20.0
    assert out.minutes == 2.0


def test_bracket_long_bate_stop():
    entry = 100.0
    window = [_c(1, 100, 101, 40, 45)]
    out = simulate_bracket(entry, "LONG", window, T0, stop_pts=50, target_pts=300)
    assert out.exit_reason == "stop"
    assert out.result_pts == -50.0


def test_bracket_empate_intrabar_assume_stop():
    """Alvo e stop no MESMO candle → pessimista assume STOP."""
    entry = 100.0
    window = [_c(1, 100, 130, 40, 100)]  # toca +30 (alvo 20) E -60 (stop 50)
    out = simulate_bracket(entry, "LONG", window, T0, stop_pts=50, target_pts=20)
    assert out.exit_reason == "stop"
    assert out.result_pts == -50.0


def test_bracket_nada_bate_marca_no_ultimo_close():
    entry = 100.0
    window = [_c(1, 100, 105, 96, 103), _c(2, 103, 106, 99, 104)]
    out = simulate_bracket(entry, "LONG", window, T0, stop_pts=50, target_pts=50)
    assert out.exit_reason == "none"
    assert out.result_pts == 4.0   # 104 - 100
    assert out.minutes is None


def test_bracket_short_alvo_e_stop_corretos():
    entry = 100.0
    win_target = [_c(1, 100, 100, 70, 72)]   # cai 30 → alvo short 20
    assert simulate_bracket(entry, "SHORT", win_target, T0, 50, 20).exit_reason == "target"
    win_stop = [_c(1, 130, 160, 100, 155)]   # sobe 60 → stop short 50
    assert simulate_bracket(entry, "SHORT", win_stop, T0, 50, 300).exit_reason == "stop"


# --- select_window ---------------------------------------------------------

def test_select_window_recorta_por_ts():
    candles = [_c(0, 1, 1, 1, 1), _c(5, 1, 1, 1, 1), _c(10, 1, 1, 1, 1)]
    win = select_window(candles, T0 + 60, T0 + 6 * 60)  # entre min 1 e 6
    assert len(win) == 1
    assert win[0]["ts"] == T0 + 5 * 60

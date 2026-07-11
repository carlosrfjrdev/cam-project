"""Testes do motor MVP-bruto + D1 ORB-30 (R-11/R-15/R-16) — puros."""
from datetime import datetime

from cam._shared.research_kernel.bars import Bar
from cam.features.strategy_lab.backtest_engine import run_d1_backtest
from cam.features.strategy_lab.metrics import compute_metrics
from cam.features.strategy_lab.strategies.d1_orb30 import (
    D1Params,
    generate_signals,
)


def _bar(h, m, o, hi, lo, c, sym="WIN", date="2026-06-03"):
    ts = datetime(2026, 6, 3, h, m)
    return Bar(
        symbol=sym, timeframe="M5", ts_open=ts, ts_close=ts,
        session_date=date, open=o, high=hi, low=lo, close=c,
        volume=100, trades=100, financial=c * 100,
    )


def _session_long_breakout() -> list[Bar]:
    """Range 100-90 nos 30min; rompe pra cima; alvo batido."""
    return [
        # opening range 09:00-09:30 (6 barras M5): high 100, low 90
        _bar(9, 0, 95, 100, 90, 96),
        _bar(9, 5, 96, 99, 92, 97),
        _bar(9, 10, 97, 100, 95, 98),
        _bar(9, 15, 98, 99, 94, 97),
        _bar(9, 20, 97, 98, 93, 96),
        _bar(9, 25, 96, 99, 95, 98),
        # após o range: rompe acima de 100 (close 101) → sinal long em 09:30
        _bar(9, 30, 99, 101, 98, 101),
        # próxima barra: fill no open (102); range=10, alvo=100+10=110
        _bar(9, 35, 102, 108, 101, 107),
        _bar(9, 40, 107, 111, 106, 110),  # toca alvo 110
        _bar(9, 45, 110, 112, 108, 109),
    ]


def test_d1_gera_sinal_long_na_quebra() -> None:
    bars = _session_long_breakout()
    sigs = generate_signals(bars, D1Params(or_minutes=30))
    assert len(sigs) == 1
    assert sigs[0].side == "long"
    # stop = OR_low (90), alvo = OR_high + 1×range = 100 + 10 = 110
    assert sigs[0].stop_price == 90
    assert sigs[0].target_price == 110


def test_d1_fill_next_bar_open_e_alvo() -> None:
    bars = _session_long_breakout()
    sigs = generate_signals(bars, D1Params(or_minutes=30))
    trades = run_d1_backtest(bars, sigs, D1Params(or_minutes=30), point_value=1.0)
    assert len(trades) == 1
    t = trades[0]
    # fill no open da barra seguinte ao sinal = 102 (09:35)
    assert t.price_entry == 102
    # saída no alvo 110
    assert t.price_exit == 110
    assert t.exit_reason == "target"
    # pnl bruto = (110-102) × 1 × 1.0 = 8
    assert t.pnl_bruto == 8.0


def test_d1_sem_quebra_sem_trade() -> None:
    # range 90-100, preço fica dentro → nenhum sinal
    bars = [
        _bar(9, 0, 95, 100, 90, 96),
        _bar(9, 5, 96, 99, 92, 97),
        _bar(9, 30, 96, 99, 93, 95),  # dentro do range
        _bar(9, 35, 95, 98, 92, 94),
    ]
    sigs = generate_signals(bars, D1Params(or_minutes=30))
    assert sigs == []
    trades = run_d1_backtest(bars, sigs, D1Params(or_minutes=30))
    assert trades == []


def test_d1_stop_pior_caso_intrabar() -> None:
    """Barra que toca stop E alvo → stop primeiro (C5 pior caso)."""
    bars = _session_long_breakout()[:7]  # ...09:30 = barra do sinal (close 101)
    # 09:35 = fill no open (102); 09:40 = barra que toca alvo 110 E stop 90
    bars.append(_bar(9, 35, 102, 103, 101, 102))   # fill aqui (open 102)
    bars.append(_bar(9, 40, 102, 110, 89, 95))     # toca alvo 110 E stop 90
    sigs = generate_signals(bars, D1Params(or_minutes=30))
    trades = run_d1_backtest(bars, sigs, D1Params(or_minutes=30), point_value=1.0)
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop"
    assert trades[0].price_exit == 90  # stop, não alvo


def test_d1_sl_tp_estatico_relativo_a_entrada() -> None:
    """Modo estático: SL/TP fixos em pontos, relativos ao fill (não ao range)."""
    bars = _session_long_breakout()[:7]      # ...09:30 sinal (close 101)
    bars.append(_bar(9, 35, 102, 103, 101, 102))  # fill no open 102
    bars.append(_bar(9, 40, 102, 110, 101, 109))  # toca TP estatico (102+5=107)
    params = D1Params(or_minutes=30, stop_points=4.0, target_points=5.0)
    sigs = generate_signals(bars, params)
    assert len(sigs) == 1
    # sinal carrega pontos, NAO preco absoluto (resolvido no fill)
    assert sigs[0].stop_points == 4.0
    assert sigs[0].target_points == 5.0
    trades = run_d1_backtest(bars, sigs, params, point_value=1.0)
    assert len(trades) == 1
    t = trades[0]
    assert t.price_entry == 102
    # TP estatico = entrada + 5 = 107 (relativo a entrada, nao 110 do range)
    assert t.price_exit == 107
    assert t.exit_reason == "target"
    assert t.pnl_bruto == 5.0


def test_d1_sl_estatico_stop_relativo_a_entrada() -> None:
    """SL estatico relativo a entrada, pior caso intrabar."""
    bars = _session_long_breakout()[:7]
    bars.append(_bar(9, 35, 102, 103, 101, 102))   # fill no open 102
    bars.append(_bar(9, 40, 102, 110, 95, 96))     # toca SL estatico (102-4=98)
    params = D1Params(or_minutes=30, stop_points=4.0, target_points=20.0)
    sigs = generate_signals(bars, params)
    trades = run_d1_backtest(bars, sigs, params, point_value=1.0)
    assert trades[0].exit_reason == "stop"
    assert trades[0].price_exit == 98  # entrada 102 - 4 pontos


def test_d1_stop_movel_trava_lucro_no_pico() -> None:
    """Stop móvel (R-15c): segue o pico e sai travando lucro, sem TP fixo."""
    bars = _session_long_breakout()[:7]            # ...09:30 sinal (close 101)
    bars.append(_bar(9, 35, 102, 103, 101, 102))   # fill no open 102
    # sobe ao pico 120 → trailing sobe o stop para 120-4=116
    bars.append(_bar(9, 40, 118, 120, 110, 118))
    # recua e toca 116 → sai no stop móvel travando +14 (não no SL inicial 82)
    bars.append(_bar(9, 45, 117, 119, 114, 115))
    params = D1Params(
        or_minutes=30, stop_points=20, target_points=0, trail_points=4
    )
    sigs = generate_signals(bars, params)
    assert sigs[0].trail_points == 4
    trades = run_d1_backtest(bars, sigs, params, point_value=1.0)
    assert len(trades) == 1
    t = trades[0]
    assert t.exit_reason == "stop"
    assert t.price_exit == 116          # stop móvel (120 - 4), não o SL inicial 82
    assert t.pnl_bruto == 14.0          # lucro travado pelo trailing


def test_d1_sem_tp_fixo_quando_target_zero() -> None:
    """target_points=0 ⇒ sem TP fixo (has_target False); só SL/trailing/sessão."""
    bars = _session_long_breakout()[:7]
    bars.append(_bar(9, 35, 102, 103, 101, 102))    # fill 102
    bars.append(_bar(9, 40, 102, 200, 101, 150))    # subiria muito; sem TP, segue
    bars.append(_bar(9, 55, 150, 151, 80, 81))      # toca SL inicial 82 (102-20)
    params = D1Params(or_minutes=30, stop_points=20, target_points=0, trail_points=0)
    sigs = generate_signals(bars, params)
    trades = run_d1_backtest(bars, sigs, params, point_value=1.0)
    assert trades[0].exit_reason == "stop"   # nunca saiu por "target"
    assert trades[0].price_exit == 82


def test_d1_gate_tendencia() -> None:
    """Gate de regime (R-15d): só entra a favor da tendência de N barras."""
    bars = _session_long_breakout()[:7]  # sinal long no idx 6 (09:30, close 101)
    # ref idx 6-3=3 (09:15, close 97) < 101 → alta confirmada → long PERMITIDO.
    sig_up = generate_signals(bars, D1Params(or_minutes=30, trend_filter_bars=3))
    assert len(sig_up) == 1 and sig_up[0].side == "long"
    # lookback maior que o histórico → sem como confirmar tendência → BLOQUEIA.
    sig_block = generate_signals(bars, D1Params(or_minutes=30, trend_filter_bars=999))
    assert sig_block == []


def test_d1_min_or_points_suprime_dia_de_chop() -> None:
    """Gate A (R-15d): dia com range do OR menor que o mínimo não opera."""
    bars = _session_long_breakout()  # OR range = 100-90 = 10
    # range mínimo 5 < 10 → opera normalmente.
    assert len(generate_signals(bars, D1Params(or_minutes=30, min_or_points=5))) == 1
    # range mínimo 50 > 10 → dia suprimido (chop).
    assert generate_signals(bars, D1Params(or_minutes=30, min_or_points=50)) == []


def test_metricas_brutas() -> None:
    bars = _session_long_breakout()
    sigs = generate_signals(bars, D1Params(or_minutes=30))
    trades = run_d1_backtest(bars, sigs, D1Params(or_minutes=30), point_value=1.0)
    m = compute_metrics(trades)
    assert m.n_trades == 1
    assert m.wins == 1
    assert m.win_rate == 1.0
    assert m.pnl_bruto_total == 8.0

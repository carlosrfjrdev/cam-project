"""Testes do otimizador (R-05/07/08) e da paridade (R-29/31) — puros."""
from cam.features.strategy_lab.optimizer import optimize
from cam.features.strategy_lab.parity import compare


# ---- otimizador ----
def test_otimizador_sugere_melhor_com_amostra() -> None:
    # score = -(x-3)^2 (ótimo em x=3); n_trades sempre suficiente
    space = {"x": [1, 2, 3, 4, 5]}

    def ev(p):
        return (-((p["x"] - 3) ** 2) + 10, 100)

    r = optimize(space, ev, method="grid", min_trades=20)
    assert r.verdict == "SUGGEST"
    assert r.best_params["x"] == 3
    assert r.n_trials == 5


def test_otimizador_dado_insuficiente() -> None:
    space = {"x": [1, 2, 3]}

    def ev(p):
        return (5.0, 2)  # poucos trades

    r = optimize(space, ev, method="grid", min_trades=20)
    assert r.verdict == "INSUFFICIENT_DATA"
    assert r.min_samples_ok is False


def test_otimizador_random_deterministico_com_seed() -> None:
    space = {"x": list(range(20)), "y": list(range(20))}

    def ev(p):
        return (float(p["x"] + p["y"]), 100)

    a = optimize(space, ev, method="random", random_n=10, seed=7)
    b = optimize(space, ev, method="random", random_n=10, seed=7)
    assert a.best_params == b.best_params  # determinístico


# ---- paridade ----
def _trade(pair_id, ts, leg, sym, pe, px, qty, reason, vol):
    return {
        "pair_id": pair_id, "ts_entry": ts, "leg": leg, "symbol": sym,
        "price_entry": pe, "price_exit": px, "qty": qty,
        "exit_reason": reason, "volume_financeiro": vol,
    }


def test_paridade_pass_identico() -> None:
    led = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "target", 212)]
    r = compare(led, list(led), tick_size=5.0)
    assert r.verdict == "PASS"
    assert r.matched == 1


def test_paridade_pass_dentro_de_1_tick() -> None:
    py = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "target", 212)]
    ea = [_trade(1, "2026-06-03T09:35", "long", "WIN", 104, 113, 1, "target", 212)]
    # tick=5 → 102 vs 104 (≤5) e 110 vs 113 (≤5) passam; volume idêntico
    r = compare(py, ea, tick_size=5.0)
    assert r.verdict == "PASS"


def test_paridade_fail_sinal_ausente() -> None:
    py = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "target", 212)]
    ea = []
    r = compare(py, ea, tick_size=5.0)
    assert r.verdict == "FAIL"
    assert any(d.dimension == "signal" for d in r.divergences)


def test_paridade_fail_preco_fora_de_tick() -> None:
    py = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "target", 212)]
    ea = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 130, 1, "target", 212)]
    r = compare(py, ea, tick_size=5.0)  # saída 110 vs 130 > 5
    assert r.verdict == "FAIL"
    assert any(d.dimension == "price_exit" for d in r.divergences)


def test_paridade_fail_motivo_saida() -> None:
    py = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "target", 212)]
    ea = [_trade(1, "2026-06-03T09:35", "long", "WIN", 102, 110, 1, "stop", 212)]
    r = compare(py, ea, tick_size=5.0)
    assert r.verdict == "FAIL"
    assert any(d.dimension == "exit_reason" for d in r.divergences)

"""
Helpers PUROS do service + registry (sem banco) — alinhamento de paridade Py↔EA.

O risco crítico da dupla implementação é o ledger do Python e o do EA não casarem
por formato de timestamp. `canon_ts` normaliza ambos ao mesmo "YYYY-MM-DDTHH:MM:SS"
que o EA emite — estes testes blindam esse contrato.
"""
from datetime import datetime

from cam.features.strategy_lab import registry
from cam.features.strategy_lab.parity import compare
from cam.features.strategy_lab.service import canon_ts, legs_to_parity_dicts


def test_canon_ts_datetime() -> None:
    assert canon_ts(datetime(2026, 6, 3, 9, 35, 0)) == "2026-06-03T09:35:00"


def test_canon_ts_iso_string_do_ea() -> None:
    # formato exato emitido por cam_d1_orb30.mq5 FmtTs()
    assert canon_ts("2026-06-03T09:35:00") == "2026-06-03T09:35:00"


def test_canon_ts_com_timezone_e_espaco() -> None:
    # ts vindo do Postgres (TIMESTAMPTZ) como string com offset e espaço
    assert canon_ts("2026-06-03 09:35:00+00") == "2026-06-03T09:35:00"


def test_canon_ts_sem_segundos() -> None:
    assert canon_ts("2026-06-03T09:35") == "2026-06-03T09:35:00"


def test_paridade_alinha_db_e_ea_apos_normalizacao() -> None:
    # lado Python: ts como datetime (vindo do DB). Lado EA: string ISO.
    py_db = [{
        "pair_id": 0, "ts_entry": datetime(2026, 6, 3, 9, 35), "leg": "long",
        "symbol": "WIN$", "price_entry": 102.0, "price_exit": 110.0, "qty": 1,
        "exit_reason": "target", "volume_financeiro": 42.4,
    }]
    ea = [{
        "pair_id": 0, "ts_entry": "2026-06-03T09:35:00", "leg": "long",
        "symbol": "WIN$", "price_entry": 102.0, "price_exit": 110.0, "qty": 1,
        "exit_reason": "target", "volume_financeiro": 42.4,
    }]
    report = compare(
        legs_to_parity_dicts(py_db), legs_to_parity_dicts(ea), tick_size=5.0
    )
    assert report.verdict == "PASS"
    assert report.matched == 1


def test_registry_d1_runnable_e_tem_param_space() -> None:
    d1 = registry.get("d1")
    assert d1 is not None
    assert d1.runnable is True
    assert "stop_points" in d1.param_space
    assert "trail_points" in d1.param_space
    # D1 do produto usa SL inicial + stop movel (trailing) por padrao
    assert d1.default_params["stop_points"] > 0
    assert d1.default_params["trail_points"] > 0


def test_registry_lista_catalogo_com_nao_runnable() -> None:
    ids = {s.id for s in registry.list_strategies()}
    assert {"D1", "D2", "D3", "V1", "V2", "S1", "S2", "LS1", "LS2", "LS3"} <= ids
    # D1 e D2 (derivativos single-symbol) são runnable; pares/multi = Onda 2.
    runnable = {s.id for s in registry.list_strategies() if s.runnable}
    assert runnable == {"D1", "D2"}
    assert registry.get("D3").runnable is False


def test_registry_run_d1_produz_ledger() -> None:
    # smoke: roda D1 sobre barras sintéticas mínimas via registry.run.
    from datetime import time

    from cam._shared.research_kernel.bars import Bar

    def bar(hh, mm, o, h, lo, c):
        return Bar(
            symbol="WIN$", timeframe="M1",
            ts_open=datetime(2026, 6, 3, hh, mm),
            ts_close=datetime(2026, 6, 3, hh, mm),
            session_date="2026-06-03",
            open=o, high=h, low=lo, close=c, volume=1,
        )

    # OR 09:00-09:30 estreito; quebra para cima às 09:35; entra 09:36.
    bars = [bar(9, 0, 100, 101, 99, 100), bar(9, 1, 100, 101, 99, 100)]
    bars.append(bar(9, 35, 100, 105, 100, 104))   # close 104 > or_high 101 → long
    bars.append(bar(9, 36, 104, 106, 103, 105))   # entrada no open 104
    bars.append(bar(9, 37, 105, 120, 104, 119))   # toca alvo (101+ (101-99)=103)
    _ = time  # silencia import não-usado em alguns linters
    # gate de tendência off (só 5 barras sintéticas) + range mode p/ o smoke.
    legs = registry.run(
        "D1", bars,
        {"or_minutes": 30, "target_r": 1.0, "stop_points": 0, "trend_filter_bars": 0},
        0.20, 1,
    )
    assert len(legs) >= 1
    assert legs[0].leg.value == "long"

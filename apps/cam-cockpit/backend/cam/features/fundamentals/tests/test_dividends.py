"""Testes das projeções de dividendo (puras, sem rede) — SPEC-Inspetor R-14."""
from datetime import UTC, datetime

from cam.features.fundamentals.dividends import project_dividends


def _now() -> datetime:
    return datetime(2026, 6, 1, tzinfo=UTC)


def test_run_rate_sums_last_12_months() -> None:
    divs = [
        {"date": "2026-03-15", "type": "DIVIDEND", "value": 1.0},
        {"date": "2025-09-15", "type": "JCP", "value": 0.5},
        {"date": "2024-01-15", "type": "DIVIDEND", "value": 9.0},  # fora de 12m
    ]
    proj = project_dividends(divs, price=20.0, now=_now())
    assert proj["run_rate_12m"]["annual"] == 1.5
    assert proj["run_rate_12m"]["yield"] == round(1.5 / 20.0, 4)
    assert proj["run_rate_12m"]["label"] == "estimativa"


def test_dy_avg_uses_complete_years() -> None:
    divs = [
        {"date": "2023-05-01", "type": "DIVIDEND", "value": 2.0},
        {"date": "2024-05-01", "type": "DIVIDEND", "value": 4.0},
        {"date": "2025-05-01", "type": "DIVIDEND", "value": 6.0},
        {"date": "2026-05-01", "type": "DIVIDEND", "value": 99.0},  # ano corrente: ignorado
    ]
    proj = project_dividends(divs, price=50.0, now=_now())
    # média de 2023/2024/2025 = (2+4+6)/3 = 4.0
    assert proj["dy_avg_3_5y"]["annual"] == 4.0
    assert 2026 not in proj["dy_avg_3_5y"]["years_used"]


def test_no_price_yields_none() -> None:
    divs = [{"date": "2026-03-15", "type": "DIVIDEND", "value": 1.0}]
    proj = project_dividends(divs, price=None, now=_now())
    assert proj["run_rate_12m"]["yield"] is None


def test_empty_dividends() -> None:
    proj = project_dividends([], price=10.0, now=_now())
    assert proj["run_rate_12m"]["annual"] is None
    assert proj["dy_avg_3_5y"]["annual"] is None

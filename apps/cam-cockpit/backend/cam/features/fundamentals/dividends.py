"""
Projeção de dividendos — 2 modelos lado a lado (SPEC-Inspetor R-14).

Ambos rotulados "estimativa". Funções puras (testáveis sem rede):
- Modelo A — Run-rate 12m: soma dos proventos dos últimos 12 meses.
- Modelo B — DY-médio histórico: média anual dos proventos nos últimos 3–5 anos.

`yield` é calculado sobre o preço atual quando disponível.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any


def _parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    s = str(value)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[: len(fmt) + 6], fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def project_dividends(
    dividends: list[dict[str, Any]],
    price: float | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """
    Retorna as 2 projeções. Cada uma: {annual, yield, label}.
    Sem dados suficientes → annual=None.
    """
    now = now or datetime.now(UTC)
    cutoff_12m = now - timedelta(days=365)

    # Modelo A — run-rate 12 meses
    run_rate = 0.0
    has_12m = False
    # Modelo B — totais por ano
    yearly: dict[int, float] = defaultdict(float)

    for d in dividends:
        dt = _parse_date(d.get("date"))
        val = _num(d.get("value"))
        if dt is None or val is None:
            continue
        if dt >= cutoff_12m:
            run_rate += val
            has_12m = True
        yearly[dt.year] += val

    def _yield(annual: float | None) -> float | None:
        if annual is None or not price:
            return None
        return round(annual / price, 4)

    run_rate_annual = round(run_rate, 4) if has_12m else None

    # média dos últimos 3–5 anos completos disponíveis (exclui ano corrente parcial)
    years = sorted((y for y in yearly if y < now.year), reverse=True)[:5]
    avg_annual = None
    if years:
        avg_annual = round(sum(yearly[y] for y in years) / len(years), 4)

    return {
        "run_rate_12m": {
            "annual": run_rate_annual,
            "yield": _yield(run_rate_annual),
            "label": "estimativa",
        },
        "dy_avg_3_5y": {
            "annual": avg_annual,
            "yield": _yield(avg_annual),
            "label": "estimativa",
            "years_used": years,
        },
    }

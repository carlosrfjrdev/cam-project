"""
Carteira Hard Policy Engine — TASK-033 (BL-F SPEC v0.4).

Avalia uma holding contra critérios fundamentalistas e produz **alertas**
(R6.04). **Nunca bloqueia operação** — apenas sinaliza (R-13).

Critérios canônicos:
  - DY < 4%        → alerta nível 1 ("baixo DY para Carteira Hard")
  - P/L > 25       → alerta nível 2 ("valuation alto")
  - Dívida_Liq/EBITDA > 3 → alerta nível 3 ("endividamento alto")
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class PolicyAlert:
    level: int
    code: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


DY_MIN = Decimal("0.04")          # 4%
PL_MAX = Decimal("25")
DIV_LIQ_EBITDA_MAX = Decimal("3")


def evaluate_holding(
    holding: dict[str, Any],
    fundamentals: dict[str, Any] | None,
) -> list[PolicyAlert]:
    """
    Recebe dict de holding + snapshot de fundamentals e retorna alertas.

    `fundamentals` pode ser None se não houver snapshot — retorna alerta de
    cobertura ausente (nível 1).
    """
    alerts: list[PolicyAlert] = []
    if fundamentals is None:
        return [
            PolicyAlert(
                level=1,
                code="NO_FUNDAMENTALS",
                message=(
                    f"Sem snapshot fundamentalista para {holding.get('ticker')}."
                ),
                suggestion="Coletar dados via Multi-Source Collector (T034).",
            )
        ]

    dy = fundamentals.get("dy")
    pl = fundamentals.get("pl")
    div_liq_ebitda = fundamentals.get("div_liq_ebitda")

    if dy is not None and Decimal(str(dy)) < DY_MIN:
        alerts.append(
            PolicyAlert(
                level=1,
                code="DY_LOW",
                message=(
                    f"DY de {dy} abaixo de {DY_MIN} para Carteira Hard."
                ),
                suggestion="Reavaliar tese de dividendos.",
            )
        )

    if pl is not None and Decimal(str(pl)) > PL_MAX:
        alerts.append(
            PolicyAlert(
                level=2,
                code="VALUATION_HIGH",
                message=f"P/L {pl} acima de {PL_MAX}.",
                suggestion="Verificar valuation antes de aumentar exposição.",
            )
        )

    if div_liq_ebitda is not None and Decimal(str(div_liq_ebitda)) > DIV_LIQ_EBITDA_MAX:
        alerts.append(
            PolicyAlert(
                level=3,
                code="LEVERAGE_HIGH",
                message=(
                    f"Dívida líq/EBITDA {div_liq_ebitda} acima de {DIV_LIQ_EBITDA_MAX}."
                ),
                suggestion="Endividamento alto — risco de calote em ciclo adverso.",
            )
        )

    return alerts


def is_blocking(alerts: list[PolicyAlert]) -> bool:
    """
    Sempre retorna False. R-13: policy alerts nunca bloqueiam operação.
    """
    return False

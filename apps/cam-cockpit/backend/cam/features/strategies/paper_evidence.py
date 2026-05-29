"""
TASK-019 (BL-C) — Validador de promoção paper_ok.

Promoção a `paper_ok` exige:
  - ≥ 100 paper trades aprovados pela estratégia.
  - aderência média ≥ 0.95.

Implementação consulta `cam_paper_trades` filtrando por strategy_id.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam.features.strategies.domain import StrategyStatus
from cam.features.strategies.evidence import EvidencePack

MIN_PAPER_TRADES = 100
MIN_ADHERENCE = Decimal("0.95")


class PaperOkPrerequisitesError(ValueError):
    """Pré-requisitos de paper_ok não satisfeitos."""


async def build_paper_evidence(
    session: AsyncSession, strategy_id: UUID
) -> EvidencePack:
    """
    Consulta `cam_paper_trades` e monta EvidencePack para PAPER_OK.

    Levanta `PaperOkPrerequisitesError` se < 100 trades aprovados ou aderência
    média < 0.95.
    """
    result = await session.execute(
        text(
            "SELECT COUNT(*) AS total, "
            "       COUNT(*) FILTER (WHERE risk_decision = 'APPROVED') AS approved, "
            "       AVG(adherence) AS avg_adherence "
            "FROM cam_paper_trades WHERE strategy_id = :sid"
        ),
        {"sid": str(strategy_id)},
    )
    row = result.fetchone()
    total = int(row[0]) if row[0] is not None else 0
    approved = int(row[1]) if row[1] is not None else 0
    avg_adh = Decimal(str(row[2])) if row[2] is not None else Decimal("0")

    missing = []
    if approved < MIN_PAPER_TRADES:
        missing.append(
            f"trades_approved={approved} < {MIN_PAPER_TRADES}"
        )
    if avg_adh < MIN_ADHERENCE:
        missing.append(f"adherence={avg_adh} < {MIN_ADHERENCE}")
    if missing:
        raise PaperOkPrerequisitesError(
            "Promoção paper_ok bloqueada: " + " | ".join(missing)
        )

    paper_results = [f"paper_trade_count={approved}"]
    return EvidencePack(
        strategy_id=strategy_id,
        status_target=StrategyStatus.PAPER_OK,
        paper_results=paper_results,
        adherence=avg_adh,
        custom_metrics={
            "total_paper_trades": total,
            "approved_paper_trades": approved,
        },
    )

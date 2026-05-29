"""
Holdings HTTP router — TASK-021 (BL-D).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.infra import get_db_session
from cam.features.ledger.holdings import (
    HoldingIn,
    HoldingsRepository,
    HoldingValidationError,
)

router = APIRouter(prefix="/api/v1/carteira-hard", tags=["carteira-hard"])


class HoldingInBody(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    quantity: Decimal = Field(..., gt=0)
    avg_price: Decimal = Field(..., gt=0)
    asset_class: str = "equity"
    acquired_at: datetime | None = None
    source: str = "MANUAL_UI"

    @field_validator("source")
    @classmethod
    def _check_source(cls, v: str) -> str:
        if v not in ("MANUAL_UI", "GENIAL_IMPORT"):
            raise ValueError("source deve ser MANUAL_UI ou GENIAL_IMPORT")
        return v


class HoldingOut(BaseModel):
    id: str
    ticker: str
    quantity: Decimal
    avg_price: Decimal
    source: str


@router.post("/holdings", status_code=status.HTTP_201_CREATED)
async def create_holding(
    body: HoldingInBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    repo = HoldingsRepository()
    try:
        sid = await repo.create(
            session,
            HoldingIn(
                ticker=body.ticker,
                quantity=body.quantity,
                avg_price=body.avg_price,
                asset_class=body.asset_class,
                acquired_at=body.acquired_at,
                source=body.source,
            ),
        )
    except HoldingValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err)
        ) from err
    if sid is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Holding duplicado (hash) — já registrado.",
        )
    return {"id": str(sid), "ticker": body.ticker.upper(),
            "quantity": str(body.quantity), "avg_price": str(body.avg_price),
            "source": body.source}


@router.get("/holdings")
async def list_holdings(
    session: AsyncSession = Depends(get_db_session),
) -> list[dict[str, Any]]:
    repo = HoldingsRepository()
    rows = await repo.list_all(session)
    return [
        {
            "id": str(r["id"]),
            "ticker": r["ticker"],
            "asset_class": r["asset_class"],
            "quantity": str(r["quantity"]),
            "avg_price": str(r["avg_price"]),
            "source": r["source"],
        }
        for r in rows
    ]

"""
Router FastAPI da feature fiscal.

Endpoints:
    GET   /api/v1/fiscal/apuration/{month}        → apuração mensal
    GET   /api/v1/fiscal/darfs                     → listagem de DARFs
    PATCH /api/v1/fiscal/darfs/{id}/mark-paid      → marcar como paga
    GET   /api/v1/fiscal/compliance                → status de compliance
    GET   /api/v1/fiscal/summary                   → resumo operacional

Arts. 24º, 25º, 26º, 27º da Constituição.
"""
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from cam.features.fiscal.domain import (
    Darf,
    DarfStatus,
    FiscalApuration,
)
from cam.features.fiscal.service import FiscalService

router = APIRouter(prefix="/api/v1/fiscal", tags=["fiscal"])

# ---------------------------------------------------------------------------
# Repositório em memória — para uso sem banco (testes e modo offline)
# ---------------------------------------------------------------------------


class _InMemoryFiscalRepo:
    def __init__(self) -> None:
        self._darfs: dict[str, Darf] = {}
        self._provision: Decimal = Decimal("0")
        self._gross: Decimal = Decimal("0")

    async def update_monthly_provision(
        self,
        tax_provisioned: Decimal,
        result_gross: Decimal,
        entry_id: str,
    ) -> None:
        self._provision += tax_provisioned
        self._gross += result_gross

    async def has_overdue_darf(self) -> bool:
        return any(d.status == DarfStatus.OVERDUE for d in self._darfs.values())

    async def get_apuration(self, month: str) -> FiscalApuration:
        from cam._shared.domain.primitives import Money
        return FiscalApuration(
            month=month,
            gross_result=Money(self._gross),
            costs=Money(Decimal("0")),
            irrf_retained=Money(Decimal("0")),
            loss_compensation=Money(Decimal("0")),
        )

    async def save_darf(self, darf: Darf) -> str:
        import uuid
        darf_id = str(uuid.uuid4())
        self._darfs[darf_id] = darf
        return darf_id

    async def get_darf(self, darf_id: str) -> Darf | None:
        return self._darfs.get(darf_id)

    async def list_darfs(self) -> list[Darf]:
        return list(self._darfs.values())


_repo = _InMemoryFiscalRepo()
_service = FiscalService(repo=_repo)


@router.get("/apuration/{month}")
async def get_apuration(month: str) -> dict:
    """Apuração fiscal do mês (formato YYYY-MM)."""
    ap = await _service.get_apuration(month=month)
    return {
        "month": ap.month,
        "gross_result": str(ap.gross_result.amount),
        "net_result": str(ap.net_result.amount),
        "taxable_base": str(ap.taxable_base.amount),
        "ir_due": str(ap.ir_due.amount),
        "darf_value": str(ap.darf_value.amount),
    }


@router.get("/darfs")
async def list_darfs() -> list[dict]:
    """Lista todas as DARFs com status."""
    darfs = await _service.list_darfs()
    return [
        {
            "month": d.month,
            "value": str(d.value.amount),
            "due_date": d.due_date,
            "status": d.status.value,
            "paid_at": d.paid_at,
            "is_compliant": d.is_compliant(),
        }
        for d in darfs
    ]


@router.patch("/darfs/{darf_id}/mark-paid")
async def mark_darf_paid(darf_id: str) -> dict:
    """
    Marca DARF como paga.

    Após pagamento: tax_compliance=True → Risk Engine desbloqueia (Art. 26º).
    Publica `DarfPaid` no event bus — harvest service recalcula snapshot (TD-005 SPEC v0.3).
    """
    try:
        darf = await _service.mark_darf_paid(darf_id=darf_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # T-TD-005 — publica evento DarfPaid (lifespan inscreve harvest_service)
    from cam._shared.events import event_bus
    from cam.features.fiscal.events import DarfPaid
    await event_bus.publish(DarfPaid(month=darf.month, value_brl=str(getattr(darf, "value", "0"))))

    return {
        "month": darf.month,
        "status": darf.status.value,
        "paid_at": darf.paid_at,
    }


@router.get("/compliance")
async def get_compliance() -> dict:
    """
    Status de compliance fiscal atual.

    False se há DARF OVERDUE — Risk Engine bloqueia operações (Art. 26º).
    """
    compliant = await _service.check_tax_compliance()
    return {
        "tax_compliance": compliant,
        "message": (
            "OK" if compliant else "DARF OVERDUE — operações bloqueadas (Art. 26º)"
        ),
    }


@router.get("/summary")
async def get_summary() -> dict:
    """Resumo fiscal para a UI operacional."""
    return await _service.get_current_month_summary()

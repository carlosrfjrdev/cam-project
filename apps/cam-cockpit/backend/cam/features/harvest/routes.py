"""
Router FastAPI da feature harvest + ledger de capital.

Endpoints:
    GET  /api/v1/harvest/proposal/{month}  → proposta de harvest do mês
    POST /api/v1/harvest/execute           → executar harvest (gate Founder)
    GET  /api/v1/harvest/history           → histórico de harvests executados
    GET  /api/v1/ledger/buckets            → saldos atuais dos 3 buckets

Arts. 21º, 22º da Constituição.
REGRA: POST /execute requer founder_approved=True (R4.07).
"""
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cam._shared.domain.primitives import Money
from cam.features.harvest.domain import (
    BUCKET_BASELINE,
    HarvestProposal,
)
from cam.features.harvest.service import HarvestService

router = APIRouter(tags=["harvest"])

# Router separado para /ledger — mesmo módulo mas prefixo diferente
ledger_router = APIRouter(prefix="/api/v1/ledger", tags=["ledger"])


# ---------------------------------------------------------------------------
# Repositório em memória — para uso sem banco (testes e modo offline)
# ---------------------------------------------------------------------------


class _InMemoryHarvestRepo:
    def __init__(self) -> None:
        self._proposals: dict[str, HarvestProposal] = {}
        self._history: list[dict] = []
        self._bucket_derivativo = Money(Decimal("3000.00"))  # começa na baseline
        self._bucket_buffer = Money(Decimal("0.00"))
        self._bucket_carteira = Money(Decimal("0.00"))

    async def get_net_monthly_profit(self, month: str) -> Money:
        return Money(Decimal("0"))

    async def get_buffer_current(self) -> Money:
        return self._bucket_buffer

    async def get_bucket_derivativo_current(self) -> Money:
        return self._bucket_derivativo

    async def get_bucket_derivativo_baseline(self) -> Money:
        return Money(BUCKET_BASELINE)

    async def get_bucket_balances(self) -> dict:
        return {
            "DERIVATIVO": str(self._bucket_derivativo.amount),
            "BUFFER": str(self._bucket_buffer.amount),
            "CARTEIRA_HARD": str(self._bucket_carteira.amount),
        }

    async def save_proposal(self, month: str, proposal: HarvestProposal) -> str:
        import uuid
        proposal_id = str(uuid.uuid4())
        self._proposals[proposal_id] = proposal
        return proposal_id

    async def get_proposal(self, proposal_id: str) -> HarvestProposal | None:
        return self._proposals.get(proposal_id)

    async def save_transactions(
        self, proposal: HarvestProposal, proposal_id: str
    ) -> None:
        self._bucket_carteira = Money(
            self._bucket_carteira.amount + proposal.carteira_hard_amount.amount
        )
        self._bucket_buffer = Money(
            self._bucket_buffer.amount + proposal.buffer_amount.amount
        )
        self._history.append({
            "proposal_id": proposal_id,
            "carteira_hard": str(proposal.carteira_hard_amount.amount),
            "buffer": str(proposal.buffer_amount.amount),
            "status": "EXECUTED",
        })

    async def get_harvest_history(self) -> list[dict]:
        return self._history


_repo = _InMemoryHarvestRepo()
_service = HarvestService(repo=_repo)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ExecuteHarvestRequest(BaseModel):
    """
    Request para execução de harvest.

    founder_approved deve ser True — sem isso o harvest é recusado (R4.07).
    """

    proposal_id: str
    founder_approved: bool


# ---------------------------------------------------------------------------
# Harvest endpoints
# ---------------------------------------------------------------------------


@router.get("/api/v1/harvest/proposal/{month}")
async def get_harvest_proposal(month: str) -> dict:
    """
    Calcula proposta de harvest do mês.

    Não executa — apenas calcula e apresenta para aprovação do Founder.
    """
    proposal = await _service.calculate_proposal(month=month)
    return {
        "month": month,
        "net_monthly_profit": str(proposal.net_monthly_profit.amount),
        "carteira_hard_amount": str(proposal.carteira_hard_amount.amount),
        "buffer_amount": str(proposal.buffer_amount.amount),
        "requires_approval": True,
        "message": "Proposta calculada — aguarda aprovação do Founder (R4.07)",
    }


@router.post("/api/v1/harvest/execute")
async def execute_harvest(body: ExecuteHarvestRequest) -> dict:
    """
    Executa harvest com aprovação do Founder.

    REQUER founder_approved=True. Sem isso, retorna 400.
    Protege contra execução automática (Art. 21º, R4.07).
    """
    try:
        await _service.execute_harvest(
            proposal_id=body.proposal_id,
            founder_approved=body.founder_approved,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "executed", "proposal_id": body.proposal_id}


@router.get("/api/v1/harvest/history")
async def get_harvest_history() -> list[dict]:
    """Histórico de harvests executados."""
    return await _service.get_history()


# ---------------------------------------------------------------------------
# Ledger endpoints
# ---------------------------------------------------------------------------


@ledger_router.get("/buckets")
async def get_bucket_balances() -> dict:
    """Saldos atuais dos 3 buckets (Derivativo, Buffer, Carteira Hard)."""
    return await _service.get_buckets()

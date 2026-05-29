"""
Router FastAPI da feature checklists.

Endpoints:
    POST /api/v1/checklists/pre-market             → salvar checklist pré-mercado
    POST /api/v1/checklists/post-market            → salvar checklist pós-mercado
    GET  /api/v1/checklists/pre-market/{date}      → consultar pré-mercado por data
    GET  /api/v1/checklists/post-market/{date}     → consultar pós-mercado por data

Arts. 32º e 33º da Constituição.
"""
from fastapi import APIRouter, HTTPException

from cam.features.checklists.domain import (
    PostMarketChecklist,
    PreMarketChecklist,
)
from cam.features.checklists.schemas import (
    ChecklistResponse,
    PostMarketChecklistRequest,
    PreMarketChecklistRequest,
)
from cam.features.checklists.service import ChecklistService

router = APIRouter(prefix="/api/v1/checklists", tags=["checklists"])

# ---------------------------------------------------------------------------
# Repositório em memória — para uso sem banco (testes e modo offline)
# ---------------------------------------------------------------------------


class _InMemoryChecklistRepo:
    def __init__(self) -> None:
        self._pre: dict[str, PreMarketChecklist] = {}
        self._post: dict[str, PostMarketChecklist] = {}

    async def save_pre_market(self, checklist: PreMarketChecklist) -> str:
        self._pre[checklist.date] = checklist
        return "in-memory"

    async def save_post_market(self, checklist: PostMarketChecklist) -> str:
        self._post[checklist.date] = checklist
        return "in-memory"

    async def get_pre_market(self, date: str) -> PreMarketChecklist | None:
        return self._pre.get(date)

    async def get_post_market(self, date: str) -> PostMarketChecklist | None:
        return self._post.get(date)


_repo = _InMemoryChecklistRepo()
_service = ChecklistService(repo=_repo)


@router.post("/pre-market", status_code=201)
async def save_pre_market(body: PreMarketChecklistRequest) -> dict:
    """
    Salva checklist pré-mercado.

    Rejeita se algum item obrigatório estiver faltando ou marcado como False.
    """
    try:
        await _service.save_pre_market(date=body.date, items=body.items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "saved", "date": body.date}


@router.post("/post-market", status_code=201)
async def save_post_market(body: PostMarketChecklistRequest) -> dict:
    """
    Salva checklist pós-mercado.

    Rejeita se algum item obrigatório estiver faltando ou marcado como False.
    """
    try:
        await _service.save_post_market(
            date=body.date, items=body.items, result_summary=body.result_summary
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "saved", "date": body.date}


@router.get("/pre-market/{date}", response_model=ChecklistResponse)
async def get_pre_market(date: str) -> ChecklistResponse:
    """Retorna o checklist pré-mercado de uma data (YYYY-MM-DD)."""
    checklist = await _service.get_pre_market(date=date)
    if checklist is None:
        raise HTTPException(
            status_code=404,
            detail=f"Checklist pré-mercado não encontrado para {date}",
        )
    return ChecklistResponse(
        date=checklist.date,
        items=checklist.items,
        is_complete=checklist.is_complete(),
    )


@router.get("/post-market/{date}", response_model=ChecklistResponse)
async def get_post_market(date: str) -> ChecklistResponse:
    """Retorna o checklist pós-mercado de uma data (YYYY-MM-DD)."""
    checklist = await _service.get_post_market(date=date)
    if checklist is None:
        raise HTTPException(
            status_code=404,
            detail=f"Checklist pós-mercado não encontrado para {date}",
        )
    return ChecklistResponse(
        date=checklist.date,
        items=checklist.items,
        is_complete=checklist.is_complete(),
        result_summary=checklist.result_summary,
    )

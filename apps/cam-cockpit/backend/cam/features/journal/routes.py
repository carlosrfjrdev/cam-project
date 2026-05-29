"""
Router FastAPI da feature journal.

Endpoints:
    POST /api/v1/journal/entries           → criar entry manual
    GET  /api/v1/journal/entries           → listar (filtros: date, asset, strategy)
    GET  /api/v1/journal/entries/{id}      → detalhe
    GET  /api/v1/journal/reports/daily     → relatório diário
    GET  /api/v1/journal/reports/weekly    → relatório semanal
    GET  /api/v1/journal/reports/monthly   → relatório mensal
    GET  /api/v1/journal/export            → exportar CSV/JSON

Art. 25º: toda resposta com P&L inclui result_gross, result_net e tax_provisioned.
Art. 31º: toda operação DEVE ter JournalEntry correspondente.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from cam.features.journal.domain import JournalEntry
from cam.features.journal.schemas import (
    JournalEntryRequest,
    JournalEntryResponse,
)
from cam.features.journal.service import JournalService

router = APIRouter(prefix="/api/v1/journal", tags=["journal"])

# ---------------------------------------------------------------------------
# Repositório em memória — para uso sem banco (testes e modo offline)
# ---------------------------------------------------------------------------


class _InMemoryJournalRepo:
    def __init__(self) -> None:
        self._entries: dict[str, JournalEntry] = {}
        self._counter = 0

    async def save(self, entry: JournalEntry) -> str:
        import uuid
        entry_id = str(uuid.uuid4())
        self._entries[entry_id] = entry
        return entry_id

    async def get_by_id(self, entry_id: str) -> JournalEntry | None:
        return self._entries.get(entry_id)

    async def list_by_date(self, date: str) -> list[JournalEntry]:
        return list(self._entries.values())

    async def list_by_strategy(self, strategy: str) -> list[JournalEntry]:
        return [e for e in self._entries.values() if e.strategy == strategy]

    async def list_all(self) -> list[JournalEntry]:
        return list(self._entries.values())


_repo = _InMemoryJournalRepo()
_service = JournalService(repo=_repo)


def _entry_to_response(
    entry: JournalEntry, entry_id: str | None = None
) -> JournalEntryResponse:
    """Converte JournalEntry para response schema — Art. 25º sempre presente."""
    return JournalEntryResponse(
        id=entry_id,
        asset=entry.asset,
        direction=entry.direction,
        contracts=entry.contracts,
        entry_price=entry.entry_price,
        exit_price=entry.exit_price,
        result_gross=entry.result_gross.amount,
        costs=entry.costs.amount,
        tax_provisioned=entry.tax_provisioned.amount,  # Art. 25º
        result_net=entry.result_net.amount,             # Art. 25º
        strategy=entry.strategy,
        setup=entry.setup,
        adherence=entry.adherence,
        emotional_note=entry.emotional_note,
        lesson=entry.lesson,
        source=entry.source,
    )


@router.post("/entries", status_code=201, response_model=JournalEntryResponse)
async def create_entry(body: JournalEntryRequest) -> JournalEntryResponse:
    """
    Cria um JournalEntry manual.

    Art. 31º: toda operação executada DEVE ter JournalEntry.
    Art. 25º: response inclui result_net e tax_provisioned.
    """
    try:
        entry = await _service.create_entry(
            asset=body.asset,
            direction=body.direction,
            contracts=body.contracts,
            entry_price=body.entry_price,
            exit_price=body.exit_price,
            result_gross=body.result_gross,
            costs=body.costs,
            strategy=body.strategy,
            setup=body.setup,
            adherence=body.adherence,
            emotional_note=body.emotional_note,
            lesson=body.lesson,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _entry_to_response(entry)


@router.get("/entries", response_model=list[JournalEntryResponse])
async def list_entries(
    date: str | None = Query(None),
    strategy: str | None = Query(None),
) -> list[JournalEntryResponse]:
    """Lista JournalEntries com filtros opcionais."""
    entries = await _service.list_entries(date=date, strategy=strategy)
    return [_entry_to_response(e) for e in entries]


@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(entry_id: str) -> JournalEntryResponse:
    """Retorna detalhe de um JournalEntry."""
    entry = await _service.get_entry(entry_id)
    if entry is None:
        raise HTTPException(
            status_code=404, detail=f"JournalEntry {entry_id} não encontrado"
        )
    return _entry_to_response(entry, entry_id=entry_id)


@router.get("/reports/daily")
async def daily_report(
    date: str = Query(..., description="Data no formato YYYY-MM-DD"),
) -> dict:
    """
    Relatório diário do journal.

    Art. 25º: inclui result_gross, result_net e tax_provisioned.
    """
    return await _service.daily_report(date=date)


@router.get("/reports/weekly")
async def weekly_report(week_start: str = Query(...)) -> dict:
    """Relatório semanal — resultado líquido sempre presente (Art. 25º)."""
    return await _service.weekly_report(week_start=week_start)


@router.get("/reports/monthly")
async def monthly_report(month: str = Query(...)) -> dict:
    """Relatório mensal — resultado líquido sempre presente (Art. 25º)."""
    return await _service.monthly_report(month=month)


@router.get("/reports/by-strategy")
async def report_by_strategy(strategy: str = Query(...)) -> dict:
    """Relatório por estratégia — resultado líquido sempre presente (Art. 25º)."""
    return await _service.report_by_strategy(strategy=strategy)


@router.get("/export")
async def export_journal(format: str = Query("csv")) -> Response:
    """
    Exporta todos os JournalEntries em CSV ou JSON.

    Art. 25º: CSV inclui result_gross, result_net e tax_provisioned.
    """
    if format == "csv":
        content = await _service.export_csv()
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=journal_export.csv"},
        )
    raise HTTPException(
        status_code=400, detail=f"Formato {format} não suportado. Use: csv"
    )

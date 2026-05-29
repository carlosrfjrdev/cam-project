"""
Schemas Pydantic da feature journal — request/response da API.

Art. 25º: toda resposta que inclua P&L deve conter result_gross, result_net
e tax_provisioned — nunca apenas o bruto.
"""
from decimal import Decimal

from pydantic import BaseModel


class JournalEntryRequest(BaseModel):
    """Request para criação de JournalEntry manual."""

    asset: str                          # WIN | WDO
    direction: str                      # LONG | SHORT
    contracts: int
    entry_price: Decimal
    exit_price: Decimal
    result_gross: Decimal
    costs: Decimal
    strategy: str
    setup: str
    adherence: str | None = None
    emotional_note: str | None = None
    lesson: str | None = None


class JournalEntryResponse(BaseModel):
    """
    Response de JournalEntry.

    Art. 25º: result_gross, result_net e tax_provisioned sempre presentes.
    """

    id: str | None = None
    asset: str
    direction: str
    contracts: int
    entry_price: Decimal
    exit_price: Decimal
    result_gross: Decimal
    costs: Decimal
    tax_provisioned: Decimal       # Art. 25º — sempre calculado
    result_net: Decimal            # Art. 25º — nunca apenas bruto
    strategy: str
    setup: str
    adherence: str | None = None
    emotional_note: str | None = None
    lesson: str | None = None
    source: str = "MANUAL"


class DailyReportResponse(BaseModel):
    """
    Relatório diário do journal.

    Art. 25º: result_net e tax_provisioned sempre presentes.
    """

    date: str
    total_operations: int
    result_gross: Decimal
    result_net: Decimal          # Art. 25º
    tax_provisioned: Decimal     # Art. 25º
    total_costs: Decimal
    win_rate: float
    entries: list[JournalEntryResponse] = []


class ExportRequest(BaseModel):
    format: str = "csv"  # csv | json

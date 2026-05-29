"""
Schemas Pydantic da feature fiscal — request/response da API.
"""
from decimal import Decimal

from pydantic import BaseModel


class FiscalApurationResponse(BaseModel):
    month: str
    gross_result: Decimal
    net_result: Decimal
    taxable_base: Decimal
    ir_due: Decimal
    darf_value: Decimal


class DarfResponse(BaseModel):
    month: str
    value: Decimal
    due_date: str
    status: str
    paid_at: str | None = None
    is_compliant: bool


class MarkDarfPaidResponse(BaseModel):
    month: str
    status: str
    paid_at: str | None = None


class FiscalSummaryResponse(BaseModel):
    month: str
    gross_result: str
    net_result: str
    taxable_base: str
    ir_due: str
    darf_value: str
    tax_compliance: bool

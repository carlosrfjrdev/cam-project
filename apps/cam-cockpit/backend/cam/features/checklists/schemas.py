"""
Schemas Pydantic da feature checklists — request/response da API.
"""
from pydantic import BaseModel


class PreMarketChecklistRequest(BaseModel):
    date: str
    items: dict[str, bool]


class PostMarketChecklistRequest(BaseModel):
    date: str
    items: dict[str, bool]
    result_summary: dict | None = None


class ChecklistResponse(BaseModel):
    date: str
    items: dict[str, bool]
    is_complete: bool
    result_summary: dict | None = None

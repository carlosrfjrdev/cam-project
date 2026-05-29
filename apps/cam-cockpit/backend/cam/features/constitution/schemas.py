from datetime import datetime
from pydantic import BaseModel


class ConstitutionVersionResponse(BaseModel):
    version: str
    content: str
    effective_date: str
    hash: str


class AmendmentProposalRequest(BaseModel):
    text: str
    reason: str


class AmendmentProposalResponse(BaseModel):
    text: str
    reason: str
    proposed_at: datetime
    status: str
    message: str

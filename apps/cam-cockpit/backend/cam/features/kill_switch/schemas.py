"""
Schemas Pydantic da feature kill_switch — request/response da API.
"""
from pydantic import BaseModel


class ActivateRequest(BaseModel):
    reason: str


class DeactivateRequest(BaseModel):
    confirm: bool


class KillSwitchStatusResponse(BaseModel):
    active: bool
    last_action: str | None = None
    last_reason: str | None = None

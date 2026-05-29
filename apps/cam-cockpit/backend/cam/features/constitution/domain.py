"""
Constitution feature -- dominio.

Constituicao e soberana (Art. 43o). Exibicao read-only.
Propostas de emenda sao apenas registros -- sem auto-execucao.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConstitutionVersion:
    version: str
    content: str
    effective_date: str
    hash: str


@dataclass
class AmendmentProposal:
    text: str
    reason: str
    proposed_at: datetime
    status: str = "PENDING_FOUNDER_APPROVAL"

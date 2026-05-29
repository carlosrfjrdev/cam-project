"""
Paper Trading — domínio isolado de produção.

CA5.5: paper trades NUNCA persistem em cam_journal_entries.
Separação garantida por tabela própria e flag is_paper=True.
"""
from dataclasses import dataclass
from enum import Enum

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
)


class PaperTradeStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class PaperTrade:
    candidate_asset: AssetType
    candidate_direction: Direction
    candidate_contracts: ContractCount
    status: PaperTradeStatus
    is_paper: bool
    rejection_reason: str | None
    simulated_result_gross: Money | None
    simulated_result_net: Money | None

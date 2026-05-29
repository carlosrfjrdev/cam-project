from decimal import Decimal
from pydantic import BaseModel


class SimulateOperationRequest(BaseModel):
    asset: str
    direction: str
    contracts: int
    entry_price: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    strategy: str = ""
    exit_price_points: Decimal | None = None


class SimulateOperationResponse(BaseModel):
    approved: bool
    reason: str | None
    simulated_result_gross: float | None
    simulated_result_net: float | None
    is_paper: bool = True

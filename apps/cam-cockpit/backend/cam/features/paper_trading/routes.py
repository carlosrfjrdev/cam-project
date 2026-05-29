"""
Paper Trading routes — T-H01.

CA5.5: badge PAPER obrigatorio. Risk Engine sempre ativo.
Nenhuma ordem real e enviada ao Profit.
"""
from decimal import Decimal

from fastapi import APIRouter

from cam._shared.domain.primitives import AssetType, ContractCount, Direction, Money, Phase
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam.features.paper_trading.schemas import SimulateOperationRequest, SimulateOperationResponse
from cam.features.paper_trading.service import PaperTradingService

router = APIRouter(prefix="/api/v1/paper-trading", tags=["paper_trading"])
_service = PaperTradingService()


def _build_stub_context() -> RiskContext:
    """Contexto stub para paper trading — substituir por leitura real do banco em T-H06."""
    return RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000.00")),
        daily_pnl=Money(Decimal("0.00")),
        weekly_pnl=Money(Decimal("0.00")),
        monthly_pnl=Money(Decimal("0.00")),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
    )


@router.post("/simulate-operation", response_model=SimulateOperationResponse)
async def simulate_operation(request: SimulateOperationRequest) -> SimulateOperationResponse:
    """Simula operacao com Risk Engine ativo. Nenhuma ordem real enviada."""
    try:
        asset = AssetType(request.asset)
        direction = Direction(request.direction)
        contracts = ContractCount(request.contracts)
    except ValueError as e:
        return SimulateOperationResponse(
            approved=False,
            reason=f"Parametros invalidos: {e}",
            simulated_result_gross=None,
            simulated_result_net=None,
        )

    candidate = OrderCandidate(
        asset=asset,
        direction=direction,
        contracts=contracts,
        intended_stop_loss_points=abs(request.stop_loss - request.entry_price) if request.stop_loss else Decimal("150"),
    )

    context = _build_stub_context()
    result = _service.simulate(candidate, context, exit_price_points=request.exit_price_points)

    return SimulateOperationResponse(
        approved=(result.status.value == "APPROVED"),
        reason=result.rejection_reason,
        simulated_result_gross=float(result.simulated_result_gross.amount) if result.simulated_result_gross else None,
        simulated_result_net=float(result.simulated_result_net.amount) if result.simulated_result_net else None,
        is_paper=True,
    )

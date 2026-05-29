"""
Paper Trading Service.

Executa simulação usando o MESMO Risk Engine do live.
Paper trades sao separados do journal de producao — persistem em cam_paper_trades.

CA5.5: is_paper=True em toda operacao simulada.
"""
from decimal import Decimal

from cam._shared.domain.primitives import Money
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.engine import validate
from cam.features.paper_trading.domain import PaperTrade, PaperTradeStatus


class PaperTradingService:
    IR_RATE = Decimal("0.20")
    COST_PER_CONTRACT = Decimal("5.00")

    def simulate(
        self,
        candidate: OrderCandidate,
        context: RiskContext,
        exit_price_points: Decimal | None = None,
    ) -> PaperTrade:
        """
        Simula uma operacao passando pelo Risk Engine real.
        Nunca persiste em cam_journal_entries.
        """
        decision = validate(candidate, context)

        if not decision.approved:
            return PaperTrade(
                candidate_asset=candidate.asset,
                candidate_direction=candidate.direction,
                candidate_contracts=candidate.contracts,
                status=PaperTradeStatus.REJECTED,
                is_paper=True,
                rejection_reason=getattr(decision, "reason", "Bloqueado pelo Risk Engine"),
                simulated_result_gross=None,
                simulated_result_net=None,
            )

        gross = self._calculate_simulated_pnl(candidate, exit_price_points)
        net = self._calculate_net(gross, candidate)

        return PaperTrade(
            candidate_asset=candidate.asset,
            candidate_direction=candidate.direction,
            candidate_contracts=candidate.contracts,
            status=PaperTradeStatus.APPROVED,
            is_paper=True,
            rejection_reason=None,
            simulated_result_gross=gross,
            simulated_result_net=net,
        )

    def _calculate_simulated_pnl(
        self,
        candidate: OrderCandidate,
        exit_price_points: Decimal | None,
    ) -> Money:
        if exit_price_points is None:
            return Money(Decimal("0.00"))

        contracts = Decimal(str(candidate.contracts.value))
        gross = exit_price_points * contracts
        return Money(gross)

    def _calculate_net(self, gross: Money, candidate: OrderCandidate) -> Money:
        contracts = Decimal(str(candidate.contracts.value))
        costs = self.COST_PER_CONTRACT * contracts

        if gross.amount > 0:
            tax = gross.amount * self.IR_RATE
            net = gross.amount - tax - costs
        else:
            net = gross.amount - costs

        return Money(net)

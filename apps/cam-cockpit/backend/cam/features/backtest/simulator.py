"""
Simulador tick-a-tick do Backtest Engine — TASK-008 (BL-A SPEC v0.4).

Substitui o stub anterior (`result_gross=0`) por **P&L real por tick scanning**:
ao aprovar um candidato, abre posição virtual e percorre os ticks subsequentes
até bater SL ou TP (ou fim dos ticks). Resultado em pontos × point_value.

Usa o MESMO Risk Engine do ambiente live — sem exceção constitucional (CA7.5).
Art. 35º: IA não pode desabilitar nem parametrizar o Risk Engine.
Art. 15º: Risk Engine bloqueia? CaM não opera — inclusive no backtest.

Art. 25º: IR 20% provisionado sobre lucros simulados (em
`BacktestTrade.tax_provisioned`).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal

from cam._shared.domain.primitives import ContractCount, Money
from cam._shared.risk import Approved, OrderCandidate
from cam._shared.risk import validate as risk_validate
from cam._shared.risk.context import RiskContext
from cam.features.backtest.domain import BacktestConfig, BacktestRun, BacktestTrade


@dataclass
class _OpenPosition:
    candidate: OrderCandidate
    entry_price: Decimal
    entry_timestamp: object


class BacktestSimulator:
    """
    Simulador tick-a-tick com P&L real (CA-A.3).

    Invariantes:
      - Risk Engine sempre ativo — sem parâmetro para desativar.
      - Após abrir posição, nenhum candidato novo é aceito até fechá-la
        (single-position por simulador — multi-strategy fica para BL-H1).
      - IR 20% provisionado sobre lucros simulados (em `BacktestTrade`).
      - Corretagem aplicada por trade.
    """

    def run(
        self,
        config: BacktestConfig,
        ticks: list[dict],
        strategy_fn,
    ) -> BacktestRun:
        """
        Executa simulação tick-a-tick.

        Args:
            config: configuração (fase, corretagem, point_value, take_profit_points)
            ticks: lista de dicts {"price": ..., "timestamp": ...}
            strategy_fn: callable(tick) -> OrderCandidate | None

        Returns:
            BacktestRun com trades fechados (cada um com risk_decision indicando
            APPROVED_CLOSED_SL | APPROVED_CLOSED_TP | APPROVED_CLOSED_EOD | REJECTED).
        """
        run = BacktestRun(id=str(uuid.uuid4()), config=config)
        run.status = "RUNNING"

        daily_pnl = Decimal("0")
        total_capital = Decimal("5000")
        operations_today = 0
        last_result: Decimal | None = None
        last_contracts: int | None = None
        open_pos: _OpenPosition | None = None

        try:
            for tick in ticks:
                price = Decimal(str(tick.get("price", 0)))

                # 1) Se há posição aberta, primeiro testa SL/TP
                if open_pos is not None:
                    exit_reason = self._check_exit(open_pos, price, config)
                    if exit_reason is not None:
                        trade = self._close_trade(
                            open_pos, price, tick, config, exit_reason
                        )
                        run.trades.append(trade)
                        daily_pnl += trade.result_net.amount
                        operations_today += 1
                        last_result = trade.result_net.amount
                        last_contracts = trade.contracts
                        open_pos = None
                    continue  # com posição aberta, não pergunta nova estratégia

                # 2) Sem posição — consulta estratégia
                candidate: OrderCandidate | None = strategy_fn(tick)
                if candidate is None:
                    continue

                # 3) Risk Engine valida
                context = RiskContext(
                    kill_switch_active=False,
                    phase=config.phase,
                    pre_market_checklist_done=True,
                    post_market_checklist_done=True,
                    tax_compliance_ok=True,
                    total_capital=Money(total_capital),
                    daily_pnl=Money(daily_pnl),
                    weekly_pnl=Money(Decimal("0")),
                    monthly_pnl=Money(Decimal("0")),
                    daily_operations_count=operations_today,
                    last_operation_result=(
                        Money(last_result) if last_result is not None else None
                    ),
                    last_operation_contracts=(
                        ContractCount(last_contracts)
                        if last_contracts is not None
                        else None
                    ),
                )
                decision = risk_validate(candidate, context)

                if not isinstance(decision, Approved):
                    # Registra rejeitada com gross 0
                    run.trades.append(
                        BacktestTrade(
                            asset=candidate.asset.value,
                            direction=candidate.direction.value,
                            contracts=candidate.contracts.value,
                            entry_price=price,
                            exit_price=price,
                            result_gross=Money(Decimal("0")),
                            brokerage=Money(Decimal("0")),
                            risk_decision="REJECTED",
                            timestamp=tick.get("timestamp"),
                        )
                    )
                    continue

                # 4) Approved — abre posição virtual
                open_pos = _OpenPosition(
                    candidate=candidate,
                    entry_price=price,
                    entry_timestamp=tick.get("timestamp"),
                )

            # 5) Se ficou posição aberta no fim, fecha no último tick (EOD)
            if open_pos is not None and ticks:
                last_tick = ticks[-1]
                last_price = Decimal(str(last_tick.get("price", 0)))
                trade = self._close_trade(
                    open_pos, last_price, last_tick, config, "EOD"
                )
                run.trades.append(trade)

            run.status = "COMPLETED"
        except Exception:
            run.status = "FAILED"
            raise

        return run

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------
    @staticmethod
    def _check_exit(
        pos: _OpenPosition,
        current_price: Decimal,
        config: BacktestConfig,
    ) -> str | None:
        """
        Retorna "SL", "TP" ou None.

        SL via `candidate.intended_stop_loss_points`. TP via
        `config.take_profit_points` (opcional — sem TP, só SL/EOD encerram).
        """
        cand = pos.candidate
        sl_pts = cand.intended_stop_loss_points
        tp_pts = config.take_profit_points

        if cand.direction.value == "LONG":
            if current_price <= pos.entry_price - sl_pts:
                return "SL"
            if tp_pts is not None and current_price >= pos.entry_price + tp_pts:
                return "TP"
        else:  # SHORT
            if current_price >= pos.entry_price + sl_pts:
                return "SL"
            if tp_pts is not None and current_price <= pos.entry_price - tp_pts:
                return "TP"
        return None

    @staticmethod
    def _close_trade(
        pos: _OpenPosition,
        exit_price: Decimal,
        exit_tick: dict,
        config: BacktestConfig,
        exit_reason: str,
    ) -> BacktestTrade:
        """Calcula P&L real e produz BacktestTrade."""
        cand = pos.candidate
        contracts = Decimal(cand.contracts.value)

        if cand.direction.value == "LONG":
            points = exit_price - pos.entry_price
        else:
            points = pos.entry_price - exit_price

        gross_brl = points * config.point_value * contracts
        brokerage_brl = config.brokerage_per_contract * contracts

        return BacktestTrade(
            asset=cand.asset.value,
            direction=cand.direction.value,
            contracts=cand.contracts.value,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            result_gross=Money(gross_brl),
            brokerage=Money(brokerage_brl),
            risk_decision=f"APPROVED_CLOSED_{exit_reason}",
            timestamp=exit_tick.get("timestamp"),
        )

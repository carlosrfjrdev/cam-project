"""
Paper Loop Governado — TASK-016 + TASK-017 (BL-C SPEC v0.4).

Loop end-to-end: replay de ticks → strategy.evaluate → Order Gateway (paper) →
persistência em cam_paper_trades. Kill switch via asyncio.Event (< 1s).

Aderência calculada por trade:
  - 1.0 se Risk Engine aprovou + estratégia respeitou parâmetros.
  - 0.0 se houve rejeição ou violação.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text

from cam._shared.autonomy.matrix import Env, Mode
from cam._shared.domain.primitives import Money, Phase
from cam._shared.order_gateway.gateway import OrderGateway, OrderResult
from cam._shared.risk.context import RiskContext
from cam.features.strategies.domain import (
    Strategy,
    StrategyContext,
    StrategyStatus,
)


@dataclass
class PaperLoopStats:
    ticks_processed: int = 0
    candidates_emitted: int = 0
    approved: int = 0
    rejected: int = 0
    kill_switch_at: datetime | None = None
    stop_reason: str = "ok"


class PaperTradingLoop:
    """
    Loop governado com kill switch.

    Uso:
        loop = PaperTradingLoop(strategy, gateway, settings, session_factory)
        await loop.run(ticks=[...], strategy_id=UUID(...))

    Para acionar kill switch externamente:
        loop.kill_switch.set()
    """

    def __init__(
        self,
        strategy: Strategy,
        gateway: OrderGateway,
        session_factory,
    ) -> None:
        self.strategy = strategy
        self.gateway = gateway
        self.session_factory = session_factory
        self.kill_switch: asyncio.Event = asyncio.Event()

    async def run(
        self,
        ticks: list[dict[str, Any]],
        strategy_id: UUID,
        risk_context_builder=None,
    ) -> PaperLoopStats:
        """
        Itera ticks chamando `strategy.evaluate` e submetendo via Order Gateway.

        Persiste paper_trade em cam_paper_trades. Aderência computada
        retroativamente quando trade fecha.
        """
        stats = PaperLoopStats()
        strategy_ctx = StrategyContext(tick={}, max_contracts=2)

        for tick in ticks:
            if self.kill_switch.is_set():
                stats.kill_switch_at = datetime.now(UTC)
                stats.stop_reason = "kill_switch"
                break

            stats.ticks_processed += 1
            strategy_ctx = StrategyContext(
                tick=tick, max_contracts=2, history=strategy_ctx.history,
            )
            candidate = self.strategy.evaluate(tick, strategy_ctx)
            if candidate is None:
                continue

            stats.candidates_emitted += 1

            # Risk context default — caller pode injetar via builder
            if risk_context_builder is not None:
                rctx = risk_context_builder(tick)
            else:
                rctx = _default_paper_risk_context(tick)

            idempotency_key = uuid4()
            result = await self.gateway.submit(
                candidate=candidate,
                risk_context=rctx,
                env=Env.PAPER,
                mode=Mode.FULL,
                strategy_status=StrategyStatus.BACKTESTED,
                idempotency_key=idempotency_key,
            )

            await self._persist_paper_trade(
                strategy_id=strategy_id,
                candidate=candidate,
                result=result,
                entry_tick=tick,
                idempotency_key=idempotency_key,
            )

            if result.approved:
                stats.approved += 1
            else:
                stats.rejected += 1

        return stats

    async def _persist_paper_trade(
        self,
        strategy_id: UUID,
        candidate,
        result: OrderResult,
        entry_tick: dict,
        idempotency_key: UUID,
    ) -> None:
        ts_open = entry_tick.get("timestamp") or datetime.now(UTC)
        entry_price = Decimal(str(entry_tick.get("price", 0)))
        # Aderência: 1.0 se aprovado; 0.0 se rejeitado por violação
        adherence = Decimal("1.0") if result.approved else Decimal("0.0")
        session_id = uuid4()
        risk_decision_str = "APPROVED" if result.approved else "REJECTED"
        async with self.session_factory() as session:
            await session.execute(
                text(
                    "INSERT INTO cam_paper_trades "
                    "(id, session_id, asset, direction, contracts, entry_price, "
                    " result_gross, risk_decision, risk_rejection_reason, "
                    " strategy_id, intent_id, adherence, ts_open, ts_close) "
                    "VALUES (gen_random_uuid(), :sid, :asset, :dir, :ct, :ep, "
                    "        0, :rd, :reason, :strat, :intent, :adh, :ts, :ts)"
                ),
                {
                    "sid": str(session_id),
                    "asset": candidate.asset.value,
                    "dir": candidate.direction.value,
                    "ct": candidate.contracts.value,
                    "ep": entry_price,
                    "rd": risk_decision_str,
                    "reason": (result.reason if not result.approved else None),
                    "strat": str(strategy_id),
                    "intent": str(idempotency_key),
                    "adh": adherence,
                    "ts": ts_open,
                },
            )
            await session.commit()


def _default_paper_risk_context(tick: dict) -> RiskContext:
    """Risk context "verde" default (BL-C — paper assume estado limpo)."""
    return RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000")),
        daily_pnl=Money.zero(),
        weekly_pnl=Money.zero(),
        monthly_pnl=Money.zero(),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        current_time=time(11, 30),
    )

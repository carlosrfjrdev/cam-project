"""
Repository da feature harvest — SQLAlchemy 2.0 async.

Persiste em cam_bucket_transactions e cam_harvest_history.
"""
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.domain.primitives import Money
from cam.features.harvest.domain import HarvestProposal


class HarvestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_net_monthly_profit(self, month: str) -> Money:
        """Retorna lucro líquido pós-fiscal do mês (de cam_fiscal_apuration)."""
        result = await self._session.execute(
            text(
                """
                SELECT gross_result - costs - tax_provisioned_accumulated
                FROM cam_fiscal_apuration
                WHERE month = :month
                """
            ),
            {"month": month},
        )
        row = result.fetchone()
        if row is None or row[0] is None:
            return Money(Decimal("0"))
        return Money(Decimal(str(row[0])))

    async def get_buffer_current(self) -> Money:
        """Retorna saldo atual do Buffer Operacional."""
        result = await self._session.execute(
            text(
                """
                SELECT COALESCE(SUM(CASE WHEN transaction_type = 'IN' THEN amount
                                        WHEN transaction_type = 'OUT' THEN -amount
                                        ELSE 0 END), 0)
                FROM cam_bucket_transactions
                WHERE bucket = 'BUFFER'
                """
            )
        )
        row = result.fetchone()
        return Money(Decimal(str(row[0])) if row and row[0] else Decimal("0"))

    async def get_bucket_derivativo_current(self) -> Money:
        """Retorna saldo atual do Bucket Derivativo."""
        result = await self._session.execute(
            text(
                """
                SELECT COALESCE(SUM(CASE WHEN transaction_type = 'IN' THEN amount
                                        WHEN transaction_type = 'OUT' THEN -amount
                                        ELSE 0 END), 0)
                FROM cam_bucket_transactions
                WHERE bucket = 'DERIVATIVO'
                """
            )
        )
        row = result.fetchone()
        return Money(Decimal(str(row[0])) if row and row[0] else Decimal("0"))

    async def get_bucket_derivativo_baseline(self) -> Money:
        """Retorna a baseline do Bucket Derivativo (constante R$ 3.000)."""
        from cam.features.harvest.domain import BUCKET_BASELINE

        return Money(BUCKET_BASELINE)

    async def get_bucket_balances(self) -> dict:
        """Retorna saldos dos 3 buckets."""
        result = await self._session.execute(
            text(
                """
                SELECT bucket,
                    COALESCE(SUM(CASE WHEN transaction_type = 'IN' THEN amount
                                     WHEN transaction_type = 'OUT' THEN -amount
                                     ELSE 0 END), 0) AS balance
                FROM cam_bucket_transactions
                GROUP BY bucket
                """
            )
        )
        rows = result.fetchall()
        balances = {"DERIVATIVO": "0", "BUFFER": "0", "CARTEIRA_HARD": "0"}
        for bucket, balance in rows:
            balances[bucket] = str(balance)
        return balances

    async def save_proposal(self, month: str, proposal: HarvestProposal) -> str:
        """Salva proposta de harvest."""
        proposal_id = str(uuid.uuid4())
        await self._session.execute(
            text(
                """
                INSERT INTO cam_harvest_history
                    (id, month, net_profit, carteira_hard_amount, buffer_amount,
                     status, created_at)
                VALUES
                    (:id, :month, :net_profit, :carteira_hard, :buffer, 'PROPOSED', :now)
                """
            ),
            {
                "id": proposal_id,
                "month": month,
                "net_profit": str(proposal.net_monthly_profit.amount),
                "carteira_hard": str(proposal.carteira_hard_amount.amount),
                "buffer": str(proposal.buffer_amount.amount),
                "now": datetime.now(UTC),
            },
        )
        await self._session.commit()
        return proposal_id

    async def get_proposal(self, proposal_id: str) -> HarvestProposal | None:
        """Retorna proposta pelo ID."""
        result = await self._session.execute(
            text(
                """
                SELECT net_profit, carteira_hard_amount, buffer_amount
                FROM cam_harvest_history
                WHERE id = :id AND status = 'PROPOSED'
                """
            ),
            {"id": proposal_id},
        )
        row = result.fetchone()
        if row is None:
            return None
        net, carteira, buffer = row
        return HarvestProposal(
            net_monthly_profit=Money(Decimal(str(net))),
            carteira_hard_amount=Money(Decimal(str(carteira))),
            buffer_amount=Money(Decimal(str(buffer))),
        )

    async def save_transactions(
        self, proposal: HarvestProposal, proposal_id: str
    ) -> None:
        """Registra transações nos buckets e marca harvest como EXECUTED."""
        now = datetime.now(UTC)
        # Transação: saída do Bucket Derivativo
        await self._session.execute(
            text(
                """
                INSERT INTO cam_bucket_transactions
                    (id, bucket, transaction_type, amount, reference, created_at)
                VALUES
                    (:id, 'DERIVATIVO', 'OUT', :amount, :ref, :now)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "amount": str(proposal.net_monthly_profit.amount),
                "ref": f"harvest:{proposal_id}",
                "now": now,
            },
        )
        # Transação: entrada na Carteira Hard
        if proposal.carteira_hard_amount.amount > Decimal("0"):
            await self._session.execute(
                text(
                    """
                    INSERT INTO cam_bucket_transactions
                        (id, bucket, transaction_type, amount, reference, created_at)
                    VALUES
                        (:id, 'CARTEIRA_HARD', 'IN', :amount, :ref, :now)
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "amount": str(proposal.carteira_hard_amount.amount),
                    "ref": f"harvest:{proposal_id}",
                    "now": now,
                },
            )
        # Transação: entrada no Buffer
        if proposal.buffer_amount.amount > Decimal("0"):
            await self._session.execute(
                text(
                    """
                    INSERT INTO cam_bucket_transactions
                        (id, bucket, transaction_type, amount, reference, created_at)
                    VALUES
                        (:id, 'BUFFER', 'IN', :amount, :ref, :now)
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "amount": str(proposal.buffer_amount.amount),
                    "ref": f"harvest:{proposal_id}",
                    "now": now,
                },
            )
        # Atualiza status da proposta
        await self._session.execute(
            text(
                "UPDATE cam_harvest_history SET status = 'EXECUTED' WHERE id = :id"
            ),
            {"id": proposal_id},
        )
        await self._session.commit()

    async def get_harvest_history(self) -> list[dict]:
        """Retorna histórico de harvests."""
        result = await self._session.execute(
            text(
                """
                SELECT id, month, net_profit, carteira_hard_amount, buffer_amount,
                       status, created_at
                FROM cam_harvest_history
                ORDER BY created_at DESC
                """
            )
        )
        rows = result.fetchall()
        return [
            {
                "id": r[0],
                "month": r[1],
                "net_profit": str(r[2]),
                "carteira_hard_amount": str(r[3]),
                "buffer_amount": str(r[4]),
                "status": r[5],
                "created_at": str(r[6]),
            }
            for r in rows
        ]

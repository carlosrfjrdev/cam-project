"""
Repository da feature fiscal — SQLAlchemy 2.0 async.

Persiste em cam_fiscal_apuration e cam_darf_history.
"""
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from cam._shared.domain.primitives import Money
from cam.features.fiscal.domain import Darf, DarfStatus, FiscalApuration


class FiscalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def update_monthly_provision(
        self,
        tax_provisioned: Decimal,
        result_gross: Decimal,
        entry_id: str,
    ) -> None:
        """Atualiza provisão fiscal mensal com o imposto de uma operação."""
        month = datetime.now(UTC).strftime("%Y-%m")
        await self._session.execute(
            text(
                """
                INSERT INTO cam_fiscal_apuration
                    (id, month, gross_result, costs, irrf_retained, loss_compensation,
                     tax_provisioned_accumulated, updated_at)
                VALUES
                    (:id, :month, :gross_result, 0, 0, 0, :tax_provisioned, :now)
                ON CONFLICT (month) DO UPDATE SET
                    gross_result = cam_fiscal_apuration.gross_result + EXCLUDED.gross_result,
                    tax_provisioned_accumulated = cam_fiscal_apuration.tax_provisioned_accumulated
                        + EXCLUDED.tax_provisioned_accumulated,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "month": month,
                "gross_result": str(result_gross),
                "tax_provisioned": str(tax_provisioned),
                "now": datetime.now(UTC),
            },
        )
        await self._session.commit()

    async def has_overdue_darf(self) -> bool:
        """Retorna True se há DARF com status OVERDUE."""
        result = await self._session.execute(
            text(
                """
                SELECT COUNT(*) FROM cam_darf_history
                WHERE status = 'OVERDUE'
                """
            )
        )
        count = result.scalar()
        return count > 0

    async def get_apuration(self, month: str) -> FiscalApuration:
        """Retorna a apuração do mês, ou apuração zerada se não existir."""
        result = await self._session.execute(
            text(
                """
                SELECT gross_result, costs, irrf_retained, loss_compensation
                FROM cam_fiscal_apuration
                WHERE month = :month
                """
            ),
            {"month": month},
        )
        row = result.fetchone()
        if row is None:
            return FiscalApuration(
                month=month,
                gross_result=Money(Decimal("0")),
                costs=Money(Decimal("0")),
                irrf_retained=Money(Decimal("0")),
                loss_compensation=Money(Decimal("0")),
            )
        gross, costs, irrf, comp = row
        return FiscalApuration(
            month=month,
            gross_result=Money(Decimal(str(gross))),
            costs=Money(Decimal(str(costs))),
            irrf_retained=Money(Decimal(str(irrf))),
            loss_compensation=Money(Decimal(str(comp))),
        )

    async def save_darf(self, darf: Darf) -> str:
        """Persiste ou atualiza uma DARF."""
        darf_id = str(uuid.uuid4())
        await self._session.execute(
            text(
                """
                INSERT INTO cam_darf_history
                    (id, month, value, due_date, status, paid_at, created_at)
                VALUES
                    (:id, :month, :value, :due_date, :status, :paid_at, :now)
                ON CONFLICT (month) DO UPDATE SET
                    status = EXCLUDED.status,
                    paid_at = EXCLUDED.paid_at
                """
            ),
            {
                "id": darf_id,
                "month": darf.month,
                "value": str(darf.value.amount),
                "due_date": darf.due_date,
                "status": darf.status.value,
                "paid_at": darf.paid_at,
                "now": datetime.now(UTC),
            },
        )
        await self._session.commit()
        return darf_id

    async def get_darf(self, darf_id: str) -> Darf | None:
        """Retorna uma DARF pelo ID."""
        result = await self._session.execute(
            text(
                """
                SELECT month, value, due_date, status, paid_at
                FROM cam_darf_history WHERE id = :id
                """
            ),
            {"id": darf_id},
        )
        row = result.fetchone()
        if row is None:
            return None
        month, value, due_date, status, paid_at = row
        return Darf(
            month=month,
            value=Money(Decimal(str(value))),
            due_date=due_date,
            status=DarfStatus(status),
            paid_at=paid_at,
        )

    async def list_darfs(self) -> list[Darf]:
        """Lista todas as DARFs."""
        result = await self._session.execute(
            text(
                """
                SELECT month, value, due_date, status, paid_at
                FROM cam_darf_history ORDER BY month DESC
                """
            )
        )
        rows = result.fetchall()
        return [
            Darf(
                month=r[0],
                value=Money(Decimal(str(r[1]))),
                due_date=r[2],
                status=DarfStatus(r[3]),
                paid_at=r[4],
            )
            for r in rows
        ]

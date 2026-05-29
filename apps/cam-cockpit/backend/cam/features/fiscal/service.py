"""
Service da feature fiscal — lógica de aplicação.

Responsabilidades:
- Apuração mensal de IR (SPEC R3.01–R3.09)
- Geração de DARF PENDING após resultado positivo
- Atualização de provisão fiscal em tempo real (handler de JournalEntryCreated)
- Verificação de compliance (Art. 26º)

O service consome JournalEntryCreated via EventBus (subscribe no lifespan).
"""
from decimal import Decimal

from cam.features.fiscal.domain import Darf, DarfStatus, FiscalApuration


class FiscalService:
    def __init__(self, repo: object) -> None:
        self.repo = repo

    async def handle_journal_entry_created(self, event: object) -> None:
        """
        Handler de JournalEntryCreated — SPEC R3.08.

        Atualiza provisão fiscal mensal em tempo real após cada operação.
        Consumido via EventBus (subscribe no lifespan).
        """
        # Extrai valores do evento (estão em string para serialização segura)
        tax_provisioned = Decimal(event.tax_provisioned_brl)
        result_gross = Decimal(event.result_gross_brl)

        await self.repo.update_monthly_provision(
            tax_provisioned=tax_provisioned,
            result_gross=result_gross,
            entry_id=event.entry_id,
        )

    async def check_tax_compliance(self) -> bool:
        """
        Verifica compliance fiscal atual.

        Retorna False se há DARF OVERDUE (Art. 26º).
        Chamado ao construir RiskContext — DARF atrasada bloqueia operações.
        """
        has_overdue = await self.repo.has_overdue_darf()
        return not has_overdue

    async def apurate_month(self, month: str) -> FiscalApuration:
        """
        Apura o resultado fiscal de um mês.

        Agrega JournalEntries do mês via repository.
        """
        return await self.repo.get_apuration(month=month)

    async def generate_darf(self, apuration: FiscalApuration) -> Darf | None:
        """
        Gera DARF PENDING para o mês apurado.

        Retorna None se não há IR devido (resultado negativo ou zero).
        Vencimento: último dia útil do mês seguinte (simplificado para 31).
        """
        if apuration.darf_value.amount <= Decimal("0"):
            return None

        # Calcular vencimento: último dia útil do mês seguinte
        year, month_num = apuration.month.split("-")
        next_month = int(month_num) + 1
        next_year = int(year)
        if next_month > 12:
            next_month = 1
            next_year += 1
        due_date = f"{next_year}-{next_month:02d}-31"

        darf = Darf(
            month=apuration.month,
            value=apuration.darf_value,
            due_date=due_date,
            status=DarfStatus.PENDING,
        )
        await self.repo.save_darf(darf)
        return darf

    async def mark_darf_paid(self, darf_id: str) -> Darf:
        """
        Marca uma DARF como paga.

        Após pagamento: tax_compliance=True → Risk Engine desbloqueia (Art. 26º).
        """
        from datetime import UTC, datetime

        darf = await self.repo.get_darf(darf_id)
        if darf is None:
            raise ValueError(f"DARF {darf_id} não encontrada")

        darf.status = DarfStatus.PAID
        darf.paid_at = datetime.now(UTC).isoformat()
        await self.repo.save_darf(darf)
        return darf

    async def get_apuration(self, month: str) -> FiscalApuration:
        """Retorna apuração do mês."""
        return await self.repo.get_apuration(month=month)

    async def list_darfs(self) -> list[Darf]:
        """Lista todas as DARFs."""
        return await self.repo.list_darfs()

    async def get_current_month_summary(self) -> dict:
        """Resumo fiscal do mês corrente para a UI operacional."""
        from datetime import date

        month = date.today().strftime("%Y-%m")
        try:
            apuration = await self.repo.get_apuration(month=month)
            return {
                "month": month,
                "gross_result": str(apuration.gross_result.amount),
                "net_result": str(apuration.net_result.amount),
                "taxable_base": str(apuration.taxable_base.amount),
                "ir_due": str(apuration.ir_due.amount),
                "darf_value": str(apuration.darf_value.amount),
                "tax_compliance": await self.check_tax_compliance(),
            }
        except Exception:
            return {
                "month": month,
                "gross_result": "0",
                "net_result": "0",
                "taxable_base": "0",
                "ir_due": "0",
                "darf_value": "0",
                "tax_compliance": await self.check_tax_compliance(),
            }

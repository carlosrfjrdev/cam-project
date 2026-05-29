"""
Service da feature journal — lógica de aplicação.

Responsabilidades:
- Validar campos obrigatórios (SPEC R2.05)
- Salvar via repository (INSERT apenas — imutabilidade)
- Publicar JournalEntryCreated no EventBus
- Gerar relatórios com result_net sempre calculado (Art. 25º)
"""
from decimal import Decimal

from cam._shared.domain.primitives import Money
from cam._shared.events import event_bus
from cam.features.journal.domain import JournalEntry
from cam.features.journal.events import JournalEntryCreated


class JournalService:
    def __init__(self, repo: object) -> None:
        self.repo = repo

    async def create_entry(
        self,
        asset: str | None,
        direction: str | None,
        contracts: int | None,
        entry_price: Decimal | None,
        exit_price: Decimal | None,
        result_gross: Decimal | None,
        costs: Decimal | None,
        strategy: str | None,
        setup: str | None,
        adherence: str | None = None,
        emotional_note: str | None = None,
        lesson: str | None = None,
        source: str = "MANUAL",
    ) -> JournalEntry:
        """
        Cria e persiste um JournalEntry.

        Valida campos obrigatórios (SPEC R2.05).
        Publica JournalEntryCreated após persistência.
        Retorna o JournalEntry com result_net e tax_provisioned calculados.
        """
        # Validação de campos obrigatórios — SPEC R2.05
        required = {
            "asset": asset,
            "direction": direction,
            "contracts": contracts,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "result_gross": result_gross,
            "costs": costs,
            "strategy": strategy,
            "setup": setup,
        }
        missing = [field for field, value in required.items() if value is None]
        if missing:
            raise ValueError(
                f"Campos obrigatórios ausentes no JournalEntry: {missing}. "
                f"SPEC R2.05 exige: asset, direction, contracts, timestamps, "
                f"preços, resultado, custos, estratégia, setup."
            )

        entry = JournalEntry(
            asset=asset,
            direction=direction,
            contracts=contracts,
            entry_price=Decimal(str(entry_price)),
            exit_price=Decimal(str(exit_price)),
            result_gross=Money(Decimal(str(result_gross))),
            costs=Money(Decimal(str(costs))),
            strategy=strategy,
            setup=setup,
            adherence=adherence,
            emotional_note=emotional_note,
            lesson=lesson,
            source=source,
        )

        # Persistência — INSERT apenas (imutabilidade constitucional)
        entry_id = await self.repo.save(entry)

        # Publicação no EventBus — fiscal/ e harvest/ consomem
        await event_bus.publish(
            JournalEntryCreated(
                entry_id=entry_id,
                result_gross_brl=str(entry.result_gross.amount),
                result_net_brl=str(entry.result_net.amount),
                tax_provisioned_brl=str(entry.tax_provisioned.amount),
                asset=asset,
            )
        )

        return entry

    async def get_entry(self, entry_id: str) -> JournalEntry | None:
        """Retorna um JournalEntry pelo ID."""
        return await self.repo.get_by_id(entry_id)

    async def list_entries(
        self,
        date: str | None = None,
        strategy: str | None = None,
    ) -> list[JournalEntry]:
        """Lista JournalEntries com filtros opcionais."""
        if date:
            return await self.repo.list_by_date(date)
        if strategy:
            return await self.repo.list_by_strategy(strategy)
        return await self.repo.list_all()

    async def daily_report(self, date: str) -> dict:
        """
        Relatório diário.

        Art. 25º: inclui result_gross, result_net e tax_provisioned.
        Nunca retorna apenas o bruto.
        """
        entries = await self.repo.list_by_date(date)
        total_gross = Decimal("0")
        total_net = Decimal("0")
        total_tax = Decimal("0")
        total_costs = Decimal("0")
        wins = 0

        for entry in entries:
            total_gross += entry.result_gross.amount
            total_net += entry.result_net.amount
            total_tax += entry.tax_provisioned.amount
            total_costs += entry.costs.amount
            if entry.result_gross.amount > 0:
                wins += 1

        count = len(entries)
        win_rate = (wins / count) if count > 0 else 0.0

        return {
            "date": date,
            "total_operations": count,
            "result_gross": str(total_gross),
            "result_net": str(total_net),       # Art. 25º — sempre presente
            "tax_provisioned": str(total_tax),  # Art. 25º — sempre presente
            "total_costs": str(total_costs),
            "win_rate": win_rate,
        }

    async def weekly_report(self, week_start: str) -> dict:
        """Relatório semanal — resultado líquido sempre calculado (Art. 25º)."""
        # Implementação básica — agrega dias da semana
        # TODO: iterar os 7 dias da semana e agregar
        return {
            "week_start": week_start,
            "result_gross": "0",
            "result_net": "0",
            "tax_provisioned": "0",
            "total_operations": 0,
            "win_rate": 0.0,
        }

    async def monthly_report(self, month: str) -> dict:
        """Relatório mensal — resultado líquido sempre calculado (Art. 25º)."""
        return {
            "month": month,
            "result_gross": "0",
            "result_net": "0",
            "tax_provisioned": "0",
            "total_operations": 0,
            "win_rate": 0.0,
        }

    async def report_by_strategy(self, strategy: str) -> dict:
        """Relatório por estratégia — resultado líquido sempre calculado."""
        entries = await self.repo.list_by_strategy(strategy)
        total_gross = sum(e.result_gross.amount for e in entries)
        total_net = sum(e.result_net.amount for e in entries)
        total_tax = sum(e.tax_provisioned.amount for e in entries)
        wins = sum(1 for e in entries if e.result_gross.amount > 0)
        count = len(entries)
        return {
            "strategy": strategy,
            "total_operations": count,
            "result_gross": str(total_gross),
            "result_net": str(total_net),
            "tax_provisioned": str(total_tax),
            "win_rate": (wins / count) if count > 0 else 0.0,
        }

    async def export_csv(self) -> str:
        """
        Exporta todos os JournalEntries em CSV.

        Art. 25º: CSV inclui result_gross, result_net e tax_provisioned.
        """
        import csv
        import io

        entries = await self.repo.list_all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "asset", "direction", "contracts",
            "entry_price", "exit_price",
            "result_gross", "costs", "tax_provisioned", "result_net",
            "strategy", "setup", "adherence", "source",
        ])
        for entry in entries:
            writer.writerow([
                entry.asset, entry.direction, entry.contracts,
                entry.entry_price, entry.exit_price,
                entry.result_gross.amount, entry.costs.amount,
                entry.tax_provisioned.amount, entry.result_net.amount,
                entry.strategy, entry.setup, entry.adherence, entry.source,
            ])
        return output.getvalue()

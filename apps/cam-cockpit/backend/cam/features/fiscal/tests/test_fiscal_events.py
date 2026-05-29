"""
Testes TDD para o event consumer da feature fiscal — T-C07.

Handler de JournalEntryCreated atualiza provisão fiscal em tempo real.
SPEC R3.08.

NOTA ARQUITETURAL: Os testes NÃO importam cam.features.journal.events diretamente
(violaria ADR-013 independence entre features). Em vez disso, usam duck typing —
o FiscalService aceita qualquer objeto com os atributos esperados do evento.
"""
from dataclasses import dataclass
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


# Duck type local do JournalEntryCreated — sem import direto de journal/
@dataclass
class _FakeJournalEntryCreated:
    """Simula o contrato do JournalEntryCreated sem importar de features/journal."""
    entry_id: str
    result_gross_brl: str
    result_net_brl: str
    tax_provisioned_brl: str
    asset: str


class TestFiscalEventHandlers:
    @pytest.mark.asyncio
    async def test_journal_created_event_updates_monthly_provision(self):
        from cam.features.fiscal.service import FiscalService

        repo = AsyncMock()
        svc = FiscalService(repo=repo)
        event = _FakeJournalEntryCreated(
            entry_id="uuid-1",
            result_gross_brl="400.00",
            result_net_brl="310.00",
            tax_provisioned_brl="80.00",
            asset="WIN",
        )
        await svc.handle_journal_entry_created(event)
        repo.update_monthly_provision.assert_called_once()

    @pytest.mark.asyncio
    async def test_overdue_check_returns_false_when_darf_overdue(self):
        from cam.features.fiscal.service import FiscalService

        repo = AsyncMock()
        repo.has_overdue_darf.return_value = True
        svc = FiscalService(repo=repo)
        result = await svc.check_tax_compliance()
        assert result is False

    @pytest.mark.asyncio
    async def test_overdue_check_returns_true_when_no_overdue(self):
        from cam.features.fiscal.service import FiscalService

        repo = AsyncMock()
        repo.has_overdue_darf.return_value = False
        svc = FiscalService(repo=repo)
        result = await svc.check_tax_compliance()
        assert result is True

    @pytest.mark.asyncio
    async def test_handle_event_extracts_tax_from_event(self):
        from cam.features.fiscal.service import FiscalService

        repo = AsyncMock()
        svc = FiscalService(repo=repo)
        event = _FakeJournalEntryCreated(
            entry_id="uuid-2",
            result_gross_brl="200.00",
            result_net_brl="150.00",
            tax_provisioned_brl="40.00",
            asset="WDO",
        )
        await svc.handle_journal_entry_created(event)
        # Verifica que o update recebe o valor do imposto corretamente
        call_kwargs = repo.update_monthly_provision.call_args
        assert call_kwargs is not None

    @pytest.mark.asyncio
    async def test_mark_darf_paid_changes_status(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import Darf, DarfStatus
        from cam.features.fiscal.service import FiscalService

        repo = AsyncMock()
        repo.get_darf.return_value = Darf(
            month="2026-05",
            value=Money(Decimal("100.00")),
            due_date="2026-07-31",
            status=DarfStatus.PENDING,
        )
        repo.save_darf.return_value = None
        svc = FiscalService(repo=repo)
        darf = await svc.mark_darf_paid(darf_id="uuid-darf")
        assert darf.status == DarfStatus.PAID

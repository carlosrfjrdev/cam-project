"""
Testes TDD para o service da feature journal — T-C04.

Valida: campos obrigatórios, publicação de eventos, cálculo de líquido.
"""
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


class TestJournalService:
    @pytest.mark.asyncio
    async def test_missing_required_field_raises(self):
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        svc = JournalService(repo=repo)
        with pytest.raises(ValueError):
            await svc.create_entry(
                asset=None,
                direction="LONG",
                contracts=1,
                entry_price=Decimal("130000"),
                exit_price=Decimal("130200"),
                result_gross=Decimal("400"),
                costs=Decimal("10"),
                strategy="teste",
                setup="A",
            )

    @pytest.mark.asyncio
    async def test_missing_strategy_raises(self):
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        svc = JournalService(repo=repo)
        with pytest.raises(ValueError):
            await svc.create_entry(
                asset="WIN",
                direction="LONG",
                contracts=1,
                entry_price=Decimal("130000"),
                exit_price=Decimal("130200"),
                result_gross=Decimal("400"),
                costs=Decimal("10"),
                strategy=None,
                setup="A",
            )

    @pytest.mark.asyncio
    async def test_entry_published_on_event_bus(self):
        from cam._shared.events import event_bus
        from cam.features.journal.events import JournalEntryCreated
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        repo.save.return_value = "uuid-test-123"
        svc = JournalService(repo=repo)
        received = []

        async def handler(e):
            received.append(e)

        event_bus.subscribe(JournalEntryCreated, handler)
        await svc.create_entry(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130200"),
            result_gross=Decimal("400"),
            costs=Decimal("10"),
            strategy="teste",
            setup="A",
        )
        await event_bus.dispatch_all()
        assert len(received) == 1
        assert received[0].asset == "WIN"
        # Limpar subscriber para não interferir em outros testes
        event_bus._handlers.pop(JournalEntryCreated, None)

    @pytest.mark.asyncio
    async def test_result_net_always_calculated(self):
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        repo.save.return_value = "uuid"
        svc = JournalService(repo=repo)
        result = await svc.create_entry(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130200"),
            result_gross=Decimal("400"),
            costs=Decimal("10"),
            strategy="teste",
            setup="A",
        )
        assert result.result_net is not None
        assert result.tax_provisioned.amount == Decimal("80.00")  # 20% de 400
        assert result.result_net.amount == Decimal("310.00")

    @pytest.mark.asyncio
    async def test_loss_entry_zero_tax(self):
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        repo.save.return_value = "uuid"
        svc = JournalService(repo=repo)
        result = await svc.create_entry(
            asset="WIN",
            direction="SHORT",
            contracts=1,
            entry_price=Decimal("130200"),
            exit_price=Decimal("130000"),
            result_gross=Decimal("-400"),
            costs=Decimal("10"),
            strategy="teste",
            setup="B",
        )
        assert result.tax_provisioned.amount == Decimal("0.00")
        assert result.result_net.amount == Decimal("-410.00")

    @pytest.mark.asyncio
    async def test_event_contains_correct_entry_id(self):
        from cam._shared.events import event_bus
        from cam.features.journal.events import JournalEntryCreated
        from cam.features.journal.service import JournalService

        # Limpa fila e handlers residuais de outros testes
        event_bus.clear()
        event_bus._handlers.pop(JournalEntryCreated, None)

        repo = AsyncMock()
        repo.save.return_value = "uuid-fixed"
        svc = JournalService(repo=repo)
        received = []

        async def handler(e):
            received.append(e)

        event_bus.subscribe(JournalEntryCreated, handler)
        await svc.create_entry(
            asset="WDO",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("5.200"),
            exit_price=Decimal("5.210"),
            result_gross=Decimal("50"),
            costs=Decimal("5"),
            strategy="scalp",
            setup="A+",
        )
        await event_bus.dispatch_all()
        assert received[0].entry_id == "uuid-fixed"
        event_bus._handlers.pop(JournalEntryCreated, None)

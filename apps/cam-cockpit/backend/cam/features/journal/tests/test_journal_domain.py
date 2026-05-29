"""
Testes TDD para o domínio e persistência da feature journal — T-C03.

Art. 25º: resultado nunca exibido sem líquido.
Art. 31º: toda operação DEVE ter JournalEntry correspondente.
cam_journal_entries é IMUTÁVEL — sem UPDATE nem DELETE.
"""
from decimal import Decimal

import pytest


class TestJournalEntryDomain:
    def test_net_result_calculated_correctly(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130200"),
            result_gross=Money(Decimal("400.00")),
            costs=Money(Decimal("10.00")),
            strategy="teste",
            setup="A",
        )
        # IR = 20% de 400 = 80; líquido = 400 - 10 - 80 = 310
        assert entry.result_net.amount == Decimal("310.00")
        assert entry.tax_provisioned.amount == Decimal("80.00")

    def test_net_result_no_tax_on_loss(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WIN",
            direction="SHORT",
            contracts=1,
            entry_price=Decimal("130200"),
            exit_price=Decimal("130000"),
            result_gross=Money(Decimal("-400.00")),
            costs=Money(Decimal("10.00")),
            strategy="teste",
            setup="B",
        )
        # Sem IR em loss
        assert entry.tax_provisioned.amount == Decimal("0.00")
        assert entry.result_net.amount == Decimal("-410.00")

    def test_result_net_never_bruto_without_liquido(self):
        """Art. 25º — garantia que o domínio sempre calcula o líquido."""
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WDO",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("5.200"),
            exit_price=Decimal("5.210"),
            result_gross=Money(Decimal("50.00")),
            costs=Money(Decimal("5.00")),
            strategy="teste",
            setup="A",
        )
        assert hasattr(entry, "result_net"), (
            "JournalEntry deve sempre expor result_net (Art. 25º)"
        )
        assert hasattr(entry, "tax_provisioned")

    def test_zero_gross_result_zero_tax(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130000"),
            result_gross=Money(Decimal("0.00")),
            costs=Money(Decimal("10.00")),
            strategy="teste",
            setup="A",
        )
        assert entry.tax_provisioned.amount == Decimal("0.00")
        assert entry.result_net.amount == Decimal("-10.00")

    def test_wdo_entry_calculates_net_correctly(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WDO",
            direction="SHORT",
            contracts=2,
            entry_price=Decimal("5.300"),
            exit_price=Decimal("5.280"),
            result_gross=Money(Decimal("200.00")),
            costs=Money(Decimal("15.00")),
            strategy="swing",
            setup="B+",
        )
        # IR = 200 * 20% = 40; líquido = 200 - 15 - 40 = 145
        assert entry.tax_provisioned.amount == Decimal("40.00")
        assert entry.result_net.amount == Decimal("145.00")

    def test_source_defaults_to_manual(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.domain import JournalEntry

        entry = JournalEntry(
            asset="WIN",
            direction="LONG",
            contracts=1,
            entry_price=Decimal("130000"),
            exit_price=Decimal("130100"),
            result_gross=Money(Decimal("100.00")),
            costs=Money(Decimal("5.00")),
            strategy="teste",
            setup="A",
        )
        assert entry.source == "MANUAL"


class TestJournalRepository:
    @pytest.mark.asyncio
    async def test_repository_does_not_allow_update(self):
        """
        cam_journal_entries é imutável — sem método update.

        Verifica que JournalRepository não expõe método 'update'.
        """
        from cam.features.journal.repository import JournalRepository

        assert not hasattr(JournalRepository, "update"), (
            "JournalRepository não deve ter método 'update' — "
            "cam_journal_entries é imutável."
        )

    @pytest.mark.asyncio
    async def test_repository_does_not_allow_delete(self):
        """
        cam_journal_entries é imutável — sem método delete.

        Verifica que JournalRepository não expõe método 'delete'.
        """
        from cam.features.journal.repository import JournalRepository

        assert not hasattr(JournalRepository, "delete"), (
            "JournalRepository não deve ter método 'delete' — "
            "cam_journal_entries é imutável."
        )

"""
Testes TDD para o domínio da feature harvest — T-C08.

Arts. 21º, 22º da Constituição. Harvest Rule não é automático.
Gate Founder obrigatório: R4.07.
"""
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


class TestHarvestProposal:
    def test_harvest_splits_60_40(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import HarvestCalculator

        calc = HarvestCalculator(
            net_monthly_profit=Money(Decimal("500.00")),
            buffer_current=Money(Decimal("800.00")),
            buffer_baseline=Money(Decimal("1000.00")),
        )
        proposal = calc.calculate()
        # 60% → Carteira Hard = 300.00
        # 40% → Buffer = 200.00 (até completar os R$ 1.000 de baseline)
        assert proposal.carteira_hard_amount.amount == Decimal("300.00")
        assert proposal.buffer_amount.amount == Decimal("200.00")

    def test_harvest_full_to_carteira_when_buffer_full(self):
        """Quando buffer já atingiu baseline, 100% vai para Carteira Hard."""
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import HarvestCalculator

        calc = HarvestCalculator(
            net_monthly_profit=Money(Decimal("500.00")),
            buffer_current=Money(Decimal("1000.00")),  # baseline atingido
            buffer_baseline=Money(Decimal("1000.00")),
        )
        proposal = calc.calculate()
        # Buffer já na baseline → 100% para Carteira Hard
        assert proposal.carteira_hard_amount.amount == Decimal("500.00")
        assert proposal.buffer_amount.amount == Decimal("0.00")

    def test_harvest_buffer_capped_at_needed_amount(self):
        """Buffer recebe apenas o necessário para atingir a baseline."""
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import HarvestCalculator

        calc = HarvestCalculator(
            net_monthly_profit=Money(Decimal("1000.00")),
            buffer_current=Money(Decimal("950.00")),   # faltam R$ 50
            buffer_baseline=Money(Decimal("1000.00")),
        )
        proposal = calc.calculate()
        # Buffer precisa de R$ 50; 40% de 1000 = 400 mas só 50 vai para buffer
        # Excedente (350) vai junto para Carteira Hard
        assert proposal.buffer_amount.amount == Decimal("50.00")
        assert proposal.carteira_hard_amount.amount == Decimal("950.00")


class TestSangriaCalculator:
    def test_sangria_triggered_when_bucket_reaches_4500(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import SangriaCalculator

        calc = SangriaCalculator(
            bucket_derivativo_current=Money(Decimal("4500.00")),
            bucket_derivativo_baseline=Money(Decimal("3000.00")),
        )
        sangria = calc.calculate()
        # excess = 1500; 80% → Carteira Hard = 1200; 20% → Buffer/Provisão = 300
        assert sangria.carteira_hard_amount.amount == Decimal("1200.00")
        assert sangria.buffer_amount.amount == Decimal("300.00")

    def test_no_sangria_below_4500(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import SangriaCalculator

        calc = SangriaCalculator(
            bucket_derivativo_current=Money(Decimal("4000.00")),
            bucket_derivativo_baseline=Money(Decimal("3000.00")),
        )
        sangria = calc.calculate()
        assert sangria is None

    def test_sangria_exact_at_4500(self):
        """Sangria disparada quando bucket = exatamente R$ 4.500."""
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import SangriaCalculator

        calc = SangriaCalculator(
            bucket_derivativo_current=Money(Decimal("4500.00")),
            bucket_derivativo_baseline=Money(Decimal("3000.00")),
        )
        sangria = calc.calculate()
        assert sangria is not None

    def test_sangria_excess_calculation(self):
        """Excedente = bucket_atual - baseline (3000)."""
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import SangriaCalculator

        calc = SangriaCalculator(
            bucket_derivativo_current=Money(Decimal("4600.00")),
            bucket_derivativo_baseline=Money(Decimal("3000.00")),
        )
        sangria = calc.calculate()
        assert sangria.excess.amount == Decimal("1600.00")
        assert sangria.carteira_hard_amount.amount == Decimal("1280.00")  # 80%
        assert sangria.buffer_amount.amount == Decimal("320.00")          # 20%


class TestHarvestRequiresFounderApproval:
    def test_harvest_requires_founder_approval(self):
        """Harvest não se auto-executa — precisa de founder_approved=True."""
        import asyncio

        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        svc = HarvestService(repo=repo)
        with pytest.raises(ValueError, match="founder_approved"):
            asyncio.run(svc.execute_harvest(proposal_id="uuid", founder_approved=False))

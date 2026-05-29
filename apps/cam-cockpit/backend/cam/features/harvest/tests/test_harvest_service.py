"""
Testes TDD para o service da feature harvest — T-C09.

Gate Founder obrigatório (R4.07): POST /harvest/execute requer founder_approved=True.
"""
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest


class TestHarvestService:
    @pytest.mark.asyncio
    async def test_execute_harvest_without_approval_raises(self):
        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        svc = HarvestService(repo=repo)
        with pytest.raises(ValueError, match="founder_approved"):
            await svc.execute_harvest(proposal_id="uuid", founder_approved=False)

    @pytest.mark.asyncio
    async def test_execute_harvest_with_approval_saves_transactions(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.domain import HarvestProposal
        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        repo.get_proposal.return_value = HarvestProposal(
            net_monthly_profit=Money(Decimal("500.00")),
            carteira_hard_amount=Money(Decimal("300.00")),
            buffer_amount=Money(Decimal("200.00")),
        )
        svc = HarvestService(repo=repo)
        await svc.execute_harvest(proposal_id="uuid", founder_approved=True)
        assert repo.save_transactions.called

    @pytest.mark.asyncio
    async def test_execute_harvest_raises_if_proposal_not_found(self):
        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        repo.get_proposal.return_value = None
        svc = HarvestService(repo=repo)
        with pytest.raises(ValueError, match="não encontrada"):
            await svc.execute_harvest(
                proposal_id="uuid-invalido", founder_approved=True
            )

    @pytest.mark.asyncio
    async def test_check_sangria_returns_none_below_threshold(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        repo.get_bucket_derivativo_current.return_value = Money(Decimal("4000.00"))
        repo.get_bucket_derivativo_baseline.return_value = Money(Decimal("3000.00"))
        svc = HarvestService(repo=repo)
        result = await svc.check_sangria()
        assert result is None

    @pytest.mark.asyncio
    async def test_check_sangria_returns_result_above_threshold(self):
        from cam._shared.domain.primitives import Money
        from cam.features.harvest.service import HarvestService

        repo = AsyncMock()
        repo.get_bucket_derivativo_current.return_value = Money(Decimal("4600.00"))
        repo.get_bucket_derivativo_baseline.return_value = Money(Decimal("3000.00"))
        svc = HarvestService(repo=repo)
        result = await svc.check_sangria()
        assert result is not None
        assert result.excess.amount == Decimal("1600.00")

    @pytest.mark.asyncio
    async def test_routes_execute_requires_founder_approved_true(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/harvest/execute",
                json={"proposal_id": "uuid", "founder_approved": False},
            )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_routes_get_buckets_returns_200(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/ledger/buckets")
        assert response.status_code == 200

"""
Testes TDD para relatórios e exportação do journal — T-C05.

Art. 25º: todo relatório inclui result_net e tax_provisioned.
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestJournalReports:
    @pytest.mark.asyncio
    async def test_daily_report_includes_net_result(self):
        """Art. 25º — relatório sempre mostra líquido."""
        from cam._shared.domain.primitives import Money
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        entry = MagicMock()
        entry.result_gross = Money(Decimal("400"))
        entry.result_net = Money(Decimal("310"))
        entry.tax_provisioned = Money(Decimal("80"))
        entry.costs = Money(Decimal("10"))
        repo.list_by_date.return_value = [entry]
        svc = JournalService(repo=repo)
        report = await svc.daily_report(date="2026-05-24")
        assert "result_net" in report
        assert "tax_provisioned" in report
        assert "result_gross" in report

    @pytest.mark.asyncio
    async def test_daily_report_calculates_win_rate(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        win_entry = MagicMock()
        win_entry.result_gross = Money(Decimal("400"))
        win_entry.result_net = Money(Decimal("310"))
        win_entry.tax_provisioned = Money(Decimal("80"))
        win_entry.costs = Money(Decimal("10"))

        loss_entry = MagicMock()
        loss_entry.result_gross = Money(Decimal("-200"))
        loss_entry.result_net = Money(Decimal("-210"))
        loss_entry.tax_provisioned = Money(Decimal("0"))
        loss_entry.costs = Money(Decimal("10"))

        repo.list_by_date.return_value = [win_entry, loss_entry]
        svc = JournalService(repo=repo)
        report = await svc.daily_report(date="2026-05-24")
        assert report["total_operations"] == 2
        assert report["win_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_csv_export_includes_all_fields(self):
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        repo.list_all.return_value = []
        svc = JournalService(repo=repo)
        csv_content = await svc.export_csv()
        assert isinstance(csv_content, str)
        # Art. 25º: CSV contém cabeçalhos com result_net e tax_provisioned
        assert "result_net" in csv_content
        assert "tax_provisioned" in csv_content
        assert "result_gross" in csv_content

    @pytest.mark.asyncio
    async def test_report_by_strategy_returns_net(self):
        from cam._shared.domain.primitives import Money
        from cam.features.journal.service import JournalService

        repo = AsyncMock()
        entry = MagicMock()
        entry.result_gross = Money(Decimal("500"))
        entry.result_net = Money(Decimal("390"))
        entry.tax_provisioned = Money(Decimal("100"))
        entry.costs = Money(Decimal("10"))
        repo.list_by_strategy.return_value = [entry]
        svc = JournalService(repo=repo)
        report = await svc.report_by_strategy(strategy="scalp")
        assert "result_net" in report
        assert "tax_provisioned" in report

    @pytest.mark.asyncio
    async def test_routes_export_endpoint_exists(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/journal/export")
        # 200 com CSV ou 400/422 — mas o endpoint deve existir (não 404)
        assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_routes_daily_report_endpoint_exists(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/journal/reports/daily?date=2026-05-24")
        assert response.status_code != 404

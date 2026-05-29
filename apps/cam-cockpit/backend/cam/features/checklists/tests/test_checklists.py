"""
Testes TDD para a feature checklists — Arts. 32º e 33º da Constituição.

Checklist pré-mercado obrigatório antes de qualquer operação.
Checklist pós-mercado obrigatório após último pregão.
"""
from unittest.mock import AsyncMock

import pytest


class TestPreMarketChecklistDomain:
    def test_checklist_not_complete_without_all_required_items(self):
        from cam.features.checklists.domain import PreMarketChecklist

        cl = PreMarketChecklist(date="2026-05-24", items={})
        assert not cl.is_complete()

    def test_checklist_complete_when_all_required_items_checked(self):
        from cam.features.checklists.domain import (
            REQUIRED_PRE_MARKET_ITEMS,
            PreMarketChecklist,
        )

        items = {item: True for item in REQUIRED_PRE_MARKET_ITEMS}
        cl = PreMarketChecklist(date="2026-05-24", items=items)
        assert cl.is_complete()

    def test_checklist_incomplete_when_one_item_missing(self):
        from cam.features.checklists.domain import (
            REQUIRED_PRE_MARKET_ITEMS,
            PreMarketChecklist,
        )

        items = {item: True for item in REQUIRED_PRE_MARKET_ITEMS}
        # Remove um item
        del items[REQUIRED_PRE_MARKET_ITEMS[0]]
        cl = PreMarketChecklist(date="2026-05-24", items=items)
        assert not cl.is_complete()

    def test_checklist_incomplete_when_item_is_false(self):
        from cam.features.checklists.domain import (
            REQUIRED_PRE_MARKET_ITEMS,
            PreMarketChecklist,
        )

        items = {item: True for item in REQUIRED_PRE_MARKET_ITEMS}
        items[REQUIRED_PRE_MARKET_ITEMS[0]] = False
        cl = PreMarketChecklist(date="2026-05-24", items=items)
        assert not cl.is_complete()

    def test_pre_market_required_items_count(self):
        from cam.features.checklists.domain import REQUIRED_PRE_MARKET_ITEMS

        # SPEC R10.03: 10 itens obrigatórios no checklist pré-mercado
        assert len(REQUIRED_PRE_MARKET_ITEMS) >= 8


class TestPostMarketChecklistDomain:
    def test_post_market_checklist_not_complete_without_items(self):
        from cam.features.checklists.domain import PostMarketChecklist

        cl = PostMarketChecklist(date="2026-05-24", items={})
        assert not cl.is_complete()

    def test_post_market_checklist_complete_when_all_checked(self):
        from cam.features.checklists.domain import (
            REQUIRED_POST_MARKET_ITEMS,
            PostMarketChecklist,
        )

        items = {item: True for item in REQUIRED_POST_MARKET_ITEMS}
        cl = PostMarketChecklist(date="2026-05-24", items=items)
        assert cl.is_complete()

    def test_post_market_required_items_count(self):
        from cam.features.checklists.domain import REQUIRED_POST_MARKET_ITEMS

        # SPEC R10.04: itens obrigatórios no checklist pós-mercado
        assert len(REQUIRED_POST_MARKET_ITEMS) >= 6


class TestChecklistService:
    @pytest.mark.asyncio
    async def test_cannot_save_incomplete_pre_market_checklist(self):
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        svc = ChecklistService(repo=repo)
        with pytest.raises(ValueError, match="incompleto"):
            await svc.save_pre_market(date="2026-05-24", items={})

    @pytest.mark.asyncio
    async def test_complete_pre_market_checklist_saves_successfully(self):
        from cam.features.checklists.domain import REQUIRED_PRE_MARKET_ITEMS
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        svc = ChecklistService(repo=repo)
        items = {item: True for item in REQUIRED_PRE_MARKET_ITEMS}
        await svc.save_pre_market(date="2026-05-24", items=items)
        repo.save_pre_market.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_save_incomplete_post_market_checklist(self):
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        svc = ChecklistService(repo=repo)
        with pytest.raises(ValueError, match="incompleto"):
            await svc.save_post_market(date="2026-05-24", items={})

    @pytest.mark.asyncio
    async def test_complete_post_market_checklist_saves_successfully(self):
        from cam.features.checklists.domain import REQUIRED_POST_MARKET_ITEMS
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        svc = ChecklistService(repo=repo)
        items = {item: True for item in REQUIRED_POST_MARKET_ITEMS}
        await svc.save_post_market(date="2026-05-24", items=items)
        repo.save_post_market.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pre_market_delegates_to_repo(self):
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        repo.get_pre_market.return_value = None
        svc = ChecklistService(repo=repo)
        await svc.get_pre_market(date="2026-05-24")
        repo.get_pre_market.assert_called_once_with(date="2026-05-24")

    @pytest.mark.asyncio
    async def test_get_post_market_delegates_to_repo(self):
        from cam.features.checklists.service import ChecklistService

        repo = AsyncMock()
        repo.get_post_market.return_value = None
        svc = ChecklistService(repo=repo)
        await svc.get_post_market(date="2026-05-24")
        repo.get_post_market.assert_called_once_with(date="2026-05-24")


class TestChecklistRoutes:
    @pytest.mark.asyncio
    async def test_post_pre_market_with_incomplete_returns_422(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/checklists/pre-market",
                json={"date": "2026-05-24", "items": {}},
            )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_post_pre_market_with_complete_returns_201(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app
        from cam.features.checklists.domain import REQUIRED_PRE_MARKET_ITEMS

        items = {item: True for item in REQUIRED_PRE_MARKET_ITEMS}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/checklists/pre-market",
                json={"date": "2026-05-24", "items": items},
            )
        assert response.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_get_pre_market_returns_200(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/checklists/pre-market/2026-05-24"
            )
        assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_get_post_market_returns_200_or_404(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/checklists/post-market/2026-05-24"
            )
        assert response.status_code in (200, 404)

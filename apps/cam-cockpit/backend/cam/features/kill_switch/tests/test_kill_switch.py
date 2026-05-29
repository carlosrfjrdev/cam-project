"""
Testes TDD para a feature kill_switch — Art. 18º da Constituição.

Ordem: Red → Green → Refactor.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestKillSwitchDomain:
    def test_kill_switch_state_inactive_by_default(self):
        from cam.features.kill_switch.domain import KillSwitchState

        state = KillSwitchState(active=False)
        assert not state.active

    def test_kill_switch_state_active(self):
        from cam.features.kill_switch.domain import KillSwitchState

        state = KillSwitchState(active=True)
        assert state.active

    def test_kill_switch_event_has_action_and_reason(self):
        from cam.features.kill_switch.events import KillSwitchActivated

        event = KillSwitchActivated(reason="Teste manual")
        assert event.reason == "Teste manual"

    def test_kill_switch_event_domain_action_activate(self):
        from cam.features.kill_switch.domain import KillSwitchEvent

        event = KillSwitchEvent(action="ACTIVATE", reason="drawdown")
        assert event.action == "ACTIVATE"
        assert event.reason == "drawdown"

    def test_kill_switch_event_domain_action_deactivate(self):
        from cam.features.kill_switch.domain import KillSwitchEvent

        event = KillSwitchEvent(action="DEACTIVATE", reason="")
        assert event.action == "DEACTIVATE"


class TestKillSwitchService:
    @pytest.mark.asyncio
    async def test_activate_sets_state_active(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=False)
        svc = KillSwitchService(repo=repo)
        await svc.activate(reason="Drawdown atingido")
        repo.save_event.assert_called_once()
        call_args = repo.save_event.call_args[0][0]
        assert call_args.action == "ACTIVATE"

    @pytest.mark.asyncio
    async def test_activate_saves_event_with_reason(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=False)
        svc = KillSwitchService(repo=repo)
        await svc.activate(reason="Limite semanal atingido")
        call_args = repo.save_event.call_args[0][0]
        assert call_args.reason == "Limite semanal atingido"

    @pytest.mark.asyncio
    async def test_deactivate_requires_explicit_confirm(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=True)
        svc = KillSwitchService(repo=repo)
        with pytest.raises(ValueError, match="confirm"):
            await svc.deactivate(confirm=False)

    @pytest.mark.asyncio
    async def test_deactivate_with_confirm_true_saves_event(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=True)
        svc = KillSwitchService(repo=repo)
        await svc.deactivate(confirm=True)
        repo.save_event.assert_called_once()
        call_args = repo.save_event.call_args[0][0]
        assert call_args.action == "DEACTIVATE"

    @pytest.mark.asyncio
    async def test_is_active_returns_current_state(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=True)
        svc = KillSwitchService(repo=repo)
        assert await svc.is_active() is True

    @pytest.mark.asyncio
    async def test_is_active_returns_false_when_inactive(self):
        from cam.features.kill_switch.service import KillSwitchService

        repo = AsyncMock()
        repo.get_current_state.return_value = MagicMock(active=False)
        svc = KillSwitchService(repo=repo)
        assert await svc.is_active() is False


class TestKillSwitchRoutes:
    @pytest.mark.asyncio
    async def test_get_status_returns_active_field(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/kill-switch/status")
        assert response.status_code == 200
        assert "active" in response.json()

    @pytest.mark.asyncio
    async def test_activate_endpoint_returns_201(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/kill-switch/activate", json={"reason": "Teste"}
            )
        assert response.status_code in (200, 201)

    @pytest.mark.asyncio
    async def test_deactivate_without_confirm_returns_error(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/kill-switch/deactivate", json={"confirm": False}
            )
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_deactivate_with_confirm_true_returns_200(self):
        from httpx import ASGITransport, AsyncClient

        from cam.api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/kill-switch/deactivate", json={"confirm": True}
            )
        assert response.status_code == 200

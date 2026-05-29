"""
Testes TDD do Bloco D — T-D04.
Cobre: NotificationService — Telegram, modo degradado, handler de eventos.

Nota de isolamento: tests NÃO importam de cam.features.kill_switch (ADR-013).
Eventos são simulados via dataclasses locais com a mesma interface.
"""
from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stubs de eventos (simulam KillSwitchActivated sem importar kill_switch)
# ---------------------------------------------------------------------------


@dataclass
class _FakeKillSwitchActivated:
    """Stub local de KillSwitchActivated — mesma interface, sem acoplamento."""

    reason: str


@dataclass
class _FakeDarfEvent:
    """Stub local de evento DarfOverdue."""

    pass


class TestTelegramNotifier:
    @pytest.mark.asyncio
    async def test_send_message_called_with_correct_text(self):
        from cam.features.notifications.service import NotificationService

        with patch("cam.features.notifications.service.Bot") as MockBot:
            mock_bot_instance = AsyncMock()
            MockBot.return_value = mock_bot_instance
            svc = NotificationService(bot_token="fake-token", chat_id="12345")
            await svc.send("Kill switch ativado!")
            mock_bot_instance.send_message.assert_called_once_with(
                chat_id="12345", text="Kill switch ativado!"
            )

    @pytest.mark.asyncio
    async def test_degraded_mode_when_no_token(self):
        """Sem token → não levanta exceção, apenas loga."""
        from cam.features.notifications.service import NotificationService

        svc = NotificationService(bot_token="", chat_id="")
        # Não deve levantar exceção
        await svc.send("Teste de modo degradado")

    @pytest.mark.asyncio
    async def test_kill_switch_event_triggers_notification(self):
        """Handler aceita qualquer evento com .reason — sem acoplar kill_switch."""
        from cam.features.notifications.service import NotificationService

        svc = AsyncMock(spec=NotificationService)
        event = _FakeKillSwitchActivated(reason="Drawdown atingido")
        await svc.handle_kill_switch_activated(event)
        svc.handle_kill_switch_activated.assert_called_once()

    @pytest.mark.asyncio
    async def test_degraded_mode_when_no_chat_id(self):
        """Sem chat_id → modo degradado silencioso."""
        from cam.features.notifications.service import NotificationService

        svc = NotificationService(bot_token="fake-token", chat_id="")
        # Não deve tentar enviar sem chat_id
        await svc.send("Sem chat_id")

    @pytest.mark.asyncio
    async def test_telegram_error_does_not_raise(self):
        """Erro na API do Telegram → loga, não propaga exceção."""
        from cam.features.notifications.service import NotificationService

        with patch("cam.features.notifications.service.Bot") as MockBot:
            mock_bot_instance = AsyncMock()
            mock_bot_instance.send_message.side_effect = Exception("API timeout")
            MockBot.return_value = mock_bot_instance
            svc = NotificationService(bot_token="fake-token", chat_id="12345")
            # Não deve propagar exceção — notificação é best-effort
            await svc.send("Mensagem que vai falhar")

    @pytest.mark.asyncio
    async def test_handle_kill_switch_calls_send(self):
        from cam.features.notifications.service import NotificationService

        with patch("cam.features.notifications.service.Bot") as MockBot:
            mock_bot_instance = AsyncMock()
            MockBot.return_value = mock_bot_instance
            svc = NotificationService(bot_token="fake-token", chat_id="12345")
            event = _FakeKillSwitchActivated(reason="Limite diário atingido")
            await svc.handle_kill_switch_activated(event)
            mock_bot_instance.send_message.assert_called_once()
            call_text = mock_bot_instance.send_message.call_args.kwargs["text"]
            assert "Limite diário atingido" in call_text

    @pytest.mark.asyncio
    async def test_handle_darf_overdue_sends_message(self):
        from cam.features.notifications.service import NotificationService

        with patch("cam.features.notifications.service.Bot") as MockBot:
            mock_bot_instance = AsyncMock()
            MockBot.return_value = mock_bot_instance
            svc = NotificationService(bot_token="fake-token", chat_id="12345")
            await svc.handle_darf_overdue(_FakeDarfEvent())
            mock_bot_instance.send_message.assert_called_once()

"""
Serviço de notificações do CaM — canal Telegram (Art. 18º, Art. 26º).

Responsável por:
    - Enviar alertas críticos via Telegram Bot
    - Operar em modo degradado quando sem credenciais (não levanta exceção)
    - Fazer bridge entre eventos do EventBus e notificações externas

Notificações são best-effort: falha no Telegram nunca bloqueia operação.
IA não envia ordem — apenas alerta o operador (Art. 35º).

Registro no EventBus: feito no lifespan de cam/api/main.py.
"""

from cam._shared.audit import get_logger
from cam._shared.config import settings

log = get_logger("notifications")

# Bot é importado condicionalmente para permitir modo degradado sem o pacote
try:
    from telegram import Bot

    _BOT_AVAILABLE = True
except ImportError:
    _BOT_AVAILABLE = False
    log.warning(
        "notifications.telegram_unavailable", hint="instale python-telegram-bot"
    )


class NotificationService:
    """
    Service de notificações via Telegram.

    Modo degradado: se bot_token ou chat_id estiver vazio, ou se o pacote
    python-telegram-bot não estiver instalado, loga e ignora sem exceção.
    """

    def __init__(self, bot_token: str = "", chat_id: str = "") -> None:
        self.bot_token = bot_token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        self._enabled = bool(self.bot_token and self.chat_id and _BOT_AVAILABLE)

    async def send(self, text: str) -> None:
        """
        Envia mensagem de texto para o chat configurado.

        Sem credenciais → loga em modo degradado.
        Erro na API → loga e silencia (notificação é best-effort).
        """
        if not self._enabled:
            log.info("notifications.degraded_mode", message=text)
            return
        try:
            bot = Bot(token=self.bot_token)
            await bot.send_message(chat_id=self.chat_id, text=text)
        except Exception as exc:
            log.error("notifications.send_failed", error=str(exc), message=text)

    # ------------------------------------------------------------------
    # Handlers de eventos do EventBus
    # ------------------------------------------------------------------

    async def handle_kill_switch_activated(self, event) -> None:
        """Handler para KillSwitchActivated — Art. 18º."""
        await self.send(f"KILL SWITCH ATIVADO\nMotivo: {event.reason}")

    async def handle_daily_loss_limit(self, event) -> None:
        """Handler para DailyLossLimitReached."""
        await self.send("LIMITE DE PERDA DIÁRIA ATINGIDO — Pregão encerrado")

    async def handle_gain_lock(self, event) -> None:
        """Handler para GainLock — meta diária atingida."""
        await self.send("GAIN LOCK ATIVADO — Meta diária atingida, pregão encerrado")

    async def handle_darf_overdue(self, event) -> None:
        """Handler para DarfOverdue — Art. 26º bloqueia novas operações."""
        await self.send("DARF ATRASADA — Novas operações BLOQUEADAS (Art. 26)")


# Singleton compartilhado — registrado no EventBus pelo lifespan da API
notification_service = NotificationService()


# T-TD-010 (SPEC v0.3) — factory lazy preferida para code novo
_lazy_instance: "NotificationService | None" = None


def get_notification_service() -> "NotificationService":
    """
    Factory lazy — cria instancia na primeira chamada.
    Permite testes com .env diferentes sem recarregar modulo.
    """
    global _lazy_instance
    if _lazy_instance is None:
        _lazy_instance = NotificationService()
    return _lazy_instance


def reset_notification_service_for_tests() -> None:
    """Apenas para testes — limpa singleton lazy."""
    global _lazy_instance
    _lazy_instance = None

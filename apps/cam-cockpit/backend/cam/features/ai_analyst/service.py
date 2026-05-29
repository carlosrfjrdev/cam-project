"""
Lógica de aplicação da IA Auditora do CaM.

Responsabilidades:
- Orquestrar coleta read-only de dados operacionais
- Construir prompt com restrições constitucionais embutidas
- Chamar provider LLM e passar output pelo ContentGuard
- Logar violações e descartar análises proibidas
- Enviar análise aprovada via notificador (Telegram)

Arts. 34-36 da Constituição: IA NÃO PODE enviar ordem, desabilitar Risk Engine
nem justificar exceção constitucional. Toda análise passa pelo ContentGuard antes
de qualquer entrega.

PROIBIÇÕES ABSOLUTAS neste módulo (Arts. 34-36):
- Zero imports de services de outras features (journal, kill_switch, fiscal, harvest)
- Zero chamadas de escrita — apenas read via AnalystDataCollector
- Nunca contornar ou desabilitar o ContentGuard
"""
from cam._shared.audit import get_logger
from cam.features.ai_analyst.content_guard import ContentGuard
from cam.features.ai_analyst.prompts import build_analysis_prompt

log = get_logger("ai_analyst.service")


class AIAnalystService:
    """
    Serviço principal da IA Auditora.

    Fluxo de análise:
    1. Coletar dados read-only (journal + decisões Risk Engine)
    2. Construir prompt com restrições constitucionais
    3. Enviar ao LLM via provider
    4. Verificar output no ContentGuard
    5. Se aprovado: enviar via notificador
    6. Se rejeitado: logar violação e descartar

    Args:
        provider: OllamaProvider, AnthropicProvider ou ProviderWithFallback
        guard: ContentGuard para verificação de conteúdo proibido
        notifier: Serviço de notificação (Telegram) — pode ser None em testes
        collector: AnalystDataCollector para leitura de dados — pode ser None em testes
    """

    def __init__(self, provider, guard: ContentGuard, notifier, collector) -> None:
        self.provider = provider
        self.guard = guard
        self.notifier = notifier
        self.collector = collector

    async def _analyze_and_guard(self, prompt: str) -> str | None:
        """
        Envia prompt ao LLM e verifica output no ContentGuard.

        Returns:
            str com análise aprovada, ou None se análise foi rejeitada/falhou
        """
        try:
            raw = await self.provider.analyze(prompt)
        except Exception as e:
            log.error("ai_analyst.provider_error", error=str(e))
            return None

        text, prohibited = self.guard.sanitize_or_reject(raw)
        if prohibited:
            log.warning(
                "ai_analyst.prohibited_content_detected",
                raw_excerpt=raw[:200],
            )
            return None

        return text

    async def run_daily_analysis(self, date: str) -> dict:
        """
        Executa análise diária pós-fechamento de mercado.

        Coleta dados do dia, gera análise, verifica conteúdo e envia via Telegram.

        Args:
            date: Data no formato YYYY-MM-DD

        Returns:
            Dict com: date, has_prohibited_content, analysis, sent_telegram
        """
        entries: list[dict] = []
        decisions: list[dict] = []

        if self.collector:
            entries = await self.collector.get_journal_entries_today(date)
            decisions = await self.collector.get_risk_decisions_today(date)

        prompt = build_analysis_prompt(
            journal_entries=entries, risk_decisions=decisions
        )
        analysis = await self._analyze_and_guard(prompt)

        # has_prohibited_content é True quando análise foi gerada mas rejeitada
        # (se provider falhou com exception, analysis é None — não é conteúdo proibido)
        has_prohibited = analysis is None and len(prompt) > 0

        sent = False
        if analysis and self.notifier:
            msg = f"Análise IA — {date}\n\n{analysis}"
            await self.notifier.send(msg)
            sent = True
            log.info("ai_analyst.analysis_sent", date=date, sent_telegram=True)

        return {
            "date": date,
            "has_prohibited_content": has_prohibited,
            "analysis": analysis,
            "sent_telegram": sent,
        }

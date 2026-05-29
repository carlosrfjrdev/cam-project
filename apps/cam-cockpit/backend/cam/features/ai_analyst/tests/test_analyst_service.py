"""
T-G03 — Testes TDD First: Scheduler e fluxo completo do serviço.

Testa o fluxo completo de análise diária: coleta, análise, guard e entrega.
Testa configuração do scheduler para execução pós-mercado (18:30 BRT / 21:30 UTC).
"""
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestAIAnalystService:
    @pytest.mark.asyncio
    async def test_run_daily_analysis_complete_flow(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FakeProvider:
            async def analyze(self, prompt: str) -> str:
                return "Análise do dia: aderência 100%, 2 trades, líquido R$ 150."

        collector = AsyncMock()
        collector.get_journal_entries_today.return_value = []
        collector.get_risk_decisions_today.return_value = []

        notifier = AsyncMock()
        guard = ContentGuard()

        svc = AIAnalystService(
            provider=FakeProvider(), guard=guard, notifier=notifier, collector=collector
        )
        result = await svc.run_daily_analysis(date="2026-05-25")

        assert result is not None
        assert result["sent_telegram"] or result["has_prohibited_content"] is False
        notifier.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_prohibited_content_not_sent_to_telegram(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FakeProvider:
            async def analyze(self, prompt: str) -> str:
                return "Recomendo comprar WIN agora."

        collector = AsyncMock()
        collector.get_journal_entries_today.return_value = []
        collector.get_risk_decisions_today.return_value = []
        notifier = AsyncMock()
        guard = ContentGuard()
        svc = AIAnalystService(
            provider=FakeProvider(), guard=guard, notifier=notifier, collector=collector
        )
        result = await svc.run_daily_analysis(date="2026-05-25")
        notifier.send.assert_not_called()
        assert result["has_prohibited_content"] is True

    @pytest.mark.asyncio
    async def test_result_includes_required_fields(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FakeProvider:
            async def analyze(self, prompt: str) -> str:
                return "Padrão de loss nas primeiras horas do pregão."

        svc = AIAnalystService(
            provider=FakeProvider(),
            guard=ContentGuard(),
            notifier=None,
            collector=None,
        )
        result = await svc.run_daily_analysis(date="2026-05-25")
        assert "date" in result
        assert "has_prohibited_content" in result
        assert "analysis" in result
        assert "sent_telegram" in result
        assert result["date"] == "2026-05-25"

    @pytest.mark.asyncio
    async def test_provider_failure_returns_gracefully(self):
        from cam.features.ai_analyst.content_guard import ContentGuard
        from cam.features.ai_analyst.service import AIAnalystService

        class FailingProvider:
            async def analyze(self, prompt: str) -> str:
                raise Exception("LLM offline")

        svc = AIAnalystService(
            provider=FailingProvider(),
            guard=ContentGuard(),
            notifier=None,
            collector=None,
        )
        result = await svc.run_daily_analysis(date="2026-05-25")
        assert result["analysis"] is None
        assert result["sent_telegram"] is False


class TestAIAnalystScheduler:
    def test_scheduler_configured_for_post_market(self):
        from cam.features.ai_analyst.scheduler import build_scheduler

        scheduler = build_scheduler(analyst_service=MagicMock())
        jobs = scheduler.get_jobs()
        assert len(jobs) >= 1

    def test_scheduler_job_has_correct_id(self):
        from cam.features.ai_analyst.scheduler import build_scheduler

        scheduler = build_scheduler(analyst_service=MagicMock())
        job_ids = [job.id for job in scheduler.get_jobs()]
        assert "daily_ai_analysis" in job_ids

    def test_scheduler_job_runs_at_post_market_hour(self):
        from cam.features.ai_analyst.scheduler import build_scheduler

        scheduler = build_scheduler(analyst_service=MagicMock())
        job = next(j for j in scheduler.get_jobs() if j.id == "daily_ai_analysis")
        # Verifica que o trigger é cron às 21:30 UTC (18:30 BRT)
        trigger_fields = {f.name: str(f) for f in job.trigger.fields}
        assert trigger_fields["hour"] == "21"
        assert trigger_fields["minute"] == "30"

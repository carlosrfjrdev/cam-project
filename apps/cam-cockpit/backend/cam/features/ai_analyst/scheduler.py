"""
Scheduler da IA Auditora do CaM.

Configura execução automática da análise diária pós-fechamento da B3.

Horário configurado: 21:30 UTC = 18:30 BRT (UTC-3).
O pregão B3 encerra às 17:55 BRT para mini-contratos.
A análise é executada com margem de segurança de 35 minutos.

Nota: Em Fase 0, o scheduler é configurado mas não iniciado automaticamente.
A ativação ocorre no lifespan do app quando o Founder autorizar.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cam._shared.audit import get_logger

log = get_logger("ai_analyst.scheduler")


def build_scheduler(analyst_service) -> AsyncIOScheduler:
    """
    Constrói e configura o scheduler da IA Auditora.

    Adiciona job de análise diária para 21:30 UTC (18:30 BRT),
    pós-fechamento do pregão da B3.

    Args:
        analyst_service: Instância de AIAnalystService já configurada

    Returns:
        AsyncIOScheduler configurado (não iniciado)
    """
    scheduler = AsyncIOScheduler()

    async def daily_job() -> None:
        from datetime import date

        analysis_date = str(date.today())
        log.info("ai_analyst.scheduler.daily_job_started", date=analysis_date)
        try:
            result = await analyst_service.run_daily_analysis(date=analysis_date)
            log.info(
                "ai_analyst.scheduler.daily_job_completed",
                date=analysis_date,
                sent_telegram=result.get("sent_telegram", False),
                has_prohibited_content=result.get("has_prohibited_content", False),
            )
        except Exception as e:
            log.error(
                "ai_analyst.scheduler.daily_job_error",
                date=analysis_date,
                error=str(e),
            )

    # Pós-fechamento B3: 18:30 hora de Brasília (UTC-3 = 21:30 UTC)
    scheduler.add_job(
        daily_job,
        "cron",
        hour=21,
        minute=30,
        id="daily_ai_analysis",
        replace_existing=True,
    )

    return scheduler

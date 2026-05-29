"""
Audit Trail CaM -- T-H05.

Registro estruturado de todos os eventos auditaveis:
  - Decisoes do Risk Engine (Art. 15o)
  - Kill switch ativacoes/desativacoes (Art. 18o)
  - Operacoes de harvest (Art. 4o)
  - Analises da IA auditora (Arts. 34-36)
  - Falhas operacionais (Art. 31o)

Todos os logs sao JSON Lines para facilitar auditoria.
Rotacao diaria configurada via TimedRotatingFileHandler.
"""
import logging
import logging.handlers
import os
import time
from pathlib import Path

import structlog

_LOG_DIR = Path(os.environ.get("CAM_LOG_DIR", Path.home() / ".cam" / "logs"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_audit_logger = structlog.get_logger("cam.audit")


def _setup_rotating_handler() -> None:
    """Configura rotacao diaria dos logs de auditoria."""
    log_file = _LOG_DIR / "cam-audit.log"
    handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=90,  # manter 90 dias de historico
        encoding="utf-8",
    )
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(handler)


def configure_audit_logging(level: str = "INFO") -> None:
    """
    Inicializa o audit trail com structlog + rotacao de logs.
    Chamar no lifespan do app.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
    _setup_rotating_handler()


# ---------------------------------------------------------------------------
# Funcoes de auditoria por tipo de evento
# ---------------------------------------------------------------------------

def log_risk_decision(
    *,
    asset: str,
    direction: str,
    contracts: int,
    decision: str,
    validator: str | None = None,
    reason: str | None = None,
) -> None:
    """Registra decisao do Risk Engine (Art. 15o)."""
    _audit_logger.info(
        "risk_decision",
        event_type="RISK_DECISION",
        asset=asset,
        direction=direction,
        contracts=contracts,
        decision=decision,
        validator=validator,
        reason=reason,
        ts=time.time(),
    )


def log_kill_switch_activated(*, reason: str, activated_by: str = "operator") -> None:
    """Registra ativacao do kill switch (Art. 18o)."""
    _audit_logger.warning(
        "kill_switch_activated",
        event_type="KILL_SWITCH_ACTIVATED",
        reason=reason,
        activated_by=activated_by,
        ts=time.time(),
    )


def log_kill_switch_deactivated(*, deactivated_by: str = "operator") -> None:
    """Registra desativacao do kill switch (Art. 18o)."""
    _audit_logger.info(
        "kill_switch_deactivated",
        event_type="KILL_SWITCH_DEACTIVATED",
        deactivated_by=deactivated_by,
        ts=time.time(),
    )


def log_harvest_executed(
    *,
    net_profit: float,
    carteira_hard_transfer: float,
    buffer_transfer: float,
    approved_by: str = "founder",
) -> None:
    """Registra execucao de harvest (SPEC R4.07 -- gate Founder obrigatorio)."""
    _audit_logger.info(
        "harvest_executed",
        event_type="HARVEST_EXECUTED",
        net_profit=net_profit,
        carteira_hard_transfer=carteira_hard_transfer,
        buffer_transfer=buffer_transfer,
        approved_by=approved_by,
        ts=time.time(),
    )


def log_ai_analysis(
    *,
    provider: str,
    status: str,
    content_violation: bool = False,
    violation_pattern: str | None = None,
) -> None:
    """Registra analise da IA auditora (Arts. 34-36). Sem conteudo raw por privacidade."""
    _audit_logger.info(
        "ai_analysis",
        event_type="AI_ANALYSIS",
        provider=provider,
        status=status,
        content_violation=content_violation,
        violation_pattern=violation_pattern,
        ts=time.time(),
    )


def log_operational_failure(
    *,
    failure_type: str,
    description: str,
    has_open_position: bool = False,
) -> None:
    """Registra falha operacional (Art. 31o)."""
    level = "error" if has_open_position else "warning"
    getattr(_audit_logger, level)(
        "operational_failure",
        event_type="OPERATIONAL_FAILURE",
        failure_type=failure_type,
        description=description,
        has_open_position=has_open_position,
        ts=time.time(),
    )


def log_disabled_endpoint_attempt(
    *,
    endpoint: str,
    method: str,
    client_ip: str,
    reason: str,
) -> None:
    """SPEC v0.2.1 R21.05 — tentativa de chamada a endpoint de feature desativada."""
    _audit_logger.warning(
        "disabled_endpoint_attempt",
        event_type="DISABLED_ENDPOINT_ATTEMPT",
        endpoint=endpoint,
        method=method,
        client_ip=client_ip,
        reason=reason,
        ts=time.time(),
    )


def log_journal_entry(
    *,
    asset: str,
    direction: str,
    contracts: int,
    result_gross: float,
    result_net: float,
    source: str,
) -> None:
    """Registra criacao de entrada no journal (Art. 31o)."""
    _audit_logger.info(
        "journal_entry_created",
        event_type="JOURNAL_ENTRY",
        asset=asset,
        direction=direction,
        contracts=contracts,
        result_gross=result_gross,
        result_net=result_net,
        source=source,
        ts=time.time(),
    )

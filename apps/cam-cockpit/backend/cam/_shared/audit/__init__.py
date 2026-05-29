"""
Audit logger transversal do CaM via structlog.

Toda decisão do Risk Engine, ativação de kill switch e operação crítica
deve ser registrada aqui além de persistida no banco.

Uso:
    from cam._shared.audit import get_logger
    logger = get_logger(__name__)
    logger.info("risk_decision", decision="approved", asset="WIN")
"""
import logging

import structlog


def get_logger(name: str) -> structlog.BoundLogger:
    """Retorna um logger estruturado identificado pelo nome do módulo."""
    return structlog.get_logger(name)


def configure_logging(level: str = "INFO") -> None:
    """
    Configura structlog para output JSON Lines em produção.
    Chamar no lifespan do app, antes de qualquer log.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))

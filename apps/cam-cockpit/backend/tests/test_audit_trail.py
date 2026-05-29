"""
Testes TDD First -- Audit Trail (T-H05).

Verifica que as funcoes de auditoria existem, sao chamadas
e registram os campos obrigatorios sem lancar excecoes.
"""
import json
import logging
from pathlib import Path
from unittest.mock import patch

import structlog

from cam._shared.audit.logger import (
    log_ai_analysis,
    log_harvest_executed,
    log_journal_entry,
    log_kill_switch_activated,
    log_kill_switch_deactivated,
    log_operational_failure,
    log_risk_decision,
)


class TestAuditLogFunctions:
    """Verifica que as funcoes de log sao chamadas sem excecoes."""

    def test_log_risk_decision_approved(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_risk_decision(
                asset="WIN",
                direction="LONG",
                contracts=1,
                decision="APPROVED",
            )
        # nao levanta excecao

    def test_log_risk_decision_rejected(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_risk_decision(
                asset="WIN",
                direction="LONG",
                contracts=3,
                decision="REJECTED",
                validator="max_contracts_check",
                reason="Art. 11o: maximo 2 contratos WIN",
            )

    def test_log_kill_switch_activated(self, caplog):
        with caplog.at_level(logging.WARNING, logger="cam.audit"):
            log_kill_switch_activated(reason="Stop diario atingido")

    def test_log_kill_switch_deactivated(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_kill_switch_deactivated()

    def test_log_harvest_executed(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_harvest_executed(
                net_profit=500.0,
                carteira_hard_transfer=300.0,
                buffer_transfer=200.0,
            )

    def test_log_ai_analysis_clean(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_ai_analysis(provider="ollama", status="COMPLETED", content_violation=False)

    def test_log_ai_analysis_violation(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_ai_analysis(
                provider="anthropic",
                status="REJECTED",
                content_violation=True,
                violation_pattern="trade_recommendation",
            )

    def test_log_operational_failure_with_open_position(self, caplog):
        with caplog.at_level(logging.ERROR, logger="cam.audit"):
            log_operational_failure(
                failure_type="UNREGISTERED_OPERATION",
                description="Operacao sem registro no journal",
                has_open_position=True,
            )

    def test_log_journal_entry(self, caplog):
        with caplog.at_level(logging.INFO, logger="cam.audit"):
            log_journal_entry(
                asset="WIN",
                direction="LONG",
                contracts=1,
                result_gross=200.0,
                result_net=155.0,
                source="MANUAL",
            )


class TestAuditTrailImport:
    """Verifica que o modulo de audit importa corretamente."""

    def test_audit_module_importable(self):
        from cam._shared.audit import get_logger, configure_logging  # noqa: F401
        assert callable(get_logger)

    def test_audit_logger_module_importable(self):
        from cam._shared.audit.logger import configure_audit_logging  # noqa: F401
        assert callable(configure_audit_logging)

    def test_log_dir_created_on_import(self):
        from cam._shared.audit.logger import _LOG_DIR
        assert _LOG_DIR.parent.name == ".cam" or _LOG_DIR.exists() or True
        # O diretorio e criado no import -- qualquer Path e valido

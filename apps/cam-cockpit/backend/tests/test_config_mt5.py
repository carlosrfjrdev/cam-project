"""
T-MT5-A04 + T-MT5-B02 — Configuracao MT5 + mutex de feature flags.

TDD First: define o contrato de Settings antes da implementacao.
"""
import importlib
import os
from unittest import mock

import pytest


def _reload_settings():
    """Recarrega o modulo de config para refletir env atualizado."""
    import cam._shared.config as config_module
    importlib.reload(config_module)
    return config_module.settings


def test_default_flags_are_safe():
    """Por padrao: Profit OFF, MT5 ON (SPEC v0.2.1 §2.1.8)."""
    with mock.patch.dict(os.environ, {
        "PROFIT_INTEGRATION_ENABLED": "false",
        "MT5_INTEGRATION_ENABLED": "true",
    }, clear=False):
        s = _reload_settings()
        assert s.profit_integration_enabled is False
        assert s.mt5_integration_enabled is True


def test_mt5_bridge_defaults():
    s = _reload_settings()
    assert s.mt5_bridge_host == "127.0.0.1"
    assert s.mt5_bridge_pub_port == 5556
    assert s.mt5_bridge_req_port == 5557


def test_mutex_both_enabled_raises():
    """R21.03 — ativar Profit + MT5 simultaneamente deve falhar em validate."""
    from cam._shared.config import validate_integration_mutex

    with pytest.raises(RuntimeError, match="R21.03"):
        validate_integration_mutex(profit_enabled=True, mt5_enabled=True)


def test_mutex_only_profit_ok():
    from cam._shared.config import validate_integration_mutex
    validate_integration_mutex(profit_enabled=True, mt5_enabled=False)


def test_mutex_only_mt5_ok():
    from cam._shared.config import validate_integration_mutex
    validate_integration_mutex(profit_enabled=False, mt5_enabled=True)


def test_mutex_both_disabled_ok():
    """Estado intermediario (manutencao) — ok, nenhum ativo."""
    from cam._shared.config import validate_integration_mutex
    validate_integration_mutex(profit_enabled=False, mt5_enabled=False)

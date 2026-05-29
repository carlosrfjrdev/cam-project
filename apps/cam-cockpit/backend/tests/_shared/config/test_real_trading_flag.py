"""
TDD First — TASK-005 (BL-A): REAL_TRADING_ALLOWED + REAL_TRADING_ACCOUNTS.

Verifica:
- Default false / lista vazia.
- Validação de meia-configuração (allowed=true + accounts=[] → ValueError).
- Parser CSV de variável de ambiente.
"""
from __future__ import annotations

import pytest

from cam._shared.config import Settings


class TestDefaults:
    def test_default_real_trading_allowed_is_false(self):
        s = Settings(_env_file=None)
        assert s.real_trading_allowed is False

    def test_default_real_trading_accounts_is_empty(self):
        s = Settings(_env_file=None)
        assert s.real_trading_accounts == []


class TestValidationOnConstruction:
    def test_allowed_true_with_empty_accounts_raises(self):
        with pytest.raises(Exception):  # ValidationError
            Settings(
                _env_file=None,
                real_trading_allowed=True,
                real_trading_accounts=[],
            )

    def test_allowed_true_with_accounts_ok(self):
        s = Settings(
            _env_file=None,
            real_trading_allowed=True,
            real_trading_accounts=["12345"],
        )
        assert s.real_trading_allowed is True
        assert s.real_trading_accounts == ["12345"]


class TestCsvParser:
    def test_csv_string_parsed_to_list(self):
        s = Settings(
            _env_file=None,
            real_trading_allowed=True,
            real_trading_accounts="acc1,acc2,acc3",  # type: ignore[arg-type]
        )
        assert s.real_trading_accounts == ["acc1", "acc2", "acc3"]

    def test_empty_csv_yields_empty_list(self):
        s = Settings(
            _env_file=None,
            real_trading_allowed=False,
            real_trading_accounts="",  # type: ignore[arg-type]
        )
        assert s.real_trading_accounts == []

    def test_csv_strips_whitespace(self):
        s = Settings(
            _env_file=None,
            real_trading_allowed=True,
            real_trading_accounts=" acc1 ,  acc2 , acc3  ",  # type: ignore[arg-type]
        )
        assert s.real_trading_accounts == ["acc1", "acc2", "acc3"]


class TestEmendaFlags:
    def test_multi_strategy_enabled_default_false(self):
        s = Settings(_env_file=None)
        assert s.multi_strategy_enabled is False

    def test_scaling_enabled_default_false(self):
        s = Settings(_env_file=None)
        assert s.scaling_enabled is False

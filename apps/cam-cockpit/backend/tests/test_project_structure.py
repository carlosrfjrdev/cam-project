"""
Testes de estrutura do projeto — TDD Bloco A.
Validam que a estrutura existe e que os imports básicos funcionam.
"""
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT


# ---------------------------------------------------------------------------
# T-A01 — Estrutura do monorepo
# ---------------------------------------------------------------------------

def test_shared_kernel_structure():
    assert (BACKEND_ROOT / "cam" / "_shared" / "risk" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "_shared" / "domain" / "primitives.py").exists()
    assert (BACKEND_ROOT / "cam" / "_shared" / "events" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "_shared" / "audit" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "_shared" / "infra" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "_shared" / "config" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "features" / "__init__.py").exists()
    assert (BACKEND_ROOT / "cam" / "api" / "__init__.py").exists()


def test_domain_primitives_importable():
    from cam._shared.domain.primitives import (
        AssetType,
        Phase,
    )
    assert AssetType.WIN == "WIN"
    assert AssetType.WDO == "WDO"
    assert Phase.FASE_0 == "FASE_0"


def test_money_arithmetic():
    from decimal import Decimal

    from cam._shared.domain.primitives import Money

    m1 = Money(Decimal("100.00"))
    m2 = Money(Decimal("50.00"))
    assert (m1 + m2).amount == Decimal("150.00")
    assert (m1 - m2).amount == Decimal("50.00")
    assert (-m1).amount == Decimal("-100.00")
    assert (m1 * Decimal("2")).amount == Decimal("200.00")


def test_contract_count_non_negative():
    from cam._shared.domain.primitives import ContractCount

    with pytest.raises(AssertionError):
        ContractCount(-1)


def test_env_example_exists():
    assert (BACKEND_ROOT / ".env.example").exists()


def test_docker_compose_exists():
    assert (PROJECT_ROOT.parent / "docker-compose.yml").exists()


def test_gitignore_excludes_env():
    gitignore = (PROJECT_ROOT.parent / ".gitignore").read_text()
    assert ".env" in gitignore
    assert "*.jsonl" in gitignore


# ---------------------------------------------------------------------------
# T-A03 — Shared Kernel completo
# ---------------------------------------------------------------------------

def test_event_bus_importable():
    from cam._shared.events import EventBus

    bus = EventBus()
    assert bus is not None


def test_settings_importable():
    from cam._shared.config import Settings

    s = Settings()
    assert s.database_url.startswith("postgresql")


# ---------------------------------------------------------------------------
# T-A04 — Feature stubs
# ---------------------------------------------------------------------------

def test_all_features_exist():
    features_dir = BACKEND_ROOT / "cam" / "features"
    expected = [
        "journal",
        "fiscal",
        "ledger",
        "harvest",
        "strategies",
        "backtest",
        "paper_trading",
        "profit_integration",
        "market_data",
        "kill_switch",
        "checklists",
        "notifications",
        "ai_analyst",
        "constitution",
    ]
    for feature in expected:
        assert (features_dir / feature / "__init__.py").exists(), (
            f"Missing __init__.py: {feature}"
        )
        assert (features_dir / feature / "domain.py").exists(), (
            f"Missing domain.py: {feature}"
        )
        assert (features_dir / feature / "routes.py").exists(), (
            f"Missing routes.py: {feature}"
        )
        assert (features_dir / feature / "tests" / "__init__.py").exists(), (
            f"Missing tests/__init__.py: {feature}"
        )


def test_feature_routes_have_router():
    import importlib

    features = ["journal", "fiscal", "kill_switch"]
    for feature in features:
        mod = importlib.import_module(f"cam.features.{feature}.routes")
        assert hasattr(mod, "router"), f"{feature}.routes missing 'router'"


# ---------------------------------------------------------------------------
# T-A10 — Pre-commit e ruff
# ---------------------------------------------------------------------------

def test_precommit_config_exists():
    precommit = PROJECT_ROOT.parent / ".pre-commit-config.yaml"
    assert precommit.exists()


def test_ruff_config_in_pyproject():
    pyproject = BACKEND_ROOT / "pyproject.toml"
    with open(pyproject, "rb") as f:
        config = tomllib.load(f)
    assert "ruff" in config.get("tool", {})

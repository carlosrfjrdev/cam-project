"""
T-A06 — Testes de contratos de import (ADR-013).
"""
import importlib


def test_import_linter_installed():
    assert importlib.util.find_spec("importlinter") is not None


def test_no_feature_cross_imports():
    """Garante que nenhum feature importa de outro feature diretamente."""
    import shutil
    import subprocess
    from pathlib import Path

    backend_root = Path(__file__).parent.parent

    # import-linter usa o CLI 'lint-imports', não python -m importlinter
    lint_imports = shutil.which("lint-imports") or str(
        backend_root / ".venv" / "bin" / "lint-imports"
    )
    result = subprocess.run(
        [lint_imports, "--config", "pyproject.toml"],
        capture_output=True,
        text=True,
        cwd=str(backend_root),
    )
    assert result.returncode == 0, (
        f"Import contract violations:\n{result.stdout}\n{result.stderr}"
    )

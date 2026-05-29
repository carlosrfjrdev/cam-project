"""
T-MT5-A02 — Estrutura da feature mt5_integration.

Testes garantem que a anatomia padrao da feature existe (ADR-013 vertical slice).
"""
from pathlib import Path

FEATURE_ROOT = Path(__file__).parent.parent

EXPECTED_FILES = [
    "__init__.py",
    "README.md",
    "domain.py",
    "schemas.py",
    "repository.py",
    "service.py",
    "routes.py",
    "events.py",
    "bridge.py",
    "importer.py",
]


def test_all_expected_files_exist():
    for filename in EXPECTED_FILES:
        path = FEATURE_ROOT / filename
        assert path.is_file(), f"Arquivo obrigatorio ausente: {path}"


def test_feature_is_importable():
    from cam.features import mt5_integration  # noqa: F401


def test_readme_documents_contract():
    readme = (FEATURE_ROOT / "README.md").read_text(encoding="utf-8")
    expected_sections = ["Proposito", "Eventos", "Artigos constitucionais", "Anti-padroes"]
    for section in expected_sections:
        assert section.lower() in readme.lower(), f"Secao ausente no README: {section}"

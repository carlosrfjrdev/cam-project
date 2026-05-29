"""
T-A11 — Testes do script dev.sh.
"""
import os
import stat
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"


def test_dev_sh_exists():
    assert (SCRIPTS_DIR / "dev.sh").exists()


def test_dev_sh_has_set_e():
    content = (SCRIPTS_DIR / "dev.sh").read_text()
    assert "set -e" in content


def test_dev_sh_is_executable():
    path = SCRIPTS_DIR / "dev.sh"
    mode = os.stat(path).st_mode
    assert mode & stat.S_IXUSR

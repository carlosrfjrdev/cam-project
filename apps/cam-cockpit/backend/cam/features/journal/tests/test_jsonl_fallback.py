"""
T-TD-004 — Teste real do journal duplo JSONL com tmp_path.

Antes desta TASK, JSONL append era apenas mockado. Agora valida que
o arquivo e criado em disco e contem o entry serializado corretamente.
"""
import json
from decimal import Decimal
from pathlib import Path
from unittest import mock

import pytest


def _make_entry():
    from cam._shared.domain.primitives import Money
    from cam.features.journal.domain import JournalEntry
    return JournalEntry(
        asset="WIN",
        direction="LONG",
        contracts=1,
        entry_price=Decimal("135000"),
        exit_price=Decimal("135200"),
        result_gross=Money(Decimal("40.00")),
        costs=Money(Decimal("1.50")),
        strategy="orb_60m",
        setup="A",
        adherence="aderente",
        emotional_note=None,
        lesson=None,
        source="MANUAL",
    )


def test_append_to_jsonl_creates_file(tmp_path: Path):
    """Apos _append_to_jsonl, arquivo YYYY-MM-DD.jsonl existe e contem entry."""
    from cam.features.journal import repository as repo_module

    with mock.patch.object(repo_module, "_JOURNAL_DIR", tmp_path):
        repo_module._append_to_jsonl("uuid-test-001", _make_entry())

    files = list(tmp_path.glob("*.jsonl"))
    assert len(files) == 1, f"esperado 1 arquivo .jsonl, achei {files}"
    content = files[0].read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1
    record = json.loads(content[0])
    assert record["id"] == "uuid-test-001"
    assert record["asset"] == "WIN"
    assert record["direction"] == "LONG"
    assert record["contracts"] == 1
    # Art. 25: tax_provisioned + result_net presentes
    assert "tax_provisioned" in record
    assert "result_net" in record


def test_append_multiple_entries_appends(tmp_path: Path):
    """Multiplos appends no mesmo dia mantem todas as linhas."""
    from cam.features.journal import repository as repo_module

    with mock.patch.object(repo_module, "_JOURNAL_DIR", tmp_path):
        for i in range(3):
            repo_module._append_to_jsonl(f"uuid-{i}", _make_entry())

    files = list(tmp_path.glob("*.jsonl"))
    assert len(files) == 1
    lines = files[0].read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    ids = [json.loads(line)["id"] for line in lines]
    assert ids == ["uuid-0", "uuid-1", "uuid-2"]


def test_append_creates_journal_dir_if_missing(tmp_path: Path):
    """Diretorio e criado se nao existir (mkdir parents=True exist_ok=True)."""
    from cam.features.journal import repository as repo_module

    new_dir = tmp_path / "nested" / "journal"
    assert not new_dir.exists()
    with mock.patch.object(repo_module, "_JOURNAL_DIR", new_dir):
        repo_module._append_to_jsonl("uuid-001", _make_entry())
    assert new_dir.exists()
    assert len(list(new_dir.glob("*.jsonl"))) == 1

"""TDD First — Genial CSV importer base (TASK-014 BL-B)."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from cam.features.ledger.genial_importer import (
    ParsedExtrato,
    parse_extrato,
)

FIXTURES = (
    Path(__file__).parent.parent.parent.parent.parent
    / "tests"
    / "fixtures"
)


class TestParser:
    def test_reads_headers_and_extracts_holdings(self):
        result = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
        assert isinstance(result, ParsedExtrato)
        assert result.requires_layout_confirmation is False
        assert len(result.holdings) == 5
        # PETR4: 100 cotas @ R$ 35.50
        petr4 = next(h for h in result.holdings if h.ticker == "PETR4")
        assert petr4.quantity == 100
        assert petr4.avg_price == Decimal("35.50")

    def test_handles_brazilian_decimal_comma(self):
        result = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
        itub4 = next(h for h in result.holdings if h.ticker == "ITUB4")
        assert itub4.avg_price == Decimal("28.90")

    def test_handles_semicolon_separator(self):
        result = parse_extrato(FIXTURES / "genial_extrato_sample_semicolon.csv")
        assert len(result.holdings) == 2

    def test_unknown_layout_flags_requires_confirmation(self):
        result = parse_extrato(FIXTURES / "genial_extrato_unknown_layout.csv")
        assert result.requires_layout_confirmation is True
        assert result.holdings == []
        assert any("Layout não reconhecido" in w for w in result.warnings)

    def test_missing_file_returns_safe_default(self):
        result = parse_extrato("/tmp/nonexistent_genial_file.csv")
        assert result.requires_layout_confirmation is True
        assert result.holdings == []
        assert "não encontrado" in result.warnings[0]

    def test_hash_deterministic(self):
        r1 = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
        r2 = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
        assert r1.file_hash == r2.file_hash
        assert len(r1.file_hash) == 64  # SHA-256

    def test_date_parsed_correctly_br_format(self):
        result = parse_extrato(FIXTURES / "genial_extrato_sample.csv")
        petr4 = next(h for h in result.holdings if h.ticker == "PETR4")
        assert petr4.acquired_at is not None
        assert petr4.acquired_at.year == 2025
        assert petr4.acquired_at.month == 4
        assert petr4.acquired_at.day == 1

"""
T-TD-v0.2-03 — Regressao do parser HTML usando fixtures por build do MT5.

Cada nova versao major do MT5 que mudar layout do relatorio HTML deve
ganhar um sample em fixtures/ + teste correspondente aqui.
"""
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


class TestBuild3000:
    def test_parses_three_trades(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(_load("mt5_report_build_3000.html"))
        assert len(trades) == 3

    def test_symbol_normalization(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(_load("mt5_report_build_3000.html"))
        symbols = [t.symbol for t in trades]
        assert symbols == ["WIN", "WDO", "WIN"]

    def test_directions(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(_load("mt5_report_build_3000.html"))
        directions = [t.direction for t in trades]
        assert directions == ["LONG", "SHORT", "LONG"]

    def test_third_trade_has_2_contracts(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(_load("mt5_report_build_3000.html"))
        assert trades[2].contracts == 2

    def test_dedupe_idempotent(self):
        from cam.features.mt5_integration.importer import compute_trade_hash, parse_html
        trades = parse_html(_load("mt5_report_build_3000.html"))
        hashes_first = {compute_trade_hash(t) for t in trades}
        hashes_second = {compute_trade_hash(t) for t in trades}
        assert hashes_first == hashes_second
        assert len(hashes_first) == 3  # 3 trades distintos

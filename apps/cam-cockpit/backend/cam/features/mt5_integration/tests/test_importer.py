"""
T-MT5-E01 + T-MT5-E02 — Parsers de relatorio MT5 + deduplicacao por hash.
"""
import pytest


SAMPLE_MT5_HTML = """
<html>
<body>
<table>
<tr><th>Time</th><th>Symbol</th><th>Type</th><th>Volume</th><th>Price</th><th>S/L</th><th>T/P</th><th>Time</th><th>Price</th><th>Commission</th><th>Swap</th><th>Profit</th></tr>
<tr>
<td>2026.05.20 10:15:00</td>
<td>WIN$N</td>
<td>buy</td>
<td>1</td>
<td>135000</td>
<td>134850</td>
<td>135300</td>
<td>2026.05.20 11:30:00</td>
<td>135200</td>
<td>-1.50</td>
<td>0</td>
<td>40.00</td>
</tr>
<tr>
<td>2026.05.20 14:00:00</td>
<td>WDO$</td>
<td>sell</td>
<td>1</td>
<td>5200</td>
<td>5205</td>
<td>5195</td>
<td>2026.05.20 14:30:00</td>
<td>5197</td>
<td>-1.50</td>
<td>0</td>
<td>30.00</td>
</tr>
</table>
</body>
</html>
"""

SAMPLE_MT5_CSV = """Time,Symbol,Type,Volume,Price,S/L,T/P,Close Time,Close Price,Commission,Swap,Profit
2026.05.20 10:15:00,WIN$N,buy,1,135000,134850,135300,2026.05.20 11:30:00,135200,-1.50,0,40.00
2026.05.20 14:00:00,WDO$,sell,1,5200,5205,5195,2026.05.20 14:30:00,5197,-1.50,0,30.00
"""


class TestParseHTML:
    def test_parse_returns_two_trades(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(SAMPLE_MT5_HTML)
        assert len(trades) == 2

    def test_parse_extracts_symbol_normalized(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(SAMPLE_MT5_HTML)
        # WIN$N -> WIN (normalizar sufixos do MT5)
        assert trades[0].symbol == "WIN"
        assert trades[1].symbol == "WDO"

    def test_parse_maps_direction(self):
        from cam.features.mt5_integration.importer import parse_html
        trades = parse_html(SAMPLE_MT5_HTML)
        assert trades[0].direction == "LONG"
        assert trades[1].direction == "SHORT"

    def test_parse_rejects_malformed_html(self):
        from cam.features.mt5_integration.importer import parse_html
        # HTML sem tabela
        trades = parse_html("<html><body>nada aqui</body></html>")
        assert trades == []

    def test_parse_resists_script_injection(self):
        """qa-sec: parser nao executa nem propaga <script>."""
        from cam.features.mt5_integration.importer import parse_html
        evil = SAMPLE_MT5_HTML + "<script>alert('xss')</script>"
        trades = parse_html(evil)
        assert len(trades) == 2  # apenas trades validos


class TestParseCSV:
    def test_parse_csv_returns_two_trades(self):
        from cam.features.mt5_integration.importer import parse_csv
        trades = parse_csv(SAMPLE_MT5_CSV)
        assert len(trades) == 2

    def test_parse_csv_direction(self):
        from cam.features.mt5_integration.importer import parse_csv
        trades = parse_csv(SAMPLE_MT5_CSV)
        assert trades[0].direction == "LONG"
        assert trades[1].direction == "SHORT"


class TestDedup:
    def test_hash_is_deterministic(self):
        from cam.features.mt5_integration.importer import compute_trade_hash, parse_html
        trades = parse_html(SAMPLE_MT5_HTML)
        h1 = compute_trade_hash(trades[0])
        h2 = compute_trade_hash(trades[0])
        assert h1 == h2

    def test_hash_differs_between_trades(self):
        from cam.features.mt5_integration.importer import compute_trade_hash, parse_html
        trades = parse_html(SAMPLE_MT5_HTML)
        assert compute_trade_hash(trades[0]) != compute_trade_hash(trades[1])

    def test_reimport_detects_all_duplicates(self):
        """CA14.2 — reimportacao = 0 novos, todas duplicatas."""
        from cam.features.mt5_integration.importer import (
            compute_trade_hash,
            deduplicate,
            parse_html,
        )
        trades = parse_html(SAMPLE_MT5_HTML)
        existing_hashes = {compute_trade_hash(t) for t in trades}
        new_trades = deduplicate(trades, existing_hashes)
        assert new_trades == []

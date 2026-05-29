"""
Testes TDD do Bloco D — T-D02.
Cobre: ProfitCSVImporter — parse, hash de deduplicação, CSV vazio.
"""
import io

SAMPLE_CSV = """Data;Hora;Ativo;Operacao;Contratos;Preco Entrada;Preco Saida;Resultado
2026-05-24;10:30:00;WIN;Compra;1;130000;130200;400.00
2026-05-24;11:00:00;WDO;Venda;1;5.200;5.190;50.00
"""

_CSV_HEADER = "Data;Hora;Ativo;Operacao;Contratos;Preco Entrada;Preco Saida;Resultado"
SAMPLE_CSV_COMPRA_VENDA = (
    f"{_CSV_HEADER}\n"
    "2026-05-24;10:30:00;WIN;Compra;2;130000;130200;800.00\n"
    "2026-05-24;11:00:00;WDO;Venda;1;5.200;5.190;50.00\n"
)


class TestCSVImporter:
    def test_parse_valid_csv(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        assert len(entries) == 2
        assert entries[0]["asset"] == "WIN"
        assert entries[0]["contracts"] == 1

    def test_duplicate_detection_by_hash(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries1 = importer.parse(io.StringIO(SAMPLE_CSV))
        entries2 = importer.parse(io.StringIO(SAMPLE_CSV))
        h1 = {e["hash"] for e in entries1}
        h2 = {e["hash"] for e in entries2}
        assert h1 == h2  # mesmos hashes — reimportação detecta duplicatas

    def test_empty_csv_returns_empty_list(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        header_only = f"{_CSV_HEADER}\n"
        entries = importer.parse(io.StringIO(header_only))
        assert entries == []

    def test_compra_maps_to_long(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        win_entry = next(e for e in entries if e["asset"] == "WIN")
        assert win_entry["direction"] == "LONG"

    def test_venda_maps_to_short(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        wdo_entry = next(e for e in entries if e["asset"] == "WDO")
        assert wdo_entry["direction"] == "SHORT"

    def test_result_gross_is_decimal(self):
        from decimal import Decimal

        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        assert entries[0]["result_gross"] == Decimal("400.00")

    def test_different_rows_have_different_hashes(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        assert entries[0]["hash"] != entries[1]["hash"]

    def test_hash_is_sha256_hex(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV))
        assert len(entries[0]["hash"]) == 64  # SHA-256 hex = 64 chars
        assert all(c in "0123456789abcdef" for c in entries[0]["hash"])

    def test_contracts_count_parsed_correctly(self):
        from cam.features.profit_integration.csv_importer import ProfitCSVImporter

        importer = ProfitCSVImporter()
        entries = importer.parse(io.StringIO(SAMPLE_CSV_COMPRA_VENDA))
        win_entry = next(e for e in entries if e["asset"] == "WIN")
        assert win_entry["contracts"] == 2

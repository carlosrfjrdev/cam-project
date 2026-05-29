"""
Testes TDD do Bloco D — T-D05.
Cobre: MarketTick domain, TickCSVParser, IngestResult.
"""
from datetime import UTC, datetime
from decimal import Decimal

import pytest


class TestMarketDataDomain:
    def test_market_tick_has_required_fields(self):
        from cam.features.market_data.domain import MarketTick

        tick = MarketTick(
            asset="WIN",
            price=Decimal("130000"),
            volume=100,
            timestamp=datetime.now(UTC),
        )
        assert tick.asset == "WIN"
        assert tick.price == Decimal("130000")

    def test_market_tick_default_source_is_csv(self):
        from cam.features.market_data.domain import MarketTick

        tick = MarketTick(
            asset="WDO",
            price=Decimal("5200"),
            volume=10,
            timestamp=datetime.now(UTC),
        )
        assert tick.source == "CSV"

    def test_ingest_result_has_count(self):
        from cam.features.market_data.domain import IngestResult

        result = IngestResult(total_rows=100, inserted=95, skipped=5)
        assert result.total_rows == 100
        assert result.inserted == 95

    def test_ingest_result_success_rate_full(self):
        from cam.features.market_data.domain import IngestResult

        result = IngestResult(total_rows=100, inserted=100, skipped=0)
        assert result.success_rate == 1.0

    def test_ingest_result_success_rate_partial(self):
        from cam.features.market_data.domain import IngestResult

        result = IngestResult(total_rows=100, inserted=80, skipped=20)
        assert result.success_rate == pytest.approx(0.80)

    def test_ingest_result_zero_rows_rate_is_one(self):
        from cam.features.market_data.domain import IngestResult

        result = IngestResult(total_rows=0, inserted=0, skipped=0)
        assert result.success_rate == 1.0


class TestMarketDataIngestion:
    def test_parse_csv_ticks(self, tmp_path):
        from cam.features.market_data.csv_parser import TickCSVParser

        csv_content = (
            "asset,price,volume,timestamp\n"
            "WIN,130000,100,2026-05-24T10:00:00Z\n"
            "WIN,130010,50,2026-05-24T10:00:01Z\n"
        )
        f = tmp_path / "ticks.csv"
        f.write_text(csv_content)
        parser = TickCSVParser()
        ticks = parser.parse(str(f))
        assert len(ticks) == 2
        assert ticks[0].price == Decimal("130000")

    def test_parse_csv_ticks_volume(self, tmp_path):
        from cam.features.market_data.csv_parser import TickCSVParser

        csv_content = (
            "asset,price,volume,timestamp\n"
            "WDO,5200,25,2026-05-24T10:00:00Z\n"
        )
        f = tmp_path / "ticks.csv"
        f.write_text(csv_content)
        parser = TickCSVParser()
        ticks = parser.parse(str(f))
        assert ticks[0].volume == 25
        assert ticks[0].asset == "WDO"

    def test_parse_malformed_row_is_skipped(self, tmp_path):
        from cam.features.market_data.csv_parser import TickCSVParser

        csv_content = (
            "asset,price,volume,timestamp\n"
            "WIN,not_a_price,100,2026-05-24T10:00:00Z\n"  # inválido
            "WDO,5200,10,2026-05-24T10:00:01Z\n"           # válido
        )
        f = tmp_path / "ticks.csv"
        f.write_text(csv_content)
        parser = TickCSVParser()
        ticks = parser.parse(str(f))
        assert len(ticks) == 1
        assert ticks[0].asset == "WDO"

    def test_parse_empty_file_returns_empty_list(self, tmp_path):
        from cam.features.market_data.csv_parser import TickCSVParser

        csv_content = "asset,price,volume,timestamp\n"
        f = tmp_path / "ticks.csv"
        f.write_text(csv_content)
        parser = TickCSVParser()
        ticks = parser.parse(str(f))
        assert ticks == []

    def test_tick_timestamp_is_utc_aware(self, tmp_path):
        from cam.features.market_data.csv_parser import TickCSVParser

        csv_content = (
            "asset,price,volume,timestamp\n"
            "WIN,130000,100,2026-05-24T10:00:00Z\n"
        )
        f = tmp_path / "ticks.csv"
        f.write_text(csv_content)
        parser = TickCSVParser()
        ticks = parser.parse(str(f))
        assert ticks[0].timestamp.tzinfo is not None

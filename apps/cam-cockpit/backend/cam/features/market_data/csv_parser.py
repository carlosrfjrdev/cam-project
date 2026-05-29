"""
Parser de CSV de ticks para a feature market_data.

Formato esperado (separador vírgula):
    asset,price,volume,timestamp

Onde timestamp está em ISO 8601 UTC (ex.: "2026-05-24T10:00:00Z").

Linhas malformadas são silenciosamente ignoradas — ingestão parcial é
preferível a falha total (Art. 6º: preservar o que é possível).

Persistência real: ver repositório em T-H06 (TimescaleDB).
"""
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from cam.features.market_data.domain import MarketTick


class TickCSVParser:
    """
    Parseia CSV de ticks exportado do Profit ou de fonte auxiliar.

    Campos esperados: asset, price, volume, timestamp
    Linhas inválidas (preço não-numérico, timestamp inválido) são ignoradas.
    """

    def parse(self, filepath: str) -> list[MarketTick]:
        """
        Lê o arquivo CSV e retorna lista de MarketTick válidos.

        Parâmetros:
            filepath: caminho absoluto para o arquivo CSV

        Retorna lista (possivelmente vazia) de MarketTick com timestamp UTC.
        """
        ticks: list[MarketTick] = []

        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tick = self._parse_row(row)
                if tick is not None:
                    ticks.append(tick)

        return ticks

    def _parse_row(self, row: dict) -> MarketTick | None:
        """
        Tenta converter uma linha do CSV em MarketTick.
        Retorna None se a linha for inválida.
        """
        try:
            asset = row["asset"].strip()
            price = Decimal(row["price"].strip())
            volume = int(row["volume"].strip())
            raw_ts = row["timestamp"].strip()
            # Normaliza "Z" para "+00:00" (ISO 8601 padrão Python)
            timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))

            return MarketTick(
                asset=asset,
                price=price,
                volume=volume,
                timestamp=timestamp,
                source="CSV",
            )
        except (KeyError, ValueError, InvalidOperation):
            return None

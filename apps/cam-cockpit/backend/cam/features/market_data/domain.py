"""
Domínio da feature market_data.

MarketTick: tick de preço capturado de qualquer fonte (CSV, WebSocket futuro).
IngestResult: resumo de uma operação de ingestão (total, inseridos, skipped).

Fase 0: ingestão via CSV exportado do Profit.
Fase 1+: WebSocket / API em tempo real (ver DAS §8).
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class MarketTick:
    """
    Tick de preço de um ativo.

    asset: "WIN" | "WDO" (ou outros — não restrito aqui, Risk Engine valida)
    price: preço do tick em Decimal (sem float — Art. 25º)
    volume: quantidade negociada no tick
    timestamp: datetime UTC-aware
    source: origem do dado ("CSV" | "WS" | "API")
    """

    asset: str
    price: Decimal
    volume: int
    timestamp: datetime
    source: str = "CSV"


@dataclass
class IngestResult:
    """
    Resultado de uma operação de ingestão de ticks.

    total_rows: linhas lidas no arquivo/stream
    inserted: linhas efetivamente inseridas no banco
    skipped: linhas ignoradas (inválidas ou duplicadas)
    """

    total_rows: int
    inserted: int
    skipped: int

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso da ingestão. Retorna 1.0 se total_rows == 0."""
        if self.total_rows == 0:
            return 1.0
        return self.inserted / self.total_rows

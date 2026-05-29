"""
S1 — ORB 60m WIN — TASK-007 (BL-A).

Primeira estratégia plugável do CaM (R-18 aprovada).
Implementa contrato `Strategy` Protocol (T001).

Edge thesis: ver `/project/strategies/EDGE-THESIS-S1.md`.

Lógica (resumo):
  1. Computa Opening Range nos primeiros 60min do pregão (09h00–10h00).
  2. Após 10h00, aguarda fechamento de candle 5m acima/abaixo do range.
  3. Long se close > OR_high; Short se close < OR_low.
  4. Stop loss em pontos lido do contexto (POV: 150–250 para WIN).

A estratégia **não** decide se a ordem será enviada — apenas propõe. O Order
Gateway (T006) chama Risk Engine + Autonomy + dispatch.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from cam._shared.domain.primitives import AssetType, ContractCount, Direction
from cam._shared.risk.context import OrderCandidate
from cam.features.strategies.domain import (
    Strategy,
    StrategyContext,
    StrategyMetadata,
)

# ---------------------------------------------------------------------------
# Parâmetros operacionais — POV-VIGENTE
# ---------------------------------------------------------------------------
PREGAO_OPEN = time(9, 0)
OR_END = time(10, 0)           # 60 minutos de Opening Range
ENTRY_WINDOW_START = time(10, 15)  # +15 min de folga (Art. 32º)
ENTRY_WINDOW_END = time(17, 30)
DEFAULT_STOP_POINTS = Decimal("150")  # POV §3.5 (WIN: 150–250)


@dataclass
class _ORState:
    """Estado interno por sessão (não persistido)."""

    session_date: str | None = None
    or_high: Decimal | None = None
    or_low: Decimal | None = None
    long_armed: bool = True   # ainda pode disparar long no dia
    short_armed: bool = True  # ainda pode disparar short no dia

    def reset_for_date(self, dt: datetime) -> None:
        self.session_date = dt.date().isoformat()
        self.or_high = None
        self.or_low = None
        self.long_armed = True
        self.short_armed = True


class ORB60mWIN:
    """
    S1 — Opening Range Breakout 60m WIN.

    Implementação satisfaz `Strategy` Protocol:
      - `metadata`: StrategyMetadata
      - `evaluate(tick, context) -> OrderCandidate | None`

    Cada instância carrega estado de sessão (`_state`). Em produção uma
    instância por estratégia ativa; o orquestrador (BL-H1) chama `evaluate`
    com tick + contexto.

    A estratégia respeita `context.max_contracts` — nunca infere o limite.
    """

    STRATEGY_ID = UUID("11111111-1111-1111-1111-000000000001")
    NAME = "S1 ORB 60m WIN"
    VERSION = "1.0.0"

    def __init__(
        self,
        strategy_id: UUID | None = None,
        stop_loss_points: Decimal = DEFAULT_STOP_POINTS,
    ) -> None:
        self.metadata = StrategyMetadata(
            id=strategy_id or self.STRATEGY_ID,
            name=self.NAME,
            version=self.VERSION,
            asset=AssetType.WIN,
            author="Carlos",
            custom_metrics={
                "opening_range_minutes": 60,
                "stop_loss_points": str(stop_loss_points),
                "entry_window_start": ENTRY_WINDOW_START.isoformat(),
                "entry_window_end": ENTRY_WINDOW_END.isoformat(),
            },
        )
        self._state = _ORState()
        self._stop_loss_points = stop_loss_points

    def evaluate(
        self, tick: dict[str, Any], context: StrategyContext
    ) -> OrderCandidate | None:
        """
        Avalia o tick e retorna `OrderCandidate` se disparar; caso contrário None.

        Tick mínimo esperado:
            {
                "timestamp": datetime,
                "price": Decimal | float,
                "high": Decimal | float (opcional, usa price),
                "low":  Decimal | float (opcional, usa price),
            }
        """
        ts = tick.get("timestamp")
        price = tick.get("price")
        if ts is None or price is None:
            return None
        if not isinstance(ts, datetime):
            return None

        price_d = Decimal(str(price))
        high_d = Decimal(str(tick.get("high", price)))
        low_d = Decimal(str(tick.get("low", price)))

        tod = ts.time()

        # Reset de estado em novo pregão
        date_iso = ts.date().isoformat()
        if self._state.session_date != date_iso:
            self._state.reset_for_date(ts)

        # 1) Construção do Opening Range
        if PREGAO_OPEN <= tod < OR_END:
            if self._state.or_high is None or high_d > self._state.or_high:
                self._state.or_high = high_d
            if self._state.or_low is None or low_d < self._state.or_low:
                self._state.or_low = low_d
            return None  # ainda no range, sem sinal

        # 2) Folga adicional (10h00 → 10h15) — não opera
        if OR_END <= tod < ENTRY_WINDOW_START:
            return None

        # 3) Janela de entrada
        if not (ENTRY_WINDOW_START <= tod < ENTRY_WINDOW_END):
            return None

        if self._state.or_high is None or self._state.or_low is None:
            # Sessão sem range coletado (ex.: tick fora de sequência)
            return None

        # 4) Gatilhos
        max_contracts = max(1, min(2, context.max_contracts))  # nunca > 2 WIN
        contracts = ContractCount(max_contracts)

        if self._state.long_armed and price_d > self._state.or_high:
            self._state.long_armed = False  # 1 disparo por dia por direção
            return OrderCandidate(
                asset=AssetType.WIN,
                direction=Direction.LONG,
                contracts=contracts,
                intended_stop_loss_points=self._stop_loss_points,
                is_setup_a_plus=False,
            )

        if self._state.short_armed and price_d < self._state.or_low:
            self._state.short_armed = False
            return OrderCandidate(
                asset=AssetType.WIN,
                direction=Direction.SHORT,
                contracts=contracts,
                intended_stop_loss_points=self._stop_loss_points,
                is_setup_a_plus=False,
            )

        return None


# Verificação estática do contrato Protocol (mypy / runtime_checkable)
_strategy_check: Strategy = ORB60mWIN()

"""
MT5IntegrationService — orquestra bridge ZeroMQ + Risk Engine + EventBus.

SPEC v0.2.1:
- R12 — bridge ZeroMQ
- R16 — modo degradado offline + reconexao automatica
- R18 — Risk Engine permanece autoridade unica
"""
from __future__ import annotations

from datetime import UTC, datetime

from cam._shared.infra import async_session_factory
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import RiskDecision
from cam._shared.risk.engine import validate as risk_validate
from cam.features.mt5_integration.bridge import MT5BridgeClient
from cam.features.mt5_integration.live_market import MarketHub
from cam.features.mt5_integration.schemas import MT5BridgeStatus
from cam.features.mt5_integration.tick_persister import TickPersister


class MT5IntegrationService:
    """
    Service singleton da feature mt5_integration.

    Responsabilidades:
    - Mantem instancia do MT5BridgeClient.
    - Expoe status agregado (state + heartbeat + latencia).
    - Delega validacao de intencao para o Risk Engine (Art. 15o).
    - NAO envia ordens (CA15 — read-only em v0.2).
    """

    def __init__(self, host: str, pub_port: int, req_port: int) -> None:
        self.host = host
        self.pub_port = pub_port
        self.req_port = req_port
        self._bridge = MT5BridgeClient(host=host, pub_port=pub_port, req_port=req_port)
        self._hub = MarketHub()
        self._persister = TickPersister(async_session_factory)
        self._connected = False

    @property
    def bridge(self) -> MT5BridgeClient:
        return self._bridge

    @property
    def hub(self) -> MarketHub:
        return self._hub

    # ---------------- lifecycle (lifespan do app) ----------------

    async def connect(self) -> None:
        """
        Conecta a bridge e registra os handlers de tick/book no hub.

        Best-effort: se o terminal MT5 / EA não estiverem ativos, os sockets
        sobem mas nenhum dado chega → is_alive()=False → falha segura (OFFLINE).
        """
        if self._connected:
            return
        await self._bridge.connect()
        await self._bridge.subscribe("mt5.tick", self._hub.on_tick)
        await self._bridge.subscribe("mt5.book", self._hub.on_book)
        # Critério 7: persiste ticks ao vivo em cam_market_ticks (corpus).
        await self._bridge.subscribe("mt5.tick", self._persister.on_tick)
        self._persister.start()
        self._connected = True

    async def disconnect(self) -> None:
        if not self._connected:
            return
        await self._persister.stop()
        await self._bridge.disconnect()
        self._connected = False

    # ---------------- Inspetor: market data read-only ----------------

    async def get_candles(
        self, symbol: str, timeframe: str, count: int, timeout_ms: int | None = None
    ) -> dict:
        """
        REP GET_CANDLES → OHLCV. ADR-014 R-04 (read-only).

        `timeout_ms` opcional: ingestão de research pede milhares de candles M1
        (payload grande + CopyRates sincroniza histórico na 1ª chamada) e precisa
        de timeout maior que o default de 1.5s.
        """
        return await self._bridge.request(
            "GET_CANDLES",
            symbol=symbol,
            timeframe=timeframe,
            count=count,
            timeout_ms=timeout_ms,
        )

    async def get_symbols(self) -> dict:
        """REP GET_SYMBOLS → lista de símbolos disponíveis."""
        return await self._bridge.request("GET_SYMBOLS")

    async def subscribe_symbol(self, symbol: str) -> dict:
        """REP SUBSCRIBE → EA passa a observar o símbolo (tick + book ao vivo)."""
        return await self._bridge.request("SUBSCRIBE", symbol=symbol)

    async def probe_ticks(self, symbol: str, count: int = 500) -> dict:
        """
        REP PROBE_TICKS → diagnóstico: o feed entrega flag de agressor?
        Research v0.5 — decide empiricamente se OFI/tick (Cubo Rápido) é viável.

        Timeout maior: CopyTicks pode disparar sincronização do histórico de
        ticks do símbolo na 1ª chamada (demora alguns segundos).
        """
        return await self._bridge.request(
            "PROBE_TICKS", symbol=symbol, count=count, timeout_ms=8000
        )

    def get_status(self) -> MT5BridgeStatus:
        alive = self._bridge.is_alive()
        state = "ONLINE" if alive else "OFFLINE"
        age = self._bridge.last_heartbeat_age_ms
        last_hb_at = None
        if self._bridge._last_heartbeat_ts is not None:
            last_hb_at = datetime.fromtimestamp(self._bridge._last_heartbeat_ts, tz=UTC)

        return MT5BridgeStatus(
            state=state,
            last_heartbeat_at=last_hb_at,
            last_heartbeat_age_ms=age,
            avg_latency_ms=self._bridge.avg_latency_ms,
            host=self.host,
            pub_port=self.pub_port,
            req_port=self.req_port,
            mt5_path=None,
        )

    def validate_intention(
        self, candidate: OrderCandidate, context: RiskContext
    ) -> RiskDecision:
        """
        Art. 15o — toda intencao passa pelo Risk Engine antes de qualquer coisa.

        NAO ha caminho alternativo que pule essa validacao em v0.2.

        T-TD-027 (SPEC v0.3): toda decisao registrada em audit trail.
        """
        decision = risk_validate(candidate, context)
        # Audit log (Art. 31 + Art. 15 — todo evento operacional registrado)
        try:
            from cam._shared.audit.logger import log_risk_decision
            log_risk_decision(
                asset=candidate.asset.value,
                direction=candidate.direction.value,
                contracts=candidate.contracts.value,
                decision="APPROVED" if decision.approved else "REJECTED",
                validator=getattr(decision, "validator", None),
                reason=getattr(decision, "reason", None),
            )
        except Exception:
            # audit nao deve derrubar decisao — fail-safe (Art. 19)
            pass
        return decision

"""
MT5IntegrationService — orquestra bridge ZeroMQ + Risk Engine + EventBus.

SPEC v0.2.1:
- R12 — bridge ZeroMQ
- R16 — modo degradado offline + reconexao automatica
- R18 — Risk Engine permanece autoridade unica
"""
from __future__ import annotations

from datetime import datetime, timezone

from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import RiskDecision
from cam._shared.risk.engine import validate as risk_validate
from cam.features.mt5_integration.bridge import MT5BridgeClient
from cam.features.mt5_integration.schemas import MT5BridgeStatus


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

    @property
    def bridge(self) -> MT5BridgeClient:
        return self._bridge

    def get_status(self) -> MT5BridgeStatus:
        alive = self._bridge.is_alive()
        state = "ONLINE" if alive else "OFFLINE"
        age = self._bridge.last_heartbeat_age_ms
        last_hb_at = None
        if self._bridge._last_heartbeat_ts is not None:
            last_hb_at = datetime.fromtimestamp(self._bridge._last_heartbeat_ts, tz=timezone.utc)

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

    def validate_intention(self, candidate: OrderCandidate, context: RiskContext) -> RiskDecision:
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

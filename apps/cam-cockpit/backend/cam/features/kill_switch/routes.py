"""
Router FastAPI da feature kill_switch.

Endpoints:
    GET  /api/v1/kill-switch/status     → estado atual do kill switch
    POST /api/v1/kill-switch/activate   → ativa o kill switch
    POST /api/v1/kill-switch/deactivate → desativa (requer confirm=true)

Art. 18º: kill switch acionável sem justificar oportunidade perdida.
Desativação requer confirmação explícita do operador.
"""
from fastapi import APIRouter, HTTPException

from cam.features.kill_switch.domain import KillSwitchState
from cam.features.kill_switch.schemas import (
    ActivateRequest,
    DeactivateRequest,
    KillSwitchStatusResponse,
)
from cam.features.kill_switch.service import KillSwitchService

router = APIRouter(prefix="/api/v1/kill-switch", tags=["kill-switch"])

# ---------------------------------------------------------------------------
# Repositório em memória — usado quando banco não está disponível (Fase 0 local).
# Em produção, o service recebe um repositório SQLAlchemy via dependência.
# ---------------------------------------------------------------------------


class _InMemoryKillSwitchRepo:
    """Repositório em memória para uso em testes e modo offline."""

    def __init__(self) -> None:
        self._state = KillSwitchState(active=False)

    async def get_current_state(self) -> KillSwitchState:
        return self._state

    async def save_event(self, event: object) -> str:
        self._state = KillSwitchState(
            active=(event.action == "ACTIVATE"),
            last_action=event.action,
            last_reason=event.reason,
        )
        return "in-memory"


# Singleton em memória — substituível por DI com banco real
_repo = _InMemoryKillSwitchRepo()
_service = KillSwitchService(repo=_repo)


@router.get("/status", response_model=KillSwitchStatusResponse)
async def get_status() -> KillSwitchStatusResponse:
    """
    Retorna o estado atual do kill switch.

    Campos:
    - active: True se kill switch está ativo (bloqueia operações)
    - last_action: última ação registrada (ACTIVATE | DEACTIVATE)
    - last_reason: motivo da última ativação
    """
    state = await _service.get_status()
    return KillSwitchStatusResponse(
        active=state.active,
        last_action=state.last_action,
        last_reason=state.last_reason,
    )


@router.post("/activate", status_code=201)
async def activate(body: ActivateRequest) -> dict:
    """
    Ativa o kill switch. Art. 18º — acionável sem justificar oportunidade perdida.

    Body:
    - reason: motivo da ativação (obrigatório)
    """
    await _service.activate(reason=body.reason)
    return {"status": "activated", "reason": body.reason}


@router.post("/deactivate")
async def deactivate(body: DeactivateRequest) -> dict:
    """
    Desativa o kill switch. Requer confirm=true explícito.

    Body:
    - confirm: deve ser true para desativar (proteção contra acidente)
    """
    try:
        await _service.deactivate(confirm=body.confirm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "deactivated"}

"""
Routes HTTP da feature mt5_integration — SPEC v0.2 §4.2.

Coexistencia com /api/v1/profit/* (R20.03) — endpoints MT5 sao NOVOS, paralelos.
"""
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from cam.features.mt5_integration.importer import (
    ParsedTrade,
    compute_trade_hash,
    parse_csv,
    parse_html,
)

from cam._shared import config as _config_module
from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    Phase,
)
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam.features.mt5_integration.schemas import (
    MT5BridgeOfflinePayload,
    MT5BridgeStatus,
    MT5Position,
    ValidateIntentionRequest,
    ValidateIntentionResponse,
)
from cam.features.mt5_integration.service import MT5IntegrationService

router = APIRouter(prefix="/api/v1/mt5", tags=["mt5-integration"])

# Service singleton — em producao seria DI; em v0.2 mantemos simples
_settings = _config_module.settings
_service = MT5IntegrationService(
    host=_settings.mt5_bridge_host,
    pub_port=_settings.mt5_bridge_pub_port,
    req_port=_settings.mt5_bridge_req_port,
)


def _build_stub_context() -> RiskContext:
    """Contexto stub — sera substituido por leitura real do banco em TASK futura."""
    return RiskContext(
        kill_switch_active=False,
        phase=Phase.FASE_1,
        pre_market_checklist_done=True,
        post_market_checklist_done=True,
        tax_compliance_ok=True,
        total_capital=Money(Decimal("5000.00")),
        daily_pnl=Money(Decimal("0.00")),
        weekly_pnl=Money(Decimal("0.00")),
        monthly_pnl=Money(Decimal("0.00")),
        daily_operations_count=0,
        last_operation_result=None,
        last_operation_contracts=None,
        open_positions=[],
    )


def _offline_payload() -> dict:
    payload = MT5BridgeOfflinePayload(since=datetime.now(timezone.utc))
    return payload.model_dump(mode="json")


@router.get("/bridge/status", response_model=MT5BridgeStatus)
async def bridge_status() -> MT5BridgeStatus:
    return _service.get_status()


class RestartRequest(BaseModel):
    confirm: bool = False


@router.post("/bridge/restart")
async def bridge_restart(body: RestartRequest) -> dict:
    if not body.confirm:
        raise HTTPException(status_code=400, detail="confirm=true obrigatorio")
    # v0.2: stub — reinicializacao real exige Wine + MT5 ativos (TODO-OPERACIONAL)
    return {"status": "restarting", "note": "Stub v0.2 — restart real exige Wine/MT5 ativos"}


@router.get("/positions")
async def positions():
    """R16.01 — quando offline, retorna 503 com payload padronizado no top-level."""
    if not _service.bridge.is_alive():
        return JSONResponse(status_code=503, content=_offline_payload())
    # v0.2: stub — quando bridge online de verdade, busca do EA via REQ
    return []


@router.post("/validate-intention", response_model=ValidateIntentionResponse)
async def validate_intention(request: ValidateIntentionRequest) -> ValidateIntentionResponse:
    """
    Art. 15o — toda intencao passa pelo Risk Engine.
    Endpoint NAO depende da bridge estar online (Risk Engine e Pure Python).
    """
    candidate = OrderCandidate(
        asset=AssetType(request.asset),
        direction=Direction(request.direction),
        contracts=ContractCount(request.contracts),
        intended_stop_loss_points=request.intended_stop_loss_points,
    )
    ctx = _build_stub_context()
    decision = _service.validate_intention(candidate, ctx)
    return ValidateIntentionResponse(
        approved=decision.approved,
        reason=getattr(decision, "reason", None),
        validator=getattr(decision, "validator", None),
    )


# Set in-memory de hashes ja importados — substituido por DB em TASK futura
_seen_hashes: set[str] = set()


@router.post("/import-report")
async def import_report(file: UploadFile = File(...)) -> dict:
    """CA14 — importa relatorio HTML/CSV do MT5 com deduplicacao por hash."""
    raw = await file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = raw.decode("latin-1")
        except Exception:
            raise HTTPException(status_code=400, detail="encoding nao reconhecido")

    name = (file.filename or "").lower()
    if name.endswith(".html") or name.endswith(".htm"):
        trades: list[ParsedTrade] = parse_html(content)
    elif name.endswith(".csv"):
        trades = parse_csv(content)
    else:
        raise HTTPException(status_code=400, detail="formato nao suportado — use .html ou .csv")

    if not trades:
        return {"imported": 0, "duplicates": 0, "errors": 1, "note": "relatorio sem trades validos"}

    imported = 0
    duplicates = 0
    for t in trades:
        h = compute_trade_hash(t)
        if h in _seen_hashes:
            duplicates += 1
            continue
        _seen_hashes.add(h)
        imported += 1
    return {"imported": imported, "duplicates": duplicates, "errors": 0}


@router.get("/reconciliation/{date}")
async def reconciliation(date: str) -> dict:
    """Stub v0.2 — reconciliacao plena exige journal/repository real (TD-v0.2-08)."""
    return {
        "date": date,
        "manual_entries": [],
        "mt5_imports": [],
        "probable_matches": [],
        "note": "Reconciliacao real exige journal repository conectado ao DB.",
    }

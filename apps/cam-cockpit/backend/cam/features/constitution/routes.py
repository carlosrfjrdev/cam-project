"""
Constitution routes -- T-H02.

SPEC R5.07: exibicao read-only. Sem endpoint de edicao direta.
Proposta de emenda apenas registra -- gate Founder obrigatorio para execucao real.

Fallback de leitura: se nao ha versao seedada no banco, le CONSTITUICAO.md do
disco para servir conteudo durante Fase 0. Persistencia real fica em TD-023.
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from cam.features.constitution.schemas import (
    AmendmentProposalRequest,
    AmendmentProposalResponse,
    ConstitutionVersionResponse,
)

router = APIRouter(prefix="/api/v1/constitution", tags=["constitution"])

# Stub in-memory para propostas (persistencia real em T-H06)
_proposals: list[dict] = []


def _resolve_constitution_file() -> Path | None:
    """
    Procura CONSTITUICAO.md em paths comuns:
    1. CAM_CONSTITUTION_PATH (env)
    2. /apps/cam-cockpit/backend/../../../CONSTITUICAO.md (monorepo)
    3. ~/teczilabs/CaM-project/CONSTITUICAO.md
    """
    import os
    env_path = os.environ.get("CAM_CONSTITUTION_PATH")
    if env_path and Path(env_path).is_file():
        return Path(env_path)

    # backend/cam/features/constitution/routes.py -> backend -> cam-cockpit -> apps -> CaM-project
    here = Path(__file__).resolve()
    candidate = here.parents[4] / "CONSTITUICAO.md"
    if candidate.is_file():
        return candidate

    fallback = Path.home() / "teczilabs" / "CaM-project" / "CONSTITUICAO.md"
    if fallback.is_file():
        return fallback

    return None


@router.get("/current", response_model=ConstitutionVersionResponse)
async def get_current_constitution() -> ConstitutionVersionResponse:
    """Retorna versao atual da Constituicao. Read-only (SPEC R5.07)."""
    path = _resolve_constitution_file()
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Constituicao nao encontrada. Defina CAM_CONSTITUTION_PATH ou coloque CONSTITUICAO.md na raiz do repo.",
        )

    content = path.read_text(encoding="utf-8")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    return ConstitutionVersionResponse(
        version="1.0",
        content=content,
        effective_date="2026-05-24",
        hash=digest,
    )


@router.get("/versions", response_model=list[ConstitutionVersionResponse])
async def list_versions() -> list[ConstitutionVersionResponse]:
    """Lista historico de versoes da Constituicao."""
    current = await get_current_constitution()
    return [current] if current else []


@router.post("/amendments", response_model=AmendmentProposalResponse, status_code=201)
async def propose_amendment(request: AmendmentProposalRequest) -> AmendmentProposalResponse:
    """
    Registra proposta de emenda constitucional.
    NAO executa a emenda -- requer aprovacao formal do Founder.
    """
    proposal = {
        "text": request.text,
        "reason": request.reason,
        "proposed_at": datetime.now(timezone.utc),
        "status": "PENDING_FOUNDER_APPROVAL",
    }
    _proposals.append(proposal)

    return AmendmentProposalResponse(
        **proposal,
        message="Proposta registrada. Execucao requer aprovacao formal do Founder e processo constitucional.",
    )

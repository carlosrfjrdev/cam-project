"""
Router FastAPI da feature ai_analyst.

Expõe endpoints de consulta de análises da IA Auditora.
Todos os endpoints são read-only (GET) — Arts. 34-36 da Constituição.

Endpoints:
- GET /api/v1/ai-analyst/analyses — lista análises (stub Fase 0)
- GET /api/v1/ai-analyst/analyses/{date} — análise de uma data (stub Fase 0)
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/ai-analyst", tags=["ai-analyst"])


@router.get("/analyses")
async def list_analyses() -> list:
    """
    Lista análises da IA Auditora.

    Stub em Fase 0 — implementar com banco em T-H06.
    """
    return []


@router.get("/analyses/{date}")
async def get_analysis(date: str) -> dict:
    """
    Retorna análise da IA Auditora para uma data específica.

    Args:
        date: Data no formato YYYY-MM-DD

    Stub em Fase 0 — implementar com banco em T-H06.
    """
    return {
        "date": date,
        "status": "STUB",
        "message": "Análise disponível pós-implementação do banco",
    }

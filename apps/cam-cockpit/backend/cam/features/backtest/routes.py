"""
Routes HTTP do Backtest Engine.

Endpoints:
  GET  /api/v1/backtest/runs              — lista runs (stub → T-H06 implementa banco)
  GET  /api/v1/backtest/runs/{run_id}     — detalhe de um run
  POST /api/v1/backtest/research/query    — DuckDB read-only (ADR-005)
  GET  /api/v1/backtest/runs/{run_id}/equity-curve

DuckDB research: apenas SELECT é permitido. Qualquer DML/DDL retorna 400.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])

# Palavras-chave que indicam operações de escrita — qualquer ocorrência
# em query DuckDB resulta em 400 (ADR-005 read-only).
FORBIDDEN_KEYWORDS = {
    "drop",
    "delete",
    "insert",
    "update",
    "create",
    "alter",
    "truncate",
}


class ResearchQueryRequest(BaseModel):
    query: str
    source_file: str


@router.get("/runs")
async def list_runs():
    """
    Lista todos os runs de backtest.
    Stub — persistência implementada em T-H06.
    """
    return []


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """
    Retorna detalhe de um run de backtest.
    Stub — implementação completa em T-H06.
    """
    return {"id": run_id, "status": "STUB"}


@router.post("/research/query")
async def research_query(body: ResearchQueryRequest):
    """
    Executa query analítica via DuckDB (read-only — ADR-005).

    Apenas queries SELECT são permitidas. DML/DDL retorna 400.
    DuckDB real implementado em T-H06 quando banco estiver disponível.
    """
    query_lower = body.query.strip().lower()
    if any(kw in query_lower for kw in FORBIDDEN_KEYWORDS):
        raise HTTPException(
            status_code=400,
            detail=(
                "Apenas queries SELECT são permitidas "
                "(DuckDB read-only — ADR-005)"
            ),
        )
    # Stub — DuckDB real implementado em T-H06
    return {
        "result": [],
        "message": "DuckDB research stub — banco não disponível",
    }


@router.get("/runs/{run_id}/equity-curve")
async def equity_curve(run_id: str):
    """
    Retorna a equity curve de um run de backtest.
    Stub — implementação completa em T-H06.
    """
    return {"run_id": run_id, "equity_curve": []}

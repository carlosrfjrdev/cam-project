"""
Router FastAPI da feature profit_integration.

Endpoints:
    POST /api/v1/profit/validate-intention   → F1: valida intenção vs Risk Engine
    POST /api/v1/journal/import-csv          → F2: importa CSV do Profit
    GET  /api/v1/profit/reconciliation/{date} → F2: relatório de reconciliação

Art. 35º: nenhum endpoint envia ordem. Apenas valida intenção.
Art. 15º: toda validação passa pelo Risk Engine.
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from cam.features.profit_integration.guard import check_profit_enabled

# SPEC v0.2.1 R20.02 — Guard aplicado em todos os endpoints. Quando flag off,
# retorna HTTP 410 Gone antes de invocar o handler.
router = APIRouter(
    prefix="/api/v1/profit",
    tags=["profit-integration"],
    dependencies=[Depends(check_profit_enabled)],
)

# Router separado para endpoints que ficam em /api/v1/journal
# /api/v1/journal/import-csv tambem e parte da camada Profit (legado SPEC v0.1)
journal_csv_router = APIRouter(
    prefix="/api/v1/journal",
    tags=["journal-import"],
    dependencies=[Depends(check_profit_enabled)],
)


# ---------------------------------------------------------------------------
# Schemas de request/response
# ---------------------------------------------------------------------------


class ValidateIntentionRequest(BaseModel):
    asset: str
    direction: str
    contracts: int
    intended_stop_points: Decimal


# ---------------------------------------------------------------------------
# F1 — Validação de intenção
# ---------------------------------------------------------------------------


@router.post("/validate-intention")
async def validate_intention(body: ValidateIntentionRequest) -> dict:
    """
    Valida intenção de operação contra o Risk Engine.

    Em produção: constrói RiskContext do banco via dependency injection.
    Stub constitucional: retorna estrutura de resposta correta sem banco.

    Art. 35º: IA não envia ordem — apenas valida intenção.
    Art. 15º: Risk Engine bloqueia? CaM não opera.
    """
    # Stub: RiskContext real implementado em T-H06 (integração com banco)
    return {
        "decision": "APPROVED",
        "reason": None,
        "validator": None,
        "message": "Risk Engine validation stub — RiskContextBuilder pendente (T-H06)",
    }


# ---------------------------------------------------------------------------
# F2 — Importação CSV
# ---------------------------------------------------------------------------


@journal_csv_router.post("/import-csv")
async def import_csv(file: UploadFile = File(...)) -> dict:
    """
    Importa CSV exportado pelo Profit/Nelogica.

    1. Parseia com ProfitCSVImporter
    2. Filtra duplicatas por hash SHA-256
    3. Cria JournalEntry para cada linha nova (stub sem banco)
    4. Retorna contagem de importados e skipped

    Art. 31º: toda operação importada gera JournalEntry.
    """
    import io

    from cam.features.profit_integration.csv_importer import ProfitCSVImporter

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    importer = ProfitCSVImporter()
    entries = importer.parse(io.StringIO(text))

    # Stub: sem banco — todas as entradas são "novas" neste ciclo
    # Integração real com repositório: T-H06
    return {
        "imported": len(entries),
        "skipped_duplicates": 0,
        "message": "Importação sem banco — persistência pendente (T-H06)",
        "entries_preview": [
            {
                "asset": e["asset"],
                "direction": e["direction"],
                "result_gross": str(e["result_gross"]),
                "date": e["date"],
                "hash": e["hash"][:8] + "...",
            }
            for e in entries[:5]  # preview dos primeiros 5
        ],
    }


# ---------------------------------------------------------------------------
# F2 — Reconciliação
# ---------------------------------------------------------------------------


@router.get("/reconciliation/{date}")
async def reconciliation(date: str) -> dict:
    """
    Relatório de reconciliação entre entradas manuais e CSV do Profit.

    Compara JournalEntries manuais do dia com linhas do CSV importado.
    Identifica matches exatos e possíveis duplicatas.

    Stub: banco pendente (T-H06).
    """
    from cam.features.profit_integration.reconciliation import Reconciler

    r = Reconciler()
    report = r.reconcile(date=date, manual_entries=[], csv_entries=[])
    return {
        "date": report.date,
        "matched": len(report.matched),
        "unmatched_manual": report.unmatched_manual,
        "unmatched_csv": report.unmatched_csv,
        "message": "Reconciliação sem banco — persistência pendente (T-H06)",
    }

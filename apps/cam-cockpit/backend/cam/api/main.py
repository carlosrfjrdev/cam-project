"""
FastAPI Composer — ponto de entrada do CaM Cockpit Backend.

Responsabilidades:
- Instanciar o app FastAPI
- Registrar middleware (CORS, logging)
- Registrar routers de todas as features
- Gerenciar lifespan (startup/shutdown)

CODE não decide arquitetura aqui — materializa o DAS §1 e ADR-002/ADR-013.
"""
# Windows: psycopg(async) e pyzmq(asyncio) exigem SelectorEventLoop. O uvicorn usa
# ProactorEventLoop por padrão no Windows → quebra DB async e bridge. Setar a policy
# ANTES do uvicorn criar o loop (este módulo é importado no load do app).
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cam.api.middleware import add_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia startup e shutdown do app.

    Startup:
    - Configurar logging estruturado
    - Registrar handlers no EventBus (fiscal, harvest, etc.)
    - (futuro) Validar conexão com banco

    Shutdown:
    - (futuro) Fechar engine de banco
    - (futuro) Flush de eventos pendentes
    """
    from cam._shared.audit import configure_logging
    from cam._shared.config import settings as cam_settings
    from cam._shared.config import validate_integration_mutex
    from cam._shared.events import event_bus
    from cam.features.journal.events import JournalEntryCreated

    configure_logging()

    # SPEC v0.2.1 R21.03 — mutex de integracao broker
    validate_integration_mutex(
        profit_enabled=cam_settings.profit_integration_enabled,
        mt5_enabled=cam_settings.mt5_integration_enabled,
    )

    # T-C07: Subscribe do fiscal ao JournalEntryCreated
    # Usa o service singleton do fiscal (in-memory em Fase 0 sem banco)
    from cam.features.fiscal.routes import _service as fiscal_service
    event_bus.subscribe(
        JournalEntryCreated,
        fiscal_service.handle_journal_entry_created,
    )

    # T-D04: Subscribe das notificações aos eventos críticos
    from cam.features.kill_switch.events import KillSwitchActivated
    from cam.features.notifications.service import notification_service
    event_bus.subscribe(
        KillSwitchActivated, notification_service.handle_kill_switch_activated
    )

    # T-TD-005 (SPEC v0.3): subscribe harvest → DarfPaid
    from cam.features.fiscal.events import DarfPaid
    from cam.features.harvest.routes import _service as harvest_service
    event_bus.subscribe(DarfPaid, harvest_service.handle_darf_paid)

    # Inspetor (ADR-014) — conecta a bridge ZeroMQ se autoconnect habilitado.
    # Best-effort: sem MT5/EA, sobe os sockets mas fica OFFLINE (falha segura).
    if cam_settings.mt5_bridge_autoconnect:
        try:
            from cam.features.mt5_integration.routes import _service as mt5_service
            await mt5_service.connect()
        except Exception:
            # falha de conexão não derruba o app — endpoints retornam 503 OFFLINE
            pass

    # startup completo
    yield

    # shutdown — desconecta bridge se conectada
    if cam_settings.mt5_bridge_autoconnect:
        try:
            from cam.features.mt5_integration.routes import _service as mt5_service
            await mt5_service.disconnect()
        except Exception:
            pass


app = FastAPI(
    title="CaM Cockpit API",
    version="0.1.0",
    description="Cockpit operacional do Carlos Alternative Money — Fase 0",
    lifespan=lifespan,
)

add_middleware(app)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
from fastapi.responses import JSONResponse  # noqa: E402

from cam.features.profit_integration.guard import FeatureDisabledException  # noqa: E402


@app.exception_handler(FeatureDisabledException)
async def feature_disabled_handler(_request, exc: FeatureDisabledException) -> JSONResponse:
    """SPEC v0.2.1 R20.02 — preserva payload no top-level (sem wrapper 'detail')."""
    return JSONResponse(status_code=exc.status_code, content=exc.payload)


# ---------------------------------------------------------------------------
# Health check — único endpoint do Bloco A
# ---------------------------------------------------------------------------

@app.get("/api/v1/health", tags=["infra"])
async def health() -> dict[str, str]:
    """
    Health check do cockpit.

    Retorna status 'ok' quando o backend está operacional.
    Não verifica banco ou serviços externos neste endpoint.
    """
    return {"status": "ok", "version": "0.1.0"}


# ---------------------------------------------------------------------------
# Registro de routers das features (Bloco A — stubs)
# ---------------------------------------------------------------------------
# Os routers serão ativados à medida que as features forem implementadas.
# Descomentar cada bloco conforme a TASK correspondente for concluída.

# Bloco C (features core) — T-C01
from cam.features.kill_switch.routes import router as kill_switch_router  # noqa: E402

app.include_router(kill_switch_router)

# Bloco C — T-C02
from cam.features.checklists.routes import router as checklists_router  # noqa: E402

app.include_router(checklists_router)

# Bloco C — T-C04/T-C05
from cam.features.journal.routes import router as journal_router  # noqa: E402

app.include_router(journal_router)

# Bloco C — T-C06/T-C07
from cam.features.fiscal.routes import router as fiscal_router  # noqa: E402

app.include_router(fiscal_router)

# Bloco C — T-C08/T-C09
from cam.features.harvest.routes import ledger_router  # noqa: E402
from cam.features.harvest.routes import router as harvest_router  # noqa: E402

app.include_router(harvest_router)
app.include_router(ledger_router)

# Bloco D — T-D01/T-D02/T-D03: profit_integration
from cam.features.profit_integration.routes import journal_csv_router  # noqa: E402
from cam.features.profit_integration.routes import router as profit_router  # noqa: E402

app.include_router(profit_router)
app.include_router(journal_csv_router)

# Bloco D — T-D05: market_data
from cam.features.market_data.routes import router as market_data_router  # noqa: E402

app.include_router(market_data_router)

# Bloco F — T-F03: backtest engine
from cam.features.backtest.routes import router as backtest_router  # noqa: E402

app.include_router(backtest_router)

# Bloco G — T-G03: ai_analyst (IA Auditora, read-only, Arts. 34-36)
from cam.features.ai_analyst.routes import router as ai_analyst_router  # noqa: E402

app.include_router(ai_analyst_router)

# Bloco H — T-H01: paper_trading (Risk Engine ativo, CA5.5)
from cam.features.paper_trading.routes import router as paper_trading_router  # noqa: E402

app.include_router(paper_trading_router)

# Bloco H — T-H02: constitution (read-only, SPEC R5.07)
from cam.features.constitution.routes import router as constitution_router  # noqa: E402

app.include_router(constitution_router)

# Dashboard composer — rotas agregadas (ADR-013: cam/api/ e o unico compositor)
from cam.api.dashboard_routes import router as dashboard_router  # noqa: E402

app.include_router(dashboard_router)

# SPEC v0.2 — mt5_integration (coexiste com profit_integration desativada)
from cam.features.mt5_integration.routes import router as mt5_router  # noqa: E402

app.include_router(mt5_router)

# Inspetor de Ativo (ADR-014) — market data read-only (candles/symbols/WS)
from cam.features.mt5_integration.market_routes import (  # noqa: E402
    router as mt5_market_router,
)

app.include_router(mt5_market_router)

# Inspetor de Ativo (ADR-014) — overlay de Regime de Markov (read-only)
from cam.features.regime.routes import router as regime_router  # noqa: E402

app.include_router(regime_router)

# Research Lane v0.5.1 (ADR-015) — Lead-Lag: ingestão MT5→research_* + Data Health.
# Composição vive em cam/api/ (autorizado a conhecer features — ADR-013); o slice
# cam.features.research NÃO importa MT5 (import-linter enforce).
from cam.api.research_routes import router as research_leadlag_router  # noqa: E402

app.include_router(research_leadlag_router)

# StrategyLab (Onda 1 — D1 ORB-30): Assets Strategy + RunTests + Experts.
# Composição vive em cam/api/ (ADR-013); o slice cam.features.strategy_lab NÃO
# importa MT5 nem execução (import-linter enforce). Valores BRUTOS (R-11).
from cam.api.strategy_lab_routes import router as strategy_lab_router  # noqa: E402

app.include_router(strategy_lab_router)

# T-TD-026 (SPEC v0.3) — WebSocket P&L stub funcional
from cam.api.websocket import router as ws_router  # noqa: E402

app.include_router(ws_router)

# ---------------------------------------------------------------------------
# BL-UI-0 (SPEC v0.5-COCKPIT-UI) — Borda HTTP: expõe features v0.4 à UI.
# Read + comandos governados/seguros. NENHUM endpoint submete ordem (Art. 35º).
# ---------------------------------------------------------------------------

# U001 — Strategy Registry (dead route → viva)
from cam.features.strategies.routes import router as strategies_router  # noqa: E402

app.include_router(strategies_router)

# U002 — Holdings / Carteira Hard (dead route → viva)
from cam.features.ledger.holdings_router import router as holdings_router  # noqa: E402

app.include_router(holdings_router)

# U003 — Robot Orchestrator (read-only)
from cam.features.robot_orchestrator.routes import (  # noqa: E402
    router as robot_orchestrator_router,
)

app.include_router(robot_orchestrator_router)

# U004 — Scaling / Escalonamento constitucional (Art. 11-B)
from cam.features.scaling.routes import router as scaling_router  # noqa: E402

app.include_router(scaling_router)

# U005 — Research / AI Workbench (governado; OpenAI bloqueado)
from cam.features.research.routes import router as research_router  # noqa: E402

app.include_router(research_router)

# U006 — Fundamentals / Dividendos / Policy alerts
from cam.features.fundamentals.routes import router as fundamentals_router  # noqa: E402

app.include_router(fundamentals_router)

# U007 — Order Gateway decisions (SEC CRÍTICO, read-only)
from cam.api.order_gateway_routes import router as order_gateway_router  # noqa: E402

app.include_router(order_gateway_router)

# Trade Analyzer — report + ticks → IA (Claude/OpenAI) analisa erros/correções
from cam.features.trade_analyzer.routes import router as trade_analyzer_router  # noqa: E402, E501

app.include_router(trade_analyzer_router)

# Operation Analyzer (CASCA) — ticks+candles+estratégia → sinais (R:R 1:3), sem bloqueio
from cam.features.operation_analyzer.routes import router as operation_analyzer_router  # noqa: E402, E501

app.include_router(operation_analyzer_router)

# App settings — preferências de runtime (provedor de dados MT5/Profit)
from cam.features.app_settings.routes import router as app_settings_router  # noqa: E402

app.include_router(app_settings_router)

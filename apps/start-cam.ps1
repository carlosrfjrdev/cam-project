# ============================================================
# CaM Cockpit -- Launcher (PowerShell)
# Sobe os 3 servicos do cockpit: BANCO (TimescaleDB/Docker) + BACKEND + FRONTEND
#
# Diferenca para scripts/dev.ps1:
#   - dev.ps1  = SETUP (instala deps, roda migrations uma vez e termina)
#   - start-cam.ps1 = LAUNCHER (sobe e mantem rodando os 3 servicos)
#
# Backend e frontend abrem cada um em sua propria janela do PowerShell
# (logs visiveis; Ctrl+C em cada janela para parar). O banco roda em
# container Docker (em background).
#
# Pre-requisitos:
#   - Docker Desktop em execucao
#   - uv instalado (https://docs.astral.sh/uv/)
#   - Node.js 20+ instalado (npm install ja feito; senao rode scripts/dev.ps1)
#
# Uso:
#   .\start-cam.ps1                  # sobe banco + backend + frontend
#   .\start-cam.ps1 -SkipDb          # nao mexe no Docker (banco ja de pe)
#   .\start-cam.ps1 -Migrate         # roda 'alembic upgrade head' antes do backend
#   .\start-cam.ps1 -BackendPort 8001
# ============================================================

param(
    [switch]$SkipDb,
    [switch]$Migrate,
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [string]$BackendHost = "127.0.0.1",
    [int]$BackendPort = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---- Paths (resolvidos a partir da localizacao do script) ------------------
$AppsDir     = Split-Path -Parent $MyInvocation.MyCommand.Path        # ...\apps
$AppDir      = Join-Path $AppsDir "cam-cockpit"
$BackendDir  = Join-Path $AppDir  "backend"
$FrontendDir = Join-Path $AppDir  "frontend"
$Compose     = Join-Path $AppDir  "docker-compose.yml"

# Porta do banco no host (docker-compose.yml: 5434:5432; .env usa 5434)
$DbHostPort  = 5434

function Write-Step { param([string]$m) Write-Host ""; Write-Host "==> $m" -ForegroundColor Cyan }
function Write-OK   { param([string]$m) Write-Host "    OK: $m"   -ForegroundColor Green }
function Write-Warn { param([string]$m) Write-Host "    AVISO: $m" -ForegroundColor Yellow }
function Write-Die  { param([string]$m) Write-Host "    ERRO: $m"  -ForegroundColor Red; exit 1 }

# ============================================================
# 1. BANCO -- TimescaleDB via Docker Compose
# ============================================================
if (-not $SkipDb) {
    Write-Step "Subindo banco (TimescaleDB) via Docker Compose..."

    try { docker info 2>&1 | Out-Null }
    catch { Write-Die "Docker Desktop nao esta em execucao. Inicie-o e tente de novo (ou use -SkipDb)." }

    docker compose -f $Compose up -d db | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Die "Falha ao subir o container do banco." }
    Write-OK "Container do banco solicitado (host:porta = localhost:$DbHostPort)"

    Write-Step "Aguardando banco aceitar conexoes..."
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        docker compose -f $Compose exec -T db pg_isready -U cam -d cam_db 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        Start-Sleep -Seconds 2
    }
    if ($ready) { Write-OK "Banco pronto" }
    else        { Write-Die "Banco nao ficou pronto em ~60s. Verifique 'docker compose -f `"$Compose`" logs db'." }
} else {
    Write-Step "Banco: -SkipDb ligado, assumindo que ja esta de pe em localhost:$DbHostPort"
}

# ============================================================
# 2. (opcional) MIGRATIONS Alembic
# ============================================================
if ($Migrate) {
    Write-Step "Rodando migrations Alembic (upgrade head)..."
    Push-Location $BackendDir
    try {
        uv run alembic upgrade head
        if ($LASTEXITCODE -eq 0) { Write-OK "Migrations aplicadas" }
        else                     { Write-Warn "Alembic retornou erro (verifique a saida acima)." }
    } finally { Pop-Location }
}

# ============================================================
# 3. BACKEND -- FastAPI (run_server.py: SelectorEventLoop no Windows)
#    Abre em nova janela do PowerShell (logs visiveis; Ctrl+C para parar).
# ============================================================
if (-not $SkipBackend) {
    Write-Step "Iniciando BACKEND em nova janela (porta $BackendPort)..."
    $backendCmd = "Set-Location '$BackendDir'; " +
                  "Write-Host 'CaM BACKEND -- http://${BackendHost}:$BackendPort' -ForegroundColor Cyan; " +
                  "uv run python run_server.py --host $BackendHost --port $BackendPort"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd | Out-Null
    Write-OK "Backend lancado -> http://${BackendHost}:$BackendPort  (docs em /docs)"
}

# ============================================================
# 4. FRONTEND -- Vite dev server (porta 5173, proxy /api -> backend)
#    Abre em nova janela do PowerShell.
# ============================================================
if (-not $SkipFrontend) {
    Write-Step "Iniciando FRONTEND em nova janela (Vite, porta 5173)..."
    if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
        Write-Warn "node_modules ausente no frontend. Rode 'npm install' (ou .\cam-cockpit\scripts\dev.ps1) antes."
    }
    $frontendCmd = "Set-Location '$FrontendDir'; " +
                   "Write-Host 'CaM FRONTEND -- http://localhost:5173' -ForegroundColor Cyan; " +
                   "npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd | Out-Null
    Write-OK "Frontend lancado -> http://localhost:5173"
}

# ============================================================
# 5. Resumo
# ============================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  CaM Cockpit -- servicos iniciados         " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Banco    : localhost:$DbHostPort (Docker container 'db')"
if (-not $SkipBackend)  { Write-Host "  Backend  : http://${BackendHost}:$BackendPort  (Swagger em /docs)" }
if (-not $SkipFrontend) { Write-Host "  Frontend : http://localhost:5173" }
Write-Host ""
Write-Host "  Parar backend/frontend : Ctrl+C em cada janela aberta." -ForegroundColor White
Write-Host "  Parar banco            : docker compose -f `"$Compose`" stop db" -ForegroundColor White
Write-Host ""

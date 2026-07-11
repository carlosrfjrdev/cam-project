# ============================================================
# CaM Cockpit -- Setup Windows (PowerShell)
# T-H03: equivalente PowerShell do dev.sh (ADR-012)
#
# Pre-requisitos:
#   - Docker Desktop com WSL2 instalado e em execucao
#   - Python 3.12+ instalado
#   - uv instalado (https://docs.astral.sh/uv/)
#   - Node.js 20+ instalado
#   - Git instalado
#
# Uso: .\scripts\dev.ps1
#      .\scripts\dev.ps1 -SkipDockerCheck
# ============================================================

param(
    [switch]$SkipDockerCheck,
    [switch]$SkipMigrations
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppDir    = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $AppDir "backend"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Message)
    Write-Host "    OK: $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "    ERRO: $Message" -ForegroundColor Red
    exit 1
}

# ============================================================
# 1. Verificar Docker Desktop
# ============================================================
if (-not $SkipDockerCheck) {
    Write-Step "Verificando Docker Desktop..."
    try {
        $dockerVersion = docker --version 2>&1
        Write-OK $dockerVersion
    } catch {
        Write-Fail "Docker nao encontrado. Instale Docker Desktop com WSL2: https://docs.docker.com/desktop/windows/"
    }

    try {
        docker info 2>&1 | Out-Null
        Write-OK "Docker Desktop esta em execucao"
    } catch {
        Write-Fail "Docker Desktop nao esta em execucao. Inicie o Docker Desktop e tente novamente."
    }
}

# ============================================================
# 2. Subir banco de dados (TimescaleDB)
# ============================================================
Write-Step "Subindo TimescaleDB via Docker Compose..."
Set-Location $AppDir
try {
    docker compose up -d db 2>&1
    Write-OK "Banco de dados iniciado na porta 5433"
} catch {
    Write-Fail "Falha ao subir banco. Verifique o docker-compose.yml."
}

# Aguardar banco estar pronto
Write-Step "Aguardando banco de dados estar pronto..."
$retries = 0
while ($retries -lt 30) {
    try {
        docker compose exec -T db pg_isready -U cam -d cam_db 2>&1 | Out-Null
        Write-OK "Banco de dados pronto"
        break
    } catch {
        $retries++
        Start-Sleep -Seconds 2
    }
}
if ($retries -eq 30) {
    Write-Fail "Banco de dados nao ficou pronto em 60 segundos"
}

# ============================================================
# 3. Instalar dependencias Python (uv)
# ============================================================
Write-Step "Instalando dependencias Python via uv..."
Set-Location $BackendDir
try {
    uv sync --extra dev 2>&1
    Write-OK "Dependencias Python instaladas"
} catch {
    Write-Fail "Falha ao instalar dependencias Python. Verifique se uv esta instalado: https://docs.astral.sh/uv/"
}

# ============================================================
# 4. Rodar migrations Alembic
# ============================================================
if (-not $SkipMigrations) {
    Write-Step "Rodando migrations Alembic..."
    $env:DATABASE_URL = "postgresql+psycopg://cam:cam@localhost:5433/cam_db"
    try {
        uv run alembic upgrade head 2>&1
        Write-OK "Migrations aplicadas"
    } catch {
        Write-Host "    AVISO: Migrations falharam (banco pode nao ter extensao TimescaleDB)" -ForegroundColor Yellow
    }
}

# ============================================================
# 5. Instalar dependencias Node.js (frontend)
# ============================================================
$FrontendDir = Join-Path $AppDir "frontend"
Write-Step "Instalando dependencias Node.js (frontend)..."
Set-Location $FrontendDir
try {
    npm install 2>&1
    Write-OK "Dependencias Node.js instaladas"
} catch {
    Write-Host "    AVISO: npm install falhou. Verifique Node.js 20+" -ForegroundColor Yellow
}

# ============================================================
# 6. Resumo
# ============================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  CaM Cockpit -- Setup Windows Concluido  " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor White
Write-Host "  1. Backend:  cd backend && uv run python run_server.py   (Windows: SelectorEventLoop p/ DB async + bridge)"
Write-Host "  2. Frontend: cd frontend && npm run dev"
Write-Host "  3. Abrir:    http://localhost:5173"
Write-Host ""
Write-Host "Configuracao obrigatoria (.env):" -ForegroundColor Yellow
Write-Host "  - TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (ver TODO-OPERACIONAL.md OP-007)"
Write-Host "  - ANTHROPIC_API_KEY (opcional, Ollama e o default)"
Write-Host ""
Write-Host "Fase atual: FASE_0 (Construcao). Sem trade real." -ForegroundColor Cyan

#!/usr/bin/env bash
# CaM Cockpit — Dev Setup (Linux)
#
# Pre-requisitos:
#   - Docker Engine instalado e rodando
#   - Python 3.12+ (uv faz download automático se necessário)
#   - Node.js 20+ e npm 10+ (para frontend)
#
# Uso: bash scripts/dev.sh
# Idempotente: pode ser executado multiplas vezes sem efeito colateral.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== CaM Cockpit — Dev Setup (Linux) ==="
echo "Diretorio do projeto: $PROJECT_DIR"

# ---------------------------------------------------------------------------
# Verificar pre-requisitos
# ---------------------------------------------------------------------------

if ! command -v docker >/dev/null 2>&1; then
    echo "ERRO: Docker nao encontrado. Instale o Docker Engine."
    echo "  https://docs.docker.com/engine/install/"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "ERRO: Docker daemon nao esta rodando. Inicie o Docker."
    exit 1
fi

PYTHON_CMD=""
if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_CMD="python3.12"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    echo "ERRO: Python 3.12+ nao encontrado."
    exit 1
fi

echo "Python: $($PYTHON_CMD --version)"
echo "Docker: $(docker --version)"

# ---------------------------------------------------------------------------
# Instalar dependencias Python via uv
# ---------------------------------------------------------------------------

if ! command -v uv >/dev/null 2>&1; then
    echo ">>> Instalando uv..."
    pip install uv --quiet
fi

echo ">>> Instalando dependencias Python..."
cd "$PROJECT_DIR/backend"
uv sync --extra dev

# ---------------------------------------------------------------------------
# Subir banco de dados
# ---------------------------------------------------------------------------

echo ">>> Subindo banco de dados (TimescaleDB)..."
cd "$PROJECT_DIR"
docker compose up -d db

echo ">>> Aguardando banco de dados ficar pronto..."
for i in $(seq 1 30); do
    if docker compose exec db pg_isready -U cam -d cam_db >/dev/null 2>&1; then
        echo "    Banco pronto!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERRO: Banco nao ficou pronto em 30 tentativas."
        exit 1
    fi
    sleep 2
done

# ---------------------------------------------------------------------------
# Rodar migrations
# ---------------------------------------------------------------------------

echo ">>> Rodando migrations Alembic..."
cd "$PROJECT_DIR/backend"
uv run alembic upgrade head

# ---------------------------------------------------------------------------
# Validar saude da API (opcional — se quiser testar startup)
# ---------------------------------------------------------------------------

echo ""
echo "=== Setup completo! ==="
echo ""
echo "Para iniciar o backend:"
echo "  cd backend && uv run uvicorn cam.api.main:app --reload --port 8000"
echo ""
echo "Para iniciar o frontend:"
echo "  cd frontend && npm install && npm run dev"
echo ""
echo "Health check (apos iniciar o backend):"
echo "  curl http://localhost:8000/api/v1/health"

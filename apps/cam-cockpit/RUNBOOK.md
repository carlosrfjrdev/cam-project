# RUNBOOK — cam-cockpit

> Referência técnica operacional. Comandos para subir, parar e trabalhar com o ambiente.
> **SO de desenvolvimento:** Linux (este guia). Para Windows, ver seção específica.

---

## Pré-requisitos

| Ferramenta | Versão mínima | Verificar |
|---|---|---|
| Docker Engine | 24+ | `docker --version` |
| Python | 3.12+ | `python3 --version` |
| uv | qualquer | `uv --version` |
| Node.js | 20+ | `node --version` |
| npm | 10+ | `npm --version` |

**Instalar uv** (se não tiver):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup inicial (primeira vez)

```bash
# 1. Entrar no diretório do app
cd ~/teczilabs/CaM-project/apps/cam-cockpit

# 2. Subir o banco (TimescaleDB na porta 5433)
docker compose up -d db

# 3. Aguardar banco pronto
docker compose exec db pg_isready -U cam -d cam_db

# 4. Instalar dependências Python
cd backend
uv sync --extra dev

# 5. Rodar migrations
uv run alembic upgrade head

# 6. Verificar migrations (deve mostrar 4 passed)
uv run pytest tests/test_migrations.py -v

# 7. Instalar dependências do frontend
cd ../frontend
npm install
```

---

## Subir o ambiente (uso diário)

### Terminal 1 — Banco de dados
```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit
docker compose up -d db
```

### Terminal 2 — Backend (API FastAPI)
```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit/backend
uv run uvicorn cam.api.main:app --reload --port 8000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### Terminal 3 — Frontend (React + Vite)
```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit/frontend
npm run dev
```

**Saída esperada:**
```
  VITE v6.x.x  ready in Xms
  ➜  Local:   http://localhost:5173/
```

### Acessar o cockpit
```
Frontend:  http://localhost:5173
API docs:  http://localhost:8000/docs
Health:    http://localhost:8000/api/v1/health
```

---

## Parar o ambiente

```bash
# Parar banco (preserva dados no volume pgdata)
cd ~/teczilabs/CaM-project/apps/cam-cockpit
docker compose stop db

# Parar backend e frontend: Ctrl+C nos terminais correspondentes
```

**Destruir banco e dados** (recomeçar do zero — irreversível):
```bash
docker compose down -v   # remove o volume pgdata também
```

---

## Comandos de desenvolvimento

### Backend

```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit/backend

# Rodar todos os testes (exceto migrations, que precisam do banco)
uv run pytest --ignore=tests/test_migrations.py -q

# Rodar todos os testes incluindo migrations (banco deve estar rodando)
uv run pytest -q

# Testes com cobertura
uv run pytest --ignore=tests/test_migrations.py --cov=cam --cov-report=term-missing -q

# Lint
uv run ruff check cam/ tests/

# Lint com auto-fix
uv run ruff check cam/ tests/ --fix

# Typecheck
uv run mypy cam/

# Verificar contratos de arquitetura (features isoladas, Risk Engine sem I/O)
uv run lint-imports

# Rodar tudo de uma vez
uv run ruff check cam/ tests/ && uv run mypy cam/ && uv run lint-imports && uv run pytest --ignore=tests/test_migrations.py -q
```

### Migrations

```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit/backend

# Ver estado atual
uv run alembic current

# Aplicar todas as migrations pendentes
uv run alembic upgrade head

# Ver histórico de migrations
uv run alembic history

# Voltar 1 migration
uv run alembic downgrade -1

# Voltar ao estado inicial (apaga todas as tabelas)
uv run alembic downgrade base
```

### Frontend

```bash
cd ~/teczilabs/CaM-project/apps/cam-cockpit/frontend

# Iniciar em modo dev (hot reload)
npm run dev

# Rodar testes
npm test

# Testes em modo watch
npm run test:watch

# Build de produção
npm run build

# Checar TypeScript
npx tsc --noEmit

# Lint
npm run lint
```

---

## Verificar saúde do ambiente

```bash
# Banco rodando?
docker compose ps

# Banco aceita conexões?
docker compose exec db pg_isready -U cam -d cam_db

# Tabelas existem?
docker compose exec db psql -U cam -d cam_db -c "\dt cam_*"

# API respondendo?
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

# Hypertables TimescaleDB criadas?
docker compose exec db psql -U cam -d cam_db \
  -c "SELECT hypertable_name FROM timescaledb_information.hypertables;"
```

---

## Configuração do .env

O arquivo `backend/.env` (não commitado) deve conter:

```bash
# Banco de dados — porta 5433 (não conflita com Teczilabs)
DATABASE_URL=postgresql+psycopg://cam:cam@localhost:5433/cam_db

# Telegram — obter via @BotFather (cockpit funciona sem, mas sem alertas)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Anthropic API — opcional (Ollama local é o default para IA auditora)
ANTHROPIC_API_KEY=

# Ollama — IA auditora local
OLLAMA_BASE_URL=http://localhost:11434

# Diretório do journal JSONL (fallback de recuperação)
CAM_JOURNAL_DIR=~/.cam/journal
```

Copiar o exemplo:
```bash
cp backend/.env.example backend/.env
# Editar backend/.env com os valores reais
```

---

## Estrutura de portas

| Serviço | Porta | Descrição |
|---|---|---|
| PostgreSQL / TimescaleDB | **5433** | Porta do host → container usa 5432 internamente |
| Backend FastAPI | **8000** | API REST + WebSocket |
| Frontend Vite | **5173** | SPA React em dev |

> **Por que 5433?** Evita conflito com bancos Teczilabs que usam a porta padrão 5432.

---

## Setup Windows (produção / integração Profit)

```powershell
# Pré-requisito: Docker Desktop com WSL2, Python 3.12+, uv, Node.js 20+

cd C:\...\CaM-project\apps\cam-cockpit
.\scripts\dev.ps1

# Subir backend
cd backend
uv run uvicorn cam.api.main:app --reload --port 8000

# Subir frontend (terminal separado)
cd ..\frontend
npm run dev
```

> Script completo: `scripts/dev.ps1` — inclui verificação do Docker Desktop, migrations e install do npm.

---

## Backup manual

```bash
# Linux — backup imediato
bash ~/teczilabs/CaM-project/apps/cam-cockpit/scripts/backup.sh

# Verificar arquivos gerados
ls ~/cam-backups/db/
ls ~/cam-backups/journal/

# Agendar via cron (02:00 diário)
crontab -e
# Adicionar: 0 2 * * * /home/carlos-ferreira/teczilabs/CaM-project/apps/cam-cockpit/scripts/backup.sh
```

---

## Troubleshooting

### `uv run alembic upgrade head` falha com "could not connect"
```bash
# Verificar se o banco está rodando
docker compose ps
docker compose up -d db
docker compose exec db pg_isready -U cam -d cam_db
```

### Porta 5433 em uso
```bash
# Ver o que está usando a porta
sudo ss -tlnp | grep 5433
# Matar o processo ou alterar a porta no docker-compose.yml
```

### Frontend não conecta ao backend (erro de CORS ou proxy)
```bash
# Verificar se o backend está rodando
curl http://localhost:8000/api/v1/health
# O vite.config.ts faz proxy de /api → localhost:8000 automaticamente
```

### Testes de migration dão SKIP
```bash
# O .env precisa existir com DATABASE_URL configurado
cat backend/.env | grep DATABASE_URL
# Rodar com banco ativo:
cd backend && uv run pytest tests/test_migrations.py -v
```

### `lint-imports` falha
```bash
# Verificar se a feature importa outra feature diretamente
uv run lint-imports --verbose
# Features só podem se comunicar via EventBus (cam/_shared/events)
# cam/api/main.py é o único compositor autorizado (ADR-013)
```

#!/usr/bin/env bash
# ============================================================
# CaM Cockpit -- Backup Linux (T-H04)
#
# Executa:
#   1. pg_dump do banco cam_db
#   2. Backup do diretorio de journals JSONL
#   3. Sync para Google Drive via rclone (se configurado)
#
# Adicionar ao crontab:
#   0 2 * * * /path/to/apps/cam-cockpit/scripts/backup.sh >> /var/log/cam-backup.log 2>&1
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${CAM_BACKUP_DIR:-$HOME/cam-backups}"
DB_NAME="${CAM_DB_NAME:-cam_db}"
DB_USER="${CAM_DB_USER:-cam}"
DB_HOST="${CAM_DB_HOST:-localhost}"
DB_PORT="${CAM_DB_PORT:-5433}"
JOURNAL_DIR="${CAM_JOURNAL_DIR:-$HOME/.cam/journal}"
RCLONE_REMOTE="${CAM_RCLONE_REMOTE:-gdrive:cam-backups}"
RETENTION_DAYS="${CAM_BACKUP_RETENTION_DAYS:-30}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ---------------------------------------------------------------------------
# Criar diretorio de backup
# ---------------------------------------------------------------------------
mkdir -p "$BACKUP_DIR/db" "$BACKUP_DIR/journal"

# ---------------------------------------------------------------------------
# 1. pg_dump do banco
# ---------------------------------------------------------------------------
log "Iniciando backup do banco de dados..."
PG_DUMP_FILE="$BACKUP_DIR/db/cam_db_${TIMESTAMP}.sql.gz"

PGPASSWORD="${CAM_DB_PASSWORD:-cam}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    "$DB_NAME" \
    | gzip > "$PG_DUMP_FILE"

log "Backup do banco concluido: $PG_DUMP_FILE ($(du -sh "$PG_DUMP_FILE" | cut -f1))"

# ---------------------------------------------------------------------------
# 2. Backup dos journals JSONL (SPEC R11.06 — journal duplo)
# ---------------------------------------------------------------------------
if [ -d "$JOURNAL_DIR" ]; then
    JOURNAL_BACKUP="$BACKUP_DIR/journal/journal_${TIMESTAMP}.tar.gz"
    tar -czf "$JOURNAL_BACKUP" -C "$(dirname "$JOURNAL_DIR")" "$(basename "$JOURNAL_DIR")"
    log "Backup dos journals JSONL concluido: $JOURNAL_BACKUP"
else
    log "AVISO: Diretorio de journals nao encontrado: $JOURNAL_DIR"
fi

# ---------------------------------------------------------------------------
# 3. Remover backups antigos (retencao configuravel)
# ---------------------------------------------------------------------------
log "Removendo backups com mais de ${RETENTION_DAYS} dias..."
find "$BACKUP_DIR" -name "*.gz" -mtime +"$RETENTION_DAYS" -delete
log "Limpeza de backups antigos concluida"

# ---------------------------------------------------------------------------
# 4. Sync com Google Drive via rclone (opcional)
# ---------------------------------------------------------------------------
if command -v rclone &>/dev/null; then
    log "Sincronizando com Google Drive via rclone..."
    if rclone lsd "$RCLONE_REMOTE" &>/dev/null 2>&1; then
        rclone sync "$BACKUP_DIR" "$RCLONE_REMOTE" --progress 2>&1 | tail -5
        log "Sync com Google Drive concluido"
    else
        log "AVISO: Remote rclone '$RCLONE_REMOTE' nao acessivel. Backup local apenas."
        log "  Configurar: rclone config && rclone ls $RCLONE_REMOTE"
    fi
else
    log "AVISO: rclone nao instalado. Backup local apenas."
    log "  Instalar: curl https://rclone.org/install.sh | bash"
fi

log "Backup CaM concluido. Arquivos em: $BACKUP_DIR"

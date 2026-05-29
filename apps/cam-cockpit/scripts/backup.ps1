# ============================================================
# CaM Cockpit -- Backup Windows (PowerShell) - T-H04
#
# Equivalente do backup.sh para Windows.
# Configurar no Task Scheduler:
#   Trigger: Diario, 02:00
#   Action:  powershell.exe -File "C:\...\backup.ps1"
# ============================================================

param(
    [string]$BackupDir  = "$env:USERPROFILE\cam-backups",
    [string]$DbName     = "cam_db",
    [string]$DbUser     = "cam",
    [string]$DbHost     = "localhost",
    [string]$DbPort     = "5433",
    [string]$JournalDir = "$env:USERPROFILE\.cam\journal",
    [string]$RcloneRemote = "gdrive:cam-backups",
    [int]$RetentionDays   = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] $Message"
}

# Criar diretorios de backup
New-Item -ItemType Directory -Force -Path "$BackupDir\db"    | Out-Null
New-Item -ItemType Directory -Force -Path "$BackupDir\journal" | Out-Null

# ---------------------------------------------------------------------------
# 1. pg_dump (requer pg_dump no PATH -- instalar PostgreSQL client tools)
# ---------------------------------------------------------------------------
Write-Log "Iniciando backup do banco de dados..."
$PgDumpFile = "$BackupDir\db\cam_db_$Timestamp.sql"

$env:PGPASSWORD = $env:CAM_DB_PASSWORD ?? "cam"
try {
    pg_dump -h $DbHost -p $DbPort -U $DbUser $DbName -f $PgDumpFile
    Compress-Archive -Path $PgDumpFile -DestinationPath "$PgDumpFile.zip" -Force
    Remove-Item $PgDumpFile
    Write-Log "Backup do banco concluido: $PgDumpFile.zip"
} catch {
    Write-Log "ERRO no pg_dump: $_"
    Write-Log "Certifique-se que pg_dump esta no PATH (PostgreSQL client tools)"
}

# ---------------------------------------------------------------------------
# 2. Backup dos journals JSONL
# ---------------------------------------------------------------------------
if (Test-Path $JournalDir) {
    $JournalBackup = "$BackupDir\journal\journal_$Timestamp.zip"
    Compress-Archive -Path $JournalDir -DestinationPath $JournalBackup -Force
    Write-Log "Backup dos journals JSONL concluido: $JournalBackup"
} else {
    Write-Log "AVISO: Diretorio de journals nao encontrado: $JournalDir"
}

# ---------------------------------------------------------------------------
# 3. Remover backups antigos
# ---------------------------------------------------------------------------
Write-Log "Removendo backups com mais de $RetentionDays dias..."
$cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Recurse -File |
    Where-Object { $_.LastWriteTime -lt $cutoff } |
    Remove-Item -Force
Write-Log "Limpeza concluida"

# ---------------------------------------------------------------------------
# 4. Sync com Google Drive via rclone
# ---------------------------------------------------------------------------
if (Get-Command rclone -ErrorAction SilentlyContinue) {
    Write-Log "Sincronizando com Google Drive via rclone..."
    try {
        rclone sync $BackupDir $RcloneRemote --progress
        Write-Log "Sync com Google Drive concluido"
    } catch {
        Write-Log "AVISO: rclone sync falhou: $_"
    }
} else {
    Write-Log "AVISO: rclone nao instalado. Backup local apenas."
}

Write-Log "Backup CaM Windows concluido. Arquivos em: $BackupDir"

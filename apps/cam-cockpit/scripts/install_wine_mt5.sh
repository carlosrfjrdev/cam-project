#!/usr/bin/env bash
# ============================================================================
# install_wine_mt5.sh — Setup automatizado Wine + MT5 + EA CaM (SPEC v0.2)
#
# Pre-requisitos:
#   - Ubuntu 24.04+ LTS (ou Debian-based equivalente)
#   - sudo / pacote sudo configurado
#   - Internet para baixar Wine e MT5
#
# Uso:
#   bash scripts/install_wine_mt5.sh                # full install
#   bash scripts/install_wine_mt5.sh --skip-wine    # pula instalacao Wine
#   bash scripts/install_wine_mt5.sh --skip-mt5     # pula download MT5
#   bash scripts/install_wine_mt5.sh --skip-ea      # pula copia do EA
#
# Idempotente: pode rodar varias vezes — pula etapas ja completas.
# ============================================================================

set -euo pipefail

SKIP_WINE=false
SKIP_MT5=false
SKIP_EA=false

for arg in "$@"; do
  case "$arg" in
    --skip-wine) SKIP_WINE=true ;;
    --skip-mt5)  SKIP_MT5=true ;;
    --skip-ea)   SKIP_EA=true ;;
    -h|--help)
      grep '^#' "$0" | sed -E 's/^# ?//; /^=+$/d'
      exit 0 ;;
    *) echo "Flag desconhecida: $arg"; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
MQL5_DIR="$APP_DIR/mql5"
WINE_PREFIX="${MT5_WINE_PREFIX:-$HOME/.wine}"
MT5_INSTALL_URL="https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
MT5_DOWNLOAD="$HOME/.cache/cam/mt5setup.exe"
MT5_TERMINAL="$WINE_PREFIX/drive_c/Program Files/MetaTrader 5/terminal64.exe"

log() { echo -e "\e[1;36m[install_wine_mt5]\e[0m $*"; }
ok()  { echo -e "  \e[32mOK\e[0m: $*"; }
warn(){ echo -e "  \e[33mAVISO\e[0m: $*"; }
fail(){ echo -e "  \e[31mERRO\e[0m: $*" >&2; exit 1; }

# ----------------------------------------------------------------------------
# 1. Wine
# ----------------------------------------------------------------------------
if $SKIP_WINE; then
  log "Pulando instalacao Wine (--skip-wine)."
elif command -v wine >/dev/null 2>&1; then
  ok "Wine ja instalado: $(wine --version)"
else
  log "Instalando Wine..."
  sudo dpkg --add-architecture i386 || true
  sudo mkdir -pm755 /etc/apt/keyrings
  sudo wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
  RELEASE="$(lsb_release -cs)"
  sudo wget -qNP /etc/apt/sources.list.d/ "https://dl.winehq.org/wine-builds/ubuntu/dists/${RELEASE}/winehq-${RELEASE}.sources"
  sudo apt-get update
  sudo apt-get install -y --install-recommends winehq-stable
  ok "Wine instalado: $(wine --version)"
fi

# ----------------------------------------------------------------------------
# 2. MetaTrader 5
# ----------------------------------------------------------------------------
if $SKIP_MT5; then
  log "Pulando instalacao MT5 (--skip-mt5)."
elif [ -f "$MT5_TERMINAL" ]; then
  ok "MT5 ja instalado em $MT5_TERMINAL"
else
  log "Baixando instalador MT5..."
  mkdir -p "$(dirname "$MT5_DOWNLOAD")"
  if [ ! -f "$MT5_DOWNLOAD" ]; then
    wget -q --show-progress -O "$MT5_DOWNLOAD" "$MT5_INSTALL_URL"
    ok "Instalador salvo em $MT5_DOWNLOAD"
  fi
  log "Executando mt5setup.exe via Wine (siga o instalador grafico)..."
  WINEPREFIX="$WINE_PREFIX" wine "$MT5_DOWNLOAD"
  if [ ! -f "$MT5_TERMINAL" ]; then
    warn "MT5 nao detectado em path padrao apos instalacao. Verifique se instalou em 'C:\\Program Files\\MetaTrader 5\\'."
  else
    ok "MT5 instalado."
  fi
fi

# ----------------------------------------------------------------------------
# 3. EA cam_bridge.mq5 + biblioteca cam_zmq.mqh
# ----------------------------------------------------------------------------
if $SKIP_EA; then
  log "Pulando copia do EA (--skip-ea)."
else
  # Localiza diretorio de scripts MQL5 do MT5 (terminal_data_path / MQL5/...)
  MT5_DATA_BASE="$(find "$WINE_PREFIX/drive_c/users" -type d -name "MetaQuotes" 2>/dev/null | head -1 || true)"
  if [ -z "$MT5_DATA_BASE" ]; then
    warn "Nao foi possivel localizar diretorio MQL5 do MT5. Copie manualmente:"
    warn "  $MQL5_DIR/experts/cam_bridge.mq5  ->  <data_folder>/MQL5/Experts/"
    warn "  $MQL5_DIR/include/cam_zmq.mqh     ->  <data_folder>/MQL5/Include/"
  else
    MT5_EXPERTS="$(find "$MT5_DATA_BASE" -type d -path "*MQL5/Experts" 2>/dev/null | head -1 || true)"
    MT5_INCLUDE="$(find "$MT5_DATA_BASE" -type d -path "*MQL5/Include" 2>/dev/null | head -1 || true)"
    if [ -n "$MT5_EXPERTS" ]; then
      cp -v "$MQL5_DIR/experts/cam_bridge.mq5" "$MT5_EXPERTS/"
      ok "cam_bridge.mq5 copiado para $MT5_EXPERTS"
    fi
    if [ -n "$MT5_INCLUDE" ]; then
      cp -v "$MQL5_DIR/include/cam_zmq.mqh" "$MT5_INCLUDE/"
      ok "cam_zmq.mqh copiado para $MT5_INCLUDE"
    fi
  fi
fi

# ----------------------------------------------------------------------------
# 4. Resumo + proximos passos manuais
# ----------------------------------------------------------------------------
log "Setup concluido. Proximos passos MANUAIS:"
cat <<EOF
  1. Abrir MT5: wine "$MT5_TERMINAL" &
  2. Logar em conta DEMO (NUNCA conta real em v0.2 — sec §7.1).
  3. Tools → Options → Expert Advisors → marcar:
       [x] Allow Algo Trading
       [x] Allow DLL imports
  4. Baixar libzmq.dll e copiar para <data_folder>/MQL5/Libraries/
       (download: https://github.com/zeromq/libzmq/releases — versao Windows x64)
  5. F4 (MetaEditor) → abrir cam_bridge.mq5 → F7 (compilar)
  6. Atachar EA ao grafico WIN ou WDO em conta DEMO.
  7. Validar conexao com backend Python:
       curl http://localhost:8000/api/v1/mt5/bridge/status
     Deve retornar state=ONLINE apos primeiro heartbeat.
EOF

#!/usr/bin/env bash
# TASK-010 (BL-A) — wrapper shell que invoca lint_mql5.py.
# Usado em CI / pre-commit.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${HERE}/lint_mql5.py" "$@"

# Scripts do cam-cockpit

> **SO oficial: Windows 11** (dev + produção — ADR-012/014). Os `.ps1` são os
> scripts **canônicos**. Os `.sh` são **legado** da fase dev-Linux (defasada) —
> mantidos por ora, mas não são o caminho suportado.

| Script | Canônico | O que faz |
|---|---|---|
| `dev.ps1` | ✅ | Setup: instala deps, roda migrations uma vez e termina. |
| `backup.ps1` | ✅ | Backup do banco/dados. |
| `lint_mql5.py` | ✅ | Lint dos EAs MQL5 (multiplataforma — Python). |
| `dev.sh`, `backup.sh`, `lint_mql5.sh` | ⚠️ legado | Equivalentes Linux (fase dev-Linux, ADR-012 defasada). |
| `install_wine_mt5.sh` | 💀 morto | Wine/Linux falhou (2026-05-30). Não usar. |

> **Launcher** (subir banco+backend+frontend e manter rodando): `apps/start-cam.ps1`.

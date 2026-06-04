---
template: ADR
phase: ARCH
status: Superseded-in-part
---

# ADR-012 — Desenvolvimento em Linux, Produção em Windows; Código Cross-Platform

> 🪟 **ATUALIZAÇÃO 2026-05-30 (soft-stage, sem ADR HARD):** o MT5 sob Wine no Linux
> **falhou** → **desenvolvimento E produção agora em Windows 11** (single-SO). Wine
> eliminado; MT5 roda nativo; bridge ZeroMQ em `127.0.0.1`. A premissa original
> "dev Linux / prod Windows" deixa de valer, **mas as regras de código
> cross-platform (§2) seguem recomendadas** (pathlib, encoding utf-8, `.gitattributes`,
> DI de adapters) — protegem contra regressões e mantêm a opção de CI bi-SO.
> O broker é **MT5** (não Profit — ADR-001 também defasada nesse ponto).
> Runbook: [`../../runbooks/RUNBOOK-WINDOWS.md`](../../runbooks/RUNBOOK-WINDOWS.md).

> **Data:** 2026-05-24 · **Atualizada:** 2026-05-30 (reversão p/ Windows)
> **Status:** Superseded-in-part (premissa de SO revista; disciplina cross-platform mantida)
> **Lead:** Oscar · **Co-lead:** Vint (INFRA-ARCH)
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-012-dev-linux-producao-windows.md`

---

## 1. Contexto

Carlos desenvolve em Linux (eficiência de tooling, Docker nativo, Python toolchain mais limpa). O CaM opera em produção no Windows 11 porque o Profit/Nelogica é Windows-only (ADR-001).

Isso cria um ambiente bi-SO que precisa ser gerido com disciplina para evitar que código funcione em Linux e quebre no Windows (ou vice-versa).

Principais diferenças SO que afetam o projeto:
- **Paths:** Linux usa `/`; Windows usa `\` — uso de `pathlib.Path` resolve
- **Line endings:** `\n` vs `\r\n` — `.gitattributes` configura normalização
- **Process management:** `os.fork()` não existe no Windows — APScheduler e Uvicorn têm workers diferentes por SO
- **Docker:** Docker nativo em Linux vs. Docker Desktop + WSL2 em Windows
- **ProfitDLL (Fase F4+):** ctypes com DLL proprietária — Windows-only, sem equivalente em Linux

---

## 2. Decisão

Desenvolvimento primário em Linux; produção em Windows 11. Código escrito para ser **cross-platform** por convenção:

**Regras de código cross-platform:**
1. **Todos os caminhos de arquivo via `pathlib.Path`** — nunca `os.path.join()` manual com strings, nunca hardcode de `/` ou `\`
2. **Encoding explícito** em toda operação de arquivo: `open(path, encoding='utf-8')`
3. **Line endings** normalizados via `.gitattributes` (`* text=auto`)
4. **Variáveis de SO** em `.env` — ex: `DB_HOST=localhost` (idêntico nos dois SOs)
5. **Adapters de integração Profit injetados via DI** — em Linux usa `MockProfitAdapter`; em Windows usa `RealProfitAdapter` — sem `if sys.platform == 'win32'` espalhado pelo código de negócio
6. **Scripts de setup:** `scripts/dev.sh` (Linux) + `scripts/dev.ps1` (Windows PowerShell)

**CI/CD futuro (Fase 1+):** GitHub Actions com matriz `[ubuntu-latest, windows-latest]` para garantir que o build e os testes passam nos dois SOs.

**Docker em cada ambiente:**
- Linux dev: Docker Engine 29.1 nativo — `docker compose up -d`
- Windows prod: Docker Desktop + WSL2 — mesmo `docker-compose.yml`, mesma experiência

**Processo de integração:**
- Risk Engine, domain, strategies, backtest, fiscal, IA: desenvolvidos 100% em Linux (sem dependência do Profit)
- Integração Profit (profit_integration feature): desenvolvida em Linux com mock, testada em Windows com real

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Desenvolvimento exclusivo em Windows | Ferramentas Python (uv, ruff, pytest, profiling) funcionam em Windows mas com mais atrito; Docker Desktop tem overhead vs. Docker nativo; loops de feedback mais lentos |
| 2 | WSL2 em Windows para desenvolvimento | Válido, mas mistura SO e adiciona complexidade de filesystem cross-boundary; Carlos já tem ambiente Linux funcional |
| 3 | Container para todo o backend (inclusive em dev) | Overcomplica o desenvolvimento do backend — editar, lint e debug dentro de container tem mais fricção que Python nativo |

---

## 4. Consequências

### Positivas
- Desenvolvimento em Linux é mais rápido e limpo para toolchain Python
- Código cross-platform é naturalmente mais portável e robusto
- A maioria do backend (Risk Engine, backtest, fiscal) pode ser desenvolvida e testada sem Windows

### Negativas
- Requer disciplina de `pathlib` e encoding — um `os.path.join('/foo', 'bar')` hardcoded quebra no Windows
- Integração Profit (Fase F4+) requer teste final em Windows — não pode ser validada completamente em Linux
- CI/CD com matriz bi-SO adiciona tempo de build

### Neutras
- `.gitattributes` e `.editorconfig` resolvem a maioria dos problemas de line ending automaticamente

---

## 5. Custo de Reversão

**Baixo** — a disciplina de código cross-platform é uma convenção de estilo, não uma decisão de arquitetura irreversível. Pode ser relaxada (ou reforçada) sem impacto em features.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §8 (infraestrutura local)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §7
- ADRs relacionadas: ADR-001 (Profit Windows-only), ADR-008 (integração faseada com DI)

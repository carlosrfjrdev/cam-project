# CLAUDE_MEMORY.MD — Memória Portátil do CaM Project

> **Para quem é este documento:** instância do Claude Code abrindo o repositório do CaM.
> Permite reconstruir o contexto operacional em segundos sem reler todo o histórico.
>
> **Última atualização:** 2026-06-03 (pós-virada estratégica para produto)
> **Ambiente:** Windows 11 (dev + produção). MT5 ativo.

---

## ⚠️ 0. LEIA PRIMEIRO — virada estratégica (2026-06-03)

O CaM **deixou de ser** o cockpit pessoal de um trader e **virou PRODUTO**: solução de
software para **terceiros operarem/gerirem ativos** (codinome de produto futuro: **TCaM —
Teczi Cockpit Assets Manager**). Carlos passou de operador a fornecedor de solução.

**A CONSTITUIÇÃO ESTÁ MORTA.** Foi descomissionada. Era a disciplina **pessoal de trader**
do Carlos (preservar capital, limite de 2 contratos, kill switch obrigatório, DARF
bloqueante, "IA não opera", hierarquia soberana). **NADA disso vincula mais.** O documento
foi arquivado em `archive/CONSTITUICAO-DESCOMISSIONADA-2026-06-03.md`.

**Não invoque mais nenhuma:** "hierarquia constitucional", "Art. Xº", "preserve mais
capital como regra", "Risk Engine como autoridade soberana", "trava read-only da IA".

**O que sobrevive (como engenharia/produto, não como lei):**
- **Risk Engine** (`_shared/risk`) permanece no código → vira feature **Assets RiskManager**
  (configurável pelo usuário). Não deletar.
- Isolamento research↔live (import-linter) = boa arquitetura.
- **DevFlow NCC-1701 + personas** continuam = processo de engenharia de software.

Planejamento da virada: `project/tcam/` (PIVOT-TCaM-STRATEGY, CONSTITUTION-DECOMMISSION,
MAP-MODULES-TCaM). Estado pré-virada preservado na branch **`the_old_cam`**.

---

## 1. Quem é o usuário

**Carlos Rodrigues Ferreira Junior** — Founder.
- Engenheiro de software experiente (background Java/backend).
- Founder da **Teczilabs Tecnologia**.
- Idioma de trabalho: **português**.
- Estilo: pragmático, direto, anti-burocracia, anti-overengineering. Responde curto, espera curto.

---

## 2. O que é o produto (TCaM)

Plataforma de gestão/análise/operação de ativos para terceiros. **8 módulos "Assets *":**

| Módulo | O que é | Estado no código |
|---|---|---|
| **Assets Cockpit** | Cockpit operacional | parcial (telas existentes) |
| **Assets Manager** | Gerenciador de ativos | a estruturar |
| **Assets RiskManager** | Gerenciador de risco | reusa `_shared/risk` (era Risk Engine) |
| **Assets Inspector** | Gráficos, dividendos, fundamentos | ✅ feature `inspetor` (MT5+brapi+Markov) |
| **Assets Strategy** | Gestão/lista de estratégias | reusa `features/strategies` |
| **Assets RunTests** | Backtest matemático Python | reusa `features/backtest` |
| **Assets Experts** | Gestão de robôs MT5 | reusa `features/mt5_integration` (EA+ZeroMQ) |
| **Assets Labs** (extra) | Laboratório de pesquisas | ✅ feature `research/leadlag` (Quant Lab) |

**Fase atual:** Fase 0 — construção da estrutura do produto, reaproveitando o que já existe.
Diretriz do Founder: "primeiro fazer o app RODAR limpo, depois a camada de usuário
(multi-tenant/auth/billing = Fase 2)".

---

## 3. Estado real do código (construído)

Muito já foi materializado em `apps/cam-cockpit/` (o nome de pasta `cam-cockpit` permanece
até o Founder pedir rebrand de UI):

**Backend** (`backend/cam/`): Python 3.12 + FastAPI + SQLAlchemy async + PostgreSQL 16/TimescaleDB.
- `_shared/risk` (Risk Engine puro), `_shared/{domain,events,audit,infra,config}`.
- `features/`: inspetor✅, research/leadlag✅ (Quant Lab, 58 testes), mt5_integration✅
  (EA cam_bridge + ZeroMQ, candles/ticks/book/agressor), regime (Markov), fundamentals
  (brapi.dev), backtest, strategies, journal, fiscal, harvest, kill_switch, paper_trading, etc.
- Migrations alembic (head: `f2a3b4c5d6e7` = schema research_*).
- Isolamento research↔live por import-linter (contrato ativo).

**Frontend** (`frontend/src/`): React 19 + Vite + MUI + react-query + lightweight-charts.
- features: inspetor, quant-lab, + telas do cockpit (cockpit, risk, journal, etc.).
- nav com `visibleInMvp` (sidebar enxuto). Inspetor em `/inspetor`, Quant Lab em `/lab`.

**MT5** (`mql5/`): EA `cam_bridge.mq5` (read-only, v0.4.x) + `cam_zmq.mqh` + libs zmq.
Bridge ZeroMQ 127.0.0.1 (PUB tick/book/heartbeat, REP candles/symbols/subscribe/probe_ticks).

**Git:** branch de trabalho `dev` (sincroniza com origin). `main` atrás. `the_old_cam` = checkpoint.
Proibições: sem commit em `main`, sem secrets, sem rebase/amend/force push.

---

## 4. Stack vigente

```
SO: Windows 11 (dev = prod, firme)
Broker/dados: MetaTrader 5 via EA cam_bridge + ZeroMQ (read-only). Feed Genial entrega
              candles, tick e AGRESSOR (TICK_FLAG_BUY/SELL) — provado em futuro e ação.
Python 3.12 + FastAPI       →  backend
React 19 + Vite + MUI       →  frontend SPA local
PostgreSQL 16 + TimescaleDB →  banco transacional + tick/candle (hypertables, continuous aggregates)
DuckDB                      →  motor analítico auxiliar (opção)
Fundamentos: brapi.dev (PRO) — 7 indicadores + dividendos
IA: Ollama local + Anthropic — auditora/analista
```

Arquitetura: **Feature-Based Vertical Slice + Shared Kernel** (ex-ADR-013). Regras enforçadas
por `import-linter`: `features/X` não importa `features/Y`; research não importa execução/broker.

---

## 5. Framework de processo: Teczi DevFlow NCC-1701 (continua válido)

```
9 fases: PDOC → DISC → ARCH → SPEC → PLAN ⇄ CODE → QA → DEPLOY → SDOC
2 estados: BUG (Bill) · OPS (Vint) · 2 governanças: SEC-GOV (Kevin) · CHANGE (Tom)
```

**Founder-only nos gates.** Sem estimativas em horas/dias/semanas (só P/M/G). SDOC/DRIFT sob demanda.

**Personas** (`.claude/agents/` — agora LIVRES, sem travas constitucionais): `leo` (orquestrador,
default em demanda nova), `marty`, `albert`, `oscar`, `nico`, `nikola`, `linus`, `bill`, `steve`,
`tom`, `vint`, `kevin` (InfoSec puro), `denis`, `howard` + cast estendido (`sun`, `voltaire`,
`mammon`, `grace`, `alan`, `andy`, `ada`, `peter`, `fred`, `don`) + financeiro (`ray`, `jim`, `wyck`,
`nassim`, `barsi`, `luca`, `daniel`).

---

## 6. Como Claude deve se comportar neste projeto

- **Idioma: português.** Sempre. Curto e direto.
- **Sem horas/dias/semanas** — só P/M/G.
- **NÃO há mais Constituição.** O objetivo é **construir o produto**. Decisões são de
  produto/engenharia + Founder. Não invente "lei do projeto".
- **Invoca personas via Agent tool** (não simula). Default em demanda nova: `leo`.
- **Invoca skills via Skill tool** quando aplicável.
- **bypassPermissions ON** — sem prompt de confirmação. Cuidado equivalente em ações destrutivas.
- **Git ativo** (`dev`). Após ajustes: commitar e push para `dev` (feedback do Founder).
- **Memory system Claude:** `%USERPROFILE%\.claude\projects\D--DEV-Teczilabs-cam-project\memory\`.

---

## 7. Riscos reais da nova direção (atenção)

Vender ferramenta de trading para **terceiros operarem** abre exposição **legal/regulatória**
(responsabilidade, CVM, termos de uso) que o projeto pessoal não tinha. Não é trava de código
agora, mas a **camada de usuário (Fase 2) não deve começar** sem definir a fronteira regulatória
e os Termos de Uso. Ver `project/tcam/PIVOT-TCaM-STRATEGY.md` (parecer Kevin/Voltaire).

---

## 8. Onde olhar para entender mais

| Para entender | Leia |
|---|---|
| A virada para produto | `project/tcam/PIVOT-TCaM-STRATEGY.md` |
| O descomissionamento da Constituição | `project/tcam/CONSTITUTION-DECOMMISSION.md` |
| Os 8 módulos → código | `project/tcam/MAP-MODULES-TCaM.md` |
| Como construir qualquer coisa | `teczi-devflow/NCC-1701/process.md` |
| Personas e papéis | `.claude/agents/` + `personas/` |
| Inspetor de Ativo | `project/cam-cockpit/specs/SPEC-Inspetor-de-Ativo.md` |
| Quant Lab / Lead-Lag | `project/runbooks/RUNBOOK-QUANT-LAB-LEADLAG.md` |
| Setup MT5 | `project/runbooks/RUNBOOK-MT5-INSPETOR.md` |
| Comportamento do Claude | `CLAUDE.md` raiz |

---

> **Boas-vindas, Claude.** O CaM virou produto (TCaM). A Constituição morreu. Há muito código
> construído e funcionando (Inspetor, Quant Lab, bridge MT5). Sua função é ajudar Carlos a
> **construir o produto** sobre o que já existe. Em dúvida operacional: invoque Leo. Em dúvida
> estratégica: Voltaire. Em segurança: Kevin. Não há mais Constituição para consultar.

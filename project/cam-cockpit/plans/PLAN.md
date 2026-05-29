---
template: PLAN
phase: PLAN
status: Approved (letscode)
---

# PLAN — cam-cockpit · Cockpit Operacional Completo CaM

> **Data:** 2026-05-24
> **Status:** Draft — aguarda aprovação do Founder (`letscode = false`)
> **Produto:** CaM Cockpit
> **Lead:** Nico
> **Co-lead:** Albert (loop P/M/G)
> **Aprovador:** Founder (Carlos Rodrigues Ferreira Junior)

---

## 1. Resumo do plano

Construir o CaM Cockpit de dentro para fora: primeiro a fundação (estrutura do monorepo, Docker, schema), depois o Shared Kernel (Risk Engine com 17 validators e testes), depois as features core (journal, fiscal, harvest, kill switch, checklists), depois as integrações e canais externos (Profit F1/F2, Telegram, market data), depois o frontend completo com os 10 painéis, depois o backtest engine, depois a IA auditora, e por último o endurecimento de infraestrutura (backup, scripts Windows, audit trail completo) — sequência garantindo que nenhuma feature de ordem superior seja construída antes do alicerce constitucional que ela depende.

---

## 2. Referência de entrada

- SPEC: [`SPEC.md`](./SPEC.md) — Draft 2026-05-24, aguarda aprovação do Founder
- DAS vigente: [`DAS.md`](./DAS.md) — Draft 2026-05-24
- ADRs: ADR-001 a ADR-013 em [`adrs/`](./adrs/)
- Constituição: [`/CONSTITUICAO.md`](/CONSTITUICAO.md) — lei suprema (v1.0 consolidada)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md)

---

## 3. Avaliação de P/M/G

| Campo | Valor |
|---|---|
| Classe na SPEC | **G (Grande)** |
| Concordância de Nico | **Sim — classificação G confirmada** |
| Re-classificação proposta | Não aplicável |
| Loop com Albert | Não necessário — Nico concorda plenamente com o rationale de Albert: 11 módulos funcionais distintos, cada um com contratos independentes e critérios de aceite próprios, Risk Engine com 17 validators property-tested, 10 telas de frontend, 4 fases de integração Profit, decomposição em TASKs é mandatória |
| Decisão final | **G** — aguarda validação do Founder (gate formal) |

**Rationale de Nico:** A classificação G é a única tecnicamente defensável. O projeto inclui módulos com contratos separados, regras constitucionais distintas e superfícies de segurança diferenciadas (Risk Engine, kill switch, journal, IA). A tentativa de reduzir para M criaria TASKs indevidamente grandes para execução agêntica e perderia a granularidade necessária para que Nikola opere em isolamento por bloco. Manter G com decomposição flat em TASKs é o caminho correto.

---

## 4. Blocos e TASKs

> Regra de leitura: cada TASK é auto-contida para execução agêntica. Nikola lê a TASK + a seção correspondente da SPEC + o README do módulo (quando existir) e executa sem precisar de contexto de outras TASKs. Dependências explicitam apenas pré-condições estruturais.
>
> Gate Founder: demandas que tocam Risk Engine, kill switch, journal, provisão fiscal e autoridade da IA acionam SEC-GOV (Kevin). Registrado explicitamente nas TASKs relevantes abaixo.

---

### Bloco A — Fundação

Infra local, estrutura do monorepo, tooling, schema de banco e Docker.

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-A01 | Criar estrutura do monorepo `apps/cam-cockpit/` conforme ADR-011 e DAS §8 | Diretórios `backend/`, `frontend/`, `ntsl/`, `scripts/`, `docker-compose.yml` criados; `pyproject.toml` com uv + ruff + pytest + import-linter; `package.json` React 19 + Vite + MUI + TypeScript; `.gitignore` incluindo `.env`, `*.jsonl`, `cam-backups/`; `.env.example` documentando todas as variáveis | A | — |
| T-A02 | Configurar Docker Compose com TimescaleDB 16 e Redis (opcional) | `docker-compose.yml` funcional com `timescale/timescaledb:latest-pg16` na porta 5432; `docker compose up -d` sobe em Linux limpo; extensão TimescaleDB verificada com `SELECT default_version FROM pg_available_extensions WHERE name = 'timescaledb'`; CA11.1 satisfeito | A | T-A01 |
| T-A03 | Criar estrutura do Shared Kernel `cam/_shared/` | Pacotes `risk/`, `domain/`, `events/`, `audit/`, `infra/`, `config/` com `__init__.py`; `domain/` contém primitivas `Money`, `ContractCount`, `Phase`, `AssetType`, `Direction`, `OpenPosition`; `infra/` contém session factory SQLAlchemy 2.0 com psycopg3; `config/` carrega `.env` via pydantic-settings | A | T-A01 |
| T-A04 | Criar estrutura de features `cam/features/` com stubs de todos os módulos | Pastas: `journal/`, `fiscal/`, `ledger/`, `harvest/`, `strategies/`, `backtest/`, `paper_trading/`, `profit_integration/`, `market_data/`, `kill_switch/`, `checklists/`, `notifications/`, `ai_analyst/`, `constitution/`; cada uma com `README.md` (propósito, I/O, eventos, artigos constitucionais, anti-padrões), `domain.py`, `schemas.py`, `repository.py`, `service.py`, `routes.py`, `events.py`, `tests/__init__.py` em branco | A | T-A03 |
| T-A05 | Criar `cam/api/` — FastAPI Composer base | `main.py` instancia `FastAPI`; `lifespan.py` gerencia startup/shutdown (banco, event bus); `middleware.py` com CORS localhost e structlog; `websocket.py` stub para P&L live; app sobe com `uvicorn cam.api.main:app` sem erro; health check `GET /api/v1/health` retorna `{"status": "ok"}` | A | T-A04 |
| T-A06 | Configurar import-linter para enforçar regras ADR-013 | `setup.cfg` ou `pyproject.toml` com contratos: `features/X` nunca importa `features/Y`; `_shared/risk/` importa apenas stdlib; CI local roda `lint-imports` sem violação em projeto base | A | T-A04 |
| T-A07 | Criar migrations Alembic — schema completo Bloco A | Migration inicial com: `CREATE EXTENSION IF NOT EXISTS timescaledb`; tabelas operacionais (`cam_orders`, `cam_positions`, `cam_trades`, `cam_journal_entries`, `cam_risk_decisions`, `cam_violations`, `cam_kill_switch_events`, `cam_checklist_pre_market`, `cam_checklist_post_market`); tabelas constitucionais (`cam_constitution_versions`, `cam_pov_versions`, `cam_phase_history`); `alembic upgrade head` em banco limpo sem erro; CA11.2 parcialmente satisfeito | A | T-A02, T-A03 |
| T-A08 | Criar migrations Alembic — schema fiscal, patrimonial e backtest | Tabelas: `cam_fiscal_apuration`, `cam_darf_history`, `cam_loss_compensation_ledger`, `cam_bucket_transactions`, `cam_harvest_history`; tabelas backtest: `cam_backtest_runs`, `cam_backtest_trades`, `cam_backtest_equity_curve`, `cam_pattern_studies`; `alembic upgrade head` consolida todas as migrations sem erro | A | T-A07 |
| T-A09 | Criar migrations Alembic — hypertables TimescaleDB e continuous aggregates | Hypertables: `cam_market_ticks` (chunk 1 dia, compressão >7 dias), `cam_market_book_snapshots` (chunk 1 dia, compressão >3 dias); continuous aggregates: `cam_candles_1s`, `cam_candles_5s`, `cam_candles_1m`, `cam_candles_5m`, `cam_candles_15m`, `cam_candles_1h`, `cam_candles_1d`; CA11.2 completamente satisfeito | A | T-A08 |
| T-A10 | Configurar pré-commit hook anti-secrets | Hook detecta padrões de API key, token, senha em stage; `.env` não pode ser commitado; teste: `git add .env` + `git commit` → commit bloqueado com mensagem clara; CA11.4 satisfeito | A | T-A01 |
| T-A11 | Criar `scripts/dev.sh` — setup Linux | Script instala dependências Python via uv, cria banco, roda migrations, valida `docker compose up -d`; execução em Linux limpo completa sem erro manual; documentação de pré-requisitos no cabeçalho do script | A | T-A09, T-A10 |

---

### Bloco B — Shared Kernel · Risk Engine

Risk Engine Pure Python com todos os 17 validators constitucionais e property-based tests. **Gate SEC-GOV (Kevin): toda TASK deste bloco aciona revisão de segurança em CODE e QA-SEC obrigatório.**

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-B01 | Criar estrutura base do Risk Engine `cam/_shared/risk/` | `engine.py` com dataclasses `OrderCandidate`, `RiskContext`, `Approved`, `Rejected`; função `validate(candidate, context) -> RiskDecision` com pipeline vazio que retorna `Approved`; módulo `validators/` com `__init__.py`; zero I/O confirmado (sem import de `sqlalchemy`, `httpx`, `aiohttp`, ou qualquer lib I/O); CA1.9 (cenário trivial) satisfeito | B | T-A03 |
| T-B02 | Implementar validators constitucionais — Grupo 1: guardas de estado | Validators: `kill_switch_active_check`, `pre_market_checklist_check`, `post_market_checklist_check`, `tax_compliance_check`, `phase_authorization_check`; executados na ordem exata da SPEC R1.06 (posições 1–5); cada validator retorna `Approved` ou `Rejected(reason, validator)`; CA1.5, CA1.6, CA1.12, CA1.13 satisfeitos; testes unitários por validator (100% cobertura neste grupo) | B | T-B01 |
| T-B03 | Implementar validators constitucionais — Grupo 2: limites de contratos e posição | Validators: `max_contracts_check` (Art. 11º — INTOCÁVEL, hardcoded ≤2 WIN / ≤2 WDO, não sobrescrevível por POV), `phase_contracts_check`, `simultaneous_position_check`; executados nas posições 6–8 da SPEC; CA1.1, CA1.2, CA1.10 satisfeitos; testes unitários por validator | B | T-B02 |
| T-B04 | Implementar validators constitucionais — Grupo 3: limites de P&L | Validators: `daily_loss_limit_check` (3% do capital), `weekly_loss_limit_check` (7%), `monthly_loss_limit_check` (15% — congela fase), `gain_lock_check` (2% — encerra dia); parâmetros de limites lidos da POV vigente, exceto limites invioláveis; executados nas posições 9–12; CA1.3, CA1.4 satisfeitos; testes unitários por validator | B | T-B03 |
| T-B05 | Implementar validators constitucionais — Grupo 4: regras operacionais | Validators: `daily_operations_count_check` (max 3 Fases 1-2, max 5 Fases 3-4), `martingale_check` (Art. 13º — proíbe aumento após loss), `trading_window_check` (janelas vedadas: 15min pós-abertura, 10min pré-fechamento), `setup_a_plus_check` (2 contratos apenas Fase 4+ com Setup A+), `circuit_breaker_check` (configurável, padrão off); executados nas posições 13–17; CA1.7, CA1.8, CA1.11 satisfeitos; testes unitários por validator | B | T-B04 |
| T-B06 | Implementar pipeline completo e registrar decisões em `cam_risk_decisions` | `validate()` executa os 17 validators na ordem exata da SPEC R1.06 (primeiro `Rejected` termina o pipeline); resultado registrado em `cam_risk_decisions` com timestamp e motivo (uso mínimo de I/O: apenas o chamador externo persiste — o Risk Engine em si permanece Pure Python, o registro ocorre no service da feature que chama o engine); todos os CAs 1.1–1.13 satisfeitos em testes de integração | B | T-B05 |
| T-B07 | Property-based tests com Hypothesis — cobertura do Risk Engine | Suite Hypothesis com 10.000+ cenários gerados: nunca `Approved` quando viola Art. 11º (CA1.14); fuzzing de `RiskContext` com valores extremos; cobertura total do `cam/_shared/risk/` ≥ 80% (`pytest --cov`); testes rodam em < 60 segundos; relatório de cobertura salvo como artefato | B | T-B06 |

---

### Bloco C — Features Core

Journal, Ledger Fiscal, Harvest/Ledger de Capital, Kill Switch e Checklists. **Features que tocam journal, fiscal, kill switch e provisão: gate SEC-GOV (Kevin) em CODE e QA-SEC.**

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-C01 | Implementar feature `kill_switch` | `domain.py` com `KillSwitchEvent`, `KillSwitchState`; `repository.py` com persistência em `cam_kill_switch_events`; `service.py` com métodos `activate(reason)`, `deactivate()`, `is_active() -> bool`; `routes.py` com `POST /api/v1/kill-switch/activate`, `POST /api/v1/kill-switch/deactivate`, `GET /api/v1/kill-switch/status`; desativação requer confirmação explícita (campo `confirm: true` no body); `events.py` publica `KillSwitchActivated`, `KillSwitchDeactivated`; testes unitários e de integração; fluxo DAS §4.4 implementado | C | T-B06, T-A07 |
| T-C02 | Implementar feature `checklists` (pré e pós mercado) | `domain.py` com `PreMarketChecklist`, `PostMarketChecklist` e todos os itens obrigatórios da SPEC R10.03 e R10.04; `repository.py` com persistência em `cam_checklist_pre_market` e `cam_checklist_post_market`; `service.py`: checklist não salvo sem todos os itens obrigatórios; `routes.py` com endpoints de criação e consulta por data; CA10.1–CA10.4 satisfeitos em testes de integração | C | T-A07 |
| T-C03 | Implementar feature `journal` — domínio e persistência | `domain.py` com `JournalEntry` (todos os campos SPEC §6.2), `JournalCorrection`, `JournalSource`; `repository.py` com persistência em `cam_journal_entries` (sem UPDATE nem DELETE — imutabilidade garantida em nível de repository); cálculo de `resultado_liquido = resultado_bruto - custos - imposto_provisionado`; cálculo de `imposto_provisionado`: 20% do bruto quando positivo, 0 quando negativo; CA2.5, CA2.6 satisfeitos | C | T-A07 |
| T-C04 | Implementar feature `journal` — service, events e routes | `service.py` valida todos os campos obrigatórios (SPEC R2.05) e rejeita entrada com campo ausente; publica `JournalEntryCreated` após persistência; journal duplo: persiste em `cam_journal_entries` E appenda em `~/.cam/journal/YYYY-MM-DD.jsonl` (CA11.3); `routes.py` com todos os endpoints SPEC §6.3; CA2.1–CA2.4 satisfeitos | C | T-C03, T-C01 |
| T-C05 | Implementar relatórios e exportação do journal | `service.py` com métodos para relatórios: diário, semanal, mensal, por estratégia, por ativo, por aderência (SPEC R2.10); endpoint `GET /api/v1/journal/reports/{tipo}`; exportação `GET /api/v1/journal/export` gera CSV/JSON; CA2.7, CA2.8 satisfeitos (importação CSV implementada como stub — será completada em T-D02) | C | T-C04 |
| T-C06 | Implementar feature `fiscal` — domínio e cálculo | `domain.py` com `FiscalApuration`, `Darf`, `DarfStatus` (PENDING/PAID/OVERDUE), `LossCompensation`; `service.py`: apuração mensal (SPEC R3.01–R3.09): IR Day Trade 20%, IRRF 1% como antecipação, compensação de prejuízo acumulado; lógica de OVERDUE (não paga após vencimento → `tax_compliance = False`); CA3.1–CA3.6 satisfeitos | C | T-A08, T-C04 |
| T-C07 | Implementar feature `fiscal` — event consumer, routes e alertas | Handler de `JournalEntryCreated`: atualiza provisão fiscal em tempo real (SPEC R3.08); job de final de mês (APScheduler): gera DARF PENDING; `routes.py` com todos os endpoints SPEC §7.2; `PATCH /api/v1/fiscal/darfs/{id}/mark-paid` atualiza status + dispara cálculo de harvest (via evento); verificação de OVERDUE executada ao construir `RiskContext`; testes de integração end-to-end | C | T-C06 |
| T-C08 | Implementar feature `ledger` e `harvest` — domínio e cálculo | `domain.py` com `Bucket` (Derivativo, Buffer Operacional, Carteira Hard), `BucketTransaction`, `HarvestProposal`, `HarvestExecution`; `service.py`: lógica dos 3 buckets (SPEC R4.01–R4.07): 60% Carteira Hard / 40% Buffer até linha de base R$ 1.000; sangria automática quando Bucket Derivativo ≥ R$ 4.500; proposta gerada sem auto-executar (gate Founder obrigatório: R4.07); CA4.1–CA4.5 satisfeitos | C | T-A08 |
| T-C09 | Implementar feature `harvest` — event consumer e routes | Handler de `DarfPaid` (ou equivalente pós-pagamento): recalcula snapshot de buckets; `routes.py` com todos os endpoints SPEC §8.2; `POST /api/v1/harvest/execute` exige confirmação explícita do Founder (campo `founder_approved: true`); transações registradas em `cam_bucket_transactions`; testes de integração com cenário de sangria | C | T-C08, T-C07 |

---

### Bloco D — Integrações

Profit F1/F2, Telegram (canal de alerta independente) e market data. **Credenciais: nunca no código — sempre via `.env`. Gate SEC-GOV se tela ou endpoint de configuração for criado.**

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-D01 | Implementar feature `profit_integration` — Fase F1 (zero integração) | `service.py` com método `validate_intention(order_candidate, risk_context) -> RiskDecision` que chama Risk Engine e retorna resultado; nenhum código de envio de ordem (F1 é manual); `routes.py` com `POST /api/v1/profit/validate-intention` para uso do frontend antes de Carlos operar no Profit; CA6.2 (formato inválido) base implementada; ADR-008 respeitada | D | T-B06 |
| T-D02 | Implementar importador CSV do Profit — Fase F2 | `service.py` com método `import_csv(file) -> ImportResult`; parser do formato CSV padrão do Profit; detecção de duplicatas por hash de conteúdo (SPEC R6.03); criação de `JournalEntry` por trade importado via `journal/service.py`; `routes.py` com `POST /api/v1/journal/import-csv`; CA6.1 satisfeito (10 trades, reimportação = 0 duplicatas) | D | T-C05 |
| T-D03 | Implementar reconciliação F2 — journal manual × CSV | `service.py` com método `reconcile(date) -> ReconciliationReport`: compara entries manuais × entries importados; matching por horário/ativo/contratos; exibe pares prováveis para confirmação do operador; `routes.py` com `GET /api/v1/profit/reconciliation/{date}`; CA6.3 satisfeito | D | T-D02 |
| T-D04 | Implementar feature `notifications` — Telegram Bot | `service.py` com envio de mensagens via `python-telegram-bot`; token e chat_id lidos de `.env` (SPEC R9.04); retry exponencial para alertas críticos (SPEC R9.02); modo degradado se token não configurado (SPEC R9.04 + CA9.4); handlers de eventos: `KillSwitchActivated`, `DailyLossLimitReached`, `WeeklyLossLimitReached`, `MonthlyLossLimitReached`, `GainLockReached`, `DarfOverdue`, `TechnicalFailureWithOpenPosition`; CA9.1–CA9.4 satisfeitos; ADR-010 respeitada | D | T-C01, T-C07 |
| T-D05 | Implementar feature `market_data` — ingestão de ticks na TimescaleDB | `domain.py` com `MarketTick`, `BookSnapshot`; `repository.py` com INSERT em `cam_market_ticks` e `cam_market_book_snapshots`; `service.py` com método `ingest_ticks(source_file) -> IngestResult` para carga de CSV/Parquet histórico; DuckDB como motor de leitura exploratória de arquivos antes de carregar no Timescale (SPEC R7.09 + ADR-005); `routes.py` com `POST /api/v1/market-data/ingest` e `GET /api/v1/market-data/status` | D | T-A09 |

---

### Bloco E — Frontend Operacional

SPA React 19 + Vite + MUI com os 10 painéis obrigatórios. Kill switch visível em toda tela. P&L sempre líquido. **Nenhum campo editável do Risk Engine na UI (CA5.4 = regra constitucional Art. 35º).**

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-E01 | Configurar frontend base — estrutura, router, providers e API client | `vite.config.ts` com proxy para backend localhost; `src/app/` com router (React Router v7), providers (MUI Theme, QueryClient, WebSocket context); `src/api/` com client gerado de OpenAPI ou typed fetch; `src/_shared/` com componentes transversais: `KillSwitchButton` (persistente em toda tela — CA5.1), `RiskEngineStatusBanner`, `PnlDisplay` (sempre exibe bruto + líquido — CA5.2); layout base com header e navegação | E | T-A05 |
| T-E02 | Implementar painel Cockpit Live | `src/features/cockpit/`: P&L líquido em tempo real via WebSocket; gauges de limites (diário, semanal, mensal); posições abertas; botão kill switch com confirmação dupla (CA5.3); status do Risk Engine no header; banner vermelho persistente quando kill switch ativo (CA5.3); dados bruto + líquido sempre visíveis (CA5.2); integra com `GET /api/v1/risk/status` e WebSocket P&L | E | T-E01, T-C01, T-B06 |
| T-E03 | Implementar painel Journal | `src/features/journal/`: listagem de entries com filtros (data, ativo, estratégia, aderência); formulário de criação manual (todos os campos SPEC §6.2, campos opcionais indicados); botão de importação CSV com feedback de resultado; link para relatórios; resultado bruto + líquido sempre exibidos juntos (CA5.2); integra com endpoints SPEC §6.3 | E | T-E01, T-C05 |
| T-E04 | Implementar painel Ledger Fiscal | `src/features/fiscal/`: apuração mensal com resultado líquido (nunca apenas bruto — CA5.6 e Art. 25º); listagem de DARFs com status (PENDING / PAID / OVERDUE); alerta visual para DARF OVERDUE no header e no painel (CA5.6); saldo compensável explícito (SPEC R3.07); botão "Marcar como paga"; integra com endpoints SPEC §7.2 | E | T-E01, T-C07 |
| T-E05 | Implementar painel Harvest | `src/features/harvest/`: proposta de distribuição com valores calculados por bucket; histórico de harvests executados; saldos atuais dos 3 buckets; botão "Executar Harvest" com confirmação explícita (gate Founder — SPEC R4.07); integra com endpoints SPEC §8.2 | E | T-E01, T-C09 |
| T-E06 | Implementar painel Risk Console | `src/features/risk-console/`: POV vigente exibida como read-only (CA5.4 — sem campo editável); log de decisões do Risk Engine (`cam_risk_decisions`) com filtros; audit trail de ativações do kill switch; indicador de fase atual; integra com `GET /api/v1/risk/decisions` e `GET /api/v1/risk/pov` | E | T-E01, T-B06, T-C01 |
| T-E07 | Implementar painel Constituição (read-only) | `src/features/constitution/`: exibição do texto da Constituição em Markdown (SPEC R5.07 — sem edição inline); histórico de versões em `cam_constitution_versions`; formulário de proposta de emenda (apenas para registro — sem auto-execução); integra com `GET /api/v1/constitution/current` e `GET /api/v1/constitution/versions` | E | T-E01 |
| T-E08 | Implementar painel Configurações | `src/features/settings/`: campos para token Telegram, chat_id, paths de CSV do Profit — sem parâmetros do Risk Engine editáveis (CA5.4); status de conexão com banco e serviços; integra com `GET /api/v1/settings` e `PATCH /api/v1/settings`; campos sensíveis nunca persistem no frontend (apenas enviados ao backend para salvar em `.env` ou DB de config) | E | T-E01, T-D04 |
| T-E09 | Implementar painel Paper Trading | `src/features/paper-trading/`: mesma UI do Cockpit Live com badge "SIMULACAO" grande e vermelho visível em toda a tela (CA5.5 — nunca confundível com live); todas as regras do Risk Engine ativas; integra com `POST /api/v1/paper-trading/simulate-operation` | E | T-E01, T-E02 |
| T-E10 | Implementar painel Carteira Hard | `src/features/carteira-hard/`: snapshot patrimonial atual (saldo do bucket Carteira Hard); histórico de entradas via harvest; placeholder para dividendos (ativos externos fora do escopo do cockpit — apenas registro manual); integra com `GET /api/v1/ledger/carteira-hard/snapshot` e `GET /api/v1/harvest/history` | E | T-E01, T-C09 |
| T-E11 | Implementar painel Backtest | `src/features/backtest/`: formulário de configuração (estratégia, janela de datas, fase simulada — sem campo para desligar Risk Engine, CA7.5); botão executar; exibição do relatório com as 7 métricas obrigatórias (SPEC R7.06); equity curve; modo walk-forward com resultado separado por janela (CA7.4); integra com endpoints Bloco F | E | T-E01 |

---

### Bloco F — Backtest e Research

Backtest engine com o mesmo Risk Engine do live. DuckDB para research exploratório.

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-F01 | Implementar feature `backtest` — domínio e simulador | `domain.py` com `BacktestConfig`, `BacktestRun`, `BacktestTrade`, `BacktestMetrics`; `service.py` com simulador tick-a-tick: carrega `cam_market_ticks`, instancia o MESMO Risk Engine com fase simulada, executa estratégia; cada trade simulado passa pelo Risk Engine (SPEC R7.01 — DRY constitucional); custo de corretagem incluído obrigatoriamente (SPEC R7.03); IR 20% provisionado sobre resultado simulado (SPEC R7.04); impossível rodar com Risk Engine "desligado" (CA7.5) | F | T-B06, T-D05 |
| T-F02 | Implementar métricas e walk-forward do backtest | `service.py`: calcular P&L total, Sharpe ratio, max drawdown, win rate, fator de lucro, distribuição de resultados, número de operações, aderência às regras (SPEC R7.06); walk-forward: janela A de otimização, janela B de validação out-of-sample (SPEC R7.07, CA7.4); resultados persistidos em `cam_backtest_runs` + `cam_backtest_trades`; CA7.1–CA7.4 satisfeitos | F | T-F01 |
| T-F03 | Implementar routes do backtest e integração com DuckDB | `routes.py` com: `POST /api/v1/backtest/run` (inicia simulação), `GET /api/v1/backtest/runs` (histórico), `GET /api/v1/backtest/runs/{id}` (detalhe + métricas), `GET /api/v1/backtest/runs/{id}/equity-curve`; endpoint de research DuckDB `POST /api/v1/backtest/research/query` (query read-only sobre CSV/Parquet — ADR-005); DuckDB nunca grava em tabelas do cockpit live (SPEC R7.09) | F | T-F02 |

---

### Bloco G — IA Auditora

Job assíncrono pós-mercado, read-only, sem autoridade de execução. **Gate SEC-GOV (Kevin) obrigatório: Arts. 34º–36º são não-negociáveis. Verificação pós-análise de conteúdo proibido é mandatória.**

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-G01 | Implementar feature `ai_analyst` — processo isolado e acesso read-only | `service.py` como job CLI/scheduler isolado do backend live (SPEC R8.03); acesso apenas read-only: `cam_journal_entries`, `cam_risk_decisions`, `cam_violations`; nenhum import de endpoint de escrita ou parametrização; prompt inclui explicitamente instrução de restrição (SPEC R8.09): "Você é uma IA auditora. Não pode recomendar trades, não pode sugerir contornar regras de risco, não pode emitir opinião sobre oportunidades de mercado."; SPEC R8.01–R8.03 implementadas | G | T-C05, T-B07 |
| T-G02 | Implementar providers de IA (Ollama local e Anthropic API) | Provider Ollama (default para dados sensíveis — SPEC R8.05); provider Anthropic API (dados anonimizados — sem nome do operador, sem CPF, sem valores absolutos de capital quando desnecessários — SPEC R8.04); fallback automático: Anthropic indisponível → Ollama local (CA8.4); verificação pós-análise: detecta conteúdo proibido (recomendação de trade, justificativa de exceção constitucional) → descarta análise + log de violação (CA8.2, CA8.3); CA8.5: auditoria de dados enviados | G | T-G01, T-D04 |
| T-G03 | Implementar scheduler e persistência da análise IA | APScheduler dispara job pós-fechamento do pregão; análise salva em banco (tabela `cam_ai_analysis`); enviada via Telegram ao operador (SPEC R8.06); CA8.1 satisfeito; migration para `cam_ai_analysis` adicionada (extend T-A08); testes: job roda sem erro, análise salva, Telegram notificado | G | T-G02 |

---

### Bloco H — Infraestrutura Avançada

Backup, scripts Windows, paper trading backend, audit trail completo e feature `constitution`.

| # | TASK | Saída esperada | Bloco | Depende de |
|---|---|---|---|---|
| T-H01 | Implementar paper trading backend | `cam/features/paper_trading/service.py`: mesma lógica de validação do live (Risk Engine ativo), porém não persiste em `cam_journal_entries` de produção — persiste em `cam_paper_trades`; todas as regras constitucionais ativas; badge "PAPER" no contexto; `routes.py` com endpoints de simulação; migration para `cam_paper_trades`; CA5.5 (nunca confundível com live) garantido por separação de tabelas | H | T-B06, T-C02 |
| T-H02 | Implementar feature `constitution` — backend | `domain.py` com `ConstitutionVersion`, `AmendmentProposal`; `repository.py` com leitura de `cam_constitution_versions`; `service.py` com método de proposta de emenda (apenas registra — sem auto-execução); `routes.py` com `GET /api/v1/constitution/current`, `GET /api/v1/constitution/versions`, `POST /api/v1/constitution/amendments` (proposta — gate Founder para execução real); SPEC R5.07 (read-only na UI) garantida por ausência de endpoint de edição direta | H | T-A07 |
| T-H03 | Criar `scripts/dev.ps1` — setup Windows (PowerShell) | Equivalente PowerShell do `dev.sh`: instala dependências Python via uv, Docker Desktop check, cria banco, roda migrations; valida `docker compose up -d` no Docker Desktop com WSL2; documentação de pré-requisitos no cabeçalho; ADR-012 (cross-platform) satisfeita | H | T-A11 |
| T-H04 | Implementar backup automatizado — Linux e Windows | `scripts/backup.sh`: `pg_dump` diário via cron Linux; `scripts/backup.ps1`: equivalente via Task Scheduler Windows (SPEC R11.04); `rclone` sync noturno para Google Drive configurável (SPEC R11.05); SPEC R11.06 (journal duplo JSONL) já implementada em T-C04 — validar que backup inclui diretório `~/.cam/journal/` | H | T-A11, T-H03 |
| T-H05 | Implementar audit trail completo — structlog transversal | `cam/_shared/audit/logger.py` com structlog configurado (JSON lines); toda decisão do Risk Engine registrada (T-B06 já persiste em `cam_risk_decisions` — aqui adicionar log estruturado paralelo); toda ativação/desativação de kill switch logada; toda operação de harvest logada; toda análise IA logada; logs rotativos configurados (não crescem indefinidamente) | H | T-C01, T-C09, T-G03 |
| T-H06 | Validação end-to-end — critérios de gate Fase 0 (SPEC §17) | Testes de integração cobrindo os 8 critérios de gate: (1) fluxo completo checklist → Risk Engine → Journal → Fiscal → Harvest; (2) cobertura Risk Engine ≥ 80%; (3) kill switch ativado → operação bloqueada → Telegram alertado → desativado; (4) backtest 100 trades com todos validators ativos; (5) 10 operações paper trading completas; (6) DARF overdue → operação bloqueada; (7) journal duplo (banco + JSONL); (8) zero credenciais no histórico git | H | T-B07, T-C09, T-F02, T-G03, T-H01, T-H05 |

---

## 5. Dependências Externas

| Dependência | Onde necessária | Quando necessária |
|---|---|---|
| Docker Engine instalado (Linux) | T-A02, T-A11 | Antes de T-A02 |
| Docker Desktop com WSL2 (Windows) | T-H03 | Antes de T-H03 |
| Python 3.12 + uv instalados | T-A01, T-A11 | Antes de T-A01 |
| Node.js 20+ + pnpm/npm instalados | T-E01 | Antes de T-E01 |
| Profit Pro ou Ultra instalado (Windows) | T-D02 (teste de CSV real), T-H03 | Antes de T-D02 (só para teste de formato real) |
| Telegram Bot criado (BotFather) + token e chat_id | T-D04 | Antes de T-D04 (modo degradado funciona sem) |
| Anthropic API Key (opcional) | T-G02 | Antes de T-G02 (Ollama é o default; chave só para provider alternativo) |
| Ollama instalado localmente | T-G02 | Antes de T-G02 |
| rclone configurado com Google Drive | T-H04 | Antes de T-H04 (backup é independente do cockpit) |
| Hypothesis instalada (via pyproject.toml) | T-B07 | Antes de T-B07 — inclusa nas deps do projeto |

---

## 6. Riscos Identificados

| Risco | Impacto | Mitigação |
|---|---|---|
| **Risk Engine complexity** — Pure Python com Hypothesis exige disciplina de design; validators em cadeia com estado implícito podem produzir comportamento inesperado | Alto (constitucional) | Bloco B é totalmente prioritário antes de qualquer feature que use o engine; cada validator tem 100% de cobertura unitária antes de T-B06 integrar o pipeline |
| **Integração Profit CSV** — formato real do CSV do Profit pode divergir do assumido na SPEC F2 | Médio | T-D02 deve ser testada com CSV real do Profit antes de ser considerada completa; se formato divergir, uma TASK de ajuste de parser é aberta como BUG fast-track |
| **Cross-platform** — desenvolvimento Linux, produção Windows; Python nativo e Docker Desktop com WSL2 têm comportamentos diferentes | Médio | ADR-012 governa; T-H03 cria o script Windows cedo; testes de integração devem rodar no Windows antes de qualquer gate de Fase 1 |
| **Property-based tests performance** — 10.000 cenários Hypothesis podem ser lentos em CI local | Baixo | Perfil em T-B07; se necessário, reduzir exemplos para CI rápido e rodar 10.000 em execução noturna manual |
| **asyncio.Queue como event bus** — sem persistência; se o backend reiniciar com eventos pendentes, eles se perdem | Médio | Aceitável para Fase 0 (1 operador local); Redis é a alternativa documentada nas Não-Decisões do DAS; acionável em Fase 1 se problema real aparecer |
| **IA com conteúdo proibido** — análise pode gerar recomendação de trade ou justificativa de exceção constitucional | Alto (Arts. 34–36) | T-G02 implementa verificação pós-análise obrigatória antes de enviar qualquer resultado; análise com conteúdo proibido é descartada e logada como violação |
| **DARF overdue não detectada** — se o job de final de mês falhar, DARF não é gerada e `tax_compliance` permanece `True` incorretamente | Alto (Art. 26º) | T-C07 implementa verificação de OVERDUE no build do `RiskContext`; job de final de mês tem log estruturado e alerta Telegram em caso de falha |

---

## 7. Reuso Aplicado

| Decisão/Artefato | Onde aplicado no PLAN |
|---|---|
| ADR-001 — Profit como plataforma de execução | T-D01, T-D02, T-D03: Profit é externo gerido; CaM valida intenção, não envia ordem |
| ADR-002 — Python 3.12 + FastAPI | Toda TASK de backend (T-A03 em diante) |
| ADR-003 — React 19 + Vite + MUI, sem Next.js | Toda TASK de frontend (T-E01 em diante) |
| ADR-004 — PostgreSQL 16 + TimescaleDB desde Fase 0 | T-A07, T-A08, T-A09 (schema completo desde o início) |
| ADR-005 — DuckDB como motor analítico auxiliar read-only | T-D05, T-F03 (research e ingestão exploratória) |
| ADR-006 — IA sem autoridade operacional | T-G01, T-G02, T-G03 (processo isolado, read-only, verificação de conteúdo proibido) |
| ADR-007 — Risk Engine Pure Python no Shared Kernel | T-B01 a T-B07 (Zero I/O Policy validada com import-linter em T-A06) |
| ADR-008 — Integração Profit faseada F1→F5 | T-D01 (F1), T-D02 e T-D03 (F2); F3+ fora do escopo Fase 0 |
| ADR-009 — Risk Engine espelhado em NTSL como 2ª linha | Futuro; pasta `ntsl/risk_mirror/` criada em T-A01 como estrutura, conteúdo é Fase 1+ |
| ADR-010 — Telegram como canal externo independente | T-D04 (falha no Telegram não afeta cockpit — SPEC R9.03) |
| ADR-011 — Monorepo único `apps/cam-cockpit/` no MVP | T-A01 (estrutura de diretórios) |
| ADR-012 — Dev Linux, produção Windows | T-A11 (dev.sh), T-H03 (dev.ps1), T-H06 (validação Windows) |
| ADR-013 — Vertical Slice + Shared Kernel mínimo | T-A03 (Shared Kernel), T-A04 (features stub), T-A06 (import-linter) |
| SPEC.md — contrato único de módulo | Nikola usa a seção da SPEC correspondente a cada TASK como contrato de implementação |
| DAS.md — mapa arquitetural | Referência obrigatória para todas as TASKs de infra, integração e composição (T-A05, T-D01 a T-D05, T-H05) |

---

## 8. `letscode`

| Campo | Valor |
|---|---|
| Status | **`true`** |
| Aprovado por | Founder (Carlos Rodrigues Ferreira Junior) em 2026-05-24 |
| Motivo | — |

> [x] Carlos Rodrigues Ferreira Junior aprova o PLAN e libera CODE — Data: 24/05/2026
>
> `letscode = true` — iniciar por TASK: **T-A01**
>
> **Instrução adicional do Founder:** TDD First — Nikola escreve testes antes de codar (Red → Green → Refactor). Os testes são o modelo mental da TASK.

**Proof Pack:** Classificação G — obrigatório. Será produzido após CODE + QA de cada bloco, antes de DEPLOY. Formato: PROOF-PACK por bloco ou consolidado ao final da Fase 0 (decisão do Founder).

---

## 9. Pontos de Atenção ao Founder (antes de `letscode`)

1. **SEC-GOV obrigatório nas TASKs do Bloco B e C** — Kevin deve revisar Risk Engine (T-B01 a T-B07), kill switch (T-C01), journal (T-C03 a T-C05), fiscal (T-C06 a T-C07) e IA auditora (T-G01 a T-G03) em CODE e em QA-SEC. Recomendo que Kevin seja envolvido ANTES de Nikola iniciar cada bloco, não apenas ao final.

2. **SPEC ainda está em Draft** — se o Founder aprovar a SPEC com alterações, este PLAN pode precisar de ajuste proporcional. Nico sugere que a aprovação da SPEC aconteça antes de `letscode`.

3. **Sequência recomendada de blocos:** A → B → C → D → E (paralelo com F) → G → H. Blocos E e F podem avançar em paralelo após C estar completo. Bloco G somente após D (Telegram) e C (Journal) estarem completos.

4. **Fases F3 e F4 da integração Profit** — não estão cobertas neste PLAN. Estão marcadas como `later` no DAS. Quando o Founder decidir avançar para F3 (monitor live) ou F4 (NTSL automation), uma nova demanda SPEC+PLAN é aberta.

5. **Setup A+ (2 contratos em Fase 4)** — `setup_a_plus_check` está implementado no Risk Engine (T-B05), mas a definição técnica do que caracteriza um Setup A+ exige histórico de Fase 3. O validator existe e bloqueia corretamente, mas a lógica de `is_setup_a_plus` no `RiskContext` precisará de especificação adicional quando Fase 3 for concluída.

---

## 10. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-05-24 | Draft inicial — produzido via NCC-1701 PLAN, lead Nico | — (aguarda Founder) |

---

> **Gate de aprovação PLAN:** Founder valida este plano e libera `letscode` antes de CODE iniciar.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

# TECH-DEBT — cam-cockpit

> **Criado em:** 2026-05-24
> **Atualizado em:** 2026-05-25 (SPEC v0.3 — auditoria sistemática + 10 TASKs saneadoras)
> **Revisão:** Founder antes de PLAN do próximo ciclo

---

## §Resolvidos — TDs removidos do ledger ativo (preservados historicamente)

| ID | Título original | Resolvido por | Data |
|---|---|---|---|
| **TD-011** | BacktestSimulator sem P&L real por tick (resultado bruto sempre zero) | `BacktestSimulator` tick-scanning com SL/TP/EOD em `simulator.py` (TASK-008 BL-A SPEC v0.4) | 2026-05-27 |
| **TD-023** | Constitution route retorna 404 (banco não conectado) | Fallback `_resolve_constitution_file` em `cam/features/constitution/routes.py` (correção bugs Bloco MT5) | 2026-05-25 |
| **TD-024** | Settings endpoint não implementado | `cam/api/dashboard_routes.py::get_settings` (correção bugs Bloco MT5) | 2026-05-25 |
| **TD-025** | Risk Status endpoint não implementado | `cam/api/dashboard_routes.py::risk_status` (correção bugs Bloco MT5) | 2026-05-25 |
| **TD-001** | Posição total aberta simultânea (WIN+WIN) | Validator `total_open_contracts_check` adicionado (T-TD-001 SPEC v0.3) | 2026-05-25 |
| **TD-004** | Journal duplo JSONL sem teste de arquivo real | Teste com `tmp_path` em `test_jsonl_fallback.py` (T-TD-004) | 2026-05-25 |
| **TD-005** | Harvest service sem subscribe ao `DarfPaid` | Wired no `lifespan` + handler `handle_darf_paid` (T-TD-005) | 2026-05-25 |
| **TD-010** | `NotificationService` singleton em import-time | Factory lazy `get_notification_service()` (T-TD-010) | 2026-05-25 |
| **TD-012** | Sharpe Ratio stub (sempre zero) | Stddev real + CDI configurável em `BacktestMetrics.compute` (T-TD-012) | 2026-05-25 |
| **TD-017** | `AnthropicProvider` modelo/versão hardcoded | Lê de `Settings.anthropic_model` / `anthropic_api_version` (T-TD-017) | 2026-05-25 |
| **TD-026** | WebSocket P&L stub não funcional | `/api/v1/ws/pnl` emite snapshot a cada 5s + flag `WEBSOCKET_PNL_REAL_DATA` (T-TD-026) | 2026-05-25 |
| **TD-027** | Audit trail não integrado nas features | `kill_switch.service` + `mt5_integration.service` chamam audit (T-TD-027) | 2026-05-25 |
| **TD-v0.2-03** | Importer HTML sem regressão por build do MT5 | Fixture `mt5_report_build_3000.html` + 5 testes (T-TD-v0.2-03) | 2026-05-25 |
| **TD-v0.2-06** | Sem UI/endpoint de feature flags | `feature_flags` em `GET /api/v1/settings` (T-TD-v0.2-06) | 2026-05-25 |

## §Congelados — feature alvo desativada (sem trabalho a fazer enquanto off)

| ID | Título original | Estado |
|---|---|---|
| **TD-007** | `profit/validate-intention` sem RiskContext real | `[CONGELADO desde 2026-05-25 — profit_integration desativada por SPEC v0.2.1 R20]` |
| **TD-008** | `journal/import-csv` (Profit) sem DB | `[CONGELADO desde 2026-05-25 — profit_integration desativada por SPEC v0.2.1 R20]` |
| **TD-009** | `profit/reconciliation` sem DB | `[CONGELADO desde 2026-05-25 — profit_integration desativada por SPEC v0.2.1 R20]` |

> Reativação dos TDs CONGELADOS exige: (a) reativar `profit_integration` via flag + (b) revisitar a aplicabilidade do TD à nova versão.

---

## §Ativos — TDs mantidos (exigem escopo maior ou Fase 1+)

Após SPEC v0.3: 13 TDs resolvidos + 3 congelados → restam **20 ativos** abaixo (TD-002, 003, 006, 011, 013–016, 018–022, TD-v0.2-01/02/04/05/07/08/09). Cada um já documentado com `Bloqueante para produção` e `Resolução proposta`.

---

## TD-001 — Posição total aberta simultânea (WIN+WIN duplicado)

**Bloco:** B — Risk Engine
**Validator afetado:** `simultaneous_position_check`
**Descrição:** O validator atual verifica WIN+WDO simultâneo (vedado em Fases 1 e 2), mas não verifica se Carlos já tem 1 WIN aberto e tenta abrir outro WIN. Isso poderia resultar em 2 WINs abertos em Fases 1-2, violando o espírito (mas não a letra explícita) do Art. 12º.
**Artigo constitucional:** Art. 12º (implícito) — max 1 contrato em Fase 2
**Impacto:** Baixo em Fase 0 (sem trade real). Médio em Fase 2 (operação real com 1 contrato).
**Resolução proposta:** Adicionar `total_open_contracts_check` no Grupo 2 do Risk Engine: soma de contratos de todas as posições abertas do mesmo ativo não pode exceder o limite de fase.
**Bloqueante para produção:** Não para Fase 0. Sim para Fase 2.

---

## TD-002 — EventBus sem persistência (asyncio.Queue)

**Bloco:** A — Shared Kernel
**Descrição:** O EventBus usa `asyncio.Queue` em memória. Se o backend reiniciar com eventos pendentes (ex: `JournalEntryCreated` não processado pelo fiscal), eles se perdem.
**Impacto:** Baixo em Fase 0 (1 operador local, reinicializações são raras). Médio em Fase 1+ (operação real diária).
**Resolução proposta:** Redis Streams ou Postgres LISTEN/NOTIFY como fallback persistente. ADR já documenta Redis como alternativa (docker-compose.yml tem serviço comentado).
**Bloqueante para produção:** Não para Fase 0. Avaliar antes de Fase 1.

---

## TD-003 — Testes de checklists e kill_switch sem banco (mocks)

**Bloco:** C — Features Core
**Descrição:** Os testes de `kill_switch` e `checklists` usam `AsyncMock` para o repository. Não testam a persistência real em banco. Testes de integração reais (com banco de testes) serão necessários antes de QA formal.
**Impacto:** Médio — comportamento do repository real pode divergir do mock.
**Resolução proposta:** Adicionar fixtures pytest com banco de teste real (PostgreSQL em Docker) usando `pytest-docker` ou `testcontainers-python`. Fazer em fase QA do Bloco C.
**Bloqueante para produção:** Não para Fase 0. Recomendado antes de Fase 1.

---

## TD-004 — Journal duplo (JSONL) sem teste de arquivo real

**Bloco:** C — Feature journal
**Descrição:** O journal duplo (banco + JSONL append) está implementado no service, mas os testes usam mock para o repository e não verificam o arquivo JSONL físico em disco.
**Impacto:** Baixo — o JSONL é fallback de recuperação, não caminho crítico.
**Resolução proposta:** Adicionar teste com `tmp_path` fixture do pytest verificando que o JSONL é criado e contém o entry correto após `create_entry()`.
**Bloqueante para produção:** Não.

---

## TD-005 — Harvest service sem integração com fiscal (acoplamento via evento)

**Bloco:** C — Features harvest + fiscal
**Descrição:** O trigger para calcular harvest é o pagamento de DARF (`DarfPaid` evento). O evento existe no design mas a cadeia `DARF marked paid → DarfPaid published → harvest recalculates snapshot` está implementada apenas parcialmente — o subscribe do harvest ao DarfPaid não está wired no lifespan.
**Impacto:** Baixo em Fase 0. Em produção, o operador precisaria acionar o harvest manualmente após pagar a DARF.
**Resolução proposta:** Adicionar `event_bus.subscribe(DarfPaid, harvest_service.handle_darf_paid)` no lifespan e criar o evento `DarfPaid` em `cam/features/fiscal/events.py`.
**Bloqueante para produção:** Não para Fase 0. Sim para uso do harvest automático.

---

## TD-006 — trading_window_check com horários hardcoded WIN/WDO

**Bloco:** B — Risk Engine, Grupo 4
**Descrição:** Os horários de fechamento do WIN (17:50) e WDO (18:15) estão hardcoded no validator. A B3 pode alterar esses horários em datas especiais (pregões reduzidos, feriados).
**Impacto:** Baixo — mudanças de horário da B3 são raras e anunciadas com antecedência.
**Resolução proposta:** Mover os horários para a POV (POV vigente no `RiskContext`) ou para uma tabela de calendário operacional.
**Bloqueante para produção:** Não. Monitorar comunicados da B3.

---

---

## TD-007 — profit_integration/validate-intention usa stub (sem RiskContext real)

**Bloco:** D — T-D01
**Endpoint:** `POST /api/v1/profit/validate-intention`
**Descrição:** O endpoint retorna APPROVED sem construir um RiskContext real do banco. O `ProfitIntegrationService.validate_intention()` está implementado e testado contra mocks, mas o endpoint HTTP não injeta o `RiskContextBuilder` real (sem banco disponível).
**Artigos afetados:** Art. 15º (Risk Engine bloqueia? CaM não opera)
**Resolução proposta:** Implementar `RiskContextBuilder` que lê estado do banco (kill_switch, daily_pnl, etc.) e injetar via FastAPI Depends. Tarefa T-H06.
**Bloqueante para produção:** Sim — endpoint não pode ser usado em operação real até T-H06 completado.

---

## TD-008 — import-csv e ingest sem persistência no banco

**Bloco:** D — T-D02 / T-D05
**Endpoints:** `POST /api/v1/journal/import-csv` e `POST /api/v1/market-data/ingest`
**Descrição:** Ambos os endpoints parsam e validam os dados corretamente, mas não persistem no banco (TimescaleDB/PostgreSQL). Retornam contagem stub "todos inseridos".
**Resolução proposta:** Implementar repositories para `JournalEntry` (profit CSV) e `MarketTick` (ticks) com integração ao banco. Tarefa T-H06.
**Bloqueante para produção:** Sim para operação real.

---

## TD-009 — Reconciliação sem banco (manual_entries sempre vazio)

**Bloco:** D — T-D03
**Endpoint:** `GET /api/v1/profit/reconciliation/{date}`
**Descrição:** O `Reconciler` está implementado e testado, mas o endpoint não busca JournalEntries do banco — passa listas vazias. Reconciliação real requer leitura dos entries manuais do dia.
**Resolução proposta:** Injetar JournalRepository no endpoint de reconciliação e buscar entries por data. Tarefa T-H06.
**Bloqueante para produção:** Sim para uso operacional.

---

## TD-010 — NotificationService singleton criado em import-time

**Bloco:** D — T-D04
**Descrição:** `notification_service = NotificationService()` é criado no import de `cam/features/notifications/service.py`. Se o `.env` não estiver disponível no momento do import (ex: testes em CI sem `.env`), o singleton inicializa com token vazio (modo degradado). Comportamento correto, mas não ideal para teste de configuração.
**Resolução proposta:** Mover criação do singleton para o lifespan do app (lazy init) ou usar Factory pattern. Baixa prioridade.
**Bloqueante para produção:** Não — modo degradado funciona corretamente.

---

---

## TD-011 — BacktestSimulator sem P&L real por tick (resultado bruto sempre zero)

**Bloco:** F — T-F01 (simulator.py)
**Descrição:** O `BacktestSimulator.run()` registra todos os trades com `result_gross = Money(0)`. O simulador completo precisa executar a lógica de SL/TP por tick: encontrar o tick onde o stop-loss ou take-profit é atingido e calcular o P&L real baseado em pontos. Sem isso, o backtest não produz métricas úteis de P&L.
**Artigos afetados:** Art. 25º (resultado líquido exibido) — quando implementado, IR 20% já está no domain.
**Resolução proposta:** T-H07 — implementar lógica de tick scanning: para cada ordem aprovada, iterar os ticks seguintes até SL ou TP ser atingido; calcular `result_gross = (exit_price - entry_price) * points_per_tick * contracts`.
**Bloqueante para produção:** Sim para backtest real. Stub é suficiente para Fase 0.

---

## TD-012 — Sharpe Ratio stub (sempre zero)

**Bloco:** F — T-F02 (domain.py BacktestMetrics)
**Descrição:** `BacktestMetrics.sharpe_ratio` retorna `Decimal("0")` — requer desvio padrão dos retornos diários e taxa risk-free (CDI). Implementação adiada para T-H07.
**Resolução proposta:** Calcular std dev dos retornos net diários na `BacktestMetrics.compute()`. Usar CDI diário configurável como risk-free rate.
**Bloqueante para produção:** Não. Métrica informativa — sem impacto operacional.

---

## TD-013 — Walk-Forward com janela única (sem multi-split deslizante)

**Bloco:** F — T-F02 (walk_forward.py)
**Descrição:** `WalkForwardRunner.split()` retorna sempre uma única tupla (otimização, validação). Walk-forward real desliza a janela N vezes pelo histórico, gerando múltiplos folds de validação out-of-sample. Implementação atual é suficiente para validação de conceito mas não para análise robusta de overfitting.
**Resolução proposta:** T-H07 — implementar `n_splits` e lógica de janela deslizante com step configurável.
**Bloqueante para produção:** Não para Fase 0. Recomendado antes de usar o backtest para decisão de sizing.

---

## TD-014 — DuckDB research sem instância real (stub)

**Bloco:** F — T-F03 (routes.py `/research/query`)
**Descrição:** O endpoint `/api/v1/backtest/research/query` retorna stub sem executar DuckDB real. Validação de queries SELECT está implementada (bloqueio de DML/DDL), mas a execução real contra arquivos CSV/Parquet depende do banco disponível.
**Resolução proposta:** T-H06 — injetar instância DuckDB configurada, montar path de arquivos de dados e executar query com resultado real. Retornar schema + rows como JSON.
**Bloqueante para produção:** Sim para uso real de research. Stub suficiente para Fase 0.

---

## TD-015 — BacktestRun sem persistência no banco

**Bloco:** F — T-F03 (routes.py `/runs`)
**Descrição:** `GET /api/v1/backtest/runs` retorna lista vazia (stub). BacktestRuns não são persistidos — existem apenas in-memory durante a execução. Impossível listar histórico de runs ou comparar resultados entre sessões.
**Resolução proposta:** T-H06 — criar `BacktestRepository` com SQLAlchemy, persistir `BacktestRun` (config + trades + métricas) em PostgreSQL. Adicionar endpoint `POST /api/v1/backtest/runs` para disparar nova execução.
**Bloqueante para produção:** Sim para uso operacional do backtest.

---

## TD-016 — AnalystDataCollector stubs sem banco (get_* sempre vazio)

**Bloco:** G — T-G01 (data_collector.py)
**Descrição:** `AnalystDataCollector.get_journal_entries_today()`, `get_risk_decisions_today()` e `get_violations_today()` retornam listas vazias. A IA Auditora sempre analisa um dia "vazio" — nenhum dado real do journal ou do Risk Engine é lido.
**Artigos afetados:** Arts. 34-36 (IA read-only — o design está correto, mas a leitura real depende do banco).
**Resolução proposta:** T-H06 — implementar queries SQLAlchemy no `AnalystDataCollector` lendo de `journal_entries` e `risk_decisions` por data. Manter zero escrita.
**Bloqueante para produção:** Sim para análise útil. Stub suficiente para Fase 0.

---

## TD-017 — AnthropicProvider com modelo e versão hardcoded

**Bloco:** G — T-G02 (providers.py)
**Descrição:** `AnthropicProvider` tem `model="claude-haiku-4-5-20251001"` e `anthropic-version: "2023-06-01"` hardcoded. Atualização de modelo requer mudança de código.
**Resolução proposta:** Carregar `ANTHROPIC_MODEL` e `ANTHROPIC_API_VERSION` de `cam/_shared/config` (variáveis de ambiente). Usar `Settings` pattern já disponível no _shared.
**Bloqueante para produção:** Não. Mas dificulta atualização de modelo.

---

## TD-018 — Scheduler do ai_analyst não ativado no lifespan

**Bloco:** G — T-G03 (scheduler.py)
**Descrição:** `build_scheduler()` está implementado e testado, mas o scheduler não é iniciado no lifespan do app (`cam/api/main.py`). A análise diária não ocorre automaticamente — requer ativação manual.
**Artigos afetados:** Nenhum constitucional. Funcionalidade pós-mercado não está rodando.
**Resolução proposta:** Adicionar `scheduler = build_scheduler(...)` e `scheduler.start()` no lifespan após gate Founder. Requer instância do `AIAnalystService` configurada com provider real (Ollama ou Anthropic) e token Telegram.
**Bloqueante para produção:** Sim para análise automática. Stub suficiente para Fase 0.
**Gate:** Aprovação do Founder antes de ativar — scheduler roda pós-mercado com LLM real.

---

## TD-019 — Rotas /analyses e /analyses/{date} retornam stubs

**Bloco:** G — T-G03 (routes.py)
**Descrição:** `GET /api/v1/ai-analyst/analyses` retorna lista vazia e `GET /api/v1/ai-analyst/analyses/{date}` retorna mensagem de stub. Nenhuma análise real é persistida ou consultável via API.
**Resolução proposta:** T-H06 — criar `AIAnalystRepository` com SQLAlchemy para persistir análises geradas. Implementar endpoints reais com filtro por data.
**Bloqueante para produção:** Sim para consulta histórica de análises.

---

## TD-020 — ContentGuard sem log estruturado de violações em banco

**Bloco:** G — T-G01 (content_guard.py / service.py)
**Descrição:** Violações detectadas pelo `ContentGuard` são logadas via structlog (log.warning), mas não persistidas em banco. Impossível auditar historicamente quantas e quais análises foram rejeitadas.
**Artigos afetados:** Art. 31º (registro de falhas operacionais) — log em arquivo é fallback, banco é SSoT.
**Resolução proposta:** T-H06 — criar tabela `ai_analyst_violations` e persistir cada violação com timestamp, excerpt censurado e hash do raw_text. Manter raw_text fora do banco (privacidade do LLM).
**Bloqueante para produção:** Não para Fase 0. Recomendado antes de Fase 1.

---

*Tech debt adicionados no Bloco H serão appendados abaixo conforme produção avança.*

---

## TD-021 — Frontend sem testes de integração de rota

**Bloco:** E — T-E01 a T-E11
**Descrição:** Os componentes React têm 12 testes de unidade para componentes críticos (KillSwitchButton, PnlDisplay, RiskEngineStatusBanner), mas não há testes de integração de rota (ex: navegar para /fiscal e verificar que a tela carrega com os dados corretos do backend).
**Impacto:** Baixo em Fase 0 (cockpit local, operador único). Médio em Fase 1 (usabilidade).
**Resolução proposta:** Adicionar `@playwright/test` ou testes de rota com `@testing-library/react` + MSW (Mock Service Worker) para simular backend. Cobrir os painéis críticos: Cockpit, Journal, Fiscal.
**Bloqueante para produção:** Não.

---

## TD-022 — Paper Trading sem persistência no banco (`cam_paper_trades`)

**Bloco:** H — T-H01
**Descrição:** O `PaperTradingService.simulate()` está implementado e testado (9 testes), mas os resultados das simulações não são persistidos. Cada sessão perde o histórico de simulações.
**Resolução proposta:** Criar migration `cam_paper_trades` e `PaperTradeRepository` com SQLAlchemy. Adicionar `GET /api/v1/paper-trading/history` ao router. Tarefa de Fase 1.
**Bloqueante para produção:** Não para Fase 0. Sim para uso contínuo do paper trading.

---

## TD-023 — Constitution route retorna 404 (banco não conectado)

**Bloco:** H — T-H02
**Descrição:** `GET /api/v1/constitution/current` retorna 404 porque a tabela `cam_constitution_versions` não tem dados semeados. A migration cria a tabela mas não insere a Constituição v1.0.
**Resolução proposta:** Criar migration de seed ou script de inicialização que insere a Constituição v1.0 atual lida do `CONSTITUICAO.md`. Executar no setup inicial.
**Bloqueante para produção:** Não. Frontend exibe mensagem orientativa quando 404.

---

## TD-024 — Settings endpoint não implementado (`/api/v1/settings`)

**Bloco:** E — T-E08
**Descrição:** O painel de Configurações do frontend chama `GET /api/v1/settings` e `PATCH /api/v1/settings`, mas esses endpoints não existem no backend. A feature de `settings` não foi implementada como feature separada.
**Resolução proposta:** Criar `cam/features/settings/` com domain, service e routes para gerenciar configurações (telegram_token, profit_csv_path) de forma segura. Armazenar em tabela de config (nunca retornar secrets em GET).
**Bloqueante para produção:** Não para Fase 0. Sim para configuração via UI.

---

## TD-025 — Risk Status endpoint não implementado (`/api/v1/risk/status`)

**Bloco:** E — T-E02/T-E06
**Descrição:** O Cockpit Live e Risk Console chamam `GET /api/v1/risk/status` para obter estado atual do Risk Engine, mas esse endpoint não existe. O backend tem `GET /api/v1/kill-switch/status` mas não um endpoint consolidado de status do Risk Engine.
**Resolução proposta:** Adicionar `GET /api/v1/risk/status` no router do kill_switch ou criar feature `risk_console` com endpoint consolidado que agrega: kill switch, daily_pnl, gain_lock, tax_compliant, fase atual.
**Bloqueante para produção:** Não para Fase 0. Necessário para Cockpit Live funcional.

---

## TD-026 — WebSocket P&L não implementado (`/api/v1/ws/pnl`)

**Bloco:** E — T-E02 (frontend) / A — T-A05 (backend)
**Descrição:** O frontend usa `usePnlWebSocket()` que conecta a `ws://localhost:8000/api/v1/ws/pnl`, mas o endpoint WebSocket está como stub em `cam/api/websocket.py`. P&L em tempo real não funciona sem banco conectado.
**Resolução proposta:** Implementar WebSocket handler que busca daily_pnl atual do banco a cada 5s e publica. Ativar no lifespan após banco disponível.
**Bloqueante para produção:** Não para Fase 0 (frontend degrada graciosamente para 0). Sim para cockpit operacional.

---

## TD-027 — Audit trail não integrado nas features (apenas funções disponíveis)

**Bloco:** H — T-H05
**Descrição:** As funções de audit (`log_risk_decision`, `log_kill_switch_activated`, etc.) estão implementadas em `cam/_shared/audit/logger.py` e testadas (12 testes), mas ainda não são chamadas pelos services das features. O Risk Engine não chama `log_risk_decision` após cada decisão.
**Resolução proposta:** Integrar chamadas de audit nos services: `kill_switch/service.py` deve chamar `log_kill_switch_activated`; o wrapper de `validate()` no `profit_integration/service.py` deve chamar `log_risk_decision`. Não chamar dentro do engine (violaria Zero I/O).
**Bloqueante para produção:** Não para Fase 0. Recomendado antes de Fase 1 para auditoria real.

---

## Tech debts da SPEC v0.2 (MT5 enquadramento — princípio de coexistência)

### TD-v0.2-01 — Bridge ZeroMQ sem autenticação

**Bloco:** SPEC v0.2 — T-MT5-C02
**Descrição:** Bridge ZeroMQ confia apenas em binding `127.0.0.1` (localhost) para isolar de rede. Não há autenticação cripto-grada de mensagens.
**Severidade:** Médio — aceitável em v0.2 (uso local). Revisitar em SPEC v0.3 quando bridge for read-write.
**Bloqueante para produção:** Não para Fase 1 (paper). Recomendado antes de Fase 2 (real).

### TD-v0.2-02 — EA MQL5 sem testes automatizados

**Bloco:** SPEC v0.2 — T-MT5-F02
**Descrição:** MQL5 não tem framework de teste automatizado consolidado. `cam_bridge.mq5` não tem cobertura unitária — apenas inspeção visual e teste manual em conta DEMO.
**Severidade:** Médio. Mitigar via paridade Python↔MQL5 quando `cam_risk_mirror.mq5` existir (SPEC v0.3).
**Bloqueante para produção:** Não para v0.2 (EA é read-only). Crítico para v0.3 (read-write).

### TD-v0.2-03 — Importador HTML depende de estrutura interna do relatório MT5

**Bloco:** SPEC v0.2 — T-MT5-E01
**Descrição:** Parser HTML em `importer.py` assume colunas na ordem do MT5 build atual. Update do MT5 pode mudar layout.
**Severidade:** Baixo — versionar samples de relatório por major version do MT5 e adicionar teste de regressão.

### TD-v0.2-04 — `profit_integration/` continua compilando mesmo desativada

**Bloco:** SPEC v0.2.1 — princípio R21
**Descrição:** Por decisão do Founder, código Profit permanece no repositório (não arquivado). Custo: ocupa testes, exige manutenção mínima em renames/upgrades.
**Severidade:** Baixo — preço aceito da reversibilidade. Reavaliar em SPEC v0.3 ou após MT5 estar em Fase 2+ por > 90 dias.

### TD-v0.2-05 — Wine pode glitchar com update do MT5 sem automação de fallback

**Bloco:** SPEC v0.2 — T-MT5-H01
**Descrição:** Runbook RUNBOOK-INCIDENTE-TECNICO §2.2 prevê migração manual para VPS Windows como plano B, mas não há automação. Founder precisa executar manualmente se Wine glitchar.
**Severidade:** Médio. Gatilho objetivo em DECISION-MEMO §7 G-B1 reabre a decisão automaticamente.

### TD-v0.2-06 — Sem UI de feature flags para o Founder

**Bloco:** SPEC v0.2.1 — R21
**Descrição:** Reativação simultânea de Profit + MT5 protegida apenas por mutex no startup. Sem painel `/settings` listando todas as feature flags vigentes.
**Severidade:** Baixo. Adicionar painel "Feature Flags" em v0.3.

### TD-v0.2-07 — Audit log de `DISABLED_ENDPOINT_ATTEMPT` sem retenção dedicada

**Bloco:** SPEC v0.2.1 — R21.05
**Descrição:** Logs cresceriam indefinidamente se um cliente externo continuar chamando endpoints Profit em loop. Sem política de rotação específica.
**Severidade:** Baixo. Alinhado com retenção geral de audit logs (família TD-H05).

### TD-v0.2-08 — Reconciliação MT5 sem persistência (`/mt5/reconciliation/{date}` stub)

**Bloco:** SPEC v0.2 — T-MT5-E04
**Descrição:** Endpoint retorna estrutura vazia. Reconciliação plena exige `JournalRepository` real conectado ao DB.
**Severidade:** Médio. Equivalente ao TD-009 da v0.1 (que ficou CONGELADO por R20.05).
**Bloqueante para produção:** Sim para uso operacional de Fase 2+.

### TD-v0.2-09 — Hashes de import-report em memória (singleton process-scoped)

**Bloco:** SPEC v0.2 — T-MT5-E03
**Descrição:** `_seen_hashes` é set em memória do processo Python. Restart do backend perde histórico de hashes, permitindo reimportar arquivo já processado.
**Severidade:** Médio. Migrar para persistência em DB (tabela `cam_mt5_imports`) em SPEC v0.3.

---

## TDs novos identificados em BL-A (SPEC v0.4 — execução autônoma 2026-05-27)

### TD-v0.4-A1 — `_IdempotencyCache` do Order Gateway é process-local (T006)

**Bloco:** BL-A — `cam/_shared/order_gateway/gateway.py`
**Descrição:** Cache de idempotency keys vive em memória do processo Python (`_IdempotencyCache` com TTL 60s). Restart do backend ou múltiplos workers (uvicorn `--workers N>1`) abrem janela para retry duplicado passar despercebido.
**Resolução proposta:** Migrar para tabela `cam_order_intents(idempotency_key TEXT PK, ts TIMESTAMPTZ, ttl_seconds INT)` com cleanup periódico via APScheduler; ou Redis com TTL nativo.
**Bloqueante para produção:** **SIM**. Antes de BL-E T028 entrar em DEMO, esta persistência precisa estar pronta.
**Severidade:** Alto — defesa contra retries em rede ZMQ depende disso.

### TD-v0.4-A2 — Order Gateway audit apenas via structlog (sem persistência DB)

**Bloco:** BL-A — `gateway._audit`
**Descrição:** Eventos do Order Gateway hoje só aparecem em log estruturado (`cam.order_gateway`). Não há persistência em `cam_audit_events` / `cam_risk_decisions`. Art. 31º exige journal completo.
**Resolução proposta:** Criar repository `OrderGatewayAuditRepository` consumindo o caller (não acoplar `gateway.py` ao DB — mantém Pure Python na shared kernel). Caller (paper_loop, EA dispatcher) chama o repository após cada `submit()`.
**Bloqueante para produção:** **SIM** para Fase 2+. Em Fase 0/1 com paper apenas, structlog é suficiente.
**Severidade:** Médio.

### TD-v0.4-A3 — Lint Python anti auto-edição de limites ainda não implementado

**Bloco:** BL-A → previsto em BL-H1 (TASK-047)
**Descrição:** PLAN v0.4 §4.10 + recomendação Leo na EMENDA-001 v2: precisa de lint que rejeite PRs alterando `MAX_WIN_CONTRACTS`, `MAX_WDO_CONTRACTS`, `MAX_DAILY_DRAWDOWN_PCT` fora da allowlist de arquivos. `lint_mql5.py` cobre apenas MQL5.
**Resolução proposta:** TASK-047 cria `scripts/lint_constitutional_limits.py` e CI workflow. Já mapeado, sem necessidade de ação fora do PLAN.
**Bloqueante para produção:** Não em BL-A; passa a ser bloqueante quando BL-H1 entrar.
**Severidade:** Baixo (mapeado).

### TD-v0.4-A4 — Hash de Evidence Pack (T003) não inclui timestamp de retire

**Bloco:** BL-A — `cam/features/strategies/promotion.py::_persist_retire_marker`
**Descrição:** Para evitar colisão de hash em múltiplas tentativas de retire da mesma estratégia, o hash gerado inclui `datetime.now(UTC).isoformat()`. Isso quebra determinismo do hash (cada chamada gera hash diferente), o que é intencional **mas** difere do comportamento das outras transições (hash determinístico via SHA256(payload)).
**Resolução proposta:** Quando T019 (BL-C) consolidar promoção paper_ok, padronizar política de retire — ou (a) retire é sticky e não permite re-registro, ou (b) hash de retire inclui marker explícito `retire-{strategy_id}-{count}` em vez de timestamp.
**Bloqueante para produção:** Não. Comportamento atual é seguro mas pouco elegante.
**Severidade:** Baixo.

### TD-v0.4-A5 — `cam_bridge.mq5` GET_VERSION sem hash do binário

**Bloco:** BL-A — `apps/cam-cockpit/mql5/experts/cam_bridge.mq5`
**Descrição:** Critério CA-A.5 da SPEC pede que GET_VERSION retorne `version + hash`. Hoje retorna `version + build_date_time` (via `__DATE__ __TIME__`). Hash real do `.ex5` compilado exigiria script de build externo que calcula SHA-256 do binário pós-MetaEditor e injeta em `cam_ea_artifacts` (tabela a criar em BL-E).
**Resolução proposta:** TASK em BL-E (T025+) — script `scripts/build_mql5.sh` pós-compilação grava em tabela `cam_ea_artifacts (filename, version, hash, compiled_at)` e EA consulta no startup.
**Bloqueante para produção:** Não em BL-A; passa a ser bloqueante em BL-E (`SUBMIT_ORDER`).
**Severidade:** Baixo.

### TD-v0.4-A6 — `BacktestSimulator` single-position (não trata multi-strategy simultânea)

**Bloco:** BL-A — `simulator.py`
**Descrição:** Substituição do stub `result_gross=0` por P&L real (TD-011 RESOLVIDO) trouxe simplificação: após abrir posição, ignora novos candidatos até fechá-la. Multi-strategy simultânea (BL-H1) exigirá refactor para tracking de N posições em paralelo respeitando agregação Art. 11-A.
**Resolução proposta:** BL-H1 T043 (orchestrator) consome esse simulator com adaptação — promover `_OpenPosition` para `list[_OpenPosition]` indexada por (strategy_id, asset).
**Bloqueante para produção:** Não. Single-strategy em paper/demo até BL-H1 finalizado.
**Severidade:** Baixo (mapeado em BL-H1).

### TD-v0.4-A7 — Strategy Registry sem endpoint HTTP (apenas repository)

**Bloco:** BL-A — `cam/features/strategies/routes.py` continua stub
**Descrição:** TASK-002/T003 entregaram domain + repository + promotion service, mas o router FastAPI segue vazio. UI (T024 BL-D e UIs subsequentes) ainda não tem como listar/ativar estratégias via HTTP.
**Resolução proposta:** Implementar `GET /api/v1/strategies`, `POST /api/v1/strategies/{id}/activate`, `POST /api/v1/strategies/{id}/promote` quando a primeira UI dependente entrar (BL-C T016 paper loop UI ou BL-H1 T049 Risk Console).
**Bloqueante para produção:** Não. Operação BL-A é via script CLI / migrations.
**Severidade:** Baixo.


---

## TDs novos identificados nas Janelas 1-5 — Execução autônoma BL-B..BL-I (2026-05-28)

> Estes TDs surgiram durante a execução autônoma BL-B..BL-I (T011..T062).
> Resumo: 710 testes verdes; sem regressão; mas várias decisões pragmáticas
> mereceram registro explícito para revisão do Founder.

### TD-v0.4-B1 — Layout do extrato CSV Genial não documentado (TASK-014)

**Bloco:** BL-B — `cam/features/ledger/genial_importer.py`
**Descrição:** O parser canônico aceita CSV com headers heurísticos (alias `ticker, codigo, ativo`, `quantidade, qtd`, `preco_medio, custo_medio`, separador `,` ou `;`, decimal vírgula BR). **Não há amostra real do extrato Genial Investimentos no repositório**, então o parser foi entregue com fixture sintética em `tests/fixtures/genial_extrato_sample.csv` + flag `requires_layout_confirmation=True` em caso de headers desconhecidos.
**Resolução proposta:** (1) Founder anexa CSV real Genial em `data/seeds/genial_extrato_real_aXXXXXXXX.csv`; (2) carregamos como fixture nova; (3) ajustamos `_GENIAL_COLUMN_MAPPINGS` se houver alias novo; (4) removemos a flag de unknown_layout. **Esta TASK depende exclusivamente de input externo do Founder.**
**Bloqueante para produção:** **SIM** para BL-D operacional via Genial Import. Não bloqueia paper/research.
**Severidade:** Médio.

### TD-v0.4-C1 — Promoção paper_ok com 100/95% pode ser ajustada por POV

**Bloco:** BL-C — `cam/features/strategies/paper_evidence.py`
**Descrição:** `MIN_PAPER_TRADES=100` e `MIN_ADHERENCE=0.95` hardcoded. POV vigente cita esses valores, mas Founder pode querer ajustar via POV sem editar código.
**Resolução proposta:** Mover thresholds para tabela `cam_pov_versions` (já existente) e carregar via `get_pov()`. Refactor leve em BL-C ou ciclo de governança POV.
**Bloqueante para produção:** Não em Fase 0/1. Sim quando Founder começar a operar em DEMO.
**Severidade:** Baixo.

### TD-v0.4-C2 — AIAnalystDataCollector ignora `cam_violations.context` JSONB

**Bloco:** BL-C — `cam/features/ai_analyst/data_collector.py`
**Descrição:** A coluna `cam_violations.context` é JSONB com payload rico (qual validator culpou, intent_id, etc.). T018 retorna apenas `context::text`, perdendo navegabilidade estrutural na análise. Suficiente para o BL-C entregar, mas IA Auditora terá menos contexto para narrativa em BL-G T039.
**Resolução proposta:** Estender query para retornar `context` como dict nativo (psycopg já faz isso automaticamente — basta remover o cast `::text`). Refactor 5 linhas + 1 teste.
**Severidade:** Baixo.

### TD-v0.4-E1 — Paridade Python↔MQL5 conservadora (Mirror tem menos validators)

**Bloco:** BL-E — `cam_risk_mirror.mq5` + `risk_mirror_harness.py`
**Descrição:** A versão MQL5 espelha os principais validators (kill_switch, checklists, DARF, max_contracts, daily/weekly/monthly loss, gain_lock, daily ops) mas **não cobre** os 4 últimos (`martingale`, `trading_window`, `setup_a_plus`, `circuit_breaker`). A propriedade de paridade testada é conservadora: **Mirror reject → Python reject**, mas Python pode rejeitar onde Mirror aprova (paridade não simétrica).
**Resolução proposta:** Expandir `cam_risk_mirror.mq5` com os 4 validators faltantes. Cada um exige `RiskContextSnapshot` adicionar campos (`recent_trade_results[]`, `current_session_time`, etc.). Tarefa específica BL-E follow-up antes de DEMO live.
**Bloqueante para produção:** **SIM** para `SUBMIT_ORDER` real em DEMO. Não bloqueia paper.
**Severidade:** Alto.

### TD-v0.4-E2 — `SUBMIT_ORDER` em `cam_bridge.mq5` é apenas handoff

**Bloco:** BL-E — `cam_bridge.mq5`
**Descrição:** O comando `SUBMIT_ORDER` no bridge não envia ordem; retorna `{"status":"handoff","target":"cam_risk_mirror"}` porque o bridge é read-only por design (CA15.1 + lint). O cockpit Python (T028 EADispatcher) precisa rotear `SUBMIT_ORDER` direto para `cam_risk_mirror.mq5` em **socket REQ/REP separado**. Hoje EADispatcher aponta para a mesma porta `5557` do bridge.
**Resolução proposta:** (1) Adicionar `input int InpRiskMirrorReqPort = 5559;` em `cam_risk_mirror.mq5`; (2) ZMQ bind no inicio do EA; (3) EADispatcher passa a usar porta 5559 quando `env=demo|real`. Trabalho de ~50 linhas; cobertura via testes E2E.
**Bloqueante para produção:** **SIM** para BL-E operacional.
**Severidade:** Alto.

### TD-v0.4-E3 — Fill subscriber sem teste E2E (dedup conservadora)

**Bloco:** BL-E — `cam/features/mt5_integration/fill_subscriber.py`
**Descrição:** A dedup atual usa `(asset + timestamp exato)` em vez de `intent_id`. Risco: dois fills distintos com mesmo timestamp seriam fundidos. `cam_journal_entries` precisa coluna nova `intent_id UUID UNIQUE` para dedup robusto.
**Resolução proposta:** Migration que adiciona `cam_journal_entries.intent_id UUID UNIQUE NULL` + ajustar persist() para usar `ON CONFLICT (intent_id) DO NOTHING`.
**Severidade:** Médio.

### TD-v0.4-F1 — Fundamentals Collector aceita apenas Placeholder

**Bloco:** BL-F — `cam/features/fundamentals/multi_source_collector.py`
**Descrição:** Esqueleto multi-source entregue com 1 fonte placeholder (fixture hardcoded). Coleta real depende de TD-v0.4-01 (escolha de fontes + ToS).
**Resolução proposta:** TD-v0.4-01 já mapeado.
**Severidade:** Baixo.

### TD-v0.4-G1 — Pattern Lab `p_value` é placeholder, não teste estatístico real

**Bloco:** BL-G — `cam/features/research/pattern_lab.py`
**Descrição:** O cálculo de `p_value` é `1 - (sucessos/total)` — não é teste de hipótese formal. Suficiente para sinalizar padrões frequentes; insuficiente para validar significância estatística.
**Resolução proposta:** Adicionar teste binomial real (`scipy.stats.binomtest`) ou implementar manualmente. Decisão depende de se queremos importar scipy (peso considerável).
**Severidade:** Baixo (research only — não decide ordem).

### TD-v0.4-G2 — Rebalance Suggestion não considera tax cost da venda

**Bloco:** BL-G — `cam/features/research/rebalance.py`
**Descrição:** Sugestões de SELL não computam IR sobre ganho de capital (renda variável 15%). Operador pode ser surpreendido por imposto efetivo.
**Resolução proposta:** Integrar com `fiscal.service.compute_capital_gains_tax(holding, sell_price, sell_qty)` quando essa função existir.
**Severidade:** Baixo.

### TD-v0.4-H1.1 — Aggregate risk recebe correlations injetadas, sem cache nem job

**Bloco:** BL-H1 — `cam/_shared/risk/aggregate.py`
**Descrição:** Correlações entre estratégias hoje são parâmetro do caller (`AggregateContext.correlations`). Não há job que pré-compute correlation rolling 30 dias e popule o contexto antes do orquestrador rodar.
**Resolução proposta:** APScheduler `correlation_job` que computa via `cross_asset_correlation.py` (já entregue em T037) sobre journal entries reais e popula `cam_strategy_runtime_state.correlations_json`.
**Severidade:** Médio. Sem job, MULTI_STRATEGY_ENABLED não pode operar com proteção do Art. 11-A item 8.

### TD-v0.4-H1.2 — `Settings.multi_strategy_enabled` flag não tem ledger automatic

**Bloco:** BL-H1 — `cam/_shared/config/__init__.py`
**Descrição:** Flag adicionada em T046 (BL-A pré-trabalho), mas toggle hoje exige edição manual de `FEATURE-FLAGS-LEDGER.md` (entrada #003 já reservada). Sem endpoint admin que automatize a ledger.
**Resolução proposta:** `POST /api/v1/admin/flags/multi-strategy/toggle` (já está no PLAN T046) — implementação adiada para quando Founder for ativar.
**Severidade:** Baixo (controle manual aceitável em Fase 0).

### TD-v0.4-H2.1 — `set_current_limits` é runtime override (process-local)

**Bloco:** BL-H2 — `cam/_shared/risk/limits.py`
**Descrição:** Override de limites via `set_current_limits()` vive em memória do processo. Restart do backend reseta para default 2+2. Para escalonamento persistente, a aplicação real deve:
  1. Persistir `IN_FORCE` em `cam_constitutional_scaling_events`.
  2. Backend lifespan carregar `latest_in_force` → `set_current_limits(...)`.
**Resolução proposta:** Adicionar `scaling.runtime.bootstrap()` chamado em `api/main.py::lifespan`.
**Bloqueante para produção:** **SIM** para BL-H2 operacional.
**Severidade:** Alto.

### TD-v0.4-H2.2 — Job APScheduler de scaling não wired no lifespan

**Bloco:** BL-H2 — TASK-051 ainda só tem esqueleto conceitual
**Descrição:** A função `compute_scaling_eligibility` (T050) está pronta + repositório (T052), mas o **job APScheduler** que roda pós-pregão diário ainda não foi entregue. T051 ficou esquemático.
**Resolução proposta:** Criar `cam/features/scaling/job.py::evaluate_all_strategies_after_close()` + agendar via `BackgroundScheduler` no lifespan.
**Bloqueante para produção:** SIM para detecção automática de elegibilidade.
**Severidade:** Médio.

### TD-v0.4-H2.3 — Endpoint `/scaling/revoke/{esc_id}` ainda não implementado

**Bloco:** BL-H2 — TASK-053
**Descrição:** A lógica de cooldown (`compute_cooldown_days`, `detect_win_streak`) está pronta + repository. **Falta o endpoint HTTP** + UI (T057) que permite operador revogar escalonamento manualmente.
**Resolução proposta:** `cam/features/scaling/router.py` + componente UI quando frontend BL-H2 entrar.
**Severidade:** Médio.

### TD-v0.4-H2.4 — Auto-revert (T054) ainda sem job rolling-30-pregões

**Bloco:** BL-H2 — TASK-054
**Descrição:** Schema + repositório suportam evento `AUTO_REVERTED`, mas o **job rolling** que dispara reversão (Voltaire 2 — DD em dobro) está pendente. Hoje é manual.
**Resolução proposta:** Encadear com job de T051 — pós-fechamento checa estratégias IN_FORCE + se algum critério caiu → emite AUTO_REVERTED + SOFT_KILL_SWITCH.
**Severidade:** Alto antes de BL-H2 operacional.

### TD-v0.4-I1 — `cam_bridge.mq5` multi-instance ainda usa canal legacy duplicado

**Bloco:** BL-I — `cam_bridge.mq5`
**Descrição:** T058 (multi-instance) injetou `EA_ID` e canais `mt5.{ea_id}.heartbeat`, mas mantém canal legacy `mt5.heartbeat` para compat com SPEC v0.2. Em deploy com 2+ EAs, ambos publicam no canal legacy → leituras podem se misturar.
**Resolução proposta:** Quando todos os subscribers Python migrarem para canais com prefixo, **remover** publicação no canal legacy. Hoje preservado para evitar quebra.
**Severidade:** Baixo.

### TD-v0.4-I2 — DSL Compiler usa `eval` (mesmo que controlado)

**Bloco:** BL-I — `cam/features/strategies/dsl/compiler.py`
**Descrição:** Mesmo com validação AST + whitelist de nodes + `__builtins__={}`, o uso de `eval()` permanece como vetor de ataque potencial. Auditor de segurança formal vai marcar `# noqa: S307` como suspeito.
**Resolução proposta:** Reescrever evaluator com AST walker próprio (sem `eval`), avaliando nodes manualmente (Compare, BoolOp, Constant, Name). ~60 linhas, sem dependência externa.
**Bloqueante para produção:** **SIM** se BL-I for entrar em DEMO/REAL.
**Severidade:** Alto.

### TD-v0.4-FEATCONTRACT — Strategy contracts deveriam estar em `_shared/`

**Bloco:** Transversal — descoberto em regression de import-linter
**Descrição:** `Strategy` Protocol, `StrategyMetadata`, `StrategyStatus`, `StrategyContext` vivem em `cam/features/strategies/domain.py` mas são consumidos por `paper_trading.loop`, `robot_orchestrator.orchestrator`, `_shared/autonomy/matrix`, `_shared/order_gateway/gateway`. Isso quebra a regra de independência entre features (ADR-013). Resolução temporária: adicionar exceções específicas em `pyproject.toml::ignore_imports`. Resolução estrutural: mover contratos para `cam/_shared/strategy_contracts/` deixando `features.strategies` apenas com persistência + S1 ORB.
**Resolução proposta:** Refactor de 1 arquivo (move + reexport) + atualizar imports.
**Severidade:** Médio (debt arquitetural, sem impacto funcional).

### TD-v0.4-T024 — UI `/carteira-hard` não implementada nesta sessão

**Bloco:** BL-D — TASK-024
**Descrição:** Backend completo (endpoint POST/GET, importer Genial integrado, assert estrutural Art. 23). UI React+MUI deferida para sessão dedicada de frontend.
**Resolução proposta:** Quando Founder priorizar frontend, implementar `apps/cam-cockpit/frontend/src/features/carteira-hard/`.
**Severidade:** Baixo (CRUD via API/admin enquanto isso).

### TD-v0.4-T039 — UI Research Workbench (Recharts) não implementada

**Bloco:** BL-G — TASK-039
**Descrição:** Backend `research/cross_asset_correlation.py`, `pair_trade_backtest.py`, `pattern_lab.py` entregues. UI com visualização Recharts deferida.
**Severidade:** Baixo (research é use-case interno, CLI/Notebook funcionam).

### TD-v0.4-T049 + T057 — UI Risk Console (aderência + histograma) não implementadas

**Bloco:** BL-H1/H2 — T049 + T057
**Descrição:** Backend completo (orchestrator, aggregate_risk_check, scaling.py, repository). UI deferida.
**Severidade:** Baixo até MULTI_STRATEGY/SCALING_ENABLED ativarem.


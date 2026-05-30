# TODO-OPERACIONAL — cam-cockpit

> **Para Carlos revisar antes de avançar para Fase 1 (Paper Trading)**
> **Criado em:** 2026-05-24
> **Atualizado em:** 2026-05-24 (Blocos A–C)

---

## Decisões pendentes do Founder

### OP-001 — Corretora e estrutura de custos (FQ-002)
**Ação:** Definir corretora vinculada ao Profit (XP? Clear? Rico?) e levantar tabela de corretagem exata (custo por mini contrato WIN e WDO).
**Impacto:** O ledger fiscal usa custo por operação no cálculo de `result_net`. Com corretagem incorreta, o edge calculado é desonesto.
**Onde mudar:** `cam/features/journal/domain.py` — adicionar constante ou tabela de custos por corretora após decisão.
**Instrumento de avaliação:** [`/project/CORRETORA-EVAL.md`](../../project/CORRETORA-EVAL.md) — matriz de 10 corretoras, edge mínimo calculado, script de contato pronto para uso.

### OP-002 — Versão do Profit: Pro ou Ultra (FQ-001)
**Ação:** Confirmar versão contratada.
**Impacto:** Fase F4 de integração (NTSL + Automação de Estratégias) só está disponível no Ultra. Se Pro, o cockpit fica limitado a F1-F3 permanentemente sem upgrade.
**Onde mudar:** `ADR-001-profit-plataforma-execucao.md` — atualizar a seção "Contexto" com a versão confirmada.

### OP-003 — Fonte de tick histórico para backfill (FQ-003)
**Ação:** Verificar se o Profit exporta tick raw (granularidade ms) ou apenas candles. Se apenas candles, definir fonte alternativa (Tickstory, Dukascopy, etc.).
**Impacto:** Bloco D (T-D05) implementou o importador de CSV/Parquet, mas o formato esperado precisa ser validado contra o export real do Profit.
**Onde mudar:** `cam/features/market_data/service.py` — método `ingest_ticks(source_file)` pode precisar de parser específico.

### OP-004 — Tese de edge da primeira estratégia (FQ-004)
**Ação:** Definir hipótese de edge antes de usar o backtest engine (Bloco F).
**Impacto:** O backtest engine está implementado mas a estratégia a ser testada não foi especificada. Sem hipótese, o backtest não tem destino.
**Onde mudar:** `cam/features/strategies/domain.py` — implementar a estratégia concreta após definição.

### OP-005 — Parâmetros iniciais do Risk Engine (FQ-006)
**Ação:** Confirmar os valores da POV v1.0 como ponto de partida:
- Stop WIN: 150–250 pontos
- Stop WDO: 3–7 pontos
- Drawdown diário: 3% do capital (= R$ 150 sobre R$ 5.000)
- Gain lock diário: 2% (= R$ 100)
**Impacto:** Esses valores estão implementados como constantes nos validators do Risk Engine. Se Carlos quiser valores diferentes, é uma alteração de POV (não de código).
**Onde mudar:** `cam/_shared/risk/validators/group3_pnl.py` — constantes `DAILY_LOSS_LIMIT_PCT` etc. são configuráveis via POV no futuro.

### OP-006 — Capital na corretora (FQ-007)
**Ação:** Definir quando o capital de R$ 5.000 será depositado. O ledger assume R$ 5.000 como base de cálculo desde Fase 0.
**Impacto:** O `RiskContext.total_capital` é construído pelo service com o valor declarado. Não afeta o funcionamento do cockpit em Fase 0, mas o ledger de buckets precisa ser inicializado com os valores reais.
**Onde mudar:** Seed inicial da tabela `cam_bucket_transactions` com saldos iniciais dos 3 buckets.

---

## Setup necessário antes de usar o cockpit

### OP-007 — Criar bot Telegram (FQ-008)
**Passos:**
1. Abrir conversa com `@BotFather` no Telegram
2. `/newbot` → definir nome e username
3. Copiar o token gerado
4. Iniciar conversa com o bot e obter o `chat_id` via `https://api.telegram.org/bot{TOKEN}/getUpdates`
5. Preencher `.env`: `TELEGRAM_BOT_TOKEN=...` e `TELEGRAM_CHAT_ID=...`
**Impacto:** Sem Telegram configurado, o cockpit funciona em modo degradado (sem alertas).

### OP-008 — Configurar rclone para backup (FQ-009)
**Passos:**
1. Instalar rclone: `curl https://rclone.org/install.sh | bash`
2. Configurar Google Drive: `rclone config` → escolher `drive`
3. Testar: `rclone ls gdrive:/cam-backups`
4. Adicionar ao crontab: `0 2 * * * /path/to/scripts/backup.sh`
**Impacto:** Sem rclone, o backup fica apenas no `pg_dump` local.

### OP-009 — Instalar Ollama para IA local (Bloco G)
**Passos:**
1. Linux: `curl -fsSL https://ollama.com/install.sh | sh`
2. Baixar modelo: `ollama pull llama3.1:8b` (ou equivalente)
3. Testar: `ollama run llama3.1:8b "Olá"`
4. Preencher `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
**Impacto:** Sem Ollama, a IA auditora usa Anthropic API (com custo e dados enviados externamente).

### OP-010 — Subir banco e rodar migrations (antes de qualquer uso)
**Passos:**
1. `cd apps/cam-cockpit && docker compose up -d db`
2. `cd backend && uv sync --extra dev`
3. `DATABASE_URL=postgresql+psycopg://cam:cam@localhost:5433/cam_db uv run alembic upgrade head`
4. Verificar: `uv run pytest tests/test_migrations.py -v` (4 testes skipped passarão a funcionar)

---

## Validações obrigatórias antes de Fase 1 (Paper Trading)

### OP-011 — Testar kill switch no Windows
**Ação:** Após setup Windows, verificar que o kill switch ativa via UI e bloqueia tentativas de operação subsequentes no Risk Engine.
**Como testar:** Ativar kill switch → tentar criar JournalEntry via API → verificar resposta `400 KILL_SWITCH_ATIVO`.

### OP-012 — Validar cálculo fiscal com operação real
**Ação:** Registrar 1 operação de teste no journal, verificar que IR 20% é provisionado corretamente e que DARF é gerada ao final do mês.
**Critério de aceite:** `result_net = result_gross - costs - (result_gross * 0.20)` para operação lucrativa.

### OP-013 — Testar importação CSV do Profit (F2)
**Ação:** Exportar CSV de uma sessão de paper trading do Profit e importar via `POST /api/v1/journal/import-csv`.
**Critério de aceite:** 0 duplicatas na reimportação (hash-based deduplication).

---

## BREAKING CHANGE — Plataforma de execução (2026-05-30)

### OP-014 — MT5 no Linux (Wine) falhou → migração para Windows nativo
**Ação:** O teste do MT5 sob Wine no Linux **não funcionou**. A camada de execução
migra para **Windows 11 nativo**. Runbook operacional criado:
[`RUNBOOK-WINDOWS.md`](../runbooks/RUNBOOK-WINDOWS.md).
**Impacto:** Reverte `DECISION-MEMO-LINUX-OR-WINDOWS.md` (Opção B = Linux+MT5/Wine)
e ressuscita parte da variante Windows arquivada. O **cockpit** (backend/frontend/
banco) é multiplataforma e não muda; muda **como o MT5 roda**.
**Pendência de gate (ARCH — Oscar + Voltaire + Grace + Vint):**
1. ADR formal "Windows+MT5 nativo revoga Linux+Wine".
2. Atualizar `project/STACK-CAM-OFICIAL.md` (hoje diz Linux+MT5/Wine) + DECISION-MEMO.
3. `mt5_wine_prefix` → deprecado/no-op; documentar `mt5_terminal_path` (Windows).
4. Kevin revalida perímetro de execução no novo SO (DEMO-only, allowlist OrderSend).
**Estado:** runbook operacional disponível; **stack canônica ainda registra Linux**
(divergência conhecida, sinalizada no topo do RUNBOOK-WINDOWS §11).

---

*TODOs adicionados nos Blocos D–H serão appendados abaixo conforme produção avança.*

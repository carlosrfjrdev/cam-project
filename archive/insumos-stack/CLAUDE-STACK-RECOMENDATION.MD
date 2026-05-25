# CaM — Recomendação de Stack Técnica

**Projeto:** CaM — The Carlos Alternative Money
**Documento:** Stack Recommendation
**Versão:** 1.0
**Status:** Recomendação técnica para Fase 0
**Autor:** Voltaire (revisão crítica) + Grace (arquitetura)
**Vinculação:** Constituição Operacional do CaM v1.0

---

## 1. Resumo Executivo

O CaM é um cockpit local, pessoal e não-produto. Isso muda todas as decisões: não há tenant, não há multiusuário, não há deploy em cloud, não há SLA externo. A stack precisa ser **simples, robusta, observável e auditável** — e precisa rodar no mesmo host do Profit (Windows) porque a `ProfitDLL` é nativa Windows.

**Stack em uma frase:** Backend Python 3.12 com FastAPI, frontend React 19/Vite/MUI, PostgreSQL 16 + TimescaleDB, integração Profit via `ProfitDLL` por `ctypes`, observabilidade via logs estruturados + dashboard próprio + bot Telegram, tudo rodando nativo no Windows do operador.

---

## 2. Princípios da Stack

Cada decisão de stack abaixo deriva de pelo menos um destes princípios:

1. **Soberania da Constituição** — a stack precisa permitir que o Risk Engine seja módulo isolado, testável e auditável (Art. 15º). Frameworks que acoplam regra a infraestrutura estão fora.

2. **DRY entre backtest e live** — as funções de sinal de estratégia executadas em backtest, paper e produção são literalmente as mesmas. Qualquer divergência é fonte de surpresa cara. Isso exclui ferramentas que obrigam reescrita.

3. **Localidade absoluta** — nada no cockpit depende de serviço externo para funcionar. Cloud é opcional para backup, nunca para operação.

4. **Custo controlado** — Art. 8º diz que custos saem do bolso do operador, fora do CaM. Então a stack favorece open source e ferramentas com tier gratuito robusto. Premium só se justificado.

5. **Familiaridade do operador** — onde existe escolha entre duas ferramentas tecnicamente equivalentes, prevalece a que está alinhada com a stack Teczilabs (Monnezy: NestJS, Prisma, React/Vite, MUI). Isso reduz custo cognitivo e permite reaproveitamento.

6. **Auditabilidade** — todo evento operacional gera registro estruturado, imutável e datado. Stack inteira é orientada a log.

7. **Falha segura** — em qualquer falha técnica, o sistema deve degradar para "não envia ordem" e nunca para "executa ordem fora de regra".

---

## 3. Restrições e Premissas

| Item | Valor | Origem |
|---|---|---|
| SO de execução | Windows 10/11 | `ProfitDLL` é Windows-only |
| Plataforma broker | Profit Pro (Nelogica) | Definição do operador |
| Interface broker | `ProfitDLL` via `ctypes` | Única forma oficial suportada |
| Capital declarado | R$ 5.000,00 | Constituição Art. 7º |
| Modelo de uso | Mono-usuário, local | Constituição Art. 1º |
| Custo da stack | Absorvido pelo PF, fora do CaM | Constituição Art. 8º |

---

## 4. Stack Recomendada — Visão Geral

| Camada | Tecnologia | Versão alvo | Justificativa curta |
|---|---|---|---|
| Execução broker | Profit Pro + `ProfitDLL` | atual | única integração oficial |
| Linguagem backend | Python | 3.12.x | maturidade async, type hints, ecossistema quant |
| Framework web/API | FastAPI | 0.115+ | async nativo, OpenAPI, WebSocket |
| ASGI server | Uvicorn | 0.32+ | padrão FastAPI |
| ORM | SQLAlchemy 2.0 | 2.0.x | maduro, async, type-safe |
| Migrations | Alembic | 1.13+ | padrão SQLAlchemy |
| Banco principal | PostgreSQL | 16 | confiável, conhecido, Monnezy usa |
| Time series | TimescaleDB | 2.x | extensão Postgres, ideal para tick/candle |
| Cache/Eventos | Redis (opcional) | 7.x | event bus persistente se necessário |
| Frontend | React + Vite | 19.x / 6.x | alinhado Monnezy |
| UI Library | MUI | 9.x | alinhado Monnezy |
| Gráficos candles | TradingView Lightweight Charts | 4.x | open source, padrão da indústria |
| Gráficos métricas | Recharts | 2.x | já no stack Teczilabs |
| Estado frontend | Zustand | 5.x | simples, sem boilerplate Redux |
| Streaming | WebSocket (nativo FastAPI) | — | tempo real sem overhead |
| Notificações | python-telegram-bot | 21+ | canal de alerta fora do cockpit |
| Logs estruturados | structlog | 24+ | JSON, contextual, performático |
| Backtest engine | Custom Python + vectorbt | 0.27+ | DRY + research |
| Testes | pytest + pytest-asyncio + hypothesis | atuais | property-based para Risk Engine |
| Gerência de deps | uv | latest | mais rápido que poetry, padrão emergente |
| Versionamento | Git + GitHub (privado) | — | regra DevFlow |
| Containers | Docker Desktop + WSL2 | atual | apenas para Postgres/Redis |

---

## 5. Detalhamento por Camada

### 5.1 Camada de Execução — `ProfitDLL` Adapter

A `ProfitDLL` é uma DLL nativa Windows (C ABI) exposta pela Nelogica. Acesso de Python via **`ctypes`** (built-in) ou **`cffi`** (mais ergonômico, mas dependência extra). Recomendação: começar com `ctypes`, migrar pra `cffi` se a fricção justificar.

**Responsabilidades do adapter:**

- Inicialização e autenticação na DLL
- Recebimento de eventos (callbacks): cotação, book, trades, retornos de ordem
- Envio de ordens: market, limit, stop
- Consulta de posições e P&L
- Tradução entre tipos da DLL e tipos do domínio Python (dataclasses)

**Isolamento crítico:** o adapter é a única parte do sistema que conhece a `ProfitDLL`. Strategy modules, Risk Engine e journal nunca importam DLL — operam sobre tipos do domínio. Isso permite trocar Profit por MT5 no futuro alterando apenas o adapter, e permite mockar tudo em testes.

**Threading:** as callbacks da DLL chegam em threads próprias da Nelogica. O adapter precisa traduzir isso para o loop async do Python — padrão: callbacks colocam evento em `asyncio.Queue` thread-safe via `call_soon_threadsafe`.

**Atenção:** a `ProfitDLL` evolui de versão. Travar a versão usada em ambiente, documentar incompatibilidades, manter changelog próprio do adapter.

---

### 5.2 Backend — Python + FastAPI

**Por que Python e não Java/TypeScript** (mesmo Carlos sendo backend Java):

- Ecossistema quant: NumPy, pandas, vectorbt, scikit-learn, statsmodels — não tem equivalente em Java.
- Wrapper de DLL via `ctypes` é trivial em Python, complexo em Java (JNI/JNA).
- Notebooks Jupyter para pesquisa de estratégia.
- Comunidade trading-quant é majoritariamente Python.

**Por que FastAPI:**

- Async nativo, casa bem com stream de market data
- WebSocket built-in
- OpenAPI automático (front consome sem dor)
- Pydantic 2 (validação de schema rigorosa)
- Performance compatível com Node

**Estrutura interna recomendada (arquitetura hexagonal leve):**

```
cam/
  domain/           # entidades, value objects, eventos (Pure Python)
  risk/             # Risk Engine (Pure Python, ZERO I/O)
  strategies/       # módulos de estratégia plugáveis
  execution/        # ProfitDLL adapter
  paper/            # Paper trading adapter (mesma interface do execution)
  market_data/      # ingestão e armazenamento
  journal/          # persistência operacional
  fiscal/           # apuração DARF, compensação de prejuízo
  backtest/         # engine de backtest (usa strategies/)
  notifications/    # bot Telegram
  api/              # FastAPI routes + WebSocket
  config/           # pydantic-settings
```

O `risk/` ser pure Python sem I/O é decisão de arquitetura constitucional: o Risk Engine é a parte mais crítica do sistema (Art. 15º), e precisa ser testável em isolamento absoluto, com property-based testing exaustivo. Qualquer ordem que chega na execution layer passou primeiro por uma validação síncrona, determinística, sem dependência de banco ou rede.

---

### 5.3 Camada de Risco — `risk/`

Módulo Python puro. Sem banco, sem HTTP, sem callbacks externos. Recebe `OrderCandidate` + `RiskContext`, retorna `RiskDecision` (`Approved` ou `Rejected(reason)`).

**Validators implementados como funções puras:**

- `max_contracts_check` (Art. 11º, 12º)
- `daily_loss_limit_check` (Art. 16º, POV)
- `weekly_loss_limit_check`
- `monthly_loss_limit_check`
- `gain_lock_check` (Art. 17º)
- `daily_operations_count_check` (Art. 20º)
- `martingale_check` (Art. 13º)
- `trading_window_check` (POV — janelas vedadas)
- `simultaneous_position_check` (Fase 1/2: WIN OU WDO; Fase 3+: ambos)
- `circuit_breaker_check` (3 stops consecutivos, etc.)
- `kill_switch_active_check`
- `tax_compliance_check` (Art. 26º — DARF atrasada bloqueia)
- `phase_authorization_check` (estratégia autorizada na fase atual)

**Cobertura de testes mínima:** 80% (Anexo II — critério de saída de Fase 0). Recomendação prática: **100% no Risk Engine**, sem exceção. Testes incluem property-based via `hypothesis` para gerar cenários adversos que humanos não pensam.

---

### 5.4 Banco de Dados — PostgreSQL 16 + TimescaleDB

Postgres você já domina. Adicionar TimescaleDB (extensão Postgres) resolve o problema de séries temporais sem trocar de banco.

**Schemas sugeridos:**

```sql
-- Domínio operacional (tabelas comuns)
cam.orders
cam.positions
cam.trades
cam.journal_entries
cam.risk_decisions   -- log de toda decisão do Risk Engine
cam.violations       -- registro de violações para cálculo de aderência
cam.constitution_versions
cam.pov_versions
cam.phase_history

-- Fiscal
cam.fiscal_apuration
cam.darf_history
cam.loss_compensation_ledger

-- Hypertables (TimescaleDB)
cam.market_data_ticks        -- por símbolo, com índice de tempo
cam.market_data_candles_1m
cam.market_data_book_snapshots

-- Backtest
cam.backtest_runs
cam.backtest_trades
```

**Política de retenção:** mercado bruto pode ter retenção de 90–180 dias (hypertable com compressão TimescaleDB depois de N dias). Journal, risk_decisions, violations: retenção infinita (são memória institucional do CaM).

**Migrations:** Alembic com convenção de naming consistente. Cada emenda à Constituição que altere parâmetros operacionais pode gerar migration de POV.

---

### 5.5 Frontend — React 19 + Vite + MUI

Stack idêntica ao Monnezy. Reaproveitamento de componentes, padrões e tooling.

**Telas mínimas para Fase 0:**

1. **Cockpit Live** — dashboard principal
   - P&L do dia (líquido após imposto provisionado)
   - Posições abertas
   - Status do Risk Engine (verde/amarelo/vermelho com razão)
   - Botão Kill Switch grande, vermelho, com confirmação dupla
   - Gauge dos limites diário/semanal/mensal
   - Estado do circuit breaker
   - Próximo evento macro (janela vedada se aplicável)

2. **Trade Journal** — listagem e detalhe das operações com filtros, exportação

3. **Estratégias** — habilitar/desabilitar (com cooldown!), parâmetros vigentes, histórico

4. **Risk Console** — visualização da POV vigente, gauges de exposição, log de decisões do Risk Engine

5. **Backtest** — executar backtest de estratégia, comparar com baseline, walk-forward

6. **Paper Trading** — mesma UI do Live, mas com badge "PAPER" em vermelho gigante

7. **Carteira Hard** — snapshot patrimonial, dividendos recebidos, histórico de harvest

8. **Fiscal** — apuração mensal, DARF a pagar, compensação de prejuízo, alerta de vencimento

9. **Constituição** — visualização read-only da Constituição e POV vigentes, com histórico de versões. Botão de "propor emenda" abre fluxo separado com cooldown

10. **Configurações** — perfil de conexão Profit, Telegram, paths, etc.

**Estado:** Zustand para estado de UI. Server state via React Query (Tanstack Query) com WebSocket subscriptions.

**Gráficos:**
- TradingView Lightweight Charts para candles em tempo real
- Recharts para P&L histórico, drawdown, distribuição de resultados

---

### 5.6 Backtest Engine

**Decisão crítica:** engine próprio, não Backtrader.

**Por quê:**

- DRY entre backtest e live é requisito constitucional. Backtrader força você a escrever estratégia como classe deles. Migrar pra produção significa reescrever — ponto de divergência inaceitável.
- Engine próprio mínimo permite que a função de sinal em `strategies/minha_estrategia.py` seja chamada exatamente da mesma forma em backtest, paper e live.

**Estrutura:**

```python
# strategies/donchian_breakout.py
def generate_signal(context: MarketContext) -> Optional[Signal]:
    ...

# backtest/engine.py
def run_backtest(strategy_fn, market_data, risk_engine, initial_capital):
    for tick in market_data:
        context = build_context(tick)
        signal = strategy_fn(context)
        if signal:
            order = build_order(signal)
            decision = risk_engine.evaluate(order, current_state)
            if decision.approved:
                fill_simulated_order(order)
```

**vectorbt:** ferramenta paralela, não obrigatória, para research e exploração rápida de hipóteses ANTES de uma estratégia virar módulo. Não substitui o engine custom.

**Walk-forward:** automatizado, parametrizado por janela de treino, janela de teste, step. Resultado em formato consumível pelo frontend.

---

### 5.7 Paper Trading

Mesma arquitetura do live, com `PaperExecutionAdapter` no lugar do `ProfitDLLAdapter`. Implementa mesma interface (`IExecutionAdapter`).

Diferenças:
- Recebe market data real via ProfitDLL (read-only)
- Não envia ordens; simula fill com latência configurável e slippage configurável
- Escreve no journal com flag `mode=paper`
- Frontend mostra badge PAPER em vermelho contínuo

**Modo recomendado de Fase 1:** paper rodando no mesmo binário do backend live, mas com flag de execução em modo paper. Reduz risco de divergência de versão entre paper e live.

---

### 5.8 Observabilidade

**Logs:** `structlog` configurado para JSONL. Rotação diária. Path: `~/.cam/logs/`.

Eventos logados em todos os pontos críticos:
- `signal_generated`
- `order_candidate_built`
- `risk_decision` (approved/rejected + razão)
- `order_sent`
- `order_filled`
- `position_closed`
- `daily_limit_reached`
- `kill_switch_activated`
- `phase_transition`
- `constitution_emendation_proposed`
- `pov_change_applied`

**Métricas:** sem Prometheus/Grafana neste estágio. O próprio dashboard React consome via WebSocket e exibe.

Se evoluir: Grafana + Prometheus rodando em docker-compose. Mas é provavelmente overkill para mono-operador.

**Crash:** Sentry self-hosted é overkill. Logs em arquivo + alerta Telegram já cobrem.

---

### 5.9 Notificações — Bot Telegram

Canal externo de alerta independente do cockpit. Se o cockpit cair, o Telegram ainda funciona.

**Eventos críticos enviados:**

- 🔴 Kill switch ativado (com motivo)
- 🔴 Daily/weekly/monthly loss limit atingido
- 🟡 Stop executado
- 🟢 Gain lock atingido — dia encerrado
- 🟡 Falha técnica detectada (ProfitDLL não responde, etc.)
- 🟡 Posição aberta sem cobertura sistêmica (callback perdido, etc.)
- 🔵 Resumo diário pós-mercado
- 🔵 Apuração mensal disponível
- 🟠 DARF vence em N dias
- 🟣 Backtest finalizado com resultado X

Biblioteca: `python-telegram-bot` (síncrona) ou `aiogram` (async, recomendada — combina com FastAPI).

---

### 5.10 Testes

```
tests/
  unit/
    test_risk_engine/        # ALTA cobertura, property-based
    test_strategies/
    test_journal/
    test_fiscal/
  integration/
    test_execution_adapter/  # mocked DLL
    test_paper_adapter/
    test_api/
  e2e/
    test_full_trade_lifecycle/   # signal → risk → execution → journal
    test_kill_switch_flow/
    test_circuit_breaker_flow/
  property/
    test_risk_invariants/    # hypothesis: nenhuma combinação de inputs viola constituição
```

**Métricas obrigatórias antes de Fase 1:**
- Risk Engine: 100% line + branch
- Strategies: ≥ 90% (cada uma)
- Execution adapter: ≥ 80%
- Global: ≥ 80% (critério de saída de Fase 0 do Anexo II)

---

### 5.11 Módulo Fiscal

Subsistema próprio, não terceirizar para planilha. Razões:

- Provisão fiscal em tempo real é requisito do Art. 25º
- Compensação de prejuízo (Art. 27º) precisa de ledger persistente
- DARF atrasada bloqueia operação (Art. 26º) — sistema precisa saber

**Capacidades mínimas:**

- Apuração mensal automática (day trade derivativos: 20% sobre lucro líquido mensal)
- IRRF de 1% retido considerado como crédito
- Ledger de prejuízos acumulados compensáveis
- Cálculo de DARF mensal a pagar
- Lembretes (Telegram) de vencimento (último dia útil do mês seguinte)
- Bloqueio operacional automático se DARF do mês anterior não marcada como paga
- Relatório anual para IRPF

**Não fazer:** integração com Receita Federal. Cálculo é interno, pagamento é manual pelo operador via DARF gerado pelo e-CAC.

---

### 5.12 IA — Integração

Conforme Art. 34º–36º, a IA é instrumento auditor/analista, **não autoridade de execução**.

**Integrações úteis:**

- **Anthropic API (Claude)**: análise post-mortem de trades, code review de estratégias, geração de relatórios, sugestão de hipóteses
- **Não integrar IA em loop de execução em tempo real**

**Onde a IA roda:**

- Em job assíncrono pós-mercado: lê journal do dia, gera análise narrativa, envia para o operador
- Em endpoints da API acionados manualmente pelo operador no frontend
- Em CLI de research separada (fora do binário live)

**Onde a IA NÃO roda:**

- No path de geração de sinal de uma estratégia em produção
- No Risk Engine (que é determinístico por Constituição)
- Como justificadora de exceção a regra (Art. 35º)

---

### 5.13 DevOps Local

**Ambiente do operador:**

- Windows 11 (ambiente do Profit)
- Python 3.12 instalado nativo no Windows (para acessar ProfitDLL)
- Docker Desktop com WSL2 (para Postgres + Redis em containers)
- Node 20 LTS + pnpm para o frontend
- VS Code + Claude Code

**docker-compose.yml (apenas serviços de infra):**

```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    ports: ["5432:5432"]
    volumes: [cam_pg:/var/lib/postgresql/data]
    environment: { POSTGRES_DB: cam, ... }

  redis:                 # opcional, só se usar event bus persistente
    image: redis:7-alpine
    ports: ["6379:6379"]
```

**Inicialização do backend:** nativa no Windows (`uv run uvicorn ...`), porque precisa acessar a DLL.

**Backup:**

- `pg_dump` diário automatizado para `~/cam-backups/`
- `rclone` para sync com cloud (Google Drive ou S3) — opcional mas recomendado
- Journal em JSONL versionado no Git em repositório privado separado (commit diário automático)

---

## 6. Alternativas Consideradas e Por Que Não

| Tecnologia | Por que não |
|---|---|
| MetaTrader 5 em vez de Profit | Decisão do operador. MT5 seria viável (MQL5 conhecido), mas Profit já está escolhido. Adapter futuro fica viável pela arquitetura hexagonal. |
| Backtrader | Acopla estratégia a framework próprio, quebra DRY backtest↔live. |
| Zipline | Descontinuado pela Quantopian, manutenção comunitária irregular. |
| QuantConnect / LEAN | Cloud-first, contra o princípio de localidade absoluta. |
| Java / Spring Boot no backend | Ecossistema quant em Python é incomparavelmente melhor. JNI/JNA para ProfitDLL é doloroso. Familiaridade Java do operador é melhor aplicada no Factory/Service. |
| NestJS no backend | Mesmo problema: ecossistema quant em Python. Coerência com Monnezy é menos importante que coerência com a natureza do problema. |
| TypeScript no backend | Mesmo problema do NestJS. |
| Mantine em vez de MUI | Mantine tem componentes de dashboard mais ricos, mas perder alinhamento com Monnezy não compensa. |
| MongoDB | Sem necessidade de schema-flexível. Postgres + JSONB resolve casos pontuais. |
| Kafka / RabbitMQ | Overkill para mono-operador. Redis Streams ou asyncio.Queue resolvem. |
| Microserviços | Anti-padrão para mono-operador. Monolito modular. |
| Cloud (AWS/GCP/Railway) | Contra princípio de localidade. Cloud só para backup. |
| Tauri / Electron como wrapper | Não há necessidade. Backend FastAPI + frontend Vite servido como SPA local resolve. |
| Docker para o backend | ProfitDLL é Windows-only. Backend precisa rodar nativo. |

---

## 7. Estrutura de Repositório

Padrão DevFlow Teczilabs (repositórios independentes):

```
teczi-cam/                        # backend Python
  cam/
    domain/
    risk/
    strategies/
    execution/
    paper/
    market_data/
    journal/
    fiscal/
    backtest/
    notifications/
    api/
    config/
  tests/
  scripts/
  migrations/                     # alembic
  pyproject.toml
  uv.lock
  README.md
  .env.example

teczi-cam-web/                    # frontend React
  src/
    features/
      cockpit/
      journal/
      strategies/
      risk-console/
      backtest/
      paper/
      hard-portfolio/
      fiscal/
      constitution/
      settings/
    shared/
    lib/
    api/
  package.json
  vite.config.ts
  README.md

teczi-cam-docs/                   # documentação operacional
  constitution/
    v1.0.txt
    emendments/
  pov/
    v1.0.md
    history/
  spec/
  arch/
  plan/
  runbooks/
    daily-routine.md
    incident-response.md
    fiscal-monthly.md
```

Regra DevFlow: branch `dev`, nunca commit em `main`, Conventional Commits PT-BR.

---

## 8. Fase 0 — Sequenciamento de Construção

Não construir nessa ordem é convidar retrabalho. Ordem proposta:

1. **Domain + Risk Engine + testes** (semana 1–2)
   Pure Python, sem I/O. Build com TDD obsessivo. Property-based testing. Critério: 100% cobertura no Risk Engine, todos os artigos relevantes da Constituição cobertos por teste nomeado (ex: `test_art_11_max_contracts_absolute`).

2. **Journal + Migrations + Banco** (semana 2)
   PostgreSQL + TimescaleDB up, schemas migrados, journal funcional.

3. **ProfitDLL Adapter — read-only** (semana 3)
   Apenas recebe market data e callbacks. Não envia ordem ainda. Valida conexão, parsing, threading correto.

4. **Paper Execution Adapter** (semana 3–4)
   Implementa interface de execução, mas simula fill. Permite testar pipeline end-to-end sem risco.

5. **Pipeline e2e em paper** (semana 4)
   Uma estratégia trivial (ex: random ou buy-and-hold sintético) → signal → risk → paper execution → journal. Verifica que tudo conversa.

6. **Frontend mínimo** (semana 4–6, paralelizável)
   Cockpit Live + Risk Console + Journal. Suficiente para observar o paper rodando.

7. **ProfitDLL Adapter — envio de ordens** (semana 6)
   Após pipeline e2e validado. Implementa envio real, mas ainda com flag global `PRODUCTION_ALLOWED = False`. Testes em conta de simulação da corretora (se disponível) ou paper interno.

8. **Backtest engine + walk-forward** (semana 6–8)
   Mesmos módulos de estratégia. Output consumível pelo frontend.

9. **Módulo Fiscal** (semana 7–8)
   Apuração mensal, DARF, compensação de prejuízo, integração com bloqueio operacional.

10. **Notificações Telegram** (semana 8)
    Bot configurado, eventos críticos cobertos.

11. **Kill Switch hardening + Circuit Breaker** (semana 9)
    Testes de cenário extremo: queda de DLL com posição aberta, perda de internet, etc.

12. **Critérios de saída de Fase 0 verificados** (semana 10)
    Cobertura ≥ 80% global, ≥ 100% no Risk Engine, kill switch validado, pipeline backtest + paper funcionais.

Estimativa: **8 a 12 semanas** de Fase 0 com dedicação compatível com sua rotina Porto + Monnezy beta. Não acelere isso. A Fase 0 é onde se constrói a segurança que protege o capital nas fases seguintes.

---

## 9. Custos da Stack — Realismo

Conforme Art. 8º, custos saem do bolso do operador, fora do CaM. Estimativa de custo mensal recorrente:

| Item | Custo aproximado | Obrigatório? |
|---|---|---|
| Profit Pro com book (Nelogica) | R$ 200–300/mês | Sim |
| Conta corretora vinculada | corretagem por trade | Sim |
| Dados de mercado adicionais | incluso no Profit | — |
| Cloud para backup (opcional) | R$ 0–30/mês | Não, mas recomendado |
| Anthropic API (uso analítico) | R$ 0–50/mês | Não, sob demanda |
| GitHub privado | R$ 0 (free tier) | Sim |
| Telegram | R$ 0 | Sim |
| PostgreSQL/TimescaleDB | R$ 0 (open source) | Sim |
| Resto da stack | R$ 0 (open source) | — |

**Total mensal típico:** R$ 200–380.

**Observação dura mas honesta:** isso é 4–8% ao mês sobre o capital declarado de R$ 5.000. O sistema precisa gerar **expectância líquida positiva acima desse patamar** antes de o operador parar de queimar caixa pessoal mantendo a operação. Esse é o **edge mínimo de sobrevivência**, e ele deve ser explícito desde o backtest. Backtest que ignora custos de plataforma está mentindo.

---

## 10. Riscos da Stack

**R1 — ProfitDLL evolui sem aviso e quebra adapter.**
Mitigação: travar versão da DLL, manter changelog próprio, testes de smoke do adapter executados antes de cada pregão.

**R2 — Windows não é o ambiente de desenvolvimento ideal para Python async.**
Mitigação: WSL2 para desenvolvimento e testes; deploy "produção local" no Windows nativo. CI no GitHub Actions com matriz Windows.

**R3 — Vazamento de credenciais da corretora.**
Mitigação: secrets em `.env` nunca versionado; pré-commit hook bloqueando padrões de chave; opção futura: Windows Credential Manager via `keyring`.

**R4 — Acoplamento acidental entre Risk Engine e infraestrutura.**
Mitigação: import linter configurado para impedir que `risk/` importe de `execution/`, `journal/`, etc. Falha de build se violar.

**R5 — Backtest divergir do live por divergência de feature engineering.**
Mitigação: contrato `MarketContext` único, mesmo construtor em todos os modos. Testes de paridade backtest/paper.

**R6 — Performance: stream de tick em Python pode gargalar.**
Mitigação: profiling desde início. Se necessário, hot path em Cython/Rust. Improvável em 1 símbolo + 1 estratégia, mas planejar margem.

**R7 — Operador desligar/contornar Risk Engine "só por hoje".**
Mitigação técnica + constitucional. Tecnicamente: `PRODUCTION_ALLOWED` flag verificada em build e em runtime; alterar exige edição de arquivo versionado + cooldown. Constitucionalmente: Art. 38º.

**R8 — Falha catastrófica do banco com posição aberta.**
Mitigação: journal em duplo escrito (Postgres + JSONL append-only em disco local). Em falha de Postgres, sistema entra em modo degradado que ainda envia ordem mas só após confirmação humana via Telegram + escreve em JSONL. Recovery posterior.

---

## 11. O Que Esta Stack NÃO É

- Não é uma stack para vender. CaM não é produto.
- Não é uma stack multiusuário. Sem auth, sem tenant.
- Não é uma stack escalável horizontalmente. Mono-host por design.
- Não é uma stack para low-latency HFT. Latência alvo: dezenas de ms, não microssegundos.
- Não é uma stack para múltiplos brokers em paralelo. Adapter único.
- Não é uma stack para arbitragem cross-venue. Single venue (B3 via Profit).

Se algum dia o CaM virar ferramenta vendável (improvável e desencorajado pela Constituição), praticamente nada disso se aproveita — então não otimize prematuramente para esse cenário.

---

## 12. Próximas Decisões Pendentes

Antes da SPEC formal, três decisões abertas:

1. **Versão da `ProfitDLL`**: levantar a documentação oficial atual junto à Nelogica e travar versão alvo. Definir antes do início da semana 3.

2. **Tese de edge da primeira estratégia**: continua pendente da conversa anterior. Sem essa decisão, a Fase 0 constrói infraestrutura sem destino conhecido — o que ainda é válido (a infra é genérica), mas a definição de "Setup A+" futuro depende disso.

3. **Corretora**: o Profit roda integrado com várias. Cada uma tem custo de corretagem diferente para mini contratos. Como o edge mínimo é função direta do custo por trade, a escolha de corretora deve ser tratada como decisão de arquitetura financeira, não administrativa.

---

**Fim do documento.**

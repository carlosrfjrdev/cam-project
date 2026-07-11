# 🧭 ORIENTAÇÃO — Mapa de navegação do repositório CaM

> **Comece por aqui.** Este é o **ponto único de entrada** para se orientar no repo:
> onde cada coisa mora e o que está **vivo / stub / morto**. Para *instruções de
> agente* veja [`CLAUDE.md`](../CLAUDE.md); para *visão de produto* (8 módulos
> Assets*) veja [`project/tcam/MAP-MODULES-TCaM.md`](./tcam/MAP-MODULES-TCaM.md).
>
> Última atualização: 2026-06-30 (reorg Fase A).

---

## 1. Onde mora o quê (topo do repo)

| Pasta | É o quê | Quando abrir |
|---|---|---|
| [`apps/`](../apps/) | **Estado real — código que roda.** `cam-cockpit` (backend/frontend) + `trader-robots` (mql5/ntsl). | "O que de fato existe e executa" |
| [`project/`](.) | **Intenção viva — docs, SCOPE/SPEC/PLAN/ADR, runbooks, análises.** | "O que está sendo decidido/construído" |
| [`personas/`](../personas/) | Cast de 5 times (agentes) — fonte autoritativa em `personas/README.md`. | Saber quem faz o quê |
| [`teczi-devflow/`](../teczi-devflow/) | Framework de processo NCC-1701 (fases/estados/governança). | Como construir |
| [`archive/`](../archive/) | Memória histórica (Constituição morta, insumos legados). | Só consulta histórica |
| `data/` *(gitignored)* | Massa de dados local (relatórios de trade com PII, CSVs). **Nunca commitado.** | Rodar análises |

> **Regra mestra:** quando `apps/` (real) divergir de `project/` (intenção),
> **o estado real vence** (NCC-1701 §2). Doc `.md` de documentação **não** entra
> em `apps/` — só `README.md` e arquivos de instrução de agente.

**Subir o cockpit:** `apps/start-cam.ps1` (launcher: banco Docker + backend + frontend).
Setup inicial: `apps/cam-cockpit/scripts/dev.ps1`. Runbook completo:
[`project/tcam/runbooks/RUNBOOK-WINDOWS.md`](./tcam/runbooks/RUNBOOK-WINDOWS.md).

---

## 2. Backend — 25 features (`apps/cam-cockpit/backend/cam/features/`)

Estado: ✅ vivo · 🟡 stub/casca · 💀 morto/deprecado (remover)

### Dados & mercado
| Feature | O que faz | Estado |
|---|---|---|
| `mt5_integration` | Bridge ZeroMQ p/ MetaTrader 5 (candles/ticks/book, read-only). **Central.** | ✅ |
| `market_data` | Ingestão de tick/candle (parser CSV de ticks). | ✅ |
| `profit_bridge` | Ticks read-only do Profit via ProfitDLL (scaffold market-data). | ✅ |
| `profit_integration` | Integração broker Profit — **DESATIVADA em 2026-05-25**. | 💀 |
| `fundamentals` | Indicadores fundamentalistas (R-20), alimenta o Inspector. | ✅ |
| `regime` | Overlay de Regime de Markov (Bull/Sideways/Bear), read-only. | ✅ |

### Análise & pesquisa
| Feature | O que faz | Estado |
|---|---|---|
| `trade_analyzer` | Sobe CSV do Profit → métricas + **MAE/MFE** (candles) + IA. ⚠️ **sem testes.** | ✅ |
| `operation_analyzer` | "Sinaliza operações" — **CASCA Fase 0** (engine não implementada). Mas seu `chart_service` é real e reusado pelo `trade_analyzer`. | 🟡 |
| `research` | Lead-lag cross-asset + pattern lab (Quant Lab). | ✅ |
| `ai_analyst` | Providers de IA (Anthropic / OpenAI / DeepSeek / Ollama) — capacidade transversal. | ✅ |

### Estratégia & execução
| Feature | O que faz | Estado |
|---|---|---|
| `strategies` | Catálogo + ciclo de vida de estratégias (+ `dsl`). | ✅ |
| `strategy_lab` | Backtest determinístico + EvidencePack (expectância/payoff/drawdown). | ✅ |
| `backtest` | Motor de backtest matemático (domain/simulator/walk_forward). | ✅ |
| `paper_trading` | Operação simulada (validação). | ✅ |
| `robot_orchestrator` | Multiestratégia / orquestração de robôs. | ✅ |
| `scaling` | Strategy Escalation Engine (escalonamento). | ✅ |

### Risco & governança
| Feature | O que faz | Estado |
|---|---|---|
| `kill_switch` | Trava de emergência (parte do Risk). | ✅ |
| `checklists` | Ritual pré/pós-mercado (disciplina — reavaliar p/ produto). | ✅ |
| `constitution` | Documento soberano — **deprecado** pós-decommission (2026-06-03). | 💀 |
| `app_settings` | Preferências de runtime (provider de dados etc.). | ✅ |
| `notifications` | Alertas via Telegram. | ✅ |

### Carteira & fiscal (BR / pessoal — reavaliar p/ produto)
| Feature | O que faz | Estado |
|---|---|---|
| `ledger` | Razão / holdings (carteira). | ✅ |
| `harvest` | Coleta/colheita de dados de carteira. | ✅ |
| `journal` | Diário de operações duplo (banco + JSONL em `~/.cam/journal/`). | ✅ |
| `fiscal` | Apuração fiscal (DARF / IR 20% / IRRF). | ✅ |

> Risco compartilhado em `cam/_shared/risk` (Risk Engine — vira feature **Assets
> RiskManager** configurável, não mais "lei"). Kernel de pesquisa em
> `cam/_shared/research_kernel` (`bars`, `indicators`, `levels`, validação WF).
> **Acoplamento entre features é por TABELA de banco, não import direto** (ADR-013,
> enforçado por import-linter).

---

## 3. Frontend — telas (`apps/cam-cockpit/frontend/src/features/`)

`cockpit` · `inspetor` · `quant-lab` · `research` · `strategies` · `strategy-lab`
· `backtest` · `paper-trading` · `robot-orchestrator` · `ea-control`
· `order-gateway` · `risk-console` · `scaling` · `market-data` · `dataset`
· `journal` · `fiscal` · `harvest` · `carteira-hard` · `trade-analyzer`
· `operation-analyzer` · `constitution` *(deprecada)* · `settings`

---

## 4. Robôs (`apps/trader-robots/`)

| Caminho | Conteúdo |
|---|---|
| `mql5/experts/` | EAs MetaTrader: executores (ORB-30, VWAP, híbridos), **`cam_disciplina_2c.mq5`** (gestor de saída disciplinada p/ entradas manuais), gravadores, `cam_risk_mirror.mq5` (guard-rails), `cam_bridge.mq5` (ZeroMQ). |
| `ntsl/` | Executores Profit (NTSL): `cam_d1_orb30`, `cam_d2_vwap`, **`cam_disciplina_2c`** (paridade), `risk_mirror` (casca). |
| Docs/política | [`project/trader-robots/`](./trader-robots/) — `POLITICA-ROBOS.md` (ciclo INDEV→APROVADO, validação tripla Profit×MT5×CAM), fichas por robô, `manualNTSL.md`. |

---

## 5. Documentação em `project/`

| Tipo | Onde |
|---|---|
| Virada p/ produto (PIVOT, DECOMMISSION, MAP de módulos) | `project/tcam/` |
| ADRs | `project/tcam/adrs/` |
| Runbooks | `project/tcam/runbooks/` *(consolidado — único local)* |
| SCOPE / SPEC / PLAN / QA / PROOF-PACK | `project/cam-cockpit/{scopes,specs,plans,...}` |
| Robôs (política, fichas) | `project/trader-robots/` |
| Stack oficial | `project/STACK-CAM-OFICIAL.md` |

---

## 6. Trabalho em andamento (2026-06-30)

**Reorganização + Motor estatístico de trades + Robô executor de disciplina.**
Plano e diagnóstico: análise da massa `data/trade-reports/trades-30dias.csv` provou
assimetria de saída (payoff 0,90:1 vs 1:3 pretendido). Em construção:
- **Motor** (Camada 2): MAE/MFE × regime → stop/alvo ótimos. Base no `trade_analyzer`.
- **Executor** (Camada 1): robô 2-contratos (C1 alvo curto, C2 breakeven+trailing) +
  guard-rails. NTSL + MQL5 em paralelo. Base reusa `cam_risk_mirror.mq5`.

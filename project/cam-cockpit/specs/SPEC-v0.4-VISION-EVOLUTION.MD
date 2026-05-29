---
template: SPEC
phase: SPEC
status: Draft
version: 0.4
date: 2026-05-27
parent_spec: SPEC-v0.3-TECH-DEBT-REVIEW.md
companions:
  - CAM-VISION-FINAL.MD (v1.1)
  - SCOPE-Vision-Evolution.md (v1.1)
demand_id: SPEC-v0.4-VISION-EVOLUTION
pmg: G
sec: true
qa_sec: true
---

# SPEC v0.4 — Vision Evolution (9 blocos consolidados)

> **Lead:** Albert (especificação) · **Co-lead:** Kevin (`sec` + `qa-sec`)
> **Orchestrator:** Leo
> **Skill:** `teczi-demand-specification`
> **Aprovador:** Founder
> **Origem:** [`CAM-VISION-FINAL.MD`](./CAM-VISION-FINAL.MD) (v1.1) + [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md) (v1.1).
>
> **Esta SPEC é única.** Consolida as antigas numerações v0.4, v0.4b, v0.5, v0.5b, v0.6, v0.6b, v0.7, v0.8, v0.9 em **9 blocos** (BL-A a BL-I) de uma só SPEC. Founder decidiu em 2026-05-27 que numeração separada por versão era ruído.

---

## 1. Contexto

Após VISION-FINAL e respostas do Founder, ficou claro que o CaM precisa entregar uma evolução ampla (Strategy Lifecycle, Market Data, AI Workbench, Carteira Hard, Cross-Asset, Orchestrator) **sem fragmentar em múltiplas releases**. A SPEC v0.4-VISION-EVOLUTION é a especificação **única** dessa evolução, organizada em 9 blocos com pré-requisitos explícitos.

### 1.1 Decisões formais vinculantes (já registradas em VISION-FINAL §4)

| Ref | Decisão (resumo) |
|---|---|
| **R-17** | Corretora vinculada: **Genial Investimentos** |
| **R-18** | S1 ORB 60m WIN **APROVADA** como primeira estratégia |
| **R-19** | Multiestrategia **APROVADA com emenda** (TD-v0.4-03 — cooldown 30 dias) |
| **R-20** | 7 indicadores fundamentalistas: `DY` (peso forte), `P/L`, `P/VP`, `ROE`, `Dívida Líq/EBITDA`, `Payout`, `ROIC` |
| **R-21** | Scraping multi-fonte fica como **TD-v0.4-01** |
| **R-22** | OpenAI fica como **TD-v0.4-02** — default permanece Ollama + Anthropic |

### 1.2 O que esta SPEC **é**

- Especificação consolidada de 9 blocos (BL-A a BL-I) cobrindo Strategy Lifecycle, Market Data Platform, Paper Loop Governado, Carteira Hard, Read-write MT5 demo, Fundamentalistas, Cross-Asset Research, Robot Orchestrator, Multi-EA/DSL.
- Vinculação direta com Constituição (Arts. 11, 12, 15, 18, 23, 25, 28, 29, 31, 35, 36) + POV vigente.
- Critérios de aceite por bloco + global da SPEC.

### 1.3 O que esta SPEC **NÃO é**

- **Não declara v1.0 do CaM.** Versão 1.0 é declaração exclusiva do Founder.
- **Não libera operação real.** `REAL_TRADING_ALLOWED=false` permanece padrão obrigatório.
- **Não toca Constituição** (exceto via emenda multiestratégia, registrada como TD-v0.4-03).
- **Não revoga SPECs anteriores** (v0.1, v0.2, v0.3) — estende.

---

## 2. Escopo

### 2.1 In (faz parte desta SPEC)

Todos os 9 blocos abaixo:

| Bloco | Foco | Trilhas |
|---|---|---|
| **BL-A** | Strategy Lifecycle + Autonomy Matrix + EA Control Plane Base | A + B parcial |
| **BL-B** | Market Data Provenance + Tick Histórico | C |
| **BL-C** | Paper Loop Governado + AI Real | A + D |
| **BL-D** | Carteira Hard Holdings + Importação Genial | E |
| **BL-E** | Read-write MT5 DEMO + `cam_risk_mirror.mq5` | B G3 |
| **BL-F** | Dividendos + Fundamentalistas + Policy Engine | E |
| **BL-G** | Cross-Asset Research + Pair Trade + AI Workbench | D + F |
| **BL-H1** | Robot Orchestrator + Multiestratégia (Art. 11-A) | A + F |
| **BL-H2** | Strategy Escalation Engine (Art. 11-B) | A |
| **BL-I** | Multi-EA + DSL Strategy Layer | A + B |

### 2.2 Out (NÃO faz parte desta SPEC)

- ❌ Operação **real** (mesmo com S1 aprovada) — exige emenda + Fase 2+ + decisão Founder
- ❌ Indicadores fundamentalistas além dos 7 da R-20 (extensão fica para SPEC própria)
- ❌ OpenAI sem ADR (TD-v0.4-02)
- ❌ Scraping de fontes sem ToS validado (TD-v0.4-01)
- ❌ HFT / scalping de alta frequência
- ❌ No-code visual builder
- ❌ Produto comercial / SaaS

### 2.3 Later (não desta SPEC)

- 🔜 Real trading governado — Founder declara em SPEC futura
- 🔜 Cross-broker (MT5 já é cross-broker mundial; integração com outros viria por SPEC própria)
- 🔜 ML quant puro (sklearn/torch sem LLM)

---

## 3. Princípios vinculantes globais

Estes princípios se aplicam **em todos os 9 blocos**. Violação = SPEC inválida.

1. **Risk Engine intocável** exceto para extensões aditivas (validators novos sem remover existentes — Art. 15).
2. **Order Gateway único:** `Strategy/Robot → Risk Engine → OrderCommand → EA MT5 → Fill → Journal/Fiscal/Audit`. Sem caminho paralelo.
3. **`REAL_TRADING_ALLOWED=false`** por design em toda release.
4. **1 estratégia ativa em produção** até TD-v0.4-03 (emenda) cumprida e BL-H entregue.
5. **Bridge MQL5 = mirror/executor.** Nunca decide ordem fora do Risk Engine Python.
6. **IA read-only** (Art. 35) — output estruturado, sem promoção automática.
7. **Carteira Hard = patrimônio** (Art. 23), nunca margem.
8. **Provenance** em todo dado ingerido (fonte, hash, qualidade, ts origem, ts ingestão, custo, ToS).
9. **Audit trail** em todo evento operacional.
10. **Cooldown constitucional** respeitado em qualquer mudança (POV: 3/14 dias; Constituição: 7/30 dias).
11. **Demo/Real segregados** por conta + flag + comando + banner UI + audit log.
12. **TDD First** em toda TASK de CODE.

---

## 4. Regras globais (G-R)

### G-R01 — Integração com MetaTrader (Pilar 3)

G-R01.01 — Toda comunicação CaM ↔ MT5 **DEVE** passar pela bridge ZeroMQ (`cam/features/mt5_integration/bridge.py`). Sem outros canais permitidos.

G-R01.02 — Conta vinculada: **Genial Investimentos** (R-17). Em BL-E (read-write demo), assume-se conta Genial DEMO. Validação prévia: `CORRETORA-EVAL.md §9` registra plano EA e custos vigentes.

G-R01.03 — Toda ordem destinada a MT5 carrega **idempotency key** (UUID v4 da intenção) para impedir duplicação em retries de bridge.

G-R01.04 — EA `.mq5` versionado + hash registrado em `cam_ea_artifacts` (tabela a criar em BL-E). Reload dinâmico **vedado** em BL-E; permitido apenas com allowlist em SPEC futura.

G-R01.05 — Heartbeat fail-closed: ausência > 3s → bridge OFFLINE → Order Gateway bloqueia → alerta Telegram → kill switch sugerido.

### G-R02 — Definição de "Robô" (Q10 + R-19)

G-R02.01 — **Robô = Estratégia + Configuração + Ambiente + Modo de Autonomia**. NÃO é IA.

G-R02.02 — Estratégia é **regra determinística** codada em Python (canonical) — função `evaluate(tick, context) → OrderCandidate | None`.

G-R02.03 — Modos de autonomia (Autonomy Matrix):
| Ambiente | Sinal (avisa) | 1-click (confirma) | Semi-auto | Full-auto |
|---|---|---|---|---|
| Backtest | ✅ | N/A | ✅ | ✅ |
| Paper | ✅ | ✅ | ✅ | ✅ |
| Demo | ✅ | ✅ | ✅ (condicionado) | ✅ (condicionado) |
| Real | ✅ | ✅ (condicionado forte) | ❌ até gate | ❌ até gate |

> "Condicionado forte" = exige cooldown 30 dias + assinatura simbólica Founder + audit log dedicado.

### G-R03 — 7 indicadores fundamentalistas (R-20)

G-R03.01 — Lista canônica de indicadores em BL-F: `DY, P/L, P/VP, ROE, Dívida_Liquida_EBITDA, Payout, ROIC`.

G-R03.02 — `DY` tem **peso forte** na decisão patrimonial (Carlos é dividend-oriented). Outros 6 são contextuais.

G-R03.03 — Schema: `cam_fundamentals_snapshot(ticker, ts_snapshot, source, dy, pl, pvp, roe, div_liq_ebitda, payout, roic, hash)`.

### G-R04 — Multiestrategia exige emenda (R-19 + TD-v0.4-03)

G-R04.01 — ~~BL-H (Robot Orchestrator)~~ **✅ RESOLVIDO** — EMENDA-001 v2 ratificada em 2026-05-27 (Constituição v1.1). BL-H decomposto em BL-H1 (Robot Orchestrator/Art. 11-A) + BL-H2 (Strategy Escalation Engine/Art. 11-B). Ambos desbloqueados.

G-R04.02 — Texto da emenda **DEVE** alterar Art. 11 ou criar Art. 11-A acrescentando: "Múltiplas estratégias podem operar simultaneamente, desde que: (a) soma de contratos respeite os limites do Art. 11 (intocáveis 2 WIN + 2 WDO); (b) risco agregado modelado em `cam/_shared/risk/aggregate.py`; (c) prioridade entre sinais conflitantes definida em POV".

G-R04.03 — Antes da emenda ratificada, registry pode ter N estratégias **registradas**, mas apenas 1 com `is_active=true`.

---

## 5. BL-A — Strategy Lifecycle + Autonomy Matrix + EA Control Plane Base

### 5.1 Regras

**R1.01** — Criar `cam/features/strategies/` com:
- `domain.py`: `Strategy` (abstract), `StrategyMetadata`, `StrategyStatus` (enum: `draft|backtested|walk_forward_ok|paper_ok|demo_ok|real_authorized|retired`).
- `registry.py`: `StrategyRegistry` com `register`, `list`, `get`, `promote(strategy_id, to_status, evidence_pack_id)`.
- `strategies/orb_60m_win.py`: implementação concreta da S1 (R-18 aprovada).

**R1.02** — Toda promoção de status exige `EvidencePack` válido — sem evidência, registry rejeita.

**R1.03** — `EvidencePack` (BL-A): dataclass com `strategy_id, status_target, backtest_runs[], walk_forward_results[], paper_results[], adherence, drawdown, expectancy_net, custom_metrics`.

**R1.04** — Adicionar `cam/_shared/autonomy/matrix.py` com `is_mode_allowed(env, mode, strategy_status) → bool` enforçando G-R02.03.

**R1.05** — EA Control Plane G2 — adicionar à whitelist REQ/REP do `cam_bridge.mq5`:
- `PAUSE_EA` — interrompe `OnTick` (publicação continua via heartbeat).
- `RESUME_EA` — retoma `OnTick`.
- `GET_VERSION` — retorna versão+hash registrado.

**R1.06** — Variável `REAL_TRADING_ALLOWED: bool = False` em `cam/_shared/config/__init__.py`. Allowlist `REAL_TRADING_ACCOUNTS: list[str] = []` (vazio default).

**R1.07** — Order Gateway único: criar `cam/_shared/order_gateway/gateway.py` com função `submit(intent, env, mode) → OrderResult` que **encadeia obrigatoriamente** `validate_intention` → audit → idempotency check → EA dispatch (se demo/real) ou paper dispatch (se paper).

**R1.08** — Lint MQL5 (script `scripts/lint_mql5.sh`) verifica que `OrderSend(`, `OrderClose(`, `PositionOpen(`, `PositionClose(`, `OrderModify(` aparecem **apenas** em `cam_risk_mirror.mq5` (futuro BL-E). Em BL-A, lint falha se aparecerem em `cam_bridge.mq5`.

**R1.09** — Backtest com P&L real por tick scanning: `BacktestSimulator.run()` calcula resultado real seguindo tick a tick até SL ou TP — substitui stub `result_gross=0`.

**R1.10** — `BacktestRun` persistido em `cam_backtest_runs` + `cam_backtest_trades` (tabelas já existem).

### 5.2 Contratos

```python
# strategies/domain.py
class Strategy(Protocol):
    metadata: StrategyMetadata
    def evaluate(self, tick: MarketTick, context: StrategyContext) -> OrderCandidate | None: ...

# order_gateway/gateway.py
async def submit(
    intent: OrderIntent,           # asset, direction, contracts, sl_points
    env: Literal["backtest","paper","demo","real"],
    mode: Literal["signal","one_click","semi","full"],
    strategy_id: str,
    idempotency_key: UUID,
) -> OrderResult:
    """Único caminho de ordem. Bloqueia em violação constitucional."""
```

### 5.3 Critérios de aceite

- **CA-A.1** Strategy Registry persiste S1 ORB no estado `draft`.
- **CA-A.2** Promoção de status sem `EvidencePack` retorna erro `EVIDENCE_REQUIRED`.
- **CA-A.3** Backtest da S1 em tick histórico (BL-B) produz `P&L != 0` e persiste `BacktestRun`.
- **CA-A.4** Autonomy Matrix bloqueia `(env=real, mode=full)` para estratégia `paper_ok`.
- **CA-A.5** `cam_bridge.mq5` responde `PAUSE_EA` → ticks param de chegar; `RESUME_EA` → retomam.
- **CA-A.6** Lint MQL5 falha se `OrderSend(` aparecer em `cam_bridge.mq5`.
- **CA-A.7** Order Gateway é o **único** ponto que invoca `risk_validate`; outras chamadas detectadas por busca textual são reportadas como warning.
- **CA-A.8** `REAL_TRADING_ALLOWED=false` faz Order Gateway retornar `RealTradingDisabled` mesmo se env=real for solicitado.

### 5.4 P/M/G por bloco e marcadores

**P/M/G:** G — múltiplas frentes. **sec=true, qa-sec=true.**

---

## 6. BL-B — Market Data Provenance + Tick Histórico

### 6.1 Regras

**R2.01** — Schema `cam_market_data_provenance(import_id, source, source_url, asset, ts_origin_min, ts_origin_max, ts_ingestion, tick_count, hash, quality_flags, license_terms_ack)`.

**R2.02** — Toda ingestão via `cam/features/market_data/service.py::ingest_ticks(file, source_metadata)` registra provenance antes de gravar ticks.

**R2.03** — Deduplicação por hash de (asset, ts, price, volume).

**R2.04** — Quality flags mínimos: `has_gaps`, `has_zero_volume`, `out_of_hours`.

**R2.05** — `Instrument Catalog`: tabela `cam_instruments` com `(ticker, asset_class, exchange, contract_size, tick_size, point_value, active)`. Pré-popular WIN/WDO/IND/DOL.

**R2.06** — Importador HTML/CSV do MT5 (BL-B reusa importer da SPEC v0.2) com extensão para Genial CSV de extrato (R-17).

### 6.2 Critérios

- **CA-B.1** Import de tick WIN gera `Provenance` + N ticks em `cam_market_ticks` + hash determinístico.
- **CA-B.2** Reimport do mesmo arquivo → 0 duplicados.
- **CA-B.3** Quality flags populados corretamente para arquivo com gaps conhecidos.
- **CA-B.4** `cam_instruments` lista WIN/WDO com `point_value` correto (0.20 / 10.00).

**P/M/G:** M. **sec=false, qa-sec=true** (parsing seguro).

---

## 7. BL-C — Paper Loop Governado + AI Real

### 7.1 Regras

**R3.01** — Wiring: `cam/features/paper_trading/service.py::loop_governed(strategy_id, duration)` lê ticks do `cam_market_ticks` (replay) → estratégia → Order Gateway (env=paper) → `cam_paper_trades`.

**R3.02** — `cam_paper_trades` (migration nova) com `(id, strategy_id, intent_id, asset, direction, contracts, entry_price, exit_price, result_gross, costs, ir_provisioned, result_net, adherence, ts_open, ts_close)`.

**R3.03** — Aderência calculada por trade: `1.0` se Risk Engine aprovou + estratégia respeitou parâmetros; `0.0` se houve violação registrada.

**R3.04** — `AIAnalystDataCollector` deixa de retornar listas vazias — consulta `cam_journal_entries`, `cam_risk_decisions`, `cam_violations` por data.

**R3.05** — Strategy Registry permite **N registradas, 1 ativa** (`is_active=true` único). Promoção a `paper_ok` exige ≥ 100 paper trades + aderência ≥ 95%.

### 7.2 Critérios

- **CA-C.1** Loop paper executa S1 ORB sobre tick histórico WIN e produz ≥ 1 paper trade aprovado pelo Risk Engine.
- **CA-C.2** Kill switch ativado durante loop → loop para em < 1s.
- **CA-C.3** `AIAnalystService.run_daily_analysis()` retorna análise não-vazia consumindo dados reais.
- **CA-C.4** Tentativa de marcar 2 estratégias `is_active=true` é rejeitada por constraint DB.
- **CA-C.5** Promoção a `paper_ok` falha com < 100 trades ou aderência < 95%.

**P/M/G:** G. **sec=true, qa-sec=true.**

---

## 8. BL-D — Carteira Hard Holdings + Importação Genial

### 8.1 Regras

**R4.01** — Schema `cam_carteira_hard_holdings(id, ticker, asset_class, quantity, avg_price, first_acquisition_at, last_acquisition_at, source, hash)`.

**R4.02** — Endpoint `POST /api/v1/carteira-hard/holdings` aceita: `{ticker, quantity, price, acquired_at, source}` — source em `{MANUAL_UI, GENIAL_IMPORT}`.

**R4.03** — Importação Genial: parser dedicado em `cam/features/ledger/genial_importer.py` para extrato Genial (formato CSV — confirmar layout na fase de PLAN).

**R4.04** — Holdings **nunca** entram em cálculo de margem do Risk Engine (assert estrutural: tentativa de `risk.add_open_position()` com asset não-derivativo levanta `InvalidAssetForRisk`).

**R4.05** — UI `/carteira-hard` lista holdings + saldo R$ + total estimado (sem valorização real até BL-F integrar cotação).

### 8.2 Critérios

- **CA-D.1** Adicionar PETR4 100 cotas a R$ 35,00 via UI → holding persistida + `source=MANUAL_UI`.
- **CA-D.2** Importar CSV Genial com 5 ações → 5 holdings com `source=GENIAL_IMPORT`.
- **CA-D.3** Reimportar mesmo CSV → 0 novos (dedupe por hash).
- **CA-D.4** Tentativa de adicionar `PETR4` ao Risk Engine como `OpenPosition` é rejeitada estruturalmente.

**P/M/G:** M.

---

## 9. BL-E — Read-write MT5 DEMO + `cam_risk_mirror.mq5`

### 9.1 Regras

**R5.01** — Adicionar ao `cam_bridge.mq5` o comando `SUBMIT_ORDER` (whitelist), apenas com:
- Verificação `ACCOUNT_TRADE_MODE == ACCOUNT_TRADE_MODE_DEMO` (G-R01.05 estendido)
- Conta na `REAL_TRADING_ACCOUNTS` allowlist **rejeita** este comando (paradoxo intencional — comando demo não opera real)
- Idempotency key validado (não pode repetir)
- `cam_risk_mirror.mq5` valida localmente antes de chamar `OrderSend`

**R5.02** — `cam_risk_mirror.mq5` (novo EA) implementa em MQL5 os 18 validators do Risk Engine Python — **paridade testada**. Suite de testes em `apps/cam-cockpit/backend/tests/test_risk_mirror_parity.py` compara 100+ cenários canônicos.

**R5.03** — Order Gateway submete via REQ/REP `SUBMIT_ORDER` (não PUB/SUB — exige ack). Timeout 2s → falha + log.

**R5.04** — Fill detectado pelo `cam_bridge.mq5` (canal `mt5.fill`) gera `JournalEntry` automaticamente com `source=MT5_BRIDGE`.

**R5.05** — Kill switch global: comando `KILL_SWITCH_ACTIVATE` (novo na whitelist) propagado para EA → EA cancela ordens pendentes + para `OnTick`.

### 9.2 Critérios

- **CA-E.1** S1 ORB rodando em paper há ≥ 30 dias + aderência ≥ 95% → habilitado a entrar em DEMO live.
- **CA-E.2** `SUBMIT_ORDER` em conta REAL é rejeitado pelo EA (verificação interna).
- **CA-E.3** Idempotency key repetida → EA retorna `DUPLICATE_INTENT`.
- **CA-E.4** Paridade Python ↔ MQL5: 100 cenários → mesma decisão (Approved/Rejected + mesmo validator culpado).
- **CA-E.5** Kill switch via cockpit propaga para EA em < 2s; ordens pendentes canceladas.
- **CA-E.6** Fill em DEMO gera `JournalEntry` automaticamente.

**P/M/G:** G. **sec=true CRÍTICO, qa-sec=true CRÍTICO** (1º envio de ordem mesmo em demo).

---

## 10. BL-F — Dividendos + Fundamentalistas + Policy Engine

### 10.1 Regras

**R6.01** — Schema `cam_dividends_calendar(id, ticker, type [DIV|JCP], ex_date, payment_date, amount_per_share, source, hash)`.

**R6.02** — Schema `cam_dividends_received(id, ticker, amount, type, payment_date, holding_id_ref)`.

**R6.03** — `cam_fundamentals_snapshot` conforme G-R03.03 com 7 indicadores R-20.

**R6.04** — `Carteira Hard Policy Engine` (`cam/features/ledger/policy_engine.py`) avalia holding contra critérios:
- `DY < 4%` → alerta nível 1 ("baixo DY para Carteira Hard")
- `P/L > 25` → alerta nível 2 ("valuation alto")
- `Dívida_Liq/EBITDA > 3` → alerta nível 3 ("endividamento alto")
- **Alerta = sugestão.** Nunca bloqueio hard (R-13).

**R6.05** — Multi-Source Collector: arquitetura preparada para múltiplas fontes (StatusInvest, Fundamentus, Dados Mercado). **Fontes específicas e ToS ficam em TD-v0.4-01.** BL-F entrega o esqueleto + 1 fonte placeholder.

### 10.2 Critérios

- **CA-F.1** Calendário de dividendos exibe próximos 12 meses para holdings registradas.
- **CA-F.2** `cam_fundamentals_snapshot` populado para 1 ticker via fonte placeholder.
- **CA-F.3** Policy Engine gera alertas corretos para holdings que violam critérios.
- **CA-F.4** Alerta nunca bloqueia operação — UI exibe banner amarelo com checklist de justificativa.

**P/M/G:** G. **sec=false, qa-sec=true** (scraping seguro — escopo TD-v0.4-01).

---

## 11. BL-G — Cross-Asset Research + Pair Trade + AI Workbench

### 11.1 Regras

**R7.01** — Adicionar canal `mt5.book` ao `cam_bridge.mq5` (level 2 — top 5 bids + top 5 asks). Persistir em `cam_market_book_snapshots` (hypertable já criada).

**R7.02** — `cam/features/research/` (nova feature):
- `pair_trade_backtest.py` — simulador de pair trade (2 instrumentos simultâneos)
- `cross_asset_correlation.py` — correlação rolling entre ativos
- `pattern_lab.py` — busca de padrões (sem ML quant ainda — apenas estatística)

**R7.03** — `AIResearchWorkbench` (`cam/features/ai_analyst/research_workbench.py`) consome `cam_market_ticks`, `cam_market_book_snapshots`, `cam_fundamentals_snapshot`. Gera output estruturado JSON + visualização (Recharts no frontend).

**R7.04** — `RebalanceSuggestionEngine` em `cam/features/ledger/rebalance.py` propõe rebalanceamento baseado em policy + DY targets. **Nunca executa** — apenas sugere via UI + Telegram.

**R7.05** — Remote AI Governance: schema `cam_ai_provider_calls(id, provider, model, prompt_hash, response_hash, anonymized, ts)`. OpenAI fica **desabilitado** (TD-v0.4-02) — apenas Anthropic + Ollama operacionais.

### 11.2 Critérios

- **CA-G.1** EA publica `mt5.book` → cockpit recebe snapshot a cada tick.
- **CA-G.2** Backtest de pair trade WIN×WDO produz métricas (correlação, Sharpe do spread).
- **CA-G.3** AI Workbench retorna JSON estruturado para 1 prompt de análise cross-asset.
- **CA-G.4** Rebalance sugere "vender 50 PETR4, comprar 100 ITUB4" mas **nunca executa**.
- **CA-G.5** Chamadas OpenAI são rejeitadas com `OpenAINotEnabled` enquanto TD-v0.4-02 não for resolvido.

**P/M/G:** G. **sec=false, qa-sec=true.**

---

## 12. BL-H — Robot Orchestrator + Risk Engine Cross-Asset

> **Decomposição pós-EMENDA-001 v2 (recomendação Leo + Marty):** BL-H ficou grande demais — dividido em **BL-H1** (Robot Orchestrator + multiestratégia) e **BL-H2** (Strategy Escalation Engine — Art. 11-B).
>
> Status TD-v0.4-03: **RATIFICADO** em 2026-05-27 (EMENDA-001 v2 → Constituição v1.1). BL-H1 e BL-H2 desbloqueados.

### 12.1 BL-H1 — Robot Orchestrator + Multiestratégia (Art. 11-A)

#### Regras

**R8.01** — `cam/features/robot_orchestrator/` (nova feature):
- `domain.py`: `Robot` (1 robô = N estratégias com prioridade)
- `orchestrator.py`: lê tick → distribui para estratégias ativas → coleta candidatos → resolve conflitos via POV §3.11
- `conflict_resolver.py`: implementa POV §3.11 (Resolução de Conflitos) com regra determinística + property-based testing obrigatório

**R8.02** — `cam/_shared/risk/aggregate.py` (NOVO): validator `aggregate_risk_check(candidates[], context)`:
- Soma de contratos por ativo respeita Art. 11º (default ou escalonado — lê limite vigente, não hardcoded)
- Drawdown agregado projetado se todos candidatos forem aprovados
- Suspende estratégia individual com aderência < 95% (Art. 11-A item 7)
- Mede correlação rolling 30 dias entre estratégias ativas + bloqueia ativação de nova estratégia com correlação > 0,7 (Art. 11-A item 8)

**R8.03** — Flag `MULTI_STRATEGY_ENABLED=false` default. Ativação:
- Exige BL-H1 entregue
- Exige pelo menos 1 estratégia com aderência individual ≥ 95% em 30 pregões
- Registra em FEATURE-FLAGS-LEDGER + audit log

**R8.04** — `max_contracts_check` refatorado: deixa de usar `MAX_WIN_CONTRACTS=2` hardcoded; passa a chamar `get_current_limits()` que lê estado vigente (default 2+2 ou limite escalonado pelo BL-H2). **Lint enforça impossibilidade de auto-edição de limite** (recomendação Leo).

**R8.05** — Gain lock individual por estratégia (POV §3.13): se estratégia individual atingir 5% do capital no dia, é suspensa do orquestrador pelo resto do pregão. Outras estratégias continuam (recomendação Mammon).

**R8.06** — Aderência calculada **por estratégia E em agregado**:
- `Strategy.adherence` individual (média ponderada por trade da estratégia)
- `Orchestrator.aggregate_adherence` (média ponderada pelo número de trades)
- Operador vê as duas em UI Risk Console

#### Critérios

- **CA-H1.1** Robot Orchestrator com 2 estratégias ativas → property-based testing com 10.000+ cenários Hypothesis nunca viola Art. 11º (com limite vigente vigente).
- **CA-H1.2** Conflito mesma direção/mesmo ativo: estratégia com maior expectância 30d vence.
- **CA-H1.3** Conflito direção oposta/mesmo ativo: ambos rejeitados + audit `DIRECTIONAL_CONFLICT`.
- **CA-H1.4** Empate de expectância dentro de 5%: ambos rejeitados + audit `AMBIGUOUS_TIE`.
- **CA-H1.5** Estratégia com aderência < 95% é automaticamente suspensa do orquestrador.
- **CA-H1.6** Correlação > 0,7 entre 2 estratégias ativas dispara alerta + bloqueia ativação de 3ª correlacionada.
- **CA-H1.7** Lint MQL5/Python detecta tentativa de auto-edição de `max_contracts_check` constants e falha CI.
- **CA-H1.8** Gain lock individual ≥ 5% do capital suspende **apenas aquela** estratégia (não bloqueia outras).
- **CA-H1.9** Primeiro deploy operacional com N=2 estratégias (S1 + S2 a definir) — recomendação Marty D1 já endereçada como gate manual.

**P/M/G:** G. **sec=true CRÍTICO, qa-sec=true CRÍTICO.**

### 12.2 BL-H2 — Strategy Escalation Engine (Art. 11-B)

#### Regras

**R8.10** — `cam/_shared/risk/scaling.py` (NOVO, Pure Python, sem auto-execução):
- `compute_scaling_eligibility(strategy_id, journal_repo) -> ScalingEligibility` lê 30 pregões consecutivos + computa as 5 métricas da Art. 11-B (a):
  - Profit Factor ≥ 1,8
  - Win rate ≥ 55%
  - Expectância líquida ≥ 1,5 × custo fixo mensal
  - Drawdown ≤ 10% do Bucket Derivativo
  - Aderência ≥ 95%
- Retorna `ScalingEligibility(eligible: bool, evidence: ScalingEvidence, missing_criteria: list[str])`

**R8.11** — Job APScheduler executa `compute_scaling_eligibility` **pós-fechamento de cada pregão**. Se elegível, publica evento `ScalingEligibilityReady` no EventBus + envia Telegram (recomendação Marty 2).

**R8.12** — Aplicação de escalonamento (Art. 11-B item c):
- Operador cria arquivo `/project/cam-constitution/escalonamentos/ESC-NNN-YYYY-MM-DD.md`
- Schema do arquivo: ref ao `ScalingEvidence` + novo limite (**incremento estrito +1**) + motivação + assinatura
- Sistema valida incremento +1 (recusa salto 2→4)

**R8.13** — Cooldown reverso (Art. 11-B item d):
- 7 dias padrão
- **21 dias** se `detect_win_streak(strategy_id) == true` no momento da elegibilidade (recomendação Voltaire 1)
- Durante cooldown, operador pode revogar sem ônus (endpoint `POST /api/v1/scaling/revoke/{esc_id}`)

**R8.14** — Reversão automática (Art. 11-B item e):
- Job rolling-30-pregões avalia continuidade dos 5 critérios
- Falha → reversão automática + audit + Telegram + kill switch soft (1 pregão bloqueado)
- **Drawdown ocorrido durante período escalonado conta em dobro** para próxima janela de elegibilidade (recomendação Voltaire 2)

**R8.15** — Tetos absolutos (Art. 11-B item f) hardcoded em `scaling.py`:
- `MAX_SCALED_WIN = 5`, `MAX_SCALED_WDO = 5`
- `MAX_DAILY_DRAWDOWN_PCT = 0.03` (Art. 16º — intocável)
- **Cláusula de blindagem:** emendas que mexam nesses tetos exigem **revisão integral** (não protocolo simplificado v2.0) — comentário hardcoded no código + nota em `PROTOCOLO-EMENDA-CONSTITUCIONAL.md` (recomendação Voltaire 3)

**R8.16** — Schema `cam_constitutional_scaling_events`:
```sql
CREATE TABLE cam_constitutional_scaling_events (
    id UUID PRIMARY KEY,
    ts TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type TEXT NOT NULL,
    -- ELIGIBILITY_COMPUTED | ELIGIBILITY_READY | PROPOSED | APPROVED | REVOKED |
    -- IN_FORCE | AUTO_REVERTED | SOFT_KILL_SWITCH | BLOCKED_ATTEMPT
    strategy_id UUID,
    proposed_limit_win INT,
    proposed_limit_wdo INT,
    evidence_json JSONB,
    cooldown_days INT,
    cooldown_ends_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);
```

**R8.17** — Flag `SCALING_ENABLED=false` default. Ativação exige BL-H2 entregue + 1ª aprovação em `escalonamentos/`. Registra em FEATURE-FLAGS-LEDGER.

**R8.18** — UI Risk Console: histograma de "tentativas-bloqueadas" mostra quais critérios faltaram (Marty 3).

#### Critérios

- **CA-H2.1** `compute_scaling_eligibility` com dataset sintético atingindo TODOS os 5 critérios → `eligible=True`.
- **CA-H2.2** Mesmo dataset com 1 critério faltando → `eligible=False` + `missing_criteria=[critério]`.
- **CA-H2.3** Tentativa de salto incremental 2→4 → rejeitado com `INCREMENTAL_VIOLATION`.
- **CA-H2.4** Detecção de win streak → cooldown = 21 dias (não 7).
- **CA-H2.5** Reversão automática registra evento + Telegram + bloqueia próximo pregão.
- **CA-H2.6** Drawdown durante escalonado dobra na próxima janela (testado com dataset sintético).
- **CA-H2.7** Tentativa de exceder MAX_SCALED_WIN=5 → `BLOCKED_BY_CEILING`.
- **CA-H2.8** `max_contracts_check` consome limite vigente (`get_current_limits()`) e não constants hardcoded.
- **CA-H2.9** UI Risk Console mostra histograma de tentativas-bloqueadas por critério.

**P/M/G:** G. **sec=true CRÍTICO, qa-sec=true CRÍTICO.**

---

## 13. BL-I — Multi-EA + DSL Strategy Layer

### 13.1 Regras

**R9.01** — `cam_bridge.mq5` v2.0 — suporte a múltiplas instâncias (uma por gráfico/ativo). Cada instância tem `EA_ID` único + porta REQ/REP única (5557 + offset).

**R9.02** — `cam/features/mt5_integration/multi_ea_manager.py` orquestra múltiplas conexões ZeroMQ.

**R9.03** — `cam/features/strategies/dsl/` — parser de DSL declarativa (JSON/YAML):
```yaml
strategy: my_orb
asset: WIN
indicators:
  - type: opening_range
    minutes: 60
entry:
  long: "price > opening_range.high AND volume > avg(volume, 20)"
exit:
  stop_loss: 150
  take_profit: "trailing 50% retracement"
```

**R9.04** — DSL **compila para Python canonical** — gera classe `Strategy` válida em runtime + persiste como `strategy.compiled_from_dsl=true` no registry.

**R9.05** — Instrument Catalog estendido (≥ 200 ativos) — universo amplo declarado, ativado por demanda.

### 13.2 Critérios

- **CA-I.1** 2 EAs simultâneos (WIN + WDO) com IDs distintos + portas separadas.
- **CA-I.2** Mutex de execução: ambos podem publicar tick, mas Order Gateway processa em série.
- **CA-I.3** DSL YAML compila para Python e estratégia gerada passa nos mesmos testes que estratégias Python nativas.
- **CA-I.4** `cam_instruments` carrega ≥ 200 ativos (lista via importação CSV).

**P/M/G:** G. **sec=true.**

---

## 14. Tech debts pré-listados

> Estes 3 TDs **bloqueiam** blocos específicos. Cada um vira SPEC própria ou processo formal.

| ID | TD | Bloqueia | Resolução |
|---|---|---|---|
| **TD-v0.4-01** | Scraping multi-fonte — fontes específicas (StatusInvest? Fundamentus?), ToS, schema canônico, rate limit, cache | BL-F (F-26) | SPEC própria antes de entregar coleta real |
| **TD-v0.4-02** | OpenAI provider — ADR aceitando + análise custo/anonimização + governança | BL-G (F-30 OpenAI) | ADR + extensão de SPEC v0.4 |
| ~~TD-v0.4-03~~ | ~~Emenda constitucional multiestratégia~~ | ~~BL-H~~ | **✅ RESOLVIDO 2026-05-27 — EMENDA-001 v2 ratificada, Constituição v1.1 vigente. BL-H decomposto em BL-H1 + BL-H2 (ambos desbloqueados)** |

---

## 15. Classificação P/M/G global

| Campo | Valor |
|---|---|
| **Classe global** | **G (Grande)** |
| **Rationale** | 9 blocos · 30+ features · 7 das 9 trilhas com `sec=true` ou `qa-sec=true` · 3 tech debts bloqueantes · exige emenda constitucional · cobre 6 trilhas paralelas. SPEC G obrigatória — decomposição em blocos é parte da governança. |
| **Albert** | G confirmada |
| **Nico (PLAN futuro)** | Loop com Albert ok — proporcional a 5 janelas de execução |

---

## 16. Marcadores SEC / QA-SEC

| Marcador | Valor | Justificativa |
|---|---|---|
| `sec` | **true** | BL-A, BL-C, BL-E, BL-H1, BL-H2, BL-I tocam Risk Engine / Order Gateway / EA bridge |
| `qa-sec` | **true** | BL-B, BL-E, BL-F, BL-G têm parsing externo / scraping / paridade Python↔MQL5 / providers remotos |

**Por bloco:**

| Bloco | sec | qa-sec | Crítico |
|---|---|---|---|
| BL-A | ✅ | ✅ | — |
| BL-B | — | ✅ | — |
| BL-C | ✅ | ✅ | — |
| BL-D | — | — | — |
| **BL-E** | ✅ | ✅ | **CRÍTICO** (1º envio ordem mesmo demo) |
| BL-F | — | ✅ | — |
| BL-G | — | ✅ | — |
| **BL-H1** | ✅ | ✅ | **CRÍTICO** (multiestratégia — Art. 11-A) |
| **BL-H2** | ✅ | ✅ | **CRÍTICO** (escalonamento de limite — Art. 11-B) |
| BL-I | ✅ | — | — |

---

## 17. Riscos identificados

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Genial não permitir EA em MT5 para PF sem plano específico | Média | Alto | Validar antes de BL-E (TODO-OPERACIONAL OP-001) |
| Paridade Python ↔ MQL5 do `cam_risk_mirror.mq5` divergir em edge cases | Média | Alto | 100+ cenários canônicos + revisão Kevin |
| Emenda constitucional levar mais que 30 dias | Baixa | Médio | Processo bem documentado em PROTOCOLO-EMENDA |
| Scraping multi-fonte (TD-v0.4-01) ficar parado bloqueando BL-F | Média | Baixo | BL-F entrega esqueleto com fonte placeholder; coleta real só após TD |
| OpenAI ADR (TD-v0.4-02) bloquear BL-G | Baixa | Baixo | Anthropic + Ollama cobrem 90% dos casos de BL-G |
| Importação Genial CSV ter formato proprietário não documentado | Média | Médio | Discovery na fase de PLAN; fallback para input manual |
| Risk Engine cross-asset performar mal com many strategies | Baixa | Médio | Property-based testing antes de release |

---

## 18. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior aprova a SPEC v0.4-VISION-EVOLUTION
    como especificação consolidada da evolução do CaM em 9 blocos,
    cobrindo as decisões R-01..R-22.

    Reconhece que:

    a) Esta é UMA SPEC, não 9 versões separadas. Numeração v0.4 a v0.9
       proposta anteriormente fica REVOGADA.

    b) v1.0 do CaM permanece como declaração futura exclusiva do Founder
       — esta SPEC não infere v1.0.

    c) Operação real continua TRAVADA POR DESIGN
       (REAL_TRADING_ALLOWED=false) em toda entrega desta SPEC.

    d) BL-H (Robot Orchestrator) só pode entregar APÓS emenda constitucional
       multiestratégia (TD-v0.4-03) ratificada com cooldown 30 dias.

    e) Liberação para PLAN exige aprovação separada (letscode).
```

---

## 19. Referências cruzadas

- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — Arts. 11, 12, 15, 18, 23, 25, 28, 29, 31, 35, 36 + Anexos
- [`CAM-VISION-FINAL.MD`](./CAM-VISION-FINAL.MD) (v1.1) — visão consolidada que originou esta SPEC
- [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md) (v1.1) — backlog estruturado com 30 features
- [`SPEC-v0.3-TECH-DEBT-REVIEW.md`](./SPEC-v0.3-TECH-DEBT-REVIEW.md) — SPEC anterior (saneamento)
- [`SPEC-v0.2-MT5-ENQUADRAMENTO.md`](./SPEC-v0.2-MT5-ENQUADRAMENTO.md) — bridge MT5 read-only base
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — POV vigente
- [`/project/strategies/EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) — S1 ORB (aprovada R-18)
- [`/project/CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) — Genial em §9 (a confirmar layout extrato)
- [`/project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../PROTOCOLO-EMENDA-CONSTITUCIONAL.md) — processo para TD-v0.4-03
- [`/apps/cam-cockpit/TECH-DEBT.md`](../../apps/cam-cockpit/TECH-DEBT.md) — onde TD-v0.4-01..03 entram após PLAN aprovado

---

> **Princípio operacional desta SPEC:**
>
> 1 SPEC. 9 blocos. 5 janelas. Cadência alta via paralelismo de trilhas. Gates intactos. Constituição vence.
>
> Construir amplo. Liberar estreito. v1.0 fica para o Founder declarar quando quiser.

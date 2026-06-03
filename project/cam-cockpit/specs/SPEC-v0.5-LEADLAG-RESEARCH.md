---
template: SPEC
phase: SPEC
status: Draft v0.5 — pendente gate do Founder
produto: CaM
codinome: research-cubo-leadlag · fatia v0.5
versao: v0.5
vive_em: project/cam-cockpit/specs/SPEC-v0.5-LEADLAG-RESEARCH.md
data: 2026-06-03
lead: Albert
co_lead_sec: Kevin (SEC-GOV)
aprovador: Founder
gate: Founder pendente
---

# SPEC v0.5 — Lead-Lag Research Lane (R0 Dados + 1ª Análise Bar-Time)

> **Data:** 2026-06-03
> **Status:** Draft v0.5 (pendente Founder)
> **Produto:** CaM — research lane
> **Lead:** Albert · **SEC-GOV:** Kevin · **Aprovador:** Founder

---

## 1. Resumo

Especifica o **loop research-only** do Cubo de Lead-Lag na fatia v0.5: **obter OHLCV do
MetaTrader 5 (bridge existente) → persistir como barras canônicas determinísticas em
schema `research_*` → computar a 1ª análise de lead-lag bar-time `C_{S→D}(δ)` com trial
accounting honesto → retornar via REST read-only para um Quant Lab mínimo** — com
isolamento técnico research↔live. **Sem execução, sem ordem, sem paper/live, sem toque
no Risk Engine.**

## 2. Referências de entrada

- **SCOPE:** [`SCOPE-v0.5-LEADLAG-RESEARCH.md`](../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md) — pendente Founder
- **Teses:** `research/leadlag/EDGE-THESIS-LEADLAG-CUBE.md`, `CaM-RESEARCH-CUBO-LEADLAG.md`,
  `CaM-SCOPE-FRONTEND-CUBO.md`, `THESIS-ANALYSIS-01.MD`, `THESIS-LEADLAG-PROPOSAL.MD`
- **Estado real (vence intenção, NCC-1701 §2 regra 7):**
  - Bridge MT5 + `GET_CANDLES` — `apps/cam-cockpit/backend/cam/features/mt5_integration/` (`service.py::get_candles`, `market_routes.py`)
  - Schema TimescaleDB — `alembic/versions/20260524_0003_*_bloco_a_timescaledb.py` (`cam_market_ticks`, `cam_candles_*`), `20260601_0011_*_inspector_candles.py` (`cam_inspector_candles`)
  - Precedente analítico read-only — `cam/features/regime/`
  - Feature `research` existente (bloqueada em `TD-v0.5-PRICESERIES`) — `cam/features/research/routes.py`
- **Constituição:** Arts. 6º, 15º, 18º, 31º, 34º–36º (IA não executora). Modo Dev Fase 0:
  `project/cam-cockpit/DECISAO-FOUNDER-FASE0-DEV-MODE.md`.
- **ADRs aplicáveis:** ADR-013 (acoplamento só via tabela de banco), ADR-014 (Inspetor/candles).
  Novos ADRs leves esperados no PLAN/ARCH: schema `research_*`, lib de heatmap.

## 3. Regras de negócio

### Ingestão MT5 → DB
- **R-01.** A ingestão obtém OHLCV exclusivamente pelo **bridge MT5 existente**
  (`GET_CANDLES`), para `(símbolo, timeframe, janela)` **pré-registrados**. Nenhuma outra
  fonte entra em v0.5.
- **R-02.** O adaptador de ingestão **não importa** Order Gateway, bridge de execução,
  `send_order`, `OrderSend` nem qualquer serviço operacional (barreira técnica, Kevin).
- **R-03.** Cada lote ingerido grava **provenance completa** em `research_data_sources`:
  `bar_origin=broker_ohlcv`, `ts_source`, símbolo, timeframe de origem, janela, `ingested_at`,
  `raw_batch_hash`. Lote sem provenance **não entra** (gate de dados).
- **R-04.** Bridge offline → ingestão falha de forma segura (sem dado parcial silencioso);
  o estado é reportado, nunca inventado (coerência com `market_routes` `_offline()`).

### Barras canônicas determinísticas
- **R-05.** A **barra canônica de bar-time é M1** (`m1_is_primary`, Cenário B Ada,
  PROPOSAL §6.1), persistida em `research_bars`. v0.5 **não** depende de tick com agressor.
- **R-06.** **M5, M15, M30, H1** são **derivadas** por agregação **determinística** de M1
  (`derive(M1, rule, TF)`, função pura): open=primeiro open, high=max, low=min, close=último
  close, volume=soma; bucket **ancorado no início da sessão B3**; último bucket do dia pode
  ser `is_partial`. **M5…H1 nunca são ingeridos direto** do broker.
- **R-07.** **H1 é computado uma única vez** a partir de M1 e referenciado por ambos os modos
  (fronteira INTRADAY↔SWING, PROPOSAL §3.5). Não existe "H1 intraday" e "H1 swing"; `mode` é view.
- **R-08.** A função de derivação é **pura e reprodutível**: rodar duas vezes produz barras
  byte-idênticas. Mudar a regra de agregação **muda o hash → nova run vinculada**, nunca edita
  a anterior (run imutável, Ada).

### Persistência research_*
- **R-09.** Todo o estado de research vive em schema/namespace **`research_*`**, **separado**
  das tabelas live. v0.5 **não reusa** os continuous aggregates `cam_candles_*` como storage
  canônico (faltam provenance/calendário/snapshot/hash e fere isolamento).
- **R-10.** Cada análise referencia um **snapshot imutável** (`research_dataset_snapshots`)
  com **hash composto** (`raw_canonical_hash ⊕ Σ_TF(rule ⊕ bar_def)`); rerun cria nova run.
- **R-11.** **Quality checks mínimos** gravados em `research_data_quality_checks`:
  `missing_bars`, `bucket_misalignment`, `partial_bar`, `m1_is_primary`, `stale_bar`.
- **R-12.** `DELETE` no namespace `/research` é **cancel/archive/soft-delete** — nunca apaga
  evidência (incluindo kill log). Resultado de run é **imutável** (sem edição manual).

### 1ª análise de lead-lag bar-time
- **R-13.** A análise computa a **correlação defasada bar-time**
  `C_{S→D}(δ) = Corr( wᵀ·r_S(t−δ), r_D(t) )`, com `r(t)=ln m(t)−ln m(t−1)`, para δ na grade
  pré-registrada, **δ ≥ 1** (PROPOSAL §3.1, `CaM-RESEARCH §4.2`).
- **R-14.** **Anti-look-ahead (inegociável):** o sinal usa informação **até e inclusive** o
  fechamento da barra t; o label é medido **estritamente depois**, a partir do **preço
  executável pós-barra** (abertura da barra seguinte). **Proibido** reaproveitar o mesmo close
  como feature e como entrada.
- **R-15.** **Trial accounting honesto:** cada run grava `N_t = |fontes| × |alvos| × |grade δ|
  × reruns` em `research_runs`; o contador é **exposto** ao consumidor. v0.5 **não** promete
  DSR/FDR/SPA completos — apenas o **contador** e o **n amostral**; a deflação estatística plena
  é declarada **LATER** (não fingida).
- **R-16.** **"Dado insuficiente" é veredito de primeira classe** (Art. 30 — confiança subjetiva
  não é evidência): abaixo do piso amostral por (par, δ), o resultado é `INSUFFICIENT_DATA`,
  distinto de "sem edge" e de "edge".
- **R-17.** A análise **não emite sinal, recomendação, candidato operacional, sizing nem
  direção de trade**. Produz **evidência descritiva** (correlação, n, δ), nada mais (Arts. 34º–36º).
- **R-18.** **Gap overnight é feature, não erro:** `close[d]→open[d+1]` preservado; forward-fill
  de preço overnight **proibido** (PROPOSAL §6.3).

### Isolamento research↔live (barreira técnica)
- **R-19.** O serviço de research **não escreve** em `cam_orders`, `cam_positions`,
  `cam_journal_entries` nem equivalentes operacionais. Permissão de escrita restrita a `research_*`.
- **R-20.** Módulos de research **não importam** execução (R-02). Verificável estaticamente
  (ex.: regra de import-linter / grep de CI) — a barreira é **código**, não comentário.
- **R-21.** Secrets de broker **nunca** em metadata de run, logs, payloads ou commit.

## 4. Contratos

### 4.1 Rotas REST (namespace `/api/v1/research`, read-only sobre o live)

| Método | Endpoint | Uso |
|---|---|---|
| POST | `/api/v1/research/leadlag/ingest` | dispara ingestão MT5→`research_bars` (corpo: símbolos[], timeframes[], janela). Retorna `snapshot_id` |
| GET | `/api/v1/research/leadlag/data-health` | cobertura por símbolo/TF, quality flags, status de ingestão |
| POST | `/api/v1/research/leadlag/runs` | lança análise sobre um `snapshot_id` (corpo: fontes[], alvo, grade δ). Retorna `run_id` + `N_t` |
| GET | `/api/v1/research/leadlag/runs` | lista runs + status + contador de tentativas |
| GET | `/api/v1/research/leadlag/runs/{run_id}` | resultado da análise: matriz `C_{S→D}(δ)`, n por célula, veredito (`OK`/`INSUFFICIENT_DATA`) |
| GET | `/api/v1/research/leadlag/stats/trials` | contador global de tentativas |

> `POST /runs` cria **job de pesquisa** — **não** ordem, **não** candidato operacional (Kevin).
> `DELETE` (se houver) = cancel/archive/soft-delete (R-12). Payloads = escalares leves
> (matriz de correlação + n), **nunca** tick cru.

### 4.2 Schema de dados (`research_*` — migração nova)

- **`research_bars`** (canônico de barras): `symbol, timeframe, ts_open, ts_close, session_date,
  open, high, low, close, volume, is_partial, provenance_id, aggregation_rule_id`.
  **`timeframe` é coluna + dimensão de partição/índice**, não tabela por TF. Índice
  `(symbol, timeframe, session_date)`.
- **`research_data_sources`** — `id, bar_origin, ts_source, symbol, source_timeframe, window_start,
  window_end, ingested_at, raw_batch_hash`.
- **`research_dataset_snapshots`** — `id, symbols[], timeframes_included[], window, composite_hash,
  calendar_version, created_at`. Imutável.
- **`research_runs`** — `id, snapshot_id, sources[], target, delta_grid[], n_trials, status, created_at`.
  `status ∈ {queued, running, done, failed, insufficient_data}`.
- **`research_run_results`** — `run_id, source, target, delta, correlation, n_samples, verdict`.
- **`research_data_quality_checks`** — `snapshot_id, symbol, timeframe, check_name, value, ts`.

### 4.3 Eventos
- v0.5 é síncrono/sob demanda no mínimo viável. Progresso de run **pode** reusar o WS existente
  do FastAPI **se** o PLAN julgar proporcional — caso contrário, polling de `GET /runs/{id}`.
  **Sem** dependência nova de fila de mensagem nesta versão.

## 5. Casos de uso / cenários

| # | Caso | Esperado |
|---|---|---|
| 1 | Founder ingere `[WIN, WDO]` M1, janela N dias | `research_bars` populado (M1 + M5/M15/M30/H1 derivados), `snapshot_id` + provenance + hash |
| 2 | Rodar análise `WIN→WDO` grade δ={1,2,3,5} sobre snapshot | `run_id`, `N_t` registrado, matriz `C(δ)` com n por célula |
| 3 | Abrir Quant Lab → Data Health | cobertura por símbolo/TF + quality flags antes de qualquer heatmap |
| 4 | Ler resultado de run | matriz `C_{S→D}(δ)` + n + veredito; manchete com n, badge RESEARCH |
| 5 | Rerun da mesma análise | nova run vinculada; barras byte-idênticas (R-08); nada editado |
| 6 | Par com poucas barras | célula marcada `INSUFFICIENT_DATA`, não "sem edge" |

## 6. Casos limite / exceções

- **Bridge MT5 offline** → ingestão falha segura (R-04); Data Health mostra estado, não inventa.
- **Sem agressor** (esperado) → v0.5 é bar-time; OFI/Granger/HY/Transfer-Entropy ficam LATER (SCOPE §4).
- **Gap overnight** → preservado como feature (R-18); proibido forward-fill.
- **Bucket parcial no fim do pregão** → `is_partial=true` (R-06), não descartado silenciosamente.
- **Amostra abaixo do piso** → `INSUFFICIENT_DATA` (R-16).
- **MT5 não entrega M1 suficiente** na janela → reportado em Data Health; decisão do Founder
  (decisão aberta SCOPE §8.2).
- **Tentativa de escrita em tabela live** → bloqueada por permissão (R-19) — falha, não degrada.

## 7. Classificação P/M/G

| Campo | Valor |
|---|---|
| Classe | **G** (decomposta) |
| Rationale | Entrega N funcionalidades coordenadas em três ambientes (schema `research_*` novo, ingestão MT5→DB, análise lead-lag bar-time pura, rotas REST, Quant Lab mínimo) sob gatilho SEC-GOV. É G por **número de funcionalidades e superfícies**, não por modificador de risco/segurança/arquitetura (proibido — Q8 Founder). Decompõe-se nos blocos BL-DB-0, BL-BE-1..4, BL-FE-1..2, BL-SEC-0 (SCOPE §6) — TASKs no PLAN (Nico). Nico mantém direito formal de contestar esta classe (loop ilimitado com Albert; Founder decide). |

(Lembrete: P = subitem de funcionalidade existente · M = melhoria/nova funcionalidade · G = N
funcionalidades / decomposição. **Sem modificadores de risco** — Q8 Founder.)

## 8. Marcadores de segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (check intrabloco no CODE) | **sim** | Isolamento research↔live é código (R-02, R-19, R-20); dados de broker (R-21); nova superfície REST. Kevin entra intrabloco no CODE dos blocos BE. |
| `qa-sec` (QA-SEC no QA) | **sim** | QA valida a barreira técnica: ausência de escrita live, ausência de import de execução, namespace `/research`, sem secrets. |

> **Gatilho SEC-GOV ATIVO** (Kevin): dados sensíveis + integração externa (MT5) + nova
> superfície + fronteira com tabelas operacionais. Conditional Go condicionado à **prova de
> isolamento técnico**. Ver [`../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md).
> Kevin recomenda, Founder decide.

## 9. Saídas esperadas

- Migração `research_*` aplicada (schema isolado do live).
- Feature backend `research/leadlag` (domain puro + repository + routes) — desbloqueia
  `TD-v0.5-PRICESERIES` da feature `research` existente.
- Rotas `/api/v1/research/leadlag/*` funcionais e read-only.
- Barras canônicas M1 + derivadas determinísticas persistidas com provenance e hash.
- 1ª análise `C_{S→D}(δ)` retornável com contador de tentativas e n amostral.
- Quant Lab mínimo: Data Health + leitura da análise + badge RESEARCH.
- Prova de isolamento research↔live (artefato SEC-GOV de Kevin).

## 10. Critérios de aceite

1. Ingestão `[WIN, WDO]` M1 popula `research_bars` com M5/M15/M30/H1 **derivados
   deterministicamente** de M1 (rerun → barras byte-idênticas, R-08).
2. Toda barra/lote tem **provenance** (R-03) e referencia **snapshot com hash composto** (R-10).
3. Análise `C_{S→D}(δ)` respeita **anti-look-ahead** (R-14) — verificável por teste com fixture
   que falharia se o close fosse reusado como entrada.
4. **Contador de tentativas** `N_t` presente em toda run (R-15); par com amostra abaixo do piso
   retorna `INSUFFICIENT_DATA` (R-16).
5. **Nenhuma** rota/serviço de research escreve em `cam_orders`/`cam_positions`/`cam_journal_entries`;
   **nenhum** módulo de research importa execução (R-19, R-20) — verificável estaticamente.
6. Quant Lab exibe **Data Health antes** de leitura de resultado; **badge RESEARCH** permanente;
   vocabulário de pesquisa; **zero** affordance de ordem/Risk Engine.
7. Build/checks/testes verdes; Kevin (QA-SEC) valida a barreira técnica.

## 11. Delta no DVP (se aplicável)

Sem alteração de direção estratégica do CaM. Materializa a research lane já prevista nas teses,
ancorada no estado real do MT5. Não promove estratégia nem altera a fase do CaM (Fase 0).

## 12. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| v0.5 | 2026-06-03 | Draft inicial — R0 dados (MT5→`research_bars` canônico) + 1ª análise lead-lag bar-time `C_{S→D}(δ)`, research-only, isolamento técnico | (pendente Founder) |

---

### Quando NÃO usar este SPEC
- OFI/tick titular, DSR de duas camadas, walk-forward/purged CV, modo SWING completo,
  Fibonacci, síntese R4 e Quant Lab completo são **LATER** (SCOPE §4) — exigem SPEC própria.
- S1 (ORB 60m WIN) é trilha separada — **OUT**.
- Nenhuma estimativa em horas/dias/semanas. Sem auto-approval. Founder aprova SCOPE e SPEC.

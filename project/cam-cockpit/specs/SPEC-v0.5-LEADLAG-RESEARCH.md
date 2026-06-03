---
template: SPEC
phase: SPEC
status: APROVADO v0.5 (rev. 2) — Founder ratificou 2026-06-03
produto: CaM
codinome: research-cubo-leadlag · tese completa v0.5
versao: v0.5
vive_em: project/cam-cockpit/specs/SPEC-v0.5-LEADLAG-RESEARCH.md
data: 2026-06-03
lead: Albert
co_lead_sec: Kevin (SEC-GOV)
co_participacao: Ada (dados), Jim (quant), Nassim (risco), Don (UX), Voltaire (challenger)
aprovador: Founder
gate: APROVADO — Founder 2026-06-03
---

# SPEC v0.5 — Cubo de Lead-Lag Cross-Asset (TESE COMPLETA, faseada)

> **Status:** Draft v0.5 rev. 2 (pendente Founder)
> **Produto:** CaM — Research Lane
> **Lead:** Albert · **SEC-GOV:** Kevin · **Aprovador:** Founder

---

## 1. Resumo

Especifica o **loop research-only parametrizável** do Cubo de Lead-Lag, cobrindo a
**tese completa** (R0 dados → R1 features → R2 cubo rápido/OFI → R3 cubo lento/
estrutura + fib → R4 síntese → Quant Lab):

> **operador seleciona a tese/universo → o sistema extrai do MetaTrader 5
> (OHLCV via `GET_CANDLES` + ticks com agressor/`flags`) → persiste em schema
> `research_*` isolado → processa (barras canônicas determinísticas, OFI assinado,
> correlação defasada bar-time e event-time, Hayashi-Yoshida, lead-lag HRY, Granger,
> estrutura + fib, síntese) com trial accounting honesto → retorna via REST
> read-only para o Quant Lab.**

**Sem execução, sem ordem, sem paper/live, sem toque no Risk Engine** (Arts. 34º–36º).
A subdivisão em sub-versões (0.5.1…0.5.7) é responsabilidade do **PLAN (Nico)** — esta
SPEC descreve o **todo**.

## 2. Referências de entrada

- **SCOPE:** [`SCOPE-v0.5-LEADLAG-RESEARCH.md`](../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md) (rev. 2) — pendente Founder.
- **Research (matemática + contrato + parecer):** `research/leadlag/CaM-RESEARCH-CUBO-LEADLAG.md`,
  `THESIS-LEADLAG-PROPOSAL.md`, `THESIS-ANALYSIS-01.md`, `CaM-SCOPE-FRONTEND-CUBO.md`.
- **Evidência do agressor (gate R0 resolvido):** `research/leadlag/PROBE-AGGRESSOR-RESULT.md`.
- **Arquitetura (já feita — referenciar, não recriar):**
  - **ADR-015** (`adrs/ADR-015-research-lane-isolada.md`) — schema `research_*` próprio,
    MT5 como fonte, isolamento técnico, research é vertical slice. **Accepted.**
  - **DAS** (`DAS.md`) — camada Research Lane + schema `research_*` + ADR-015.
  - **import-linter** (`pyproject.toml`) — contrato "Research Lane nao importa execucao
    nem broker (ADR-015)" **ATIVO** (`source_modules = ["cam.features.research"]`).
- **Estado real (vence intenção, NCC-1701 §2 regra 7):**
  - Bridge MT5 + `GET_CANDLES` + `PROBE_TICKS` — `cam/features/mt5_integration/`
    (`service.py`, `market_routes.py`, `routes.py` `/api/v1/mt5/probe-ticks`).
  - `TickPersister` (`tick_persister.py`) grava `cam_market_ticks(asset, price, volume,
    timestamp, source)` — **NÃO persiste `flags`** (agressor) hoje.
  - Continuous aggregates `cam_candles_*` (live); precedente read-only `cam/features/regime/`.
  - Feature `research` (`cross_asset_correlation.py` — Pearson defasado puro).
- **Constituição:** Arts. 6º, 15º, 18º, 30º (confiança ≠ evidência), 31º, 34º–36º.
  Modo Dev Fase 0: `DECISAO-FOUNDER-FASE0-DEV-MODE.md` (isolamento permanece).

## 3. Regras de negócio

### 3.1 Ingestão parametrizável MT5 → DB
- **R-01.** A ingestão obtém dado **exclusivamente** pelo **bridge MT5 existente**:
  OHLCV via `GET_CANDLES` **e** ticks via o caminho `CopyTicks/COPY_TICKS_ALL`
  (`PROBE_TICKS` provou a viabilidade). Nenhuma outra fonte entra em v0.5.
- **R-02.** **Universo parametrizável (1ª classe):** a run carrega `sources[]`,
  `target(s)`, `delta_grid[]`, `timeframes[]`, `mode`, `thresholds` como
  **configuração**. **Nada de universo hardcoded.** O operador seleciona a tese; o
  sistema extrai exatamente o que a run declara.
- **R-03.** O adaptador de ingestão roda **na borda** e **não importa** Order Gateway,
  `mt5_integration` de execução, bridge de execução, `send_order`, `OrderSend`, paper
  trading nem robot orchestrator (barreira técnica — import-linter ativo, ADR-015).
- **R-04.** Cada lote grava **provenance completa** em `research_data_sources`:
  `bar_origin ∈ {broker_ohlcv, broker_m1, tick}`, `ts_source ∈ {exchange, broker_recv,
  local_ingest}`, símbolo, timeframe de origem, janela, `ingested_at`, `raw_batch_hash`,
  `aggressor_source ∈ {exchange, broker, lee_ready, unknown}`. Lote sem provenance **não
  entra** (gate de dados). `ts_source=local_ingest` é marcado **No-Go** para lead-lag
  (latência de rede vira "sinal" — Ada §6.4).
- **R-05.** **Janela histórica M1:** a ingestão pede "o máximo que o MT5 entregar" via
  `GET_CANDLES`; a cobertura **real** obtida é reportada em Data Health (R-31), nunca
  assumida. Bridge offline → ingestão **falha de forma segura** (sem dado parcial
  silencioso); o estado é reportado, nunca inventado (coerência com `market_routes`).

### 3.2 Tick com agressor (`flags`)
- **R-06.** A v0.5 **persiste o lado agressor** do tick: `aggressor ∈ {+1, −1, 0}`
  derivado de `MqlTick.flags` (`TICK_FLAG_BUY=32 → +1`, `TICK_FLAG_SELL=64 → −1`,
  trade sem lado → `0`), com `t_msc` (timestamp ms) e `volume`. A `TickPersister`
  atual **não** grava `flags` — esta é mudança de escopo.
- **R-07.** **Decisão de dados (Ada — resolver no início do CODE):** o tick com
  agressor vive em **`research_ticks` próprio** (recomendado — coerente com ADR-015 e
  isolamento; `cam_market_ticks` é storage **live**) **ou** estende `cam_market_ticks`
  com `flags`/`aggressor`. **Recomendação:** `research_ticks` em schema `research_*`,
  para não acoplar research ao ciclo de vida do live (retenção/compressão).
- **R-08.** **Liquidez de tick é não-uniforme e registrada, não escondida** (Nassim/
  Voltaire — `PROBE-AGGRESSOR-RESULT.md`): WIN faz ~500 ticks em ~5s; PETR4 em ~255s. O
  event study (R-22) **condiciona por liquidez do alvo**; a capacidade é medida como
  liquidez **no instante do evento**, não volume diário.

### 3.3 Barras canônicas determinísticas
- **R-09.** A **barra canônica de bar-time é M1** (`m1_is_primary`, Cenário B/Ada,
  PROPOSAL §6.1), persistida em `research_bars`.
- **R-10.** **M5, M15, M30, H1, H4, D1** são **derivadas** por agregação
  **determinística** de M1 (`derive(M1, rule, TF)`, função **pura**): open=primeiro,
  high=max, low=min, close=último, volume/financial/trades=soma; VWAP recomputado
  (nunca média de VWAPs); bucket **ancorado no início da sessão B3**; último bucket do
  dia pode ser `is_partial`. **M5…D1 nunca são ingeridos direto** do broker.
- **R-11.** **H1 é computado uma única vez** a partir de M1 e referenciado por ambos os
  modos (fronteira INTRADAY↔SWING). Não existe "H1 intraday" e "H1 swing"; `mode` é uma
  *view* (PROPOSAL §3.5/§6.2).
- **R-12.** A derivação é **pura e reprodutível**: rodar duas vezes produz barras
  **byte-idênticas**. Mudar a regra de agregação **muda o hash → nova run vinculada**,
  nunca edita a anterior (run imutável — Ada).
- **R-13.** **Calendário B3 versionado** (`research_calendar`): `is_trading_day`,
  `session_open/close`, leilões, `early_close`. D1 indexado por `session_date`, não data
  corrida. **Gap overnight é feature** — `close[d]→open[d+1]` preservado; **forward-fill
  de preço overnight proibido** (PROPOSAL §6.3).
- **R-14.** **Rolagem WIN/WDO (swing):** contratos individuais crus preservados
  (`WINM26`, `WING26`); a série contínua (`WIN_c1`) é artefato **derivado e versionado**
  (`roll_rule` + `splice_method`), rastreável ao contrato físico. **Sem regra de rolagem
  versionada + teste de salto** (sem descontinuidade > X·ATR no ponto de rolagem),
  **nenhuma série contínua entra** no cubo lento (gate R0 swing — Ada §6.3).

### 3.4 Persistência research_*
- **R-15.** Todo o estado de research vive em schema/namespace **`research_*`**,
  **separado** das tabelas live. **Não reusa** os continuous aggregates `cam_candles_*`
  como storage canônico (faltam provenance/calendário/snapshot/hash e fere isolamento —
  ADR-015 decisão 1).
- **R-16.** Cada análise referencia um **snapshot imutável** (`research_dataset_snapshots`)
  com **hash composto** (`raw_canonical_hash ⊕ calendar_version ⊕ Σ_TF(rule ⊕ bar_def ⊕
  price_series) ⊕ continuous_series_version`); rerun cria nova run vinculada.
- **R-17.** **Quality checks** gravados em `research_data_quality_checks`: `missing_bars`,
  `bucket_misalignment`, `partial_bar`, `m1_is_primary`, `stale_bar`, `roll_discontinuity`,
  `clock_skew_ms`.
- **R-18.** `DELETE` no namespace `/research` é **cancel/archive/soft-delete** — nunca
  apaga evidência (incluindo kill log). Resultado de run é **imutável** (sem edição manual).

### 3.5 OFI assinado e correlação defasada (cubo rápido — event-time)
- **R-19.** **OFI assinado** (`CaM-RESEARCH §3.1`): para cada negócio `k` de `i`,
  `ε_k ∈ {+1,−1}` (do `flags`/agressor, R-06) e volume `v_k`; fluxo numa janela rolante
  `Δ` (não é candle): `x_i(t;Δ)=Σ ε_k v_k`, normalizado `x̃_i = x_i / Σ v_k ∈ [−1,1]`.
- **R-20.** **Correlação defasada event-time** `ρ_{F→D}(τ)=Corr(x̃_F(t), r_D(t,τ))`
  (`§3.2`), `r(t,h)=ln m(t+h)−ln m(t)`.
- **R-21.** **Hayashi-Yoshida (mata-Epps):** a covariação assíncrona usa o estimador HY
  (`§3.3`) — **sem reamostragem**. Lead-lag por contraste **HRY** `θ̂=argmax|U(θ)|`
  (`§3.4`): sinal de `θ̂` diz quem lidera, valor diz por quanto tempo. **H5 (anti-Epps)
  é refutação obrigatória:** se a correlação ingênua não sobrevive ao HY, é artefato.
- **R-22.** **Event study assinado** (`§3.7`): padronização rolante `z_F(t)`; evento
  `|z_F(t*)|>κ`, sinal `s=sgn(z_F(t*))`; retorno assinado `g(t*,h)=s·r_D(t*,h)`;
  **expectância líquida** `μ̂_h = (1/M)Σ[g−c−IR]` por horizonte. **Taxa de acerto crua é
  proibida como prova** (Art. 28). Condicionado por liquidez do alvo (R-08).
- **R-23.** **Granger / transfer entropy** (`§3.5`) como causalidade direcional
  corroborante (VAR em event-bars finas; net flow se `T_{F→D}>T_{D→F}`).
- **R-24.** **Condição de executabilidade** (`§3.8`): a célula só é candidata se
  `μ̂_{h=λ}>0` após a latência `λ` real do CaM. Edge que vive **< λ** é HFT → **fora de
  escopo** (No-Go).

### 3.6 Cubo lento / estrutura (bar-time, dois modos)
- **R-25.** **Correlação defasada bar-time** `C_{S→D}^{(T)}(δ)=Corr(wᵀ·r_S^{(T)}(t−δ),
  r_D^{(T)}(t))`, `δ ≥ 1` (PROPOSAL §3.1, `§4.2`), por TF e por **modo** (INTRADAY M1–H1;
  SWING H1–D1). Mecanismo é **declarado por modo antes de rodar** (PROPOSAL §3.4/§3.5).
- **R-26.** **Estrutura mecânica anti-hindsight** (`§4.3`): swing por ZigZag (`θ_z`),
  pivô fractal de ordem `n`, S/R objetivo — **definidos por regra fixa antes do teste**.
- **R-27.** **Fibonacci é réu** (`§4.5`): níveis `L_φ`/`E_φ` + feature de toque `d_φ(t)=
  |P(t)−L_φ|/ATR(t)`. Teste de **modelo aninhado**: A (baseline estrutural) vs B (A + fib).
  Fib **só fica** se `Δ=μ̂_B−μ̂_A>0` com significância OOS **e** o coeficiente sobrevive
  aos controles de redundância ("também é máx/mín / número redondo / nó de volume").
  Caso contrário, fib é S/R reetiquetado → cai, usa-se o baseline.

### 3.7 Síntese (R4)
- **R-28.** **Síntese regime × gatilho** (`§7`): `sinal = 1{regime lento favorável} ×
  gatilho de fluxo rápido`. A composição só é registrada como sobrevivente se **supera as
  partes isoladas OOS**, com o trial accounting da **própria** busca de composição incluído.

### 3.8 Validação estatística honesta (transversal R2–R4)
- **R-29.** **Anti-look-ahead (inegociável):** o sinal usa informação **até e inclusive**
  o fechamento da barra `t`; o label é medido **estritamente depois**, a partir do **preço
  executável pós-barra** (`t_exec` = abertura da barra seguinte). **Proibido** reaproveitar
  o mesmo close como feature e como entrada (PROPOSAL §3.1).
- **R-30.** **Trial accounting + DSR de duas camadas (IN, faseado):** cada run grava
  `N_t^{(T)} = |fontes|×|alvos|×|grade δ|×|thresholds|×|regimes|×|variantes|×reruns`;
  por modo `N_t^{intraday}`, `N_t^{swing}`, e global **descontando H1 uma vez**
  (`N_t^{global}=N_t^{intraday}+N_t^{swing}−N_t^{(H1)}`). DSR usa o denominador do **nível
  da afirmação**; **FDR (BH) por modo** (duas famílias, sem pooling); **SPA/Bonferroni** no
  topo (PROPOSAL §4). **Sem confirmação cross-mode como evidência independente** (labels H1
  compartilhados → uma observação, não duas). **O rigor cresce com o corpus:** OFI é viável
  já (agressor provado), mas **DSR pleno exige corpus consolidado** (Jim) — o estado real do
  corpus é reportado em Data Health, **nunca fingido**.
- **R-31.** **"Dado insuficiente" é veredito de 1ª classe** (Art. 30 — confiança subjetiva
  não é evidência): abaixo do piso `N_eff` por (par, δ, TF), o resultado é
  `INSUFFICIENT_DATA`, **distinto** de "sem edge" e de "edge". Crítico para swing/D1
  (PROPOSAL §5.2 — `N_eff ≈ N_barras/k` reduzido pela autocorrelação).
- **R-32.** **Walk-forward + purged CV com embargo wall-clock** (`§5.2`, PROPOSAL §5):
  embargo ≥ horizonte `k` + cauda de autocorrelação, medido em **wall-clock** (purga
  cross-TF por timestamp, não por bar-index). Regime definido **ex-ante** (Ray); edge que
  só existe em regime definido **depois** de ver resultado = No-Go.
- **R-33.** A análise **não emite** sinal, recomendação, candidato operacional, sizing nem
  direção de trade. Produz **evidência descritiva** (correlação, n, δ, expectância,
  veredito) — nada mais (Arts. 34º–36º). Kelly fracionário, se exibido, é **métrica de
  research, não autorização de tamanho** (Nassim).

### 3.9 Isolamento research↔live (barreira técnica)
- **R-34.** O serviço de research **não escreve** em `cam_orders`, `cam_positions`,
  `cam_journal_entries` nem equivalentes operacionais. Escrita restrita a `research_*`
  (idealmente role/usuário de banco sem grant nas tabelas live).
- **R-35.** Módulos de research **não importam** execução nem broker (R-03) — verificável
  estaticamente pelo contrato **import-linter já ativo** (ADR-015) + check de CI.
- **R-36.** Secrets de broker **nunca** em metadata de run, logs, payloads ou commit.

## 4. Contratos

### 4.1 Rotas REST (namespace `/api/v1/research`, read-only sobre o live)

| Método | Endpoint | Uso |
|---|---|---|
| POST | `/api/v1/research/ingest` | dispara ingestão MT5→`research_*` (corpo: `sources[]`, `timeframes[]`, `window`, `with_ticks`). Retorna `snapshot_id` |
| GET | `/api/v1/research/data-health` | cobertura por símbolo/TF, quality flags, status de ingestão, **cobertura M1 real**, liquidez de tick por ativo |
| POST | `/api/v1/research/runs` | lança análise sobre `snapshot_id` (corpo **parametrizável**: `sources[]`, `target(s)`, `delta_grid[]`, `timeframes[]`, `mode`, `lens ∈ {fast,slow}`, `thresholds`). Retorna `run_id` + `N_t` |
| GET | `/api/v1/research/runs` | lista runs + status + contador de tentativas |
| GET | `/api/v1/research/runs/{id}` | resultado: matriz de correlação (`ρ(τ)` ou `C(δ)`), n por célula, DSR/FDR por TF/modo, veredito (`OK`/`INSUFFICIENT_DATA`/`KILLED`) |
| GET | `/api/v1/research/runs/{id}/cube?metric=&lens=&lag=` | fatia do cubo para o heatmap (escalares leves) |
| GET | `/api/v1/research/cells/{run_id}/{F}/{D}/{tau}` | dossiê da célula: decaimento, event study, HY vs ingênua, contraste lead-lag, veredito, checklist Go/No-Go |
| GET | `/api/v1/research/runs/{id}/fib-ab/{cell}` | baseline (A) vs augmentado com fib (B), `Δ` + significância |
| GET | `/api/v1/research/stats/trials` | contador global de tentativas (alimenta DSR) |
| DELETE | `/api/v1/research/runs/{id}` | cancel/archive/soft-delete (R-18) |
| WS | `/api/v1/research/runs/{id}/progress` | progresso de job (reusa WS FastAPI; **sem** fila nova) |

> `POST /runs` cria **job de pesquisa** — **não** ordem, **não** candidato operacional
> (Kevin). Payloads = escalares leves (matriz + n + veredito), **nunca** tick cru (este
> fica no Inspetor — Don).

### 4.2 Schema de dados (`research_*` — migração nova, ADR-015)

- **`research_bars`** — `symbol, timeframe, ts_open, ts_close, session_date, open, high,
  low, close, volume, financial, trades, vwap, is_partial, price_series (raw|adjusted),
  provenance_id, aggregation_rule_id`. **`timeframe` é coluna + dimensão de partição/
  índice** (não tabela por TF). Índice `(symbol, timeframe, session_date)`.
- **`research_ticks`** (decisão Ada R-07) — `symbol, t_msc, price, volume, aggressor
  (+1/−1/0), flags_raw, provenance_id`. Event-time, agressor assinado para OFI.
- **`research_data_sources`** — `id, bar_origin, ts_source, aggressor_source, symbol,
  source_timeframe, window_start, window_end, ingested_at, raw_batch_hash`.
- **`research_dataset_snapshots`** — `id, symbols[], timeframes_included[], mode
  (intraday|swing|both), window, composite_hash, calendar_version, continuous_series_version,
  created_at`. Imutável.
- **`research_aggregation_rules`** — regra determinística versionável/hasheável.
- **`research_calendar`** — calendário B3 versionado (R-13).
- **`research_continuous_series`** — rolagem WIN/WDO (`roll_rule`, `splice_method`, R-14).
- **`research_runs`** — `id, snapshot_id, lens, mode, sources[], target, delta_grid[],
  timeframes[], thresholds, n_trials, status, created_at`. `status ∈ {queued, running,
  done, failed, insufficient_data, killed}`.
- **`research_run_results`** — `run_id, source, target, timeframe, delta_or_tau,
  correlation, mu_net, n_samples, dsr, fdr_q, verdict`.
- **`research_data_quality_checks`** — `snapshot_id, symbol, timeframe, check_name, value, ts`.

### 4.3 Eventos
- v0.5 é síncrono/sob demanda no mínimo viável; progresso de run **pode** reusar o WS
  existente do FastAPI se o PLAN julgar proporcional — caso contrário, polling de
  `GET /runs/{id}`. **Sem** dependência nova de fila de mensagem.

## 5. Casos de uso / cenários

| # | Caso | Esperado |
|---|---|---|
| 1 | Founder seleciona universo seed (`WIN, WDO, VALE3, ITUB4, PETR4, AXIA3, BBDC4, B3SA3`), ingere M1 "máximo disponível" + ticks | `research_bars` (M1 + M5…D1 derivados) + `research_ticks` (com agressor) + `snapshot_id` + provenance + hash; Data Health mostra cobertura M1 real e liquidez de tick por ativo |
| 2 | Rodar OFI/cubo rápido `VALE3→PETR4`, grade τ, lens=fast | `run_id`, `N_t`, `ρ_{F→D}(τ)` event-time, HY (mata-Epps), event study líquido condicionado por liquidez, curva de decaimento, `μ̂_{h=λ}` |
| 3 | Rodar cubo lento bar-time `WIN→VALE3`, modo intraday, grade δ | matriz `C_{S→D}(δ)` por TF; H1 computado uma vez; mecanismo declarado por modo |
| 4 | Rodar Fib A/B sobre célula estrutural | `μ̂_A` vs `μ̂_B`, `Δ` + significância; veredito FIB FICA / FIB CAI |
| 5 | Abrir Quant Lab → Data Health | cobertura por símbolo/TF + quality flags + liquidez de tick antes de qualquer heatmap |
| 6 | Ler dossiê de célula | decaimento, event study, HY vs ingênua, contraste lead-lag, DSR/FDR por TF/modo, checklist Go/No-Go; manchete = expectância líquida + n |
| 7 | Rerun da mesma análise | nova run vinculada; barras byte-idênticas (R-12); nada editado |
| 8 | Trocar universo (parametrização) | nova run com `sources[]`/`target` diferentes, sem alterar código (R-02) |
| 9 | Par/TF com amostra abaixo do piso | célula marcada `INSUFFICIENT_DATA`, não "sem edge" (R-31) |

## 6. Casos limite / exceções

- **Bridge MT5 offline** → ingestão falha segura (R-05); Data Health mostra estado, não inventa.
- **Liquidez de tick esparsa de ação** (PETR4 ~255s/500 ticks) → event study condiciona por
  liquidez (R-08); janela de evento mais longa; capacidade = liquidez no instante do evento.
- **MT5 não entrega M1 suficiente** na janela → reportado em Data Health (R-05); swing/D1
  pode cair em `INSUFFICIENT_DATA` (R-31).
- **Gap overnight** → preservado como feature (R-13); proibido forward-fill.
- **Bucket parcial no fim do pregão** → `is_partial=true` (R-10), não descartado.
- **Rolagem WIN/WDO sem teste de salto** → série contínua **não entra** no swing (R-14).
- **Correlação ingênua que não sobrevive ao HY** → marcada artefato de Epps (R-21), não edge.
- **Edge que vive < latência real** → No-Go executabilidade (R-24); fora de escopo (HFT).
- **Tentativa de escrita em tabela live** → bloqueada por permissão (R-34) — falha, não degrada.

## 7. Classificação P/M/G

| Campo | Valor |
|---|---|
| Classe | **G** (decomposta em sub-versões no PLAN) |
| Rationale | Entrega a **tese completa** — N funcionalidades coordenadas em três ambientes: schema `research_*` novo (bars + ticks com agressor + snapshots + runs + calendário + rolagem), ingestão parametrizável MT5→DB (candles + ticks/`flags`), OFI assinado + ρ defasado event-time + HY + HRY + Granger, cubo lento bar-time dois modos + fib, síntese R4, validação estatística (DSR/FDR/walk-forward), Quant Lab completo. É **G por número de funcionalidades e superfícies**, **não** por modificador de risco/segurança/arquitetura (proibido — Q8 Founder). **Decomposição em sub-versões 0.5.1…0.5.7 é do PLAN (Nico)** — recomendação em SCOPE §6. Nico mantém direito formal de redesenhar a decomposição e contestar esta classe (loop ilimitado com Albert; Founder decide quando parar). |

> Lembrete: P = subitem de funcionalidade existente · M = melhoria/nova funcionalidade ·
> G = N funcionalidades / decomposição. **Sem modificadores de risco** — Q8 Founder.
> **Proibido estimar em horas/dias/semanas.**

## 8. Marcadores de segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (intrabloco no CODE) | **sim** | Isolamento research↔live é código (R-03, R-34, R-35 — import-linter ativo); dados de broker (R-36); persistência de tick/agressor (R-06); nova superfície REST. Kevin entra intrabloco no CODE dos blocos de backend/dados. |
| `qa-sec` (QA-SEC no QA) | **sim** | QA valida a barreira técnica: ausência de escrita live, ausência de import de execução/broker (contrato import-linter verde), namespace `/research`, sem secrets, soft-delete preserva evidência. |

> **Gatilho SEC-GOV ATIVO** (Kevin): dados sensíveis (broker) + integração externa (MT5) +
> nova superfície + fronteira com tabelas operacionais. Conditional Go condicionado à **prova
> de isolamento técnico** (import-linter + permissão de banco) — **ADR-015 já fixa os
> controles de aceite**. Ver [`../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md`](../../../teczi-devflow/NCC-1701/governance/SEC-GOV.md).
> Kevin recomenda, Founder decide.

## 9. Saídas esperadas

- Migração `research_*` aplicada (bars + ticks com agressor + snapshots + runs + calendário
  + rolagem + quality), isolada do live (ADR-015).
- `TickPersister`/ingestão estendida para **persistir o agressor** (`flags` → `aggressor`).
- Feature backend `research/leadlag` (domain puro + repository + routes) — reusa/estende
  `cross_asset_correlation.py` (Pearson defasado já existente).
- OFI assinado + ρ defasado event-time + HY + HRY + Granger; cubo lento dois modos + fib;
  síntese R4; stats layer (trial accounting, DSR/FDR, walk-forward/purged CV).
- Rotas `/api/v1/research/*` funcionais e read-only; universo **parametrizável** por run.
- Quant Lab: Data Health + Explorer + Cell Detail (dossiê Go/No-Go) + Launcher + Registry +
  Fib A/B + Synthesis + badge RESEARCH.
- Prova de isolamento research↔live (artefato SEC-GOV de Kevin — contrato import-linter verde).

## 10. Critérios de aceite

1. Ingestão **parametrizável** (R-02): trocar `sources[]`/`target` muda o universo **sem
   alterar código**; universo seed do 1º teste roda como **dado de run**, não hardcode.
2. `research_bars` com M5…D1 **derivados deterministicamente** de M1 (rerun → byte-idêntico,
   R-12); H1 computado uma vez (R-11).
3. Ticks persistidos **com agressor** (`flags`→`aggressor`, R-06); OFI assinado computável.
4. Toda barra/lote tem **provenance** (R-04) e referencia **snapshot com hash composto** (R-16).
5. Análise respeita **anti-look-ahead** (R-29) — verificável por fixture que falharia se o
   close fosse reusado como entrada.
6. **HY mata Epps** (R-21): a célula só sobrevive se a correlação resiste ao estimador
   assíncrono; correlação ingênua isolada não é aceita como evidência.
7. **Trial accounting** `N_t` por run/modo/TF (R-30); DSR/FDR reportados no **nível correto**;
   par/TF abaixo do piso → `INSUFFICIENT_DATA` (R-31). Estado do corpus exposto em Data Health
   (DSR pleno **não fingido**).
8. **Fib é réu** (R-27): só fica com `Δ>0` OOS + sobrevivência aos controles; senão cai.
9. **Nenhuma** rota/serviço de research escreve em `cam_orders`/`cam_positions`/
   `cam_journal_entries`; **nenhum** módulo de research importa execução/broker (R-34, R-35) —
   contrato **import-linter verde** + check de CI.
10. Quant Lab exibe **Data Health antes** de leitura de resultado; **badge RESEARCH**
    permanente; vocabulário de pesquisa; **zero** affordance de ordem/Risk Engine.
11. Liquidez de tick não-uniforme **visível** em Data Health (R-08); não escondida.
12. Build/checks/testes verdes; Kevin (QA-SEC) valida a barreira técnica.

## 11. Delta no DVP (se aplicável)

Sem alteração de direção estratégica do CaM. Materializa a Research Lane já prevista nas teses,
ancorada no estado real do MT5 (com agressor **provado**). Não promove estratégia nem altera a
fase do CaM (Fase 0 — Construção).

## 12. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| v0.5 (rev. 1) | 2026-06-03 | Draft — R0 dados + 1ª análise bar-time; OFI/tick em LATER (assumido) | (substituído) |
| v0.5 (rev. 2) | 2026-06-03 | **Reescrito para a tese completa.** OFI/tick **IN** (agressor provado — `PROBE-AGGRESSOR-RESULT.md`); persistir `flags`/agressor (R-06/R-07). Universo **parametrizável** 1ª classe (R-02). HY/HRY/Granger/event study/cubo lento/fib/síntese/DSR-FDR-walk-forward como regras numeradas. Decomposição em sub-versões movida ao PLAN. Referencia ADR-015 + import-linter ativo. | (pendente Founder) |

---

### Quando NÃO usar este SPEC
- **S1 (ORB 60m WIN)** é trilha separada — **OUT**.
- Execução real, envio de ordem, candidato operacional, paper/live, escrita em tabelas live —
  **OUT** (Arts. 34º–36º).
- Promoção de célula a estratégia segue o Go/No-Go (`CaM-RESEARCH §6`) + pipeline formal do CaM,
  fora desta SPEC.
- Nenhuma estimativa em horas/dias/semanas. Sem auto-approval. **Founder aprova SCOPE e SPEC.**

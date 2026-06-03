---
template: PLAN
phase: PLAN
status: Approved (letscode=true sub-versão 0.5.1) — Founder 2026-06-03
produto: CaM — research lane
codinome: research-cubo-leadlag
versao: v0.5
lead: Nico
co_lead: Albert (loop P/M/G)
sec: Kevin (SEC-GOV ativo)
aprovador: Founder
vive_em: project/cam-cockpit/plans/PLAN-v0.5-LEADLAG-RESEARCH.md
data: 2026-06-03
---

# PLAN v0.5 — Lead-Lag Research Lane (decomposição em sub-versões)

> **Data:** 2026-06-03 · **Lead:** Nico · **SEC-GOV:** Kevin · **Aprovador:** Founder
> **Entrada:** SPEC v0.5 (APROVADA) + SCOPE v0.5 (APROVADO) + ADR-015 (Accepted).
> Decompõe a tese completa em **sub-versões 0.5.1 → 0.5.7**. O Founder liberou
> `letscode=true` para **0.5.1 (Dados/R0)** com execução; as demais sub-versões têm
> gate próprio.

---

## 1. Resumo do plano

A SPEC v0.5 é classe **G** (a tese inteira). Decompõe-se em **7 sub-versões sequenciais**,
cada uma um entregável com gate Founder. **Dados primeiro** (consenso THESIS-ANALYSIS-01):
sem R0 reprodutível, nenhum ranking de edge é confiável. Execução começa por **0.5.1**.

## 2. Referência de entrada

- SPEC: [`../specs/SPEC-v0.5-LEADLAG-RESEARCH.md`](../specs/SPEC-v0.5-LEADLAG-RESEARCH.md) — **APROVADA** 2026-06-03 (36 regras R-01..R-36).
- SCOPE: [`../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md`](../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md) — **APROVADO** (faseamento §6).
- ADR: [`../adrs/ADR-015-research-lane-isolada.md`](../adrs/ADR-015-research-lane-isolada.md) — schema `research_*`, isolamento, import-linter ativo.
- Evidência: [`../research/leadlag/PROBE-AGGRESSOR-RESULT.md`](../research/leadlag/PROBE-AGGRESSOR-RESULT.md) — agressor provado.

## 3. Avaliação de P/M/G

| Campo | Valor |
|---|---|
| Classe na SPEC | **G** |
| Concordância de Nico | **Sim** — a tese inteira é G; decompõe-se em sub-versões, cada uma M/P |
| Loop com Albert | Sem divergência: 0.5.1..0.5.7 mapeiam o faseamento sugerido no SCOPE §6 |
| Decisão final | **G**, decomposta. 0.5.1 liberado para CODE; demais com gate próprio |

## 4. Decomposição em sub-versões (mapa)

| Sub | Entrega | Lente | Gate |
|---|---|---|---|
| **0.5.1** | **Dados/R0** — schema `research_*`, ingestão parametrizável MT5→DB (candles + ticks com agressor), barras canônicas M1→derivadas determinísticas, snapshot/hash, quality checks, Data Health, isolamento técnico | — | ✅ **CONCLUÍDO** — 8/8 papéis ingeridos ao vivo (Founder validou 2026-06-03) |
| **0.5.2** | OFI/cubo rápido (R2) — OFI assinado, ρ defasado event-time, event study líquido condicionado por liquidez, decaimento | fast | ✅ **CONCLUÍDO** (núcleo + UI; Founder validou) |
| **0.5.3** | Validação estatística — trial accounting, DSR (camadas), FDR/SPA, walk-forward + purged CV, "dado insuficiente" | transversal | ✅ **letscode=true** (Founder 2026-06-03 "segue para 0.5.3") |
| **0.5.4** | Cubo lento/swing (R3) — `C_{S→D}(δ)` bar-time, modos intraday/swing, H1 único, rolagem WIN/WDO + teste de salto | slow | Founder após 0.5.3 |
| **0.5.5** | Fibonacci — modelo aninhado A/B, controle de redundância (fib réu) | slow | Founder após 0.5.4 |
| **0.5.6** | Síntese (R4) — regime lento × gatilho rápido; composição > partes | both | Founder após 0.5.5 |
| **0.5.7** | Quant Lab completo — Explorer 3D, Cell Detail, Launcher, Registry, Fib A/B, Synthesis | — | Founder após corpus |

> HY/HRY/Granger/transfer entropy acompanham 0.5.2/0.5.3 (event-time). UI cresce em
> paralelo (Data Health em 0.5.1; demais telas conforme o backend amadurece).

---

## 5. TASKs do 0.5.1 — Dados/R0 (por ambiente, com subtasks)

> **Foco do CODE atual.** Convenção: `T-{AMB}-{n}`; subtask `{T}.f{n}`. TDD onde houver
> lógica pura. **Sem estimativa de tempo.** Lente da SPEC entre parênteses (R-*).

### 🗄️ Ambiente Dados-DB

**T-DB-1 — Migração schema `research_*`** · `sec`

| Subtask | Saída | SPEC |
|---|---|---|
| T-DB-1.f1 | `research_bars` (symbol, timeframe, ts_open, ts_close, session_date, OHLC, volume, financial, trades, vwap, is_partial, price_series, provenance_id, aggregation_rule_id); índice `(symbol, timeframe, session_date)` | R-09, R-15, §4.2 |
| T-DB-1.f2 | `research_ticks` (symbol, t_msc, price, volume, aggressor ±1/0, flags_raw, provenance_id) — event-time, hypertable Timescale | R-06, R-07 |
| T-DB-1.f3 | `research_data_sources` (bar_origin, ts_source, aggressor_source, symbol, source_timeframe, window, ingested_at, raw_batch_hash) | R-03 |
| T-DB-1.f4 | `research_dataset_snapshots` (symbols[], timeframes[], mode, window, composite_hash, calendar_version, created_at) imutável | R-16 |
| T-DB-1.f5 | `research_runs` + `research_run_results` + `research_data_quality_checks` + `research_aggregation_rules` | R-17, §4.2 |
| T-DB-1.f6 | `research_calendar` (B3 versionado) — seed mínimo de pregões | R-13 |

### ⚙️ Ambiente Backend (`cam/features/research/leadlag/`)

**T-BE-1 — Ingestão parametrizável MT5→DB** · `sec`

| Subtask | Saída | SPEC |
|---|---|---|
| T-BE-1.f1 | Adaptador de ingestão: chama bridge (`get_candles`) na **borda**, não importa execução; universo/janela parametrizáveis | R-01, R-02, R-35 |
| T-BE-1.f2 | Persiste M1 canônico em `research_bars` + provenance + `raw_batch_hash` | R-03, R-09 |
| T-BE-1.f3 | Persiste ticks com **agressor** (`flags`→±1/0) em `research_ticks` (estende a lógica do `TickPersister`, que hoje não grava flags) | R-06, R-07 |
| T-BE-1.f4 | Bridge offline → falha segura (sem dado parcial silencioso) | R-05 |

**T-BE-2 — Barras canônicas determinísticas (função pura)** · TDD

| Subtask | Saída | SPEC |
|---|---|---|
| T-BE-2.f1 | `derive(M1, rule, TF)` puro: M5/M15/M30/H1/H4/D1; open=1º, high=max, low=min, close=último, volume/financial/trades=soma; bucket ancorado na sessão B3; `is_partial` | R-10 |
| T-BE-2.f2 | **H1 computado uma vez** (fronteira intraday↔swing) | R-11 |
| T-BE-2.f3 | Reprodutibilidade: rerun byte-idêntico; teste de determinismo por fixture | R-12 |
| T-BE-2.f4 | Gap overnight preservado (`close[d]→open[d+1]`), forward-fill proibido | R-13 |

**T-BE-3 — Snapshot, hash composto e quality checks** · TDD

| Subtask | Saída | SPEC |
|---|---|---|
| T-BE-3.f1 | `composite_hash` (raw ⊕ calendar ⊕ Σ_TF(rule ⊕ bar_def)); snapshot imutável | R-16 |
| T-BE-3.f2 | Quality checks: `missing_bars`, `bucket_misalignment`, `partial_bar`, `m1_is_primary`, `stale_bar` | R-17 |
| T-BE-3.f3 | Run accounting básico (registro de run, `n_trials`, status) | R-30 (parcial) |

**T-BE-4 — Rotas REST read-only** · `sec`

| Subtask | Saída | SPEC |
|---|---|---|
| T-BE-4.f1 | `POST /api/v1/research/ingest` (sources[], timeframes[], window, with_ticks) → snapshot_id | §4.1 |
| T-BE-4.f2 | `GET /api/v1/research/data-health` (cobertura símbolo/TF, quality flags, cobertura M1, liquidez de tick) | §4.1, R-08 |
| T-BE-4.f3 | `DELETE` = soft-delete/archive (nunca apaga evidência) | R-18 |
| T-BE-4.f4 | Registrar router no compositor `api/main.py` | §4.1 |

### 🖥️ Ambiente Frontend (`features/quant-lab/` — UI-R0 mínima)

**T-FE-1 — Quant Lab + Data Health**

| Subtask | Saída | SPEC |
|---|---|---|
| T-FE-1.f1 | Rota `/lab` + badge **RESEARCH** permanente; separação visual do Cockpit | Don, §UI |
| T-FE-1.f2 | Data Health: cobertura por símbolo/TF + quality flags + liquidez de tick **antes** de qualquer leitura | R-08, caso 5 |
| T-FE-1.f3 | Form de ingestão (universo seed parametrizável) → `POST /ingest` | R-01, UNIV |
| T-FE-1.f4 | Item no sidebar (atrás de `visibleInMvp` apropriado) | — |

### 🛡️ Ambiente SEC-GOV (transversal — Kevin)

**T-SEC-1 — Prova de isolamento research↔live**

| Subtask | Saída | SPEC |
|---|---|---|
| T-SEC-1.f1 | Confirmar contrato import-linter "Research Lane nao importa execucao" verde com o slice `research/leadlag` | R-35 |
| T-SEC-1.f2 | Assert: serviço de research só escreve em `research_*` (sem INSERT/UPDATE em tabelas live) | R-34 |
| T-SEC-1.f3 | Sem secrets em metadata/log/payload | R-36 |

---

## 6. Dependências (0.5.1)

```
T-DB-1 (schema) ──► T-BE-1 (ingestão) ──► T-BE-2 (barras) ──► T-BE-3 (snapshot/QC) ──► T-BE-4 (REST) ──► T-FE-1 (UI)
                                                                                          │
T-SEC-1 (isolamento) ── transversal, fecha o gate ─────────────────────────────────────┘
```

## 7. Riscos identificados (0.5.1)

- **MT5 limita M1 histórico** → Data Health reporta cobertura real; swing pode cair em `INSUFFICIENT_DATA` (aceito).
- **`research_ticks` cresce rápido** (tick é volumoso) → hypertable Timescale + compressão (herda padrão de `cam_market_ticks`).
- **Reuso indevido de `cam_candles_*`** → proibido por ADR-015; barras vêm de `research_bars`.
- **Acoplamento research→mt5_integration** → ingestão chama o bridge na borda; import-linter guarda.

## 8. Reuso aplicado

- `cross_asset_correlation.py` (Pearson puro) — base das correlações (0.5.2).
- `TickPersister` — padrão de persistência em lote; estende para gravar `flags`/agressor.
- Bridge MT5 (`service.get_candles`, `probe_ticks`) — fonte de dado.
- Padrão de migração alembic (`alembic/versions/`), feature-slice (`regime` como molde),
  hypertable Timescale (`cam_market_ticks`), Inspetor (precedente read-only frontend).
- ADR-015 + import-linter já ativos.

## 9. `letscode`

| Campo | Valor |
|---|---|
| Status | **`true` para 0.5.1** ✅ |
| Aprovado por | **Carlos (Founder) — 2026-06-03** ("scop e spec aprovada derive os plans... e já vá para code") |
| Escopo liberado | **0.5.1 (Dados/R0)** — T-DB-1, T-BE-1..4, T-FE-1, T-SEC-1. Sub-versões 0.5.2+ têm gate próprio. |

## 10. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1.0 | 2026-06-03 | Decomposição 0.5.1..0.5.7; TASKs do 0.5.1 por ambiente; letscode 0.5.1 | Carlos (Founder) |

---

> CODE do 0.5.1 com Nikola (+Linus intrabloco, +Kevin no `sec`). Research-only.
> Risk Engine intocado. Sub-versões seguintes voltam ao gate do Founder.

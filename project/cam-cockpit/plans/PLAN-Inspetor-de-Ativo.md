---
template: PLAN
phase: PLAN
status: Draft — aguarda letscode do Founder
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
version: 1.0
date: 2026-05-31
lead: Nico
co-lead: Albert
aprovador: Founder
---

# PLAN — INSPETOR · Inspetor de Ativo (MVP)

> **Data:** 2026-05-31
> **Status:** Draft — aguarda `letscode` do Founder
> **Lead:** Nico · **Co-lead:** Albert (loop P/M/G) · **Aprovador:** Carlos (Founder)
> **Organização (diretriz do Founder):** TASKs **fechadas por ambiente** (EA · Backend · Frontend),
> com **subtasks por feature**. Cada subtask referencia a regra da SPEC e o bloco do SCOPE.

---

## 1. Resumo do plano

Executar o Inspetor em **3 ambientes paralelos** com um gate Founder único ao final. O ambiente
**EA** estende o `cam_bridge` (read-only) com candles/book/símbolos; o **Backend** preenche 3 slices
auto-contidos (`market_data`, `fundamentals`, `regime`); o **Frontend** oculta 13 telas e constrói a
tela do Inspetor (gráfico + book + fundamentos + dividendos + regime). Governança (ADR-014) **já
ratificada** — pré-CODE cumprido.

## 2. Referência de entrada

- **SPEC:** [`../specs/SPEC-Inspetor-de-Ativo.md`](../specs/SPEC-Inspetor-de-Ativo.md) — **Approved** 2026-05-31 (regras R-01..R-26; matriz de camadas §7.1).
- **SCOPE:** [`../scopes/SCOPE-Inspetor-Consolidado.md`](../scopes/SCOPE-Inspetor-Consolidado.md) — blocos BL-1..BL-8.
- **DAS:** [`../DAS.md`](../DAS.md) v1.1 (corrigido por ADR-014).
- **ADR:** [`../adrs/ADR-014-mt5-market-data-read-only.md`](../adrs/ADR-014-mt5-market-data-read-only.md) — **Accepted**.

## 3. Avaliação de P/M/G

| Campo | Valor |
|---|---|
| Classe na SPEC | **G** |
| Concordância de Nico | **Sim** — toca 3 ambientes + governança; cada slice é M, o conjunto é G e exige decomposição com gate único |
| Re-classificação proposta | Nenhuma |
| Loop com Albert | Sem divergência. Albert confirma que BL-8 (regime) é núcleo (decisão Founder) e cabe no mesmo gate. |
| Decisão final | **G**, organizada por ambiente (Founder) |

---

## 4. TASKs por ambiente (com subtasks de feature)

> **Convenção de IDs:** `T-{AMBIENTE}-{n}` para a TASK; `{T}.f{n}` para a subtask de feature.
> **TDD First** (compromisso #12): cada subtask de código nasce com teste. **Sem estimativa de tempo.**

### 🛡️ Ambiente 0 — Governança (pré-CODE) — ✅ CONCLUÍDO

| TASK | Saída | Bloco | Estado |
|---|---|---|---|
| T-GOV-1 | `ADR-014` (MT5 market data read-only) | — | ✅ Accepted (2026-05-31) |
| T-GOV-2 | Correção do DAS (§2 camada de market data, §3 ADRs, §9 não-decisões, §11 histórico) | — | ✅ Feito (DAS v1.1) |

---

### 🤖 Ambiente A — EA / MQL5 (`apps/cam-cockpit/mql5/`)

> Estende o **`cam_bridge.mq5` v0.3 existente** — **não criar EA novo**. Tudo read-only,
> allowlistado (CA15.1/CA15.3). `sec` **crítico** — Kevin valida intrabloco.

**T-EA-1 — Estender `cam_bridge` para o Inspetor** · Bloco BL-2 · `sec` crítico

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-EA-1.f1 | `GET_CANDLES(symbol, timeframe, count)` via `CopyRates` → REP | R-04 | Resposta `{candles:[{ts,o,h,l,c,v}]}`; `count` limitado |
| T-EA-1.f2 | Canal PUB `mt5.book` (`MarketBookAdd` + `OnBookEvent`) | R-05 | PUB de níveis bid/ask; condicional ao ativo |
| T-EA-1.f3 | `GET_SYMBOLS` (`SymbolsTotal`/`SymbolName`) → REP | R-06 | Lista de símbolos disponíveis |
| T-EA-1.f4 | `SUBSCRIBE`/`UNSUBSCRIBE(symbol)` (`SymbolSelect`) | R-06 | EA passa a observar o símbolo pesquisado |
| T-EA-1.f5 | Allowlist estendida + rejeição/log de comando fora dela | R-02, R-03 | 11 comandos read-only; `UNAUTHORIZED_COMMAND` logado |
| T-EA-1.f6 | Permitir conta **REAL** read-only (`InpRequireDemoAccount=false` consciente) | R-10 | Guard documentado; **sem** comando de escrita; aval Kevin |
| T-EA-1.f7 | Revisar buffer em `cam_zmq.mqh` para payload de candles maior | R-04 | Sem truncamento de resposta REP |
| T-EA-1.f8 | **Prova read-only:** `grep OrderSend` no `.mq5` = vazio + teste de allowlist | R-02 (CA15.1) | Critério bloqueante Kevin |

---

### ⚙️ Ambiente B — Backend / FastAPI (`apps/cam-cockpit/backend/cam/features/`)

> 3 slices **auto-contidos** (ADR-013) — nenhum importa o outro; composição só na API.
> `market_data/service.py` é stub vazio; `fundamentals/` já tem Protocol + 7 R-20.

**T-BE-1 — `features/market_data/` (preencher o stub)** · Bloco BL-3 · `qa-sec`

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-BE-1.f1 | Subscriber ZeroMQ (`mt5.tick`/`mt5.book`/`mt5.heartbeat`) + normalização | R-05, R-09 | Consome PUB; status OFFLINE em ausência de heartbeat |
| T-BE-1.f2 | REP client (`GET_CANDLES`, `GET_SYMBOLS`, `SUBSCRIBE`) | R-04, R-06 | Cliente tipado para o EA |
| T-BE-1.f3 | Persistência `cam_market_ticks` (+ book snapshots) com proveniência | R-07 | `source="mt5.cam_bridge"`, `ts_recv`; reusa `provenance.py` |
| T-BE-1.f4 | Resolução de símbolo (ticker B3 ↔ MT5: sufixos, `WIN$`/`WINM25`) | R-08 | 404 claro p/ símbolo inexistente; reusa `instruments_loader.py` |
| T-BE-1.f5 | Endpoints REST (`/market/symbols`, `/symbol/{ticker}`, `/candles`) | §4.2 | Contratos da SPEC §4.2 |
| T-BE-1.f6 | WS `/ws/market/{symbol}` (`tick`/`book`/`status`) | §4.2, R-09 | Falha segura: emite `status:OFFLINE` |
| T-BE-1.f7 | Testes: contrato ZMQ, resolução de símbolo, falha segura (sem MT5 em CI via mock) | §10 | qa-sec: parsing seguro de payload |

**T-BE-2 — `features/fundamentals/` (estender coletor existente)** · Bloco BL-6 · `qa-sec`

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-BE-2.f1 | `BrapiSource(FundamentalsSource)` — token `keyring`/`.env` | R-11, R-15 | Nova fonte no Protocol já existente; sem token commitado |
| T-BE-2.f2 | Mapeamento dos 7 R-20 + EV/EBITDA bônus; `N/A` por campo ausente | R-12, R-13 | Reusa `cam_fundamentals_snapshot` (campos já existem) |
| T-BE-2.f3 | 2 projeções de dividendo (run-rate 12m + DY-médio 3–5a × preço) | R-14 | Ambas rotuladas "estimativa" |
| T-BE-2.f4 | Cache TTL (6–24h) + flag `stale` em falha de rede | R-15, §6 | Não derruba a tela em rate limit/timeout |
| T-BE-2.f5 | Endpoint `GET /fundamentals/{ticker}` (futuro → bloco null) | §4.3, R-13 | Contrato da SPEC §4.3 |
| T-BE-2.f6 | Testes: `BrapiSource` via fixture/mock (sem rede em CI) | §10 | qa-sec: timeout, sanitização de resposta |

**T-BE-3 — `features/regime/` (novo slice)** · Bloco BL-8 · `qa-sec`

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-BE-3.f1 | Vendorizar funções puras Markov (com atribuição Roan/Lewis Jackson) | R-23, R-24 | `label_regimes`, `build_transition_matrix`, `stationary_distribution`, `signal_from_matrix`, `walk_forward_backtest`; **sem yfinance**; **sem rodar instalador** |
| T-BE-3.f2 | Leitura de `cam_candles_*` (NÃO importa `market_data`) | R-22 | Close dos candles do CaM → série de entrada |
| T-BE-3.f3 | Endpoint `GET /regime/{symbol}?timeframe&window&threshold` | §4.5, R-21 | Contrato §4.5; só `type:stock` |
| T-BE-3.f4 | Disclaimer + caveats no payload | R-26 | `"histórico, não preditivo"` |
| T-BE-3.f5 | Testes: determinismo das funções puras; read-only (papel A) | R-25, §10 | qa-sec: sem sinal de execução |

---

### 🖥️ Ambiente C — Frontend / React (`apps/cam-cockpit/frontend/src/`)

> Nova `features/inspetor/`. **Sem deletar** componentes/rotas/testes das telas ocultadas.

**T-FE-1 — Simplificação do cockpit** · Bloco BL-1 · *(independente — pode iniciar já)*

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-FE-1.f1 | `visibleInMvp?: boolean` em `nav.tsx` + filtro no `Sidebar.tsx` | R-17 | 4 itens visíveis (Inspetor, Cockpit, Constituição, Configurações) |
| T-FE-1.f2 | Rota `/inspetor` (registrada em `router.tsx`) + página vazia | R-18 | Rotas ocultas seguem acessíveis por URL |

**T-FE-2 — Inspetor base (busca + gráfico)** · Bloco BL-4

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-FE-2.f1 | `SymbolSearch` (autocomplete via `/market/symbols`) | §3 R-08 | Busca por ticker |
| T-FE-2.f2 | `CandleChart` (`lightweight-charts`; verificar React 19 / fallback `recharts`) | §6 | Gráfico histórico via `/market/candles` |
| T-FE-2.f3 | `TimeframeSelector` (M1…MN1; default H1) | R-04 | Recarrega candles ao trocar |
| T-FE-2.f4 | Hook WS (tick live) + indicador `ONLINE/OFFLINE` + **banner REAL** | R-09, R-10 | Falha segura visível; não mente sobre dado fresco |

**T-FE-3 — Book panel** · Bloco BL-5

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-FE-3.f1 | `BookTable` condicional (oculto/aviso se indisponível) | R-05, §5 | "Book não disponível" quando ausente |

**T-FE-4 — Fundamentos + Dividendos** · Bloco BL-7

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-FE-4.f1 | `FundamentalsPanel` + 7 `IndicatorCard` (só Ação/FII; `N/A` + tooltip) | R-12, R-13 | Bloco omitido p/ futuros |
| T-FE-4.f2 | `DividendsTable` (histórico) + 2 estimativas rotuladas | R-14 | "estimativa" visível |

**T-FE-5 — Bloco de Regime** · Bloco BL-8

| Subtask | Feature | SPEC | Saída |
|---|---|---|---|
| T-FE-5.f1 | `RegimePanel` (estado, matriz 3×3, estacionária, sinal, Sharpe/maxDD) | R-21 | Só ações |
| T-FE-5.f2 | Disclaimer "histórico, não preditivo" + caveats visíveis | R-26 | Honestidade no rótulo |

---

## 5. Dependências

```
T-GOV-1/2 ✅ (pré-CODE cumprido)
        │
        ├── T-FE-1 ............................ independente (inicia já — alívio de navegação)
        │
        ├── T-EA-1 ──► T-BE-1 ──► T-FE-2 ──► T-FE-3
        │                  │
        │                  └──► T-BE-3 ──► T-FE-5     (regime lê cam_candles_* gerados por T-BE-1)
        │
        └── T-BE-2 ──► T-FE-4 ................. paralelo a EA/T-BE-1 (cano de fundamento independente)
```

| TASK | Depende de |
|---|---|
| T-FE-1 | — |
| T-EA-1 | T-GOV ✅ |
| T-BE-1 | T-EA-1 |
| T-BE-2 | — (paralelo) |
| T-BE-3 | T-BE-1 (candles persistidos) |
| T-FE-2 | T-BE-1 |
| T-FE-3 | T-BE-1 |
| T-FE-4 | T-BE-2 |
| T-FE-5 | T-BE-3 + T-FE-2 |

**Ordem sugerida (sem tempo):** T-FE-1 → T-EA-1 → T-BE-1 → (T-FE-2 + T-FE-3) ‖ (T-BE-2 → T-FE-4) → T-BE-3 → T-FE-5. **Gate Founder único** ao final.

## 6. Riscos identificados

Herdados do SCOPE §15 (EA aborta em REAL → `InpRequireDemoAccount=false` + Kevin; EA single-thread →
limitar `count`; símbolo MT5 ≠ B3 → resolução; brapi free tier → cache; `lightweight-charts` × React 19
→ fallback). Risco de PLAN adicional:

- **Continuous aggregates `cam_candles_*` inativos** → T-BE-3 (regime) sem fonte. Mitigação: T-BE-1.f3
  confirma a cadeia tick → candle antes de T-BE-3 iniciar.

## 7. Reuso aplicado

- **EA:** estende `cam_bridge.mq5` v0.3 + `cam_zmq.mqh` (não recria).
- **Backend `fundamentals`:** Protocol `FundamentalsSource` + `PlaceholderSource` + tabela
  `cam_fundamentals_snapshot` com os **7 R-20 já existentes** — `BrapiSource` é só uma nova fonte.
- **Backend `market_data`:** reaproveita `provenance.py`, `instruments_loader.py`, `repository.py`,
  `schemas.py` (orientados a CSV, adaptáveis).
- **Shared Kernel:** `_shared/events`, `_shared/audit`, `_shared/infra`, `_shared/domain`.
- **Frontend `_shared`:** Header (indicador WS), `EnvBanner` (REAL/DEMO), `AppShell`, `Sidebar`.
- **Decisões:** ADR-013 (vertical slice), ADR-006 (IA read-only), ADR-004 (TimescaleDB), ADR-014.

## 8. `letscode`

| Campo | Valor |
|---|---|
| Status | **`false`** |
| Aprovado por | — (aguarda Founder) |
| Motivo se `false` ainda | PLAN recém-emitido; aguarda ratificação do Founder para abrir CODE. Sugestão: liberar **T-FE-1** primeiro (independente, baixo risco, alívio imediato de navegação) e o restante em seguida. |

## 9. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1.0 | 2026-05-31 | Draft inicial — TASKs por ambiente (EA/Backend/Frontend) com subtasks de feature | — (aguarda Founder) |

---

> **Gate PLAN/Founder:** ao aprovar, marcar `letscode=true` (total ou por TASK). CODE segue com Nikola
> (+Linus intrabloco, +Kevin no `sec` de T-EA-1).
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

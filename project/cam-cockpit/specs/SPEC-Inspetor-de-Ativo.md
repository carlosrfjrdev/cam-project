---
template: SPEC
phase: SPEC
status: Draft
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
version: 1.0
date: 2026-05-31
lead: Albert
aprovador: Founder
---

# SPEC — INSPETOR · Inspetor de Ativo (MVP)

> **Data:** 2026-05-31
> **Status:** Draft — aguarda aprovação do Founder
> **Produto:** CaM — The Carlos Alternative Money
> **Lead:** Albert · **Aprovador:** Carlos (Founder)

---

## 1. Resumo

Especifica uma tela **read-only** onde o operador pesquisa um ativo e o CaM exibe, ao vivo, o
**gráfico** (candles históricos + tick e book do MT5 via EA `cam_bridge`/ZeroMQ) e, para papéis à
vista (ações/FIIs), os **7 indicadores fundamentalistas do R-20** e **dois cenários de dividendo**
(via brapi.dev). Nenhuma superfície de execução. Em paralelo, simplifica o cockpit ocultando 13 das
17 telas do sidebar sem deletar código.

## 2. Referências de entrada

- **SCOPE:** [`../scopes/SCOPE-Inspetor-Consolidado.md`](../scopes/SCOPE-Inspetor-Consolidado.md) — consolida e revoga `SCOPE-evolution2`, `SCOPE-Inspetor-de-Ativo` e `SCOPE-Inspetor-de-Ativo (1)`.
- **DAS vigente:** [`../DAS.md`](../DAS.md) — **desatualizado** quanto a broker/SO (ver R-13 e ADR-014).
- **ADRs aplicáveis:** ADR-013 (vertical slice), ADR-006 (IA sem autoridade), ADR-004 (TimescaleDB), ADR-003 (React/Vite/MUI), ADR-002 (FastAPI). **ADR-014 (novo, requerido)** — MT5 como market data read-only.
- **Constituição:** Arts. 6º, 13º, 18º, 25º, 34º–36º; CA15.1/CA15.3 (allowlist do bridge).
- **Estado real do código:** `mql5/experts/cam_bridge.mq5` v0.3; `features/market_data/` (service.py stub); `features/fundamentals/multi_source_collector.py` (Protocol + 7 R-20 + `cam_fundamentals_snapshot`).

## 3. Regras de negócio

### Market data (cano de preço)

- **R-01.** O único canal de dados de mercado é o EA `cam_bridge` via ZeroMQ. O pacote Python `MetaTrader5` **não** é usado no caminho operacional.
- **R-02.** O EA é **read-only por construção**: nenhum `OrderSend`/`OrderClose`/`PositionOpen`/`PositionClose` existe no arquivo (CA15.1). Qualquer comando REP fora da allowlist é rejeitado e logado (CA15.3).
- **R-03.** Allowlist REP completa: `PING, GET_STATE, GET_POSITIONS, GET_SYMBOL_INFO, GET_VERSION, PAUSE_EA, RESUME_EA, GET_CANDLES, GET_SYMBOLS, SUBSCRIBE, UNSUBSCRIBE`. Comandos de escrita (`SUBMIT_ORDER` etc.) **nunca** entram aqui (vivem só em `cam_risk_mirror.mq5`, fora deste slice).
- **R-04.** Candles históricos vêm via REP `GET_CANDLES(symbol, timeframe, count)` (`CopyRates`). `count` limitado no MVP (ex.: ≤ 5.000 barras ou ≤ 1 ano em M5) para não travar o heartbeat do EA single-thread.
- **R-05.** Tick ao vivo vem via PUB `mt5.tick` (já publicado pelo EA). Book ao vivo vem via PUB `mt5.book` (novo: `MarketBookAdd`/`OnBookEvent`), **condicional** — se a corretora não fornece DOM para o ativo, o canal não publica e a tela exibe "Book não disponível".
- **R-06.** `GET_SYMBOLS` retorna os símbolos disponíveis no terminal. `SUBSCRIBE(symbol)` faz `SymbolSelect(symbol, true)` e passa o EA a observar o símbolo pesquisado; `UNSUBSCRIBE` reverte.
- **R-07.** Todo tick recebido é persistido em `cam_market_ticks` com proveniência (fonte=`mt5.cam_bridge`, ts de recepção). Continuous aggregates geram `cam_candles_*`. Nenhum tick histórico massivo é renderizado na tela.
- **R-08.** **Resolução de símbolo:** o backend mapeia ticker B3 ↔ símbolo MT5 (sufixos, futuros `WIN$`/`WINM25`/`WDO$`). Símbolo inexistente no MT5 → 404 com mensagem clara.
- **R-09.** **Falha segura:** EA caído/ZMQ sem heartbeat → WS emite `status: OFFLINE`; a tela mostra "sem dado fresco", nunca um estado que sugira operação liberada.
- **R-10.** **Conta REAL read-only:** o EA hoje aborta em conta REAL (`InpRequireDemoAccount=true`). Para o Inspetor na conta real de Carlos, `InpRequireDemoAccount=false` é setado conscientemente. Pré-condições (SEC-GOV/Kevin): (a) banner **REAL** permanente no header; (b) verificação automatizada de que a allowlist não contém comando de escrita; (c) audit log da sessão.

### Fundamentos (cano de fundamento)

- **R-11.** Fundamentos e dividendos vêm da **brapi.dev** (free tier) via nova `BrapiSource` implementando o Protocol `FundamentalsSource` já existente. Scraping (Fundamentus/StatusInvest) **não** entra no MVP — fica em TD-v0.4-01 (LATER).
- **R-12.** Indicadores exibidos = **7 do R-20**: DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC (campos já em `cam_fundamentals_snapshot`). EV/EBITDA é **bônus** opcional se a brapi retornar. Campo ausente → `N/A` com tooltip.
- **R-13.** Bloco de fundamentos só aparece para **Ação** e **FII**. Para **futuro** (WIN/WDO) a seção é **omitida** (sem erro). FII: P/L, ROE, Dívida/EBITDA, ROIC normalmente `N/A` (não aplicável) — tooltip explica.
- **R-14.** **Duas projeções de dividendo**, lado a lado, ambas rotuladas **"estimativa"**:
  - **Modelo A — Run-rate 12m:** soma dos proventos dos últimos 12 meses.
  - **Modelo B — DY-médio 3–5 anos × preço atual:** DY médio histórico aplicado ao preço corrente.
- **R-15.** Fundamentos são **cacheados** (TTL alinhado à atualização da brapi; ex.: 6–24h). Token brapi (se usado) via `keyring`/`.env`, **nunca** commitado.
- **R-16.** `features/market_data/` e `features/fundamentals/` são auto-contidos (ADR-013) — um **nunca** importa o outro. Composição só na API e no frontend.

### Simplificação do cockpit

- **R-17.** `NavItem` ganha `visibleInMvp?: boolean`. O `Sidebar` renderiza apenas itens com `visibleInMvp === true`. Visíveis: **Inspetor, Cockpit Live, Constituição, Configurações** (4). As outras 13 ficam ocultas.
- **R-18.** Rotas ocultas **permanecem registradas** em `router.tsx` — acessíveis por URL direta. Nenhum componente, rota ou teste é deletado.

### Constituição

- **R-19.** Slice 100% read-only (Arts. 13/34–36, ADR-006). Nenhum endpoint deste slice envia ordem, parametriza Risk Engine ou justifica exceção.
- **R-20.** P&L exibido em qualquer posição mostrada (via `mt5.position`, se exibido) deve ser tratado como informativo bruto do terminal; este slice **não** calcula resultado operacional (Art. 25º se aplica às telas operacionais, não ao Inspetor read-only) — não exibir como "resultado" do operador.

## 4. Contratos

### 4.1 ZeroMQ (EA ↔ backend)

```
PUB mt5.tick   : { "symbol", "bid", "ask", "last", "volume", "ts_unix_ms" }        (existe)
PUB mt5.book   : { "symbol", "ts", "bids":[{"price","vol"}], "asks":[{"price","vol"}] }  (novo)
PUB mt5.heartbeat : { "ts" }                                                        (existe)

REP GET_CANDLES : req {"cmd":"GET_CANDLES","symbol","timeframe","count"}
                → rep {"status":"ok","data":{"symbol","timeframe","candles":[{"ts","o","h","l","c","v"}]}}
REP GET_SYMBOLS : req {"cmd":"GET_SYMBOLS"}
                → rep {"status":"ok","data":["PETR4","VALE3","WIN$", ...]}
REP SUBSCRIBE   : req {"cmd":"SUBSCRIBE","symbol"}    → rep {"status":"ok","data":"PETR4"}
REP UNSUBSCRIBE : req {"cmd":"UNSUBSCRIBE","symbol"}  → rep {"status":"ok","data":"PETR4"}
fora da allowlist → rep {"error":"UNAUTHORIZED_COMMAND","cmd":"..."}                 (existe)
```

`timeframe` ∈ `{M1,M5,M15,M30,H1,H4,D1,W1,MN1}` (mapeado p/ `TIMEFRAME_*` no EA).

### 4.2 API REST/WS (backend ↔ frontend) — prefixo `/api/v1`

| Método | Rota | Resposta |
|---|---|---|
| GET | `/market/symbols` | `["PETR4","VALE3","MXRF11","WIN$", ...]` |
| GET | `/market/symbol/{ticker}` | `{ ticker, mt5_symbol, name, type: "stock"\|"fii"\|"future", currency, point, tick_size }` |
| GET | `/market/candles?symbol=&timeframe=&count=` | `{ symbol, timeframe, candles:[{ time, open, high, low, close, volume }] }` |
| WS | `/ws/market/{symbol}` | stream `{ type:"tick"\|"book"\|"status", ... }` |
| GET | `/fundamentals/{ticker}` | ver 4.3 |

### 4.3 `GET /fundamentals/{ticker}`

```json
{
  "ticker": "PETR4",
  "type": "stock",
  "source": "brapi",
  "ts_snapshot": "2026-05-31T12:00:00Z",
  "indicators": {
    "dy": 0.085, "pl": 4.20, "pvp": 1.15, "roe": 0.32,
    "div_liq_ebitda": 0.95, "payout": 0.45, "roic": 0.28,
    "ev_ebitda": 3.10
  },
  "dividends_history": [
    { "date": "2026-03-15", "type": "DIVIDEND", "value": 1.20 }
  ],
  "dividend_projection": {
    "run_rate_12m":   { "annual": 4.80, "yield": 0.084, "label": "estimativa" },
    "dy_avg_3_5y":    { "annual": 4.10, "yield": 0.072, "label": "estimativa" }
  }
}
```

Para `type:"future"` → `404` ou `{ "type":"future", "indicators": null }` (frontend omite o bloco).

### 4.4 Eventos / persistência

- `cam_market_ticks` (hypertable): insert por tick com `source="mt5.cam_bridge"`, `ts_recv`.
- `cam_market_book_snapshots`: insert por evento de book (quando publicado).
- `cam_fundamentals_snapshot`: upsert idempotente por hash (já implementado no coletor).

## 5. Casos de uso / cenários

| # | Caso | Esperado |
|---|---|---|
| 1 | Buscar `PETR4` (ação) | Candles D1 < 2s; tick ao vivo; 7 indicadores; histórico + 2 estimativas de dividendo |
| 2 | Buscar `MXRF11` (FII) | Candles + tick; DY/P/VP/Payout preenchidos; P/L/ROE/ROIC = `N/A` (tooltip); dividendos mensais |
| 3 | Buscar `WIN$` (futuro) | Só candles + tick + book; **sem** bloco de fundamentos, sem erro |
| 4 | Trocar timeframe D1→M5 | Gráfico recarrega via `GET_CANDLES` com novo timeframe |
| 5 | Ativo com DOM disponível | Painel de book ao vivo renderiza níveis bid/ask |
| 6 | Ativo sem DOM | "Book não disponível para este símbolo" (discreto) |
| 7 | EA morto | Header → `WS OFFLINE`; gráfico congela com aviso "sem dado fresco" |
| 8 | Símbolo inexistente | 404 + "Símbolo não encontrado no MT5" |
| 9 | Abrir o cockpit | Sidebar mostra 4 itens; URL `/journal` ainda abre a tela (não deletada) |
| 10 | Conta MT5 real | Banner **REAL** no header durante toda a sessão |

## 6. Casos limite / exceções

- **`GET_CANDLES` grande:** backend limita `count`; estoura → 422 "intervalo excede o limite do MVP".
- **brapi rate limit / timeout:** retorna último snapshot cacheado + flag `stale: true`; se nunca houve cache, indicadores = `N/A` com aviso, **sem** derrubar a tela.
- **brapi sem o ticker:** `indicators: null`; tela mostra "fundamentos indisponíveis para este ativo".
- **EA em conta REAL com `InpRequireDemoAccount=true`:** EA não inicia → backend sem PUB → WS OFFLINE. Operador deve ajustar o input conscientemente (R-10).
- **Book parcial (só bid ou só ask):** renderiza o lado disponível.
- **Símbolo subscrito ≠ símbolo do gráfico do EA:** `SUBSCRIBE` resolve via `SymbolSelect`; tick ao vivo só flui para símbolos selecionados; candles via REP funcionam sempre.
- **`lightweight-charts` incompatível com React 19:** fallback `recharts` (verificar no BL-4).

## 7. Classificação P/M/G

| Campo | Valor |
|---|---|
| Classe | **G** (decomposta em BL-1..BL-7; BL-8 fora) |
| Rationale | Toca múltiplas funcionalidades novas em camadas distintas — EA (MQL5), backend (2 slices), frontend (tela nova), governança (ADR-014) — e introduz o primeiro caminho de market data ao vivo. Cada bloco isolado é P/M, mas o conjunto é G e exige decomposição com gate Founder. |

Blocos (do SCOPE §14): BL-1 (P), BL-2 (M), BL-3 (M), BL-4 (M), BL-5 (P), BL-6 (M), BL-7 (M).

## 8. Marcadores de segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (intrabloco no CODE) | **sim — BL-2** | Estende a allowlist do bridge e libera operação em conta REAL. Gatilho SEC-GOV CaM: toca o perímetro EA/ZeroMQ e a trava read-only da IA (Art. 35º). Kevin valida: allowlist sem comando de escrita, `grep OrderSend` vazio, banner REAL. |
| `qa-sec` (QA-SEC no QA) | **sim — BL-3, BL-6** | BL-3: parsing seguro de payload ZMQ, segregação read-only, audit. BL-6: cliente HTTP externo (brapi) — timeout, sem vazamento de token, sanitização de resposta. |

> Gatilho SEC-GOV automático (CaM): a demanda toca **autoridade da IA / perímetro do EA**. Kevin
> entra cross-cutting em BL-2 (sec) e BL-3/BL-6 (qa-sec). Ver `governance/SEC-GOV.md`.

## 9. Saídas esperadas

- EA `cam_bridge` estendido (GET_CANDLES, mt5.book, GET_SYMBOLS, SUBSCRIBE) — read-only mantido.
- `features/market_data/` funcional (subscriber + REP client + persistência + WS + endpoints).
- `features/fundamentals/` com `BrapiSource` + endpoint + 2 projeções + cache.
- `features/inspetor/` no frontend (busca + gráfico + book + fundamentos + dividendos).
- `nav.tsx`/`Sidebar.tsx` com `visibleInMvp`; 4 telas visíveis.
- `ADR-014` ratificado + linha de market data do DAS corrigida.
- Testes: contrato ZMQ, resolução de símbolo, `BrapiSource` (sem rede em CI, via fixture/mock), filtro do sidebar.

## 10. Critérios de aceite

Os 10 critérios do SCOPE §12 são a régua de QA (Linus). Go = todos verdes, com destaque para:

- **(8)** `grep -r "OrderSend"` no slice = vazio (bloqueante — Kevin).
- **(6/7/9)** Falha segura, persistência de tick e sidebar reduzido verificáveis objetivamente.
- **(10)** Banner REAL presente.
- Contratos da §4 batem com o implementado (validação de schema).

## 11. Delta no DVP (se aplicável)

Sem mudança de direção estratégica. Reforça "construir amplo, liberar estreito" e o gate de dados
(Pilar 4). Ajuste **documental**: DAS precisa refletir a recalibração de 2026-05-30 (Windows firme;
MT5 como market data) — capturado em ADR-014, fora desta SPEC de produto.

## 12. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1.0 | 2026-05-31 | Draft inicial — consolidação de 3 escopos | — (aguarda Founder) |

---

> **Gate SPEC/Founder:** Carlos aprova esta SPEC **e** o `ADR-014` antes do PLAN fechar para CODE.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

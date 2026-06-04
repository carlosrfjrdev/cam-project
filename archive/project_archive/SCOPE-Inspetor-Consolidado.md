---
template: SCOPE
phase: DISC→SPEC
status: Draft — aguarda ratificação do Founder
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
version: 2.0 (consolidado)
date: 2026-05-31
orchestrator: Leo
supersedes:
  - SCOPE-evolution2.md
  - SCOPE-Inspetor-de-Ativo.md
  - "SCOPE-Inspetor-de-Ativo (1).md"
relacionados: CONSTITUICAO.md (v1.1), DAS.md (Draft — desatualizado, ver §11), STACK-CAM-OFICIAL.md
---

# SCOPE — CaM · Inspetor de Ativo (MVP) — **Consolidado**

> **Uma frase:** uma tela onde o operador pesquisa um ativo e o CaM traz, ao vivo, o **gráfico**
> (candles históricos + tick e book do MT5) e, para papéis à vista, os **indicadores
> fundamentalistas (7 do R-20)** e **dois cenários de dividendo** (via brapi.dev) —
> tudo **read-only**, sem nenhuma superfície de execução.

Este documento **consolida e revoga** três escopos que descreviam o mesmo objetivo:

| Escopo de origem | Autor | O que trouxe de melhor | O que foi descartado |
|---|---|---|---|
| `SCOPE-evolution2.md` | Leo (sessão interna) | Tabela de **ocultação das 17 telas**; cadência em blocos pequenos | Conexão via `MetaTrader5` (Python lib) — **superada** pelo estado real do código |
| `SCOPE-Inspetor-de-Ativo.md` | Mentoria CaM (externo) | Arquitetura **EA + ZeroMQ**; contratos de dados; ADR-014; critérios de aceite | — (base arquitetural adotada) |
| `SCOPE-Inspetor-de-Ativo (1).md` | Mentoria CaM (externo) | Tudo do anterior **+ overlay de Regime de Markov** (read-only) | Markov movido para **LATER** (BL-8) — fora do núcleo do MVP |

**Princípio de consolidação aplicado:** *estado real vence intenção* (NCC-1701 §2, regra 7).
Onde os escopos divergiam, o código já materializado no repositório decidiu.

---

## 1. Por que existir (re-escopo)

O cockpit cresceu para **17 destinos de menu** antes de ter **um único fluxo ponta-a-ponta
funcionando**. Carlos abre o cockpit e enfrenta um menu que promete mais do que o sistema
entrega na Fase 0. A insatisfação é legítima: faltou um slice vertical que prove o caminho.

Este MVP corta para **uma tela que funciona**: busca → gráfico + fundamentos. Reafirma o
princípio **"construir amplo, liberar estreito"**: todo o resto continua no código, atrás de
flag, fora do menu. É também o **primeiro slice vertical que prova o caminho de dados do MT5
ponta-a-ponta** — pré-requisito implícito de tudo que vem depois (paper loop, backtest com dado
real, pattern lab).

---

## 2. Estratégia de simplificação (Ocultar + Revelar)

### 2.1 Classificação das 17 telas (estado real do `nav.tsx`)

O arquivo `apps/cam-cockpit/frontend/src/_shared/nav.tsx` hoje lista **16 itens** em 5 grupos
(Operação, Estratégia, Registro, Patrimônio, Sistema). O Inspetor é o **17º** (novo).

| Tela | Path | Grupo atual | Decisão MVP |
|---|---|---|---|
| **Inspetor de Ativo** (nova) | `/inspetor` | Pesquisa | **VISÍVEL-MVP** — tela principal desta demanda |
| Cockpit Live | `/` | Operação | **VISÍVEL-MVP** — dashboard raiz |
| Constituição | `/constitution` | Sistema | **VISÍVEL-MVP** — referência sempre acessível |
| Configurações | `/settings` | Sistema | **VISÍVEL-MVP** — config básica (token brapi, porta ZMQ) |
| Order Gateway | `/order-gateway` | Operação | OCULTAR — sem trade ativo |
| Risk Console | `/risk` | Operação | OCULTAR — Risk Engine sem dados |
| EA Control | `/ea-control` | Operação | OCULTAR — control plane fora do MVP |
| Strategy Registry | `/strategies` | Estratégia | OCULTAR — sem estratégia registrada |
| Robot Orchestrator | `/robots` | Estratégia | OCULTAR — sem robô ativo |
| Escalonamento | `/scaling` | Estratégia | OCULTAR — pré-req BL-H não entregue |
| Market Data | `/market-data` | Estratégia | OCULTAR — **funções migram para o Inspetor** (ver §10) |
| Journal | `/journal` | Registro | OCULTAR — sem trade ativo |
| Ledger Fiscal | `/fiscal` | Registro | OCULTAR — sem DARF |
| Harvest | `/harvest` | Registro | OCULTAR — sem aporte em andamento |
| Carteira Hard | `/carteira-hard` | Patrimônio | OCULTAR — sem holdings registradas |
| Research | `/research` | Patrimônio | OCULTAR — DuckDB research fora do MVP |
| Backtest | `/backtest` | Patrimônio | OCULTAR — sem dado real ainda |
| Paper Trading | `/paper-trading` | Patrimônio | OCULTAR — sem loop governado ativo |

**Resultado:** 4 itens visíveis no sidebar (Inspetor, Cockpit, Constituição, Configurações).

### 2.2 Mecanismo de ocultação

- Adicionar campo opcional `visibleInMvp?: boolean` a cada `NavItem` em `nav.tsx`.
- `Sidebar.tsx` filtra `NAV_ITEMS.filter(i => i.visibleInMvp)`.
- **Rotas permanecem registradas** em `router.tsx` — navegação direta por URL continua
  funcionando. Ocultar = sumir do menu, **nunca** deletar componente, rota ou teste.
- Revelar = marcar `visibleInMvp: true` quando o pré-requisito da tela for cumprido.

> Constituição: nenhum guardrail tocado. Ocultar telas não-operacionais **aumenta** a defesa
> de capital ao reduzir superfície de ação acidental (espírito do Art. 6º).

---

## 3. Decisões travadas (consolidadas)

| # | Decisão | Detalhe | Origem |
|---|---|---|---|
| **D1** | Fonte de market data: **MT5** | Conta **REAL**, Windows, **read-only**. Requer `ADR-014` (§11). | externo + Founder |
| **D2** | Canal MT5↔backend: **EA `cam_bridge` + ZeroMQ** | **Já existe no repo** (`mql5/experts/cam_bridge.mq5` v0.3 + `include/cam_zmq.mqh`). O pacote Python `MetaTrader5` **não** entra no caminho operacional. | **estado real do código** |
| **D3** | Histórico de candle: **REP `GET_CANDLES`** | Via `CopyRates` no EA. **Comando novo** a adicionar (hoje o EA não tem). Sem tick histórico massivo no MVP. | externo |
| **D4** | Tick ao vivo: **PUB `mt5.tick`** | **Já publicado** pelo EA. Persistido em `cam_market_ticks` → semeia corpus preditivo. | estado real |
| **D5** | Book ao vivo: **PUB `mt5.book`** | **Comando/canal novo** — `MarketBookAdd` + `OnBookEvent` no EA (hoje não existe). Condicional ao ativo. | externo (gap real) |
| **D6** | Lista de símbolos: **`GET_SYMBOLS` / `SUBSCRIBE`** | EA expõe símbolos disponíveis e passa a observar o pesquisado (`SymbolSelect`). **Comandos novos**, allowlistados. | gap real |
| **D7** | Fundamentos/dividendos: **brapi.dev** | Primário, free tier. Nova `BrapiSource` implementando o Protocol `FundamentalsSource` **já existente**. | meu + externo |
| **D8** | Scraping (Fundamentus/StatusInvest): **LATER** | Fallback governado → **TD-v0.4-01** (User-Agent, rate limit, cache, ToS). Fora do núcleo do MVP. | reconciliação |
| **D9** | Projeção de dividendo: **2 modelos lado a lado** | Run-rate 12m **e** DY-médio 3–5 anos × preço. Ambos rotulados **"estimativa"**. | externo |
| **D10** | Indicadores: **7 do R-20** | DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC — **campos já no schema** `cam_fundamentals_snapshot`. EV/EBITDA exibido como **bônus** se a brapi retornar. | estado real + R-20 |
| **D11** | EA read-only **por construção** | Zero `OrderSend`/`PositionOpen` no arquivo (CA15.1 já vigente). Canal de comando **allowlistado**. | estado real |
| **D12** | Universo | Ações/FIIs à vista: gráfico + fundamentos. Futuros (WIN/WDO): **só gráfico**, sem bloco de fundamentos, sem erro. | externo + Founder |
| **D13** | Regime de Markov: **IN (núcleo)** | Overlay analítico **read-only** no Inspetor — **decisão do Founder (2026-05-31): é núcleo do MVP**, não LATER. Bloco "assistente de pesquisa" (Art. 13/34–36, ADR-006). Funções puras vendorizadas, alimentadas pelos candles do CaM (não yfinance). | externo (1) + Founder |

---

## 4. Arquitetura do slice — os dois canos

```
Cano de preço (read-only):
  MT5 (conta REAL) → EA cam_bridge  [read-only, sem OrderSend]
        → ZeroMQ  PUB: mt5.tick, mt5.book, mt5.heartbeat
                  REP: GET_CANDLES, GET_SYMBOLS, SUBSCRIBE, GET_SYMBOL_INFO
        → backend features/market_data  (subscriber + REP client)
        → TimescaleDB (cam_market_ticks → cam_candles_*)  +  WebSocket interno
        → frontend Inspetor (gráfico ao vivo)

Cano de fundamento:
  brapi.dev → backend features/fundamentals (BrapiSource + cache TTL)
        → HTTP → frontend Inspetor (7 indicadores + dividendos + 2 estimativas)

Os dois canos cruzam APENAS pelo ticker. features/market_data e features/fundamentals
são slices auto-contidos (ADR-013) — um nunca importa o outro.
```

### 4.1 O que já existe vs. o que falta construir

| Componente | Estado real hoje | Falta para o Inspetor |
|---|---|---|
| `mql5/experts/cam_bridge.mq5` | **v0.3** — PUB tick/heartbeat/position; REP PING/GET_STATE/GET_POSITIONS/GET_SYMBOL_INFO/PAUSE/RESUME/GET_VERSION; **read-only; aborta em conta REAL** | **+ `GET_CANDLES`** (CopyRates), **+ `mt5.book`** (MarketBookAdd/OnBookEvent), **+ `GET_SYMBOLS`/`SUBSCRIBE`**; permitir conta REAL read-only (§9) |
| `mql5/include/cam_zmq.mqh` | existe | revisar buffer p/ payload de candles maior |
| `backend/.../market_data/service.py` | **stub vazio** ("TODO") | subscriber ZMQ + REP client + persistência + WS |
| `backend/.../market_data/{provenance,instruments_loader,csv_parser,repository,schemas,domain}.py` | construídos (orientados a import CSV) | reaproveitar provenance/instruments; **não** depende do CSV path |
| `backend/.../fundamentals/multi_source_collector.py` | **Protocol `FundamentalsSource` + `PlaceholderSource` + persistência `cam_fundamentals_snapshot` com os 7 R-20** | **+ `BrapiSource`** (nova fonte) + projeções de dividendo + endpoint |
| `cam_market_ticks` / `cam_candles_*` (TimescaleDB) | **previstos no DAS / migrations** | confirmar continuous aggregates ativos |
| Frontend `features/market-data/`, `features/research/` | telas existem | nova `features/inspetor/` (reaproveita o que servir) |

> **Passo zero do CODE:** verificar o estado exato de cada item acima antes de escrever —
> não assumir nada pronto nem nada vazio.

---

## 5. Componentes a construir / estender

**EA `cam_bridge.mq5` (extensão read-only — NÃO criar EA novo)**
- `GET_CANDLES(symbol, timeframe, count)` via `CopyRates` → REP com array OHLCV.
- Canal `mt5.book`: `MarketBookAdd(symbol)` + `OnBookEvent` → PUB de níveis bid/ask.
- `GET_SYMBOLS` → lista de símbolos disponíveis (`SymbolsTotal`/`SymbolName`).
- `SUBSCRIBE(symbol)` / `UNSUBSCRIBE(symbol)` → `SymbolSelect` + watch; allowlist estendida.
- **Nenhuma chamada de ordem.** Allowlist rejeita e loga qualquer comando fora dela (CA15.3).

**Backend `features/market_data/` (preencher o stub)**
- Subscriber ZeroMQ: consome `mt5.tick`/`mt5.book`, normaliza, persiste em `cam_market_ticks`
  (+ snapshots de book), publica no WS interno.
- Cliente REP: `GET_CANDLES`, `GET_SYMBOLS`, `SUBSCRIBE`.
- Endpoints: `GET /market/symbols`, `GET /market/symbol/{ticker}`, `GET /market/candles`,
  `WS /ws/market/{symbol}`, canal interno `subscribe/unsubscribe` (allowlist).
- Camada de **resolução de símbolo** (ticker B3 ↔ símbolo MT5, sufixos, `WIN$`/`WINM25`).

**Backend `features/fundamentals/` (estender o coletor existente)**
- `BrapiSource(FundamentalsSource)`: token via `keyring`/`.env`; tickers free sem token no MVP.
- Endpoint `GET /fundamentals/{ticker}` → 7 indicadores + histórico de proventos + **2 projeções**.
- Cache com TTL alinhado à atualização da brapi.

**Frontend `features/inspetor/`**
- Campo de busca por ticker (autocomplete via `GET /market/symbols`).
- Gráfico de candles com stream ao vivo (`lightweight-charts`).
- Seletor de timeframe (M1…MN1; default H1).
- Painel de book ao vivo (condicional ao ativo).
- Bloco de fundamentos (7 cards R-20; só Ação/FII).
- Bloco de dividendos: histórico + 2 estimativas rotuladas.
- Indicador `WS ONLINE/OFFLINE` no header (já existe no header atual).

---

## 6. Contratos de dados (rascunho — SPEC formaliza)

**ZeroMQ**
- Tick (PUB `mt5.tick`): `{ symbol, bid, ask, last, volume, ts_unix_ms }` *(já publicado)*
- Book (PUB `mt5.book`, **novo**): `{ symbol, ts, bids:[{price,vol}], asks:[{price,vol}] }`
- Candles (REP, **novo**): `req {cmd:"GET_CANDLES", symbol, timeframe, count}` →
  `rep {status:"ok", data:{symbol, timeframe, candles:[{ts,o,h,l,c,v}]}}`
- Símbolos (REP, **novo**): `req {cmd:"GET_SYMBOLS"}` → `rep {status:"ok", data:[...tickers]}`
- Assinatura (REP, **novo**): `req {cmd:"SUBSCRIBE"|"UNSUBSCRIBE", symbol}` → `rep {status:"ok", data:symbol}`
- **Allowlist** (CA15.3): apenas `PING, GET_STATE, GET_POSITIONS, GET_SYMBOL_INFO, GET_VERSION,
  PAUSE_EA, RESUME_EA, GET_CANDLES, GET_SYMBOLS, SUBSCRIBE, UNSUBSCRIBE`. Qualquer outro → rejeitado + logado.

**WebSocket (frontend):** `{ type:"tick"|"book"|"status", ... }`

**brapi:** `GET /api/quote/{ticker}?modules=defaultKeyStatistics,financialData&dividends=true&fundamental=true`

---

## 7. Persistência & corpus preditivo

`cam_market_ticks` (hypertable) recebe todo tick ao vivo → *continuous aggregate* gera
`cam_candles_*`. O Inspetor, **só por estar ligado, acumula base de tick com proveniência limpa**
(um canal só). A trilha preditiva (slice futuro, inclui o Markov de BL-8) consome essa base.
**Nenhum tick histórico massivo vai para a tela.**

---

## 8. Features IN / OUT / LATER

**IN (núcleo do MVP):**
- Ocultação das 13 telas; rota + tela `Inspetor`.
- EA estendido: `GET_CANDLES`, `mt5.book`, `GET_SYMBOLS`, `SUBSCRIBE`.
- Gráfico de candles (histórico via REP + atualização ao vivo via tick PUB).
- Tabela/painel de ticks recentes; book condicional.
- 7 indicadores R-20 + histórico de dividendos + 2 estimativas (brapi).
- Resolução de símbolo (Ação/FII/futuro); futuros sem bloco de fundamentos.
- **Overlay de Regime de Markov (read-only)** — ver §13 (BL-8). Estado atual, matriz de
  transição, mix de longo prazo, sinal e Sharpe/maxDD walk-forward, todos rotulados
  "histórico, não preditivo".

**OUT (não fazer):**
- Qualquer envio de ordem / rota de execução. Zero `OrderSend`.
- Risk Engine, Order Gateway, EA Control, Strategy Registry, Robot Orchestrator,
  Escalonamento, Paper, Backtest, Journal, Fiscal, Harvest, Carteira Hard — dormem atrás de flag.
- Tick histórico massivo **na tela**; book histórico (MT5 não guarda).
- Backfill anterior à captura (ETL offline, futuro).
- Profit / NTSL / ProfitDLL (execução).
- Scraping de fundamentos (vai para TD-v0.4-01 → LATER).
- Autenticação (cockpit local mono-usuário).
- Markov como **gate de entrada ou sizing** (papéis B/C — Parte VII, futuro).

**LATER (próximos blocos, gate próprio):**
- Markov como **gate de entrada ou sizing** (papéis B/C — Parte VII); o overlay de leitura (papel A)
  é **IN** (núcleo, BL-8). Só a autoridade de execução fica LATER.
- Scraping governado de fundamentos (TD-v0.4-01).
- Streaming de candles via WS dedicado; alertas de preço.
- Reexibição progressiva das telas ocultadas conforme pré-requisitos.

---

## 9. Guardrails constitucionais (não-negociáveis)

- **Arts. 13 / 34–36 + ADR-006:** slice read-only; o Inspetor é "assistente de pesquisa".
  Nenhum endpoint de execução.
- **EA sem código de ordem:** impossibilidade **estrutural**, não flag (CA15.1 já vigente).
- **Canal de comando allowlistado** (CA15.3).
- **Falha segura:** falha técnica degrada para "WS OFFLINE / sem dado fresco", **nunca** para
  falsa sensação de "liberado". Sem execução, o pior caso é tela sem dado.
- **Conta REAL — atenção SEC-GOV (Kevin):** o EA hoje **aborta em conta REAL**
  (`InpRequireDemoAccount=true`, `OnInit`). Para o Inspetor operar na conta real de Carlos, o
  operador deve **conscientemente** setar `InpRequireDemoAccount=false`. Como o bridge é read-only
  por construção (sem `OrderSend`), ler dado de conta real é seguro — **mas exige**: (a) banner
  **REAL** permanente no header; (b) confirmação de que nenhum comando de escrita existe na
  allowlist; (c) registro em audit log. Kevin valida no `sec` do BL-3.
- **Credenciais** (token brapi) nunca commitadas; `keyring`/`.env`.

---

## 10. Relação com telas existentes

- **`MarketDataPage` (`/market-data`)** e **`ResearchPage` (`/research`)**: ficam **ocultas**.
  As funções úteis (visualização de candles, exploração de ativo) **migram para o Inspetor**.
  Não deletar — podem ser reativadas com função distinta (ex.: import CSV histórico, research DuckDB)
  quando houver demanda.

---

## 11. Governança requerida (gate antes do CODE)

**`ADR-014` — MT5 como fonte de market data read-only no Inspetor.**
- Registra MT5 (via EA+ZeroMQ) como fonte oficial de dado de mercado read-only.
- **Atualiza o DAS**, que está desatualizado: o DAS (2026-05-24) §9 lista "MT5 como fallback —
  out-of-scope" e §2 lista "Profit como plataforma de execução"; ADR-001/008/012 ainda dizem
  Profit + dev-Linux. A recalibração de 2026-05-30 (Windows firme, MT5 em teste / Profit standby)
  **ainda não foi refletida no DAS** — ADR-014 deve, no mínimo, corrigir a linha de market data.
- Registra que a decisão é sobre **dados**, não **execução** (a escolha de broker de execução
  segue aberta — OP-014/OP-015).
- **Sem `ADR-014` ratificado, o slice não promove além de Draft.**

---

## 12. Critérios de aceite (MVP "pronto")

1. Digito `PETR4` → vejo candles diários (histórico via EA `GET_CANDLES`) em < 2s.
2. O gráfico atualiza ao vivo (tick PUB) sem reload; book ao vivo visível quando disponível.
3. Vejo os 7 indicadores R-20 do papel (brapi): DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC.
4. Vejo histórico de proventos + **duas** estimativas de dividendo, ambas rotuladas "estimativa".
5. Digito um futuro (ex.: `WIN$`/`WINM25`) → vejo só o gráfico, **sem** bloco de fundamentos, sem erro.
6. Mato o EA → header vai a `WS OFFLINE`; a tela **não mente** sobre dado fresco.
7. Tick ao vivo aparece em `cam_market_ticks` (verificável no banco).
8. **Nenhuma rota de execução existe no slice** (`grep -r OrderSend` no slice = vazio).
9. Sidebar exibe **apenas 4** itens (Inspetor, Cockpit, Constituição, Configurações); as demais
   rotas continuam acessíveis por URL direta (não deletadas).
10. Header exibe banner **REAL** enquanto a conta MT5 for real.
11. Para uma **ação**, vejo o bloco de **Regime**: estado atual (Bull/Bear/Sideways), matriz de
    transição 3×3, mix de longo prazo (distribuição estacionária), sinal ∈ [−1,1] e Sharpe/maxDD
    walk-forward — **todos rotulados "histórico, não preditivo"**.

---

## 13. BL-8: Overlay de Regime de Markov (read-only) — **NÚCLEO (IN)**

> **Decisão do Founder (2026-05-31): é núcleo do MVP**, no mesmo gate dos blocos BL-1..BL-7.
> Continua sendo um overlay **read-only** ("assistente de pesquisa", papel A) — informação, nunca
> ordem. O que fica fora são os papéis B (confirmar entrada) e C (sizing), que tocam execução.

**Origem.** Framework de Roan (@RohOnChain), refatorado por Lewis Jackson (`markov_regime.py`).
Rotula cada dia Bull/Bear/Sideways pelo retorno acumulado de N dias (default 20) vs ±limiar
(default 5%), monta matriz de transição 3×3 (MLE), resolve distribuição estacionária e roda
backtest walk-forward sem lookahead (Sharpe + maxDD). Sinal = P(Bull) − P(Bear) ∈ [−1,1].

**Papel no CaM (só "A").** Bloco analítico **read-only** no Inspetor — "assistente de pesquisa"
(Art. 13/34–36, ADR-006). Mostra informação, **nunca** emite ordem. Confirmação de entrada (B) e
sizing pela estacionária (C) tocam execução/contratos e ficam **fora**, gated pela Parte VII.

**Integração.** `features/regime/` lê `cam_candles_*` (não importa `market_data`), vendoriza só as
funções puras (com atribuição), **descarta o caminho yfinance** (alimenta com close dos candles do
CaM). HMM degrada com elegância se não compilar no Windows.

**Caveats honestos (no rótulo).** Rótulo é tendência defasada; janelas sobrepostas autocorrelacionam
→ persistência é em parte artefato. Backtest não modela custo/spread → Sharpe bruto. Regime diário
é filtro macro grosseiro; para S1 (ORB 60m WIN) é contexto, não sinal.

**Procedência (Kevin / SEC-GOV).** O arquivo `markov-hedge-fund-method.md` é um prompt
auto-instalador com marketing embutido. **Não rodar o instalador** — aproveitar só a matemática,
com atribuição, sob governança do CaM.

---

## 14. Sequência de execução (blocos — sem estimativa de tempo)

| Bloco | Entregável | P/M/G | sec/qa-sec | Pré-requisito |
|---|---|---|---|---|
| **BL-1** | Ocultar 13 telas no sidebar (`visibleInMvp`) + rota `/inspetor` vazia | P | — | — |
| **BL-0/ADR** | `ADR-014` + correção do DAS (market data) | — | governança | Founder ratifica |
| **BL-2** | EA `cam_bridge`: `GET_CANDLES` + `mt5.book` + `GET_SYMBOLS`/`SUBSCRIBE` + allowlist + permitir REAL read-only | M | **sec crítico** | ADR-014 |
| **BL-3** | Backend `market_data`: subscriber + REP client + persistência + WS + endpoints + resolução de símbolo | M | qa-sec | BL-2 |
| **BL-4** | Frontend Inspetor: busca + `lightweight-charts` + timeframe + WS status | M | — | BL-3 |
| **BL-5** | Book ao vivo na tela (condicional) | P | — | BL-3 |
| **BL-6** | Backend `fundamentals`: `BrapiSource` + endpoint + 2 projeções + cache | M | qa-sec | — (paralelo a BL-2/3) |
| **BL-7** | Frontend: painel 7 indicadores + dividendos + 2 estimativas | M | — | BL-4 + BL-6 |
| **BL-8** | Backend `features/regime/` (funções puras Markov) + endpoint `GET /regime/{symbol}` + bloco de Regime no frontend (read-only) | M | qa-sec | BL-3 (candles em `cam_candles_*`) + BL-4 (tela) |

**Paralelismo:** BL-1 e BL-6 correm em paralelo a BL-2/BL-3. BL-7 depende de BL-4 + BL-6.
BL-8 depende de candles persistidos (BL-3) e da tela (BL-4).
**Gate Founder único** ao final do núcleo (BL-1..BL-8).

---

## 15. Riscos & mitigação

| Risco | Mitigação |
|---|---|
| Qualidade de book/tick varia por corretora | Validar com o ativo real cedo, já no BL-2/BL-3. |
| **EA aborta em conta REAL** | `InpRequireDemoAccount=false` consciente + banner REAL + validação Kevin (§9). |
| EA single-thread: `GET_CANDLES` grande segura heartbeat | Limitar `count`/timeframe no MVP (ex.: ≤ 1 ano em M5); tick histórico fica fora. |
| Símbolo MT5 ≠ ticker B3 (sufixos, `WIN$`) | Camada de resolução de símbolo no `market_data`. |
| brapi free tier limita tickers/atualização | Cache TTL; subir de plano só com valor provado. |
| `lightweight-charts` × React 19 | Verificar versão compatível antes de instalar; fallback `recharts`. |
| EA só PUB-a o símbolo do gráfico atual | `SUBSCRIBE` faz `SymbolSelect`; candles via `GET_CANDLES` funcionam p/ qualquer símbolo. |

---

## 16. Handoff (ordem DevFlow)

1. Founder ratifica este SCOPE consolidado.
2. Oscar/Kevin: `ADR-014` + correção do DAS (ARCH).
3. Albert: **SPEC** detalhado (ver `../specs/SPEC-Inspetor-de-Ativo.md`).
4. Nico: PLAN proporcional dos blocos BL-1..BL-7.
5. Nikola (+Linus intrabloco, +Kevin no `sec` do BL-2): CODE.
6. Linus: QA contra os critérios §12.

---

> **Gate de aprovação SCOPE/Founder:** Carlos ratifica este consolidado **e** o `ADR-014` antes
> do detalhamento fechar para CODE.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

---
template: SCOPE
phase: SPEC
status: Draft — aguarda ratificação do Founder
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
data: 2026-05-31
autor: Mentoria CaM (PO/Mentor) — para execução via ClaudeCode
relacionados: CONSTITUICAO.md (v1.1), DAS.md (Draft, não ratificado), STACK-CAM-OFICIAL.md
superseded_by: SCOPE-Inspetor-Consolidado.md
---

> ⚠️ **SUPERSEDED (2026-05-31):** consolidado em
> [`SCOPE-Inspetor-Consolidado.md`](./SCOPE-Inspetor-Consolidado.md). O overlay de Regime de Markov
> (§14) é **BL-8, núcleo do MVP** no consolidado (decisão do Founder 2026-05-31) — overlay
> read-only no mesmo gate dos demais blocos. Mantido como histórico.

# SCOPE — CaM · Inspetor de Ativo (MVP)

## 1. Objetivo (uma frase)

Uma tela onde o operador pesquisa um ativo e o CaM traz, ao vivo, o **gráfico** (candles + tick e book do MT5) e, para papéis à vista, os **indicadores fundamentalistas** e **dois cenários de dividendo** (via brapi.dev) — tudo **read-only**, sem nenhuma superfície de execução.

## 2. Por que existir (re-escopo)

O cockpit cresceu para ~17 destinos de menu antes de ter um único fluxo ponta-a-ponta funcionando. Este MVP corta para **uma tela que funciona**: busca → gráfico + indicadores. Reafirma o princípio "construir amplo, liberar estreito": todo o resto continua no código, atrás de flag, fora do menu. É também o **primeiro slice vertical que prova o caminho de dados do MT5 ponta-a-ponta**.

## 3. Fora de escopo (explícito — não fazer)

- Qualquer envio de ordem; qualquer rota de execução. Zero `OrderSend`.
- Risk Engine, Order Gateway, EA Control, Strategy Registry, Robot Orchestrator, Escalonamento, Paper Trading, Backtest, Journal, Ledger Fiscal, Harvest, Carteira Hard — dormem atrás de flag, fora do menu.
- Tick histórico massivo **na tela** (é a trilha preditiva — slice próprio, futuro).
- Book histórico (o MT5 não guarda; gravação é concern futuro).
- Backfill do passado anterior à captura (ETL offline isolado, futuro).
- Profit / NTSL / ProfitDLL (execução, fora do MVP).
- Autenticação (cockpit local mono-usuário — já decidido no DAS).
- Regime de Markov como **gate de entrada ou sizing** (papéis B/C) — trilha futura, gated pela Parte VII (ver §14).

## 4. Decisões travadas (ratificadas nesta sessão)

| # | Decisão | Detalhe |
|---|---|---|
| D1 | **Fonte de market data: MT5** | Conta real, Windows, **read-only**. Requer `ADR-014` (ver §10). |
| D2 | **Canal MT5↔backend: EA + ZeroMQ** | Cross-platform (honra dev-Linux/prod-Windows, ADR-012). O pacote `MetaTrader5` (Python, Windows-only) **não** entra no caminho operacional. |
| D3 | **Histórico de candle: via REP do EA** | Opção C. **Sem tick histórico** no MVP. |
| D4 | **Tick/book ao vivo: via PUB do EA** | Persistidos em `cam_market_ticks` → semeia o corpus preditivo e alimenta candles por *continuous aggregate*. |
| D5 | **Fundamentos/dividendos: brapi.dev** | Free tier no MVP. **Sem scraping.** |
| D6 | **Projeção de dividendo: 2 modelos lado a lado** | Run-rate 12m **e** DY-médio 3–5 anos × preço. Ambos rotulados "estimativa". |
| D7 | **EA read-only por construção** | Sem `OrderSend`/`PositionOpen` no código. Canal de comando **allowlistado** a `SUBSCRIBE`/`UNSUBSCRIBE`. |
| D8 | **Universo** | Ações/FIIs à vista: gráfico + fundamentos. Futuros (WIN/WDO): só gráfico. |
| D9 | **Regime de Markov: overlay read-only** | Bloco analítico no inspetor (papel constitucional de "assistente de pesquisa"). Sem autoridade de execução. Confirmação/sizing ficam fora (§14). Alimentado por candles do CaM (Timescale), **não** yfinance. |

## 5. Os dois canos (arquitetura do slice)

```
Cano de preço:
  MT5 (real) → EA cam_bridge (read-only)
            → ZeroMQ  [ PUB: tick + book ] [ REP: GET_CANDLES ]
            → backend features/market_data
            → TimescaleDB (cam_market_ticks → cam_candles_*)  +  WebSocket
            → frontend (gráfico ao vivo)

Cano de fundamento:
  brapi.dev → backend features/fundamentals (cache)
           → HTTP → frontend (indicadores + dividendos)

Cruzam apenas pelo ticker.
```

Encaixe no DAS (ADR-013, Vertical Slice + Shared Kernel): `features/market_data/` e `features/fundamentals/` são slices **auto-contidos** — um nunca importa o outro. A composição é feita pela API e pelo frontend.

## 6. Componentes a construir / verificar

> **Passo zero do ClaudeCode:** verificar o que já existe no repo (`features/market_data`, qualquer EA, qualquer ZeroMQ). O DAS autoritativo **não** define bridge EA/ZeroMQ — este slice o **introduz**. Não assumir nada pronto.

**EA `cam_bridge.mq5` (MQL5) — read-only**
- Subscreve o símbolo sob comando (`SymbolSelect` + `MarketBookAdd`).
- PUB de tick (INFO + TRADE) e de book (`OnBookEvent`).
- REP responde `GET_CANDLES(symbol, timeframe, from, to)` via `CopyRates`.
- **Nenhuma chamada de ordem existe no arquivo.**

**Backend `features/market_data/`**
- Subscriber ZeroMQ: consome PUB, normaliza, persiste em `cam_market_ticks` (+ snapshots de book), publica no WS interno.
- Cliente REP para histórico de candle.
- Endpoints: `GET /market/symbol/{ticker}` (resolve/valida no MT5), `GET /market/candles`, `WS /ws/market/{symbol}`, e o canal interno `subscribe/unsubscribe` (allowlist).

**Backend `features/fundamentals/`**
- Cliente brapi (token via `keyring`/`.env`; free tickers sem token no MVP).
- `GET /fundamentals/{ticker}` → indicadores + histórico de proventos + 2 projeções.
- Cache com TTL alinhado à atualização da brapi.

**Backend `features/regime/`** (overlay read-only — ver §14)
- Lê `cam_candles_*` (não importa `market_data`), computa o modelo de Markov, devolve o dict `analyze()`.
- `GET /regime/{symbol}?timeframe&window&threshold`.
- Matemática vendorizada (funções puras + HMM opcional), **sem** o caminho yfinance.

**Frontend (feature do inspetor)**
- Campo de busca por ticker (autocomplete simples).
- Gráfico de candles com stream ao vivo (ex.: lightweight-charts).
- Painel de book ao vivo (dado já chega; exibição opcional no MVP).
- Bloco de fundamentos (P/L, P/VP, DY, ROE, EV/EBITDA…).
- Bloco de dividendos: histórico + 2 estimativas rotuladas.
- Indicador `WS OFFLINE/ONLINE` (já existe no header).

## 7. Contratos de dados (rascunho — ClaudeCode formaliza no SPEC)

**ZeroMQ**
- Tick: `{ symbol, ts, bid, ask, last, volume, flags }`
- Book: `{ symbol, ts, bids:[{price,vol}], asks:[{price,vol}] }`
- Histórico (REQ/REP): `req { cmd:"GET_CANDLES", symbol, timeframe, from, to }` → `rep { symbol, timeframe, candles:[{ts,o,h,l,c,v}] }`
- Comando (REQ/REP): `req { cmd:"SUBSCRIBE"|"UNSUBSCRIBE", symbol }` → `rep { ok, symbol }`
- **Allowlist:** apenas `SUBSCRIBE`, `UNSUBSCRIBE`, `GET_CANDLES`. Qualquer outro comando → rejeitado e logado.

**WebSocket (frontend):** `{ type:"tick"|"book"|"status", ... }`

**brapi:** `GET /api/quote/{ticker}?modules=defaultKeyStatistics,financialData&dividends=true&fundamental=true`

## 8. Persistência & corpus preditivo

`cam_market_ticks` (hypertable, **já prevista no DAS**) recebe todo tick ao vivo → *continuous aggregate* gera `cam_candles_15m/1h/1d`. O inspetor, só por estar ligado, **acumula a base de tick com proveniência limpa** (um canal só). A trilha preditiva (slice futuro) consome essa base. Nenhum tick histórico vai para a tela.

## 9. Guardrails constitucionais (não-negociáveis)

- **Arts. 13 / 34–36 + ADR-006:** este slice é read-only; o inspetor é "assistente de pesquisa" — papel constitucional da IA. Nenhum endpoint de execução.
- **Falha segura (DAS §7):** falha técnica degrada para "sem dado fresco / WS OFFLINE", nunca para falsa sensação de "liberado". Sem execução, o pior caso é tela sem dado.
- **EA sem código de ordem:** impossibilidade **estrutural**, não flag.
- **Canal de comando allowlistado** (§7).
- **Credenciais** (token brapi) nunca commitadas; `keyring`/`.env`.
- **Ambiente:** header marca DEMO/REAL. Como é read-only, REAL é seguro.

## 10. ADR requerido (gate de governança)

**`ADR-014` — MT5 como fonte de market data read-only no inspetor.**
- Atualiza a linha "MT5 como fallback — out-of-scope" no DAS §9 (Não-Decisões).
- Registra que **ADR-001 (Profit como plataforma de execução) permanece intacto** — esta decisão é sobre *dados*, não *execução*.
- Sem o `ADR-014` ratificado pelo Founder, o slice não promove além de Draft.

## 11. Critérios de aceite (MVP "pronto")

1. Digito `PETR4` → vejo candles diários (histórico via EA REP) em < 2s.
2. O gráfico atualiza ao vivo (tick) sem reload; book ao vivo visível.
3. Vejo P/L, P/VP, DY, ROE, EV/EBITDA do papel (brapi).
4. Vejo histórico de proventos + **duas** estimativas de dividendo rotuladas "estimativa".
5. Digito um futuro (ex.: `WIN$`) → vejo só o gráfico, sem bloco de fundamentos, sem erro.
6. Mato o EA → header vai a `WS OFFLINE`; a tela não mente sobre dado fresco.
7. Tick ao vivo aparece em `cam_market_ticks` (verificável no banco).
8. Nenhuma rota de execução existe no slice (`grep OrderSend` = vazio).
9. Para uma ação, vejo o bloco de **Regime**: estado atual, matriz de transição, mix de longo prazo, sinal e Sharpe/maxDD walk-forward — todos rotulados "histórico, não preditivo".

## 12. Riscos & mitigação

| Risco | Mitigação |
|---|---|
| Qualidade de book/tick varia por corretora | Validar com o ativo real cedo, no primeiro teste. |
| brapi free tier limita tickers/atualização | OK para prova; subir de plano só com valor provado. |
| EA single-thread: `GET_CANDLES` grande segura o heartbeat | Limitar range/timeframe no MVP (ex.: máx. 1 ano em M5); tick histórico fica fora (D3). |
| Símbolo MT5 ≠ ticker B3 (sufixos, `WIN$N`) | Camada de resolução de símbolo no `features/market_data`. |

## 13. Handoff ClaudeCode (ordem sugerida — DevFlow)

1. Ratificar `ADR-014` + atualizar DAS §9 (Oscar/Albert).
2. SPEC detalhado do slice a partir deste SCOPE (Albert).
3. Verificar repo: o que existe de EA / ZeroMQ / `market_data`? (Tom/Nikola)
4. EA `cam_bridge` read-only (PUB tick/book + REP candles + comando allowlist).
5. Backend `market_data` (subscriber + REP client + endpoints + WS + persistência).
6. Backend `fundamentals` (brapi client + cache + endpoint + 2 projeções).
7. Frontend do inspetor (busca + gráfico + blocos).
8. QA contra os critérios de aceite §11 (Linus).

---

## 14. Adendo — Overlay de Regime de Markov (read-only)

**Origem.** Framework de Roan (@RohOnChain), refatorado por Lewis Jackson (`markov_regime.py`). Rotula cada dia Bull/Bear/Sideways pelo retorno acumulado de N dias (default 20) vs ±limiar (default 5%), monta a matriz de transição 3×3 por contagem (MLE), resolve a distribuição estacionária (mix de longo prazo) e roda um backtest walk-forward **sem lookahead** (Sharpe + maxDD). Sinal = P(Bull|atual) − P(Bear|atual) ∈ [−1,1].

**Papel no CaM — só A no MVP.** Bloco analítico **read-only** no inspetor — "assistente de pesquisa" (Art. 13/34–36, ADR-006). Mostra informação, nunca emite ordem. Os papéis **B (confirmar entrada)** e **C (sizing pela estacionária)** tocam execução/contratos e ficam **fora**, como trilha futura gated pela **Parte VII** (validação por evidência em dado do CaM, líquido de custos, congelamento em POV) e Arts. 10/11/11-B.

**Integração (MVP).**
- Vendorizar só as funções puras (`label_regimes`, `build_transition_matrix`, `stationary_distribution`, `signal_from_matrix`, `walk_forward_backtest`, HMM opcional) com atribuição. **Descartar o caminho yfinance** — alimentar com a série de close dos candles do CaM (Timescale). Mantém o canal único.
- HMM degrada com elegância (pode não compilar no Windows de produção sem MSVC; o modelo observável segue válido).

**Caveats honestos (no rótulo, não escondidos).**
- O rótulo é tendência **defasada**; janelas sobrepostas (19/20 dias) autocorrelacionam os rótulos → a "persistência" da matriz é em parte artefato. Tratar persistência/estacionária como descritivo, não profecia.
- O backtest usa `sign(sinal)` e **não modela custo/spread** → Sharpe é bruto. É trend-following disfarçado: Sharpe bom em índice ≠ edge em WIN intradiário.
- Regime **diário** é filtro macro grosseiro; para a S1 (ORB 60m WIN) é contexto, não sinal. Regime intradiário exige re-tunar janela/limiar e corrigir a anualização (√252 é diária).

**Procedência (Kevin / SEC-GOV).** O arquivo `markov-hedge-fund-method.md` é um **prompt auto-instalador** que executa comandos e imprime um bloco de marketing (skool.com) verbatim. **Não rodar o instalador.** Aproveitar só a matemática (padrão de livro-texto), com atribuição a Roan e Lewis Jackson, sob a governança do CaM.

---

> **Gate de aprovação SPEC/Founder:** Carlos ratifica este SCOPE e o `ADR-014` antes do detalhamento do SPEC.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

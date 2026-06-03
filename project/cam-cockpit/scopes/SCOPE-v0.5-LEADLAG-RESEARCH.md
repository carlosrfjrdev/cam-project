---
template: SCOPE
phase: DISC → SPEC (research lane)
status: Draft v0.5 — pendente gate do Founder
produto: CaM
codinome: research-cubo-leadlag ("O Cubo") · fatia v0.5
versao: v0.5
vive_em: project/cam-cockpit/scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md
data: 2026-06-03
lead: Marty (DISC) · Leo (orquestração) · Founder (aprovação)
co_participacao: Ada (dados), Jim (quant), Nassim (risco), Don (UX), Kevin (SEC-GOV), Voltaire (challenger)
baseado_em:
  - project/cam-cockpit/research/leadlag/EDGE-THESIS-LEADLAG-CUBE.md
  - project/cam-cockpit/research/leadlag/CaM-RESEARCH-CUBO-LEADLAG.md
  - project/cam-cockpit/research/leadlag/CaM-SCOPE-FRONTEND-CUBO.md
  - project/cam-cockpit/research/leadlag/THESIS-ANALYSIS-01.MD
  - project/cam-cockpit/research/leadlag/THESIS-LEADLAG-PROPOSAL.MD
gate: Founder pendente
---

# SCOPE v0.5 — Lead-Lag Research Lane (R0 Dados + 1ª Análise Bar-Time)

> Fatia **research-only**, proporcional e honesta, do Cubo de Lead-Lag.
> **Não** promove estratégia, **não** envia ordem, **não** aciona paper/live,
> **não** parametriza Risk Engine, **não** justifica exceção constitucional.
> Isolamento research↔live como **barreira técnica** (Kevin). Modo Dev Fase 0
> vigente (`DECISAO-FOUNDER-FASE0-DEV-MODE.md`): cerimônia constitucional
> suspensa até v1.0, mas isolamento e "sem execução real" **permanecem**.

---

## 1. Contexto e motivação

O Founder pediu para evoluir o CaM materializando o loop pedido pela tese do Cubo:
**obter dado de análise do MetaTrader 5 → persistir em banco → fazer a análise →
retornar os dados.** A tese inteira (R0→R4, dois modos bar-time, OFI/tick, Fibonacci,
síntese regime×gatilho, Quant Lab completo) é **GRANDE demais** para uma única versão.

O consenso das personas em `THESIS-ANALYSIS-01.MD` é inequívoco: **dados primeiro**.
O primeiro gate é **de dados**, não estatístico (Voltaire Q2, Jim, Ada). Construir
ranking de edge sobre dado sem provenance é "máquina elegante de medir ruído"
(THESIS-ANALYSIS §3.2).

Esta v0.5 entrega a **fatia R0 + a primeira análise de lead-lag bar-time**, ancorada
no que **já existe e roda** (estado real vence intenção, NCC-1701 §2 regra 7). Não é o
Cubo inteiro; é o **loop completo, honesto e falsificável** sobre uma fundação real.

## 2. Posicionamento — research lane isolada, MT5 como fonte real

### 2.1 A tese mudou de fonte (estado real vence intenção)

A tese (`CaM-RESEARCH-CUBO-LEADLAG.md §1/§9`) assumia "research lane Parquet/DuckDB
isolada importando dado de terceiros". **Desde então, construímos a integração MT5
real.** Estado real verificado em `/apps`:

| Componente real | Onde | O que entrega |
|---|---|---|
| Bridge MT5 (EA read-only + ZeroMQ) | `apps/cam-cockpit/backend/cam/features/mt5_integration/` | `GET_CANDLES` (OHLCV histórico, qualquer TF), `GET_SYMBOLS`, `SUBSCRIBE`, tick ao vivo (`mt5.tick`), book (`mt5.book`), heartbeat |
| `MarketHub` / `market_routes` | idem | fan-out WS, `GET /api/v1/mt5/candles`, `symbol_resolver` |
| `cam_market_ticks` (hypertable) | migração `c3d4e5f6a7b8` | ticks ao vivo (`source="mt5.cam_bridge"`), via `TickPersister` |
| `cam_candles_*` (continuous aggregates 1s→1d) | idem | candles derivados de `cam_market_ticks` |
| `cam_inspector_candles` (tabela regular D1) | migração `e1f2a3b4c5d6` | candles D1 upsert idempotente; alimenta `regime` |
| feature `regime` (Markov, funções puras) | `cam/features/regime/` | **precedente** de slice analítico read-only sobre tabela de banco |
| feature `research` (correlação, pair-trade) | `cam/features/research/` | já existe; **bloqueada em `TD-v0.5-PRICESERIES`** (sem séries persistidas) |

**Implicação central:** a fonte primária do Cubo na v0.5 é o **MT5 via bridge**, não
importação de Parquet de terceiros. A research lane **não desaparece** — ela passa a
ser **alimentada pelo MT5** e materializada em **schema `research_*` próprio** no mesmo
PostgreSQL/TimescaleDB, com isolamento técnico do live.

### 2.2 O gate de dados do agressor (honestidade inegociável)

A **Tese 1 (Cubo Rápido / OFI)** exige a flag de **agressor** (comprador vs vendedor —
B3 Times&Trades, §3.1). **O MT5 padrão NÃO entrega agressor confiável**: dá `last`,
`bid`, `ask`, `volume`, mas não o lado agressor auditável. Isto é um **gate de dados
crítico**, não um detalhe.

Consequência direta para v0.5 (alinhada à PROPOSAL, Cenário B de Ada):

> O cenário realista de curto prazo é **bar-time / OHLCV** (`PROPOSAL §6.1 Cenário B`,
> `m1_is_primary`). v0.5 favorece os modos **bar-time (INTRADAY e SWING)** da PROPOSAL.
> **OFI/tick é LATER, não titular** — entra como camada opcional falsificável (modelo
> aninhado) só quando/se houver fonte de agressor auditável.

Isto responde a Voltaire Q1 (`THESIS-ANALYSIS §9.1`): a tese **não morre** sem agressor —
ela **se adapta honestamente** ao modo bar-time, e o admite por escrito em vez de fingir
ter um dado que não tem.

## 3. O que a v0.5 entrega

Loop completo pedido pelo Founder, numa fatia provável:

```
MT5 (GET_CANDLES OHLCV) ──► ingestão research ──► research_bars (canônico M1
                                                  + derivadas determinísticas)
                                   │
                                   ▼
                  1ª análise lead-lag bar-time: C_{S→D}(δ) sobre grade de δ
                  (anti-look-ahead, trial accounting honesto)
                                   │
                                   ▼
          REST /api/v1/research/leadlag/* ──► Quant Lab mínimo (read-only, badge RESEARCH)
```

### 3.1 Backend — ingestão + persistência canônica (R0)

- Ingestão **sob demanda** de OHLCV do MT5 via bridge existente (`GET_CANDLES`), para
  um universo e janela pré-registrados.
- **Barra canônica M1** persistida em `research_bars` (schema `research_*` novo);
  **M5, M15, M30, H1** derivadas por **agregação determinística** de M1 (PROPOSAL §6.1):
  open=primeiro, high=max, low=min, close=último, volume=soma; bucket ancorado no início
  da sessão B3. **H1 computado uma vez** e compartilhado (fronteira INTRADAY↔SWING).
- **Provenance por lote** (`research_data_sources`): `bar_origin=broker_ohlcv`,
  `ts_source`, símbolo, TF, janela, `ingested_at`, hash do lote.
- **Snapshot imutável com hash composto** (`research_dataset_snapshots`): rerun cria
  nova run vinculada, nunca edita (Ada — run imutável).
- **Quality checks mínimos** (`research_data_quality_checks`): `missing_bars`,
  `bucket_misalignment`, `partial_bar`, `m1_is_primary`, `stale_bar`.

### 3.2 Backend — 1ª análise de lead-lag bar-time (fatia de R2-bar)

- **Correlação defasada bar-time** `C_{S→D}(δ)` (PROPOSAL §3.1 / `CaM-RESEARCH §4.2`),
  para δ ∈ grade pré-registrada, δ ≥ 1.
- **Anti-look-ahead inegociável** (PROPOSAL §3.1): feature usa informação até e
  inclusive o fechamento da barra t; label medido estritamente depois (preço executável
  pós-barra). Reaproveitar close como feature e entrada = vazamento → proibido.
- **Trial accounting honesto** (`research_runs` + contador): registra `N_t` = |fontes| ×
  |alvos| × |grade δ| × reruns. **Sem prometer DSR/SPA/FDR completos** antes do dado
  existir — v0.5 expõe o **contador de tentativas** e marca claramente que a deflação
  estatística plena (DSR de duas camadas) é **LATER**.
- **Veredito "dado insuficiente" é estado de primeira classe** (Art. 30 — confiança
  subjetiva não é evidência): abaixo de piso amostral, a célula não é "edge" nem "sem
  edge", é **insuficiente**.

### 3.3 Frontend — Quant Lab mínimo (UI-R0 + leitura da 1ª análise)

- Área **Quant Lab** separada do Cockpit Live, **badge `RESEARCH` permanente** (Don).
- **Data Health** (cobertura por símbolo/TF, status de ingestão) **antes** de qualquer
  leitura otimista.
- **Leitura da 1ª análise**: tabela/heatmap mínimo de `C_{S→D}(δ)` por δ, com contador
  de tentativas e n amostral ao lado; **manchete = expectância/correlação com n**, nunca
  taxa de acerto.
- **Vocabulário de pesquisa** (hipótese, célula, evidência, candidata) — proibido sinal,
  compra, venda, entrada, setup.
- **Sem nenhum atalho** para paper/live, ordem ou Risk Engine.

## 4. IN / OUT / LATER

### IN (v0.5)
- Ingestão OHLCV do MT5 via bridge existente (`GET_CANDLES`), sob demanda.
- `research_bars` canônico M1 + derivadas determinísticas (M5/M15/M30/H1).
- Schema `research_*` (sources, snapshots, quality_checks, runs) — mínimo viável.
- Provenance + snapshot imutável + hash composto + quality checks mínimos.
- 1ª análise lead-lag bar-time `C_{S→D}(δ)` com grade de δ, anti-look-ahead.
- Trial accounting honesto (contador de tentativas), "dado insuficiente" 1ª classe.
- Isolamento research↔live **técnico** (barreira, não texto).
- Rotas REST `/api/v1/research/leadlag/*` read-only.
- Quant Lab mínimo: Data Health + leitura da 1ª análise + badge RESEARCH.

### OUT (não entra — fora de escopo)
- **S1 (ORB 60m WIN)** — trilha separada, decisão explícita do Founder.
- Execução real, envio de ordem, candidato operacional, paper/live.
- Qualquer escrita em `cam_orders`, `cam_positions`, `cam_journal_entries`.
- Parametrização/desabilitação do Risk Engine (Art. 35º).
- Re-render de tick cru no Quant Lab (fica no Inspetor existente).
- Edição manual de resultado/estatística (run é imutável).

### LATER (reconhecido, adiado)
- **OFI/tick como titular** — depende de fonte de agressor auditável (gate §2.2).
  Entra como camada opcional aninhada (modelo B vs A), nunca carregador único.
- **DSR de duas camadas / FDR por modo / Hansen SPA** completos (PROPOSAL §4) —
  estatística plena de deflação só faz sentido com corpus consolidado.
- **Walk-forward + purged CV com embargo** (PROPOSAL §5) — pós-R0 estável.
- **Modo SWING completo (H4/D1)** com rolagem contínua WIN/WDO + teste de salto
  (PROPOSAL §6.3) — exige ≥3–5 anos e ≥2 regimes macro; v0.5 prepara o contrato, não
  promove o veredito swing.
- **Fibonacci** (réu até prova de incremento OOS — `CaM-RESEARCH §4.5`).
- **Síntese R4** (regime lento × gatilho rápido).
- **Granger / Transfer Entropy / Hayashi-Yoshida** (event-time, dependem de tick).
- **Quant Lab completo** (Cube Explorer 3D, Cell Detail dossiê, Run Launcher, Fib A/B,
  Synthesis) — `CaM-SCOPE-FRONTEND-CUBO.md` é a visão completa, LATER.

## 5. Dependências técnicas

| Camada | Reuso (existe) | Novo (v0.5) |
|---|---|---|
| Broker | bridge MT5 + `GET_CANDLES` + `market_routes` | adaptador de ingestão research (chama bridge, não importa execução) |
| Dados-DB | PostgreSQL 16 / TimescaleDB; padrão de migração alembic; precedente `cam_inspector_candles` | schema `research_*` (migração nova); funções puras de agregação M1→TF |
| Backend | FastAPI + SQLAlchemy async; padrão feature-slice (`regime` como modelo); feature `research` existente (desbloqueia `TD-v0.5-PRICESERIES`) | feature `research/leadlag` (domain puro + repository + routes) |
| Frontend | React 19 + Vite + MUI + react-query + lightweight-charts; Inspetor como precedente read-only | área Quant Lab mínima + Data Health + leitura da análise |

> **Decisão de dados (Ada) endereçada no SPEC:** `research_bars` é tabela **própria**
> (não reusa os continuous aggregates `cam_candles_*`), porque a research exige
> provenance, calendário, snapshot e hash que os aggregates do live **não** carregam —
> e porque misturar storage de research com storage do live fere o isolamento (Kevin).
> Os `cam_candles_*`/`cam_market_ticks` permanecem como fonte **live** independente.

## 6. Blocos de execução por ambiente (sem estimativa de tempo)

| Bloco | Ambiente | Conteúdo |
|---|---|---|
| **BL-DB-0** | Dados-DB | Migração schema `research_*` (bars, sources, snapshots, quality_checks, runs); índices `(symbol, timeframe, session_date)` |
| **BL-BE-1** | Backend | Adaptador de ingestão MT5→`research_bars` (canônico M1 + derivadas determinísticas + provenance + hash) |
| **BL-BE-2** | Backend | Quality checks + snapshot imutável + run accounting |
| **BL-BE-3** | Backend | Análise `C_{S→D}(δ)` (domain puro, anti-look-ahead) + contador de tentativas + "dado insuficiente" |
| **BL-BE-4** | Backend | Rotas `/api/v1/research/leadlag/*` (read-only) + isolamento técnico (sem import de execução) |
| **BL-FE-1** | Frontend | Área Quant Lab + badge RESEARCH + Data Health |
| **BL-FE-2** | Frontend | Leitura da 1ª análise (heatmap/tabela mínima + contador + n) |
| **BL-SEC-0** | SEC-GOV (transversal) | Prova de isolamento research↔live, permissões, namespace `/research`, ausência de import de execução, sem secrets |

> Ordem natural: BL-DB-0 → BL-BE-1 → BL-BE-2 → BL-BE-3 → BL-BE-4 → (BL-FE-1, BL-FE-2).
> BL-SEC-0 é **transversal** (Kevin) e fecha o gate. Detalhamento e decomposição em
> TASKs ficam para o PLAN (Nico).

## 7. Riscos

| # | Risco | Mitigação na v0.5 |
|---|---|---|
| RK-1 | **Sem agressor** → Tese 1/OFI inviável | Aceito por escrito (§2.2); v0.5 é bar-time; OFI = LATER aninhado |
| RK-2 | **Decoração estatística** (Voltaire) — heatmap bonito sem denominador | Contador de tentativas obrigatório; "dado insuficiente" 1ª classe; DSR pleno é LATER explícito, não fingido |
| RK-3 | **Look-ahead** (close usado como feature e entrada) | Regra anti-look-ahead inegociável no SPEC (R-*); label pós-barra |
| RK-4 | **Vazamento research→live** | Barreira técnica: serviço sem escrita em tabelas live; sem import de Order Gateway/bridge de execução/`OrderSend` (Kevin) |
| RK-5 | **Não-determinismo da agregação** | `derive(M1, rule, TF)` função pura; rerun byte-idêntico; hash composto |
| RK-6 | **Gap overnight tratado como erro** | Gap é feature (PROPOSAL §6.3); forward-fill proibido |
| RK-7 | **Amostra escassa** vira "sem edge" falso | Piso amostral → veredito "dado insuficiente" (Art. 30) |
| RK-8 | **UI cria maturidade falsa** (Don) | Data Health antes do heatmap; vocabulário de pesquisa; zero affordance de trade |

## 8. Decisões abertas do Founder

1. **Universo inicial** v0.5: quais símbolos (ex.: WIN, WDO + 1–2 single-names) entram na
   1ª ingestão/análise? (recomendação: começar pequeno e auditável)
2. **Janela histórica** e **TF base**: M1 como canônico exige volume de barras — confirmar
   profundidade inicial (ex.: N dias) e se MT5 entrega M1 suficiente via `GET_CANDLES`.
3. **Grade inicial de δ** (defasagem em barras) por TF — confirmar tabelas PROPOSAL §3.3
   ou calibrar.
4. **Piso amostral** abaixo do qual o veredito é "dado insuficiente".
5. **Persistência** confirmada: PostgreSQL com namespace `research_*` + permissões duras
   (recomendação Leo/Ada/Kevin), em vez de store separado.
6. **Modo SWING** (H4/D1 + rolagem contínua): v0.5 só prepara contrato, ou já ingere D1
   reusando `cam_inspector_candles` como insumo? (recomendação: preparar contrato, não
   promover veredito swing nesta versão)
7. **S1 (ORB 60m WIN)** confirmado **OUT** desta trilha — apenas ratificar.

## 9. Gate de aprovação

- Este SCOPE **não avança** sem aprovação explícita do Founder (Founder-only, NCC-1701 §7).
- Aprovado o SCOPE → SPEC (`SPEC-v0.5-LEADLAG-RESEARCH.md`, Albert) → PLAN (Nico) → CODE.
- Gatilho **SEC-GOV obrigatório** (Kevin): dados sensíveis + nova superfície + fronteira
  com tabelas operacionais. Conditional Go condicionado à **prova de isolamento técnico**.
- Sem auto-approval em nenhum gate. Research-only. Risk Engine intocado.

## 10. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| v0.5 | 2026-06-03 | Draft inicial — fatia R0 dados + 1ª análise bar-time, ancorada no MT5 real | (pendente Founder) |

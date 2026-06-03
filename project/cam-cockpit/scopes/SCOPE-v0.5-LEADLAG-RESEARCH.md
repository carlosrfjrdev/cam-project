---
template: SCOPE
phase: DISC → SPEC (research lane)
status: APROVADO v0.5 (rev. 2) — Founder ratificou 2026-06-03
produto: CaM
codinome: research-cubo-leadlag ("O Cubo") · tese completa v0.5
versao: v0.5
vive_em: project/cam-cockpit/scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md
data: 2026-06-03
lead: Marty (DISC) · Leo (orquestração) · Founder (aprovação)
co_participacao: Ada (dados), Jim (quant), Nassim (risco), Don (UX), Kevin (SEC-GOV), Voltaire (challenger)
baseado_em:
  - project/cam-cockpit/research/leadlag/CaM-RESEARCH-CUBO-LEADLAG.md
  - project/cam-cockpit/research/leadlag/THESIS-LEADLAG-PROPOSAL.md
  - project/cam-cockpit/research/leadlag/THESIS-ANALYSIS-01.md
  - project/cam-cockpit/research/leadlag/CaM-SCOPE-FRONTEND-CUBO.md
  - project/cam-cockpit/research/leadlag/PROBE-AGGRESSOR-RESULT.md
arquitetura:
  - project/cam-cockpit/adrs/ADR-015-research-lane-isolada.md (Accepted)
  - project/cam-cockpit/DAS.md (camada Research Lane)
  - pyproject.toml — contrato import-linter "Research Lane nao importa execucao nem broker (ADR-015)" (ativo)
gate: Founder pendente
---

# SCOPE v0.5 — Cubo de Lead-Lag Cross-Asset (TESE COMPLETA, faseada)

> Trilha **research-only**, isolada do live por barreira técnica (ADR-015).
> **Não** promove estratégia, **não** envia ordem, **não** aciona paper/live,
> **não** parametriza Risk Engine, **não** justifica exceção constitucional
> (Arts. 34º–36º). Modo Dev Fase 0 vigente
> (`DECISAO-FOUNDER-FASE0-DEV-MODE.md`): cerimônia constitucional suspensa até
> v1.0, mas **isolamento research↔live** e **"sem execução real"** permanecem.

---

## 0. O que mudou nesta revisão (rev. 2)

Decisão do Founder após revisar a v0.5 (rev. 1):

1. **A v0.5 cobre a TESE INTEIRA, num documento único.** Rejeitado o framing
   anterior que empurrava metade da tese para "LATER". O SCOPE/SPEC descrevem o
   **todo** (R0 dados → R1 features → R2 cubo rápido/OFI → R3 cubo lento/estrutura
   + fib → R4 síntese → Quant Lab). **A subdivisão em sub-versões (0.5.1, 0.5.2, …)
   é feita no PLAN (Nico)**, não aqui. "Oneshot one kill da 0.5 real."
2. **OFI/tick está PROVADO e entra como IN** (não mais LATER assumido). O gate de
   dados do agressor foi resolvido **empiricamente** — ver `PROBE-AGGRESSOR-RESULT.md`.
3. **Universo é parametrizável** — requisito de primeira classe. O operador
   seleciona a tese/universo → o sistema extrai do MT5 → persiste → processa →
   exibe resultado. Nada hardcoded.

A seção **LATER** que empurrava partes da tese para fora **foi removida**. O que é
da tese é **IN, faseado** (§4). **OUT** continua valendo só para o que **não é** da
tese (S1, execução, ordem, paper/live, escrita em tabelas live).

---

## 1. Contexto e motivação

O Founder pediu para materializar o loop central da tese do Cubo:

> **seleciono a tese/universo → os dados são extraídos do MetaTrader 5 →
> persistidos em base → processados → resultado exibido.**

A tese completa está formalizada em três artefatos de research (matemática,
contrato de dados e parecer consolidado das personas):

- `CaM-RESEARCH-CUBO-LEADLAG.md` — matemática formal (OFI, Hayashi-Yoshida,
  HRY, Granger, transfer entropy, DSR/FDR/SPA, event study, Kelly, duas lentes).
- `THESIS-LEADLAG-PROPOSAL.md` — dois modos bar-time (intraday/swing), trial
  accounting por modo, contrato de dados (Ada), fronteira H1.
- `THESIS-ANALYSIS-01.md` — parecer consolidado (Jim, Nassim, Ada, Don, Kevin,
  Voltaire). **Reusado, não recomeçado.**

O consenso permanece: **dados primeiro**. O primeiro gate é **de dados**, não
estatístico (Voltaire, Jim, Ada). A diferença desta revisão é que **o gate de
dados mais crítico — o agressor — já foi resolvido por medição** (§2.2), o que
torna a tese rápida (OFI) viável **dentro** da v0.5.

## 2. Posicionamento — research lane isolada, MT5 como fonte real (provada)

### 2.1 A fonte é o MT5 (estado real vence intenção, NCC-1701 §2 regra 7)

A tese original assumia "Parquet/DuckDB importando dado de terceiros". O estado
real é melhor: a **integração MT5** já existe e roda. Confirmado em `/apps`:

| Componente real | Onde | O que entrega |
|---|---|---|
| Bridge MT5 (EA read-only + ZeroMQ) | `apps/cam-cockpit/backend/cam/features/mt5_integration/` | `GET_CANDLES` (OHLCV, qualquer TF), `GET_SYMBOLS`, `SUBSCRIBE`, tick ao vivo (`mt5.tick`), book, `PROBE_TICKS`, heartbeat |
| `PROBE_TICKS` + `/api/v1/mt5/probe-ticks` | idem + EA `cam_bridge` v0.40 | `CopyTicks(COPY_TICKS_ALL)` lendo `MqlTick.flags` (agressor) — **commitado** |
| `MarketHub` / `market_routes` | idem | fan-out WS, `GET /api/v1/mt5/candles`, `symbol_resolver` |
| `TickPersister` → `cam_market_ticks` | `tick_persister.py` (migração `c3d4e5f6a7b8`) | grava `asset, price, volume, timestamp, source` — **NÃO grava `flags`** hoje |
| `cam_candles_*` (continuous aggregates 1s→1d) | idem | candles do **live**, derivados de `cam_market_ticks` |
| feature `regime` (Markov, funções puras) | `cam/features/regime/` | precedente de slice analítico read-only sobre tabela de banco |
| feature `research` | `cam/features/research/` | já existe; Pearson defasado implementado; barreira import-linter ativa |
| **ADR-015 + import-linter** | `ADR-015-research-lane-isolada.md` + `pyproject.toml` | schema `research_*` próprio; contrato "Research Lane nao importa execucao nem broker" **ativo** |

**Implicação:** a fonte primária do Cubo é o **MT5 via bridge**, materializada em
**schema `research_*` próprio** no mesmo PostgreSQL/TimescaleDB, isolada do live por
barreira de código (ADR-015 — já **Accepted**).

### 2.2 O gate do agressor — RESOLVIDO empiricamente (não mais suposição)

A v0.5 (rev. 1) **assumia no papel** que "MT5 não entrega agressor" e rebaixava
OFI/tick para LATER. **Medimos.** Comando `PROBE_TICKS` (EA, read-only) →
`CopyTicks(symbol, COPY_TICKS_ALL, 0, 500)` lendo `MqlTick.flags`, mercado aberto.
Evidência registrada em **`PROBE-AGGRESSOR-RESULT.md`**:

| Símbolo | copied | agressor disponível | n_buy | n_sell | span | nota |
|---|---|---|---|---|---|---|
| **WIN$** (contínuo) | 500 | ✅ **true** | 176 | 224 | 7,4 s | índice — fluxo denso |
| **WINM26** (vencimento) | 500 | ✅ **true** | 319 | 140 | 3,0 s | futuro — fluxo denso |
| **PETR4** (ação) | 500 | ✅ **true** | 319 | 72 | 254,8 s | ação — fluxo **esparso** |

Bits `TICK_FLAG_BUY (32)` / `TICK_FLAG_SELL (64)` vêm **populados**, com timestamp
em ms (`t_msc`). **Veredito:** o `ε_k ∈ {+1,−1}` do OFI (`CaM-RESEARCH §3.1`)
**EXISTE** no CaM via MT5/Genial, em **futuro E ação**.

**Consequência de escopo (promoção de LATER → IN, faseado):**
- **OFI/tick** (cubo rápido) é **IN**.
- **Hayashi-Yoshida** (mata-Epps), **Granger**, **transfer entropy**, **lead-lag HRY**
  ficam viáveis (têm tick assíncrono com `t_msc`) → **IN**.
- A `TickPersister` precisa passar a **persistir o `flags`** (agressor) — hoje grava
  só `price/volume`. Persistir o agressor entra no escopo.

### 2.3 Caveat honesto — liquidez de tick NÃO é uniforme (Nassim / Voltaire)

Registrado em `PROBE-AGGRESSOR-RESULT.md §Caveat` e **não escondido**: a liquidez
de tick varia muito por ativo — **WIN faz 500 ticks em ~5s; PETR4 em ~255s**. O dado
existe, mas a microestrutura não é uniforme. O horizonte τ explorável e a capacidade
por ativo dependem do giro do alvo. O **event study tem de condicionar por liquidez
do alvo** (`CaM-RESEARCH §10`, PROPOSAL §5.4). OFI viável ≠ OFI uniforme.

## 3. O loop parametrizável que a v0.5 entrega

```
[Founder seleciona TESE/UNIVERSO]
   sources[] · target(s) · delta_grid[] · thresholds · timeframes · modo
        │
        ▼
MT5 (GET_CANDLES OHLCV  +  ticks com flags/agressor)
        │  ingestão research (na borda; sem import de execução)
        ▼
research_* (PostgreSQL): research_bars (canônico M1 + derivadas determinísticas)
                         research_ticks (com agressor) · snapshots · quality · runs
        │  processamento (funções puras, anti-look-ahead, trial accounting honesto)
        ▼
Cubo: ρ defasado bar-time + event-time · OFI assinado · HY · HRY · Granger ·
      cubo lento/estrutura + fib (réu) · síntese regime×gatilho (R4)
        │  REST /api/v1/research/* (read-only)
        ▼
Quant Lab (badge RESEARCH): Data Health → Explorer → Cell Detail (dossiê Go/No-Go)
```

Nada do universo é hardcoded: o operador **seleciona** e a run carrega a
configuração (§4, requisito UNIV).

## 4. IN / OUT (sem seção "LATER" empurrando tese para fora)

> Tudo que é da tese é **IN**, **faseado** (faseamento sugerido em §6). A
> decomposição final em sub-versões é do **PLAN (Nico)** — §6.

### IN (v0.5 — a tese completa)

**R0 — Dados (fundação, gate de dados primeiro)**
- Ingestão **parametrizável** MT5 → DB: OHLCV via `GET_CANDLES` **e** ticks com
  `flags`/agressor; universo, janela e grade definidos pela run.
- **Janela histórica M1:** ingerir "o máximo que o MT5 entregar"; Data Health
  reporta a cobertura real (decisão Founder, §8).
- `research_bars` canônico **M1** + **M5/M15/M30/H1/H4/D1** derivados por agregação
  **determinística** de M1 (função pura, byte-idêntica); H1 computado **uma vez**.
- `research_ticks` (ou `cam_market_ticks` estendido com `flags`) com agressor
  assinado — **decisão de dados de Ada no SPEC** (§5).
- Provenance por lote + snapshot imutável + hash composto + quality checks.
- Calendário B3 versionado; gap overnight como feature; rolagem WIN/WDO versionada
  (série contínua + teste de salto) quando o swing exigir.

**R1 — Features (puras, versionadas, anti-look-ahead)**
- OFI assinado (`§3.1`), z-score rolante; estrutura (ZigZag/fractal, S/R, breakout,
  RS); volatilidade (ATR/RV); níveis Fibonacci + `d_φ`. Todas determinísticas.

**R2 — Cubo rápido / OFI (event-time)**
- Correlação defasada `ρ_{F→D}(τ)`; **Hayashi-Yoshida** (mata-Epps); lead-lag
  **HRY** (`argmax U(θ)`); **Granger** / **transfer entropy**; event study assinado
  com expectância líquida; curva de decaimento e condição de executabilidade
  (`μ̂_{h=λ}>0`), condicionado por liquidez do alvo (§2.3).

**R3 — Cubo lento / estrutura (bar-time, dois modos)**
- Lead-lag estrutural `C_{S→D}(δ)` (baseline **sem** fib); modo INTRADAY (M1–H1) e
  SWING (H1–D1); **Fibonacci como réu** (modelo aninhado A vs B; fica só se
  `Δ=μ̂_B−μ̂_A>0` OOS e sobrevive aos controles de redundância — `§4.5`).

**R4 — Síntese**
- Regime lento (porteiro) × gatilho rápido (direção/timing); a composição só vale
  se **supera as partes isoladas OOS**.

**Validação estatística honesta (transversal a R2–R4)**
- **Trial accounting** real por modo/TF (`N_t`), **DSR de duas camadas**, **FDR (BH)
  por modo**, **Hansen SPA / Bonferroni** no topo, **walk-forward + purged CV com
  embargo wall-clock**. **"Dado insuficiente" é veredito de 1ª classe** (Art. 30).
- O **rigor cresce com a sub-versão** (§6): OFI viável já agora; **DSR pleno exige
  corpus** (Jim) — não se finge deflação sobre amostra inexistente, declara-se o
  estado real em Data Health.

**Quant Lab (frontend, `CaM-SCOPE-FRONTEND-CUBO.md`)**
- Data Health → Cube Explorer (heatmap + slider de lag + filtro de sobreviventes +
  ranking) → Cell Detail (decaimento, event study, HY vs ingênua, contraste
  lead-lag, veredito DSR/FDR, **checklist Go/No-Go**) → Run Launcher (pré-registro
  imutável) → Run Registry (contador global de tentativas) → Fib A/B → Synthesis.
- Badge **RESEARCH** permanente; vocabulário de pesquisa; **zero** affordance de trade.

**Isolamento + parametrização (requisitos de 1ª classe)**
- **UNIV — Universo parametrizável:** `research_runs` carrega `sources[]`,
  `target(s)`, `delta_grid[]`, `timeframes[]`, `mode`, thresholds. **Nada hardcoded.**
- **ISO — Isolamento research↔live técnico:** import-linter (ativo) + permissão de
  banco; sem escrita em tabelas live; namespace `/api/v1/research/*`.

### OUT (não é da tese — fora de escopo)
- **S1 (ORB 60m WIN)** — trilha separada. **Confirmado OUT** pelo Founder (§8).
- **Execução real, envio de ordem, candidato operacional, paper/live.**
- Qualquer **escrita** em `cam_orders`, `cam_positions`, `cam_journal_entries` ou
  equivalentes operacionais (escrita **live**).
- Parametrização/desabilitação do Risk Engine (Art. 35º).
- Promoção automática de célula → estratégia (passa pelo Go/No-Go + pipeline CaM).
- Re-render de tick cru no Quant Lab (fica no Inspetor existente).
- Edição manual de resultado/estatística (run imutável).
- HFT / sub-segundo (edge que vive < latência real é fora de escopo — `§3.8`).

> **Não há seção LATER de tese.** O único "depois" legítimo é o **faseamento
> interno** (§6) — sequência de execução, não exclusão de escopo.

## 5. Dependências técnicas

| Camada | Reuso (existe) | Novo (v0.5) |
|---|---|---|
| Broker | bridge MT5 + `GET_CANDLES` + `PROBE_TICKS` + `market_routes` | adaptador de ingestão research **na borda** (chama bridge; não importa execução — import-linter ativo) |
| Tick | `TickPersister` + `cam_market_ticks` | **persistir `flags`/agressor** (hoje ausente) — `research_ticks` próprio ou estender `cam_market_ticks` (decisão Ada no SPEC) |
| Dados-DB | PostgreSQL 16 / TimescaleDB; alembic; precedente `cam_inspector_candles`; ADR-015 (Accepted) | schema `research_*` (migração); funções puras de agregação M1→TF; calendário/rolagem versionados |
| Backend | FastAPI + SQLAlchemy async; feature-slice (`regime`, `research`); Pearson defasado existente | feature `research/leadlag` (domain puro + repository + routes); OFI/HY/HRY/Granger; stats layer |
| Frontend | React 19 + Vite + MUI + react-query + lightweight-charts; Inspetor read-only | Quant Lab (Explorer, Cell Detail, Launcher, Registry, Data Health, Fib A/B, Synthesis) |

## 6. Faseamento sugerido — RECOMENDAÇÃO ao PLAN (Nico decide)

> O SCOPE/SPEC descrevem o **todo**. A **decomposição em sub-versões é do PLAN**
> (`teczi-code-planning`, Nico). A sequência abaixo é **recomendação**, ancorada na
> ordem "dados primeiro" (THESIS-ANALYSIS §7) e no faseamento R0→R4
> (`CaM-RESEARCH §8.7`, PROPOSAL §10). **Nico tem direito formal de redesenhar** a
> decomposição e de contestar o P/M/G (loop ilimitado com Albert; Founder decide).

| Sub-versão sugerida | Conteúdo | Nota |
|---|---|---|
| **0.5.1 — Dados (R0)** | schema `research_*`, ingestão parametrizável MT5→DB (candles + ticks com agressor), barras canônicas determinísticas, snapshot/hash, quality checks, Data Health, isolamento técnico | gate de dados **primeiro**; UI-R0 mínima |
| **0.5.2 — OFI / cubo rápido (R2)** | OFI assinado, ρ defasado event-time, event study líquido condicionado por liquidez, curva de decaimento, top-N | usa agressor provado (§2.2) |
| **0.5.3 — Validação estatística** | trial accounting, DSR (camadas), FDR/SPA, walk-forward + purged CV, "dado insuficiente" 1ª classe | rigor cresce com corpus (Jim) |
| **0.5.4 — Cubo lento / swing (R3 estrutura)** | `C_{S→D}(δ)` bar-time, modos intraday/swing, H1 único, rolagem WIN/WDO + teste de salto | amostra é a restrição (Nassim) |
| **0.5.5 — Fibonacci** | níveis + `d_φ`, modelo aninhado A/B, controle de redundância (fib como réu) | fica só se incrementa OOS |
| **0.5.6 — Síntese (R4)** | regime lento × gatilho rápido; composição > partes | deflação de topo sobre os modos |
| **0.5.7 — Quant Lab completo** | Explorer 3D, Cell Detail dossiê, Launcher, Registry, Fib A/B, Synthesis | UI cresce com o backend |

> HY/HRY/Granger/transfer entropy acompanham 0.5.2/0.5.3 (event-time). A UI cresce
> em paralelo (UI-R0 em 0.5.1; demais telas conforme o backend amadurece).

## 7. Riscos

| # | Risco | Mitigação na v0.5 |
|---|---|---|
| RK-1 | **Liquidez de tick não-uniforme** (WIN ~5s vs PETR4 ~255s) | Registrado (§2.3); event study **condiciona por liquidez do alvo**; capacidade = liquidez no instante do evento, não volume diário (Nassim) |
| RK-2 | **Decoração estatística** (Voltaire) — heatmap bonito sem denominador | Trial accounting obrigatório; DSR de duas camadas; "dado insuficiente" 1ª classe; DSR pleno cresce com corpus, declarado em Data Health, **não fingido** |
| RK-3 | **Look-ahead** (close usado como feature e entrada) | Regra anti-look-ahead inegociável (SPEC R-*); label pós-barra; fixture que falharia se o close fosse reusado |
| RK-4 | **Vazamento research→live** | Barreira técnica: import-linter **ativo** (ADR-015) + permissão de banco; sem escrita em tabelas live; sem import de execução/broker (Kevin) |
| RK-5 | **Não-determinismo da agregação** | `derive(M1, rule, TF)` pura; rerun byte-idêntico; hash composto; mudar regra → nova run vinculada |
| RK-6 | **Gap overnight tratado como erro** | Gap é feature (PROPOSAL §6.3); forward-fill proibido |
| RK-7 | **Amostra escassa** (esp. swing/D1) vira "sem edge" falso | Piso `N_eff` → veredito "dado insuficiente" (Art. 30), não "sem edge" |
| RK-8 | **Múltiplos testes** com dois modos + OFI | DSR por modo/TF; subtração de H1; FDR em duas famílias; SPA no topo (PROPOSAL §4) |
| RK-9 | **Rolagem WIN/WDO** mal feita injeta salto | Série contínua versionada + teste de salto (< X·ATR); contratos crus preservados (Ada §6.3) |
| RK-10 | **UI cria maturidade falsa** (Don) | Data Health antes do heatmap; vocabulário de pesquisa; zero affordance de trade; checklist Go/No-Go no centro |
| RK-11 | **OFI viável ≠ DSR pleno** | Rigor cresce com sub-versão (§6); honestidade sobre o estado do corpus (Jim) |

## 8. Decisões do Founder — RESOLVIDAS e abertas

### ✅ Resolvidas (não reabrir nesta revisão)
- ✅ **Agressor/OFI:** disponível em futuro e ação (medido — `PROBE-AGGRESSOR-RESULT.md`).
  OFI/HY/HRY/Granger entram **IN** (§2.2).
- ✅ **Janela histórica M1:** ingerir "o máximo que o MT5 entregar"; Data Health
  reporta cobertura real.
- ✅ **Universo parametrizável** é requisito; nada hardcoded (UNIV).
- ✅ **Universo SEED do 1º teste** (não hardcode — seed inicial, trocável):
  **WIN, WDO** + 6 maiores do IBOV — **VALE3** (12,43%), **ITUB4** (8,26%),
  **PETR4** (7,58%), **AXIA3** (4,03%), **BBDC4** (3,74%), **B3SA3** (3,74%).
- ✅ **Persistência:** PostgreSQL, schema `research_*` isolado (ADR-015 Accepted;
  import-linter ativo).
- ✅ **S1 (ORB 60m WIN):** confirmado **OUT**.
- ✅ **Modo Dev Fase 0** vigente: cerimônia suspensa até v1.0; isolamento e "sem
  execução real" permanecem.

### Abertas (decididas no SPEC/PLAN, não bloqueiam o SCOPE)
1. **`research_ticks` próprio vs estender `cam_market_ticks` com `flags`** — decisão
   de dados de **Ada** no SPEC (recomendação: tabela `research_*` própria, coerente
   com ADR-015 e isolamento).
2. **Grade inicial de δ/τ e labels k por TF** — confirmar tabelas PROPOSAL §3.3 ou
   calibrar (parametrizável por run de qualquer modo).
3. **Pisos `N_eff` por TF** — confirmar tabela PROPOSAL §5.2 ou calibrar.
4. **Regra de rolagem WIN/WDO** (`roll_rule` + `splice_method`) para a série contínua
   swing — necessária antes de promover veredito swing (R0 swing).
5. **Lib de heatmap** (`plotly` vs `visx`) — ADR leve no ARCH/PLAN.

## 9. Gate de aprovação

- Este SCOPE **não avança** sem aprovação explícita do Founder (Founder-only,
  NCC-1701 §7).
- Aprovado o SCOPE → **SPEC** (`SPEC-v0.5-LEADLAG-RESEARCH.md`, Albert) → **PLAN**
  (Nico, decompõe em sub-versões 0.5.x) → **CODE** (Nikola) por sub-versão.
- **SEC-GOV ATIVO** (Kevin): dados sensíveis (broker) + integração externa (MT5) +
  nova superfície + fronteira com tabelas operacionais. Conditional Go condicionado
  à **prova de isolamento técnico** (import-linter + permissão de banco) — ADR-015
  já estabelece os controles de aceite.
- Sem auto-approval em nenhum gate. Research-only. Risk Engine intocado.

## 10. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| v0.5 (rev. 1) | 2026-06-03 | Draft — fatia R0 dados + 1ª análise bar-time; OFI/tick em LATER (assumido) | (substituído) |
| v0.5 (rev. 2) | 2026-06-03 | **Reescrito para a tese completa** (R0→R4 + OFI + HY + Granger + cubo lento + fib + síntese + Quant Lab). OFI **IN** (agressor provado — `PROBE-AGGRESSOR-RESULT.md`). Universo **parametrizável** (1ª classe) + seed inicial. Subdivisão 0.5.x movida para o **PLAN**. Seção LATER de tese removida. | (pendente Founder) |

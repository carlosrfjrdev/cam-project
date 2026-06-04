---
template: PLAN
phase: PLAN
status: APROVADO v1 — letscode=true (Founder autorizou CODE em seguida, 2026-06-03)
produto: TCaM (cam-cockpit)
id: PLAN-STRATEGYLAB-TRIAD
demanda: STRATEGYLAB-v0.6
data: 2026-06-03
lead: Nico
co: Albert (loop P/M/G — consenso em G, sem contestação)
incorpora: DESIGN-REVIEW-FRONTEND (Andy) — diretrizes no BL-FRONT
aprovador: Founder
classe: G (Grande) — decomposta · letscode: true
vinculacao: >
  SPEC-STRATEGYLAB-TRIAD v1 (APROVADA) · SCOPE-STRATEGYLAB-TRIAD v0.7 ·
  ARCH-STRATEGYLAB-TRIAD · ADR-SL-01 · ADR-SL-02 · ADR-SL-03 (Accepted) ·
  EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5 · CATALOGO-12-ESTRATEGIAS-ELEITAS ·
  DESIGN-REVIEW-FRONTEND (Andy)
modo: >
  Produto TCaM. Constituição DESCOMISSIONADA — sem Risk Engine soberano, sem Arts.,
  sem trava de capital. Permanece o RIGOR de engenharia (paridade, anti-data-snooping,
  isolamento de execução, build verde, sem secrets) como boa prática. MVP de VALORES
  BRUTOS (sem custo/IR/slippage). Ordem incremental: D1 ORB-30 fim-a-fim PRIMEIRO
  (Onda 1); as demais 9 atrás do gate "Founder validou D1".
---

# PLAN — StrategyLab do CaM · Tríade Assets Strategy + RunTests + Experts

> **Lead:** Nico (PLAN) · **Co:** Albert (P/M/G) · **Incorpora:** Andy (frontend) · **Aprovador:** Founder
> **Status:** v1 — `letscode=true` (CODE autorizado)

---

## 1. Resumo do plano

Este PLAN materializa a SPEC aprovada da tríade **Assets Strategy + RunTests + Experts** num
plano de execução **proporcional a G**, decomposto em **TASKs por bloco** e ordenado por
**ondas incrementais**. O eixo estratégico é uma decisão travada do Founder (Q2/R-33): **não se
constrói as 10 estratégias em paralelo**. Constrói-se **D1 ORB-30 single-symbol fim-a-fim**
(DEF → backtest Python bruto → `.mq5` à mão → paridade PASS → otimizador sugere → 3 telas), o
Founder **testa o EA e o backtest via CAM** e dá o OK; só então as ondas seguintes (multi-símbolo
D3/LS, à vista V/S, cesta S1) são liberadas.

O trabalho é **majoritariamente recomposição + 5 peças novas/estendidas** (motor MVP-bruto
multi-série, DSL multi-símbolo/par, otimizador on-demand, EA executor multi-símbolo, camada de
paridade). O estado real (`/apps`) já contém quase todas as peças — o PLAN ancora cada TASK em
path real e marca o reuso.

**Referência de entrada (fonte de verdade):** [`SPEC-STRATEGYLAB-TRIAD.md`](./SPEC-STRATEGYLAB-TRIAD.md)
(APROVADA v1 — 35 regras R-01..R-35, 13 rotas REST, 3 tabelas novas, critérios de aceite focados
em D1 fim-a-fim). Subordinada a [`SCOPE`](./SCOPE-STRATEGYLAB-TRIAD.md) v0.7, [`ARCH`](./ARCH-STRATEGYLAB-TRIAD.md)
e [`ADR-SL-01/02/03`](./adrs/) (Accepted). Frontend incorpora [`DESIGN-REVIEW-FRONTEND.md`](./DESIGN-REVIEW-FRONTEND.md) (Andy).

**Princípio de processo:** sem estimativa em horas/dias/semanas (proibido). TDD First na lógica
pura (motor de backtest, compilador, métricas, comparador de paridade). Build/checks verdes
obrigatórios por bloco. Commit em `main` proibido. Sem secrets no EA/config/repo.

---

## 2. Avaliação P/M/G — consenso com Albert

| Campo | Valor |
|---|---|
| Classe (Albert, SPEC §7) | **G (Grande) — decomposta** |
| Avaliação do PLAN (Nico) | **CONCORDO — G mantido. Sem contestação.** |

**Rationale do consenso.** A SPEC classifica G por **tamanho/decomposição** (sem modificadores de
risco/segurança/arquitetura/release — Q8). Concordo integralmente: são **três módulos de produto**
(Strategy/RunTests/Experts) + **cinco peças novas/estendidas** (motor MVP-bruto multi-série, DSL
multi-símbolo/par, otimizador on-demand, EA executor multi-símbolo, camada de paridade) +
**três ambientes** (Python/FastAPI, React 19, MQL5/MT5) que precisam **concordar numericamente**,
sobre **10 estratégias** (5 multi-símbolo). Isso exige decomposição em TASKs e ordem incremental —
**é a definição de G**. As decisões estruturantes já estão fechadas (3 ADRs Accepted), o que
**não rebaixa** o G: reduz risco arquitetural, mas não o tamanho da execução.

**Por que não contestei para baixo (M).** O atenuante real é o alto reuso e o MVP-bruto, que
**encolhem o esforço por estratégia** — mas a **largura** (3 ambientes × 10 estratégias × paridade
bloqueante) é irredutível. Tentar rodar como M esconderia a necessidade de gate por salto de
complexidade (single → par → cesta) e abriria a porta do feature-factory que o Voltaire/Marty
alertaram. **G com ordem incremental é a forma honesta.** A disciplina anti-fábrica não está no
P/M/G — está na **ordem de execução** (§4): Onda 1 = D1 isolada; resto atrás de gate Founder.

> **Loop com Albert:** consenso imediato em **G**. Não houve contestação a abrir; o direito formal
> (loop ilimitado) não foi exercido por desnecessário.

---

## 3. TASKs decompostas por bloco

> **Convenção.** `T-XXX` · **Bloco pai** (BL-*) · **Saída esperada** · **Depende de** · **R-* cumpridas**
> · **TDD** (sim quando há lógica pura testável). Os blocos seguem a topologia do SCOPE §7 e do
> ARCH §3. Toda TASK respeita import-linter (feature→feature proibido; cross-feature só via
> `_shared/` ou evento) e o isolamento de execução (ordem só no MQL5 — R-26).
>
> **Marcação de onda.** 🟢 **[ONDA 1 — D1]** = subconjunto mínimo que entrega D1 ORB-30 fim-a-fim
> nos 3 ambientes + paridade + otimizador + 3 telas. As demais ondas (§4) ficam **atrás do gate
> "Founder validou D1"** e estão em granularidade maior (refina quando o Founder liberar).

---

### BL-DADOS — Persistência / domínio (DB + Python)

Reuso de `research_bars`/`research_ticks` (ingestão canônica, provenance — R-09); novo **só** de
domínio de estratégia (par como unidade). Promoção do kernel acontece aqui (pré-requisito de
import-linter para `strategy_lab` consumir `bars.py`).

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-001** | **Promover `bars.py` → `_shared/research_kernel/`** | `bars.py` (função pura M1→TF, fuso SP) movido de `features/research/leadlag/` para `_shared/research_kernel/`; imports atualizados em `research/leadlag`; import-linter verde; testes existentes de `bars` passam no novo local. | — | R-13, R-20 | sim (reusa testes existentes) |
| 🟢 **T-002** | **Promover `validation.py` → `_shared/research_kernel/`** (junto, já que o optimizer o consome direto) | `validation.py` (DSR/WF/no-cliff) em `_shared/research_kernel/`; consumidores atualizados; import-linter verde. | T-001 | R-07, R-18, R-20 | sim (reusa testes existentes) |
| 🟢 **T-003** | **Scaffold da feature `features/strategy_lab/`** | Pasta nova com `README.md` (contrato), `__init__.py`, esqueleto de `domain.py`/`repository.py`/`service.py`/`routes.py`; registrada no app FastAPI; import-linter reconhece o slice. | — | R-12 | não (scaffold) |
| 🟢 **T-004** | **Modelo de domínio `strategy_param_set`** | Tabela + modelo: `id, strategy_id, params(jsonb), origin(manual\|suggested), optimization_id(null), created_at`; migração. | T-003 | R-04, R-08 | sim (repo round-trip) |
| 🟢 **T-005** | **`backtest_run` estendido (mode=gross, symbols[], unit)** | Modelo/migração de `backtest_run` na feature `strategy_lab` com `symbols text[]`, `unit enum(single\|pair\|basket)`, `mode const 'gross'`, `metrics jsonb`. **Não toca** `features/backtest/domain.py` (não-regressão R-12). | T-003 | R-10, R-11, R-12 | sim (repo round-trip) |
| 🟢 **T-006** | **`backtest_leg_trade` (par como unidade, leg+pair_id)** | Tabela/modelo: `id, run_id, pair_id, leg(long\|short), symbol, ts/price entry/exit, qty, exit_reason, pnl_bruto, volume_financeiro`. `single` = par de uma perna. Agregação por `pair_id` é cálculo, não entidade. | T-005 | R-19, R-35 | sim (agregação single/pair) |
| **T-007** | **Validação de provenance na config de backtest** (símbolo sem dados ⇒ erro explícito) | Guarda que recusa rodar quando `research_*` não tem a série/período (R-09; caso-limite §6). Erro tipado, não resultado vazio silencioso. | T-005 | R-09 | sim |

---

### BL-CONTRATO — DEF comum + DSL multi-símbolo (Python)

A DEF comum é a fonte humana única (versionada em `/project`); o lado Python a compila reusando
`strategies/dsl`. **Sem codegen** (R-02, ADR-SL-01).

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-010** | **Formato da DEF comum (`strategy_def`)** | Modelo de domínio + parser do YAML da DEF (SPEC §4.4): `strategy, family, symbols[], unit, timeframe, session(tz=America/Sao_Paulo, open/close, flat_at_close), indicators, signal(long/short, fill=next-bar-open, intrabar=worst-case, gap=honest), stop/target, sizing, seed`. Subset MVP sem C7/C8. | T-003 | R-02, R-03 | sim |
| 🟢 **T-011** | **DEF de D1 ORB-30 (single) versionada em `/project`** | Arquivo DEF de `D1_orb30_win` (family D, symbols [WIN], unit single, TF, sessão SP, indicador opening_range 30min, sinais ORB, stop/alvo mecânicos, seed) em `/project/tcam/.../defs/`. | T-010 | R-03, R-34 | não (artefato) |
| 🟢 **T-012** | **Compilador Python da DEF (single) — reusa `strategies/dsl`** | Adapta `strategies/dsl/{parser,compiler}` (AST whitelist, sem eval) para compilar a DEF em estratégia executável **single-symbol**; D1 ORB-30 derivada de `orb_60m_win.py` adaptada para ORB-**30**. | T-010, T-011 | R-02, R-34 | sim |
| **T-013** | **Extensão DSL multi-símbolo / par como unidade** | Gramática para `unit: pair\|basket`: `symbols[]`, `spread`/`beta`, `z_entry/z_exit/z_stop`, `leg_execution: atomic` (C14). Compila spread/z-score sobre N séries. **(Onda multi-símbolo — não-D1.)** | T-012 | R-03, R-19 | sim |

---

### BL-BACKTEST — Motor MVP-bruto multi-série (Python)

Motor **novo** em `strategy_lab/backtest_engine.py`, **não importa `_shared.risk`** (R-12,
ADR-SL-02). Caminho Risk-acoplado de `features/backtest/` **intocado**.

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-020** | **Núcleo do motor MVP-bruto single-symbol** | `backtest_engine.py`: ordem de avaliação fixa por barra fechada (atualiza indicadores → **saídas** → **entradas** → filtros — C3), fill `next-bar-open` (C4), intrabar pior-caso (C5), gap honesto (C6), single-position por estratégia (R-15). `P&L = pontos × valor_do_ponto × qtd`, **bruto** (R-11). Indicadores **on-the-fly** das barras canônicas (R-16). | T-001, T-012, T-005 | R-11, R-12, R-15, R-16 | **sim (First)** |
| 🟢 **T-021** | **Ledger de trades canônico (schema único)** | Emissão do ledger `trade_id, pair_id, leg, symbol, lado, ts/preço entrada/saída, qtd, motivo_saida, pnl_bruto, volume_financeiro` (SPEC §4.5). Sem custo/IR/pnl_liquido. É o contrato consumido pela paridade. | T-006, T-020 | R-17, R-35 | sim |
| 🟢 **T-022** | **Rotina única de métricas brutas** | Função Python **única** sobre o ledger: WR, expectância bruta, profit factor, nº trades, max drawdown, curva de equity bruta. **A mesma** rotina consome o ledger do EA (R-26) — elimina divergência de cálculo. | T-021 | R-17 | **sim (First)** |
| 🟢 **T-023** | **Walk-forward OOS (reuso)** | Liga `walk_forward.py` + `validation.py` (`_shared/research_kernel`) ao engine para OOS sob demanda. | T-002, T-020 | R-18 | sim |
| **T-024** | **Multi-série: leitura e sincronização de N séries por timestamp** | Motor lê N séries de `research_*`, deriva barras canônicas idênticas e **sincroniza por timestamp** (mesma barra `[t,t+Δ)` carimbada em `t`, fuso SP). **Barra ausente num símbolo do par ⇒ não opera a perna; sem meia-posição** (R-14). **(Onda multi-símbolo — não-D1.)** | T-020, T-013 | R-10, R-13, R-14 | sim |
| **T-025** | **Contabilização par como unidade** | Agrega gain/loss do spread por `pair_id`; pernas para auditoria/UI; "perna separada" só se o Founder pedir. **(Onda multi-símbolo.)** | T-024 | R-19 | sim |

---

### BL-OTIM — Otimizador on-demand (Python)

On-demand, **sugere não aplica** (R-05, R-08). Rota distinta de backtest (R-05).

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-030** | **Otimizador grid + random** | `optimizer.py`: varredura grid (espaço pequeno determinístico) + random (espaço maior) sobre o engine. **Só roda quando acionado** (R-05); backtest e otimização são ações distintas. | T-020 | R-05, R-06 | sim |
| 🟢 **T-031** | **Guard-rail anti-overfit (DSR + WF OOS + no-cliff)** | Todo conjunto sugerido passa por `validation.py`: **DSR penalizado pelo nº de combinações testadas** + walk-forward OOS + checagem no-cliff. Reporta **nº de tentativas + robustez ao redor do ótimo** — nunca "o pico" sem contexto. **Recusa sugerir** se dados OOS insuficientes (caso-limite §6). | T-030, T-002, T-023 | R-06, R-07 | **sim (First)** |
| 🟢 **T-032** | **Sugestão como `param_set` marcado `suggested` (sem auto-apply)** | Resultado gravado como `strategy_param_set origin=suggested` ligado ao `optimization_id`; **Founder decide** adoção via `PUT .../params` (R-08). Sem auto-apply. | T-031, T-004 | R-08 | sim |

---

### BL-EA — EA executor MQL5 multi-símbolo (MQL5 / MT5) · **sec (Kevin no bloco)**

EA **novo**, escrito à mão seguindo a DEF como especificação (R-21, dupla implementação
deliberada). Execução **exclusiva no MQL5**; backend só orquestra/observa (R-26). **Kevin entra
neste bloco** (guard-rail DEMO — marcador `sec` da SPEC §8).

> **⚙️ Ajuste de diretriz — dois EAs entregues na Onda 1 (ADR-SL-04, 2026-06-03).** O bloco
> materializou **DOIS `.mq5`** para a D1, em vez de um:
> - **`cam_d1_orb30.mq5` — gravador (T-041/T-042):** roda a lógica D1 e **exporta o ledger**
>   (pior-caso canônico) **sem ordem** — é o lado MQL5 da **paridade** (BL-PARIDADE). Fora da
>   allowlist `lint_mql5`.
> - **`cam_d1_orb30_exec.mq5` — executor (T-045, NOVO):** **opera de fato** a mercado com SL/TP
>   (`CTrade`), **visível no Strategy Tester** — atende o pedido do Founder de "ver a estratégia
>   operando". Estratégia pura, **sem Risk Engine** nesta onda. Dentro da allowlist (testado).
>
> A paridade (BL-PARIDADE) é checada contra o **gravador**; o executor entrega validação
> visual. T-040 (guard-rail DEMO duplo) vale para **os dois**.

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-040** | **Scaffold do EA + guard-rail DEMO duplo (ambos os EAs)** | Novos `.mq5` em `apps/cam-cockpit/mql5/experts/` (distintos de `cam_bridge`). **Guard-rail duplo (R-24, sec):** (1) `input` apontando conta/servidor DEMO; (2) checagem runtime `AccountInfoInteger(ACCOUNT_TRADE_MODE)` — se ≠ DEMO, **recusa operar** e loga. Sem caminho de promoção silenciosa a real. **Kevin valida.** | — | R-21, R-24 | n/a (MQL5; teste via Strategy Tester) |
| 🟢 **T-041** | **Lógica D1 ORB-30 no EA gravador (single-symbol)** | `cam_d1_orb30.mq5` implementa **à mão** a lógica D1 conforme a DEF (T-011): opening range 30min, entrada na quebra, stop/alvo mecânicos, flat at close, sessão SP. **Sem ordem** (gravador). | T-040, T-011 | R-21, R-23 | n/a |
| 🟢 **T-042** | **Export do ledger do EA no schema canônico** | EA gravador exporta ledger de trades (CSV) no schema único (SPEC §4.5) para a paridade consumir (R-27). | T-041, T-021 | R-27, R-35 | n/a |
| 🟢 **T-045** | **EA executor D1 (opera de fato) — ADR-SL-04** | `cam_d1_orb30_exec.mq5`: mesma lógica D1, mas **envia ordem a mercado** com SL/TP (`CTrade`), flat na sessão, visível no Strategy Tester. **Sem Risk Engine** (estratégia pura, decisão do Founder). Entra na **allowlist `lint_mql5`** (junto de `cam_risk_mirror`); guard-rail DEMO duplo (T-040). Testes do lint cobrem allowlist. | T-040, T-041 | R-21, R-24 | sim (lint allowlist) |
| 🟢 **T-043** | **Orquestração/observação via `mt5_integration` (sem feature→feature)** | EA disparado/observado por **evento** ou endpoint da própria `mt5_integration` (`ea_dispatcher`/`multi_ea_manager`/`fill_subscriber`). `strategy_lab` **não importa** `mt5_integration` (R-26). Mecanismo fino (evento vs API interna) decidido no CODE dentro do princípio. | T-040 | R-26 | sim (lado Python da orquestração) |
| **T-044** | **Execução atômica das pernas (par) + short mecânico** | EA monta posição de par só com **as duas pernas** (book aceitável); se uma não preenche, **não monta meia-posição** (R-22); saída das duas no mesmo evento. Perna short mecânica (`SELL`), **sem modelar aluguel** (R-25). **(Onda multi-símbolo — DEMO ao vivo, R-23.)** | T-040, T-024 | R-22, R-23, R-25 | n/a |

---

### BL-PARIDADE — Comparador Py↔EA (Python) — **gate bloqueante**

Dupla checagem independente (R-28). PASS paga a dupla implementação (R-30). FAIL → BUG (R-31).

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-050** | **Comparador trade-a-trade (alinhado por barra de sinal)** | `parity.py`: alinha ledger Python (T-021) × ledger EA (T-042) por barra de sinal; compara lado-a-lado. Reusa a rotina única de métricas (T-022) nos dois lados. | T-021, T-042, T-022 | R-28 | **sim (First)** |
| 🟢 **T-051** | **Critério PASS + relatório PASS/FAIL** | PASS = **100% sinais coincidem (mesma barra/lado) + preço entrada/saída ≤1 tick + volume financeiro idêntico + qtd idêntica + motivo de saída idêntico** (R-29, Q6). Relatório trade-a-trade + métricas lado a lado + **veredito**; FAIL aponta causa C1–C14 (ordem do pipeline EDGE-CONTRATO §5.5). | T-050 | R-29, R-31 | sim |
| 🟢 **T-052** | **Gate bloqueante + abertura de BUG no FAIL** | Mexeu num lado (Python ou `.mq5`) ⇒ roda paridade; **FAIL bloqueia promoção** (R-30). FAIL **abre BUG** (`teczi-bug-fix`); proibido "tunar" um lado para casar sem entender a causa (R-31). Pré-condição C13 (mesmo dataset/DEF) checada antes das métricas (caso-limite §6). | T-051 | R-30, R-31 | sim |
| **T-053** | **Paridade do par (rebaixe para lógica de sinal onde o book de DEMO não é reproduzível)** | Para D3/LS em DEMO ao vivo, onde a reprodutibilidade exata do book não existe, a paridade pode rebaixar de trade-a-trade-de-preço para **paridade de lógica de sinal** (mesmos pontos de entrada/saída) — **registrar explicitamente no run** (R-31, ADR-SL-03 §2.2). **(Onda multi-símbolo.)** | T-051, T-044 | R-31 | sim |

---

### BL-FRONT — 3 telas React + painel de Paridade (React 19 + MUI) · **incorpora Andy**

Diretrizes do `DESIGN-REVIEW-FRONTEND` **são critério de aceite visual**: 1 manchete por tela,
progressive disclosure, conclusão antes de evidência, zero jargão na superfície, cortar→agrupar→mostrar.
Reusa padrão `inspetor`/`quant-lab` (react-query, MUI, lightweight-charts/SVG). As 3 telas
**nascem simples**.

| ID | TASK | Saída esperada | Depende de | R-* | TDD |
|---|---|---|---|---|---|
| 🟢 **T-060** | **Design system mínimo (Andy §5)** | 4 componentes-padrão reutilizáveis: `PageHeader` (título seco + ações, sem subtítulo-prosa), `PageContainer` (margem única), `StatStrip` (3–5 métricas-chave), `DetailDisclosure` (accordion fechado para detalhe/tabela longa/jargão). Tema `theme.ts` já existe — falta só composição. | — | R-32 (chip "bruto") | sim (render/snapshot leves) |
| 🟢 **T-061** | **Tela Assets Strategy (manchete = lista de cards)** | Lista das 10 estratégias (família, símbolo(s), `unit`, **1 chip de status**). Multi-símbolo = "par"/"cesta" (uma palavra). Clique → **drawer** de detalhe com DEF + params + `param_set` ativo; avançados em accordion. Rotas 1–4. **No D1: só a lista + card D1 + drawer de params funcionam.** | T-004, T-060 | R-01, R-04 | sim |
| 🟢 **T-062** | **Otimizador on-demand na UI (1 recomendação + selo de robustez)** | Botão "Otimizar" (sóbrio). Dispara rota 9 → mostra **1 recomendação** (ex.: "sugerido: janela 20, stop 1.5×ATR") + **selo de robustez** ("testou 240 combinações · OOS ok · superfície chata") como **3 chips** — **não** a grade inteira (varredura atrás de "ver varredura"). Founder adota via rota 4; sem auto-apply. Rotas 9–10. | T-061, T-032 | R-05, R-07, R-08 | sim |
| 🟢 **T-063** | **Tela Assets RunTests (manchete = curva de equity)** | Config compacta em 1 linha + botão "rodar" (rota 5). **Manchete: curva de equity (bruta)** dominando a dobra (rota 7). Apoio: **4–5 métricas-chave como `StatStrip`** (WR, PF, nº trades, DD). **Trades e walk-forward em `DetailDisclosure` fechado** (rota 8). **Chip `bruto`+tooltip** ("sem custo/IR — não confirma edge líquido") persistente — a trava de honestidade do MVP **não vira parágrafo** (R-32). Multi-símbolo: 1 linha por trade-par; pernas no expand. Rotas 5–8. | T-022, T-060 | R-11, R-17, R-32 | sim |
| 🟢 **T-064** | **Painel de Paridade (manchete = veredito PASS/FAIL)** | Veredito **PASS/FAIL** grande e legível; trade-a-trade e métricas lado a lado em `DetailDisclosure`; causa C1–C14 no FAIL. Rotas 11–12. | T-051, T-060 | R-28, R-29, R-31 | sim |
| 🟢 **T-065** | **Tela Assets Experts (manchete = lista de robôs + selo DEMO)** | Lista de robôs MT5 com **status grande** (rodando/parado) e **selo DEMO sempre visível** (guard-rail vira affordance — sobriedade máxima, cor forte só em DEMO/parar). Logs/fills on-click. Reusa `robot-orchestrator`/`ea-control`. Start/stop = rota 13. | T-043, T-060 | R-21, R-24, R-26 | sim |

---

## 4. Ordem de execução incremental — Ondas

> **Decisão travada do Founder (Q2/R-33):** D1 ORB-30 single-symbol é o **vertical slice de prova**.
> Não planejar as 10 em paralelo. **Não começar a próxima onda antes de a anterior bater paridade.**

### 🟢 ONDA 1 — D1 ORB-30 single-symbol fim-a-fim (foco do CODE AGORA)

O subconjunto mínimo que entrega D1 nos **3 ambientes + paridade + otimizador + 3 telas**. É o que
o Founder vai **testar via CAM** (EA no Strategy Tester + backtest Python) antes de liberar o resto.

**Sequência sugerida (respeitando dependências):**

```
Fundação      T-001 → T-002 → T-003 → T-004 → T-005 → T-006
Contrato D1   T-010 → T-011 → T-012
Backtest D1   T-020 → T-021 → T-022 → T-023
Otimizador    T-030 → T-031 → T-032
EA D1 (sec)   T-040 → T-041 → T-042 → T-045 (executor) → T-043
Paridade      T-050 → T-051 → T-052
Frontend      T-060 → T-061 → T-063 → T-064 → T-062 → T-065
```

**TASKs da Onda 1 (lista fechada que o CODE ataca primeiro):**
`T-001, T-002, T-003, T-004, T-005, T-006, T-010, T-011, T-012, T-020, T-021, T-022, T-023,
T-030, T-031, T-032, T-040, T-041, T-042, T-045, T-043, T-050, T-051, T-052, T-060, T-061, T-062,
T-063, T-064, T-065`.

**Critério de fechamento da Onda 1 (= "Go de D1" da SPEC §10):**
1. Backtest Python de D1+WIN produz equity bruta + ledger + métricas brutas (R-11).
2. EA de D1 roda no Strategy Tester e exporta ledger no schema canônico (R-27).
3. **Paridade PASS** sobre mesmo dataset (100% sinais + ≤1 tick + volume + qtd + motivo — R-29).
4. Otimizador sugere `param_set` + nº de tentativas + robustez no-cliff; não aplica (R-07/R-08).
5. Rótulo/chip **"BRUTO — sem custo/IR"** presente em toda tela de resultado (R-32).
6. Guard-rail DEMO efetivo; isolamento mantido (sem caminho de ordem no backend); sem secrets.
7. Não-regressão: `features/backtest/` (Risk-acoplado) **intocado** (R-12).

> ⛔ **GATE FOUNDER — "Founder validou D1".** Carlos testa o EA e o backtest via CAM e dá o OK.
> **As ondas seguintes não começam antes deste gate.** (Q2/R-33.)

### Ondas seguintes — atrás do gate (granularidade maior; refina quando o Founder liberar)

- **ONDA 2 — Par (D3, LS1) — multi-símbolo 2 pernas.** Habilita: `T-013` (DSL pair/spread/z-score),
  `T-024` (multi-série, sincronização por timestamp, R-14), `T-025` (par como unidade), `T-044`
  (EA execução atômica + short mecânico em **DEMO ao vivo**, R-23), `T-053` (paridade do par —
  lógica de sinal onde o book não é reproduzível). Prova o salto **single → par**.
- **ONDA 3 — Demais single à vista/derivativo (D2, V1, V2, S2).** Repete o vertical de D1 com DEFs
  novas; reusa T-012/T-020/T-041 já provados. Pouca peça nova — sobretudo DEFs + `.mq5` à mão.
- **ONDA 4 — Cesta/ranking (S1) — multi-símbolo por ranking.** Modelo distinto do par (N símbolos,
  rebalance diário, DEMO ao vivo). Maior peça nova das ondas; refina TASKs ao liberar.
- **ONDA 5 — LS swing (LS2, LS3).** Pares cointegração/ON×PN; reusa Onda 2. **Atenção redobrada**
  (R-32): LS parecem ótimas no bruto (refém do custo) — esperado e enganoso.

> A ordem fina das Ondas 2–5 é refinada **no momento da liberação** de cada uma pelo Founder. O
> compromisso de disciplina (anti-feature-factory) é: **uma estratégia bate paridade antes de a
> próxima começar.**

---

## 5. Dependências externas · riscos de execução · reuso aplicado

### 5.1 Dependências externas
- **MetaTrader 5 + Strategy Tester** (Windows 11) com **histórico de WIN** disponível para D1; bridge
  ZeroMQ 127.0.0.1 já operacional (`RUNBOOK-WINDOWS.md`). EA D1 single-symbol = caminho mais simples
  (ADR-SL-03: single no tester).
- **`research_*` populado** com a série WIN do período de teste (provenance — R-09); sem dados, T-007
  recusa rodar.
- **Conta DEMO MT5** configurada (guard-rail T-040). **Sem capital real neste ciclo.**

### 5.2 Riscos de execução (e mitigação no plano)
| Risco | Mitigação no PLAN |
|---|---|
| **Divergência silenciosa Py↔EA** (dupla implementação) | Paridade é **gate bloqueante** (T-052); rotina de métricas **única** nos dois lados (T-022); FAIL→BUG, proibido tunar (R-31). |
| **Overfit do otimizador** | Guard-rail DSR-por-tentativas + WF OOS + no-cliff **obrigatório** (T-031); sugere-não-aplica (T-032); on-demand (T-030). |
| **Falsa confiança do "bruto"** (LS brilham e enganam) | Chip `bruto`+tooltip em toda tela (T-063, R-32); atenção redobrada nas LS na Onda 5. |
| **Multi-símbolo no Strategy Tester** (ponto duro) | **Fora da Onda 1** (D1 é single). Resolvido por ADR-SL-03: par valida em **DEMO ao vivo** (T-044), não no tester. |
| **Import-linter (feature→feature)** | Promoção de kernel **antes** do consumo (T-001/T-002); `strategy_lab` **não** importa `mt5_integration` — orquestra por evento/endpoint (T-043). |
| **Regressão no backtest Risk-acoplado** | Motor MVP-bruto é **feature nova** que **não importa `_shared.risk`** (T-020); `features/backtest/` intocado (R-12). |
| **Salto não-intencional p/ conta real** | Guard-rail DEMO duplo (T-040, sec/Kevin); live real **para tudo e aciona SEC-GOV** antes (R-24). |
| **Frontend repetir "pilha de Papers"** | DS mínimo (T-060) + diretrizes Andy como critério de aceite; 3+ tabelas na vertical = refatorar. |

### 5.3 Reuso aplicado (estado real `/apps` — confirmado)
| Peça | Origem real | Ação no PLAN |
|---|---|---|
| Barra canônica C1 | `features/research/leadlag/bars.py` | **Promover** → `_shared/research_kernel/` (T-001) |
| Anti-overfit | `features/research/leadlag/validation.py` | **Promover** + reusar no otimizador (T-002, T-031) |
| DSL declarativa | `features/strategies/dsl/{parser,compiler}.py` | **Reusar** como compilador da DEF; estender p/ par (T-012, T-013) |
| Estratégia-exemplo | `features/strategies/strategies/orb_60m_win.py` | **Adaptar** p/ D1 ORB-30 (T-011/T-012) |
| Motor backtest | `features/backtest/{simulator,walk_forward}.py` + `domain.py` | **Derivar** MVP-bruto em feature nova; **não tocar** Risk-acoplado (T-020, T-023) |
| Ingestão tick/candle | `research_bars`/`research_ticks` | **Reusar** (T-005, T-007) |
| Orquestração EA | `features/mt5_integration/{ea_dispatcher,multi_ea_manager,fill_subscriber}` | **Reusar** p/ orquestrar/observar (T-043) |
| EA base | `mql5/experts/{cam_bridge,cam_risk_mirror}.mq5` | **Referência**; executor é **novo** (T-040) |
| Padrão UI | `features/{quant-lab,inspetor}` | **Reusar** padrão; DS mínimo Andy (T-060) |

---

## 6. letscode

| Campo | Valor |
|---|---|
| **`letscode`** | **`true`** ✅ |
| Autorizado por | Founder (2026-06-03) — "autorizou começar o CODE em seguida" |
| Escopo liberado | **Onda 1 — D1 ORB-30 fim-a-fim** (TASKs listadas em §4). Ondas 2–5 atrás do gate "Founder validou D1". |
| Lead do CODE | Nikola (+ Linus intrabloco sempre; **+ Kevin no BL-EA** — marcador `sec` da SPEC §8) |
| Guard-rails de CODE | build/checks verdes por bloco · TDD First na lógica pura · import-linter verde · **commit em `main` proibido** · **sem secrets** no EA/config/repo · execução só no MQL5 (R-26) |

> **Gate final aceso.** O CODE pode começar pela Onda 1. O **fechamento da Onda 1** (Go de D1, §4)
> é o ponto de validação do Founder antes de qualquer onda seguinte.

---

## 7. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-06-03 | PLAN único da tríade — consenso em **G** (sem contestação a Albert); TASKs T-001..T-065 por bloco (BL-DADOS→FRONT); ondas incrementais com **Onda 1 = D1 fim-a-fim**; diretrizes Andy no BL-FRONT; `letscode=true`. | Founder |

---

> PLAN / Nico · TCaM / produto · Constituição descomissionada · MVP de valores brutos · G decomposta ·
> ordem incremental D1-first (gate Founder entre ondas) · sem codegen (dupla implementação, paridade
> como gate) · frontend simples desde o início (Andy) · `letscode=true` · 2026-06-03 · v1.
> **Próxima fase: CODE (Nikola +Linus, +Kevin no EA) — atacar a Onda 1.**

---
template: SPEC
phase: SPEC
status: APROVADO v1 — Founder ratificou (2026-06-03) → PLAN (Nico)
produto: TCaM (cam-cockpit)
id: SPEC-STRATEGYLAB-TRIAD
demanda: STRATEGYLAB-v0.6
data: 2026-06-03
lead: Albert
co: Kevin (marcador sec/qa-sec — guard-rail DEMO no EA)
aprovador: Founder
vinculacao: >
  SCOPE-STRATEGYLAB-TRIAD v0.7 (APROVADO) · ARCH-STRATEGYLAB-TRIAD ·
  ADR-SL-01 · ADR-SL-02 · ADR-SL-03 (todos Accepted) ·
  EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5 · CATALOGO-12-ESTRATEGIAS-ELEITAS
modo: >
  Produto TCaM. Constituição DESCOMISSIONADA — sem Risk Engine soberano, sem Arts.,
  sem trava de capital. Permanece o RIGOR de engenharia (paridade, anti-data-snooping,
  isolamento de execução) como boa prática, não como amarra constitucional. MVP de
  VALORES BRUTOS (sem custo/IR/slippage). 10 estratégias no escopo; critérios de aceite
  focam D1 ORB-30 fim-a-fim (demais escalam após validação do Founder — Q2).
---

# SPEC — StrategyLab do CaM · Tríade Assets Strategy + RunTests + Experts

> **Lead:** Albert (SPEC) · **Co:** Kevin (sec/qa-sec) · **Aprovador:** Founder
> **Status:** Draft v1 (aguarda gate)

---

## 1. Resumo

Especifica a tríade **Assets Strategy + Assets RunTests + Assets Experts**: gestão das 10 estratégias eleitas com otimizador on-demand, backtest matemático Python MVP-**bruto** multi-série, EA executor MQL5 multi-símbolo em DEMO, e a camada de **paridade Py↔EA** (dupla checagem como gate bloqueante a cada alteração) — começando por **D1 ORB-30 single-symbol fim-a-fim**.

## 2. Referências de entrada

- **SCOPE:** [`SCOPE-STRATEGYLAB-TRIAD.md`](./SCOPE-STRATEGYLAB-TRIAD.md) — APROVADO v0.7 (Founder, 2026-06-03); Q1–Q10 respondidas.
- **ARCH (DAS-lite):** [`ARCH-STRATEGYLAB-TRIAD.md`](./ARCH-STRATEGYLAB-TRIAD.md) — topologia, feature nova `strategy_lab`, promoção de kernel.
- **ADR-SL-01** [`adrs/ADR-SL-01-definicao-comum-dupla-implementacao.md`](./adrs/ADR-SL-01-definicao-comum-dupla-implementacao.md) — Accepted. DEF comum + **dupla implementação Python+MQL5 sem codegen**; paridade = detector de dessincronização; `unit: single|pair|basket`.
- **ADR-SL-02** [`adrs/ADR-SL-02-persistencia-backtest-mvp-bruto.md`](./adrs/ADR-SL-02-persistencia-backtest-mvp-bruto.md) — Accepted. Reuso `research_*`; novo de domínio (`param_set` + `leg_trade` par-como-unidade); motor MVP-bruto desacoplado de Risk/IR; multi-série; indicadores on-the-fly; promover `bars.py`/`validation.py` → `_shared/research_kernel`.
- **ADR-SL-03** [`adrs/ADR-SL-03-execucao-multisimbolo-ea-mt5.md`](./adrs/ADR-SL-03-execucao-multisimbolo-ea-mt5.md) — Accepted. Execução híbrida: single no Strategy Tester / par-cesta em DEMO ao vivo; execução atômica; short mecânico; guard-rail DEMO.
- **EDGE-CONTRATO:** [`EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md`](./EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md) — C1–C14, E1–E8. No MVP: subconjunto **sem C7/C8** (custo/IR).
- **CATÁLOGO:** [`CATALOGO-12-ESTRATEGIAS-ELEITAS.md`](./CATALOGO-12-ESTRATEGIAS-ELEITAS.md) — lógica/parâmetros das 10 (D1 ORB-30 = primeira a implementar).
- **Estado real reaproveitável:** `apps/cam-cockpit/backend/cam/features/{strategies/dsl,backtest,research/leadlag,mt5_integration}` · `apps/cam-cockpit/mql5/experts/`.

---

## 3. Regras de negócio

> Numeradas `R-*`. Agrupadas por frente (Strategy / RunTests / Experts / Paridade / Anti-falsa-confiança / Transversais). Toda regra respeita as decisões travadas do Founder (Q1–Q10) — **não reabrir**.

### 3.1 Assets Strategy (gestão de estratégias + otimizador on-demand)

- **R-01.** O sistema lista e gere as **10 estratégias** do escopo: D1, D2, D3, V1, V2, S1, S2, LS1, LS2, LS3. **F1 e H1 estão OUT** (buy&hold sem EA). Cada estratégia exibe família, símbolo(s) e `unit` (`single|pair|basket`). Estratégia multi-símbolo (D3, LS1, LS2, LS3) mostra **o par como unidade**; S1 mostra a **cesta/ranking**.
- **R-02.** Cada estratégia tem uma **DEF comum** (ADR-SL-01 §2.2) — artefato declarativo **legível**, versionado em `/project`, que descreve **parâmetros + regras** num formato único (ver §4.4). A DEF é a **fonte humana única**: o lado Python a compila; o lado MQL5 a usa como especificação para escrita à mão. **Não há codegen** (Q3).
- **R-03.** A DEF declara, no mínimo (subconjunto MVP de C1–C14, **sem C7/C8**): `strategy`, `family`, `symbols[]`, `unit`, `timeframe`, `session` (tz=America/Sao_Paulo, open/close, flat_at_close), `indicators`, `signal` (long/short, `fill: next-bar-open` C4, `intrabar: worst-case` C5, `gap: honest` C6), `stop`/`target` (C10), `sizing` (C9 determinístico, rounding), `seed` (C12). Para `unit: pair|basket`: `spread`/`beta`, `z_entry`/`z_exit`/`z_stop`, `leg_execution: atomic` (C14).
- **R-04.** O usuário **visualiza e edita** os parâmetros de uma estratégia (ex.: janela ORB, stop, alvo, β do spread, z-score de entrada/saída). Toda edição produz/atualiza um `param_set` versionado, ligado à DEF.
- **R-05.** O **otimizador é on-demand** (Q9): roda **somente** quando o usuário aciona explicitamente; **nunca** automático em todo backtest. Backtest e otimização são ações distintas.
- **R-06.** Os métodos de otimização do MVP são **grid search** + **random search**, com **walk-forward** como validação do candidato sugerido. Otimização multi-objetivo, genética e bayesiana são **OUT** (Later).
- **R-07.** **Guard-rail anti-overfit obrigatório:** todo conjunto sugerido passa por `validation.py` (DSR penalizado pelo nº de combinações testadas + walk-forward OOS + checagem **no-cliff**). O otimizador **reporta o nº de tentativas e a robustez ao redor do ótimo** — nunca entrega "o pico do backtest" sem esse contexto.
- **R-08.** O otimizador **SUGERE, não aplica** (Q9). Um conjunto sugerido é gravado como `param_set` marcado `suggested`; **o Founder decide** se adota. **Sem auto-apply.**

### 3.2 Assets RunTests (backtest matemático Python MVP-bruto, multi-série)

- **R-09.** A ingestão de dados **reusa `research_bars`/`research_ticks`** (Q4) — multi-símbolo, com **provenance** (ADR-SL-02 §2.1). **Nenhuma** tabela `strategy_bars`/`strategy_ticks` é criada. **Dado sem origem rastreável não entra**, mesmo no MVP.
- **R-10.** O backtest é configurável sobre **uma ou mais séries** (ativo(s) + período + TF). Para multi-símbolo (D3, LS1, LS2, LS3, S1), o config aceita **N símbolos / o par** como unidade de configuração.
- **R-11.** O motor de backtest opera em modo **MVP-VALORES-BRUTOS**: simula **entrada, saída, gain, loss e volume financeiro bruto**. `P&L = pontos × valor_do_ponto × qtd`, **bruto, sem dedução**. **NÃO** aplica corretagem, emolumentos, slippage nem IR (decisão §3 do SCOPE). O trade bruto reporta **apenas** `pnl_bruto` e `volume_financeiro` — `tax_provisioned`/`result_net` do domínio antigo **não são usados** no caminho bruto.
- **R-12.** O motor vive na feature nova **`features/strategy_lab/backtest_engine.py`** e **não importa `_shared.risk`** (ADR-SL-02 §2.3). O caminho Risk-acoplado de `features/backtest/` permanece **intocado** (não-regressão).
- **R-13.** A barra é a **canônica de `bars.py`** (M1→TF determinística, C1), carimbada pelo **timestamp de abertura** no fuso **America/Sao_Paulo** (C2/Q7), **idêntica para todos os símbolos de um par**. Sem default de fuso do broker/MT5.
- **R-14.** Multi-série: o motor lê N séries de `research_*`, deriva barras canônicas e **sincroniza por timestamp** (mesma barra `[t, t+Δ)` carimbada em `t`). **Barra ausente num símbolo do par num timestamp** ⇒ **não opera a perna naquele bar; sem meia-posição** (regra explícita, R-22/R-23 no EA espelham).
- **R-15.** A ordem de avaliação por barra fechada é fixa (C3): atualizar indicadores → checar **saídas** → checar **entradas** → filtros. **Saída sempre antes de entrada.** Fill em `next-bar-open` (C4); intrabar pior-caso (C5); gap honesto (C6). **Single-position por estratégia/par** no MVP (uma posição por vez).
- **R-15b.** **SL/TP estáticos (decisão do Founder, 2026-06-04 — D1).** Além do modo "range" (stop no extremo do OR, alvo `target_r × range`), a estratégia aceita **SL e TP fixos em pontos** (`stop_points`/`target_points`), **relativos ao preço de ENTRADA** (não ao range). **Resolvidos no fill** (a entrada só é conhecida em `t+1`): `long → SL = entrada − stop_points`, `TP = entrada + target_points`; `short` espelhado. Modo estático ativo quando **`stop_points > 0`**; **`target_points` é OPCIONAL** (0 = sem TP fixo — ver R-15c). **Os mesmos parâmetros valem em Python (backtest), no EA gravador (paridade) e no EA executor** — é parâmetro de paridade. Para a **D1 do produto este é o modo padrão**; o range fica como fallback.
- **R-15d.** **Gate de regime na ENTRADA (decisão do Founder, 2026-06-04 — D1).** Filtros de entrada **simples e espelháveis no EA** (proxy de regime — o Markov do overlay é inviável em MQL5 e quebraria paridade). Dois, ambos opcionais (0 = off): **`trend_filter_bars`** — só entra A FAVOR da tendência (`long` se `close > close[N barras atrás]`; `short` espelhado); **`min_or_points`** — só opera o dia se o range do OR ≥ valor (suprime chop de baixa volatilidade). **Provado no WINM26 (6 meses):** `trend_filter_bars=400` (~1 pregão) reduz maxDD de −778 p/ −513 (−34%) e eleva a consistência walk-forward de 56% p/ 78%, sacrificando ~15% do lucro bruto. **Default da D1 do produto:** `trend_filter_bars=400`. É **parâmetro de paridade** (idêntico nos três lados). Relação com risco (conselho): drawdown é função de **sizing × severidade da sequência de perdas**, não do win rate — o gate ataca o drawdown encurtando as sequências perdedoras em regime de chop.
- **R-15c.** **Stop móvel / trailing (decisão do Founder, 2026-06-04 — D1).** Parâmetro `trail_points` (0 = desligado). Enquanto a posição está aberta, o stop **segue o pico** a `trail_points` de distância e **só anda a favor, nunca recua**: `long → SL = max(SL, maior_high_desde_entrada − trail_points)`; `short` espelhado. **No backtest/gravador** o stop vigente é checado com o pico das barras **anteriores** (pior caso intrabar, C5) e só **depois** ratcheta com o extremo da barra atual. **No EA executor** o SL é movido via `PositionModify` a cada nova barra. Combina com `stop_points` (SL inicial) e `target_points` opcional (TP fixo): quando `target_points=0`, a saída é só por stop móvel / SL inicial / fim de sessão (deixa o ganho correr). **Default da D1 do produto:** `stop_points=500`, `target_points=0`, `trail_points=200`. É **parâmetro de paridade** (idêntico nos três lados).
- **R-16.** Os **indicadores são computados on-the-fly** das barras canônicas a cada run (Q5). **Sem tabela de indicadores materializados** no MVP (materialização = Later 0.6.1).
- **R-17.** O resultado produz **ledger de trades** (schema §4.5), **curva de equity (bruta)**, lista de trades, **drawdown** e **métricas brutas canônicas** (WR, expectância **bruta**, profit factor, nº trades, max drawdown). As métricas são calculadas por **uma rotina Python única** sobre o ledger — a **mesma** que consome o export do EA (R-26), eliminando divergência de cálculo (ADR-SL-02 §2.5).
- **R-18.** **Walk-forward OOS** disponível, reusando `walk_forward.py`/`validation.py`.
- **R-19.** **Par como unidade** (Q10): para D3/LS, a unidade contábil é o **par** (gain/loss do spread agregado). As pernas existem para auditoria/UI; "perna separada" é disponibilizada **só se o Founder pedir** (ele disse: "se sentir falta peço separado").
- **R-20.** **Promoção de kernel:** `bars.py` (e `validation.py` se o optimizer o consumir direto) são promovidos a **`_shared/research_kernel/`** antes de `strategy_lab` consumi-los, para não violar import-linter (feature→feature proibido). Momento exato (antes de D1 ou junto do multi-símbolo) é detalhe do PLAN; o **destino** (`_shared/`) está decidido (ADR-SL-02 §2.6).

### 3.3 Assets Experts (EA executor MQL5 multi-símbolo, DEMO)

> **⚙️ Ajuste de diretriz — dois EAs por estratégia (ADR-SL-04, 2026-06-03).** A Onda 1
> materializou **dois EAs** para a D1, e esta é a diretriz para as próximas estratégias:
> - **EA gravador (`cam_d1_orb30.mq5`):** computa a estratégia e **exporta o ledger canônico**
>   (R-27) **sem enviar ordem** — fica **fora** da allowlist de `OrderSend`. É o lado MQL5 que
>   **prova a paridade** contra o backtest Python (R-28..R-31), em pior-caso canônico.
> - **EA executor (`cam_d1_orb30_exec.mq5`):** **opera de fato** (R-21) a mercado com SL/TP,
>   **visível no Strategy Tester**; **dentro** da allowlist `lint_mql5`. Na Onda 1 executa a
>   **estratégia pura, sem Risk Engine** (decisão do Founder: "ainda não verificando riscos").
>
> O executor usa o modelo de fill real do broker (SL/TP intrabar) e **não é tick-idêntico** ao
> backtest — portanto **a paridade (R-28..R-31) é checada contra o GRAVADOR**, não contra o
> executor. O executor entrega validação **visual/comportamental** ao Founder. Evolução prevista:
> quando o Assets RiskManager existir, o executor passa a consultá-lo (como `cam_risk_mirror`).

- **R-21.** Nasce um **EA executor novo** em MQL5 (`apps/cam-cockpit/mql5/experts/`), distinto do `cam_bridge` (read-only): envia/modifica/fecha ordem no **Strategy Tester** e em **conta DEMO**. É **escrito à mão**, seguindo a DEF comum como especificação — **dupla implementação deliberada** da lógica Python (ADR-SL-01). **Acompanhado de um EA gravador** que exporta o ledger sem operar (ADR-SL-04 — ver nota acima); a paridade roda contra o gravador.
- **R-22.** **Execução atômica das pernas** (par como unidade — C14): o EA só monta a posição de um par se conseguir **as duas pernas** com book aceitável; se uma perna não preenche, **não monta meia-posição** (perna solta = direcional não-intencional). Saída das duas pernas no **mesmo evento**.
- **R-23.** **Multi-símbolo híbrido por classe** (ADR-SL-03 §2.1):
  - **Single-symbol** (D1, D2, V1, V2, S2) → **Strategy Tester** (every tick based on real ticks): fidelidade e reprodutibilidade máximas.
  - **Par / 2 pernas** (D3, LS1, LS2, LS3) → **conta DEMO ao vivo** (dois books sincronizados em ticks reais); Strategy Tester só como apoio de dev/sanity, **não** como gate de paridade.
  - **Cesta / ranking** (S1) → **conta DEMO ao vivo** (N símbolos, rebalance diário).
- **R-24.** **Guard-rail de conta DEMO (duplo)** (ADR-SL-03 §2.5, **sec**):
  1. **Configuração** — `input` apontando para conta/servidor DEMO; e
  2. **Checagem em runtime no próprio EA** — lê `AccountInfoInteger(ACCOUNT_TRADE_MODE)`; se **≠ `ACCOUNT_TRADE_MODE_DEMO`**, o EA **recusa operar** (não envia ordem) e loga.
  Live real **só por ato explícito do Founder** — e, quando solicitado, **para tudo e aciona SEC-GOV/Kevin** antes (gatilho: integração externa com capital real). **Não há caminho de promoção silenciosa a conta real.**
- **R-25.** **Perna short mecânica, sem aluguel** (Q8): as LS têm perna short; vender a descoberto é mecanicamente possível no tester/DEMO (`SELL`). **Não se modela aluguel/disponibilidade/custo de BTC** — coerente com MVP-bruto. **Simplificação consciente registrada**; aluguel real = Later (com C7/C8). Isto **infla** o edge das LS no bruto (esperado e enganoso — ver R-32).
- **R-26.** O EA **orquestra-se/observa-se via `mt5_integration`** (`ea_dispatcher`/`multi_ea_manager`/`fill_subscriber`, ZeroMQ 127.0.0.1). A **execução de ordem vive exclusivamente no MQL5**; o backend Python **só orquestra/observa** — **nenhuma feature Python ganha caminho de envio de ordem** (isolamento mantido; import-linter intacto). O slice `strategy_lab` **não** importa `mt5_integration` (seria feature→feature); a orquestração é por evento ou endpoint da própria `mt5_integration` (mecanismo fino = PLAN).
- **R-27.** O EA **exporta um ledger de trades** no schema único (§4.5) para a camada de paridade consumir.

### 3.4 Paridade Py↔EA (dupla checagem — gate bloqueante)

- **R-28.** A **paridade é dupla checagem independente** (ADR-SL-01 §2.3): como as duas implementações **não** se geram, a única garantia de convergência é comparar trade-a-trade o ledger Python contra o ledger exportado pelo EA, **alinhado por barra de sinal**.
- **R-29.** **Critério PASS (subconjunto C1–C14 sem C7/C8):** **100% dos sinais coincidem** (mesma barra, mesmo lado) **+ preço de entrada/saída ≤ 1 tick + volume financeiro idêntico + qtd idêntica + motivo de saída idêntico** (Q6). Cobre `unit: pair/basket` (par como unidade — C14).
- **R-30.** A paridade é **gate bloqueante a cada alteração de qualquer lado** (Python ou `.mq5`) — **é o que paga a dupla implementação** (ADR-SL-01 §4). Mexeu num lado, **roda paridade**; **FAIL bloqueia a promoção**.
- **R-31.** **FAIL → abre BUG** (`teczi-bug-fix`): divergência é **bug em UM dos dois** lados, nunca "variação natural de ambiente". Investiga na ordem do pipeline (EDGE-CONTRATO §5.5: dados → barra/fuso → ordem de avaliação → fill/gap → sizing → stop/alvo/sessão). **Proibido "tunar" um lado para casar** sem entender a causa. O comparador emite **relatório PASS/FAIL** (trade-a-trade + métricas lado a lado + veredito). **Nuance dos pares** (ADR-SL-03 §2.2): onde a reprodutibilidade exata do book de DEMO não existe, a paridade do par pode ser rebaixada de trade-a-trade-de-preço para **paridade de lógica de sinal** (mesmos pontos de entrada/saída) — registrar explicitamente no run.

### 3.5 Anti-falsa-confiança

- **R-32.** **Rótulo de UI obrigatório:** toda tela/relatório de resultado exibe o marcador **"BRUTO — sem custo/IR"** de forma visível. O MVP prova **mecânica/paridade**, **não** edge líquido. **Atenção redobrada nas LS (LS1/LS3):** são refém do custo; **parecem ótimas no bruto** — isso é esperado e enganoso. "Tem edge líquido?" só se responde com C7/C8 (Later). **Paridade verde no bruto ≠ estratégia aprovada.**

### 3.6 Transversais

- **R-33.** **Ordem incremental (Q2):** o escopo são as 10 estratégias, mas a **construção é incremental** — **D1 ORB-30 single-symbol primeiro, fim-a-fim**; o Founder valida (testa o EA e o backtest via CAM) e dá o OK; só então escala para par (D3/LS), cesta (S1) e à vista (V/S). **Não começar a próxima antes de a anterior bater paridade.** A ordem fina é do PLAN.
- **R-34.** **D1 é derivada de `orb_60m_win.py`** (hoje ORB-60) adaptada para **ORB-30** (§ catálogo D1). A DSL existente (`strategies/dsl`) é **reusada** como compilador do lado Python e **estendida** para multi-símbolo/par.
- **R-35.** O **schema do ledger de trades** (§4.5) é **único** e compartilhado por backtest Python e export do EA — é o contrato que a paridade consome dos dois lados. No MVP **sem** `custo`, `ir`, `pnl_liquido` (C7/C8 Later).
- **R-36.** **D2 — VWAP Mean-Reversion fade (WDO, single-symbol), 2026-06-04.** Single-symbol → **reusa o motor da D1** (`run_d1_backtest` é agnóstico ao sinal). Lógica (ficha D2): VWAP **cumulativo da sessão** + σ ponderado por volume (typical=(h+l+c)/3); **FADE** na tocada de ±`k_entry`·σ (short na esticada pra cima, long pra baixo); **alvo = VWAP**, **stop = VWAP ± `k_stop`·σ** (congelados no fill, absolutos → espelháveis no EA); sem runner; `warmup_bars` antes de operar (σ confiável); 1 sinal por excursão (re-arma ao voltar pra dentro da banda). Default `k_entry=2.0`, `k_stop=3.0`, `warmup_bars=30`. **Para o MQL5 (à mão, paridade):** acumular `sum_pv/sum_v/sum_pv2` por sessão, congelar VWAP/σ no sinal, mesma regra de fade/alvo/stop. Lado Python = `strategies/d2_vwap.py` (referência).
- **R-37.** **D3 — Spread/lead-lag WIN×WDO (PAR, multi-símbolo).** É o **"ponto duro"** (ADR-SL-03, Onda 2): exige **motor multi-símbolo** (lê 2 séries de `research_*`, sincroniza por timestamp), beta EWMA, z-score do resíduo, entrada >±2σ, saída em z=0, stop em z>3σ, **par como unidade** (C14). **NÃO reusa o motor single-symbol.** Fica como build da Onda 2 — só após D1/D2 baterem paridade. Listada `runnable=False` até o motor de par existir.

---

## 4. Contratos

> Rotas, schemas e formatos. Nomes de rota/coluna são propostos; ajuste fino de nomenclatura é do CODE dentro do escopo.

### 4.1 Rotas REST — `/api/v1/strategy-lab/*`

| # | Método · Rota | Frente | Descrição |
|---|---|---|---|
| 1 | `GET /api/v1/strategy-lab/strategies` | Strategy | Lista as 10 estratégias (família, símbolos, `unit`, status). |
| 2 | `GET /api/v1/strategy-lab/strategies/{id}` | Strategy | Detalhe + DEF + `param_set` ativo. |
| 3 | `GET /api/v1/strategy-lab/strategies/{id}/params` | Strategy | Lista `param_set`s (inclui `suggested` do otimizador). |
| 4 | `PUT /api/v1/strategy-lab/strategies/{id}/params` | Strategy | Edita/cria `param_set` (R-04). |
| 5 | `POST /api/v1/strategy-lab/backtests` | RunTests | Dispara backtest MVP-bruto (config: estratégia, símbolos[], período, TF). Retorna `run_id`. |
| 6 | `GET /api/v1/strategy-lab/backtests/{run_id}` | RunTests | Status + métricas brutas canônicas + rótulo BRUTO. |
| 7 | `GET /api/v1/strategy-lab/backtests/{run_id}/equity` | RunTests | Curva de equity (bruta). |
| 8 | `GET /api/v1/strategy-lab/backtests/{run_id}/trades` | RunTests | Ledger de trades (par como unidade; pernas em detalhe se pedido). |
| 9 | `POST /api/v1/strategy-lab/optimizations` | Strategy | Dispara otimização **on-demand** (grid+random+WF). Retorna `opt_id`. |
| 10 | `GET /api/v1/strategy-lab/optimizations/{opt_id}` | Strategy | Resultado: `param_set` **sugerido** + nº de tentativas + robustez no-cliff (R-07/R-08). |
| 11 | `POST /api/v1/strategy-lab/parity` | Paridade | Dispara comparação Py↔EA para uma estratégia/período (ledger Python × export EA). Retorna `parity_id`. |
| 12 | `GET /api/v1/strategy-lab/parity/{parity_id}` | Paridade | Relatório **PASS/FAIL** trade-a-trade + métricas lado a lado + veredito + causa C1–C14 se FAIL. |
| 13 | `GET /api/v1/strategy-lab/experts` · `POST .../experts/{id}/{start\|stop}` | Experts | Lista/gere EAs (reusa `robot_orchestrator`/`ea-control`/`mt5_integration`). |

> Observação: rota 9 (`optimizations`) é **distinta** de rota 5 (`backtests`) — backtest e otimização **nunca** se acoplam (R-05). Adoção de um `param_set` sugerido é ação do usuário via rota 4 (R-08).

### 4.2 Tabelas novas de domínio (feature `strategy_lab`)

**`strategy_param_set`**

| Coluna | Tipo | Nota |
|---|---|---|
| `id` | uuid/pk | |
| `strategy_id` | fk | liga à DEF/estratégia |
| `params` | jsonb | conjunto de parâmetros |
| `origin` | enum(`manual`,`suggested`) | `suggested` = saída do otimizador, **não aplicado** (R-08) |
| `optimization_id` | fk null | proveniência se `suggested` |
| `created_at` | ts | |

**`backtest_run`** (reuso/extensão de `backtest/domain.py:BacktestRun`)

| Coluna | Tipo | Nota |
|---|---|---|
| `id` | uuid/pk | `run_id` |
| `strategy_id` · `param_set_id` | fk | |
| `symbols` | text[] | **novo** — multi-símbolo |
| `unit` | enum(`single`,`pair`,`basket`) | **novo** |
| `period_start`/`period_end` · `timeframe` | | |
| `mode` | const `gross` | MVP-bruto (sem custo/IR) |
| `metrics` | jsonb | métricas brutas canônicas |

**`backtest_leg_trade`** (trade multi-perna — par como unidade, Q10)

| Coluna | Tipo | Nota |
|---|---|---|
| `id` | uuid/pk | |
| `run_id` | fk | |
| `pair_id` | uuid | agrupa as pernas de uma unidade-par; a **contabilização é por `pair_id`** (agregação por janela entrada/saída comum). `single` = par com uma perna só |
| `leg` | enum(`long`,`short`) | |
| `symbol` | text | |
| `ts_entry`/`price_entry`/`ts_exit`/`price_exit` | | C4–C6 |
| `qty` | int | C9 |
| `exit_reason` | enum(`stop`,`target`,`time`,`session`) | C3/C10/C11 |
| `pnl_bruto` | numeric | **bruto** (R-11) |
| `volume_financeiro` | numeric | |

> **Decisão fina (ADR-SL-02 §2.2):** modelagem por **`leg` + `pair_id`** numa tabela de pernas; a unidade-par é **agregação**, não entidade `backtest_pair_trade` separada. Um único modelo cobre single/pair/basket.

### 4.3 Reuso (não recriar)

`research_bars` / `research_ticks` (ingestão canônica multi-símbolo, provenance) — **reusados** (R-09). `bars.py` (C1) e `validation.py` — promovidos a `_shared/research_kernel/` (R-20). `walk_forward.py` — reusado (R-18).

### 4.4 Formato da DEF de estratégia (legível, fonte única — ADR-SL-01 §2.2)

```yaml
strategy: D1_orb30_win
family: D                 # D | V | S | LS
symbols: [WIN]            # lista — par/cesta quando multi-símbolo
unit: single              # single | pair | basket   (C14 / Q10)
timeframe: M5             # decisão; barra canônica M1→TF (C1)
session:
  tz: America/Sao_Paulo   # C2/C11 — padrão B3, sem default do broker
  open: "09:00"
  close: "17:55"
  flat_at_close: true
indicators:
  - type: opening_range
    minutes: 30
signal:
  long:  "price > opening_range.high"   # ordem C3: saída antes de entrada
  short: "price < opening_range.low"
  fill: next-bar-open                   # C4
  intrabar: worst-case                  # C5
  gap: honest                           # C6
stop:   { type: points, value: 150 }    # C10 mecânico
target: { type: points, value: 300 }
sizing: { contracts: 1, rounding: floor } # C9 determinístico
seed: 42                                 # C12
# multi-símbolo (unit: pair|basket):
# spread:  "P[WIN] - beta * P[WDO]"
# z_entry: 2.0   z_exit: 0.5   z_stop: 3.5
# leg_execution: atomic                  # C14 — pernas no mesmo evento
```

A DEF é versionada em `/project` (não em `/apps`); é simultaneamente **entrada do compilador Python** e **especificação humana do `.mq5`**. **Sem C7/C8** (custo/IR) no MVP.

### 4.5 Ledger de trades — schema canônico (contrato de paridade)

Subconjunto MVP do schema do EDGE-CONTRATO §4, consumido pelos **dois** lados (Python e export do EA):

```
trade_id, pair_id, leg, symbol, lado,
ts_entrada, preco_entrada, ts_saida, preco_saida,
qtd, motivo_saida, pnl_bruto, volume_financeiro
```

**Sem** `custo`, `ir`, `pnl_liquido` (C7/C8 Later). Métricas calculadas pela **mesma rotina Python** sobre este ledger nos dois lados (R-17).

---

## 5. Casos de uso / cenários

| # | Caso | Esperado |
|---|---|---|
| 1 | **Rodar backtest D1** (single-symbol WIN) | `POST /backtests` com D1+WIN+período+M5 → run bruto; equity bruta, ledger de trades, métricas brutas; rótulo "BRUTO — sem custo/IR" presente. |
| 2 | **Otimizar D1 on-demand** | `POST /optimizations` (acionado pelo usuário) → grid+random+WF; retorna `param_set` **sugerido** + nº de tentativas + robustez no-cliff; **não aplica** (Founder decide via `PUT .../params`). |
| 3 | **Comparar paridade Py↔EA (D1)** | Backtest Python + run do EA no Strategy Tester sobre **mesmo dataset** → `POST /parity` → relatório: 100% sinais + preço ≤1 tick + volume idêntico ⇒ **PASS**; senão **FAIL** + causa C1–C14. |
| 4 | **Rodar par D3 multi-símbolo** (WIN×WDO) | Backtest Python multi-série (sincronização por timestamp, par como unidade); EA executa as duas pernas **atomicamente** em **DEMO ao vivo**; paridade cobre o par (lógica de sinal onde a reprodutibilidade exata do book não existe — R-31). |

---

## 6. Casos limite / exceções

- **Símbolo sem dados no período:** backtest **não roda** (provenance/dado ausente — R-09); retorna erro explícito, não resultado vazio silencioso.
- **Barra ausente num símbolo do par** num timestamp: **não opera a perna naquele bar; sem meia-posição** (R-14); o EA espelha (R-22).
- **Otimizador sem dados suficientes** (poucos trades OOS p/ DSR/walk-forward): otimizador **recusa sugerir** e reporta insuficiência; **não** entrega "o pico" sem robustez (R-07).
- **Paridade FAIL:** **abre BUG** (R-31); **bloqueia promoção** da estratégia; nunca "tunar" para casar.
- **Conta não-DEMO no EA:** guard-rail duplo (R-24) **recusa operar** e loga; **sem promoção silenciosa a real**; live real aciona SEC-GOV antes.
- **Par com book insuficiente para uma perna** no EA: **não monta meia-posição** (R-22).
- **DEF e dataset divergentes entre os dois lados** da paridade: pré-condição falha (C13) — comparação **inválida** antes de qualquer métrica.

---

## 7. Classificação P/M/G

| Campo | Valor |
|---|---|
| Classe | **G (Grande) — decomposta** |
| Rationale | Três módulos de produto (Strategy/RunTests/Experts) + quatro peças novas/estendidas (otimizador on-demand, motor MVP-bruto **multi-série**, **DSL multi-símbolo/par**, **EA executor multi-símbolo**) + camada de **paridade**, atravessando **três ambientes** (Python/FastAPI, React, MQL5/MT5) que precisam concordar numericamente, sobre **10 estratégias** (5 multi-símbolo). Exige **decomposição em TASKs** e **ordem incremental** (D1 primeiro, fim-a-fim — R-33). Decisões arquiteturais estruturantes já fechadas em 3 ADRs Accepted. |

> Classe por **tamanho/decomposição apenas** — **sem** modificadores de risco/segurança/arquitetura/release (Q8). **Nico pode contestar no PLAN** (loop ilimitado até consenso; Founder decide quando parar).
>
> **Recomendação de ordem ao PLAN:** construir **D1 ORB-30 single-symbol fim-a-fim** (DEF → backtest Python bruto → `.mq5` à mão → paridade PASS → otimizador sugere) como vertical slice que prova a arquitetura, **antes** de paralelizar as demais. Gate de prova a cada salto de complexidade (single → par → cesta).

---

## 8. Marcadores de segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (check intrabloco no CODE) | **sim** | **Guard-rail de conta DEMO no EA** (R-24): isolamento de execução (ordem só no MQL5, backend só observa — R-26), recusa de operar em conta não-DEMO, sem caminho de promoção silenciosa a real. **Kevin entra no bloco do EA executor.** |
| `qa-sec` (QA-SEC no QA) | **sim** | QA-SEC valida proporcionalmente: (a) guard-rail DEMO duplo (config + runtime) efetivo; (b) isolamento mantido (import-linter — nenhuma feature Python com caminho de ordem); (c) **sem secrets** no EA/config/repo. |

> **Proporcionalidade (ARCH §8):** superfície sensível clássica (Risk Engine/kill switch/journal) está **OUT** e a Constituição foi descomissionada — **não há gatilho constitucional**. Threat-model formal do Kevin é **opcional** neste ciclo (research/DEMO, sem capital real) e **obrigatório** se algum dia o EA for apontado a conta real → aí **para tudo e aciona SEC-GOV** (gatilho: integração externa com capital real). Sem secrets em commit (regra universal).

---

## 9. Saídas esperadas

- Feature backend **`features/strategy_lab/`** (DEF, compiler Python, `backtest_engine` MVP-bruto multi-série, `optimizer`, `parity`, `domain`/`repository`/`service`/`routes`).
- **Tabelas novas:** `strategy_param_set`, `backtest_run` (estendida), `backtest_leg_trade`; **reuso** de `research_*`.
- **`bars.py`/`validation.py`** promovidos a `_shared/research_kernel/`.
- **EA executor MQL5 novo** (`mql5/experts/`), multi-símbolo, com guard-rail DEMO duplo.
- **DEF de D1 ORB-30** versionada em `/project`.
- **3 telas React** (Assets Strategy / RunTests / Experts) + **painel de Paridade** (PASS/FAIL), com **rótulo "BRUTO — sem custo/IR"** visível.
- **Rotas `/api/v1/strategy-lab/*`** (§4.1).
- **Relatório de paridade** Py↔EA (trade-a-trade + métricas + veredito).

## 10. Critérios de aceite

> QA valida (Linus + Kevin em QA-SEC). **Foco do MVP: D1 ORB-30 fim-a-fim** (Q2); demais escalam após OK do Founder.

**Go de D1 (fim-a-fim):**

1. **Backtest Python roda:** `POST /backtests` com D1+WIN produz equity bruta, ledger de trades e métricas brutas canônicas; resultado **bruto** (sem custo/IR aplicados — R-11).
2. **EA roda no Strategy Tester:** o `.mq5` de D1 executa entrada/stop/alvo/saída no tester (single-symbol), exportando ledger no schema canônico (R-27).
3. **Paridade PASS:** comparador Py↔EA sobre **mesmo dataset** → **100% sinais coincidentes + preço ≤1 tick + volume idêntico + qtd e motivo de saída idênticos** (R-29); relatório PASS emitido.
4. **Otimizador sugere:** `POST /optimizations` para D1 retorna `param_set` **sugerido** + nº de tentativas + robustez no-cliff; **não aplica** (R-07/R-08).
5. **Rótulo BRUTO presente:** todas as telas/relatórios de resultado exibem **"BRUTO — sem custo/IR"** (R-32).
6. **Guard-rail DEMO:** EA recusa operar em conta não-DEMO (R-24); isolamento mantido (sem caminho de ordem no backend — R-26); sem secrets (qa-sec).
7. **Não-regressão:** caminho Risk-acoplado de `features/backtest/` **intocado** (R-12).

**Critérios das demais estratégias** (escala pós-OK do Founder): paridade dos **pares** (D3/LS) conforme R-31 (trade-a-trade onde reprodutível; lógica de sinal em DEMO ao vivo quando o book exato não é reproduzível); execução atômica das pernas comprovada (R-22); rótulo BRUTO e atenção redobrada nas LS (R-32).

## 11. Delta no DVP (se aplicável)

Sem delta de direção estratégica nesta SPEC — a virada para produto TCaM e o descomissionamento da Constituição já estão registrados em `project/tcam/` (PIVOT/DECOMMISSION) e refletidos no SCOPE v0.7. Esta SPEC apenas materializa requisitos sob essa direção já estabelecida.

## 12. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-06-03 | Draft inicial — SPEC unificada da tríade (35 regras R-*, 13 rotas, 3 tabelas novas, foco em D1 fim-a-fim); subconjunto C1–C14 sem C7/C8; sec/qa-sec marcados | _(pendente)_ |

---

> SPEC / Albert · TCaM / produto · Constituição descomissionada · MVP de valores brutos ·
> sem codegen (dupla implementação deliberada, paridade como detector de dessincronização) ·
> 10 estratégias no escopo, D1 ORB-30 primeiro fim-a-fim · 2026-06-03 · v1 ·
> co: Kevin (sec/qa-sec — guard-rail DEMO). **Próxima fase: PLAN (Nico) — pode contestar P/M/G. O Founder decide o gate.**

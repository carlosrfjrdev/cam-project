---
template: SCOPE
phase: DISC
status: APROVADO v0.7 — Founder ratificou (2026-06-03); ARCH concluida (3 ADRs Accepted)
produto: TCaM (cam-cockpit)
id: SCOPE-STRATEGYLAB-TRIAD
version: v0.7
slug: strategylab-triad-strategy-runtests-experts
data: 2026-06-03
lead: Marty
orquestrador: Leo
solicitante: Founder
supersede_parcial: SCOPE-STRATLAB-PARITY-001 (vira insumo; paridade rebaixada de título para sub-objetivo)
reanalise: >
  Reescrito sob 4 decisões verbatim do Founder (2026-06-03): (1) escopo ampliado de D1 para
  10 estratégias (D1,D2,D3,V1,V2,S1,S2,LS1,LS2,LS3 — só F1/H1 OUT); (2) multi-símbolo IN
  desde já (move de OUT→IN); (3) otimizador on-demand IN no MVP (acionável pelo usuário);
  (4) MVP simula VALORES BRUTOS (gain/loss/volume) — sem corretagem, emolumentos, IR, slippage.
modo: >
  Produto TCaM. Constituição DESCOMISSIONADA (2026-06-03) — sem Risk Engine soberano,
  sem Arts., sem "preservar capital" como lei. Permanece apenas o RIGOR de engenharia
  (anti-data-snooping, paridade Py↔EA) como boa prática, não como amarra constitucional.
  MVP de VALORES BRUTOS (decisão verbatim do Founder). Execução de ordem ATIVA no EA
  (Strategy Tester/DEMO). Live real continua OUT.
personas_consultadas: [Marty, Oscar, Jim, Nassim, Ada, Nikola, Don, Peter, Voltaire]
---

# SCOPE — StrategyLab do CaM · A Tríade Assets Strategy + RunTests + Experts

> **Reposicionamento (Leo):** este SCOPE substitui o título do `SCOPE-STRATLAB-PARITY-001`.
> Lá, o **organizador era a paridade**. Aqui, o organizador são os **três módulos de produto**
> que o Founder quer ver funcionando — **Assets Strategy**, **Assets RunTests**,
> **Assets Experts**. A paridade Python↔EA continua sendo o coração técnico, mas vira
> **sub-objetivo**, não o nome da entrega. E o MVP nasce **com valores brutos** — paridade de
> **lógica** (entrada/saída/gain/loss/volume), não de **fricção**.

> ⚠️ **REANÁLISE v0.7 (Leo, 2026-06-03):** o Founder revisou o v0.6 e tomou 4 decisões que
> mudam o eixo do SCOPE. O que era "**D1 vertical slice**, multi-símbolo OUT, otimizador 2ª
> entrega" virou "**10 estratégias** multi-família, **multi-símbolo IN**, **otimizador
> on-demand IN**". A construção continua **incremental** (ordem é decisão do PLAN), mas o
> **escopo** agora abraça as 10. As seções §2, §3, §4, §6, §7, §8, §9, §10 foram reescritas.
> **Distinção crítica deste SCOPE:** ESCOPO = 10 estratégias. ORDEM = incremental (PLAN).

---

## 1. Contexto e motivação

### 1.1 A virada para produto
O CaM virou **TCaM** — produto para terceiros operarem. A Constituição foi descomissionada
(`project/tcam/CONSTITUTION-DECOMMISSION.md`). Não há mais Risk Engine como lei, limite de
2 contratos como artigo, nem "preservação de capital" como hierarquia soberana. O Risk Engine
sobrevive como **feature** (Assets RiskManager) e está **fora** deste SCOPE.

O que **fica** dos artefatos anteriores (eram corretos como engenharia, não como lei):
- A **régua anti-data-snooping** do Jim (DSR, walk-forward, ≥N trades OOS, no-cliff).
- O **contrato de paridade C1–C14** do EDGE-CONTRATO — adaptado: no MVP só os itens de
  **lógica** valem; os itens de **custo/IR** (C7/C8) ficam **Later**.

### 1.2 Os três módulos (mapa → estado real)
`MAP-MODULES-TCaM.md` já mapeou os três a features existentes — **nenhum nasce do zero**:

| Módulo | Frontend existente | Backend existente | Estado |
|---|---|---|---|
| **Assets Strategy** | `features/strategies/StrategyRegistryPage` | `features/strategies` (+ `dsl/{parser,compiler}`, `strategies/orb_60m_win`) | ✅ base; falta **otimizador** |
| **Assets RunTests** | `features/backtest/BacktestPage` + `paper-trading` | `features/backtest/{simulator,walk_forward}` + `research/leadlag/{bars,validation}` | ⚠️ motor parcial + acoplado a Risk/Constituição |
| **Assets Experts** | `features/robot-orchestrator` + `features/ea-control` | `features/mt5_integration` + `robot_orchestrator` + EAs `cam_bridge`/`cam_risk_mirror` | ⚠️ plumbing existe; falta **EA executor** (agora **multi-símbolo**) |

> **Marty (anti-feature-factory), reposicionado:** o Founder ampliou o ESCOPO para 10
> estratégias — essa é uma decisão soberana, registrada. A defesa anti-fábrica **não some**,
> ela **muda de lugar**: deixa de ser "limitar o escopo a D1" e passa a ser "**ordem de
> construção incremental com gate de prova a cada salto de complexidade**". O escopo são 10;
> a **construção** começa pela mais simples (single-symbol, D1), prova a arquitetura
> fim-a-fim, e só então escala para multi-símbolo (D3/LS) e à vista (V/S). A ordem é do
> **PLAN** — mas o SCOPE registra a recomendação: **provar 1 fim-a-fim antes de paralelizar 10**.

### 1.3 As 10 estratégias do escopo (decisão do Founder)
> **Verbatim:** "Eu já fiz o filtro das estratégias, devemos ir com **D1, D2, D3, V1, V2,
> S1, S2, LS1, LS2, LS3** — só **F1 e H1 ficam de fora**."

| # | Estratégia | Família | Símbolos | Multi-símbolo? | Origem catálogo |
|---|---|---|---|---|---|
| **D1** | ORB-30 filtrado por regime | Derivativo intraday | WIN | Não (single) | ⭐⭐⭐ |
| **D2** | VWAP Mean-Reversion fade | Derivativo intraday | WDO | Não (single) | ⭐⭐ |
| **D3** | Spread/lead-lag WIN×WDO | Derivativo intraday | WIN + WDO | **Sim (2 pernas)** | ⭐⭐⭐⭐ |
| **V1** | Gap-and-Go com confirmação de fluxo | Ação à vista intraday | 1 ação (cesta watchlist) | Não (single por trade) | ⭐⭐½ |
| **V2** | Mean reversion oversold (RSI2+MM200) | Ação à vista curto | 1 ação | Não (single) | ⭐⭐⭐ |
| **S1** | Momentum cross-sectional | Ação à vista swing | universo IBrX (ranking) | **Sim (N símbolos)** | ⭐⭐⭐⭐⭐ |
| **S2** | Pullback em tendência | Ação à vista swing | 1 ação por trade | Não (single por trade) | ⭐⭐⭐⭐ |
| **LS1** | Spread WIN×WDO intraday (z-score) | Long & short intraday | WIN + WDO | **Sim (2 pernas)** | ⭐⭐ |
| **LS2** | Pair trading setorial (cointegração) | Long & short swing | 2 ações (par) | **Sim (2 pernas)** | ⭐⭐⭐ |
| **LS3** | Pair trading ON×PN mesmo emissor | Long & short intraday | 2 classes (par) | **Sim (2 pernas)** | ⭐⭐ |

**Fora do escopo (decisão verbatim):** **F1 (FII)** e **H1 (dividendos)** — são buy&hold de
total-return, **sem EA de Strategy Tester**, perfil de Carteira Hard. Vão para um módulo
total-return separado (**Later**).

> **Consequência central da ampliação (Jim/Nassim):** das 10, **4 são multi-símbolo / 2 pernas**
> (D3, LS1, LS2, LS3) e **1 é multi-símbolo por ranking** (S1). Isso torna **multi-símbolo um
> requisito de primeira classe** do contrato, do backtester e — o ponto duro — do **EA no
> Strategy Tester**. Endereçado em §3.2, §4 e §8.

### 1.4 Reaproveitamento — a descoberta que muda o tamanho
O estado real (`apps/cam-cockpit/backend/cam/features/`) já contém quase todas as peças:

- **DSL declarativa já existe** (`strategies/dsl/parser.py` + `compiler.py`): lê YAML/JSON
  (`strategy/asset/indicators/entry/exit`) → classe `Strategy` em runtime, com **AST whitelist**
  segura (sem `eval`). **Esta é a semente do contrato de estratégia única** — mas hoje é
  **single-asset**; precisa estender para **N símbolos / par como unidade** (§4.3).
- **Barra canônica determinística já existe** (`research/leadlag/bars.py`): M1→TF puro,
  reprodutível (R-12). É o **C1** do contrato de paridade, pronto. Já é multi-símbolo por
  natureza (processa N séries).
- **Anti-overfit já existe** (`research/leadlag/validation.py`): DSR (Bailey/López de Prado),
  walk-forward splits, Benjamini-Hochberg/FDR, Hayashi-Yoshida. É o **guard-rail do otimizador**.
- **Backtester tick-a-tick já existe** (`backtest/simulator.py` + `walk_forward.py`) — porém
  **acoplado ao Risk Engine e à Constituição** (importa `_shared.risk`, provisiona IR 20%,
  cita Arts.) **e single-symbol**. Precisa de um **modo MVP-bruto** desacoplado **e
  multi-série** (§3, §4.3).
- **MT5 plumbing já existe** (`mt5_integration`: candles/ticks/book via ZeroMQ, `ea_dispatcher`,
  `multi_ea_manager`, `fill_subscriber`) + EAs `cam_bridge` (read-only) e `cam_risk_mirror`.
  **Falta o EA executor** (envia/modifica/fecha ordem no Strategy Tester/DEMO) — agora
  **multi-símbolo** (ponto mais duro do SCOPE — §2.4, §8).

**Consequência:** o trabalho é majoritariamente **recomposição + 4 peças novas/estendidas**
(otimizador on-demand, modo-bruto do backtester multi-série, DSL multi-símbolo, EA executor
multi-símbolo), não construção greenfield.

---

## 2. Os três módulos detalhados

### 2.1 Assets Strategy — gestor de estratégias + otimizador ON-DEMAND que SUGERE

**O que é:** a tela onde o Founder **vê, gerencia e lista** estratégias, vê seus **parâmetros**,
e dispara o **otimizador de parâmetros** — **acionável sob demanda** (botão "otimizar"), não
automático em todo backtest.

**In (MVP):**
- Lista de estratégias (reusa `StrategyRegistryPage` + `features/strategies`) — agora cobre as
  **10 estratégias** (incluindo as multi-símbolo: o card de uma estratégia 2-pernas mostra
  **ambos os símbolos / o par como unidade**).
- Visualização e edição dos **parâmetros** de uma estratégia (ex.: janela do ORB, stop, alvo,
  β do spread, z-score de entrada/saída para LS).
- **Otimizador de parâmetros ON-DEMAND** (decisão verbatim do Founder — IN no MVP):
  > **Verbatim:** "Otimizador entra agora, mas ele é on-demand, eu posso rodar ou não a
  > otimização."
  - **Acionamento:** o usuário **dispara** a otimização explicitamente (botão/ação). **Não roda
    automático** em todo backtest. Backtest e otimização são ações distintas.
  - **Métodos MVP (Jim):** **grid search** (espaço pequeno, determinístico) e **random search**
    (espaço maior). Walk-forward como validação do candidato sugerido.
  - **Guard-rail anti-overfit obrigatório (Jim + Nassim):** todo conjunto sugerido passa por
    `validation.py` — **DSR penalizado pelo nº de combinações testadas** + **walk-forward OOS** +
    **checagem no-cliff** (a superfície ao redor do ótimo é chata, não um pico). O otimizador
    **nunca** entrega "o pico do backtest" sem reportar nº de tentativas e a robustez ao redor.
  - **O otimizador SUGERE, não aplica.** O Founder decide se adota o conjunto. (Sem auto-apply.)

**Out (MVP):** otimização multi-objetivo, algoritmos genéticos/bayesianos, otimização
distribuída. **Later.**

> **Nassim (lente, não dono):** o otimizador é a peça mais perigosa do SCOPE — é uma
> **fábrica de overfit** por construção. Que seja **on-demand** **reduz a exposição** (o usuário
> escolhe quando pagar o risco), mas **não anula** a necessidade da defesa: quanto mais
> combinações ele testa, mais "edge" de ruído ele acha. DSR pelo nº real de tentativas +
> no-cliff + OOS continuam **obrigatórios**, on-demand ou não. Um otimizador sem essas três
> travas é um gerador de falsa confiança com UI bonita.

### 2.2 Assets RunTests — backtest matemático Python + persistência + simulação (multi-símbolo)

**O que é:** a tela de backtest. O Founder obtém dados do MT5 (já faz no Quant Lab), **persiste
em banco** os dados do(s) papel(éis)/ticks/indicadores, e roda o **backtest matemático da
estratégia em Python** sobre a(s) série(s) temporal(is) escolhida(s).

**In (MVP):**
- **Configurar e rodar** um backtest de uma estratégia sobre **uma ou mais séries** (ativo(s) +
  período + TF). Para estratégias multi-símbolo (D3, LS1, LS2, LS3, S1), o config aceita **N
  símbolos / o par** como unidade.
- **Motor de backtest matemático em Python** — modo **MVP-VALORES-BRUTOS**: simula **entrada,
  saída, gain, loss e volume financeiro bruto** (P&L bruto em pontos × valor do ponto). **NÃO**
  aplica corretagem, emolumentos, slippage nem IR (decisão §3).
  - Reusa `backtest/simulator.py`, mas com um **modo desacoplado do Risk Engine** (o `simulator`
    atual importa `_shared.risk` e provisiona IR — isso precisa virar opcional/desligável) **e
    multi-série** (hoje é single-symbol; precisa ler e sincronizar N séries por timestamp).
  - Reusa `bars.py` (barra canônica, já multi-símbolo) e `walk_forward.py`.
- **Persistência (requisito explícito do Founder):** os dados do(s) papel(éis), ticks e
  indicadores derivados, persistidos em banco — para gerar os indicadores que o MT5 provê e
  rodar a estratégia matematicamente sem reextrair toda vez (ver §2.3 Ada). **Persiste N papéis**
  quando a estratégia é multi-símbolo.
- **Resultado visual:** curva de equity, lista de trades (entrada/saída/lado/qtd/P&L bruto),
  drawdown, métricas (WR, expectância bruta, profit factor, nº trades). Para multi-símbolo,
  o trade exibe **as pernas do par**. Reusa padrão de UI do Quant Lab.
- **Walk-forward OOS** (reusa `validation.py`).

**Out (MVP):** custos, IR, fiscal, provisão, slippage. **Later.** Live forward em conta real: **OUT**.

### 2.3 Persistência (Ada) — papel(éis)/ticks/indicadores, multi-símbolo

> **Ada (dados):** decisão de persistência é estruturante e vai para o ARCH. Posição inicial:

- **Reusar `research_bars`/`research_ticks`** como **camada de ingestão canônica** (já têm
  provenance e barra determinística, **e já modelam múltiplos símbolos**) **em vez de** criar
  `strategy_*` paralelas que dupliquem tick/candle. Provenance é inegociável mesmo no MVP:
  dado sem origem rastreável não entra.
- Criar **somente** o que é novo de domínio de estratégia: `strategy_param_set` (conjuntos de
  parâmetros, inclusive os sugeridos pelo otimizador), `backtest_run`/`backtest_trade`
  (já existem em `backtest/domain.py` — reusar; estender `backtest_trade` para **trade
  multi-perna**, registrando as pernas do par e a unidade-par), e cache de **indicadores
  derivados** se o recompute por run ficar caro.
- **Perguntas de ARCH:** (a) os indicadores ficam **materializados** (tabela) ou **computados sob
  demanda** a partir das barras canônicas? MVP tende a **on-the-fly** (mais simples, menos
  drift); materializar é otimização **Later**. (b) como modelar o **par/multi-símbolo** no
  schema de trades sem inflar o domínio — `backtest_trade` ganha `leg` + `pair_id`, ou nasce uma
  entidade `backtest_pair_trade`? (decisão fina = ARCH).

### 2.4 Assets Experts — gestão de robôs MT5 + EA executor (multi-símbolo)

**O que é:** a gestão dos robôs MT5 — e, distinto do `cam_bridge` (read-only), um **EA executor**
que **envia/modifica/fecha ordem** no **Strategy Tester** e em **conta DEMO**.

**In (MVP):**
- Gestão/listagem dos robôs MT5 (reusa `robot-orchestrator` + `ea-control` + `multi_ea_manager`).
- **EA executor novo (Nikola):** EA MQL5 que **opera de fato** no Strategy Tester/DEMO —
  entrada, stop, alvo, saída — implementando a **mesma lógica** da estratégia Python
  correspondente.
- **EA executor MULTI-SÍMBOLO (decisão verbatim do Founder — IN):** o EA precisa operar
  estratégias de **2 pernas** (D3, LS1, LS2, LS3) e de **ranking N-símbolos** (S1). Este é o
  **ponto duro do SCOPE** — endereçado honestamente em §8 e elevado a **ADR de ARCH**:
  > **Verbatim:** "precisamos multi-símbolo desde já".
  - **O problema real (Nikola, honesto):** o **MT5 Strategy Tester é single-symbol por padrão** —
    ele roda o EA sobre **um** símbolo/gráfico. Ler outro símbolo de **dentro** do EA é possível
    (`SymbolSelect`, `CopyRates`/`CopyTicks` de outro símbolo, `iCustom`), **mas com caveats no
    Strategy Tester**: o modo "**every tick based on real ticks**" + múltiplos símbolos tem
    limitações de sincronização de ticks entre símbolos e de disponibilidade de histórico do
    símbolo secundário dentro do tester. Em **conta DEMO ao vivo** (fora do tester) o
    multi-símbolo é direto; **no Strategy Tester** exige decisão de arquitetura.
  - **Isto NÃO é uma impossibilidade — é uma decisão de ARCH e um risco ativo.** O EA pode:
    (a) operar multi-símbolo via `CopyRates` do símbolo secundário no tester (com os caveats
    documentados), ou (b) validar multi-símbolo **em DEMO ao vivo** e usar o Strategy Tester
    só para as single-symbol, ou (c) sincronizar pernas via dados pré-carregados. **Oscar
    decide no ADR.** A **persistência (`research_*`) e o motor Python já são multi-símbolo
    naturalmente** — o gargalo é só o EA no tester.
- **Guard-rail de conta (Nikola):** o EA executor é **preso a conta DEMO** por configuração +
  checagem de tipo de conta no próprio EA. Live real só por ato explícito do Founder.
- **Pernas short (LS) no EA DEMO (Nikola):** as estratégias LS têm **perna short** (venda
  descoberta / aluguel). No Strategy Tester / DEMO, vender a descoberto é mecanicamente possível
  (o tester permite `SELL`), mas **aluguel/disponibilidade não são modelados** — coerente com o
  MVP-bruto (sem custo de aluguel). Registrar como **simplificação consciente** (§8).

**Out (MVP):** live real; modelagem de aluguel/short real; custo de execução real.

> **Nikola (engenharia):** o `cam_bridge` é read-only por design (e o import-linter garante que
> `research` não importa execução). O EA executor **precisa** tocar execução — mas no MT5/MQL5,
> **não** no backend Python. O isolamento do backend **não quebra**: o executor vive no EA
> (`apps/cam-cockpit/mql5/experts/`), e o backend só **orquestra/observa** via `ea_dispatcher`/
> `fill_subscriber`. A fronteira de isolamento é mantida — só muda de lado (MQL5). O
> multi-símbolo **não viola** isso; só torna o EA mais pesado.

---

## 3. Decisão MVP-VALORES-BRUTOS (registrar explicitamente)

> **Esclarecimento verbatim do Founder:** "Quando me referi a custo foram custo de corretagem,
> emolumentos e IR... agora é somente **valores brutos de gain e loss**."

**Decisão registrada (CRISTALINA — é a simplificação central do MVP):**
1. O MVP simula **apenas valores OPERADOS, brutos**: **entrada, saída, gain, loss e volume
   financeiro bruto**. P&L = pontos × valor do ponto, **sem nenhuma dedução**.
2. **Fora do MVP (explicitamente, decisão do Founder):** **corretagem, emolumentos, slippage,
   ISS, aluguel/short, IR**. → **Later**. O resultado do MVP é **bruto**, nunca líquido.
3. **A paridade no MVP é de LÓGICA + VALORES BRUTOS, não de fricção.** O critério de aprovação
   muda em relação ao EDGE-CONTRATO original: valem os itens de lógica do contrato (C1 barra,
   C2 fuso, C3 ordem de avaliação, C4 fill next-bar-open, C5 intrabar pior-caso, C6 gap, C9
   sizing, C10 stop/alvo, C11 sessão, C12 determinismo, C13 mesmo dataset, C14 par/estado).
   **Saem do MVP:** **C7 (custo)** e **C8 (IR)**. A paridade verifica: **mesmos pontos de
   entrada/saída, mesmo gain/loss bruto, mesmo volume financeiro**.
4. **Implicação positiva (Jim):** o MVP fica **muito mais simples e mais fácil de bater
   paridade** — sem custo, a maior fonte de divergência Py↔EA (modelo de fricção, item mais
   sensível do contrato) **desaparece**. A paridade de lógica + valores brutos é alcançável com
   tolerância apertada (100% dos sinais coincidem, preço ≤ 1 tick, volume idêntico).
5. **Ressalva honesta (Jim, registrada, não bloqueante):** backtest sem custo **infla** o edge.
   O Founder está ciente — isto é um MVP de **mecânica/paridade**, **não** uma prova de que a
   estratégia dá dinheiro. A pergunta "tem edge líquido?" só se responde quando custos/IR
   entrarem (Later). Não confundir "paridade verde no MVP" com "estratégia aprovada".
   **Atenção redobrada nas LS (LS1/LS3):** o catálogo crava que o edge delas é **refém do custo**
   — no MVP-bruto elas parecerão excelentes; isso é **esperado e enganoso**. O veredito real só
   vem com C7/C8 (Later).

---

## 4. Contrato de estratégia única (Python ↔ MQL5) — decisão arquitetural central

> Esta é a Q8 do SCOPE anterior e o coração do ARCH. **Codegen vs dupla implementação** —
> agora com a complicação **multi-símbolo / par como unidade**.

### 4.1 Recomendação (Oscar): **definição única declarativa → codegen para os dois lados**
- **Fonte única da verdade:** a **DSL declarativa que JÁ EXISTE** (`strategies/dsl/`). Uma
  estratégia é descrita **uma vez** em YAML/JSON (`indicators/entry/exit/params`).
- **Python:** o `compiler.py` já transforma a DSL em `Strategy` executável. **Reuso direto**
  (estendido para multi-símbolo — §4.3).
- **MQL5:** **gerar o `.mq5` a partir da mesma DSL** (codegen) — um template MQL5 parametrizado
  pela mesma AST. Assim, **uma mudança de lógica nasce nos dois lados por construção**, e a
  paridade deixa de depender de o humano manter duas implementações sincronizadas.

**Por que não dupla implementação:** duas implementações independentes (Python + MQL5 escritos à
mão) transformam **toda divergência em caça-bug manual** — exatamente o "experimento parecido,
falsa validação" que o EDGE-CONTRATO §5.5 alerta. Codegen mata o default não-declarado.

**Trade-off honesto (Oscar):** codegen MQL5 é **trabalho novo** e o gerador é, ele próprio, código
a validar. Para começar pela **1ª estratégia** (recomendação: D1 ORB-30, single-symbol), é
defensável escrever o `.mq5` **à mão**, **mas derivado da mesma DSL** e validado pela paridade —
e só investir no **gerador** quando a 2ª/3ª estratégia (e o multi-símbolo) provarem o padrão.
**Decisão fina = ARCH/ADR.**

> **Oscar:** a decisão estruturante (DSL como fonte única) deve fechar no ARCH **antes** do SPEC.
> O "à mão derivado da DSL" vs "codegen automático" é faseável — mas a **fonte única declarativa**
> não é negociável se a paridade importa. Com 10 estratégias e 5 multi-símbolo, o **codegen** vira
> mais atraente mais cedo (manter 10 `.mq5` à mão sincronizados com 10 DSLs é insustentável).

### 4.2 Itens do contrato que o ARCH precisa fixar (subconjunto MVP de C1–C14)
Barra canônica (C1 — `bars.py` pronto), fuso B3 (C2), ordem de avaliação saída-antes-de-entrada
(C3), fill next-bar-open (C4), intrabar pior-caso (C5), gap honesto (C6), sizing determinístico
(C9), stop/alvo mecânicos (C10), sessão B3 (C11), determinismo/seed (C12), mesmo dataset (C13),
**par/estado (C14 — agora crítico)**. **C7/C8 (custo/IR) explicitamente adiados.**

### 4.3 DSL multi-símbolo / par como unidade (novo — decisão de ARCH)
> **Requisito direto da decisão "multi-símbolo IN" do Founder.** A DSL atual é **single-asset**.
> Precisa expressar estratégias de **N símbolos / par como unidade**:

- **D3 / LS1 (spread WIN×WDO):** dois símbolos derivativos, spread beta-ajustado, **par é a
  unidade** (entra/sai das duas pernas no mesmo evento).
- **LS2 (pair cointegração):** duas ações distintas, par cointegrado, swing.
- **LS3 (ON×PN):** duas classes do mesmo emissor, par intraday.
- **S1 (momentum cross-sectional):** **N símbolos** (universo IBrX), seleção por ranking — não é
  "par", é **cesta/ranking** (modelo distinto de multi-símbolo).

A DSL precisa de uma **gramática que expresse**: (a) lista de símbolos / par; (b) o spread/β como
expressão derivada; (c) sinais sobre o **z-score do par** (não sobre um preço único); (d) execução
**atômica das pernas**. O **C14 do EDGE-CONTRATO já trata "par como unidade"** — a DSL tem que
materializar isso. **Oscar decide a forma no ADR** (extensão da gramática vs um tipo de estratégia
`pair`/`basket` separado). Isto NÃO é negociável se as 4 estratégias multi-símbolo entram no MVP.

---

## 5. Reaproveitamento (o que vem de onde)

| Peça do StrategyLab | Origem no código real | Ação |
|---|---|---|
| Contrato de estratégia declarativo | `strategies/dsl/{parser,compiler}.py` | **Reusar** como fonte única; **estender p/ multi-símbolo/par**; codegen MQL5 |
| Estratégia-exemplo | `strategies/strategies/orb_60m_win.py` | **Adaptar** p/ D1 ORB-30 (hoje é ORB-60) |
| Barra canônica (C1) | `research/leadlag/bars.py` | **Reusar** direto (M1→TF determinístico, já multi-símbolo) |
| Anti-overfit do otimizador | `research/leadlag/validation.py` (DSR, WF, FDR) | **Reusar** como guard-rail do otimizador on-demand |
| Motor de backtest | `backtest/simulator.py` + `walk_forward.py` | **Reusar c/ modo MVP-bruto** (desacoplar Risk/IR) + **estender multi-série** |
| Persistência tick/candle | `research_bars`/`research_ticks` + provenance | **Reusar** como ingestão canônica (já multi-símbolo) |
| Run/trade de backtest | `backtest/domain.py` (`BacktestRun`/`BacktestTrade`) | **Reusar** schema; **estender p/ trade multi-perna (par)** |
| MT5 plumbing | `mt5_integration/{ea_dispatcher,multi_ea_manager,fill_subscriber}` | **Reusar** p/ orquestrar EA executor multi-símbolo |
| EAs base | `mql5/experts/{cam_bridge,cam_risk_mirror}.mq5` | **Referência**; EA executor é **novo** (e multi-símbolo) |
| Padrão de UI | `features/quant-lab`, `features/inspetor` (SVG charts, react-query, MUI) | **Reusar** padrão p/ as 3 telas |

---

## 6. IN / OUT / LATER

### IN (MVP)
- **As 10 estratégias no escopo:** D1, D2, D3, V1, V2, S1, S2, LS1, LS2, LS3 *(escopo;
  construção incremental — ordem no PLAN)*.
- **Multi-símbolo / 2 pernas / ranking** (decisão verbatim do Founder): D3, LS1, LS2, LS3 (par) +
  S1 (cesta/ranking). No Python e na persistência é natural; **no EA é o ponto duro a resolver no
  ARCH** (§2.4, §8).
- **Assets Strategy:** lista/gestão das 10 estratégias + visualização/edição de parâmetros +
  **otimizador ON-DEMAND (grid/random + walk-forward) que SUGERE** com guard-rail anti-overfit.
- **Assets RunTests:** backtest matemático Python de **VALORES BRUTOS** (entrada/saída/gain/loss/
  volume bruto) **multi-série** + persistência de papel(éis)/ticks/indicadores + equity/trades/
  drawdown/métricas + walk-forward.
- **Assets Experts:** gestão de robôs MT5 + **EA executor multi-símbolo** (envia ordem no
  Strategy Tester/DEMO), preso a DEMO.
- **Contrato de estratégia única declarativo** (DSL) como fonte da verdade Py↔MQL5, **estendido
  para par/multi-símbolo**.
- **Paridade de LÓGICA + VALORES BRUTOS** Py↔EA (subconjunto C1–C14 sem C7/C8) + relatório
  PASS/FAIL.

### OUT (este ciclo)
- ❌ **Live trading em conta REAL** — só por ato explícito do Founder.
- ❌ **Assets RiskManager / kill switch / journal / fiscal** — outro módulo, fora deste SCOPE.
- ❌ **F1 (FII) e H1 (dividendos)** — buy&hold/total-return sem EA; módulo separado (Later).
- ❌ **Broker Profit / outros** — MT5 fixado neste ciclo.
- ❌ **Modelagem de aluguel/short real** (custo de BTC, disponibilidade) — coerente com MVP-bruto.

### LATER
- ⏳ **Custos, slippage, IR, fiscal** (C7/C8) — entram **depois** do MVP; aí a paridade vira
  "de fricção", o resultado vira **líquido**, e o backtest passa a responder "tem edge líquido?".
  **Crítico para as LS** (edge refém do custo).
- ⏳ **Codegen MQL5 automático** — quando a 2ª/3ª estratégia (e o multi-símbolo) justificarem o
  gerador. Com 10 estratégias, isso vem cedo.
- ⏳ **F1 (FII) e H1 (dividendos)** — módulo total-return separado, buy&hold, sem EA.
- ⏳ **Otimização avançada** (bayesiana/genética/multi-objetivo).
- ⏳ **Live forward / bridge ZeroMQ ao vivo para execução real.**

> **Removido do LATER (agora IN):** "escalar para 12 estratégias" e "multi-símbolo / 2 pernas no
> EA" — ambos promovidos a IN por decisão do Founder. Restam **10** no escopo (F1/H1 OUT).

---

## 7. Dependências técnicas e blocos por ambiente (alto nível — fino no PLAN)

| Bloco | Ambiente | Conteúdo (alto nível) | Depende de |
|---|---|---|---|
| **BL-DADOS** | DB / Python | Persistência **N papéis**/ticks/indicadores; reuso `research_*` + provenance; trade multi-perna | — (base existe) |
| **BL-CONTRATO** | Python | DSL como fonte única **+ extensão multi-símbolo/par**; subset C1–C14 sem custo | BL-DADOS |
| **BL-BACKTEST** | Python | Modo MVP-bruto do `simulator` (desacoplar Risk/IR) **+ multi-série** (sincronização N séries); equity/trades/métricas brutas | BL-CONTRATO |
| **BL-OTIM** | Python | Otimizador **on-demand** grid/random + guard-rail `validation.py` (DSR/WF/no-cliff) | BL-BACKTEST |
| **BL-EA** | MQL5 / MT5 | EA executor derivado da DSL; **multi-símbolo no Strategy Tester** (ponto duro); guard-rail conta DEMO | BL-CONTRATO |
| **BL-PARIDADE** | Python | Comparador trade-a-trade Py↔EA (lógica + valores brutos) + relatório PASS/FAIL; cobre par/multi-símbolo | BL-BACKTEST, BL-EA |
| **BL-FRONT** | React | 3 telas: Strategy (lista 10 + params + otimizador on-demand), RunTests (config multi-símbolo + equity + trades), Experts (robôs + EA) | BL-OTIM, BL-PARIDADE |

> Decomposição fina em TASKs é do **PLAN** (Nico) — incluindo a **ordem incremental** de
> construção das 10 estratégias. Aqui só a topologia e as dependências.

---

## 8. Riscos

| Risco | Tipo | Descrição | Mitigação |
|---|---|---|---|
| **Multi-símbolo no Strategy Tester** | **Factibilidade (ATIVO)** | O Strategy Tester do MT5 é single-symbol por padrão; D3/LS1/LS2/LS3 (2 pernas) e S1 (N símbolos) precisam de execução multi-símbolo no EA. **Não pode mais ser mitigado rebaixando p/ Python-only** (multi-símbolo é IN por decisão do Founder) | **ADR dedicado (Oscar)**: decidir entre `CopyRates`/`SymbolSelect` do símbolo secundário no tester (com caveats "every tick real ticks" + histórico do símbolo 2), validação multi-símbolo em DEMO ao vivo, ou sincronização por dados pré-carregados. **Risco a resolver no ARCH**, não impossibilidade |
| **Overfit do otimizador** | Confiança | Otimizador on-demand vira fábrica de ruído com UI bonita | DSR pelo nº de tentativas + walk-forward OOS + no-cliff **obrigatórios** (Jim/Nassim). On-demand reduz exposição; sugere, não aplica |
| **Falsa confiança do "valores brutos"** | Desejabilidade | Paridade verde + equity bonita lidos como "estratégia aprovada"; **LS parecem ótimas no bruto** (são refém do custo) | Registrar §3.5: MVP prova **mecânica/paridade**, não edge líquido. "Tem edge?" = Later. Alerta explícito nas LS |
| **Divergência silenciosa Py↔EA** | Factibilidade | Duas lógicas sutilmente diferentes — agravado por par/multi-símbolo (execução atômica das pernas) | DSL fonte única (multi-símbolo) + paridade trade-a-trade como gate (100% sinais, ≤1 tick, volume idêntico) cobrindo par |
| **DSL single→multi-símbolo** | Factibilidade | A DSL atual é single-asset; estendê-la p/ par/cesta é trabalho de design não-trivial | ADR de extensão da gramática (§4.3); par como unidade (C14) |
| **Acoplamento do backtester ao Risk/Constituição** | Factibilidade | `simulator.py` importa `_shared.risk` e provisiona IR; é single-symbol | Modo MVP-bruto desacoplado + extensão multi-série; não tocar o caminho Risk existente |
| **EA executor x isolamento** | Arquitetura | Execução não pode contaminar o backend research-only | Execução vive no MQL5; backend só orquestra via dispatcher (import-linter intacto). Multi-símbolo não viola |
| **Perna short (LS) no EA DEMO** | Factibilidade | LS têm perna short (venda descoberta/aluguel); tester permite SELL mas não modela aluguel | Coerente com MVP-bruto (sem custo de aluguel); registrar como simplificação consciente; aluguel real = Later |
| **Salto não-intencional p/ conta real** | Operacional | EA executor apontado p/ real por engano | Preso a DEMO por config + checagem de tipo de conta no EA |
| **Feature factory (10 estratégias de uma vez)** | Valor | Construir 10 estratégias × 3 módulos em paralelo = muito código, pouco aprendizado | **Ordem incremental no PLAN**: provar 1 fim-a-fim (D1 single-symbol) antes de paralelizar; gate de prova a cada salto de complexidade (single→par→cesta) (Marty/Voltaire) |

---

## 9. Perguntas abertas ao Founder (Q1–Q10 — REANALISADAS)

> Várias decisões já foram tomadas (estratégias, multi-símbolo, otimizador, valores brutos);
> as perguntas remanescentes são majoritariamente **técnicas / de ARCH**.

- [ ] **Q1 — Multi-símbolo no Strategy Tester (a pergunta mais dura):** o EA executor precisa
  rodar D3/LS (2 pernas) e S1 (N símbolos). Aceita que o **ARCH (Oscar) decida o mecanismo**
  — `CopyRates`/`SymbolSelect` do símbolo secundário no tester (com caveats), validação em DEMO
  ao vivo, ou pré-carga sincronizada? Há **preferência** sua por validar multi-símbolo **em DEMO
  ao vivo** (mais fiel) vs **no Strategy Tester** (mais reproduzível)?
  R: O oscar pode definir.
- [ ] **Q2 — Ordem de implementação incremental:** confirma que o **escopo são as 10**, mas a
  **construção é incremental** começando pela mais simples single-symbol (**D1**) para provar a
  arquitetura fim-a-fim, depois multi-símbolo (D3/LS), depois à vista (V/S)? (A ordem fina é do
  PLAN; aqui só confirmo o princípio "1 fim-a-fim antes de paralelizar".)
  R: ok podemos fazer d1, eu testo mo EA e backtest via CAM depois dou o ok para demais
- [ ] **Q3 — DSL fonte única vs dupla implementação:** adota **DSL declarativa como fonte única**
  (Oscar recomenda), estendida para **par/multi-símbolo**? E no MVP: `.mq5` **à mão derivado da
  DSL** para as primeiras, **codegen automático** depois — ou já quer o gerador desde o início
  (com 10 estratégias, o codegen se justifica mais cedo)?
  R: assim o codegen não teremos pela aplicação não quero dupla implementação Python para CAM e EA... vamos de backtests em 2 locais... redundancia para segurança
- [ ] **Q4 — Persistência: `research_*` vs `strategy_*`:** confirma **reusar `research_bars`/
  `research_ticks`** como ingestão canônica (provenance) e criar **só** o novo de domínio
  (`strategy_param_set`, trade multi-perna), em vez de tabelas `strategy_*` paralelas?
  R: Confirmo
- [ ] **Q5 — Indicadores: materializados vs on-the-fly:** no MVP, computar indicadores
  **on-the-fly** das barras canônicas (Ada recomenda — mais simples, menos drift), deixando
  materialização em tabela para **Later**?
  R: Indicadores on the fly... primeiro, se eu sentir falta materializamos em um 0.6.1
- [ ] **Q6 — Tolerância de paridade de lógica:** com C7/C8 fora, o alvo é **100% dos sinais
  coincidentes + preço ≤ 1 tick + volume financeiro idêntico**. Confirma esse alvo apertado
  como critério PASS do MVP?
  R:OK
- [ ] **Q7 — Convenção de barra/fuso:** confirmar barra canônica de `bars.py` (M1→TF) + fuso
  America/Sao_Paulo como regra única Py↔EA (sem default do broker/MT5), **idêntica para todos os
  símbolos de um par** (sincronização por timestamp).
  R: isso mesmo fuso sp é o padrão b3
- [ ] **Q8 — Pernas short (LS) no EA DEMO:** confirma que no MVP a **perna short** é simulada
  mecanicamente (tester permite SELL) **sem modelar aluguel/disponibilidade/custo de BTC** —
  coerente com valores brutos — e que aluguel real fica Later?
  R:OK 
- [ ] **Q9 — Otimizador on-demand:** confirma que **grid + random + walk-forward** é suficiente
  para o MVP, que ele **sugere (não aplica)**, e que é **acionado pelo usuário** (não roda
  automático em todo backtest)?
  R: OK
- [ ] **Q10 — Unidade de trade no par:** para D3/LS, o resultado deve exibir e contabilizar o
  **par como unidade** (gain/loss do spread agregado) **ou** as **duas pernas separadas** (P&L
  bruto de cada perna)? (Afeta UI, schema `backtest_trade` e o relatório de paridade.)
  R: Par como unidade se eu sentir falta peço separado.

---

## 10. Classificação P/M/G e próxima fase

**Classificação: G (Grande).**

Justificativa (tamanho/decomposição, **sem** modificadores de risco/segurança — proibidos):
- São **três módulos de produto** + **quatro peças novas/estendidas** (otimizador on-demand,
  modo-bruto **multi-série** do backtester, **DSL multi-símbolo**, **EA executor multi-símbolo**)
  + **camada de paridade**, atravessando **três ambientes** (Python/FastAPI, React, MQL5/MT5) que
  precisam concordar numericamente — agora sobre **10 estratégias**, **5 multi-símbolo**.
- Exige **decomposição em TASKs** no PLAN (ver blocos §7) **e ordem incremental** das 10.
- Tem **decisões arquiteturais abertas** estruturantes: DSL fonte única **+ multi-símbolo** (Q3),
  e **multi-símbolo no Strategy Tester** (Q1) — esta última é nova e pesada.

> **Por que é mais G que o v0.6:** a ampliação para 10 estratégias e, sobretudo, **multi-símbolo
> IN** (incluindo no EA/Strategy Tester) **aumentam** o G face à v0.6. O atenuante do MVP-bruto
> e do alto reuso (DSL, bars, validation, simulator, mt5_integration já existem) **permanece** —
> mas a largura cresceu (4 estratégias 2-pernas + 1 ranking) e surgiu um **risco de
> factibilidade ativo** no EA. Continua **G**. Nico pode contestar no PLAN (loop P/M/G).

**Próxima fase recomendada: ARCH (Oscar) — com foco em 3 ADRs (era 2).**

1. **ADR — Contrato de estratégia única (DSL) + extensão multi-símbolo/par:** DSL declarativa
   como fonte da verdade; gramática para par/cesta (par como unidade — C14); codegen MQL5 vs
   `.mq5` à mão derivado da DSL no MVP (faseado, mas codegen mais cedo com 10 estratégias).
2. **ADR — Persistência + modo MVP-bruto **multi-série** do backtester:** reuso `research_*` vs
   `strategy_*`; trade multi-perna (par); desacoplamento do `simulator` de Risk Engine/IR;
   sincronização de N séries por timestamp; indicadores materializados vs on-the-fly.
3. **ADR — Execução multi-símbolo do EA no MT5 (NOVO — o ponto duro):** como o EA executor roda
   estratégias de 2 pernas / N símbolos no **Strategy Tester** (caveats de `CopyRates`/
   `SymbolSelect`, modo "every tick real ticks", histórico do símbolo secundário) vs validação em
   **DEMO ao vivo**; execução atômica das pernas; guard-rail conta DEMO; tratamento da perna short.

Demais itens (paridade trade-a-trade de valores brutos, tolerância) podem ir direto ao SPEC após
esses 3 ADRs.

- [x] **Avançar para ARCH** (3 ADRs) → depois SPEC (Albert) → PLAN (Nico, com ordem incremental)
- [ ] Incubar · [ ] Descartar · [ ] Investigar mais

**Quem decide:** Founder · **Quando:** _(pendente)_

---

## 11. A pergunta dura (Voltaire ⚔️)

> Voltaire não questiona a stack (território da Grace) — questiona a **direção**.

**Três inversões antes de o Founder aprovar (atualizadas à luz das 4 decisões):**

1. **10 estratégias no escopo — ou 10 chances de não terminar nenhuma?** O Founder ampliou de
   D1 para 10. Defensável: o filtro de estratégias já foi feito (catálogo), e ter o escopo claro
   evita re-decidir. **Mas o risco mudou de "feature factory" para "frente larga demais".** A
   única defesa honesta é a **ordem incremental com gate de prova**: 1 fim-a-fim (single-symbol)
   → par → cesta. **Inversão:** se você não consegue se comprometer com "não começo a 5ª
   estratégia antes da 1ª bater paridade", o escopo de 10 vira uma lista de desejos, não um plano.
   O SCOPE registra 10; a **disciplina de ordem** é sua, no gate do PLAN.

2. **Multi-símbolo no EA — você quer a feature, ou aceita o caveat?** Multi-símbolo é IN, e o
   ponto duro é o **Strategy Tester single-symbol**. Há uma escolha honesta escondida aqui: o
   multi-símbolo **fiel** roda melhor em **DEMO ao vivo** que no Strategy Tester. **Inversão:**
   se a paridade perfeita no Strategy Tester for difícil/impossível para os pares, você aceita
   **validar os multi-símbolo em DEMO ao vivo** (menos reproduzível, mais fiel) e reservar o
   Strategy Tester para os single-symbol? Decida isso **antes** de cobrar paridade trade-a-trade
   perfeita de um D3 no tester.

3. **"Valores brutos" simplifica o MVP — ou esconde a única pergunta que importa?** Tirar custo
   torna a paridade fácil e a equity bonita. Mas a pergunta que decide se TCaM é produto ou
   brinquedo é **"sobra dinheiro depois do custo?"** — e essa você adiou. **Crítico nas LS:**
   LS1/LS3 são, pelo próprio catálogo, **refém do custo** — no bruto elas vão brilhar, e isso é
   **enganoso por construção**. **Inversão:** está construindo a parte fácil primeiro porque é a
   ordem de engenharia correta (mecânica/paridade antes de edge líquido — defensável), ou porque
   é a confortável? A linha defensável existe — **desde que ninguém confunda "paridade verde no
   bruto" com "estratégia que ganha"**, especialmente nas LS. Mantenha essa linha visível, ou o
   MVP vira teatro.

> **Voltaire encerra:** aprovar este SCOPE é defensável. Mas aprove sabendo que você está
> comprando **mecânica + paridade de 10 estratégias em valores brutos**, não um cassino que dá
> lucro. A hora de dizer "sem custo" é agora; a hora de pagar essa conta é quando custos e IR
> entrarem (Later). A pergunta que fica: **o que você faz no dia em que LS3 bate paridade
> perfeita no bruto e, com 4 boletas + IR, não sobra nada?**

---

## 12. Referências

- Catálogo 12 estratégias: [`./CATALOGO-12-ESTRATEGIAS-ELEITAS.md`](./CATALOGO-12-ESTRATEGIAS-ELEITAS.md)
- Contrato edge/paridade (Jim): [`./EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md`](./EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md)
- SCOPE anterior (insumo, superseded-parcial): [`./SCOPE-STRATLAB-PARITY-001.md`](./SCOPE-STRATLAB-PARITY-001.md)
- Mapa dos módulos Assets*: [`../../MAP-MODULES-TCaM.md`](../../MAP-MODULES-TCaM.md)
- Pivot p/ produto: [`../../PIVOT-TCaM-STRATEGY.md`](../../PIVOT-TCaM-STRATEGY.md) · [`../../CONSTITUTION-DECOMMISSION.md`](../../CONSTITUTION-DECOMMISSION.md)
- Código real reaproveitável: `apps/cam-cockpit/backend/cam/features/{strategies/dsl, backtest, research/leadlag, mt5_integration}` · `apps/cam-cockpit/mql5/experts/`

---

> **Modo:** TCaM / produto · Constituição descomissionada · MVP de valores brutos · multi-símbolo
> IN · 10 estratégias no escopo · rigor de engenharia mantido · personas consultadas: Marty
> (escopo), Oscar (arch), Jim (quant), Nassim (lente risco), Ada (dados), Nikola (eng — EA
> multi-símbolo), Don/Peter (UX implícito nas 3 telas), Voltaire (challenger).
> **Leo consolida. O Founder decide.** · 2026-06-03 · v0.7 (reanálise sob 4 decisões do Founder)

---
template: EDGE-CONTRATO-VALIDACAO
phase: research (estudo livre)
status: Draft 1.0
produto: CaM
escopo: contrato de edge + paridade Python ↔ EA MetaTrader 5
data: 2026-06-03
lead: Jim (quant/edge)
co: Nassim (risco/sizing), Luca (custos/fiscal), Voltaire (devil's advocate), Founder (gate)
vinculacao: Constituição Arts. 28º–30º (gates por evidência) — trava DESLIGADA neste estudo, rigor mantido
aviso: research-only. Define o que é "edge provado" e o contrato que Python e EA devem cumprir
       para um ser espelho fiável do outro. Não é tese aprovada nem ordem de execução.
---

# EDGE / CONTRATO DE VALIDAÇÃO — Espelho Python ↔ EA MetaTrader 5

> **Jim:** Duas implementações da mesma estratégia que produzem resultados diferentes não
> são duas estratégias — são uma estratégia e um bug. Este documento existe para que,
> quando o Founder rodar a mesma lógica no Python e no EA MT5, qualquer divergência seja
> tratada como **defeito a investigar**, não como "variação natural de ambiente".
>
> **Princípio-mãe:** *o backtest e o live só são comparáveis se forem o MESMO experimento.*
> Tudo abaixo é a definição operacional de "mesmo experimento".

---

## 0. Escopo e fronteira

- **Cobertura:** famílias **D** (derivativo intraday), **V** (ação à vista curto/intraday),
  **S** (ação à vista swing) e **LS** (long & short). As famílias **F** (FII) e **H**
  (holding dividendos) são Carteira Hard, **não têm EA** e ficam fora deste contrato.
- **Dois ambientes, um contrato:**
  - **Python** — Strategy & Backtest Analyser do CaM (research, validação, Evidence Pack).
    É o **ambiente de prova**.
  - **EA MT5** — Expert Advisor em MQL5 (execução/forward em MT5, hoje DEMO).
    É o **ambiente de operação**.
- **Relação canônica:** o **Python é a fonte da verdade do edge**; o **EA é o espelho
  executável**. Se divergirem, a hipótese padrão é *o EA está errado* — até que se prove
  que o erro está no Python (acontece, e é igualmente bug).
- **Fora de escopo aqui:** a tese de edge de cada estratégia (vive nos EDGE-THESIS por
  família) e o dimensionamento de ruína (Nassim, R-08). Este doc define **edge + paridade**,
  não o conteúdo de cada estratégia.

---

## 1. Definição de edge no CaM

> Reaproveita a régua anti-data-snooping do catálogo (§II) e a eleva a contrato formal.
> **Edge não é win rate. Edge é expectância líquida positiva fora de amostra, robusta e
> não explicável por sorte.**

Uma estratégia tem **edge provado no CaM** quando **TODAS** as condições abaixo são verdes
**simultaneamente**. Qualquer uma vermelha → **sem edge, não promove**.

| # | Condição | Critério objetivo (passa) | Reprova se |
|---|---|---|---|
| **E1** | **Expectância líquida OOS** | Expectância por trade **> 0 em R**, líquida de custos + IR, medida **out-of-sample** (walk-forward), não in-sample | ≤ 0 OOS |
| **E2** | **Nº mínimo de trades OOS** | **≥ 200 trades** out-of-sample (significância). Para swing (S/LS-swing), aceitar ≥ 100 **se** cobrir ≥ 3 anos e ≥ 2 regimes | < 100 OOS |
| **E3** | **Deflated Sharpe Ratio (DSR)** | **DSR > 0** considerando o nº de configurações testadas (penaliza data-snooping). Reportar nº de tentativas | DSR ≤ 0 |
| **E4** | **Walk-forward** | **≥ 60%** das janelas OOS com **expectância líquida positiva**; degradação de Sharpe in-sample → OOS **≤ 50%** | < 60% janelas positivas, ou colapso OOS |
| **E5** | **Robustez de parâmetro (no-cliff)** | Superfície de desempenho em torno do parâmetro escolhido é **chata, não um pico**: variar cada parâmetro-chave ±1 passo mantém expectância líquida positiva | Penhasco — desempenho desaba ao mover 1 passo |
| **E6** | **Custo no pior quartil** | Expectância líquida ainda **> 0** quando custos (slippage, corretagem, emolumentos) são fixados no **pior quartil histórico**, não na média | Vira ≤ 0 sob custo de pior quartil |
| **E7** | **Não é beta disfarçado** | Para V/S/LS: edge sobrevive ao controle por Ibov/fator. Para D: edge não some quando se remove tendência do dia | Some ao controlar por beta/tendência |
| **E8** | **Paridade Py↔EA** | Espelho aprovado conforme §5 deste documento (sem paridade, o "edge do Python" não é o que o EA vai operar) | Divergência fora de tolerância (§5) |

> **Jim:** E1–E7 provam que a vantagem existe. E8 prova que a vantagem **é a que será
> operada**. Um edge real no Python que não passa em E8 é um edge que você **não tem** —
> porque não é ele que vai pra mesa.

**Anti-padrões que NÃO contam como edge (rejeição automática):**
- Win rate alto com R:R invertido sem teste de cauda (a sereia — ver D2/LS1/LS3 no catálogo).
- Backtest in-sample sem walk-forward.
- Métrica bruta (antes de custo + IR).
- Curva de equity bonita sem nº de trades suficiente.
- Parâmetro "ótimo" encontrado por varredura sem reportar quantas combinações foram testadas (E3).

---

## 2. Pipeline de validação

> Cada etapa tem critério de passa/reprova. **Reprovou → volta uma etapa ou descarta.**
> Promoção de status é **gate do Founder** (Art. 30º) — Jim entrega evidência, não promove.

```
[T] Tese de edge
      │  passa: hipótese falsificável + de-quem-ganha + regime (Ray) + custo estimado
      ▼
[B] Backtest in-sample (Python)
      │  passa: expectância líquida > 0; lógica determinística; sem look-ahead
      ▼
[W] Walk-forward OOS (Python)
      │  passa: E1–E7 verdes (expectância OOS, ≥200 trades, DSR>0, ≥60% janelas, no-cliff, pior quartil, não-beta)
      ▼
[P] Paridade Python ↔ EA MT5
      │  passa: E8 verde — espelho dentro da tolerância (§5) sobre o MESMO período/dados
      ▼
[EP] Evidence Pack
      │  passa: pacote completo (§2.6) reprodutível, com seeds e versões
      ▼
[⛔ GATE Founder]  →  promoção no Strategy Lifecycle (Arts. 28º–30º)
```

### 2.1 [T] Tese de edge — passa/reprova
- **Passa:** hipótese falsificável (de quem ganha, em que regime, por quê), faixa de custo
  estimada, e ao menos um **modo de falha** nomeado (Voltaire).
- **Reprova:** "ganha porque sobe", sem contraparte, sem regime adverso.

### 2.2 [B] Backtest in-sample (Python) — passa/reprova
- **Passa:** expectância líquida in-sample > 0; pipeline determinístico; **zero look-ahead**
  (sinal no fechamento da barra `t` só pode usar dados ≤ `t`).
- **Reprova:** look-ahead detectado, ou expectância in-sample já ≤ 0 (não adianta seguir).

### 2.3 [W] Walk-forward OOS (Python) — passa/reprova
- **Passa:** E1–E7 (§1) todos verdes. Janelas roladas (ex.: treina 12m / testa 3m,
  avança 3m), parâmetros congelados por janela.
- **Reprova:** qualquer E1–E7 vermelho → estratégia volta para [T] ou é descartada.

### 2.4 [P] Paridade Python ↔ EA MT5 — passa/reprova
- **Passa:** E8 verde — EA reproduz os trades do Python dentro da tolerância (§5), sobre
  **o mesmo período e os mesmos dados**.
- **Reprova:** divergência fora de tolerância → **abre BUG** (skill `teczi-bug-fix`).
  Não se prossegue com espelho quebrado.

### 2.5 [EP] Evidence Pack — passa/reprova
- **Passa:** pacote §2.6 completo e **reprodutível** por terceiro a partir dos artefatos.
- **Reprova:** falta seed, versão, dataset ou métrica → pacote incompleto, não vai a gate.

### 2.6 Conteúdo mínimo do Evidence Pack
1. Tese ([T]) + modos de falha (Voltaire).
2. Dataset usado: fonte, período, ativo, granularidade, hash/provenance (Ada/Wyck).
3. Config exata (parâmetros congelados) + **nº de combinações testadas** (para o DSR).
4. Resultados in-sample e OOS no **formato canônico de métricas** (§4).
5. Relatório walk-forward (janelas, expectância por janela, degradação).
6. Teste de robustez (mapa de calor no-cliff E5) e custo de pior quartil (E6).
7. **Relatório de paridade Py↔EA** (§5): trade-a-trade + métricas lado a lado + veredito.
8. Sizing e cauda (Nassim) — risco por trade, drawdown, risco de ruína.
9. Custos e IR aplicados (Luca) — resultado **sempre líquido** (Art. 25º).
10. Versões: commit do Python, versão do `.mq5`, build do MT5, seeds.

---

## 3. Contrato de paridade Python ↔ EA MT5 (núcleo)

> **Esta é a parte central.** Para o EA ser espelho fiável do Python, os itens abaixo
> **precisam ser idênticos por construção** — não "parecidos". Cada item tem uma **regra
> canônica única** que **ambos** os ambientes implementam. Onde Python e EA têm
> comportamento default diferente, **o default é proibido** e a regra canônica vence.

### Tabela-mestra do contrato

| # | Elemento | Regra canônica (ambos seguem **exatamente** isto) |
|---|---|---|
| **C1** | **Definição de barra** | Barra OHLC fechada, timeframe explícito por família (§6). Uma barra é identificada pelo **timestamp de ABERTURA**. Barra só "existe" para decisão quando **fechada**. Proibido decidir com barra em formação. |
| **C2** | **Timestamp / relógio** | Toda barra carimbada pelo **horário de abertura** no fuso **America/Sao_Paulo** (horário do pregão B3). Python converte tudo para esse fuso na ingestão; EA usa o tempo do servidor MT5 **normalizado para horário B3** (não o tempo do broker cru). DST: B3 não tem horário de verão desde 2019 — fixar offset, nunca confiar em conversão automática do broker. |
| **C3** | **Ordem de avaliação de sinais** | Sequência fixa e idêntica, executada **uma vez por barra fechada**: (1) atualizar indicadores com barra `t`; (2) checar **saídas** (stop/alvo/tempo/sessão) da posição aberta; (3) checar **entradas**; (4) aplicar filtros (regime, horário, macro); (5) aplicar gate de risco (sizing/limites). **Saída sempre antes de entrada.** Nunca inverter. |
| **C4** | **Modelo de preenchimento (fill)** | **Regra canônica: fill na ABERTURA da barra `t+1`** (`next-bar-open`). O sinal nasce no fechamento de `t`; a ordem é preenchida no open de `t+1`. **Proibido fill no close da própria barra de sinal** (look-ahead). Vale para entrada e saída por sinal. Stop/alvo intrabar → ver C5. |
| **C5** | **Stop e alvo intrabar** | Stop/alvo são níveis de preço, podem disparar **dentro** da barra. Regra canônica de resolução intrabar: **assume-se o pior caso** — se na mesma barra o range tocou stop **e** alvo, considera-se **stop primeiro** (conservador). Preço de execução do stop/alvo = **o nível exato** (sem melhora otimista). Slippage adicional aplicado conforme C7. |
| **C6** | **Tratamento de gap / lacuna** | Se o open de `t+1` **ultrapassa** o nível de stop/alvo (gap), executa-se **no open real**, não no nível teórico (modela slippage de gap honestamente — pior para o trade). Em ações (V/S/LS), gap de abertura é a regra, não exceção: stop "saltado" preenche no open. Sem assumir que o nível foi respeitado. |
| **C7** | **Modelo de custo** | **Idêntico nos dois ambientes**, parametrizado num **único arquivo de custos** (fonte única, lido pelo Python e espelhado nas `input` do EA): corretagem, emolumentos B3 (por contrato/lado em D/LS-deriv; % do volume em V/S/LS-ações), ISS quando aplicável, aluguel/short (LS à vista), e **slippage** (em ticks). Slippage canônico para validação de edge = **pior quartil** (E6). Para o relatório de paridade, usar o **mesmo** valor de slippage nos dois lados (senão não há como comparar). |
| **C8** | **Impostos (IR)** | Aplicado no resultado, **sempre líquido** (Art. 25º): day trade D/V/LS-intraday = **20%** + IRRF; swing ações S/LS-swing = **15%** (modelar isenção R$ 20k/mês quando aplicável); compensação de prejuízo conforme Luca. EA e Python usam a **mesma** rotina de apuração (espelhada). |
| **C9** | **Sizing / position sizing** | Função de sizing **idêntica e determinística**: dado capital, risco-por-trade (R) e distância de stop → mesma quantidade. **Sem arredondamento divergente:** definir a regra de arredondamento de lote/contrato (ex.: `floor` para inteiro) e usá-la nos dois. No estudo livre o limite de 2 contratos está desligado, mas a **fórmula** de sizing é a mesma. |
| **C10** | **Stop / alvo / trailing** | Mesma definição numérica e mesma mecânica de atualização. Trailing/break-even avaliados **uma vez por barra fechada** (C1/C3), nunca tick-a-tick num lado e por barra no outro. Se a estratégia usa trailing, ele é **mecânico e idêntico** — saída discricionária é proibida na versão validada (mata a paridade). |
| **C11** | **Fuso e sessão** | Janela operacional definida em **horário B3** (§6 por família). Abertura/fechamento de pregão, janelas vedadas e horário de eventos macro são os **mesmos** carimbos nos dois ambientes. Posição intraday (D/V/LS-intraday) **fecha compulsoriamente** no mesmo horário nos dois. |
| **C12** | **Sementes / determinismo** | Pipeline **determinístico**: mesma entrada → mesma saída, sempre. Onde houver aleatoriedade (ex.: Monte Carlo de cauda), **seed fixa e registrada**. EA é determinístico por barra. Proibido qualquer componente não-reproduzível na lógica de decisão. |
| **C13** | **Dados de entrada** | **Mesmo dataset** na validação de paridade: mesma fonte, mesmo período, mesma granularidade, mesmo tratamento de ajustes (proventos/desdobramentos em V/S/LS — ajustar ou não, mas **igual** nos dois). Provenance obrigatória (Ada/Wyck). Divergência de dados invalida o teste de paridade antes de qualquer métrica. |
| **C14** | **Estado e contabilização** | Uma posição por estratégia/instrumento (salvo LS, que tem 2 pernas — então **par** é a unidade). Mesma convenção de marcação (a mercado, no close da barra) e mesmo momento de realização de P&L. Trade contabilizado quando **fecha**, com o mesmo preço de saída resolvido por C4–C6. |

### 3.1 Princípio de resolução de conflito de default
Quando o backtester do MT5 (Strategy Tester) e o Python têm comportamentos default
diferentes (ex.: modelo de tick, fill default, fuso do broker), **nenhum default é
aceito**: define-se a regra canônica acima e **ambos são forçados a ela**. O EA não deve
depender de configuração de modelagem do Strategy Tester que o Python não consiga
reproduzir.

> **Jim:** o inimigo silencioso da paridade é o **default**. O MT5 preenche de um jeito, o
> seu loop em Python de outro, e os dois "funcionam" — divergindo. C1–C14 existem para
> matar todo default não-declarado.

---

## 4. Métricas canônicas

> **Lista única.** Os dois ambientes reportam **estas** métricas, com **estas** definições
> e **este** formato, para permitir comparação lado a lado. Tudo **líquido** (Art. 25º).

| Métrica | Definição canônica | Unidade |
|---|---|---|
| **Net Expectancy (R)** | `(WR × média_ganho_R) − ((1−WR) × média_perda_R)`, líquido de custo+IR | R por trade |
| **Profit Factor** | soma de ganhos líquidos ÷ soma de perdas líquidas (abs) | razão |
| **Win Rate** | trades vencedores ÷ total de trades | % |
| **Payoff (R:R médio)** | média de ganho ÷ média de perda (em módulo) | razão |
| **Nº de trades** | total de trades fechados (e o subtotal **OOS**) | inteiro |
| **Max Drawdown** | maior queda de pico a vale da curva de equity líquida | % e em R$ |
| **Sharpe (anualizado)** | sobre retornos por barra/dia, anualizado por √(períodos/ano) | razão |
| **DSR (Deflated Sharpe)** | Sharpe deflacionado pelo nº de tentativas (E3) | razão |
| **Expectância líquida total** | soma do P&L líquido do período | R$ |
| **Tempo médio em posição** | média de duração dos trades | minutos (D/V/LS-intraday) / dias (S/LS-swing) |
| **Pior trade / pior cluster** | maior perda única e maior sequência de perdas | R / R |

**Formato de troca (obrigatório nos dois ambientes):** um **CSV/JSON de trades** com schema
fixo — `trade_id, instrumento, lado, timestamp_entrada, preço_entrada, timestamp_saída,
preço_saída, qtd, motivo_saída, custo, ir, pnl_bruto, pnl_liquido_R, pnl_liquido_BRL`.
A partir desse ledger de trades, **ambos** calculam as métricas com a **mesma** rotina
(idealmente a rotina de métricas é código Python único, alimentado tanto pelo backtest
Python quanto pelo export de trades do EA). Métrica nunca é recalculada "do jeito do MT5".

---

## 5. Critério de aprovação do parity

> **Divergência = bug até prova em contrário.** A pergunta não é "deu parecido?" — é
> "bateu dentro da tolerância declarada, e o resíduo tem explicação física?".

### 5.1 Pré-condição (senão o teste nem roda)
- Mesmo dataset (C13), mesmo período, mesma config, mesmo arquivo de custos (C7), mesmo
  slippage nos dois lados. Sem isso, qualquer comparação é inválida.

### 5.2 Camada 1 — Paridade trade-a-trade (a mais forte)
Compara o ledger de trades dos dois ambientes, trade a trade, **alinhados por barra de
sinal**.

| Dimensão | Tolerância (passa) | Ação se exceder |
|---|---|---|
| **Mesmos sinais** | **100%** dos sinais coincidem (mesma barra, mesmo lado) | Divergência de sinal = **bug duro**. Investiga C1/C3/C4 antes de tudo |
| **Preço de entrada/saída** | diferença ≤ **1 tick** do instrumento (resíduo de arredondamento) | > 1 tick → investiga C4/C5/C6 (fill/gap) |
| **Qtd / sizing** | **idêntica** | Diferença = bug em C9 (arredondamento) |
| **Motivo de saída** | **idêntico** (stop/alvo/tempo/sessão) | Diferente = bug em C3/C10/C11 |

> Camada 1 é o **padrão-ouro**. Se 100% dos sinais batem e preços ficam dentro de 1 tick,
> o espelho é fiável. Qualquer sinal que aparece num ambiente e não no outro é
> **defeito**, não ruído.

### 5.3 Camada 2 — Paridade de métricas agregadas (rede de segurança)
Quando o trade-a-trade tem resíduo aceitável (≤ 1 tick), as métricas agregadas devem cair
dentro de:

| Métrica | Tolerância (passa) |
|---|---|
| Net Expectancy (R) | ≤ **2%** de diferença relativa |
| Profit Factor | ≤ **2%** |
| Win Rate | ≤ **1 ponto percentual** |
| Nº de trades | **idêntico** (Camada 1 já garante) |
| Max Drawdown | ≤ **3%** relativo |
| Sharpe | ≤ **5%** relativo |

### 5.4 Veredito
- **PASS:** Camada 1 com 100% de sinais coincidentes + preços ≤ 1 tick **e** Camada 2
  dentro das tolerâncias. → espelho aprovado (E8 verde).
- **FAIL:** qualquer sinal divergente, ou preço > 1 tick sem explicação, ou métrica fora
  da tolerância. → **abre BUG** (`teczi-bug-fix`), classifica a causa por item C1–C14, e
  **não promove** a estratégia até o espelho fechar.

### 5.5 Protocolo de divergência (a regra de ouro)
1. **Divergência é bug, não "característica do ambiente".** Ônus da prova é mostrar que o
   resíduo é fisicamente inevitável (ex.: arredondamento de tick), não um erro de lógica.
2. **Investigar na ordem do pipeline de decisão (C3):** dados (C13) → barra/fuso (C1/C2) →
   ordem de avaliação (C3) → fill/gap (C4–C6) → custo/IR (C7/C8) → sizing (C9) →
   stop/alvo/sessão (C10/C11).
3. **Resíduo aceitável** só existe se for: (a) arredondamento de tick documentado, ou
   (b) diferença de custo declarada e idêntica em magnitude esperada. Tudo além disso é bug.
4. **Nunca "calibrar" um ambiente para casar com o outro escondendo a causa.** Ajustar
   sem entender a causa transforma o espelho numa ilusão e contamina o Evidence Pack.

> **Jim:** se você precisa "tunar" o EA para bater com o Python sem saber por quê, você não
> tem um espelho — tem dois experimentos parecidos e uma falsa sensação de validação. Isso
> é pior que não ter paridade, porque mente pra você no momento de promover.

---

## 6. Notas per-família

> O que **cada família precisa provar a mais**, além de E1–E8. Famílias do catálogo:
> **D** (D1/D2/D3), **V** (V1/V2), **S** (S1/S2), **LS** (LS1/LS2/LS3).

### D — Derivativo intraday (WIN/WDO)
- **TF/sessão canônicos:** intraday puro, **zero overnight**; fechamento compulsório de
  posição no horário B3 (C11) idêntico nos dois ambientes.
- **Prova a mais:**
  - **Custo domina o edge** (tick WDO = R$ 5; IR 20% + IRRF). E6 (pior quartil de slippage)
    é **eliminatório**, não opcional.
  - **Intrabar é onde o espelho quebra:** stop e alvo na mesma barra (C5) e gap de abertura
    intraday (C6) precisam de **paridade trade-a-trade impecável** — derivativo tem muitos
    trades, qualquer viés intrabar acumula.
  - **D2 (mean-reversion) e a sereia do WR alto:** provar a **cauda** (pior cluster), não a
    média. DSR rigoroso. Hard-block de eventos macro idêntico nos dois (C11).
  - **D3 (lead-lag WIN×WDO):** **duas pernas, dois books** — a paridade precisa cobrir
    execução simultânea; perna solta vira direcional não-intencional. Tratar como par (C14).

### V — Ação à vista curto/intraday
- **Prova a mais:**
  - **Gap de abertura é a regra** (C6): em ações o stop overnight/abertura quase sempre
    preenche no open, não no nível. O EA e o Python têm que tratar isto igual ou divergem
    sistematicamente.
  - **Ajuste de proventos/desdobramentos** (C13): definir e **igualar** o tratamento — série
    ajustada vs não-ajustada muda sinais. Divergência aqui é causa nº 1 de quebra de paridade
    em ações.
  - **Custo unitário pior** que derivativo; **selection bias** (V1 gap-and-go): universo
    **fixo ex-ante**, watchlist congelada antes do backtest, idêntica no EA.
  - **IR:** day trade ação = 20%; se a posição vira swing, muda regime fiscal (C8) — a
    rotina de IR precisa classificar igual nos dois.

### S — Ação à vista swing
- **Prova a mais:**
  - **Nº de trades menor** → E2 relaxa para ≥ 100 **mas exige ≥ 3 anos e ≥ 2 regimes**.
    Cuidado redobrado com DSR (poucos trades → fácil snooping).
  - **Mecanização total** (S2 pullback): definição de tendência/suporte/saída **inviolável e
    por regra** — discricionariedade mata a paridade (C10). Se há "olho humano" no Python,
    o EA não consegue espelhar.
  - **Isenção fiscal R$ 20k/mês** e IR 15% (C8) modelados igual.
  - **Momentum crash (S1):** filtro de vol idêntico; provar que não é beta (E7).
  - Barra diária (C1) e fuso (C2/C11): rebalance no **mesmo** carimbo de tempo.

### LS — Long & short
- **Unidade é o PAR, não a perna** (C14): entrada/saída/contabilização das duas pernas
  resolvidas no mesmo momento e com a mesma regra de fill (C4–C6).
- **Prova a mais:**
  - **Custo dobrado** (4 boletas, 2 IRs, 2 slippages — LS1/LS3): E6 é decisivo; edge fino
    raramente sobrevive.
  - **Cauda conjunta** (Nassim §IV): as duas pernas perdem juntas em choque — o backtest
    **tem que incluir** os períodos de quebra de correlação/cointegração. Paridade na
    **resolução de perna solta** (gap numa perna e não na outra — C6) é crítica.
  - **LS2 (cointegração, swing):** reteste de estacionariedade idêntico nos dois;
    **survivorship bias** proibido — incluir pares que quebraram. Aluguel BTC (custo
    invisível) modelado e igual.
  - **LS3 (ON×PN intraday):** spread estreito → **viabilidade refém do custo**; a paridade
    de **modelo de custo/aluguel/short intradiário** (C7) é o item mais sensível — diferença
    de fricção entre Python e EA inverte o sinal do edge. Kill de fechamento (C11) e stop de
    evento idênticos. Zera no fechamento nos dois.
  - **Risco-por-trade ≤ 0,25–0,5%** (Nassim): mesma fórmula de sizing (C9) por par.

---

## 7. Resumo executivo (uma página)

- **Edge no CaM = E1–E8 verdes.** Expectância líquida OOS positiva, ≥200 trades, DSR>0,
  walk-forward ≥60% janelas, no-cliff, sobrevive ao pior quartil de custo, não é beta — **e**
  passa na paridade Py↔EA.
- **Python prova o edge; EA espelha.** Divergência entre eles é **bug até prova em contrário**.
- **C1–C14** definem o "mesmo experimento": barra, fuso, ordem de avaliação, fill `next-bar-open`,
  intrabar pior-caso, gap honesto, custo/IR idênticos por arquivo único, sizing determinístico,
  stop/alvo mecânicos, sessão B3, determinismo, mesmo dataset, par como unidade.
- **Métricas canônicas** (§4) saem de um **ledger de trades de schema único**, calculadas pela
  **mesma rotina** nos dois lados.
- **Paridade aprova** com 100% de sinais coincidentes + preços ≤ 1 tick (Camada 1) e métricas
  dentro de ≤2% expectância / ≤1pp WR / ≤3% DD (Camada 2). Senão, **abre BUG**.
- **Sem paridade fiável, o "edge do Python" não é o que o EA opera — logo, não é edge.**

---

> **Fronteira reafirmada:** este documento é estudo livre (trava constitucional desligada),
> mas o rigor anti-data-snooping não se desliga. Qualquer estratégia que um dia entre no CaM
> real volta aos gates dos Arts. 28º–30º e ao Risk Engine. Jim prova o *se* (edge líquido OOS
> + paridade). Nassim desenha o freio. Luca garante o líquido. **O Founder decide.**
>
> Research-only · Estudo livre · 2026-06-03 · Lead: Jim 🧪
>
> **Referências:** [Catálogo das 12 estratégias](../../strategies/CATALOGO-12-ESTRATEGIAS-ELEITAS.md) ·
> [SCOPE STRATLAB-PARITY-001](../scopes/SCOPE-STRATLAB-PARITY-001.md) ·
> [ARCH-NOTE paridade (Oscar)](../analysis/ARCH-NOTE-PARIDADE-EA-PYTHON.md)

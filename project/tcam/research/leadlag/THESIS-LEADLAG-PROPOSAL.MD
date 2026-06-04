---
template: THESIS-PROPOSAL
phase: P&D / Research Lane
status: Draft 1.0 — proposta pré-DevFlow (hipótese 2)
produto: CaM
codinome: research-cubo-leadlag
vive_em: project/cam-cockpit/research/THESIS-LEADLAG-PROPOSAL.MD
data: 2026-06-03
lead: Leo
co_participacao: Jim (quant), Ada (dados), Nassim (risco), Don (UX), Kevin (segurança), Voltaire (challenger)
baseado_em:
  - project/cam-cockpit/research/EDGE-THESIS-LEADLAG-CUBE.md
  - project/cam-cockpit/research/CaM-RESEARCH-CUBO-LEADLAG.md
  - project/cam-cockpit/research/CaM-SCOPE-FRONTEND-CUBO.md
  - project/cam-cockpit/research/THESIS-ANALYSIS-01.MD
gate: Founder pendente
---

# THESIS-LEADLAG-PROPOSAL — Cubo de Lead-Lag em Dois Modos de Bar-Time

> Proposta de research **pré-DevFlow**. Reformula a tese do Cubo a pedido do Founder:
> o lead-lag deve funcionar em **dois modos de bar-time** — **intraday** e **swing** —
> fechando os gaps levantados em `THESIS-ANALYSIS-01.MD`. Este documento **não promove
> estratégia**, **não recomenda execução**, **não aciona paper/live**, **não parametriza
> Risk Engine** e **não justifica exceção constitucional**. Research-only.

---

## 1. O que muda em relação à hipótese 1

A tese 1 separava **Cubo Rápido** (event-time/tick/OFI) de **Cubo Lento** (bar-time/estrutura).

A hipótese 2 **reorganiza a espinha**: o Cubo passa a operar em **dois modos de bar-time**, distinguidos por escala temporal, com **H1 como fronteira compartilhada**.

| Modo | Timeframes | Mecanismo econômico dominante | Camada OFI/tick |
|---|---|---|---|
| **INTRADAY** | M1, M5, M15, M30, **H1** | Propagação de fluxo/liquidez e informação **dentro do pregão**; líderes de índice (WIN/WDO/ES) puxando single-names intrasessão; rotação de liquidez | **Opcional** — lift incremental falsificável, nunca titular |
| **SWING** | **H1**, H4, D1 | Transmissão **macro/setorial**, rotação, risk-on/off, commodity→equity, câmbio→exportadora; posicionamento migrando ao longo de horas-dias | Fora de escopo (irrelevante na escala) |

**Decisão de enquadramento:** o tick/OFI **não some** — ele rebaixa de titular para **camada opcional de microestrutura** no modo intraday. A espinha agora é **bar-time em duas escalas**. A tese 1 e seu scope continuam válidos como insumo; esta proposta é a evolução priorizada pelo Founder.

> Princípio que governa tudo (Jim): dois modos **dobram a superfície de descoberta** e **dobram a superfície de autoengano**. Cada eixo novo (modo + timeframe) multiplica o denominador de tentativas. O ganho de cobertura vem com **imposto estatístico** — e pagá-lo honestamente é o coração desta proposta.

---

## 2. Mapa: cada gap da análise → como esta proposta fecha

| Gap (THESIS-ANALYSIS-01) | Fechamento nesta proposta |
|---|---|
| **5.1 Dados** — provenance, agressor, clock sync, contrato | §6: canônico único M1, barras derivadas determinísticas, calendário B3 versionado, rolagem WIN/WDO, clock em bar-time |
| **5.2 Estatístico** — data snooping, trial accounting | §4: trial ledger por modo e por TF, DSR de duas camadas, subtração de H1 |
| **5.3 Causa comum** — F e D no mesmo barco | §3.4 + §5: controles por modo (intraday: WIN/WDO/ES intradiários; swing: macro/setor/commodity/FX) |
| **5.4 Executabilidade** — latência, capacidade | §5: label do preço executável pós-barra, meia-vida pós-latência (intraday), risco de gap/overnight (swing) |
| **5.5 UX/psicologia** — autoengano | §7: modo + TF visíveis, vocabulário de pesquisa, sem confirmação cross-mode como evidência dupla |
| **Fronteira H1** (novo nesta hipótese) | §3.3: H1 canônico único, contado uma vez, sem dupla contagem nem vazamento |

---

## 3. Definição de lead-lag em bar-time por modo (Jim)

### 3.1 Objeto comum

Para cada timeframe $T$, retorno de barra do alvo medido **no fechamento da barra** $t$:

$$r_D^{(T)}(t) = \ln m_D(t) - \ln m_D(t-1).$$

Lead-lag = defasagem $\delta$ (em barras) do fator-fonte ponderado:

$$C_{\mathcal{S}\to D}^{(T)}(\delta) = \operatorname{Corr}\!\big(\mathbf{w}^\top \mathbf{r}_{\mathcal{S}}^{(T)}(t-\delta),\; r_D^{(T)}(t)\big),\qquad \delta \ge 1.$$

**Regra anti-look-ahead inegociável:** o sinal usa informação **até e inclusive** o fechamento da barra $t$; o label é medido **estritamente depois**, a partir do **preço executável pós-barra** ($t_{\text{exec}}$ = abertura da barra seguinte, ou close + slippage/latência), **nunca** o mesmo close usado como feature. Reaproveitar o close como feature e como entrada é o vazamento clássico que infla todo backtest de barra.

### 3.2 Forward return label

$$y_D^{(T)}(t,k) = \ln m_D(t+k) - \ln m_D(t_{\text{exec}}),$$

com $k$ = horizonte de decisão em barras (operável para o modo). Expectância **líquida** (custos + IR + slippage). Taxa de acerto crua é proibida como prova (R-11, Art. 28).

### 3.3 Grade de defasagem por TF (em barras **e** wall-clock)

A grade é registrada nas duas unidades — é o wall-clock que revela sobreposição entre TFs (§3.5). Parâmetros iniciais, **pré-registráveis**, decisão do Founder, não compromisso:

**Modo INTRADAY**

| TF | grade $\delta$ (barras) | janela wall-clock | label $k$ típico |
|---|---|---|---|
| M1 | {1,2,3,5,10,15} | 1–15 min | 5–15 |
| M5 | {1,2,3,6,12} | 5–60 min | 3–12 |
| M15 | {1,2,4,8} | 15–120 min | 2–8 |
| M30 | {1,2,4,6} | 30–180 min | 2–6 |
| **H1** | {1,2,3,6} | 1–6 h | 2–6 |

**Modo SWING**

| TF | grade $\delta$ (barras) | janela wall-clock | label $k$ típico |
|---|---|---|---|
| **H1** | {1,2,3,6} | 1–6 h | 2–6 |
| H4 | {1,2,3,5} | 4–20 h | 1–5 |
| D1 | {1,2,3,5,10} | 1–10 dias | 1–10 |

### 3.4 Dois mecanismos, não um em duas velocidades

Não é a mesma história acelerada/desacelerada — são **mecanismos econômicos distintos**, e isso muda a hipótese nula e os controles:

| | INTRADAY (M1–H1) | SWING (H1–D1) |
|---|---|---|
| Inimigo nº 1 | Fricção de execução + sincronização de fechamentos | **Não-estacionariedade + amostra escassa** |
| OFI/tick | Camada opcional (réu) | Irrelevante |
| Controle de causa comum | WIN/WDO/ES intradiários | Macro/setor/commodity/FX |

Consequência: uma célula H1 **não herda** mecanismo dos dois lados. O mecanismo é **declarado por modo, antes de rodar** (§3.5).

### 3.5 H1 — a fronteira, sem dupla contagem nem vazamento

H1 é o único TF nos dois modos. Dois perigos: (a) inflar o denominador contando H1 duas vezes; (b) tratar confirmação cross-mode como evidência **independente**, quando os labels H1 são os **mesmos** (correlacionados). Regras:

1. **Run canônico único de H1.** Um snapshot, um feature set, um hash. Os dois modos referenciam o **mesmo artefato** — nada de "H1-intraday" e "H1-swing" recomputados.
2. **H1 conta uma vez no global** (ver §4.1).
3. **Sem confirmação cross-mode como evidência independente.** "Foi bem nos dois modos" = **uma** observação, não duas.
4. **Mecanismo declarado por modo antes de rodar.** A mesma célula H1 pode ser testada como propagação-rápida (intraday) **ou** porteiro-de-regime (swing). Pré-registre qual. Escolher o vencedor **depois** de ver o resultado é hindsight.
5. **Embargo por calendário wall-clock, não por índice de barra.** Calendário de embargo global: qualquer barra de qualquer TF dentro da janela de embargo de um label usado em qualquer fold é purgada em **todos** os TFs que compartilham aquele instante. Purgar por timestamp, não por bar-index.

---

## 4. Trial accounting e DSR por modo e por TF (Jim)

### 4.1 O denominador honesto

Por TF, o número de tentativas conta **toda** liberdade de busca:

$$N_t^{(T)} = |\mathcal{F}| \times |\mathcal{D}| \times |\text{grade}_\delta^{(T)}| \times |\text{thresholds}| \times |\text{regimes}| \times |\text{variantes}| \times \text{reruns}.$$

Por modo e global (descontando H1 **uma vez**):

$$N_t^{\text{intraday}} = \!\!\sum_{T\in\{M1,M5,M15,M30,H1\}}\!\! N_t^{(T)},\quad
N_t^{\text{swing}} = \!\!\sum_{T\in\{H1,H4,D1\}}\!\! N_t^{(T)},$$
$$N_t^{\text{global}} = N_t^{\text{intraday}} + N_t^{\text{swing}} - N_t^{(H1)}.$$

### 4.2 DSR no nível da afirmação

O denominador da DSR depende do **escopo da alegação**:

- "Esta célula no M5 é edge" → a DSR usa no mínimo $N_t^{\text{intraday}}$ (a liberdade de escolher o melhor TF dentro do modo é, ela própria, teste múltiplo). Usar só $N_t^{(M5)}$ é trapaça de denominador.
- "O modo intraday tem edge" → $N_t^{\text{intraday}}$.

### 4.3 Correção em duas camadas (sem pooling)

**Não jogar p-valores de intraday e swing num único Benjamini-Hochberg** — amostras efetivas e base rates muito diferentes; pooling distorce o FDR:

1. **FDR (BH) dentro de cada modo**, separadamente — duas famílias.
2. **Gate family-wise no topo** (Hansen SPA ou Bonferroni) sobre os **2 vencedores de modo** — deflaciona o ato de escolher o modo que pareceu melhor.
3. **DSR > limiar** (ex. 0,95) com o denominador do nível correto, reportada **por TF e por modo**.

---

## 5. Walk-forward, purged CV e Go/No-Go por escala (Jim + Nassim)

### 5.1 Princípio único

**Embargo ≥ horizonte do label $k$ + cauda de autocorrelação, medido em wall-clock** (comparável entre TFs). Reportar sempre **amostra efetiva**, não bruta:

$$N_{\text{eff}}^{(T)} \approx \frac{N_{\text{barras}}^{(T)}}{k}\ \text{(labels não-sobrepostos)},\ \text{reduzida pela autocorrelação}.$$

### 5.2 Calibração por TF (pisos pré-registrados — parâmetros iniciais)

| Modo | TF | barras/ano ≈ | $k$ | embargo | WF treino/teste/passo | piso $N_{\text{eff}}$/fold |
|---|---|---|---|---|---|---|
| Intraday | M1 | ~80k | 5–15 | ~30 barras | 40d/10d/10d | ≥ 1000 |
| Intraday | M5 | ~16k | 3–12 | $k$+ | 60d/20d/20d | ≥ 500 |
| Intraday | M15 | ~5,3k | 2–8 | $k$+ | 60d/20d/20d | ≥ 300 |
| Intraday | M30 | ~2,6k | 2–6 | $k$+ | 90d/30d/30d | ≥ 200 |
| Fronteira | H1 | ~1,3k | 2–6 | $k$+ | 120d/40d/40d | ≥ 150 |
| Swing | H4 | ~330 | 1–5 | $k$+ (dias) | 2a/0,5a/0,5a | ≥ 80 |
| Swing | D1 | ~250 | 1–10 | $k$ dias+buffer | 4a/1a/1a | ≥ 50 |

- **Intraday:** dado abundante → walk-forward rolante por dias/semanas; purged k-fold com embargo em barras.
- **Swing:** amostra é a **restrição vinculante**. D1 ≈ 250 barras/ano; com $k=5$ e ~50 labels não-sobrepostos/ano, a DSR é brutal e exige **≥ 3–5 anos** e **≥ 2 períodos macro estruturalmente distintos**.
- **Abaixo do piso $N_{\text{eff}}$ → veredito é "dado insuficiente"**, nunca "sem edge" nem "edge" (Art. 30: confiança subjetiva não é evidência).

### 5.3 Go/No-Go quant por modo

**Comuns (ambos):** $\hat{\mu}_{\text{oos}} > 0$ líquida; DSR > limiar com denominador do nível correto; sobrevive a controles de causa comum; $N_{\text{eff}} \ge$ piso; edge **distribuído entre folds** (nenhum período carrega sozinho).

**INTRADAY — específico:**
- Edge sobrevive à fricção de fechamento de barra (label do preço executável pós-barra, não do close-sinal).
- Meia-vida do edge ≥ **1 barra operável** do TF **após** latência. Edge que morre na próxima barra executável = **No-Go**.
- Se OFI/tick entrar: o edge bar-time **tem que se sustentar sozinho primeiro**; OFI só adiciona lift incremental falsificável (modelo aninhado B vs A, como o fib), nunca é o único carregador.
- Capacidade = liquidez **no instante do evento intradiário**, não volume diário.
- Se o lead-lag inverte ao alinhar fechamentos corretamente → **No-Go** (era artefato de sincronização).

**SWING — específico:**
- Piso $N_{\text{eff}}$ é o gate dominante: abaixo dele → "dado insuficiente", **não promove e não mata**.
- Purged CV com embargo ≥ $k$ dias; **regime (Ray) definido ex-ante** — edge que só existe em regime definido depois de ver resultado = **No-Go**.
- Persistência em **≥ 2 períodos macro estruturalmente diferentes**, não uma tendência de sorte.
- Expectância tem que **descontar risco de gap/overnight**.

**No-Go (qualquer modo):** $\hat{\mu} \le 0$ líquida; DSR abaixo do limiar; edge some sob controle de causa comum; carregado por um fold/período; $N_{\text{eff}}$ abaixo do piso; mecanismo retro-encaixado; label com look-ahead.

### 5.4 Lente de risco (Nassim)

- **Correlação de P&L entre células**, não só ortogonalidade de preditores. Duas células parecidas via H1 compartilhado contam como **um** risco, não diversificação.
- **Sizing** segue research-only: Kelly fracionário é métrica, não autorização de tamanho. O tamanho operacional futuro seria o mínimo entre fração de Kelly conservadora, risco por trade, drawdown projetado, Art. 16º e teto agregado do Art. 11º/11-A.
- **Cauda dominante por modo:** intraday → loss streak em clusters (notícia, abertura, fechamento, feed); swing → gap/overnight e mudança de regime macro.
- **No-Go de risco:** se o pior cenário plausível de perdas encosta no Art. 16º, ou exige velocidade que o CaM não tem sem virar HFT.

---

## 6. Contrato de dados para dois modos (Ada)

### 6.1 Canônico único + barras derivadas determinísticas

Uma **única fonte de verdade bruta** por símbolo. Tudo acima é função pura e determinística:

```
TICK canônico (event-time, Parquet)      ← verdade absoluta (se disponível)
        │ agregação determinística
        ▼
M1 canônico (menor bar-time, Parquet)    ← canônico de bar-time
        │ agregação determinística (M1 → TF alvo)
        ▼
M5, M15, M30, H1, H4, D1 (derivadas / cache)
```

Dois cenários de fonte, mesmo contrato (registrar como ADR leve):

| Cenário | Fonte primária | M1 é... |
|---|---|---|
| **A — tick disponível** (B3 Times&Trades) | tick com agressor | **derivado** do tick (permite reconciliar tick↔M1) |
| **B — só OHLCV** (broker entrega candle M1) | candle M1 do broker | **canônico de bar-time** (`quality_flag: m1_is_primary`) |

**M5…D1 nunca são ingeridos direto** — sempre `GROUP BY` determinístico do M1:
open = primeiro open; high = max; low = min; close = último close; volume/trades/financial = soma; VWAP recomputado (nunca média de VWAPs); **bucket ancorado no início da sessão B3** (último bucket do dia pode ser `is_partial`).

### 6.2 Consistência forçada e fronteira H1

**Invariante de reconciliação (gate R0):** para todo bucket de TF maior, o agregado derivado bate byte a byte com o recomputado de M1. **H1 é computado UMA vez** a partir de M1 e **compartilhado** entre os modos — não existe "H1 intraday" e "H1 swing", só um H1 canônico; `mode` é apenas uma *view*. Recomendação: derivar **sempre direto de M1** (`M1 → TF`), não em cascata; cascata só como cache entre TFs com aninhamento exato.

### 6.3 Calendário B3 e swing

- `research_calendar` versionado e hasheado: `is_trading_day`, `session_open/close`, leilões, `early_close`, `dst_offset`. D1 indexado por `session_date`, **não** data corrida.
- **Gap overnight é feature, não erro** — `close[d]→open[d+1]` existe separado; forward-fill de preço overnight é proibido.
- **Ajustes (D1 swing):** duas séries persistidas — `raw` (execução/validação) e `adjusted` (retorno/lead-lag). Nunca uma só.
- **Rolagem WIN/WDO** (o ponto mais delicado do swing): contratos individuais crus preservados (`WINM26`, `WING26`); série contínua (`WIN_c1`) é artefato **derivado e versionado** com `roll_rule` + `splice_method`, rastreável ao contrato físico. **Gate R0 swing:** sem regra de rolagem versionada + teste de salto (sem descontinuidade > X·ATR no ponto de rolagem), nenhuma série contínua entra no Cubo.

### 6.4 Clock sync em bar-time

O requisito **afrouxa** de milissegundo (tick) para **borda de bucket** (bar-time), mas muda de natureza:

- **Mesmo bucket-edge para todos os símbolos**, ancorado no mesmo `session_open` e no relógio da B3 (não broker, não máquina local).
- **`ts_source` explícito:** `exchange` exigido para lead-lag; `broker_recv` aceitável com flag; `local_ingest` é **No-Go** (latência de rede vira "sinal").
- **Convenção fixa:** barra rotulada por `ts_open`, lead-lag em nº de barras. Misturar open/close entre símbolos cria deslocamento de 1 barra — exatamente o que o Cubo mede.
- **`clock_skew_ms` auditado**, não assumido zero — vira `quality_flag` quando excede fração do TF.

### 6.5 Schema `research_*` — timeframe como dimensão de primeira classe

- **`research_bars`** (Parquet, canônico de barras): `symbol, timeframe, ts_open, ts_close, session_date, OHLC, volume, financial, trades, vwap, is_partial, price_series (raw|adjusted), provenance_id, aggregation_rule_id`. **`timeframe` é coluna + partição**, não tabela por TF.
- **Postgres `research_*`** (metadados/runs/resultados, nunca as barras cruas), novas/ajustadas:
  - `research_bar_definitions` — anchor, partial_handling, vwap_method, bucket_alignment, derived_from, `definition_hash`.
  - `research_aggregation_rules` — regra determinística versionável/hasheável.
  - `research_calendar` (§6.3).
  - `research_continuous_series` — rolagem WIN/WDO (§6.3).
  - `research_dataset_snapshots` — `+ timeframes_included[], mode (intraday|swing|both), calendar_version`.
  - `research_data_sources` — `+ bar_origin (tick|broker_m1|broker_ohlcv), ts_source`.
  - `research_data_quality_checks` — `+ bucket_misalignment, partial_bar, m1_is_primary, missing_bars, stale_bar, roll_discontinuity`.
- **Modo (intraday/swing) é metadado de run** (`research_runs.mode + timeframes[]`), não de storage — as barras são as mesmas; o recorte é a *view*.

### 6.6 Reprodutibilidade — hash composto

```
dataset_snapshot_hash = H(
    raw_canonical_hash
  ⊕ calendar_version
  ⊕ Σ_timeframes H( timeframe ⊕ aggregation_rule_id ⊕ bar_definition_hash ⊕ price_series )
  ⊕ continuous_series_version )
```

Mudar a regra de agregação (anchor do H4, método de rolagem, raw→adjusted) **muda o hash → cria nova run vinculada**, nunca edita a antiga. `derive(canonical, rule, tf)` é função pura → roda duas vezes, Parquet byte-idêntico (gate R0 automatizável). Cache é descartável; **canônico + regras vencem o cache**.

### 6.7 Performance

- Particionamento Parquet Hive-style: **`symbol / timeframe / session_date`** (predicate pushdown alinhado às queries do Cubo). Para M1 de muitos anos, `session_month` como folha.
- Cache materializado de M5…D1, invalidado por hash; M1 sempre materializado; **H1 cacheado uma vez, servido aos dois modos**.
- Índices Postgres compostos `(symbol, timeframe, session_date)` só nos metadados.

---

## 7. UX dos dois modos no Quant Lab (Don)

Herdando os guardrails da análise, com os acréscimos da dualidade:

- **Modo e timeframe sempre visíveis** em toda célula, run e resultado — o operador nunca confunde um edge M1 com um edge D1.
- **Badge `RESEARCH` permanente** e separação visual clara do Cockpit Live.
- **Sem confirmação cross-mode como selo de qualidade:** a UI **não** pode exibir "validado nos 2 modos" como reforço — via H1 compartilhado isso é uma observação correlacionada, não dupla (§3.5). Deve aparecer com aviso explícito.
- **Expectância líquida como manchete** por modo/TF; DSR e contador de tentativas **por TF e por modo** ao lado.
- **Data Health antes do heatmap:** sem reconciliação de barras, calendário e (swing) teste de rolagem, a UI bloqueia leitura otimista.
- **Vocabulário de pesquisa:** hipótese, célula, evidência, sobrevivente estatística, candidata. Proibido sinal, compra, venda, entrada, setup liberado.
- **Veredito "dado insuficiente" é um estado de primeira classe** na UI (distinto de "sem edge" e de "edge") — crítico para swing.

---

## 8. Fronteira de segurança (Kevin)

Inalterada e reforçada pela dualidade:

- Isolamento research/live **técnico**: serviço de research sem escrita em `cam_orders`, `cam_positions`, `cam_journal_entries`.
- Namespace `/research` só muta estado de research; `DELETE` = cancel/archive/soft-delete, nunca apaga evidência (incluindo kill log por TF).
- Módulos de research **não importam** Order Gateway, bridge MT5, `send_order`, `OrderSend`.
- Dados de corretora (tick, candle, contratos, rolagem) com provenance, **sem secrets** em Parquet, logs ou metadata de run.
- Libs novas (quant, heatmap) exigem ADR leve + lockfile + dependency scan.
- Esta frente **aciona SEC-GOV** por dados sensíveis e dependências novas — Conditional Go condicionado à prova de isolamento.

---

## 9. Evidence Pack para dois modos (Jim)

O Evidence Pack passa a carregar o eixo **modo/TF** explícito:

1. **Pré-registro por modo/TF:** modo, TF, grade $\delta$ (barras + wall-clock), label $k$, **hipótese de mecanismo** — antes do run.
2. **Trial ledger por modo:** $N_t^{\text{intraday}}$, $N_t^{\text{swing}}$, $N_t^{\text{global}}$ com **subtração de H1 explícita**; duas famílias FDR + deflação de topo.
3. **$N_{\text{eff}}$ e DSR por TF** (amostra efetiva, não barras brutas; denominador de nível).
4. **Spec WF / purged CV por escala** + **calendário de embargo global** para purga cross-TF.
5. **Declaração de fronteira H1:** hash do run canônico único; H1 contado uma vez; **negação explícita** de independência cross-mode.
6. **Bloco de fricção por modo:** intraday → label executável pós-barra + meia-vida pós-latência; swing → risco de gap/overnight descontado + regime ex-ante.
7. **Controles de causa comum por modo.**
8. **Kill log por TF:** todo TF/célula morto com motivo. **Matar é evidência.**
9. **Seção de resultado negativo:** TFs/modos sem edge ou em "dado insuficiente" — impede que a sobrevivente pareça "a única coisa testada".

---

## 10. Fases e gates (atualizados para dois modos)

| Fase | Conteúdo | Gate |
|---|---|---|
| **R0 — Dados** | Canônico M1 único; barras derivadas determinísticas; H1 único; calendário B3 versionado; rolagem WIN/WDO + teste de salto; `ts_source=exchange`; snapshot com hash composto | Reconciliação byte a byte + provenance completa + (swing) rolagem versionada |
| **R1 — Features** | Biblioteca pura por TF, sem look-ahead, versionada e testada; feature cache por snapshot | Determinismo + testes de borda por TF |
| **R2-INTRADAY — Cubo intraday** | M1–H1; event study líquido; OOS/WF; FDR/DSR intraday; controles WIN/WDO/ES; OFI só incremental | ≥1 célula sobrevive **ou** modo intraday é morto; $N_{\text{eff}}$ ok |
| **R2-SWING — Cubo swing** | H1–D1; purged CV embargo em dias; FDR/DSR swing; regime ex-ante; ≥2 períodos macro; risco de gap | ≥1 célula sobrevive, **ou** "dado insuficiente", **ou** morto |
| **R3 — Estrutura/Fib** | Baseline estrutural por modo; fib como réu (incremento OOS) | Baseline antes; fib fica só se acrescenta |
| **R4 — Síntese** | Regime lento (swing) × gatilho rápido (intraday); deflação de topo sobre os 2 modos | Composição supera as partes isoladas OOS, trial accounting incluído |

> H1 é o nó de ligação entre R2-INTRADAY e R2-SWING — **um run canônico**, referenciado pelos dois, contado uma vez.

---

## 11. Decisões abertas para o Founder

1. **Cenário de dados:** a corretora exporta tick com agressor (cenário A) ou só candle M1 (cenário B)? Define se há reconciliação tick↔M1.
2. **Universo inicial** por modo: quais single-names + WIN/WDO/ES entram em intraday e em swing.
3. **Profundidade histórica:** swing exige ≥3–5 anos e ≥2 regimes macro — a fonte cobre isso?
4. **Grades de $\delta$ e labels $k$** iniciais por TF (tabelas §3.3).
5. **Regra de rolagem WIN/WDO** (`roll_rule` + `splice_method`) para a série contínua swing.
6. **Anchor do H4** e tratamento do bucket parcial no pregão B3.
7. **Pisos de $N_{\text{eff}}$** por TF (tabela §5.2) — confirmar ou calibrar.
8. **Persistência:** Postgres com namespace `research_*` + permissões duras, ou store separado.
9. **Lib de heatmap** (`plotly` vs `visx`) — ADR leve.

---

## 12. Perguntas duras (acrescentadas pela dualidade)

1. Dois modos cobrem mais mercado — ou só dobram a chance de decorar ruído? O trial ledger e a subtração de H1 serão tão rigorosos quanto o heatmap é bonito?
2. Se o swing nunca atinge $N_{\text{eff}}$ mínimo, ele será arquivado como "dado insuficiente" ou forçado a parecer vivo?
3. A confirmação cross-mode via H1 será tratada como **uma** observação correlacionada, ou venderá convicção dobrada?
4. O mecanismo de cada célula H1 será declarado **antes** do run, ou escolhido depois conforme o resultado?
5. Qual resultado faria Carlos matar **um modo inteiro** sem negociação?
6. Se o intraday só vive antes da latência real e o swing só vive em "dado insuficiente", a tese 2 inteira é descartada como vitória?

---

## 13. Conclusão

A hipótese 2 é **viável e bem-posta como research**, desde que cada eixo novo (modo + timeframe) pague seu imposto estatístico. O caminho correto continua sendo **dados primeiro**: um canônico M1 único, barras derivadas determinísticas, H1 compartilhado e contado uma vez, calendário e rolagem versionados. Sobre essa fundação, o Cubo roda em duas escalas com trial accounting honesto, DSR de duas camadas e Go/No-Go por modo.

O valor desta proposta não é prometer dois edges. É construir uma máquina que diga, com honestidade auditável e **por modo**: esta célula morreu, esta ainda não tem dado, ou esta sobreviveu o bastante para virar EDGE-THESIS específica e entrar no pipeline formal do CaM.

Próximo passo sugerido (ainda sob gate do Founder): abrir o fluxo DevFlow a partir de **DISC/SPEC R0 — Market Data Research Snapshot (dois modos)**, que materializa o contrato de dados desta proposta.

Research-only. Risk Engine intocado. Founder gate pendente. Sem execução.

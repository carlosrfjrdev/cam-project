---
template: EDGE-THESIS + SCOPE (research)
phase: P&D / Research Lane
status: Draft 1.0 (hipótese — não promovido) · SUPERSEDE EDGE-THESIS-LEADLAG-CUBE.md v0.1
produto: CaM
codinome: research-cubo-leadlag ("O Cubo")
vive_em: project/cam-cockpit/research/CaM-RESEARCH-CUBO-LEADLAG.md
data: 2026-06-01
lead: Mentor de Estratégia (criação) · Founder (aprovação)
---

# Cubo de Lead-Lag Cross-Asset — Teses Unificadas + Scope CaM

> Documento de **research**, pré-estratégia. Não toca o cockpit live, não consome
> capital real, roda na research lane (Parquet/DuckDB) isolada das tabelas operacionais.
> A promoção de qualquer célula para paper/live passa pelo Go/No-Go (§6) e, na operação,
> pela autoridade do Risk Engine. Nada aqui contorna a Constituição: ela governa
> **operação**; este documento governa **descoberta**.

---

## 1. Visão geral — uma tese, duas lentes

Existe **um** objeto conceitual: o **cubo**, um tensor de descoberta indexado por

$$\textbf{célula} = (\,F \;\text{fonte},\; D \;\text{alvo},\; \tau \;\text{defasagem}\,) \longmapsto \text{métrica de edge}.$$

A fonte $F$ pode ser um ativo único ou um **conjunto** $\mathcal{S}$. O alvo $D$ é livre.
Duas instâncias do mesmo cubo:

| | **Tese 1 — Cubo Rápido** | **Tese 2 — Cubo Lento** |
|---|---|---|
| Domínio temporal | event time (tick) | bar time (1m, 10m, 1h, 4h, 1d) |
| Sinal | fluxo de agressão (OFI) | estrutura de preço (± Fibonacci) |
| Defasagem $\tau$ | 0.5s … 30s | 1 … N barras (min/horas/dias) |
| Mecanismo econômico | microestrutura / propagação de fluxo | transmissão macro / setorial / rotação |
| Inimigo estatístico nº 1 | Epps + latência | poucas observações + não-estacionariedade |

A relação entre elas não é paralela e sim **hierárquica**: a lente lenta é o **porteiro de regime** da rápida (§7).

---

## 2. Notação e definições comuns

- Universo $\mathcal{U}=\{1,\dots,N\}$. Preço de meio (mid) de $i$: $m_i(t)=\tfrac{1}{2}(\text{bid}_i(t)+\text{ask}_i(t))$.
- Log-retorno em horizonte $h$: $\;r_i(t,h)=\ln m_i(t+h)-\ln m_i(t).$
- Custo round-trip em bps: $c$ (corretagem + emolumentos + **slippage** estimado). IR sobre ganho líquido: aplicado no agregado (honestidade constitucional).
- Função de teste de edge usa **expectância líquida**, nunca taxa de acerto crua.

---

## 3. Tese 1 — Cubo Rápido (microestrutura / fluxo)

### 3.1 Sinal de fluxo (Order Flow Imbalance)

Cada negócio $k$ de $i$ no instante $t_k^i$ tem sinal de agressor $\epsilon_k^i\in\{+1,-1\}$
(comprador levanta o offer $=+1$; vendedor bate no bid $=-1$) e volume $v_k^i$.
B3 fornece o agressor no Times&Trades — usar direto; fallback = regra de Lee–Ready.

Fluxo assinado (OFI) numa janela de cálculo $\Delta$ (rolante; **não é candle**):

$$x_i(t;\Delta)=\!\!\sum_{k:\,t_k^i\in(t-\Delta,\,t]}\!\!\epsilon_k^i\,v_k^i,\qquad
\tilde{x}_i(t;\Delta)=\frac{x_i(t;\Delta)}{\sum v_k^i}\in[-1,1].$$

Refinamento opcional (v2): OFI de **livro** (Cont–Kukanov–Stoikov), somando variações de tamanho no melhor bid/ask por evento — captura pressão antes do trade impresso.

### 3.2 Célula do cubo (fast) — correlação defasada

$$\rho_{F\to D}(\tau)=\operatorname{Corr}\!\big(\tilde{x}_F(t),\; r_D(t,\tau)\big).$$

Primeira varredura, barata e interpretável. **Não conclui nada sozinha** — sofre do Epps (§3.3).

### 3.3 Covariância assíncrona — Hayashi–Yoshida (mata-Epps)

Tick de $F$ e $D$ chega em instantes diferentes. Reamostrar para correlacionar **fabrica** lead-lag (efeito Epps). O estimador consistente para a covariação integrada de processos observados de forma assíncrona é o de Hayashi–Yoshida. Para incrementos $\Delta a_i$ em intervalos $I_i^a=(t_{i-1}^a,t_i^a]$ e $\Delta b_j$ em $I_j^b$:

$$\widehat{\langle a,b\rangle}^{HY}=\sum_{i,j}\Delta a_i\,\Delta b_j\,\mathbb{1}\{I_i^a\cap I_j^b\neq\emptyset\}.$$

Sem reamostragem, sem viés de sincronização.

### 3.4 Lead-lag — contraste de Hoffmann–Rosenbaum–Yoshida

Defasando uma série por $\theta$ e maximizando o contraste:

$$U_{a,b}(\theta)=\sum_{i,j}\Delta a_i\,\Delta b_j\,\mathbb{1}\{(I_i^a-\theta)\cap I_j^b\neq\emptyset\},
\qquad \hat{\vartheta}=\arg\max_{\theta}\,\big|U_{a,b}(\theta)\big|.$$

O **sinal** de $\hat{\vartheta}$ diz quem lidera; o **valor** diz por quanto tempo.

### 3.5 Causalidade direcional

**Granger** num VAR em event-bars finas (corroborado pelo HY, pelo caveat assíncrono):

$$y_D(t)=\alpha+\sum_{\ell=1}^{L}\beta_\ell\,y_D(t-\ell)+\sum_{\ell=1}^{L}\gamma_\ell\,y_F(t-\ell)+u(t),
\qquad H_0:\gamma_1=\dots=\gamma_L=0.$$

Rejeitar $H_0$ (Wald/F) ⇒ $F$ Granger-causa $D$.

**Transfer entropy** (não-linear, direcional), com defasagens $f_t^{(l)}$, $d_t^{(k)}$:

$$T_{F\to D}=\sum p\big(d_{t+1},d_t^{(k)},f_t^{(l)}\big)\,
\log\frac{p\big(d_{t+1}\mid d_t^{(k)},f_t^{(l)}\big)}{p\big(d_{t+1}\mid d_t^{(k)}\big)}.$$

Net flow $F\to D$ se $T_{F\to D}>T_{D\to F}$.

### 3.6 Conjunto-fonte e ortogonalidade

Para $\mathcal{S}=\{i_1,\dots,i_q\}$, o preditor é uma combinação $\mathbf{w}^\top\mathbf{x}_{\mathcal{S}}(t)$.
Preditores correlacionados entre si = **um fator**, não $q$. Procedimento:

1. Branquear via PCA: $\mathbf{z}=\mathbf{W}\mathbf{x}_{\mathcal{S}}$ (componentes ortogonais).
2. Medir $R^2$ **incremental** de cada componente sobre $r_D$ — descartar os que não somam.
3. Reportar o fator preditivo efetivo (eigen-combinação), não a lista crua.

### 3.7 Event study (núcleo econômico)

Padronização rolante do fluxo: $\;z_F(t)=\dfrac{\tilde{x}_F(t)-\mu_F(t)}{\sigma_F(t)}.$
Evento em $t^\*$: $|z_F(t^\*)|>\kappa$, sinal $s=\operatorname{sgn}(z_F(t^\*))$.
Retorno **assinado** do alvo: $g(t^\*,h)=s\cdot r_D(t^\*,h)$.

Expectância líquida por horizonte (decisão), sobre $M$ eventos:

$$\hat{\mu}_h=\frac{1}{M}\sum_{m=1}^{M}\big[g(t_m^\*,h)-c\big]
\;=\;p\,\bar{w}-(1-p)\,\bar{l}-c-\text{IR}.$$

Probabilidade $p$ **sozinha não basta**: $60\%$ com payoff ruim perde.

### 3.8 Curva de decaimento e condição de executabilidade

$\hat{\mu}_h$ em função de $h$ dá a meia-vida do edge. Com latência de execução $\lambda$ (MT5/Profit), a célula é executável sse o edge ainda é positivo após $\lambda$:

$$\hat{\mu}_{h=\lambda}>0\quad\text{e}\quad \int_{\lambda}^{H}\frac{\partial\hat{\mu}_h}{\partial h}\,dh \;\text{compatível com saída realista.}$$

Edge que vive $<\lambda$ é terreno de co-located ⇒ **fora do escopo** (CaM não é HFT).

### 3.9 Hipóteses formais (Tese 1)

- **H1 — existência:** $\exists\,(F,D,\tau)$ com $|\rho_{F\to D}(\tau)|$ significativa e estável OOS.
- **H2 — expectância:** $\hat{\mu}_h>0$ líquida para algum $h$ operável.
- **H3 — não-causa-comum:** efeito sobrevive a controle por $\{$WDO, ES, macro$\}$.
- **H4 — executável:** $\hat{\mu}_{h=\lambda}>0$.
- **H5 — refutação a derrubar:** a relação **não** é artefato Epps (confirmar via HY/§3.3).

> Avança sse H1–H4 passam **e** H5 é derrubada.

---

## 4. Tese 2 — Cubo Lento (estrutura de preço em barras)

### 4.1 Barras: tempo vs atividade

Time bars são o pior amostrador para fluxo (oversample do pregão morto). Preferir **barras por atividade** quando possível: tick bars (cada $N$ negócios), volume bars (cada $N$ contratos), dollar bars (cada $\$X$). Em 1h/4h/1d o argumento enfraquece — time bars são aceitáveis. No 1m/10m, considerar volume bars para sincronizar melhor a informação entre ativos.

### 4.2 Modelo de lead-lag estrutural — **baseline SEM Fibonacci**

Esta é a versão honesta de partida: só preço/retorno e estrutura objetiva.

Regressão multi-fonte defasada em retornos de barra $r^{(T)}$:

$$r_D^{(T)}(t)=\alpha+\sum_{j=1}^{q}\sum_{\delta=1}^{\Delta_{\max}}\beta_{j,\delta}\,r_{i_j}^{(T)}(t-\delta)+\varepsilon(t),
\qquad H_0:\{\beta_{j,\delta}\}=\mathbf{0}.$$

Lead-lag por defasagem do fator-fonte ponderado:

$$C_{\mathcal{S}\to D}(\delta)=\operatorname{Corr}\!\big(\mathbf{w}^\top\mathbf{r}_{\mathcal{S}}(t-\delta),\,r_D(t)\big).$$

### 4.3 Definição **mecânica** de swing e S/R (anti-hindsight)

Toda estrutura é definida por regra fixa **antes** do teste:

- **Swing por ZigZag:** novo ponto confirmado quando o preço reverte $\ge\theta_z$ do último extremo.
- **Pivô fractal de ordem $n$:** $t$ é topo se $P(t)>P(t\pm1),\dots,P(t\pm n)$ (e simétrico para fundo).
- **S/R horizontal objetivo:** máx/mín do dia anterior, extremos rolantes de $N$ barras, POC/nós de volume.

### 4.4 Features estruturais (baseline)

Rompimento de swing prévio; distância normalizada à S/R; estado de média móvel; força relativa $RS_i(t)=r_i^{(T)}(t)-r_{\text{índice}}^{(T)}(t)$. Evento-fonte = rompimento estrutural ou spike $z$-scored do retorno-fonte; mede-se $\hat{\mu}_k$ (expectância líquida) no alvo nas próximas $k$ barras (mesma forma de §3.7).

### 4.5 Variante **COM Fibonacci**

#### 4.5.1 Construção dos níveis
Dada uma perna de swing confirmada de $P_0$ a $P_1$, retração de razão $\phi$:

$$L_\phi=P_1-\phi\,(P_1-P_0),\quad \phi\in\{0.236,0.382,0.5,0.618,0.786\};$$
$$\text{extensão}\;E_\phi=P_1+(\phi-1)(P_1-P_0),\quad \phi\in\{1.272,1.618,2.618\}.$$

#### 4.5.2 Feature de toque normalizada por ATR
$$d_\phi(t)=\frac{|P(t)-L_\phi|}{\text{ATR}(t)},\qquad \text{toque}\iff d_\phi(t)<\eta.$$

#### 4.5.3 Teste de falsificação (o que decide se fib fica ou cai)
Comparação de modelos aninhados:

- **Modelo A (baseline §4.2–4.4):** só estrutura objetiva.
- **Modelo B (augmentado):** A + features de toque de fib.

Edge incremental: $\;\Delta=\hat{\mu}_B-\hat{\mu}_A.$
**Controle de redundância** — regredir o desfecho do toque de fib sobre indicadoras "também é máx/mín anterior", "número redondo", "nó de volume":

$$H_0^{\text{fib}}:\;\mathbb{E}[\Pi\mid\text{toque fib}]=\mathbb{E}[\Pi\mid\text{toque de S/R genérico no mesmo ponto}].$$

Fib só **fica** se $\Delta>0$ com significância OOS **e** o coeficiente do fib sobrevive aos controles. Se evaporar ⇒ fib era S/R reetiquetado ⇒ usa-se o **baseline**.

### 4.6 Hipóteses formais (Tese 2)
- **H1′ — existência (sem fib):** $\exists\,(\mathcal{S},D,\delta)$ com lead-lag estrutural significativo OOS.
- **H2′ — expectância (sem fib):** $\hat{\mu}_k>0$ líquida em horizonte operável.
- **H3′ — não-causa-comum:** sobrevive a controle por fatores macro/setoriais.
- **H4′ — fib incremental:** $\Delta>0$ significativo **e** robusto a controles — caso contrário, fib é rejeitado.
- **H5′ — sem hindsight:** resultados invariantes à regra de swing dentro de faixa razoável de $\theta_z,n$.

---

## 5. Higiene estatística (ambas as lentes)

### 5.1 Múltiplos testes — o maior risco do cubo
O cubo tem $\sim N\times N\times|\{\tau\}|$ células. Varrer tudo **acha padrão no ruído**. Defesas:

- Controle de FDR (**Benjamini–Hochberg**) ou family-wise (Bonferroni) nos $p$-valores.
- Teste de superioridade preditiva do **conjunto** da busca: White's Reality Check / **Hansen SPA**.
- **Deflated Sharpe Ratio** (Bailey–López de Prado), penalizando o nº de tentativas $N_t$:

$$SR_0=\sqrt{\widehat{V}[SR]}\left[(1-\gamma)\,Z^{-1}\!\Big(1-\tfrac{1}{N_t}\Big)+\gamma\,Z^{-1}\!\Big(1-\tfrac{1}{N_t e}\Big)\right],$$
$$\mathrm{DSR}=Z\!\left(\frac{(\widehat{SR}-SR_0)\sqrt{n-1}}{\sqrt{1-\hat{\gamma}_3\widehat{SR}+\frac{\hat{\gamma}_4-1}{4}\widehat{SR}^2}}\right),$$

com $\gamma\approx0.5772$ (Euler–Mascheroni), $Z^{-1}$ inversa da normal, $\hat{\gamma}_3,\hat{\gamma}_4$ assimetria/curtose. Exige-se p.ex. $\mathrm{DSR}>0.95$.

### 5.2 Validação — walk-forward + purged CV
Walk-forward parametrizado (janela treino, teste, step). Para a lente lenta (labels de múltiplas barras se sobrepõem), usar **purged k-fold CV com embargo** (López de Prado) para eliminar vazamento.

### 5.3 Estacionariedade e regime
ADF/KPSS em fluxo e retornos. **Condicionar por regime**: terços de volatilidade realizada; tendência via ADX/Hurst. A propagação pode existir só em alta vol / abertura e inverter fora.

### 5.4 Capacidade e impacto de mercado
Lei raiz-quadrada do impacto: $\;\dfrac{\Delta P}{P}\approx Y\,\sigma\sqrt{Q/V}\;$ ($Q$=tamanho, $V$=volume diário, $\sigma$=vol, $Y=\mathcal{O}(1)$). O edge por trade tem de **exceder** o impacto no tamanho pretendido — senão o sinal não "aguenta banca".

### 5.5 Sizing — Kelly fracionário (traduz o "jogar a banca")
Aposta dimensionada pela **expectância e variância medidas**, não pela convicção:

$$f^\*=\frac{\mu}{\sigma^2}\;\;(\text{contínuo}),\qquad f^\*=p-\frac{1-p}{b}\;\;(\text{discreto, payoff }b),\qquad \text{usar }\phi f^\*,\ \phi\in(0,\,0.5].$$

Concentrar 100% numa célula = variância máxima. O tamanho sai do número.

---

## 6. Go/No-Go unificado

Promove uma célula para **paper** se **todas**:

1. Expectância OOS líquida $\hat{\mu}^{oos}>0$ (custos+IR), com **DSR ajustada** acima do limiar.
2. Persistência: (rápida) $\hat{\mu}_{h=\lambda}>0$; (lenta) edge vivo por $\ge1$ barra operável.
3. Sobrevive a controles de causa comum (WDO/ES; fatores macro/setoriais).
4. (Rápida) HY confirma e mata Epps; (lenta) sobrevive a purged CV.
5. (Fib) edge incremental $\Delta>0$ e robusto — caso contrário, fib cai e segue baseline.
6. Capacidade $\ge$ capital pretendido.

**Mata** em qualquer falha. **Matar cedo é vitória** — economiza capital e tempo.

---

## 7. Síntese — duas camadas, um sistema

A lente lenta **não compete** com a rápida: ela a **contextualiza**.

$$\text{Sinal operável} \;=\; \underbrace{\mathbb{1}\{\text{regime lento favorável}\}}_{\text{porteiro (Tese 2)}}\;\times\;\underbrace{\text{gatilho de fluxo (Tese 1)}}_{\text{direção e timing}}.$$

O cubo diário/4h diz "VALE3 em regime de alta + commodity a favor"; o cubo de tick só dispara a propagação intraday na direção abençoada. Contexto lento filtrando gatilho rápido — é o que transforma duas hipóteses em um sistema robusto.

---

## 8. SCOPE para o CaM

### 8.1 Posicionamento na arquitetura
Todo este trabalho vive na **research lane** do CaM: leitura de Parquet via DuckDB, **isolada** das tabelas operacionais (`cam_orders`, `cam_positions`, `cam_journal_entries`, etc.). A research **nunca grava** em tabela vista pelo cockpit live. O Risk Engine permanece intocado e é a autoridade exclusiva quando/se uma estratégia derivada chegar ao live.

### 8.2 Módulos a construir (research/quant lab)

| Módulo | Responsabilidade | Saída |
|---|---|---|
| **Ingestão tick** | Tick → Parquet particionado (símbolo/dia) com flag de agressor; validação de **clock sync** (ms) e provenance | dataset canônico |
| **Bar builder** | Time bars + activity bars (tick/volume/dollar) p/ lente lenta | barras versionadas |
| **Feature library** | Fluxo (OFI, $z$-score), estrutura (ZigZag/fractal, S/R, breakout, RS), volatilidade (ATR, RV), Fibonacci (níveis + $d_\phi$) | features puras/determinísticas |
| **Cube engine** | $\rho$ defasado, HY + lead-lag HRY, Granger, transfer entropy, event study sobre a grade $(F,D,\tau)$ — instâncias rápida e lenta | ranking de células + $\hat{\mu}_h$ |
| **Stats layer** | FDR/SPA, **DSR**, purged walk-forward CV, condicionamento por regime, controles de causa comum | veredito por célula |
| **Reporting** | Curvas de decaimento, tabelas de expectância, painel Go/No-Go | relatório de research |

### 8.3 Contrato com `strategies/` e o Risk Engine (DRY)
Uma célula aprovada vira um `strategies/leadlag_<id>.py` expondo o **mesmo** contrato canônico:

```python
def generate_signal(context: MarketContext) -> Optional[Signal]: ...
```

usado igual em backtest, paper e live. Fluxo: `signal → order_candidate → risk_engine.validate → execução`. A research só produz o sinal candidato e a evidência; **promoção e operação** seguem as fases do CaM e a autoridade do Risk Engine.

### 8.4 Dentro (In)
- Ingestão tick com flag de agressor + bar builder (time + activity).
- Feature library com as três famílias + fib (como feature falsificável).
- Cube engine rápido (microestrutura) e lento (estrutura).
- Stats layer com DSR/FDR/purged CV/regime/controles.
- Reporting de research (decaimento, expectância, ranking, Go/No-Go).
- Universo inicial: blue chips Ibov + WIN + WDO + ES (controle).

### 8.5 Fora (Out)
- Execução real a partir da research (research only).
- HFT / sub-segundo.
- Opções (parkeado — single-name e propagação de volatilidade ficam para fase 2).
- Multi-alvo simultâneo / portfólio de sinais antes de 1 célula provada.
- Qualquer escrita em tabela do cockpit live.

### 8.6 Depois (Later)
- Promoção de célula → EDGE-THESIS de estratégia + `strategies/` + backtest.
- Camada de execução por instrumento (à vista vs futuro) conforme natureza do preditor.
- Opções (direcional single-name; volatilidade).
- Composição formal das duas camadas (porteiro × gatilho) como uma estratégia única.

### 8.7 Fases e gates
1. **R0 — Dados:** ingestão + clock sync + bar builder. Gate: dataset reprodutível e validado.
2. **R1 — Features:** biblioteca pura, testada. Gate: cada feature determinística e versionada.
3. **R2 — Cubo Rápido:** §3 completo. Gate: H1–H4 + H5 derrubada em ≥1 célula (DSR ok).
4. **R3 — Cubo Lento:** §4 completo, baseline e fib. Gate: H1′–H3′ + decisão de H4′ (fib fica/cai).
5. **R4 — Síntese:** porteiro × gatilho. Gate: edge da composição > edge das partes.
6. **→ Paper:** só células que passam o Go/No-Go (§6), sob o pipeline padrão do CaM.

### 8.8 Decisões abertas do Founder
- **Universo $N$** e lista inicial de alvos candidatos.
- **Profundidade da janela histórica** (especialmente crítica na lente lenta — §5.1/5.2).
- **Grade de $\tau$** (rápida) e $\delta$ (lenta) iniciais.
- **Limiares** $\kappa$ (evento), $\eta$ (toque fib), $\theta_z/n$ (swing), $\phi$ (Kelly).
- A corretora **exporta tick** com agressor? (confirma fonte do dado primário — TODO-OPERACIONAL.)

---

## 9. Stack técnica sugerida (alinhada ao CaM)
- **Armazenamento/consulta:** Parquet particionado + **DuckDB** (research). Nunca tabelas do live.
- **Processamento:** **polars** (tick em rajada) / pandas; **numpy/scipy**.
- **Econometria:** **statsmodels** (Granger/VAR, ADF/KPSS); HY e lead-lag HRY implementados (núcleo pequeno) ou lib dedicada; transfer entropy via lib de info-teoria.
- **Volatilidade:** `arch` (RV/GARCH para regime).
- **Validação:** scikit-learn + purged CV/embargo customizado; DSR implementado a partir das fórmulas (§5.1).
- **Reporting:** matplotlib para relatórios de research; o painel Go/No-Go pode reusar o frontend React do cockpit (read-only).

---

## 10. Histórico de versões

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 0.1 | 2026-06-01 | Draft inicial (só Tese 1) | — |
| 1.0 | 2026-06-01 | Unificação Tese 1 + Tese 2 (com/sem fib), rigor matemático, SCOPE CaM. Supersede 0.1 | (pendente Founder) |

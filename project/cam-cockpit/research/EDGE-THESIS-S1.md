---
template: EDGE-THESIS
phase: SPEC
status: Draft
version: 1
date: 2026-05-25
---

# EDGE-THESIS-S1 — Tese de Edge da Primeira Estratégia do CaM

> **Lead:** Albert (especificação de tese)
> **Crítico:** Voltaire (devil's advocate sobre o edge)
> **Suporte:** Sun (estratégia)
> **Skills:** `teczi-demand-specification` + `strategy-session`
> **Aprovador:** Founder
> **Vinculação constitucional:** Arts. 28º (gates de validação), 29º (aderência), 30º (escala por evidência)
>
> Este documento é **tese, não decisão implementacional.** A implementação técnica (código MQL5 ou NTSL) vem na SPEC da estratégia futura. Aqui é apenas a **hipótese de edge** com critérios de validação e descarte.

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Codinome | **S1 — Opening Range Breakout 60m WIN** (proposta inicial) |
| Ativo alvo | **WIN** (mini-índice Bovespa) |
| Timeframe primário | **5 minutos** |
| Timeframe de filtro/contexto | **15 minutos** + diário |
| Janela operacional sugerida | Após 1h do open (~10h05–11h00, considerando janela vedada do Art. 32º + 15min pós-abertura) até o início da janela vedada de fechamento |
| Direção | Long e short |
| Lado dominante | Definido empiricamente em backtest (sem viés a priori) |
| Status | **Proposta** — aguarda aprovação do Founder ou rejeição com proposta alternativa |

> **Nota Albert:** ORB 60m em WIN é a proposta natural por compatibilidade com janelas vedadas + robustez documentada em literatura quant + adequação ao perfil de stops da POV (150–250 pontos). **Founder pode rejeitar e propor outra base** — o ritual deste documento continua válido para qualquer S1 candidata.

---

## 2. Tese central

### 2.1 Por que essa estratégia ganha dinheiro?

A hipótese é que o **range de abertura (opening range, OR)** dos primeiros 60 minutos do pregão captura o estado de equilíbrio inicial entre fluxo institucional e ruído pré-abertura. Quando o preço **rompe** esse range com volume e contexto coerente:

- (a) operadores institucionais (que ainda não posicionaram totalmente) tendem a perseguir o movimento na direção do rompimento;
- (b) operadores stops do lado oposto são forçados a sair, alimentando o movimento;
- (c) o filtro de horário (após 60min) reduz fakes do primeiro impulso de abertura, que historicamente tem maior taxa de reversão.

A estratégia **ganha de**:

- operadores que entraram contra o rompimento sem confirmação (perdem stop);
- operadores que tentaram fade do movimento no range sem critério (perdem stop);
- ruído de pré-abertura que não tem follow-through quando o fluxo institucional confirma direção.

### 2.2 De quem ela ganha dinheiro?

| Contraparte | Por que perde |
|---|---|
| Day trader amador com viés intra-range | Tenta operar reversão dentro do range sem aceitar que o rompimento confirma direção |
| Algo de scalping de bandas curtas | Stops curtos pegam ruído normal pós-rompimento |
| Operador emocional pós-gap | Entra na abertura, sofre nos 60min de range e sai no stop quando começa o movimento real |
| Posicionado contrário ao fluxo institucional | Em B3, fluxo institucional matinal tende a definir direção do dia |

### 2.3 Quando ela DEIXA de funcionar (regimes adversos)?

Esta estratégia **falha de forma sistemática** em pelo menos três regimes:

| Regime adverso | Por que falha |
|---|---|
| **Lateralidade prolongada (range day)** | Rompe, volta, rompe pro outro lado, volta — alta frequência de stop com baixo follow-through |
| **Pré-evento macro (Copom, FOMC, Payroll)** | Liquidez reduzida e gap-and-go aleatório invalidam a hipótese de opening range significativo |
| **Volatilidade compressed (VIX local baixíssimo)** | Range de 60min é tão estreito que o rompimento ocorre com 5 pontos — qualquer ruído gera stop |

> **A POV §3.6 já neutraliza o segundo regime** (janelas vedadas em torno de eventos macro). Os outros dois são responsabilidade dos filtros da §5 deste documento.

---

## 3. Lógica de entrada (descritiva, não implementação)

> **Esta seção descreve a INTENÇÃO da estratégia. A IMPLEMENTAÇÃO técnica (código MQL5/NTSL) vem na SPEC da estratégia futura.** Albert escreve em linguagem operacional, não em pseudocódigo.

### 3.1 Construção do Opening Range (OR)

1. A cada pregão, registrar o **máximo** e **mínimo** dos primeiros **60 minutos** de pregão (das 09h00 às 10h00 nos horários padrão da B3).
2. Esse intervalo `[OR_low, OR_high]` é o **range de abertura**.
3. Esperar **15 minutos** adicionais (POV §3.6 — janela vedada do início do pregão respeitada com folga adicional).

### 3.2 Gatilho de entrada long

| Condição | Descrição |
|---|---|
| (a) Preço fechou candle de 5m **acima** de `OR_high` | Confirmação visual de rompimento |
| (b) Filtros §5 todos verdes | Ver §5 |
| (c) Risk Engine permite (Art. 15º) | Validação obrigatória |
| (d) Stop calculado e dentro da POV §3.5 | 150–250 pontos para WIN |

### 3.3 Gatilho de entrada short

Espelho do long:

| Condição | Descrição |
|---|---|
| (a) Preço fechou candle de 5m **abaixo** de `OR_low` | Confirmação visual de rompimento |
| (b) Filtros §5 todos verdes | Ver §5 |
| (c) Risk Engine permite | Validação obrigatória |
| (d) Stop calculado e dentro da POV | 150–250 pontos |

### 3.4 Anti-padrões de entrada (rejeições)

- **Não entrar** se rompimento ocorreu no minuto 16 após a abertura (muito próximo do final da janela vedada).
- **Não entrar** se já houve rompimento e retorno ao range no mesmo dia (range invalidado).
- **Não entrar** se Risk Engine indicar gain lock já atingido (Art. 17º).
- **Não entrar** após uma loss do dia que coloque o operador a < 50 pontos do limite diário (POV §3.2 — proteção de drawdown).

---

## 4. Lógica de saída

### 4.1 Stop loss

| Critério | Valor |
|---|---|
| Tipo de stop | Fixo, em pontos, calculado na entrada |
| WIN | **180 pontos** (proposta inicial, dentro da faixa POV 150–250) |
| Referência | Stop fica abaixo do `OR_low` em entrada long; acima do `OR_high` em entrada short |
| **Trailing após gatilho** | Quando o preço alcança **1R (180 pontos a favor)**, move stop para break-even + 5 pontos (gestão de risco assimétrica) |

> **180 pontos é proposta.** Backtest pode mostrar valor melhor entre 150 e 250 — refinamento esperado.

### 4.2 Take profit

Sem take profit fixo. **Saída discricionária por:**

| Critério de saída | Descrição |
|---|---|
| Trailing após break-even | Stop sobe progressivamente em janelas de 5 minutos seguindo o mínimo (long) ou máximo (short) do candle anterior |
| **Reversão de fluxo** | Candle de 5m fechando contra o trade com volume acima da média móvel de 20 candles |
| **Tempo máximo em posição** | **120 minutos** (proposta) — se não atingiu nem stop nem trailing após 120min, encerrar manualmente (provável range day) |
| **Janela vedada de fechamento** | 10min antes do fechamento (POV §3.6) — encerrar qualquer posição aberta |

### 4.3 R:R esperado

- **R** = 180 pontos (stop)
- **TP médio esperado** = 220–280 pontos (1.2–1.5R) — refinamento empírico no backtest
- **R:R alvo da estratégia** = **1.3R** (proposta inicial)

---

## 5. Filtros propostos

> Filtros são **pré-condições obrigatórias**. Se qualquer filtro retornar vermelho, **não entra**.

### 5.1 Filtro de regime (tendência vs lateral)

| Indicador | Critério para entrada |
|---|---|
| **ADX (14)** no diário | ≥ 20 (mercado com direção) |
| **ADX (14)** no 15m | ≥ 18 (microestrutura coerente) |
| Não operar se | ADX diário e 15m ambos < 20 → range day provável |

### 5.2 Filtro de volatilidade

| Indicador | Critério para entrada |
|---|---|
| **ATR(14)** no 15m | ≥ 50 pontos WIN (volatilidade mínima para o stop ser estatisticamente relevante) |
| **ATR(14)** no 15m máximo | ≤ 400 pontos (volatilidade explosiva — provável evento macro não-mapeado) |

### 5.3 Filtro de horário (consistente com POV §3.6)

| Janela | Permitido? |
|---|---|
| 09h00–09h15 | ❌ Janela vedada do início (POV §3.6) |
| 09h15–10h00 | ❌ Construção do OR — não opera |
| 10h00–10h15 | ❌ Folga adicional após construção (anti-padrão §3.4) |
| 10h15–17h40 | ✅ Operacional (sujeito a outros filtros) |
| 17h40–17h50 | ❌ Janela vedada do fechamento (POV §3.6) |

### 5.4 Filtro macro

| Evento no dia | Ação |
|---|---|
| **Copom** (qualquer horário) | Não operar o dia inteiro |
| **FOMC** (madrugada/dia) | Não operar o dia inteiro |
| **IPCA** (manhã) | Não operar até 11h30 |
| **Payroll EUA** (sexta às 09h30) | Não operar a primeira hora pós-divulgação |
| **Pregão reduzido B3** (D-1 de feriado) | Não operar — janelas vedadas dominam |

---

## 6. Análise contraditória (Voltaire)

> Voltaire **não defende S1.** Voltaire procura os modos de falha mais honestos antes do Founder aprovar.

### 6.1 Por que essa estratégia PODE FALHAR?

#### Modo de falha M1 — Edge erodido por overcrowding

O ORB é uma das estratégias **mais ensinadas** em cursos de day trade no Brasil e no mundo. Se o edge depende de operadores amadores perdendo stop contra o rompimento, e o número de amadores operando ORB **diminui** (porque os que operam mal já quebraram, e os novos foram ensinados a evitar fade), o edge se reduz com o tempo.

**Sinal de erosão:** queda gradual do win rate ao longo de 6 meses de operação real, mesmo com aderência operacional alta.

#### Modo de falha M2 — Range days dominam o regime atual

Se 2026 for um ano de baixa volatilidade direcional na B3 (cenário com Selic alta sustentada e mercado de range), a estratégia gera múltiplos stops por mês com poucos trades vencedores. Os filtros §5 ajudam mas **não eliminam** dias de range disfarçados de tendência inicial.

**Sinal de regime adverso:** sequência de 5+ stops consecutivos em 10 dias úteis com aderência 100%.

#### Modo de falha M3 — Custo > edge no perfil de R$ 5.000

Com 180 pontos de stop (R$ 36 por contrato) e R:R 1.3, o lucro médio esperado é **R$ 47 por trade vencedor**. Com win rate de 45% e 3 operações/dia (POV §3.4), o **lucro esperado diário** é ~R$ 25 — antes de IR. Após IR 20% e custos de corretagem (que dependem de DOC 2), o lucro líquido pode ficar **abaixo do edge mínimo** calculado em CORRETORA-EVAL.md §5.

**Voltaire é honesto:** se DOC 2 mostrar corretagem zero (Clear/Genial/Toro), edge é viável. Se DOC 2 mostrar custo recorrente de plataforma de R$ 200–380/mês (Profit Pro), **a estratégia precisa de win rate ≥ 55%** para sobreviver — patamar não-trivial.

#### Modo de falha M4 — Saída discricionária introduz subjetividade

A §4.2 admite saída por "reversão de fluxo" e "tempo máximo em posição". Saídas discricionárias **destróem** a comparabilidade entre backtest e live. O backtest implementa regra mecânica; o operador real introduz hesitação. **Aderência ≥ 95% (Art. 29º) fica vulnerável.**

**Sinal de problema:** divergência > 30% entre P&L do paper trading e do backtest com mesma configuração (Anexo II — Fase 1 critério de saída).

### 6.2 Que evidência o backtest precisa produzir para refutar M1–M4?

| Modo | Evidência mínima no backtest para validação |
|---|---|
| M1 | Edge sustentado em **3 períodos out-of-sample distintos** (Art. 28º) cobrindo regimes de volatilidade diferentes (alta, média, baixa) |
| M2 | Win rate ≥ 40% mesmo no quartil inferior de volatilidade do período |
| M3 | Expectância líquida positiva **incluindo custos de DOC 2 + IR 20%** + custo recorrente de plataforma rateado por trade |
| M4 | Saída discricionária **eliminada da especificação técnica final** — toda saída mecânica, ou subjetividade quantificada com regras objetivas |

### 6.3 Que sinais em paper trading indicam falha precoce?

> Estes são **gatilhos de descarte da S1** antes mesmo de Fase 2 começar.

- **G1:** Win rate < 35% nos primeiros 30 trades de paper trading → descartar S1 e voltar para tese.
- **G2:** Drawdown simulado > 25% do Bucket Derivativo (R$ 750) → descartar.
- **G3:** Divergência P&L paper vs backtest > 50% → revisitar critérios de entrada/saída.
- **G4:** Aderência < 90% nos primeiros 50 trades → estratégia tem ambiguidade operacional, refatorar.
- **G5:** 5+ stops consecutivos com aderência 100% → regime adverso M2 — pausar até regime mudar.

---

## 7. Hipóteses testáveis

> Valores numéricos esperados. Backtest valida ou refuta.

| Métrica | Hipótese (alvo) | Mínimo aceitável | Refutação se: |
|---|---|---|---|
| **Win rate** | 45% | 40% | < 38% |
| **R:R efetivo médio** | 1.3 | 1.1 | < 1.0 |
| **Expectância matemática bruta** (R:R × Win% − (1−Win%)) | +0.04R por trade | +0.02R | ≤ 0 |
| **Expectância líquida após custos + IR** | +0.025R por trade | +0.01R | ≤ 0 |
| **Frequência de trades por semana** | 8–12 | 5 | < 4 (não amortiza custos fixos) |
| **Drawdown máximo simulado** | < 12% do Bucket Derivativo | < 20% | ≥ 20% |
| **Sharpe ratio (anualizado, sobre retornos diários)** | ≥ 1.2 | ≥ 0.8 | < 0.8 |
| **Profit factor** | ≥ 1.4 | ≥ 1.2 | < 1.1 |
| **Aderência operacional em paper** | ≥ 95% | ≥ 90% | < 90% |
| **Tempo médio em posição** | 40–60 min | 25–90 min | > 120 min (range day disfarçado) |

---

## 8. Critérios de aprovação (Arts. 28º, 29º, 30º)

> Para a S1 sair do paper trading e entrar em Fase 2 (trade real), **todos** os critérios abaixo devem estar verdes. Qualquer um vermelho bloqueia.

### 8.1 Backtest (Art. 28º (a) e (b))

- [ ] Expectância matemática líquida positiva em **3 períodos out-of-sample distintos** cobrindo regimes diferentes (alta volatilidade, média, baixa)
- [ ] Walk-forward sem degradação severa entre janelas (variação de Sharpe entre janelas ≤ 40%)
- [ ] Custos de corretagem **reais da corretora vinculada** (DOC 2 §9) incluídos
- [ ] IR Day Trade 20% incluído
- [ ] Custo recorrente de plataforma rateado por trade incluído

### 8.2 Paper trading (Art. 28º (c) e Fase 1 Anexo II)

- [ ] Mínimo de **30 dias úteis OU 100 operações** (o que vier depois)
- [ ] Win rate ≥ 40% no paper
- [ ] Aderência operacional ≥ 95% (Art. 29º)
- [ ] Expectância paper dentro de 30% da expectância do backtest (Fase 1 critério de saída)
- [ ] Drawdown simulado < 20% do Bucket Derivativo

### 8.3 Risk Engine (Art. 28º (d))

- [ ] Todos os validators (max_contracts, daily_loss, gain_lock, kill_switch, trading_window, martingale, simultaneous_position, tax_compliance, etc.) testados nos cenários da estratégia
- [ ] Cobertura ≥ 80% no Risk Engine global (Anexo II Fase 0)
- [ ] Cobertura ≥ 100% nos validators críticos (Arts. 11º, 16º, 18º)

### 8.4 Contingência (Art. 28º (e))

- [ ] Plano de contingência documentado em RUNBOOK-INCIDENTE-TECNICO.md (DOC 5)
- [ ] Treino de cenário em conta demo registrado em journal

---

## 9. Critérios de descarte

> Diferente de §6.3 (descarte durante paper). Estes critérios descartam a S1 **antes** de paper trading, ainda em fase de backtest, e exigem nova proposta de S1.

| ID | Critério | Origem |
|---|---|---|
| D1 | Expectância líquida do backtest **negativa** em qualquer período out-of-sample | Art. 28º (a) |
| D2 | Win rate < 38% em **2 períodos out-of-sample diferentes** | §7 |
| D3 | Drawdown máximo simulado > **30% do Bucket Derivativo** em qualquer período | §6 mod. M2 |
| D4 | Frequência média de trades < 4/semana em qualquer período | §7 (não amortiza custos) |
| D5 | Sharpe < 0.8 em **3 períodos** | §7 |
| D6 | Modo de falha M1, M2, M3 ou M4 confirmado por evidência empírica | §6 |

> Se qualquer critério acima for ativado, **a S1 é descartada** e o Founder propõe nova estratégia base (S2 candidata). Este documento é reutilizado como template para a próxima tese.

---

## 10. Estratégias alternativas consideradas

> Apresentação resumida das alternativas que **não** foram propostas como S1. Razão da preterição registrada para evitar revisitar sem informação nova.

### 10.1 VWAP Mean Reversion intra-day em WDO

- **Tese resumida:** preço se afasta do VWAP em horários de baixa liquidez, reverte para a média.
- **Por que não foi S1:** stop em WDO é estreito (3–7 pontos POV §3.5), e a estratégia exige stops com tolerância de ruído maior em momentos de baixa liquidez. Conflita com a POV vigente.
- **Quando reconsiderar:** se Carlos quiser priorizar WDO sobre WIN OU se POV for emendada para stops mais largos em WDO.

### 10.2 Trend Following por médias móveis WIN diário

- **Tese resumida:** swing de 1–3 dias seguindo cruzamento de médias.
- **Por que não foi S1:** time horizon é swing, não day trade. Conflita com Anexo II — fases 1–4 são day trade. Exige emenda constitucional.
- **Quando reconsiderar:** se a Constituição for emendada para incluir swing trade (cooldown 30 dias — Art. 38º).

### 10.3 Scalping de banda estreita WIN

- **Tese resumida:** stops curtos (40–80 pontos), R:R 1:1, 20+ trades/dia em alta frequência.
- **Por que não foi S1:** estouro do limite de operações da POV §3.4 (3 trades/dia em fases iniciais). Exige aumento via cooldown reduz-proteção (14 dias). Operacionalmente exige automação plena, incompatível com Fase 1 (paper manual).
- **Quando reconsiderar:** Fase 4+ com Setup A+ definido + automação completa.

### 10.4 Mean reversion em range do mid-day

- **Tese resumida:** opera dentro do range identificado entre 11h30 e 14h30.
- **Por que não foi S1:** requer identificação confiável de "range" em tempo real — difícil sem modelagem complexa. Reservada para versão futura quando Fase 3 estiver consolidada e Carlos puder operar lógica condicional mais complexa.
- **Quando reconsiderar:** Fase 3+ com ferramental de detecção de regime consolidado.

---

## 11. Gate Founder

> Founder escolhe **uma** das três opções abaixo. Não há "decisão parcial".

```
[ ] OPÇÃO A — Aprovar S1 como Opening Range Breakout 60m WIN
    Carlos aprova esta tese como S1 e libera execução das fases:
      (1) implementação técnica do backtest da S1 (SPEC futura)
      (2) primeira rodada de backtest histórico (Bloco F do PLAN)
      (3) avaliação de gates §8 antes de Fase 1

    Carlos reconhece que esta aprovação NÃO compromete capital real
    nem autoriza operação automática — apenas autoriza o estudo.

    Data: ___/___/______

    Assinatura simbólica: _________________________


[ ] OPÇÃO B — Rejeitar e propor S1 alternativa
    Carlos rejeita esta proposta e indica abaixo qual estratégia
    deve substituir como S1, com motivação escrita:

    Nova S1 proposta: _________________________________________

    Motivação: ________________________________________________
              ________________________________________________

    Data: ___/___/______

    Assinatura simbólica: _________________________


[ ] OPÇÃO C — Adiar definição de S1
    Carlos prefere adiar a definição de S1 até resolver dependências:

    Dependências bloqueantes (marcar):
    [ ] DECISION-MEMO-LINUX-OR-WINDOWS (DOC 1)
    [ ] CORRETORA-EVAL (DOC 2)
    [ ] POV-VIGENTE v1.1 com Setup A+ definido
    [ ] Outro: _____________________

    Data esperada para retomada: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../../CONSTITUICAO.md) Arts. 11º, 12º, 14º, 16º, 17º, 20º, 28º, 29º, 30º + Anexo II + Anexo III
- [`POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) §3.5 stops, §3.6 janelas vedadas, §3.10 Setup A+
- [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](../DECISION-MEMO-LINUX-OR-WINDOWS.md) — define linguagem de execução final (NTSL ou MQL5)
- [`CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) §5 — edge mínimo por corretora vigente
- [`apps/cam-cockpit/backend/cam/features/backtest/`](../../apps/cam-cockpit/backend/cam/features/backtest/) — engine que vai validar esta tese empiricamente
- [`apps/cam-cockpit/backend/cam/features/strategies/`](../../apps/cam-cockpit/backend/cam/features/strategies/) — onde a implementação concreta da S1 será adicionada após aprovação

---

> **Princípio operacional deste documento:**
>
> Albert propõe. Voltaire contradita. Sun avalia o mercado. O Founder aprova, rejeita ou adia.
>
> Estratégia sem tese é destino sem mapa. Tese sem critérios de descarte é fé, não disciplina.

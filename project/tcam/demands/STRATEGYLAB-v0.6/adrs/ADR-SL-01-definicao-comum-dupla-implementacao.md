---
template: ADR
phase: ARCH
status: Accepted
demanda: STRATEGYLAB-v0.6
---

# ADR-SL-01 — Definição de estratégia comum + dupla implementação independente (Python + MQL5)

> **Data:** 2026-06-03
> **Status:** Accepted — Founder 2026-06-03
> **Lead:** Oscar
> **Aprovador final:** Founder
> **Vive em:** domínio `project`
> **Supersede:** decisão central da `ARCH-NOTE-PARIDADE-EA-PYTHON.md` (modelo (a)/(c)) —
> invertida pelo Founder (Q3).

---

## 1. Contexto

A tríade StrategyLab precisa que a **mesma estratégia** rode em dois mundos: backtest
matemático em **Python (CAM)** e execução em **MQL5 (EA, Strategy Tester/DEMO)**. A
pergunta estruturante é: *qual é a fonte da verdade da estratégia e como se garante que
as duas execuções concordam?*

A nota de ARCH anterior recomendava **spec declarativa única + dupla implementação +
suíte de paridade** (modelo a), e diferia **codegen/DSL geradora** (modelo c) como alvo
futuro "quando 3+ estratégias convergissem". Com 10 estratégias no escopo (5
multi-símbolo), o codegen parecia ficar mais atraente mais cedo.

O Founder decidiu o oposto (Q3, **verbatim**): *"assim o codegen não teremos pela
aplicação, não quero dupla implementação Python para CAM e EA... vamos de backtests em 2
locais... redundância para segurança."*

**Interpretação acatada:** o Founder quer **DUAS implementações independentes e
deliberadas** — Python escrito à mão no CAM, MQL5 escrito à mão no EA — **sem nenhuma
gerar a outra**. A redundância **é o recurso de segurança**: dois caminhos de
implementação dissimilares que devem convergir nos valores brutos. Isto é **N-version
programming / redundância dissimilar** — uma escolha de engenharia válida e clássica.
A paridade muda de natureza: deixa de ser "espelho gerado, correto por construção" e
passa a ser **dupla checagem independente que detecta dessincronização**.

> O Founder foi explícito: **não reintroduzir codegen.** Este ADR arquiteta sobre a
> decisão dele, não a contesta.

---

## 2. Decisão

### 2.1 Sem codegen, sem DSL como gerador. Dupla implementação deliberada.

1. **Não há gerador de `.mq5` a partir da DEF.** O EA é **escrito à mão** em MQL5,
   seguindo a DEF comum como **especificação legível**.
2. **Não há gerador de Python a partir da DEF como "linguagem".** O Python consome a DEF
   via o **compilador existente** (`strategies/dsl/{parser,compiler}`), que já transforma
   uma definição declarativa em estratégia executável **com AST whitelist segura (sem
   eval)**. Isto **não** é codegen no sentido proibido (não emite código-fonte de outra
   linguagem nem gera o lado MQL5) — é a forma natural do lado Python ler a DEF. Fica
   explícito para não haver ambiguidade.
3. As duas implementações são **independentes por construção**: escritas por caminhos
   diferentes, de propósito, como redundância de validação cruzada.

### 2.2 A DEF de estratégia comum (especificação, não gerador)

Existe **uma** DEF por estratégia — um artefato legível, versionado em `/project`, que
**ambos** os lados seguem. Não gera código; é a **referência canônica humana**. Conteúdo
mínimo (subconjunto MVP do contrato C1–C14, **sem** C7/C8):

```yaml
strategy: D1_orb30_win
family: D            # derivativo intraday
symbols: [WIN]       # lista — par/cesta quando multi-símbolo
unit: single         # single | pair | basket   (par/cesta como unidade — C14/Q10)
timeframe: M5        # TF de decisão; barra canônica M1→TF (C1/C7)
session:             # janela B3, fuso America/Sao_Paulo (C2/C11)
  tz: America/Sao_Paulo
  open: "09:00"
  close: "17:55"
  flat_at_close: true
indicators:
  - type: opening_range
    minutes: 30
signal:
  long:  "price > opening_range.high"   # ordem de avaliação C3: saída antes de entrada
  short: "price < opening_range.low"
  fill: next-bar-open                   # C4
  intrabar: worst-case                  # C5
  gap: honest                           # C6
stop:   { type: points, value: 150 }    # C10, mecânico
target: { type: points, value: 300 }
sizing: { contracts: 1, rounding: floor } # C9 determinístico
seed: 42                                 # C12 determinismo
# multi-símbolo (quando unit: pair/basket):
# spread:  "P[WIN] - beta * P[WDO]"
# z_entry: 2.0   z_exit: 0.5   z_stop: 3.5
# leg_execution: atomic                  # entra/sai das pernas no mesmo evento (C14)
```

- **Esta DEF é a unidade de paridade.** Tudo que diferencia um experimento do outro está
  declarado aqui — nada de default não-declarado (princípio do EDGE-CONTRATO §3.1).
- **Versionada em `/project`** (não em `/apps`), referenciada pelo README da feature.

### 2.3 A camada de paridade é o que garante a convergência

Como as duas implementações **não** se geram, a única garantia de que concordam é a
**dupla checagem trade-a-trade** (a feature `strategy_lab/parity`):

- Os dois mundos exportam um **ledger de trades de schema único** (§6 da ARCH-NOTE).
- A paridade compara, **alinhado por barra de sinal**: **100% dos sinais coincidem**
  (mesma barra, mesmo lado), **preço de entrada/saída ≤ 1 tick**, **volume financeiro
  idêntico**, **qtd idêntica**, **motivo de saída idêntico** (Q6 confirmado).
- **PASS** = convergência → confiança de que a lógica está certa nos dois.
- **FAIL** = divergência → **bug em UM dos dois**; abre BUG (`teczi-bug-fix`); investiga
  na ordem do pipeline (EDGE-CONTRATO §5.5). **Nunca** "tunar" um lado para casar sem
  entender a causa.

A paridade é, portanto, **o detector de dessincronização** — o mecanismo que paga o custo
da redundância (ver §4).

### 2.4 O que vira da DSL existente

A `strategies/dsl/{parser,compiler}` **não é descartada nem promovida a gerador
universal**. Ela é **rebaixada de "fonte única geradora" para "compilador do lado
Python"**: lê a DEF e produz a estratégia executável Python. É **estendida** para
multi-símbolo (ver §2.5). O lado MQL5 **não** a usa — lê a DEF como texto.

### 2.5 Par / multi-símbolo como unidade (C14)

A DEF e o compilador Python ganham `unit: single|pair|basket` e a gramática de spread/
z-score:

- **`pair`** (D3, LS1, LS2, LS3): dois símbolos, spread β-ajustado, **execução atômica
  das pernas**, contabilização **par como unidade** (Q10 — gain/loss do spread agregado).
- **`basket`** (S1): N símbolos, seleção por ranking (cross-sectional momentum) — modelo
  distinto do par.
- **Forma escolhida:** **extensão da DEF + um tipo `unit`** (não uma DEF separada por
  classe). Mantém uma gramática única, evita bifurcar o formato. O compilador Python
  ramifica por `unit`; o `.mq5` à mão implementa a mesma semântica de pernas atômicas.

---

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | **Codegen MQL5 a partir da DEF** (gerar `.mq5`) | **Vetada pelo Founder (Q3).** Além disso: o gerador vira código a validar; templates MQL5 parametrizados são frágeis; a "paridade por construção" esconde bugs do próprio gerador. |
| 2 | **ZeroMQ: Python cérebro, EA braço** (um só cérebro) | Mata o Strategy Tester (EA dependente de processo externo não roda no tester nativo) — exatamente o ambiente que o Founder usa. Cria caminho de execução Python→ordem. Já rejeitada na ARCH-NOTE. |
| 3 | **Uma única implementação (só Python OU só MQL5)** | Perde a redundância que o Founder quer ("backtests em 2 locais"). Sem segunda fonte, não há dupla checagem. |
| 4 | **DSL geradora dos dois lados (modelo c da ARCH-NOTE)** | Mesma razão da #1 — é codegen. Vetada. |
| 5 | **DEF comum + dupla implementação independente + paridade (ESCOLHIDA)** | É exatamente o que o Founder pediu: redundância dissimilar, dois backtests, paridade como rede de segurança. |

---

## 4. Consequências

### Positivas
- **Redundância dissimilar real:** dois caminhos independentes que se validam mutuamente;
  um bug que afeta só um lado é **detectado** pela paridade (é o ponto da decisão do Founder).
- **Strategy Tester preservado:** o EA roda nativo no tester, sem depender de runtime Python.
- **Sem gerador para manter/validar:** não há a classe de bug "o codegen emitiu errado".
- **Reuso máximo:** o compilador Python (`strategies/dsl`) é aproveitado quase inteiro.
- **DEF legível** serve de documentação viva e de contrato de paridade ao mesmo tempo.

### Negativas
- **Custo de manutenção dobrado e manual (o trade-off honesto).** Toda mudança de lógica
  precisa ser feita **duas vezes à mão** (Python **e** `.mq5`) e mantida sincronizada
  manualmente. Com 10 estratégias (5 multi-símbolo), são **até 20 implementações** a mais
  evoluir em paralelo. **Não há nada que force as duas a concordar exceto a paridade.**
  → **Mitigação:** a camada de paridade **é** o controle de qualidade da sincronização —
  ela tem que ser executada **a cada mudança de qualquer lado**, e um FAIL **bloqueia** a
  promoção. A disciplina "rodou paridade verde depois de mexer em qualquer lado" é o que
  impede a dessincronização silenciosa. Isto precisa estar explícito no SPEC como gate.
- **A paridade carrega um peso maior** do que carregaria com codegen: aqui ela é a **única**
  defesa contra divergência, não uma checagem redundante. Logo, a paridade precisa ser
  **robusta e fácil de rodar** (idealmente automatizável no fluxo de cada estratégia).
- **Risco de "dois experimentos parecidos"** (EDGE-CONTRATO §5.5): se as DEFs/datasets não
  forem rigorosamente os mesmos, a paridade compara coisas diferentes. → A DEF única +
  mesmo dataset (C13) + provenance mitigam.

### Neutras
- O MVP-bruto (sem C7/C8) **facilita** a paridade: a maior fonte de divergência (modelo de
  custo) desaparece. A dupla implementação fica mais fácil de bater agora; o custo de
  manutenção cresce quando custos entrarem (Later).
- A DEF vive em `/project`, não em `/apps` (política de documentação do Founder).

---

## 5. Custo de reversão

**Médio.** A DEF e o compilador Python são baratos de evoluir. Se um dia o Founder
quiser codegen (reabrir Q3), a DEF declarativa **já é o embrião** de um gerador — o
caminho de volta existe e foi deixado aberto pela escolha de manter a DEF formal. O que é
caro de desfazer é a quantidade de `.mq5` escritos à mão acumulados (cada estratégia vira
trabalho manual investido), mas isso é custo afundado, não barreira arquitetural.

---

## 6. Referências

- ARCH: [`../ARCH-STRATEGYLAB-TRIAD.md`](../ARCH-STRATEGYLAB-TRIAD.md)
- SCOPE: [`../SCOPE-STRATEGYLAB-TRIAD.md`](../SCOPE-STRATEGYLAB-TRIAD.md) (Q3, §4)
- Contrato de paridade: [`../EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md`](../EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md) (C1–C14, §3.1, §5)
- ADR anterior invertida: `archive/project_archive/ARCH-NOTE-PARIDADE-EA-PYTHON.md` (modelos a/b/c)
- Código: `apps/cam-cockpit/backend/cam/features/strategies/dsl/{parser,compiler}.py`
- ADRs relacionadas: [ADR-SL-02](ADR-SL-02-persistencia-backtest-mvp-bruto.md) · [ADR-SL-03](ADR-SL-03-execucao-multisimbolo-ea-mt5.md)

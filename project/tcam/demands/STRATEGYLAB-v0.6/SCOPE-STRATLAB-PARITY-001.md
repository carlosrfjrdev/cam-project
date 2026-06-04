---
template: SCOPE
phase: DISC
status: Superseded-parcial — insumo do SCOPE-STRATEGYLAB-TRIAD (v0.6)
produto: CaM (cam-cockpit)
id: SCOPE-STRATLAB-PARITY-001
slug: strategy-lab-parity-mt5
data: 2026-06-03
lead: Marty
solicitante: Founder
superseded_por: SCOPE-STRATEGYLAB-TRIAD.md
modo: construção/estudo — Constituição NÃO vigente nesta fase; Risk Engine/kill/journal/provisão desativados; execução de ordem ATIVA no EA (Strategy Tester/DEMO); live trading só por ato explícito do Founder; broker = MT5
---

> ⚠️ **NOTA DE SUPERSESSÃO PARCIAL (Leo, 2026-06-03).** Este SCOPE permanece como **insumo
> válido** (todo o conteúdo de paridade C1–C14 e a régua anti-data-snooping continuam corretos),
> mas **deixa de ser o SCOPE de título**. Ele foi **reorganizado e atualizado** pelo
> [`SCOPE-STRATEGYLAB-TRIAD.md`](./SCOPE-STRATEGYLAB-TRIAD.md), que:
> (1) mapeia a demanda nos **três módulos de produto** Assets Strategy / RunTests / Experts;
> (2) registra a decisão do Founder de **MVP SEM CUSTOS** — a paridade vira de **lógica**, não de
> fricção (C7/C8 custo/IR → **Later**); (3) eleva o **otimizador de parâmetros** e a
> **persistência papel/ticks/indicadores** a requisitos de primeira classe; (4) reposiciona a
> **paridade** de título para **sub-objetivo**. As Q1–Q9 daqui foram reaproveitadas/atualizadas
> no §9 do SCOPE-TRIAD. **Use o SCOPE-TRIAD como fonte ativa; este, como referência de paridade.**

# SCOPE — STRATLAB-PARITY-001 · Strategy & Backtest Analyser + EAs MT5 + camada de Paridade

> **Data:** 2026-06-03
> **Status:** Draft
> **Produto:** CaM — cam-cockpit
> **Lead:** Marty
> **Solicitante:** Founder
> **Fronteira (decisão do Founder, 2026-06-03):** Fase de **construção e estudo** — a **Constituição não está vigente** neste laboratório. Risk Engine, kill switch, journal e provisão fiscal estão **desativados no momento**. **Execução/envio de ordem PRECISA funcionar no EA** (backtest no Strategy Tester do MT5 + conta DEMO). **Live trading (conta real)** é a **única** linha que permanece fora — entra **apenas quando o Founder disser explicitamente**. Broker fixado em **MT5 por enquanto**.

---

## 1. Problema (1 parágrafo)

O Founder elegeu 12 estratégias (famílias D/V/S/LS/F/H) e precisa de uma capacidade para **definir, rodar e VALIDAR edge** com rigor estatístico antes de qualquer decisão de operar. Hoje não há motor de backtest no CaM nem forma sistemática de provar que uma estratégia tem expectância líquida out-of-sample. Além disso, o Founder quer construir os mesmos setups como EAs no MetaTrader 5 (Strategy Tester) e precisa de **garantia de que o resultado do MT5 e o resultado do Python representam a mesma estratégia** — caso contrário, o backtest de um ambiente vira falsa confiança para o outro. O problema central, portanto, não é só "ter um backtester": é **ter um backtester confiável + um espelho MT5 + uma camada que prove paridade entre os dois**.

## 2. Usuário / contexto

- **Usuário único:** Carlos (Founder), pesquisando estratégias na Fase 0 do CaM, cockpit local Windows 11.
- **Onde acontece:** ambiente local — Python 3.12/FastAPI (CaM) para o Strategy Lab; **MT5 + MQL5 para os EAs (broker fixado: MT5 por enquanto)**; dados de tick/candle já extraíveis do MT5 (premissa resolvida).
- **Quando aparece:** ciclo de research/construção — o Founder define uma estratégia, roda backtest nos dois ambientes (EA executa ordens no Strategy Tester/DEMO), compara, e decide se há edge. Constituição/Risk Engine/journal/provisão **desativados nesta fase**; live trading só quando o Founder liberar.

## 3. Resultado esperado

Quando entregue, o Founder consegue: (a) descrever uma estratégia uma vez e rodá-la no Strategy Lab Python gerando métricas + walk-forward + relatório de edge; (b) ter o EA MT5 equivalente para rodar no Strategy Tester; (c) rodar **a mesma estratégia nos dois ambientes** sobre os mesmos dados e receber um **relatório de paridade** que afirma, com tolerância numérica explícita, se os dois resultados batem ou divergem — apontando ONDE divergem quando divergem.

## 4. Dentro (In)

### 4.1 Strategy Lab Python (CaM)
- Motor de backtest event-driven em Python para as famílias **intraday e à vista negociável** (D, V, S, LS).
- Camada de definição de estratégia (interface comum: sinal de entrada/saída, stops, alvos, filtros de regime).
- Ingestão de dados tick/candle **exportados do MT5** como fonte (premissa resolvida).
- Modelo de custos explícito e parametrizável: corretagem, emolumentos, slippage, IR — conforme premissas do catálogo (§II).
- Métricas de avaliação: expectância líquida, WR, R:R, Sharpe, drawdown, nº de trades, distribuição de cauda.
- **Walk-forward** (janelas rolantes in/out-of-sample) e régua anti-data-snooping (DSR, ≥200 trades OOS, % de janelas lucrativas).
- Relatório de edge por estratégia (artefato legível — Markdown/HTML/notebook).

### 4.2 EAs MT5 (MQL5)
- EAs para as famílias **D, V, S, LS** (setups negociáveis no MT5), rodáveis no **Strategy Tester** do MT5.
- Mesma lógica de sinal/stop/alvo/filtro das estratégias Python correspondentes.
- Mesmo modelo de custo/slippage configurável no Strategy Tester, alinhado ao Python.
- **Execução/envio de ordem ATIVO no EA** — o EA **envia, modifica e fecha ordens** (entrada, stop, alvo, saída) no **Strategy Tester** e em **conta DEMO**. É requisito: o EA tem que operar de fato para o backtest do MT5 ser real.
- **Limite atual:** conta **DEMO**, sem live trading. Live (conta real) só quando o Founder liberar explicitamente.

### 4.3 Otimização de parâmetros (Python)
- **Otimização automática de parâmetros no Strategy Lab Python** (grid/random/walk-forward optimization) — **habilitada nesta fase**.
- Sob a régua anti-data-snooping do Jim (DSR penalizado pelo nº de combinações, validação OOS), para não virar overfit.
- A otimização do Strategy Tester nativo do MT5 fica opcional/secundária; a fonte de otimização canônica é o Python.

### 4.4 Camada de Paridade / Espelho
- Especificação de **contrato comum de estratégia** (mesma definição de barra, mesmo timestamp, mesma regra de preenchimento de ordem) que os dois lados devem honrar.
- Pipeline de comparação: dado o mesmo dataset + mesma estratégia, comparar trade-a-trade (ou métrica-a-métrica) Python × MT5.
- **Relatório de paridade** com tolerância numérica explícita: lista de trades casados, divergências, e classificação (paridade OK / divergência tolerável / divergência crítica).
- Convenção única de custos/slippage para os dois lados (parity de premissas, não só de lógica).

### 4.5 Frontend (React + Vite + MUI)
- **UI do Strategy Lab no cockpit** — **dentro do escopo** (decisão do Founder).
- Visualização de resultados de backtest: curva de equity, métricas, distribuição de trades, drawdown.
- Visualização do **relatório de paridade** Py↔EA (trades casados, divergências, veredito PASS/FAIL).
- Disparo/configuração de runs de backtest e de otimização a partir da UI.
- Comparação visual entre estratégias e entre as duas execuções (Python × MT5).

## 5. Fora (Out)

- ❌ **Live trading em conta REAL** — a **única** linha que permanece fora. Entra **apenas quando o Founder disser explicitamente**. (Execução de ordem em Strategy Tester/DEMO está **dentro** — §4.2.)
- ❌ **Risk Engine, kill switch, journal, provisão fiscal** — **desativados nesta fase** por decisão do Founder; fora deste escopo de construção. Voltam quando a operação real for habilitada.
- ❌ **EAs para famílias F (FIIs) e H (holding dividendos)** — são buy&hold de longo prazo, não setups de Strategy Tester intraday (ver Later).
- ❌ **Broker Profit / outros brokers** — broker fixado em **MT5 por enquanto**; demais ficam fora deste ciclo.

## 6. Depois (Later)

- ⏳ **Backtest de F1 (FII Core+Yield) e H1 (Quality Dividend Hold)** — definir se entram no engine como módulo buy&hold/total-return separado, ou se ficam em análise de carteira (pergunta aberta Q4). Não são compatíveis com o engine intraday event-driven nem com Strategy Tester de EA.
- ⏳ **Live trading em conta real** — quando o Founder liberar. Nesse momento, **reativam-se** Risk Engine, kill switch, journal e provisão fiscal, e a Constituição volta a vigorar para a camada de operação.
- ⏳ **Bridge ZeroMQ ao vivo** para sinais/dados — quando fizer sentido para a operação real.
- ⏳ **Reavaliação de broker** (MT5 vs Profit vs outros) — fora deste ciclo; MT5 fixado por enquanto.

## 7. Atores / personas envolvidas

| Persona | Papel no DISC/discovery |
|---|---|
| **Marty** (lead) | Delimitação de escopo, In/Out/Later, anti-feature-factory |
| **Jim** | Quant/edge — régua anti-data-snooping, métricas, walk-forward |
| **Nassim** | Risco de cauda/ruína — distribuição de tail, Monte Carlo empírico |
| **Ada** | Dados — provenance tick/candle MT5, qualidade, dedupe |
| **Nikola** | Implementação do engine Python (futuro CODE) |
| **Oscar** | Arquitetura do contrato de estratégia + camada de paridade (ARCH) |
| **Wyck** | Fluxo/tape — para setups dependentes de confirmação de fluxo (V1, D) |
| **Barsi** | Famílias F/H — opinar se/como entram no engine (Later) |
| **Founder** | Aprova SCOPE e cada gate; dono das decisões de tolerância/paridade |

## 8. Perguntas abertas

- [ ] **Q1 — Fonte de verdade dos dados:** o dataset canônico para os dois lados é sempre o tick/candle **exportado do MT5**? O Python consome o mesmo arquivo, ou cada ambiente pode usar sua própria leitura? (Paridade exige fonte única.)
- [ ] **Q2 — Granularidade da paridade:** a paridade é exigida **trade-a-trade** (cada entrada/saída casa), **métrica-a-métrica** (expectância/Sharpe/drawdown batem), ou **ambos em níveis distintos**? Qual é o nível mínimo aceitável?
- [ ] **Q3 — Tolerância numérica do parity:** qual desvio é "OK" vs "crítico"? (ex.: ±1 tick de preenchimento, ±X% no PnL total, ±N trades de diferença). Definir tolerância por família.
- [ ] **Q4 — FIIs/Holding no engine:** F1 e H1 são buy&hold/total-return — entram em um módulo de backtest separado, ficam em análise de carteira, ou ficam totalmente fora do laboratório nesta fase?
- [ ] **Q5 — Escopo de ativos à vista:** as famílias V/S/LS à vista cobrem qual universo (lista fixa de tickers? cesta? índice)? O MT5 do Founder dá acesso confiável a esses ativos à vista para o EA, ou só derivativos (WIN/WDO)?
- [ ] **Q6 — Custos/slippage idênticos nos dois lados:** como garantir que Python e MT5 usam **exatamente** o mesmo modelo de corretagem/emolumento/slippage/IR? Quem é a fonte canônica dos parâmetros de custo? (Divergência de custo = divergência de PnL falsa.)
- [ ] **Q7 — Convenção de barra e timestamp:** Python e MT5 tratam abertura/fechamento de candle, fuso, e ordem de preenchimento (na abertura vs no fechamento da barra) de forma idêntica? Definir a regra única.
- [ ] **Q8 — Definição de "estratégia única":** a definição de estratégia é escrita uma vez e gera os dois lados (codegen), ou são duas implementações independentes (Python + MQL5) que a paridade audita? (Decisão de ARCH, mas o Founder precisa sinalizar a intenção.)
- [ ] **Q9 — LS à vista vs derivativo:** LS1 (spread WIN×WDO) é derivativo e cabe no MT5; LS2 (pair cointegração, swing) e LS3 (pair ON×PN intraday) são à vista de 2 pernas — o Strategy Tester (single-symbol por padrão) suporta? Quais L&S têm EA e quais ficam Python-only?

## 9. Riscos de produto

| Risco | Tipo | Descrição | Mitigação proposta |
|---|---|---|---|
| **Divergência silenciosa EA↔Python** | Factibilidade/Confiança | Os dois ambientes "rodam", dão números parecidos, mas representam estratégias sutilmente diferentes (fill, timestamp, custo) → o Founder confia num edge que não existe. **Risco-mãe deste projeto.** | Camada de paridade com tolerância explícita + relatório que falha alto quando diverge. Paridade é gate, não enfeite. |
| **Feature factory de estratégias** | Valor | Construir 12 estratégias × 2 ambientes antes de validar 1 fim-a-fim → muito código, pouco aprendizado. | Validar **uma** estratégia (sugestão: D1 ORB-30, simples e líquida) fim-a-fim com paridade antes de escalar. |
| **Falsa precisão do backtest** | Desejabilidade | Engine sem custo/slippage realista ou sem OOS produz edge inflado. | Régua anti-data-snooping do Jim obrigatória; custo no pior quartil; walk-forward. |
| **Inviabilidade no Strategy Tester** | Factibilidade | Setups multi-ativo (D3/LS1 spread WIN×WDO, LS à vista de 2 pernas) podem não rodar fielmente no Strategy Tester (single-symbol por padrão). | Validar no ARCH quais famílias o MT5 suporta; rebaixar para Python-only as que não couberem. |
| **Salto não-intencional para conta real** | Operacional | EA com execução ativa em DEMO ser apontado por engano para conta real antes da liberação do Founder. | EA preso a **conta DEMO** por configuração; checagem de tipo de conta no EA; live só por ato explícito do Founder (guardrails RUNBOOK-WINDOWS). |
| **Overfit pela otimização automática** | Desejabilidade | Otimização de parâmetros no Python encontrar "edge" que é ruído. | Régua anti-data-snooping do Jim: DSR penalizado pelo nº de combinações, validação OOS/walk-forward obrigatória. |
| **Dados não-canônicos** | Factibilidade | Sem fonte/provenance única, cada lado lê dados levemente diferentes → paridade impossível. | Fonte única de dataset (Q1) com provenance (Ada). |

## 10. Classificação P/M/G

**Classificação: G (Grande).**

**Justificativa (proporcionalidade, sem estimativa temporal):**
- São **três subsistemas distintos** com contratos de interface entre eles: engine de backtest Python, EAs MQL5, e camada de paridade. Não é uma funcionalidade — é uma capacidade nova com arquitetura própria.
- Atravessa **duas linguagens e dois runtimes** (Python/FastAPI e MQL5/MT5) que precisam concordar numericamente — acoplamento de difícil verificação.
- Cobre **múltiplas famílias de estratégia** com semânticas diferentes (intraday, swing, long&short, e potencialmente buy&hold).
- Exige **decomposição em TASKs** no PLAN (engine, modelo de custo, walk-forward, contrato de estratégia, EA-base, comparador de paridade, relatórios).
- Tem **decisões arquiteturais abertas** relevantes (codegen vs dupla implementação — Q8; suporte multi-símbolo do Strategy Tester).

> A classificação G reflete **tamanho e decomposição**, não risco/segurança (modificadores de risco/segurança são proibidos no P/M/G — Q8 Founder). A inclusão de **execução de ordem no EA, otimização no Python e frontend** **amplia** o tamanho — são quatro/cinco subsistemas (Strategy Lab, EAs com execução, otimizador, paridade, UI). A paridade entre dois runtimes continua sendo o núcleo de dificuldade.

## 11. Decisão de saída

- [x] **Avançar para ARCH** (recomendado)
- [ ] Incubar
- [ ] Descartar
- [ ] Investigar mais (volta para DISC)

**Próxima fase recomendada: ARCH (Oscar).** Antes de SPEC, há decisões arquiteturais estruturantes que condicionam todo o resto e devem ser resolvidas primeiro:
1. **Contrato de estratégia** e modelo "definição única vs dupla implementação" (Q8).
2. **Arquitetura da camada de paridade** (trade-a-trade vs métrica; tolerância — Q2/Q3).
3. **Fonte de verdade de dados e convenção de barra/custo** (Q1/Q6/Q7).
4. **Quais famílias têm EA viável no Strategy Tester** vs Python-only (Q5/Q9).

> A nota de ARCH já foi produzida (Oscar) — ver [ARCH-NOTE-PARIDADE-EA-PYTHON.md](../analysis/ARCH-NOTE-PARIDADE-EA-PYTHON.md). Após os ADRs candidatos serem decididos pelo Founder, a demanda segue para SPEC. Recomenda-se **fatiar a primeira entrega em uma única estratégia (D1 ORB-30) fim-a-fim com paridade provada** como vertical slice antes de escalar para as 12.

**Quem decide:** Founder · **Quando:** _(pendente)_

## 12. Referências

- Catálogo: [project/strategies/CATALOGO-12-ESTRATEGIAS-ELEITAS.md](../../strategies/CATALOGO-12-ESTRATEGIAS-ELEITAS.md)
- Contrato de edge + paridade (Jim): [project/cam-cockpit/research/EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md](../research/EDGE-CONTRATO-VALIDACAO-PARIDADE-PY-MT5.md)
- Nota de arquitetura (Oscar): [project/cam-cockpit/analysis/ARCH-NOTE-PARIDADE-EA-PYTHON.md](../analysis/ARCH-NOTE-PARIDADE-EA-PYTHON.md)
- Stack: [project/STACK-CAM-OFICIAL.md](../../STACK-CAM-OFICIAL.md)
- Constituição (vigor reativado quando live trading for habilitado): [CONSTITUICAO.md](../../../CONSTITUICAO.md) — Arts. 15º, 18º, 28º–30º, 35º
- Runbook Windows/MT5: [project/runbooks/RUNBOOK-WINDOWS.md](../../runbooks/RUNBOOK-WINDOWS.md)

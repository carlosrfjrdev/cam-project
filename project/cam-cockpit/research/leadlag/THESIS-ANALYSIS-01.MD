---
template: THESIS-ANALYSIS
phase: P&D / Research Lane
status: Draft 1.0 — análise consolidada read-only
produto: CaM
codinome: research-cubo-leadlag
vive_em: project/cam-cockpit/research/THESIS-ANALYSIS-01.MD
data: 2026-06-03
lead: Leo
co_participacao: Jim, Nassim, Ada, Don, Kevin, Voltaire
escopo: análise dos 3 artefatos de tese/scope, sem alterar os originais
gate: Founder pendente
---

# THESIS-ANALYSIS-01 — Cubo de Lead-Lag Cross-Asset

> Análise consolidada da nova tese do CaM para implementação futura na Research Lane.
> Este documento **não promove estratégia**, **não recomenda execução**, **não aciona paper/live**, **não parametriza Risk Engine** e **não justifica exceção constitucional**.

## 1. Artefatos analisados

1. `EDGE-THESIS-LEADLAG-CUBE.md` — tese original v0.1 do Cubo Rápido.
2. `CaM-RESEARCH-CUBO-LEADLAG.md` — tese unificada + scope backend, supersede v0.1.
3. `CaM-SCOPE-FRONTEND-CUBO.md` — scope frontend do Quant Lab.

Leitura constitucional aplicada: Arts. 6, 11, 15, 16, 18, 25, 28-36. Leitura de processo aplicada: NCC-1701 Stage 0, Founder-only gates, estado real vence intenção, reuso antes de criação, proporcionalidade P/M/G.

## 2. Veredito executivo

**GO condicional para implementar Research Lane em fatias R0 -> R1 -> R2.**

**NO-GO absoluto para qualquer operação, paper/live, envio de ordem, alteração de Risk Engine ou promoção automática de célula.**

A tese é forte como **programa de descoberta**: ela reconhece os principais inimigos estatísticos, exige expectância líquida, trata Epps/assincronicidade, impõe controles de causa comum, prevê DSR/FDR/SPA, separa research de live e coloca o Quant Lab como interface de honestidade. Isso é bom.

O risco central é outro: a tese é sofisticada o bastante para seduzir antes de provar. Heatmap bonito, célula ranqueada, curva de decaimento positiva e linguagem de "sinal" podem virar autorização psicológica informal. O CaM precisa tratar o Cubo como **máquina de falsificação**, não como máquina de confirmação.

## 3. Leitura dos 3 itens

### 3.1 EDGE-THESIS-LEADLAG-CUBE.md — tese original

**Força:** a tese original acerta ao formular um objeto claro: fonte, alvo e lag produzem uma métrica de edge. Também acerta ao separar sinal de instrumento, exigir latência maior que o edge, prever Hayashi-Yoshida contra Epps, controles de causa comum e expectância líquida em vez de taxa de acerto.

**Fragilidade:** a versão original ainda mistura descoberta e linguagem operacional com mais facilidade. Termos como instrumento, sizing, operável e camada de execução são tecnicamente úteis, mas precisam ficar encapsulados como hipótese futura, nunca como convite de implementação operacional.

**Uso recomendado:** preservar como memória da tese v0.1. A fonte vigente para implementação deve ser o documento unificado, porque ele amplia o rigor estatístico e delimita melhor a Research Lane.

### 3.2 CaM-RESEARCH-CUBO-LEADLAG.md — tese unificada + scope backend

**Força:** é o artefato mais importante para backend/research. A evolução é clara: uma tese, duas lentes. A lente rápida busca propagação de fluxo em event time; a lente lenta funciona como porteiro de regime em bar time. A camada estatística é honesta: múltiplos testes, DSR, FDR, SPA, walk-forward, purged CV, regime, capacidade e impacto.

**Fragilidade:** o documento ainda depende de premissas duras de dados: tick com agressor confiável, timestamp em ms, clock sync entre símbolos, histórico suficiente por regime, custo/slippage realistas e latência medida no ambiente CaM. Sem isso, o Cubo vira uma máquina elegante de medir ruído.

**Ponto crítico:** R0 deve ser um gate de dados antes de qualquer entusiasmo estatístico. Se o dado não for research-grade, não há Cubo.

### 3.3 CaM-SCOPE-FRONTEND-CUBO.md — Quant Lab

**Força:** o scope frontend tem a postura certa: Quant Lab separado do Cockpit Live, badge `RESEARCH`, read-only, consumo de agregados, pré-registro, contador de tentativas, DSR em destaque e checklist Go/No-Go. Isso transforma UX em defesa contra autoengano.

**Fragilidade:** a própria UI pode criar maturidade falsa. Um Explorer com slider, ranking lateral e heatmap divergente pode dar sensação de domínio antes da evidência. A interface deve evitar vocabulário e affordances de operação: nada de compra, venda, entrada, setup liberado, sinal ativo ou botão que pareça acionar trade.

**Ponto crítico:** Data Health e Run Registry devem nascer antes do espetáculo visual do heatmap. Primeiro confiança no dado e no denominador estatístico; depois exploração visual.

## 4. Parecer das personas

### Jim — Quant & Edge

Parecer: a tese é boa como research, não como estratégia. O avanço correto é R0/R1/R2 com Evidence Pack crescente. O maior risco é múltiplos testes: fonte x alvo x lag x regime x timeframe x thresholds x variantes. Sem ledger global de tentativas, DSR e SPA viram decoração.

Exigências de Jim:

- Pré-registro real da hipótese e dos parâmetros.
- Snapshot de dados com provenance e hash.
- OOS, walk-forward e purged CV quando houver labels sobrepostos.
- Custo, IR, slippage e latência na expectância.
- Relatório por célula com motivo explícito de kill.
- R4 só passa se a composição regime lento x gatilho rápido superar as partes isoladas fora da amostra.

### Nassim — Market Risk & Ruin

Parecer: o Cubo pode concentrar perdas em rajadas. Sinais curtos falham em clusters quando há notícia, abertura, fechamento, latência, fila, feed ruim ou mudança de microestrutura. Média positiva não basta se a cauda encosta nos limites constitucionais.

Exigências de Nassim:

- Modelar loss streak, slippage extremo, atraso de execução e evento sem liquidez.
- Medir correlação de P&L entre células; células parecidas contam como um único risco.
- Capacidade deve ser liquidez no instante do evento, não volume diário genérico.
- Kelly fracionário pode ser métrica de research, não autorização de tamanho.
- No-Go se o pior cenário plausível ameaça Art. 16 ou exige velocidade que o CaM não tem.

### Ada — Data & Intelligence

Parecer: antes do Cube Engine, precisa existir contrato R0 de dados. Agressor, clock sync e provenance são a fundação da tese. Se esses campos forem fracos, tudo acima deles é falso conforto.

Exigências de Ada:

- Parquet como canônico bruto de research; DuckDB/Polars para processamento.
- Postgres `research_*` apenas para metadados, runs, quality checks e resultados agregados.
- `research_data_sources`, `research_dataset_snapshots`, `research_data_quality_checks`, `research_runs`, `research_run_artifacts`, `research_cell_results` como base futura de SPEC.
- Cada lote com fonte, símbolo, pregão, timezone, timestamp de origem, timestamp de ingestão, hash bruto, hash normalizado, parser version, calendário e quality flags.
- Flag explícita de `aggressor_source`: exchange, broker, lee_ready ou unknown.
- Run imutável: rerun cria nova run vinculada, nunca edita a antiga.

### Don — UX como Defesa de Capital

Parecer: o Quant Lab precisa parecer laboratório, não cockpit operacional. A UI deve reduzir autoengano, não apenas mostrar gráficos bonitos.

Exigências de Don:

- Badge `RESEARCH` permanente em todas as subrotas e exportações.
- Separação visual clara do Cockpit Live.
- Expectância líquida como manchete; taxa de acerto e retorno bruto como secundários.
- Checklist Go/No-Go visível no centro da Cell Detail.
- Contador de tentativas por rodada e global junto do DSR.
- Linguagem de pesquisa: hipótese, célula, evidência, sobrevivente estatística, candidata. Evitar sinal, entrada, compra, venda, setup liberado.
- Sem atalhos para paper/live dentro do Lab.

### Kevin — Segurança + Guardião Constitucional

Parecer: Conditional Go apenas se a separação research/live virar barreira técnica, não só texto. Esta frente aciona SEC-GOV por dados sensíveis, dependências novas, integração com dados de corretora e fronteira futura com Risk Engine/journal/IA.

Exigências de Kevin:

- Usuário/serviço de research sem permissão de escrita em `cam_orders`, `cam_positions`, `cam_journal_entries` e equivalentes.
- Namespace `/research` só muta estado de research. `DELETE` deve ser cancel/archive/soft-delete, nunca apagar evidência.
- Módulos de research não importam Order Gateway, bridge MT5, `send_order`, `OrderSend` ou serviços de execução.
- `POST /research/runs` cria job de pesquisa, não ordem, não candidato operacional.
- Secrets de corretora nunca em Parquet, logs, metadata de run, notebooks ou commit.
- Libs quant e frontend novas exigem ADR leve, lockfile e dependency scan.

### Voltaire — Devil's Advocate

Parecer: a tese está bem protegida no discurso; exatamente por isso pode enganar. Sofisticação estatística não compensa dado ruim, amostra curta ou hipótese pós-hoc. O Cubo pode virar uma fábrica de falso positivo com visual elegante.

Pergunta de Voltaire: se o achado mais valioso do Cubo for provar que o Cubo não deve operar, Carlos aceitará isso como vitória?

## 5. Riscos principais

### 5.1 Risco de dados

O Cubo depende de tick com agressor, timestamp confiável, calendário correto, clock sync e histórico suficiente. Sem provenance completa e quality gates, qualquer lead-lag pode ser latência de feed, falha de sincronização ou diferença de liquidez.

No-Go se:

- A corretora não exportar agressor confiável e o fallback Lee-Ready não for auditável.
- Clock sync não for mensurável por símbolo/dia.
- Gaps, duplicatas, out-of-session e alterações de contrato não forem rastreados.
- Runs dependerem de tabela mutável sem snapshot/hash.

### 5.2 Risco estatístico

O maior inimigo é data snooping. O denominador real inclui célula, parâmetro, universo, timeframe, threshold, regime, rerun, versão de feature e variação de custo. Se isso não conta no trial ledger, a deflação do Sharpe fica otimista.

No-Go se:

- DSR/FDR/SPA não usarem contador honesto de tentativas.
- Labels de forward return vazarem informação futura.
- Fib, swing, S/R ou regime forem definidos depois de ver resultado.
- A composição R4 for aceita sem comparar contra as partes isoladas.

### 5.3 Risco de causa comum

F e D podem parecer ligados quando ambos reagem a WDO, WIN/índice, ES, notícia, leilão, abertura, fechamento ou setor. Granger e transfer entropy não salvam uma tese se os controles de causa comum forem fracos.

No-Go se:

- A célula desaparece ao controlar WDO/ES/macro/setor.
- O efeito só aparece em uma janela escolhida depois.
- O sinal depende de regime cuja definição foi otimizada retrospectivamente.

### 5.4 Risco de executabilidade

O Cubo Rápido opera perto do limite onde latência, fila, spread, slippage e plataforma importam mais que a regressão. Edge que vive menos que a latência real do CaM é fora de escopo.

No-Go se:

- `mu_h` só é positivo antes da latência real medida.
- O edge exige co-location, sub-segundo ou reação que o CaM não consegue reproduzir.
- Slippage conservador consome a expectância.
- Capacidade no instante do evento é insuficiente.

### 5.5 Risco de UX/psicologia operacional

O Quant Lab pode se tornar uma máquina de convicção se a UI transformar pesquisa em espetáculo. A Constituição protege contra isso: IA pode pesquisar, auditar e sugerir hipóteses; não pode virar autoridade final de execução.

No-Go se:

- A UI usar linguagem operacional prematura.
- Heatmap/ranking aparecer sem Data Health, DSR e contador de tentativas.
- Houver qualquer affordance parecida com trade.
- O usuário conseguir esconder testes mortos ou editar resultados.

## 6. Gates recomendados por fase de research

### R0 — Dados

Gate: dataset reprodutível e validado.

Critérios mínimos:

- Provenance completa por lote.
- Aggressor source explícito.
- Clock sync e cobertura por símbolo/dia.
- Dedupe, gaps e out-of-session auditados.
- Snapshot com hash e calendário versionado.
- Data Health exposto no Quant Lab.

Sem R0 aprovado, não construir ranking de edge.

### R1 — Features

Gate: biblioteca determinística, pura e testável.

Critérios mínimos:

- OFI, z-score, barras, ZigZag/fractal, S/R, ATR/RV e fib sem look-ahead.
- Feature cache por snapshot.
- Versionamento de feature definitions.
- Testes contra fixtures pequenas e casos de borda.

Sem R1 aprovado, qualquer célula é estatística sobre feature instável.

### R2 — Cubo Rápido

Gate: pelo menos uma célula sobrevive a falsificação forte, ou a hipótese rápida é morta.

Critérios mínimos:

- OOS + walk-forward.
- FDR/DSR/SPA com trial accounting.
- HY/HRY contra Epps.
- Event study líquido com custos, IR, slippage e latência.
- Controles de causa comum.
- Capacidade e decaimento compatíveis com execução não-HFT.

### R3 — Cubo Lento

Gate: baseline estrutural prova valor; Fibonacci só fica se acrescentar OOS.

Critérios mínimos:

- Baseline sem fib aprovado antes.
- Purged CV com embargo quando labels se sobrepõem.
- Regime definido sem hindsight.
- Fib tratado como réu: se não provar incremento, cai.

### R4 — Síntese

Gate: regime lento x gatilho rápido supera as partes isoladas.

Critérios mínimos:

- Comparação OOS contra lente rápida isolada e lente lenta isolada.
- Trial accounting inclui a própria busca da composição.
- Risco agregado e correlação de P&L entre células medidos.
- Evidence Pack antes de qualquer conversa de paper.

## 7. Sequência de implementação recomendada

1. **SPEC R0 — Market Data Research Snapshot.** Definir contratos de dado, provenance, snapshots, hashes, quality checks, clock sync e Data Health.
2. **UI-R0 mínima.** Data Health + Run Registry básico + badge `RESEARCH`. Sem heatmap ainda.
3. **R1 — Feature Library determinística.** Features puras, versionadas e testadas.
4. **Run Launcher com pré-registro imutável.** Modelo de custo, universo, lag grid, thresholds, validação e controles definidos antes de rodar.
5. **R2 MVP — Cubo Rápido top-N.** Primeiro mata Epps/latência/causa comum nas candidatas; evitar varrer tudo com visual completo antes de ter trial ledger.
6. **Cell Detail como dossiê de evidência.** Decaimento, event study, HY vs ingênua, DSR/FDR/SPA, Data Health, capacidade e checklist Go/No-Go.
7. **R3/R4 só depois.** Lente lenta, fib e síntese entram após R0-R2 estarem confiáveis.

## 8. Decisões abertas para o Founder

1. Universo inicial: quantos ativos e quais símbolos entram em R0/R2.
2. Profundidade histórica mínima por lente e por regime.
3. Grade inicial de lag/defasagem e limites de busca.
4. Thresholds iniciais: evento, toque fib, swing, filtros de liquidez e n mínimo.
5. Fonte primária de tick com agressor e regra de fallback.
6. Persistência: mesmo Postgres com namespace `research_*` e permissões duras, ou store separado.
7. Granularidade do contador de tentativas: recomendação Leo/Jim/Ada = por célula, parâmetro, run e acumulado global.
8. Lib de heatmap: `plotly` pela velocidade de research ou `visx` pelo controle fino; exige ADR leve.

## 9. Perguntas duras antes do letscode

1. Se a corretora não entregar tick com agressor, timestamp confiável e histórico suficiente, a tese morre ou será adaptada até parecer viva?
2. O primeiro gate será estatístico ou será corretamente um gate de dados?
3. Quantas tentativas contam no denominador do DSR: célula, parâmetro, universo, timeframe, rerun, limiar e versão de código?
4. O Cubo procura uma anomalia econômica ou só maximiza uma busca combinatória até achar decoração estatística?
5. A composição regime x trigger será aceita apenas se superar as partes isoladas OOS?
6. Fibonacci começa como hipótese culpada até prova contrária?
7. Qual resultado faria Carlos matar a tese sem negociação?
8. Se a melhor célula exigir execução mais rápida que o CaM consegue operar sem virar HFT, ela será descartada?
9. A UI do Quant Lab impede autoengano ou apenas torna o autoengano mais bonito?
10. Se o Cubo provar que o Cubo não deve operar, isso será tratado como vitória?

## 10. Conclusão

O Cubo merece implementação como **Research Lane**, começando por dados e reprodutibilidade. Não merece ainda status de estratégia, nem paper, nem live.

A tese correta para o CaM agora não é "encontrar edge". É construir uma máquina que consiga dizer, com honestidade auditável: **esta hipótese morreu**, **esta hipótese ainda não tem dado suficiente**, ou **esta célula sobreviveu o bastante para virar EDGE-THESIS específica e passar ao pipeline formal**.

Até lá: research-only, Risk Engine intocado, Founder gate pendente, sem execução.

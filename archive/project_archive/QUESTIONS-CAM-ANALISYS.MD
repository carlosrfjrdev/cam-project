---
template: QUESTIONS
phase: DISC
status: Draft
version: 1
date: 2026-05-25
companion_of: CAM-ANALISYS.MD
purpose: Perguntas para Carlos refinar os 11 desejos antes de virarem SPEC
---

# QUESTIONS-CAM-ANALYSIS — Perguntas para refinar os 11 desejos

> **Origem:** companion de [`CAM-ANALISYS.MD`](./CAM-ANALISYS.MD)
> **Princípio:** cada pergunta tem **3-4 opções concretas** + espaço para "outro". Carlos marca uma e adiciona contexto se quiser.
>
> Sem respostas, várias destas perguntas viram bloqueadores para PLAN futuro. Marty levanta; Founder decide.

---

## Para Q1 — Algorithmic Trader

### Q1.A — O que você quer dizer com "Algorithmic Trader"?

```
[ ] (A) Robô totalmente autônomo: lê tick, decide, envia ordem, gerencia stop — sem mim no loop
[ ] (B) Sistema semi-autônomo: robô propõe entrada/saída, eu confirmo no app antes de virar ordem
[ ] (C) Sistema de sinais: robô avisa quando estratégia dispara, eu executo manualmente
[ ] (D) Misto: durante backtest/paper, totalmente autônomo; em real, semi-autônomo
[X] Outro: é amplo desde robo totalmente autonomo, semi autonomo e sinais
```

### Q1.B — Em que fase você quer começar a operar algoritmicamente?

```
[ ] (A) Paper trading apenas — quero validar a infra
[ ] (B) Conta DEMO MT5 com EA real, sem dinheiro real
[ ] (C) Conta real Fase 2 (1 contrato, R$ 1.500 efetivo) imediatamente após paper
[ ] (D) Conta real Fase 3+ (1-2 contratos, R$ 3.000) — só com 90 dias de track real
[x] Outro: na v1.0 do CAM ja quero a possibilidade em conta real e demo
```

### Q1.C — Quanto controle manual você quer manter?

```
[ ] (A) Zero — robô faz tudo, eu só olho
[ ] (B) Botão "pause robô" sempre visível, mas robô executa
[ ] (C) Cada ordem do robô precisa minha confirmação (1-click)
[ ] (D) Robô só sugere via Telegram, eu executo no MT5
[x] Outro: Bom... precisaremos ter um certo nível de controle... então posso definir 1 clique, pause ou full automatico
```

---

## Para Q2 — Ciclo de vida do EA

### Q2.A — Quando você diz "Iniciar/Pausar/Recomeçar", quer controlar o quê?

```
[ ] (A) O processo do MT5 inteiro (subir/derrubar Wine + MT5)
[ ] (B) O EA dentro do MT5 (atachar/desatachar do gráfico)
[ ] (C) Apenas a publicação de dados via ZeroMQ (PAUSE/RESUME publicação)
[ ] (D) Apenas a execução de ordens (publicação continua, execução pausa)
[X] Outro: Pensei neste cenario em ter o controle total dos EA diretamente no CAM como sendo uma extensão do metatrader mesmo
```

### Q2.B — Você quer múltiplos EAs simultâneos?

```
[ ] (A) 1 EA, 1 gráfico (WIN OU WDO) — simples
[ ] (B) 2 EAs (1 em WIN + 1 em WDO) simultâneos, com Risk Engine validando soma
[ ] (C) N EAs (vários gráficos), cada um uma estratégia diferente
[ ] (D) Deixar isso para SPEC futura
[x] Outro: provavelmente chegaremos a este nível pois eu quero EA analisando Mercado, Analisando book e Operando efetivamente
```

---

## Para Q3 — Cotação real-time

### Q3.A — Qual nível de cotação você precisa?

```
[ ] (A) Apenas último preço (tick top of book) — suficiente para gauges/dashboard
[ ] (B) Tick completo (cada negócio com volume) — para tape reading
[ ] (C) Book level 2 (5-10 níveis de profundidade) — para book reading e identificação de player
[ ] (D) Todos os 3 níveis
[X] Outro: Tudo, a ideia é trazer histórico para base com todos os 3 niveis mais profundos pois pretendo entender padrões com técnica de big data... e aplicar e encontrar estratégicas e insights estratégicos com IA em uma grande massa organica.
```

### Q3.B — Para quais ativos você precisa de real-time?

```
[ ] (A) Apenas WIN e WDO (derivativos) — já temos via cam_bridge.mq5
[ ] (B) WIN/WDO + 5-10 ações grandes (PETR4, VALE3, ITUB4, BBDC4, etc.)
[ ] (C) WIN/WDO + FIIs principais (HGLG11, KNRI11, etc.)
[ ] (D) Universo amplo (200+ ativos) — para screening
[X] Outro: Universo amplo e podemos estender para outros ativos alem de derivativos, ações e FIIs
```

### Q3.C — Quanto você aceita gastar por mês em feed real-time?

```
[ ] (A) R$ 0 — apenas o que vier do MT5 da corretora (gratuito incluído)
[ ] (B) R$ 0-50/mês — feed básico (Yahoo Finance, scraping)
[ ] (C) R$ 50-200/mês — feed semi-profissional (UP2DATA basic)
[ ] (D) R$ 200+/mês — feed institucional (UP2DATA full, B3 vendor)
[X] Outro: Vamos começar com dados de corretoras e feed basico mas a meta é só apos 1 mes no verde com mais de 90% de acerto partiremos para investimentos
```

---

## Para Q5 — Montar estratégias

### Q5.A — Como você quer escrever estratégias?

```
[ ] (A) Em Python — eu codo a função `evaluate(tick, context) -> Order | None`
[ ] (B) Em MQL5 — eu codo direto no EA (mas perde o Risk Engine Python)
[ ] (C) Em DSL declarativa — JSON/YAML com regras: "se RSI < 30 e ADX > 25, comprar"
[ ] (D) Visual builder (no-code drag-and-drop)
[X] Outro: Python e MQL5 e DSL podemos ir por ABC (depois de maduro pensaremos em D)
```

> **Nota Voltaire:** opção (D) é desencorajada — vira "fábrica de estratégias ruins sem disciplina". Opção (A) preserva governança Python + Risk Engine.

### Q5.B — Quantas estratégias você quer ter ativas em paralelo?

```
[ ] (A) 1 — uma estratégia por vez, validada e operando
[ ] (B) 2-3 — diversificação modesta
[X] (C) N — múltiplas (exige decisão constitucional sobre divisão de capital)
[ ] (D) Deixar como decisão futura
[ ] Outro: 
```

---

## Para Q6 — Carteira Hard

### Q6.A — Como você quer registrar aquisições da Carteira Hard?

```
[ ] (A) Manual via UI: form com ticker, qtde, preço, data → entra no inventário
[ ] (B) Importação CSV da corretora (similar ao Profit CSV — mas para extrato de ações)
[ ] (C) Sync automatizado com home broker da corretora (exige API da corretora)
[ ] (D) Apenas saldo R$ alocado — não preciso de inventário ticker-a-ticker
[X] Outro: Manual via UI + importação da corretora para conciliação
```

### Q6.B — Que controles você quer sobre a Carteira Hard?

```
[ ] (A) Apenas registro (CRUD básico)
[ ] (B) Registro + valorização a mercado (exige Q3 resolvido)
[ ] (C) Registro + valorização + alertas (concentração > 30%, perda > 20%, etc.)
[X] (D) Registro + valorização + rebalanceamento sugerido
[ ] Outro: 
```

### Q6.C — Quais critérios "longo prazo" (Art. 23) você quer enforcar?

```
[ ] (A) Nenhum — qualquer ação/FII vale
[ ] (B) Apenas ações com DY > 5% e FIIs com DY > 8%
[ ] (C) Critérios fundamentalistas (P/L < 15, ROE > 15%, etc.)
[ ] (D) Lista branca de tickers permitidos (você define a lista)
[X] Outro: Criterios fundamentais mas DY ganha
```

---

## Para Q7 — Dividendos/JCP

### Q7.A — De onde virão os dados de proventos?

```
[ ] (A) Status Invest (scraping gratuito)
[ ] (B) Fundamentus (scraping gratuito)
[ ] (C) API paga (StatusInvest API, IComS&P, etc. — R$ 30-100/mês)
[ ] (D) Upload manual (CSV ou input via UI)
[x] Outro: Scraping multiplo
```

### Q7.B — Que visões você quer sobre dividendos?

```
[ ] (A) Calendário "próximos 30 dias"
[x] (B) Histórico recebido + projeção próximos 12 meses
[ ] (C) Comparação com benchmark (CDI, Selic)
[ ] (D) Reinvestimento automatizado em mais cotas (Carteira Hard cresce sozinha)
[ ] Outro: 
```

---

## Para Q8 — Indicadores fundamentalistas

### Q8.A — Por que você quer indicadores no CaM em vez de usar Status Invest separado?

> Recomendação Voltaire+Sun: **não fazer interno**, manter foco em derivativos + governança.

```
[ ] (A) Concentração de informação no cockpit (UX) — vale a pena mesmo sem ser core
[ ] (B) Quero integrar indicadores com sinais (ex: só comprar ação se P/L < 15)
[ ] (C) Já uso Status Invest, vou continuar — perg foi exploratória
[X] (D) Quero substituir uso de outras ferramentas — quero "tudo no CaM"
[X] Outro: Não me dou bem com multiplas ferramentas, pretendo fazer analise cruzada de informações, quando eu operava via padrões em graficos considerando 5/10 ações para operar derivativo, e se o CAM encontrar estes padrões pra mim ?
```

### Q8.B — Se decidir construir, qual escopo?

```
[ ] (A) Apenas P/L + DY + P/VP (3 indicadores)
[ ] (B) Painel completo (10-15 indicadores)
[ ] (C) Comparador peer-to-peer (Itaú vs Bradesco vs Santander)
[ ] (D) Decidir depois — primeiro Q8.A
[x] Outro: Vamos eleger indicadores fundamentalistas de mais peso para decisão pelo menos 7
```

---

## Para Q9 — Long & Short

### Q9.A — Qual L&S você quer estudar?

```
[ ] (A) Direção isolada (operar Long OU Short em WIN/WDO) — já suportado
[ ] (B) Pair trade clássico WIN × WDO (Long WIN + Short WDO simultâneo)
[ ] (C) Pair trade ações (ex: Long ITUB4 + Short BBDC4)
[ ] (D) Long & Short com hedge (Long ação à vista + Short futuro WIN)
[X] Outro: Trade de ações e classico. (headge se tiver maturidade)
```

### Q9.B — Pré-requisitos confortáveis

```
[x] Pair trade WIN×WDO exige Fase 3+ (Art. 12 simultâneo vedado em F1/F2) — aceita?
[ ] Pair trade ações exige Q3 (cotação real-time) e Q6 (inventário Carteira Hard) — aceita esperar?
[ ] L&S com hedge exige posição em Carteira Hard interagir com Risk Engine — escopo grande

Não aceito esperar... vamos construir o que for necessário..

```

---

## Para Q10 — Robôs de estratégia

### Q10.A — Modelo conceitual de "robô"

```
[ ] (A) 1 robô = 1 estratégia + 1 EA + 1 conta — simples e isolado
[ ] (B) 1 robô = 1 estratégia, mas pode rodar em vários ativos
[x] (C) 1 robô = orquestrador de várias estratégias com regras de priorização
[ ] (D) Outro: 
```

### Q10.B — Quantos robôs simultâneos?

```
[ ] (A) 1 — começar simples
[ ] (B) 2-3 — diversificação (ex: ORB, mean reversion, breakout)
[X] (C) N — exige decisão de divisão de capital + emenda constitucional
[ ] (D) Decisão futura
[X] Outro: Começar com um mas ser escalavel
```

### Q10.C — Onde rodam os robôs?

```
[X] (A) Backend Python + EA MT5 — robô em Python decide, EA executa via bridge
[ ] (B) EA MQL5 puro — robô codado em MQL5, perde Risk Engine Python (NÃO recomendado)
[ ] (C) Misto — alguns robôs em Python (passa pelo Risk Engine), outros em MQL5 puro com risk_mirror
[ ] Outro: 
```

---

## Para Q11 — IA padrões / tape / book

### Q11.A — Qual a prioridade entre os 3?

```
[ ] (A) Correlação cross-asset (à vista afeta derivativo)
[ ] (B) Tape reading (fluxo de tick — agressor comprador vs vendedor)
[ ] (C) Book reading (level 2 — desequilíbrio de liquidez)
[X] (D) Todos juntos
[ ] Outro: ________________________________________
```

### Q11.B — IA local ou remota?

```
[ ] (A) Apenas Ollama local (privacidade total, sem custo, performance limitada)
[ ] (B) Apenas Anthropic API (qualidade máxima, custo R$ 0-50/mês, dados anonimizados)
[ ] (C) Misto: local para dados sensíveis (journal, posições), remoto para análise quant geral
[ ] (D) Não-LLM: ML quant (sklearn/torch) sem prompt
[X] Outro: Vamos começar local, mas testarei Anthropic e OpenIA
```

### Q11.C — Output da análise

```
[ ] (A) Relatório em texto via Telegram (já temos infra)
[ ] (B) Estruturado (JSON com padrões, scores, evidências) — UI consome
[ ] (C) Sugestão de regra para nova estratégia (Carlos valida → SPEC → backtest)
[ ] (D) Visualização (heatmap correlação, gráfico padrões)
[X] Outro: Todos os itens
```

---

## Cross-cutting — Decisões transversais

### CC.1 — Posicionamento do CaM no mercado

```
[ ] (A) Ferramenta pessoal — sem ambição comercial, só protege Carlos
[ ] (B) Eventual produto Teczilabs (SaaS para outros operadores)
[ ] (C) Open source (modelo Teczi DevFlow embarcado)
[X] (D) Decisão futura
[X] Outro: Estou construindo pra mim, não é preocupação agora mas pode virar
```

> Resposta afeta: stack escolhida (Linux+MT5 favorece A,C; multi-broker favorece B), licensing, escopo de testes.

### CC.2 — Horizonte temporal de evolução

```
[ ] (A) Foco em Fase 1 (paper) até estabilizar — SPECs v0.4-v0.5 apenas
[ ] (B) Acelerar para Fase 2 (real) — SPECs em paralelo
[ ] (C) Pesquisa quant paralela (Q11 ML) mesmo antes de Fase 1
[ ] (D) Decisão por trimestre — não compromete ano inteiro
[X] Outro: Vocês estão se preocupando muito com prazo vamos acelerar tudo, minha meta é 15 dias a primeira operação, visto que consigo gerar e validar de 1 a 2 specs por dia.
```

### CC.3 — Prioridade de SPECs v0.4-v0.7 (escolher ORDEM)

> Ordene de 1 (primeiro) a 4 (último).

```
[ ___ ] v0.4 — Bridge read-write + S1 + DEMO live (Q1, Q2, Q5, Q10)
[ ___ ] v0.5 — Carteira Hard inventário + data_collector real (Q6, Q11 parcial)
[ ___ ] v0.6 — Dividendos + cotação ações externa (Q3 ext, Q7)
[ ___ ] v0.7 — Tape/book reading + ML quant (Q11 extensão)

FAZER TUDO JUNTO

```

---

## Para Carlos preencher e devolver

> Marque suas escolhas + adicione contexto livre nos espaços "Outro". Não precisa responder tudo de uma vez — priorize Q1, Q5, Q10 (operacionais críticos).

**Data de entrega:** ___/___/______

**Assinatura:** ______________________________

(BUROCRACIA DESNECESSÁRIA TIRA ISSO DE DATA E ASSINAR)

---

## Como Marty vai usar suas respostas

1. Cada bloco respondido vira **input de SPEC v0.4+** correspondente.
2. Respostas que contradizem Constituição (Art. 11, 15, 18, 25, 35, 36) ganham nota de Voltaire alertando antes de virar SPEC.
3. Respostas que exigem custo recorrente (Q3.C, Q7.A) acionam Mammon para reanálise de edge mínimo em CORRETORA-EVAL.
4. Respostas (CC.3) que ordenam SPECs viram backlog priorizado.

---

> **Princípio operacional deste documento:**
>
> Marty pergunta. Carlos decide. As respostas viram SPEC. SPEC vira PLAN. PLAN vira CODE.
>
> Não há substituto para o Founder responder. Nenhuma análise multi-persona substitui o "Carlos quer X" registrado.

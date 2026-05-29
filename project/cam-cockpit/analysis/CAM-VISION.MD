---
template: VISION
phase: DISC
status: Draft
version: 1
date: 2026-05-25
purpose: Bússola de visão para transformar CAM-ANALISYS e QUESTIONS em direção de produto, features candidatas e filtros anti-feature-factory
source:
  - CAM-ANALISYS.MD
  - QUESTIONS-CAM-ANALISYS.MD
sec_gov: Conditional Go para documento de visão; No-Go para qualquer promessa de execução real sem gates constitucionais
---

# CAM-VISION - Direção Evolutiva do CaM Cockpit

> **Origem:** análise da direção de [`CAM-ANALISYS.MD`](./CAM-ANALISYS.MD) e [`QUESTIONS-CAM-ANALISYS.MD`](./QUESTIONS-CAM-ANALISYS.MD)
> **Função deste documento:** visão e filtro de decisão. Não é SPEC, não é PLAN, não aprova CODE e não autoriza operação.
> **Regra-mãe:** Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual.

---

## 1. Frase de visão

**O CaM é um cockpit constitucional local que transforma tese operacional em execução governada, auditável e patrimonializada.**

Isso significa:

- antes de operar melhor, o CaM precisa **provar melhor**;
- antes de automatizar, o CaM precisa **governar**;
- antes de escalar, o CaM precisa **registrar e preservar capital**;
- antes de buscar mais dados, o CaM precisa saber **qual decisão cada dado melhora**;
- antes de virar robô, cada estratégia precisa passar pelo ciclo constitucional de evidência.

O CaM não deve ser definido como plataforma de trading algorítmico. Ele pode conter automação algorítmica, mas sua identidade é outra: **um sistema pessoal de disciplina, risco, evidência, registro e conversão de lucro tático em patrimônio**.

---

## 2. Leitura da direção do CAM-analysis

O CAM-analysis revela uma direção boa, mas perigosa se for lida como lista de desejos. As perguntas não estão pedindo apenas telas novas. Elas estão tentando descobrir se o CaM consegue sustentar um ciclo completo:

```text
Tese -> Dados -> Backtest -> Walk-forward -> Paper/Demo -> Risk Engine -> Execução governada -> Journal -> Fiscal -> Harvest -> Carteira Hard
```

A visão saudável é organizar tudo nesse ciclo. A visão perigosa é tentar construir, ao mesmo tempo, robôs, tape reading, book, dividendos, indicadores fundamentalistas, feed externo, IA quant, múltiplos EAs e long & short.

### O que cada grupo de perguntas está realmente perguntando

| Perguntas | Desejo real por baixo | Risco de leitura ruim | Direção recomendada |
|---|---|---|---|
| Q1, Q2, Q5, Q10 | Automatizar estratégia sem perder controle | Virar robô livre cedo demais | Strategy Lifecycle governado |
| Q3, Q11 | Ter dados e inteligência sobre mercado | Comprar/coletar dado antes de saber uso | Evidence Layer primeiro |
| Q4, Q9 | Estudar estratégias com rigor | Confundir estudo com autorização de operar | Research e backtest auditáveis |
| Q6, Q7 | Fechar o ciclo patrimonial da Harvest Rule | Transformar CaM em gestor amplo de carteira | Carteira Hard auditável, simples |
| Q8 | Concentrar análise fundamentalista | Virar mini Status Invest | Out por padrão, Later se houver razão forte |
| CC.1, CC.2, CC.3 | Definir identidade e sequência | Decidir feature sem decidir postura | Subir para o topo do questionário |

---

## 3. Diagnóstico das perguntas atuais

### 3.1 Perguntas fortes

As perguntas estão fortes quando obrigam Carlos a escolher **modo operacional**, **fase**, **custo**, **nível de dado** e **grau de autonomia**. Esse é o tipo certo de pergunta, porque evita que a IA ou o sistema decidam sozinhos o que é risco aceitável.

Blocos especialmente úteis:

| Bloco | Por que é bom |
|---|---|
| Q1 Algorithmic Trader | Expõe a diferença entre robô autônomo, semi-autônomo e sistema de sinais |
| Q2 Ciclo de vida do EA | Separa controle técnico do EA de controle de execução |
| Q3 Cotação real-time | Obriga a escolher granularidade: último preço, tick, book |
| Q5 Montar estratégias | Força decisão entre Python, MQL5, DSL ou no-code |
| Q6 Carteira Hard | Traz a Carteira Hard do abstrato para inventário real |
| Q11 IA padrões/tape/book | Diferencia IA textual, análise de dados e ML quant |
| CC.3 Prioridade de SPECs | Transforma vontade em sequência |

### 3.2 Perguntas sobrepostas

Q1, Q5 e Q10 estão orbitando o mesmo núcleo: **qual é o modelo de estratégia/robô permitido no CaM?**

Hoje elas perguntam separadamente:

- O que é algorithmic trader?
- Como montar estratégia?
- O que é robô de estratégia?

A pergunta-mãe deveria ser:

> **Qual ciclo uma estratégia pode percorrer no CaM: apenas backtest, paper/demo, sinal com confirmação manual, execução automática governada ou real autorizado?**

A partir dela, as subperguntas ficam mais simples:

- onde a estratégia roda: Python, MQL5 mirror, ou ambos;
- quem confirma ordem: sistema, Carlos ou ninguém porque é apenas paper;
- em qual ambiente: backtest, paper, demo, real;
- qual status auditável a estratégia tem no registry.

### 3.3 Perguntas faltantes

O companion não tem uma seção própria para Q4 Backtest, embora Q4 seja uma das peças mais importantes. Antes de discutir read-write MT5, o CaM precisa responder:

```text
Qual é a primeira estratégia candidata?
Qual fonte de tick histórico será usada?
Quais custos reais entram no backtest?
Qual métrica descarta a estratégia sem negociação emocional?
Como comparar backtest, walk-forward e paper?
```

Também falta uma pergunta explícita sobre **Strategy Registry**:

```text
Uma estratégia pode existir no CaM sem status auditável?
[ ] Não. Toda estratégia precisa estar registrada.
[ ] Sim, para estudos livres fora do cockpit.
[ ] Apenas notebooks/research podem existir sem registry.
```

Recomendação: no CaM operacional, toda estratégia que possa virar sinal ou ordem deve passar pelo registry.

---

## 4. Questionário v2 recomendado

A versão atual do questionário é boa como brainstorming. A versão seguinte deveria ser mais curta e mais decisiva.

### Bloco A - Decisões-mãe

Estas perguntas devem vir antes das features:

```text
A1. O CaM continua sendo ferramenta pessoal, local e não comercial?
[ ] Sim, sem ambição comercial
[ ] Talvez produto futuro, mas não agora
[ ] Quero desenhar desde já como produto
```

```text
A2. Qual foco do próximo ciclo?
[ ] Preparar Fase 1 com evidência e paper
[ ] Acelerar automação demo
[ ] Construir patrimônio/Carteira Hard
[ ] Pesquisa quant/IA
```

```text
A3. Qual prioridade de entrega?
[ ] Strategy Lifecycle primeiro
[ ] Carteira Hard primeiro
[ ] IA/tape/book primeiro
[ ] Automação MT5 read-write primeiro
```

### Bloco B - Modelo de estratégia e robô

Fundir Q1, Q5 e Q10:

```text
B1. Qual modo máximo permitido por ambiente?
Backtest: [ ] autônomo [ ] sinal [ ] manual
Paper:   [ ] autônomo [ ] sinal [ ] manual
Demo:    [ ] autônomo [ ] semi-autônomo [ ] manual
Real:    [ ] sinal [ ] confirmação 1-click [ ] automático governado [ ] não autorizado
```

```text
B2. Como estratégias são escritas?
[ ] Python como fonte canônica + MQL5 apenas mirror/execução
[ ] MQL5 puro
[ ] DSL declarativa
[ ] No-code visual
```

Default recomendado: **Python como fonte canônica + MQL5 mirror/execução**. MQL5 puro deve ser não recomendado porque cria risco de bypass do Risk Engine Python.

```text
B3. Quantas estratégias ativas no início?
[ ] 1 estratégia por vez
[ ] 2-3 estratégias, sem simultaneidade operacional
[ ] N estratégias simultâneas
```

Default recomendado: **1 estratégia por vez** até o registry, backtest persistido, paper e journal estarem maduros.

### Bloco C - Dados de mercado

Reformular Q3 para sair de “quero dado?” e ir para “qual decisão esse dado melhora?”

```text
C1. Qual uso justifica o dado real-time?
[ ] Dashboard e P&L
[ ] Backtest/paper com tick confiável
[ ] Tape reading
[ ] Book reading
[ ] Valorização Carteira Hard
```

```text
C2. Qual dado vem primeiro?
[ ] Tick histórico WIN para validar S1
[ ] Tick real-time WIN/WDO via MT5
[ ] Book level 2
[ ] Ações/FIIs
```

Default recomendado: **tick histórico WIN para validar S1**, depois tick real-time WIN/WDO. Book e ações/FIIs ficam depois.

### Bloco D - Carteira Hard

Manter Q6, mas trocar “enforçar critérios” por “qual nível de enforcement?”

```text
D1. Como a Carteira Hard registra ativos?
[ ] Manual via UI
[ ] Importação CSV
[ ] Sync corretora
[ ] Apenas saldo R$
```

Default recomendado: **manual via UI**, depois CSV.

```text
D2. Critérios de longo prazo são:
[ ] Apenas alerta
[ ] Bloqueio hard
[ ] Checklist de justificativa
[ ] Lista branca de tickers
```

Default recomendado: começar com **alerta + justificativa**, não bloqueio hard, até Carlos definir política patrimonial objetiva.

### Bloco E - IA e análise

Separar LLM de ML quant:

```text
E1. O que a IA faz primeiro?
[ ] Resume journal e aderência
[ ] Detecta anomalias operacionais
[ ] Sugere hipóteses de estratégia
[ ] Analisa tape/book
```

Default recomendado: **resume journal e aderência** com dados reais. Tape/book vem depois.

```text
E2. Qual saída da IA é útil?
[ ] Texto Telegram
[ ] JSON estruturado para UI
[ ] Sugestão de SPEC de estratégia
[ ] Visualização
```

Default recomendado: **JSON estruturado + resumo humano**, sempre read-only.

---

## 5. Filtros de decisão para qualquer feature

Uma feature só deve entrar em SPEC se passar por estes filtros.

### 5.1 Filtros positivos

| Filtro | Pergunta |
|---|---|
| Preserva capital? | A feature reduz risco, bloqueia erro ou evita ilusão operacional? |
| Aumenta evidência? | Ela melhora backtest, paper, comparação ou auditoria? |
| Reduz erro humano? | Ela tira decisão emocional do caminho crítico? |
| Respeita o Risk Engine? | Toda ordem ou intenção passa pelo `cam/_shared/risk/`? |
| Registra tudo? | Journal, audit trail, fiscal e eventos ficam rastreáveis? |
| Mostra líquido? | Qualquer resultado operacional aparece líquido de imposto provisionado? |
| Mantém localidade? | Continua coerente com Linux + MT5 + cockpit local? |
| Tem custo justificável? | Se houver mensalidade/feed/API, o benefício compensa o capital de R$ 5.000? |

### 5.2 Filtros negativos

A feature deve ir para Out ou Later se:

- aumenta frequência de operação antes de aumentar controle;
- permite ordem sem Risk Engine;
- depende de IA como autoridade de execução;
- exibe lucro bruto como métrica operacional principal;
- dilui o CaM para competir com Status Invest, plataformas de execução ou produto multiusuário;
- adiciona custo recorrente sem edge mensurável;
- cria múltiplos robôs antes de definir exposição agregada;
- depende de dados externos sem qualidade, contrato ou rastreabilidade;
- faz a Carteira Hard virar margem emocional ou trade disfarçado.

---

## 6. Pilares da visão

### Pilar 1 - Governança Constitucional

O cockpit deve tornar a Constituição operacional, não apenas visível.

Features naturais:

- Risk Console consolidado;
- audit trail append-only;
- bloqueio por DARF, checklist, kill switch e pós-mercado pendente;
- histórico de decisões do Risk Engine;
- status de fase operacional;
- feature flags de execução com fail-closed.

### Pilar 2 - Strategy Lifecycle

Toda estratégia precisa sair do campo da ideia e entrar em um ciclo auditável.

Estados recomendados para o registry:

```text
draft -> backtested -> walk_forward_ok -> paper_ok -> demo_ok -> real_authorized -> retired
```

Regras:

- nenhuma estratégia se autopromove;
- promoção exige evidência registrada;
- Founder decide gates;
- Risk Engine valida qualquer candidato;
- S1 ORB deve ser a primeira candidata se Carlos aprovar a tese.

### Pilar 3 - Evidence Layer

Antes de automação read-write, o CaM precisa dominar dados, backtest e comparação.

Features naturais:

- ingestão confiável de tick histórico;
- persistência de backtest runs;
- comparação de runs;
- P&L real por tick scanning;
- walk-forward multi-split;
- relatórios de evidência por estratégia;
- custos e imposto sempre incluídos.

### Pilar 4 - Operação Assistida MT5

MT5 executa. Python governa. MQL5 espelha e executa apenas quando autorizado.

Camadas:

1. read-only: ticks, posições, fills, heartbeat;
2. controle seguro: pause/resume, status, healthcheck;
3. paper/demo loop: estratégia gera candidato, Risk Engine valida, paper/demo registra;
4. read-write DEMO: EA executa em conta demo com `cam_risk_mirror.mq5`;
5. real autorizado: somente após Art. 28 completo, SPEC própria, SEC-GOV e QA-SEC.

### Pilar 5 - Journal, Fiscal e Harvest

O CaM precisa fechar o ciclo emocional e patrimonial:

```text
operação -> resultado líquido -> DARF/provisão -> harvest -> Carteira Hard -> patrimônio
```

Features naturais:

- journal automático e manual reconciliável;
- ledger fiscal real;
- DARF e compensação visíveis;
- harvest mensal;
- Carteira Hard com holdings;
- dividendos/JCP como extensão depois dos holdings.

### Pilar 6 - IA Auditora

IA no CaM é lente, não volante.

Permitido:

- resumir journal;
- encontrar anomalias;
- sugerir hipóteses;
- explicar comportamento operacional;
- gerar relatório pós-mercado;
- apoiar SPEC de estratégia.

Vedado:

- enviar ordem;
- habilitar robô;
- alterar parâmetro do Risk Engine;
- justificar exceção constitucional;
- decidir aumento de exposição;
- atuar como autoridade final em tempo real.

---

## 7. Features candidatas implementáveis

As features abaixo são sugestões de implementação futura. Cada uma ainda precisa de SPEC, gate Founder e, quando tocar ordem/Risk Engine/journal/IA, lente SEC-GOV proporcional.

### F-01 - Strategy Registry

| Campo | Valor |
|---|---|
| O que é | Cadastro auditável de estratégias, parâmetros, versão, status e evidências |
| Por que importa | Sem registry, o CaM não sabe quais estratégias existem nem quais gates cumpriram |
| Resolve | Q1, Q4, Q5, Q10 |
| Dependências | Definir contrato `Strategy`; aprovar modelo de status |
| Guardrail | Nenhuma estratégia promove a si mesma; Founder aprova transições |
| Prioridade sugerida | Alta |

### F-02 - S1 ORB Backtestável

| Campo | Valor |
|---|---|
| O que é | Implementar a S1 Opening Range Breakout 60m WIN como estratégia plugável para backtest |
| Por que importa | Dá destino concreto ao backtest engine e testa o ciclo de evidência |
| Resolve | Q4, Q5, Q10 |
| Dependências | Aprovação ou ajuste de [`EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md); tick histórico confiável |
| Guardrail | Não autoriza paper, demo ou real automaticamente |
| Prioridade sugerida | Alta |

### F-03 - Backtest P&L Real + Runs Persistidos

| Campo | Valor |
|---|---|
| O que é | Calcular resultado por tick scanning e persistir `BacktestRun`, trades e métricas |
| Por que importa | Sem P&L real e histórico de runs, backtest é demonstração técnica, não evidência |
| Resolve | Q4, TD-011, TD-015 |
| Dependências | Repository/migration de backtest; dados de tick |
| Guardrail | Resultado sempre líquido, com custos e IR |
| Prioridade sugerida | Alta |

### F-04 - Market Data Import Wizard

| Campo | Valor |
|---|---|
| O que é | Fluxo para importar CSV/Parquet/relatório MT5, validar schema, deduplicar e persistir ticks |
| Por que importa | Dado ruim gera backtest bonito e decisão ruim |
| Resolve | Q3, Q4, OP-003, TD-v0.2-09 |
| Dependências | Fonte de dados definida pelo Founder |
| Guardrail | Cada import deve registrar origem, hash, range temporal e contagem |
| Prioridade sugerida | Alta |

### F-05 - Evidence Pack de Estratégia

| Campo | Valor |
|---|---|
| O que é | Relatório por estratégia reunindo tese, runs, walk-forward, custos, violações, drawdown e status |
| Por que importa | Conecta Art. 28 a um artefato verificável |
| Resolve | Q4, Q5, Q10 |
| Dependências | F-01, F-03 |
| Guardrail | Evidence Pack não aprova gate; apenas mostra evidência |
| Prioridade sugerida | Alta |

### F-06 - Paper Trading Ledger

| Campo | Valor |
|---|---|
| O que é | Persistir simulações em `cam_paper_trades`, listar histórico e comparar paper vs backtest |
| Por que importa | Fase 1 exige evidência e aderência; paper sem histórico não sustenta decisão |
| Resolve | Q1, Q10, TD-022 |
| Dependências | Migration e repository |
| Guardrail | Badge e segregação explícita de PAPER; sem confusão com real |
| Prioridade sugerida | Alta |

### F-07 - Loop Governado de Paper/Demo

| Campo | Valor |
|---|---|
| O que é | Tick -> Strategy -> Risk Engine -> paper/demo fill -> journal/audit |
| Por que importa | Testa a automação completa sem capital real |
| Resolve | Q1, Q2, Q5, Q10 |
| Dependências | F-01, F-06, MT5 read-only estável |
| Guardrail | Kill switch deve parar o loop; fail-closed se heartbeat ou dado ficar stale |
| Prioridade sugerida | Alta, depois da base de backtest |

### F-08 - EA Control Plane Seguro

| Campo | Valor |
|---|---|
| O que é | Comandos allowlistados `PING`, `GET_STATE`, `PAUSE_EA`, `RESUME_EA`, healthcheck e audit |
| Por que importa | Dá controle operacional sem abrir envio de ordem |
| Resolve | Q2 |
| Dependências | Bridge MT5 read-only; contrato REQ/REP |
| Guardrail | `RELOAD_EA` fica fora até allowlist de artefatos/versionamento; sem path arbitrário |
| Prioridade sugerida | Média |

### F-09 - AI Analyst com DataCollector Real

| Campo | Valor |
|---|---|
| O que é | IA lendo journal, risk decisions e violações reais, com saída estruturada e resumo |
| Por que importa | A IA só fica útil quando lê dado real; antes disso, comenta vazio |
| Resolve | Q11, TD-016, TD-019, TD-020 |
| Dependências | Repositories reais; decisão Ollama/Anthropic |
| Guardrail | Read-only; remoto apenas com anonimização quando houver dado sensível |
| Prioridade sugerida | Média |

### F-10 - Carteira Hard Holdings

| Campo | Valor |
|---|---|
| O que é | Registro de ativos da Carteira Hard: ticker, quantidade, preço médio, data, origem do recurso |
| Por que importa | Harvest sem inventário vira saldo abstrato, não patrimônio auditável |
| Resolve | Q6 |
| Dependências | Definir política mínima de longo prazo |
| Guardrail | Carteira Hard não vira margem, não cobre loss e não aumenta exposição em derivativos |
| Prioridade sugerida | Média |

### F-11 - Dividendos/JCP Manual First

| Campo | Valor |
|---|---|
| O que é | Calendário e registro manual/CSV de dividendos/JCP, antes de scraping/API |
| Por que importa | Entrega valor patrimonial sem custo recorrente nem dependência frágil |
| Resolve | Q7 |
| Dependências | F-10 |
| Guardrail | Fonte de dados declarada e auditável; scraping/API só depois |
| Prioridade sugerida | Média-baixa |

### F-12 - Read-write MT5 em DEMO com Risk Mirror

| Campo | Valor |
|---|---|
| O que é | Bridge read-write apenas em conta DEMO, com `cam_risk_mirror.mq5`, audit e kill switch E2E |
| Por que importa | É o ensaio controlado da automação real |
| Resolve | Q1, Q2, Q10 |
| Dependências | F-01 a F-08; SPEC própria; SEC-GOV; QA-SEC |
| Guardrail | Nunca real por padrão; flags desligadas; demo e real segregados por conta, comando e log |
| Prioridade sugerida | Later governado |

---

## 8. Sequência recomendada de evolução

Esta sequência ajusta a proposta do CAM-analysis. A mudança principal: **não começar por read-write completo**. Primeiro evidência, depois paper/demo, depois patrimônio, depois automação de ordem em demo.

| Versão candidata | Outcome | Features centrais | Por que vem aqui |
|---|---|---|---|
| v0.4 | Evidence Engine | F-01 Strategy Registry, F-02 S1 ORB, F-03 Backtest P&L real + runs, F-04 Market Data Import, F-05 Evidence Pack | Maior valor com menor risco constitucional; transforma tese em evidência |
| v0.5 | Governed Paper Loop | F-06 Paper Trading Ledger, F-07 Paper/Demo loop, F-08 EA Control Plane, início F-09 AI DataCollector | Testa automação sem capital real e prepara Fase 1 |
| v0.6 | Wealth Loop | F-10 Carteira Hard Holdings, F-11 Dividendos Manual First, Harvest -> holdings, valorização simples | Fecha o propósito patrimonial da Constituição sem virar plataforma de investimentos |
| v0.7 | Demo Automation | F-12 Read-write MT5 em DEMO, `cam_risk_mirror.mq5`, kill switch E2E, journal automático de fills | Só depois de evidência, registry e paper loop auditável |

Observação: se Carlos quiser priorizar Carteira Hard antes de paper/demo, v0.5 e v0.6 podem trocar de lugar sem violar a visão. O que não deveria subir cedo é **read-write real**.

---

## 9. Features Later

Estas ideias fazem sentido, mas não agora.

| Feature | Por que later |
|---|---|
| Tape reading | Precisa tick real confiável, agressor, storage e hipótese testável |
| Book level 2 | Dado mais complexo, custo maior, risco de fascínio visual sem edge |
| ML quant para descobrir padrões | Pesquisa, não produto operacional; alto risco de overfitting |
| Pair trade / Long & Short clássico | Exige simultaneidade, exposição agregada e Fase 3+ para real |
| Múltiplos robôs | Exige regra constitucional/POV de capital, prioridade e risco agregado |
| Feed externo ações/FIIs | Depende de custo, contrato e necessidade real de decisão |
| Indicadores fundamentalistas internos | Não é core; usar ferramenta externa até provar necessidade de integração |
| RELOAD_EA/start total pelo CaM | Superfície de ataque maior; só com allowlist/versionamento forte |
| Produto comercial/SaaS | Contradiz natureza atual pessoal/local; só por decisão estratégica formal |

---

## 10. Features Out

Estas devem ficar explicitamente fora da visão atual.

- IA enviando ordem.
- IA alterando ou parametrizando Risk Engine.
- IA habilitando robô ou justificando exceção constitucional.
- Robô MQL5 puro que bypassa o Risk Engine Python.
- Execução real automática em Fase 0.
- Execução real automática sem Art. 28 completo.
- No-code visual builder de estratégias no ciclo inicial.
- HFT ou scalping de alta frequência.
- Exibição operacional de lucro bruto como métrica principal.
- Carteira Hard usada como margem, cobertura de loss ou argumento para aumentar mão.
- Múltiplos robôs simultâneos sem decisão explícita de exposição agregada.
- Scraping/API de dados sem verificar termos, qualidade e rastreabilidade.

---

## 11. Guardrails SEC-GOV obrigatórios

SEC-GOV deu **Conditional Go** para este documento como visão. Para execução futura, os guardrails abaixo devem aparecer nas SPECs correspondentes.

### 11.1 Ordem e automação

Toda feature que gere, confirme ou envie ordem deve declarar o fluxo:

```text
Strategy/Robot -> Risk Engine -> kill switch check -> journal/fiscal -> execução
```

Sem caminho paralelo.

Read-write MT5 só entra com:

- `cam_risk_mirror.mq5` como segunda linha de defesa;
- Risk Engine Python como autoridade principal;
- feature flags desligadas por padrão;
- fail-closed em heartbeat ausente, dado stale ou falha de conexão;
- comandos allowlistados;
- idempotency key contra duplicidade/replay;
- audit log de cada comando, decisão, fill, pause/resume, kill switch e falha.

### 11.2 Limites constitucionais

- Art. 11: máximo absoluto 2 WIN / 2 WDO.
- Fases 1 e 2: 1 contrato, WIN OU WDO, sem simultaneidade.
- Art. 15: se Risk Engine bloqueia, CaM não opera.
- Art. 18: kill switch deve parar robôs, EAs, bridge read-write e loops paper/demo.
- Art. 25: UI operacional mostra líquido de imposto provisionado.
- Art. 26: DARF atrasada bloqueia novas operações.
- Art. 31: operação/fill sem journal é falha operacional.
- Art. 35: IA não envia ordem, não altera risco, não justifica exceção.

### 11.3 Segregação demo/real

Demo e real devem ser separados por:

- conta;
- flag;
- comando;
- banner UI;
- audit log;
- configuração explícita;
- testes de impossibilidade de envio acidental para real.

Nunca depender apenas do nome do ambiente.

### 11.4 Supply chain MQL5

Qualquer EA, script ou `.ex5` deve ter:

- versão registrada;
- hash registrado;
- origem conhecida;
- allowlist de artefatos;
- sem path arbitrário;
- sem reload dinâmico antes de SPEC própria.

---

## 12. Decisões que Carlos precisa tomar primeiro

Estas decisões têm mais valor do que escolher feature isolada.

| ID | Decisão | Default recomendado |
|---|---|---|
| D-01 | CaM continua ferramenta pessoal/local? | Sim, por enquanto |
| D-02 | Próximo foco é evidência, automação, patrimônio ou IA? | Evidência primeiro |
| D-03 | Estratégias são Python-first? | Sim, com MQL5 como mirror/execução |
| D-04 | Quantas estratégias ativas no início? | Uma |
| D-05 | S1 ORB é aprovada como primeira tese? | Carlos decide em [`EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) |
| D-06 | Fonte de tick histórico inicial? | Resolver antes de backtest sério |
| D-07 | Read-write MT5 fica depois de registry/backtest/paper? | Sim |
| D-08 | Carteira Hard terá holdings ticker-a-ticker? | Sim, manual primeiro |
| D-09 | Indicadores fundamentalistas entram no CaM? | Não, usar ferramenta externa |
| D-10 | IA local/remota/mista? | Local para sensível; remoto só anonimizado |

---

## 13. Próxima SPEC recomendada

A próxima SPEC mais coerente com esta visão é:

```text
SPEC v0.4 - Evidence Engine e Strategy Lifecycle
```

Escopo sugerido:

- `Strategy` contract;
- Strategy Registry;
- S1 ORB como primeira estratégia plugável;
- backtest com P&L real por tick scanning;
- persistência de `BacktestRun`;
- import confiável de tick histórico;
- Evidence Pack por estratégia;
- nenhuma execução read-write;
- nenhuma autorização de operação real.

Por que esta SPEC primeiro:

- responde o núcleo de Q1/Q4/Q5/Q10 sem tocar capital real;
- reduz risco de automação prematura;
- transforma desejo de robô em ciclo de validação;
- prepara Fase 1 com evidência, não com entusiasmo;
- mantém a Constituição como arquitetura, não como rodapé.

---

## 14. Resumo executivo

O CAM-analysis está indo na direção certa: o CaM quer virar um cockpit capaz de estudar, validar, operar e patrimonializar com disciplina. O ajuste necessário é trocar a pergunta “quais features posso ter?” por “qual ciclo constitucional uma ideia precisa cumprir antes de virar operação?”.

A resposta de visão é:

```text
Strategy Lifecycle primeiro.
Dados como evidência, não decoração.
IA como auditora, não executora.
MT5 como executor, Python como governador.
Carteira Hard como patrimônio, não margem.
Read-write só em demo depois de registry, backtest, paper, kill switch e journal.
```

Se essa bússola for mantida, o CaM pode crescer sem virar feature factory e sem repetir o erro original que a Constituição nasceu para impedir: deixar convicção passar na frente do sistema.

---

## Referências cruzadas

- [`CAM-ANALISYS.MD`](./CAM-ANALISYS.MD)
- [`QUESTIONS-CAM-ANALISYS.MD`](./QUESTIONS-CAM-ANALISYS.MD)
- [`DVP.md`](./DVP.md)
- [`SCOPE.md`](./SCOPE.md)
- [`SPEC-v0.3-TECH-DEBT-REVIEW.md`](./SPEC-v0.3-TECH-DEBT-REVIEW.md)
- [`PLAN-v0.3.md`](./PLAN-v0.3.md)
- [`../STACK-CAM-OFICIAL.md`](../STACK-CAM-OFICIAL.md)
- [`../strategies/EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md)
- [`../../CONSTITUICAO.md`](../../CONSTITUICAO.md)
- [`../../apps/cam-cockpit/TECH-DEBT.md`](../../apps/cam-cockpit/TECH-DEBT.md)

---

> **Gate de visão:** Founder revisa, ajusta defaults e decide se a próxima SPEC nasce como `SPEC v0.4 - Evidence Engine e Strategy Lifecycle`.
>
> [ ] Carlos Rodrigues Ferreira Junior - Data: ___/___/______

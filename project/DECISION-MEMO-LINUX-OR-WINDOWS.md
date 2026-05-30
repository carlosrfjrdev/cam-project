---
template: DECISION-MEMO
phase: ARCH
status: Approved
version: 1
date: 2026-05-25
decided_at: 2026-05-25
decision: Opção B — Linux + MT5 + MQL5
---

# DECISION-MEMO — Stack Linux+MT5 vs Windows+Profit

> **Decisão-mãe da Fase 0 → Fase 1.** Sem ela, nada começa.
>
> **Lead:** Oscar (arquitetura)
> **Contraditório:** Voltaire (devil's advocate dos dois lados)
> **Skill:** `teczi-architecture-decision`
> **Aprovador:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vinculação constitucional:** Arts. 6º (preservar mais capital), 8º (perímetro), 38º (emenda)
>
> Este documento **não decide.** Ele organiza a decisão para o Founder tomar com plena consciência do trade-off.

---

## 1. Contexto da decisão

O CaM precisa de plataforma de execução vinculada a uma corretora brasileira para operar WIN/WDO. Existem hoje duas variantes de stack documentadas em paralelo (`STACK-CAM-OFICIAL.md` e `STACK-CAM-OFICIAL-LINUX.MD`), e a decisão entre elas é a **decisão-mãe** que precede toda a Fase 1 (Paper Trading).

### Fricção real reportada pelo Founder

Carlos manifestou desconforto operacional com Windows como SO de produção. O ambiente de desenvolvimento já é Linux (Ubuntu 26.04 LTS, Docker 29.1 nativo). Manter dev em Linux e prod em Windows introduz uma classe de bugs (paths, line endings, codecs, comportamento de filesystem) que não existe quando dev=prod.

### Por que esta decisão é irreversível na prática

- Cada variante exige integração específica (NTSL vs MQL5) → mudar depois é refazer Bloco D do PLAN.
- Cada variante exige corretora compatível com a plataforma → mudança força nova vinculação.
- Cada variante define o **edge mínimo de sobrevivência** via custos fixos mensais.

Por isso este Decision Memo precisa de aprovação formal com **cooldown explícito antes de reabertura** (Art. 38º — emenda constitucional aplicada por analogia, mesmo não sendo emenda à Constituição em si).

### Vinculação à Constituição

- **Art. 8º (perímetro):** Custos de plataforma estão **fora** do perímetro do CaM — saem do bolso PF. Isso não significa que custo é irrelevante: ele define o edge mínimo que a estratégia precisa atingir para o operador parar de queimar caixa pessoal.
- **Art. 6º (preservar mais capital):** Em conflito entre as variantes, prevalece a que reduz risco de erro operacional e custo recorrente sobre o capital declarado de R$ 5.000,00.
- **Art. 38º (emenda):** Esta decisão, embora não seja emenda constitucional, é decisão-mãe arquitetural. Deve respeitar cooldown de reabertura para não ser revisitada em D+0 de qualquer evento emocional.

---

## 2. Opções consideradas

### 2.1 Opção A — Windows 11 + Profit Pro/Ultra + NTSL

**Stack canônica:** [`STACK-CAM-OFICIAL.md`](./STACK-CAM-OFICIAL.md)

| Item | Valor |
|---|---|
| SO produção | Windows 11 |
| SO desenvolvimento | Linux → Windows (dual SO) |
| Broker/plataforma | Profit Pro/Ultra (Nelogica) |
| Linguagem broker | NTSL (parecido com Pascal) |
| Backend cockpit | Python 3.12 + FastAPI (idêntico nas duas opções) |
| Frontend | React 19 + Vite + MUI (idêntico) |
| Banco | PostgreSQL 16 + TimescaleDB via Docker Desktop + WSL2 |
| API Python para o broker | ProfitDLL (Fase 5+ opcional, só Windows) |
| Custo de plataforma mensal | R$ 200–380 (Profit Pro) + R$ ? (Automação de Estratégias Fase 4+) |
| Custo de licença SO | Windows 11 (≈ R$ 700 uma vez, ou OEM já no hardware) |
| Faseamento integração | Manual → CSV → Semi-auto → NTSL → ProfitDLL (5 fases) |

**Documento de referência:** ADR-001 (Profit como plataforma oficial), ADR-008 (Integração faseada Profit), ADR-009 (NTSL espelhada como 2ª linha), ADR-012 (Dev Linux, prod Windows).

### 2.2 Opção B — Linux (Ubuntu LTS) + MetaTrader 5 + MQL5

**Stack canônica:** [`STACK-CAM-OFICIAL-LINUX.MD`](./STACK-CAM-OFICIAL-LINUX.MD)

| Item | Valor |
|---|---|
| SO produção | Ubuntu 24.04+ LTS |
| SO desenvolvimento | Mesmo Linux (dev = prod) |
| Broker/plataforma | MetaTrader 5 (MetaQuotes) |
| Linguagem broker | MQL5 (parecido com C++) |
| Backend cockpit | Python 3.12 + FastAPI (idêntico nas duas opções) |
| Frontend | React 19 + Vite + MUI (idêntico) |
| Banco | PostgreSQL 16 + TimescaleDB via Docker Engine nativo |
| API Python para o broker | Bridge ZeroMQ (dwx-zeromq-connector) OU MetaApi SaaS OU package oficial (só Windows) |
| Hospedagem do MT5 | Wine local (A) OU container Wine (B) OU VPS Windows remoto (C) |
| Custo de plataforma mensal | R$ 0 (MT5 gratuito) ou R$ 80–180 (se VPS opção C) |
| Custo de licença SO | R$ 0 (Ubuntu LTS) |
| Faseamento integração | Manual → CSV/HTML → Bridge read-only → Bridge read-write → Package nativo opcional (5 fases) |

**Documento de referência:** ADR-001-LINUX, ADR-008-LINUX, ADR-009-LINUX (Risk Engine espelhado em MQL5), ADR-012-LINUX (dev = prod), ADR-014-LINUX (Wine local + plano B VPS), ADR-015-LINUX (Docker Engine nativo).

### 2.3 Opção híbrida (mencionada para descartar conscientemente)

Começar Linux+MT5 com plano explícito de migrar para Windows+Profit se Wine glitchar nas primeiras 4 semanas. **Não recomendado** por Oscar nem por Voltaire: introduz custo de mudança não-trivial, dilui a aprendizagem em duas plataformas, e o cooldown do Art. 38º estaria sempre tensionado. **Listada aqui para que o Founder rejeite explicitamente.**

---

## 3. Critérios de decisão

> **Regra:** O Founder atribui peso a cada critério antes de decidir. Os pesos não estão preenchidos abaixo — Oscar não infere prioridades.

| # | Critério | Descrição | Vantagem para A (Windows+Profit) | Vantagem para B (Linux+MT5) | Peso (1-5) Founder |
|---|---|---|---|---|---|
| 3.1 | **Custo recorrente mensal** | Quanto sai do bolso PF todo mês só para a stack rodar | — | R$ 200–350/mês a menos | ___ |
| 3.2 | **Dev = Prod** | Mesmo SO em dev e prod, eliminando classe de bugs cross-platform | — | Dev e prod no mesmo Linux | ___ |
| 3.3 | **Estabilidade da plataforma** | Plataforma funciona consistentemente, sem glitches que parem o operador | Profit nativo Windows, robusto | MT5 nativo apenas em Windows; em Linux passa por Wine ou VPS | ___ |
| 3.4 | **Familiaridade do operador** | Tempo até o operador estar produtivo na linguagem da estratégia | NTSL é simples (Pascal-like) | MQL5 é C++-like — mais alinhado ao background Java do Carlos | ___ |
| 3.5 | **Latência ordem→broker** | Tempo entre decisão Python e ordem chegando ao mercado | Profit nativo: ms (sem hop adicional) | Wine local: ms (idêntico); VPS: ms + RTT até SP | ___ |
| 3.6 | **Comunidade PT-BR** | Quantidade de tutoriais, fóruns e quants brasileiros operando a stack | Profit/NTSL dominante no Brasil; documentação 100% PT | MT5 com PT da MetaQuotes; comunidade BR menor, EN abundante | ___ |
| 3.7 | **Compatibilidade da corretora** | Corretora vinculada permite operar a plataforma escolhida com EA/automação para PF | A maioria das corretoras brasileiras suporta Profit | Várias suportam MT5 — **precisa validar antes da Fase 1** (ver §5) | ___ |
| 3.8 | **Risco de descontinuação** | Risco da plataforma sair do mercado ou perder suporte oficial em horizonte de 5+ anos | Profit ~20 anos, Nelogica BR consolidada | MT5 padrão mundial, MetaQuotes referência global | ___ |
| 3.9 | **Fricção operacional pessoal** | Quanto a stack incomoda o operador no uso diário (a fricção real reportada por Carlos) | Windows é a fricção declarada | Linux é o ambiente confortável declarado | ___ |
| 3.10 | **Backtest no broker (auxiliar)** | Qualidade do simulador da própria plataforma como complemento ao backtest engine do CaM | Profit tem replay/simulador | MT5 tem **Strategy Tester** tick-by-tick robusto | ___ |
| 3.11 | **Cross-broker futuro** | Possibilidade de operar outros mercados (Forex, Crypto) sem trocar de stack | Profit é uni-broker BR | MT5 é cross-broker mundial | ___ |
| 3.12 | **Stack 100% open source** | Toda a stack (exceto driver da B3) ser livre, sem dependência comercial | Profit Pro é pago | MT5 é gratuito, Ubuntu, Docker Engine, Wine — tudo open source | ___ |

### Como o Founder usa esta tabela

1. Atribui peso 1–5 a cada critério na coluna direita.
2. Pontua A e B em cada critério (escala 0–10 onde 10 = vantagem máxima).
3. Soma `peso × pontuação` para cada opção.
4. Maior soma indica direção, **não** decisão final — a decisão segue na §6.

> **Oscar não preenche os pesos.** Founder-only.

---

## 4. Análise contraditória — Voltaire fala dos dois lados

> Voltaire **não escolhe** entre A e B. Voltaire **defende cada uma** com o melhor argumento honesto que consegue produzir. O Founder lê os dois e decide.

### 4.1 Voltaire pró-A (Windows+Profit)

**O argumento honesto pró-Windows:**

> "Você não está construindo um cockpit para celebrar liberdade técnica. Você está construindo um cockpit para **impedir que você quebre quando estiver convicto demais** (Art. 4º). Liberdade técnica é confortável, **estabilidade operacional é constitucional**.
>
> Profit é a plataforma de execução com **maior densidade de operadores brasileiros, maior volume de tutoriais em português e maior cobertura de cenários edge** já documentados em fóruns BR. Quando você abrir o cockpit em pregão real pela primeira vez e algo der errado — e vai dar errado pelo menos uma vez — você vai querer Google em português com 50.000 resultados, não vai querer descobrir que o forum.mql5.com tem 3 respostas para o seu problema específico, todas em inglês, todas de 2019.
>
> O custo de R$ 200–380/mês de Profit Pro é **honestidade dura sobre o edge mínimo** (Voltaire web disse isso, e ainda vale). Mas isso **não muda** com a opção B se você for para VPS: R$ 80–180/mês de VPS Windows é o mesmo problema com cara diferente. E se você for para Wine local, você não economiza R$ 0–30/mês; você gasta R$ 0 em dinheiro **e horas indeterminadas em manutenção de Wine** — que custam mais que R$ 200/mês ao operador que opera Porto + Monnezy.
>
> Você é um engenheiro Java/backend que conhece Windows porque Microsoft é dominante no mercado corporativo. Aprender MQL5 (C++-like) é mais alinhado com Java do que NTSL (Pascal-like) — **verdade**. Mas o tempo de aprendizagem da linguagem não é o gargalo. O gargalo é **operar com confiança em horário de pregão**. E confiança vem de previsibilidade — Profit just works.
>
> Linux+MT5 é a escolha do operador que **gosta de mexer no carro**. Windows+Profit é a escolha do operador que **quer chegar ao destino**. Você precisa decidir qual operador você é antes desta primeira fase. Em caso de dúvida, Art. 6º: o que **preserva mais capital** é a configuração com menor variância operacional, e essa é Windows+Profit hoje."

**Modos de falha de A (Voltaire admite honestamente):**

- (A.1) Custo recorrente R$ 200–380/mês corrói o edge mínimo se a estratégia não compensar — risco constitucional sobre R$ 5.000.
- (A.2) Dev=prod quebrado introduz bugs sutis em paths/codecs que vão pegar você em pregão.
- (A.3) Profit é caixa-preta — quando glitcha, você não tem acesso ao source para investigar.
- (A.4) NTSL é menos expressiva — quando a estratégia evoluir, você pode bater no teto da linguagem antes do tempo.
- (A.5) Lock-in com Nelogica — se a Nelogica subir preço ou mudar política, você não tem alternativa fácil.

### 4.2 Voltaire pró-B (Linux+MT5)

**O argumento honesto pró-Linux:**

> "Você é desenvolvedor Linux há anos. Sua rotina, seu Docker, seu Git, seu editor — tudo está afinado em Linux. **Você ganhou produtividade dura nessa configuração**. Forçar produção em Windows é colocar o operador no terreno onde ele é mais lento e tem maior fricção — o que aumenta a probabilidade de erro humano em pregão.
>
> Custo zero ou quase-zero (R$ 0–30/mês) não é só economia: é **autonomia constitucional**. Se a Nelogica subir o Profit Pro para R$ 500/mês daqui a 2 anos, você não tem escolha — é sair do mercado ou pagar. Com MT5 gratuito, você decide quando trocar de broker, quando trocar de hospedagem, quando trocar de bridge. Você **não fica refém de uma decisão de pricing de terceiro**.
>
> MQL5 é mais alinhado ao seu background Java/C++. Você vai ler código MQL5 com mais naturalidade do que NTSL (Pascal-like). Isso reduz tempo de bug em estratégia, e bug em estratégia em horário real custa caro.
>
> O argumento de comunidade brasileira é real, mas tem nuance: Profit/NTSL tem comunidade BR maior, **mas a comunidade quant séria globalmente está em MT5**. Backtest, walk-forward, Sharpe, distribuição de retornos — você acha esse tipo de discussão em volume muito maior em forum.mql5.com (em EN) do que em qualquer fórum BR sobre NTSL. Para quant amador, PT-BR ganha. Para quant rigoroso (que é o que a Constituição exige), EN vence.
>
> Wine é a variável incômoda — verdade. Mas você não precisa decidir Wine vs VPS hoje. Você decide **Linux como SO produção**, instala Wine para Fase 1 (paper trading com conta demo MT5), e **mede empiricamente** se Wine estabiliza. Se sim, ótimo. Se não, migra para VPS Windows (R$ 80–150/mês) sem reescrever bridge — só muda IP da conexão ZeroMQ. **Reversibilidade barata**. Já no caminho Windows+Profit, voltar para Linux é refazer Bloco D inteiro.
>
> Em caso de dúvida, Art. 6º: o que **preserva mais capital** sobre R$ 5.000 declarados é a configuração com custo recorrente menor. R$ 200/mês de Profit Pro são **4% mensais sobre o capital declarado**. Em 12 meses isso são R$ 2.400 — metade do capital declarado, sumindo só em plataforma. Em Linux+MT5+Wine, isso vai pra R$ 0–30/mês. A matemática é dura, e Art. 6º não negocia."

**Modos de falha de B (Voltaire admite honestamente):**

- (B.1) Wine glitcha em update do MT5 ou do Wine, e você fica sem operar em pregão.
- (B.2) Bridge ZeroMQ perde conexão silenciosamente (TCP sem heartbeat ativo) — risco de posição aberta sem cobertura sistêmica (Art. 19º).
- (B.3) Corretora brasileira pode exigir plano específico para "Algorithmic Trading" via EA — pode anular a economia frente ao Profit.
- (B.4) Comunidade BR é menor — quando algo der errado em pregão, ajuda em PT é mais escassa.
- (B.5) MetaQuotes pode encerrar suporte oficial a Linux/Wine sem aviso — força migração para VPS (mas a bridge não muda).
- (B.6) Manutenção de Wine consome tempo do operador (custo invisível) que não aparece em planilha de custos.

### 4.3 O que Voltaire **não vai fazer**

- Voltaire **não vai dizer** qual opção é "a certa". A decisão é do Founder (Art. 36º — operador em decisão manual no topo da hierarquia quando legitimamente em estado frio).
- Voltaire **não vai usar** o argumento "Linux é melhor porque é open source" como princípio moral — só vale como argumento operacional se Carlos for o tipo de operador que opera melhor em open source. **Pergunta para o Founder, não para Voltaire.**
- Voltaire **não vai descartar** o desconforto reportado do Founder com Windows como "subjetivo demais". Fricção operacional pessoal é critério constitucional válido (Art. 6º — preserva mais capital também significa reduzir probabilidade de erro humano por fricção).

---

## 5. Pontos que dependem de evidência externa (gatilhos a investigar)

Estes pontos **não devem ser resolvidos por inferência**. São perguntas para o mundo real responder antes da decisão final.

### 5.1 Corretora confirma suporte a EA em MT5 para PF?

**Status:** Aberto — requer investigação na fase de discovery de corretora ([`CORRETORA-EVAL.md`](./CORRETORA-EVAL.md) — DOC 2 deste pacote).

**Ações:**
- Listar corretoras brasileiras que oferecem MT5 com WIN/WDO (XP, Clear, Genial, Modal, Avenue, Toro são candidatas).
- Para cada uma, perguntar formalmente: **"Para PF com R$ 5.000 declarados em conta, é permitido operar Expert Advisor via MT5 sem plano adicional ou taxa de Algorithmic Trading? Existe plano específico para isso? Qual o custo?"**
- Se nenhuma corretora viável permitir EA para PF sem custo proibitivo, **a Opção B fica fragilizada** — eleva risco constitucional.

### 5.2 Wine local estabiliza em uso real?

**Status:** Aberto — só pode ser medido empiricamente.

**Ações (se Founder pendular para Opção B):**
- Instalar Wine + MT5 no Ubuntu 26.04 atual.
- Rodar conta demo MT5 com EA simples (ex: ler ticks + escrever em log) durante 4 semanas de horário de pregão.
- Registrar: número de crashes, número de updates do Wine que quebraram MT5, latência média da bridge ZeroMQ.
- Critério de validação: **0 crashes em horário de pregão durante 4 semanas consecutivas** → Wine validado para Fase 1. Caso contrário → migrar para Opção C (VPS Windows).

### 5.3 Custo real de VPS Windows (Opção C dentro de B)?

**Status:** Aberto — requer cotação atualizada.

**Ações:**
- Cotar VPS Windows com latência ≤ 10 ms para B3/SP em pelo menos 3 provedores (Forex VPS, ContaboFX, AWS LightSail Windows, Vultr).
- Confirmar: custo mensal, uptime SLA, suporte para MT5, latência medida da datacenter para B3.
- Se VPS sair acima de R$ 200/mês, **a economia da Opção B desaparece** — reabre comparação direta com Opção A.

### 5.4 ProfitDLL real está acessível e mantida?

**Status:** Aberto — atinge a Opção A no longo prazo.

**Ações:**
- Confirmar com Nelogica: versão atual do ProfitDLL, política de versionamento, custo (se houver) para acesso PF.
- Se ProfitDLL estiver descontinuada ou exigir plano corporativo, a Fase 5 da Opção A vira inviável — não afeta Fase 1, mas afeta horizonte de longo prazo.

### 5.5 Profit Pro vs Ultra: qual permite Automação de Estratégias?

**Status:** Aberto — toca a Opção A.

**Ações:**
- Confirmar com Nelogica: qual versão (Pro ou Ultra) permite módulo de Automação de Estratégias.
- Levantar custo do módulo de Automação separadamente.
- Se for apenas Ultra **e** custar significativamente mais, recalcular custo mensal da Opção A — pode ultrapassar R$ 400/mês.

---

## 6. DECISÃO DO FOUNDER

> Esta seção é preenchida **exclusivamente** pelo Founder em estado frio (pregão fechado, fora de D+0 de evento emocional — Art. 38º por analogia).

**Opção escolhida:**
```
[ ] A — Windows 11 + Profit Pro/Ultra + NTSL
[x] B — Linux (Ubuntu LTS) + MT5 + MQL5
[ ] Adiar decisão (registrar motivo abaixo)
```

**Data da decisão:** 25/05/2026

**Motivação registrada (mínimo 3 frases — para o ledger constitucional):**

```
A decisão foi tomada primariamente por causa de custos.
Como o CaM está em uma fase de construção iremos adotar a abordagem de MCP (Menor Custo Possível)
Se o CaM se provar valioso e lucrativo, podemos migrar para profit.

```

**Critérios determinantes (quais da §3 pesaram mais):**

```
Tenho experiencia com mql5 e o metatrader possui custos mais competitivos.
Podemos criar externalização das automações isto facilita integração com CAM.
O modelo olhama funciona melhor em linux
Podemos evoluir posteriormente na v2
Mas declaro: V1 é MT5 + Linux, v2 podemos extender a capacidade multiplataforma.

```

**Cooldown declarado para reabertura desta decisão:**

```
[ ] 30 dias (cooldown padrão Art. 38º para mudança expansiva)
[ ] 90 dias (cooldown estendido por irreversibilidade prática do código gerado)
[ X ] Outro: 00 dias com justificativa: Depende da minha decisão
```

**Assinatura simbólica do Founder (rubricar):** (frescura overengineering)

---

## 7. Condições que reabririam a decisão (gatilhos objetivos)

A decisão registrada na §6 **não pode ser reaberta** dentro do cooldown declarado, **exceto** se um dos gatilhos objetivos abaixo for ativado de forma documentável. Cada gatilho ativo dispara revisão **obrigatória** desta decisão.

### Gatilhos que reabrem para **revisitar Opção A → B** (se A foi escolhida)

- **G-A1:** Custo recorrente Profit Pro + Automação de Estratégias ultrapassa R$ 500/mês em pregão fechado vigente.
- **G-A2:** Nelogica descontinua oficialmente o Profit Pro **ou** o módulo de Automação de Estratégias.
- **G-A3:** Operador acumula **3 ou mais incidentes** de quebra de produtividade documentados em journal/OPS-event causados por dual SO (path errado, encoding, etc.) em janela de 30 dias.
- **G-A4:** ProfitDLL é descontinuada e Fase 5 da integração vira inviável **enquanto** a estratégia em uso precisar de execução automática mais granular do que NTSL oferece.

### Gatilhos que reabrem para **revisitar Opção B → A** (se B foi escolhida)

- **G-B1:** Wine local registra **3 ou mais crashes** documentados em horário de pregão em janela de 30 dias **e** VPS Windows (Opção C) ultrapassa R$ 200/mês na cotação vigente.
- **G-B2:** Nenhuma corretora brasileira viável permite EA em MT5 para PF sem plano adicional acima de R$ 100/mês.
- **G-B3:** MetaQuotes encerra suporte oficial a Linux/Wine **e** a comunidade não publica solução estável em 60 dias.
- **G-B4:** Bridge ZeroMQ registra **2 ou mais incidentes** de perda silenciosa de conexão com posição aberta em janela de 90 dias (violação operacional do Art. 19º).

### Gatilhos universais (reabrem em qualquer direção)

- **G-U1:** Emenda constitucional (Art. 38º) altera Art. 11º, Art. 12º ou Art. 15º de forma que invalida o desenho de execução vigente.
- **G-U2:** Carlos formalmente declara cooldown expirado em estado frio, com motivação escrita no ledger constitucional.

---

## 8. Consequências em cascata

Esta decisão dispara as seguintes atualizações encadeadas. Não executar antes da §6 estar assinada.

### Se Opção A (Windows+Profit) for escolhida

1. `STACK-CAM-OFICIAL-LINUX.MD` → mover para `archive/` com nota "não escolhido em 2026-XX-XX por decisão registrada em DECISION-MEMO-LINUX-OR-WINDOWS.md".
2. `STACK-CAM-OFICIAL.md` → renomear para refletir status canônico definitivo (remover marcação "proposta em paralelo").
3. ADRs propostos relacionados promovidos a **ACEITA**: ADR-001, ADR-008, ADR-009, ADR-012 (variantes não-LINUX).
4. ADRs com sufixo `-LINUX` arquivados como **rejeitados** com link de volta a este Decision Memo.
5. `CLAUDE_MEMORY.MD` §5 e §11 → atualizar para refletir variante única escolhida.
6. `project/cam-cockpit/PLAN.md` → revisão obrigatória do Bloco D (integração) para confirmar que TASKs T-D01 a T-D04 estão alinhadas com Profit/NTSL.
7. `CORRETORA-EVAL.md` (DOC 2 deste pacote) → foco apenas em corretoras compatíveis com Profit.

### Se Opção B (Linux+MT5) for escolhida

1. `STACK-CAM-OFICIAL.md` → mover para `archive/` com nota "não escolhido em 2026-XX-XX por decisão registrada em DECISION-MEMO-LINUX-OR-WINDOWS.md".
2. `STACK-CAM-OFICIAL-LINUX.MD` → renomear para `STACK-CAM-OFICIAL.md` (sem sufixo) refletindo status canônico definitivo.
3. ADRs com sufixo `-LINUX` promovidos a **ACEITA** sem sufixo: ADR-001, ADR-008, ADR-009, ADR-012, ADR-014, ADR-015.
4. ADRs originais (sem sufixo) que conflitam com a variante Linux arquivados como **rejeitados** com link de volta a este Decision Memo.
5. `CLAUDE_MEMORY.MD` §5 e §11 → atualizar para refletir variante única escolhida.
6. `project/cam-cockpit/PLAN.md` → revisão obrigatória do Bloco D (integração) para substituir `profit_integration/` por `mt5_integration/` com bridge ZeroMQ.
7. `apps/cam-cockpit/backend/cam/features/profit_integration/` → renomear para `mt5_integration/` e adaptar implementação (Bridge ZeroMQ no lugar de CSV importer Profit).
8. `apps/cam-cockpit/ntsl/` → renomear para `apps/cam-cockpit/mql5/` com nova estrutura (`experts/`, `indicators/`, `scripts/`, `include/`).
9. `CORRETORA-EVAL.md` (DOC 2 deste pacote) → foco apenas em corretoras com MT5 + EA para PF.
10. `scripts/install_wine_mt5.sh` → criar (script de instalação Wine+MT5 ainda inexistente).

### Independente da escolha

- **DOC 2 (`CORRETORA-EVAL.md`)** só pode focar definitivamente após esta decisão. Até lá, deve manter matriz dupla.
- **DOC 4 (`EDGE-THESIS-S1.md`)** independe desta decisão para a tese central, mas a implementação técnica (NTSL vs MQL5) depende.
- **DOC 5 (`RUNBOOK-INCIDENTE-TECNICO.md`)** depende: comandos e telefones de suporte mudam conforme a plataforma.

---

## 9. Gate Founder

Esta seção é o ponto de aprovação formal. **Não preencher** até a §6 estar completa e o cooldown da §7 estar declarado.

```
[ ] Carlos Rodrigues Ferreira Junior aprova este Decision Memo como instrumento de
    decisão e registra na §6 sua escolha em estado frio, com pregão fechado,
    fora de D+0 de qualquer evento emocional documentado.

    Data: 25/05/2026

    Assinatura simbólica: (frescura overengineering)

    Próximo gate: execução das §8 (consequências em cascata) por agente designado,
    confirmação do Founder ao final de cada cascata.
```

---

## 10. ADENDO 2026-05-30 — Reversão da decisão (Opção B revogada)

**Gatilho objetivo disparado** (§7 — "Wine glitcha repetidamente / inviável"):
o MT5 sob **Wine no Linux falhou em teste**. O Founder **reverteu o SO para
Windows 11 nativo**, mantendo o broker **MetaTrader 5** (muda só onde/como o MT5
roda; sai a camada Wine).

- **Vigente:** Windows 11 + MT5 nativo + bridge ZeroMQ em `127.0.0.1`.
- **Soft-stage:** decisão de concepção pré-v1 — **sem ADR HARD**; docs moldáveis.
- **Inalterado:** Constituição, NCC-1701, backend Python/FastAPI, frontend React/MUI,
  Postgres+Timescale, Risk Engine, política da IA, EAs (`cam_bridge.mq5`,
  `cam_risk_mirror.mq5`), allowlist `OrderSend`, `REAL_TRADING_ALLOWED=false`.
- **Docs atualizadas:** `STACK-CAM-OFICIAL.md` (§0 + tabela + §6.1 supersedida),
  `ADR-012` (Superseded-in-part), runbook [`runbooks/RUNBOOK-WINDOWS.md`](./runbooks/RUNBOOK-WINDOWS.md),
  `cam-cockpit/TODO-OPERACIONAL.md` (OP-014).
- **ADRs alinhadas (2026-05-30):** ADR-001 → Superseded (plataforma = MT5);
  ADR-008/009 → Superseded-in-part (broker = MT5, espelho = `cam_risk_mirror.mq5`;
  princípios mantidos). **Pendente só na v1:** consolidar a stack Windows como HARD.

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) Arts. 4º, 6º, 8º, 11º, 12º, 15º, 19º, 36º, 38º
- [`STACK-CAM-OFICIAL.md`](./STACK-CAM-OFICIAL.md) — variante Windows+Profit
- [`STACK-CAM-OFICIAL-LINUX.MD`](./STACK-CAM-OFICIAL-LINUX.MD) — variante Linux+MT5, §13 matriz comparativa
- [`CORRETORA-EVAL.md`](./CORRETORA-EVAL.md) — DOC 2 deste pacote (matriz dupla até esta decisão)
- [`CLAUDE_MEMORY.MD`](../CLAUDE_MEMORY.MD) §5 e §11 — decisão-mãe pendente
- [`teczi-devflow/NCC-1701/phases/03-ARCH.md`](../teczi-devflow/NCC-1701/phases/03-ARCH.md) — fase ARCH NCC-1701

---

> **Princípio operacional deste documento:**
>
> Oscar organiza. Voltaire contradita os dois lados. O Founder decide.
>
> Nenhuma inferência substitui a §6.

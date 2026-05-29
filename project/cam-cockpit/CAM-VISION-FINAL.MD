---
template: VISION-FINAL
phase: DISC
status: Vigente
version: 1.1
date: 2026-05-27
source:
  - CAM-ANALISYS.MD
  - QUESTIONS-CAM-ANALISYS.MD (respondido pelo Founder)
  - CAM-VISION.MD
  - CAM-ANALISYS-REVIEW.MD
  - SCOPE-Vision-Evolution.md (v1.1)
orchestrator: Leo
personas_consolidadas:
  - Oscar (arquitetura)
  - Marty (escopo/discovery)
  - Albert (especificação)
  - Voltaire (devil's advocate)
  - Kevin (SEC-GOV)
  - Mammon (capital/custos)
  - Sun (estratégia mercado)
  - Vint (infra/OPS)
target_spec: SPEC-v0.4-VISION-EVOLUTION.MD
revision_note: >
  v1.1 — Founder consolidou 9 versões propostas em SPEC única
  (SPEC-v0.4-VISION-EVOLUTION). v1.0 fica sob declaração exclusiva
  do Founder (sem inferência). 6 decisões novas registradas (R-17..R-22):
  corretora Genial, S1 aprovada, multiestrategia com emenda, indicadores
  inferidos, scraping e OpenAI viraram tech debts.
---

# CAM-VISION-FINAL — Visão consolidada do CaM Cockpit

> **Função deste documento:** bússola final da evolução proposta. Consolida análise, respostas do Founder, visão preliminar e review num único artefato. Não é SPEC, não é PLAN, não autoriza CODE — direciona. **A v1.0 do CaM é declaração exclusiva do Founder e não é inferida aqui.**
>
> **Companion operacional:** [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md) — traduz esta visão em features in/out/later e trilhas de SPEC.

---

## 1. Identidade definitiva do CaM

> **O CaM é um cockpit-orquestrador pessoal, local, constitucional, capaz de transformar tese operacional em execução governada, evidência reprodutível e patrimônio auditável.**

Cinco palavras carregam essa identidade:

| Palavra | Significado vinculante |
|---|---|
| **Cockpit** | Centraliza decisões, controles e visão; não substitui o operador em estado frio |
| **Orquestrador** | Coordena estratégias, EAs, dados, IA e Carteira Hard num único loop governado |
| **Pessoal** | Construído para Carlos; SaaS/produto fica para decisão futura (CC.1 = "não é preocupação agora mas pode virar") |
| **Constitucional** | Toda capacidade respeita a hierarquia `Constituição > Risk Engine > Estratégia > IA > Operador` |
| **Auditável** | Cada decisão, dado, ordem e fill tem rastreabilidade completa (journal + audit + provenance) |

---

## 2. Frase-mãe da governança

```
Construir amplo. Liberar estreito.
Arquitetura N-ready. Operação inicial 1-first.
```

Esta é a tradução operacional de duas tensões reais nas respostas do Founder:

- Carlos quer **plataforma ampla** (Q3 "todos os níveis", Q5 "Python + MQL5 + DSL", Q8 "tudo no CaM", Q10 "orquestrador de estratégias", Q11 "todos juntos").
- Mas a Constituição exige **operação disciplinada** (Arts. 28, 29, 30 — gates antes de qualquer escalada).

A tensão se resolve assim:

| Camada | Pode nascer ampla? | Pode operar ampla nesta SPEC? |
|---|---|---|
| Modelo de domínio | ✅ Sim, N-ready | — |
| Esquemas DB | ✅ Sim, com provenance | — |
| Capacidade técnica | ✅ Sim (capacidade latente) | ❌ Travada por flag |
| Operação real | — | ❌ `REAL_TRADING_ALLOWED=false` por design |
| Operação demo/paper | — | ✅ 1 estratégia, 1 EA |
| Múltiplas estratégias simultâneas | ✅ no registry | ✅ permitido a partir de BL-H1 (Art. 11-A vigente desde EMENDA-001 v2 ratificada em 2026-05-27) |

---

## 3. Os 6 Pilares (consolidados)

> Cada pilar é uma família de features. SCOPE-Vision-Evolution detalha o quê e quando.

### Pilar 1 — Governança Constitucional

Materializa a Constituição como código que protege o operador.

**Núcleo já existente:** Risk Engine (18 validators), Kill Switch, Checklists, Audit Trail, Journal duplo (DB+JSONL), Mutex de feature flags.

**Extensões:**

- **Autonomy Matrix** — modo permitido por ambiente (backtest/paper/demo/real) × tipo (sinal/1-click/semi/full)
- **Order Gateway único** — todo path de ordem é forçado a passar por `Strategy/Robot → Risk Engine → OrderCommand → EA → Fill → Journal`
- **Risk Engine cross-asset** — futuro, para Long & Short e múltiplas estratégias agregadas
- **`REAL_TRADING_ALLOWED` por design** — flag pessoal trancada, `.env` + auditoria de mudança

### Pilar 2 — Strategy Lifecycle

Toda estratégia entra num ciclo auditável de estado, evidência e gate Founder.

**Estados do registry:**

```
draft → backtested → walk_forward_ok → paper_ok → demo_ok → real_authorized → retired
```

**Regras:**

- Nenhuma estratégia se autopromove. Founder aprova cada transição.
- Cada transição exige `Evidence Pack` (métricas, runs, aderência).
- Risk Engine valida cada candidate gerado pela estratégia.
- **Python = fonte canônica.** MQL5 = mirror/execução. DSL = camada declarativa futura que compila para o modelo Python.
- Múltiplas estratégias **registradas** ok. **Apenas 1 ativa em produção** até decisão Founder + risco agregado modelado.

### Pilar 3 — Integração MetaTrader (EA Control Plane)

> MT5 e EAs viram **extensão controlada do CaM**, não caixa preta externa. O cockpit fala com o terminal MT5 como se fosse parte do CaM — bridge ZeroMQ é o único tubo permitido.

**Princípios da integração MetaTrader:**

1. **MT5 executa, Python governa.** O terminal MT5 é processo externo conectado via bridge — nunca processo interno do CaM.
2. **Bridge ZeroMQ é único canal autorizado.** Nenhuma feature pode falar com MT5 por outro meio (sem `subprocess`, sem AppleScript-equivalente, sem injection).
3. **Conta vinculada Genial (R-17).** Toda integração assume conta Genial DEMO no MT5 inicialmente; conta real em allowlist explícita travada por flag.
4. **EA versionado + assinado.** Todo `.mq5`/`.ex5` com hash registrado em audit; reload exige allowlist (vedado por design em G2; liberado por SPEC dedicada em G3+).
5. **Heartbeat fail-closed.** Ausência de heartbeat > 3s ⇒ bridge `OFFLINE` ⇒ bloqueio de ordem + alerta Telegram.

**Capacidades progressivas:**

| Geração | Capacidade | Onde entra |
|---|---|---|
| G1 (já existe) | heartbeat, status, position/tick PUB | SPEC v0.2 |
| G2 | `PAUSE_EA`, `RESUME_EA`, versão+hash registrados, audit log de comandos | BL-A da SPEC v0.4-VISION-EVOLUTION |
| G3 | bridge read-write **em DEMO** com `cam_risk_mirror.mq5` | BL-E |
| G4 | múltiplos EAs simultâneos com risco agregado | BL-I (após BL-H emenda) |
| G5 | execução real com EA por estratégia | Não pertence a esta SPEC — Founder declara |

**Vedado por design:** `OrderSend/PositionOpen/etc` em MQL5 fora do Order Gateway. EA MQL5 puro decidindo ordem fora do Risk Engine Python = bypass constitucional.

### Pilar 4 — Market Data Platform

Dado vira evidência, não decoração. Antes de buscar mais dado, decidir **qual decisão melhora**.

**Camadas:**

- **Instrument Catalog** — WIN/WDO + ações + FIIs + outros (universo amplo declarado mas habilitado por demanda)
- **Tick / Trade / Book** — todos os 3 níveis aceitos como destino (Q3 Founder: "tudo"); ordem de ingestão por necessidade de decisão
- **Provenance** — fonte, custo, qualidade, hash, latência, contrato de uso registrados por lote
- **Tick histórico WIN** primeiro (validar S1) → tick real-time WIN/WDO → book level 2 → ações/FII → cross-asset
- **Gate Mammon (R-11):** feed pago só após 1 mês operacional acima do break-even + drawdown controlado

### Pilar 5 — Wealth Loop (Journal → Fiscal → Harvest → Carteira Hard)

Fecha o ciclo patrimonial constitucional.

**Núcleo já existente:** Journal duplo, Fiscal (IR 20%, IRRF 1%, DARF, compensação), Harvest 60/40 + Sangria 80/20.

**Extensões:**

- **Carteira Hard com holdings reais** — ticker, qtde, preço médio, data; manual via UI + importação corretora para conciliação
- **Valorização a mercado** (após Pilar 4 entregar cotação ações/FII)
- **Critérios fundamentalistas leves** — DY tem peso forte, mais 6 indicadores a definir em POV
- **Rebalanceamento sugerido** — sugestão, nunca execução automática
- **Dividendos/JCP** — calendário + histórico + projeção 12 meses; scraping múltiplo com cache e respeito a ToS

### Pilar 6 — Research & AI Workbench

IA como **lente**, nunca volante. Workbench de pesquisa para hipóteses, padrões, cross-asset.

**Inputs reais:** journal, risk decisions, ticks, posições, book (quando disponível).

**Outputs aceitos:** texto, JSON estruturado, score, sugestão de regra (que vira SPEC), visualização.

**Vedado (Art. 35):** IA enviar ordem, IA habilitar estratégia, IA alterar Risk Engine, IA justificar exceção constitucional, IA decidir exposição.

**Providers:**

- **Ollama local** (default — privacidade total)
- **Anthropic API** (qualidade superior — dados anonimizados)
- **OpenAI** (a avaliar) — exige ADR antes de entrar na stack

**Cross-Asset Pattern Lab** — feature distinta da IA "auditora pós-mercado". Lab consome book/tape/cross-asset, gera hipóteses, devolve para Founder validar via SPEC + backtest. Sem promoção automática.

---

## 4. Decisões formalmente registradas (R-01..R-16)

Estas decisões saem das respostas do Founder + review e ficam **vigentes** até nova SPEC ou emenda.

| ID | Decisão registrada |
|---|---|
| **R-01** | CaM tem **capacidade real latente** + **operação real travada por design** (`REAL_TRADING_ALLOWED=false` default + allowlist explícita). Quando liberar real é declaração do Founder, não desta visão |
| **R-02** | Autonomy Matrix vigente: backtest/paper aceitam todos os modos; demo aceita 1-click + semi; real bloqueado até gates da Constituição cumpridos |
| **R-03** | **Python é fonte canônica** de estratégia. MQL5 é mirror/execução. DSL é camada declarativa futura que compila para Python |
| **R-04** | MQL5 só **executa/mira** — proibido decidir ordem fora do Risk Engine Python |
| **R-05** | **S1 = ORB 60m WIN** (provisional — Founder confirma em [`EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) §11) |
| **R-06** | **1 estratégia ativa em produção inicial.** Registry N-ready |
| **R-07** | Regra de conflito entre sinais (Robot Orchestrator) **a definir em SPEC própria** quando 2ª estratégia for promovida |
| **R-08** | Risco agregado multi-EA / multi-estratégia **a modelar em SPEC própria** antes de qualquer operação simultânea |
| **R-09** | Comandos EA na ordem: `PING/GET_STATE/GET_POSITIONS/GET_SYMBOL_INFO` (já) → `PAUSE_EA/RESUME_EA` (v0.4) → `RELOAD_EA/START/STOP` (allowlist+versionamento, depois) |
| **R-10** | Fonte de tick histórico inicial: importação CSV/Parquet via `cam_market_ticks` + provenance; corretora confirma se exporta tick (TODO-OPERACIONAL OP-003) |
| **R-11** | Gatilho de investimento em feed pago: **expectância líquida positiva após custos+IR + drawdown ≤20% por 30 dias úteis** (não "% de acerto" cru — Voltaire) |
| **R-12** | 7 indicadores fundamentalistas iniciais — a serem eleitos em SPEC própria; DY tem peso forte; lista provisória: `DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC` |
| **R-13** | Critérios Carteira Hard: **sugestivos com alerta + checklist de justificativa**. Bloqueio hard só após política patrimonial objetiva em POV |
| **R-14** | Scraping múltiplo aceito **com governança**: fonte rastreável, cache local, rate limit, respeito a ToS. Sem bypass de login/CAPTCHA |
| **R-15** | OpenAI **fora da stack atual** — exige ADR + SPEC antes de entrar. Ollama + Anthropic permanecem default |
| **R-16** | Long & Short começa em **research/backtest** (Trilha F do SCOPE). Real depende de fase compatível + Risk Engine cross-asset |
| **R-17** | **Corretora vinculada: Genial Investimentos.** Cobre tanto BL-D (importação de holdings) quanto BL-E (MT5 DEMO read-write). Validação de plano EA permanece como ação de TODO-OPERACIONAL antes de BL-E |
| **R-18** | **S1 ORB 60m WIN APROVADA** como primeira estratégia plugável. Founder confirmou — sem necessidade de nova rodada `EDGE-THESIS-S1.md` §11 |
| **R-19** | **Multiestrategia APROVADA** — ✅ **EMENDA-001 v2 RATIFICADA em 2026-05-27** (Constituição v1.1). Art. 11-A criado (multiestratégia simultânea, 8 condições) + Art. 11-B criado (escalonamento condicional do limite por default — métrica composta + cooldown reverso + reversão automática). BL-H decomposto em BL-H1 (Robot Orchestrator) + BL-H2 (Strategy Escalation Engine). Ambos desbloqueados |
| **R-20** | **7 indicadores fundamentalistas (lista oficial):** `DY` (peso forte), `P/L`, `P/VP`, `ROE`, `Dívida Líquida/EBITDA`, `Payout`, `ROIC`. Inferidos por Albert a partir de prática consolidada do mercado BR. Lista pode ser ajustada via emenda à POV |
| **R-21** | **Scraping multi-fonte: vira `TD-v0.4-01`** — fontes específicas, ToS, schema canônico, rate limit e cache a definir em SPEC própria antes de BL-F entregar F-26 |
| **R-22** | **OpenAI provider: vira `TD-v0.4-02`** — ADR aceitando OpenAI na stack + análise custo/anonimização a definir antes de BL-G habilitar OpenAI. Default permanece Ollama (local) + Anthropic (remoto anonimizado) |

---

## 5. Boundaries — o que o CaM **NUNCA** será

> Lista vedada. Cada item aqui é resultado direto da Constituição ou do princípio de preservar capital.

- ❌ **IA enviando ordem** (Art. 35)
- ❌ **IA alterando/parametrizando Risk Engine** (Art. 35)
- ❌ **Robô MQL5 puro bypassando Risk Engine Python** (R-04)
- ❌ **Execução real automática em Fase 0–1** (Anexo II)
- ❌ **HFT / scalping de alta frequência** (latência alvo: dezenas de ms, não microssegundos)
- ❌ **No-code visual builder de estratégias no ciclo inicial** (Voltaire — vira feature factory)
- ❌ **P&L bruto como métrica operacional principal** (Art. 25)
- ❌ **Carteira Hard como margem / cobertura de loss / argumento para aumentar mão** (Art. 23)
- ❌ **Múltiplos robôs simultâneos sem risco agregado modelado** (R-08)
- ❌ **Scraping com bypass de login/CAPTCHA/ToS** (R-14)
- ❌ **`REAL_TRADING_ALLOWED=true` por default em qualquer release** (R-01)
- ❌ **Pair trade real em Fases 1-2** (Art. 12)
- ❌ **Hedge envolvendo Carteira Hard sem Risk Engine cross-asset** (R-08)

---

## 6. Filtros de decisão para qualquer feature futura

> Toda feature candidata passa estes filtros antes de virar SPEC.

### Filtros positivos (≥ 6 dos 8 devem responder SIM)

1. **Preserva capital?** A feature reduz risco, bloqueia erro ou evita ilusão operacional?
2. **Aumenta evidência?** Melhora backtest, paper, comparação ou auditoria?
3. **Reduz erro humano?** Tira decisão emocional do caminho crítico?
4. **Respeita Risk Engine?** Toda ordem ou intenção passa por `cam/_shared/risk/`?
5. **Registra tudo?** Journal, audit, fiscal e eventos ficam rastreáveis?
6. **Mostra líquido?** Qualquer resultado operacional aparece líquido de imposto?
7. **Mantém localidade?** Coerente com Linux + MT5 + cockpit local?
8. **Tem custo justificável?** Se houver mensalidade, benefício compensa sobre R$ 5.000?

### Filtros negativos (qualquer 1 SIM = bloqueio ou Out)

1. Aumenta frequência de operação antes de aumentar controle?
2. Permite ordem sem Risk Engine?
3. Depende de IA como autoridade de execução?
4. Exibe lucro bruto como métrica operacional principal?
5. Dilui CaM para competir com Status Invest, plataformas de execução ou produto multiusuário?
6. Adiciona custo recorrente sem edge mensurável?
7. Cria múltiplos robôs antes de definir exposição agregada?
8. Depende de dados externos sem qualidade, contrato ou rastreabilidade?
9. Faz Carteira Hard virar margem emocional ou trade disfarçado?

---

## 7. Linguagem operacional (tradução das respostas do Founder)

> Algumas frases do Founder em `QUESTIONS-CAM-ANALISYS.MD` precisam ser traduzidas para serem operacionalmente seguras sem trair a intenção.

| Frase original | Tradução operacional vigente |
|---|---|
| "Fazer tudo junto" | Construir **trilhas paralelas** com gates separados (SCOPE define) |
| "Não aceito esperar" | **Construir** pré-requisitos agora; **liberar operação** só por gate constitucional |
| "v1.0 com possibilidade real e demo" | Código preparado; real **travado por design** (R-01); declaração de v1.0 é do Founder |
| "N estratégias" | Registry **N-ready**, 1 estratégia ativa no início |
| "Controle total dos EAs" | EA Control Plane **progressivo e allowlistado** |
| "IA encontra padrões" | IA gera **hipóteses**; estratégia só nasce por SPEC + backtest + gates |
| "1 mês no verde com 90% de acerto" | Gate de investimento por **expectância líquida positiva + drawdown ≤ 20% + aderência ≥ 95%** (R-11) — não "% acerto" cru |
| "Tudo no CaM" | Integração **seletiva** com foco em decisão, não cópia de ferramentas |
| "Meta 15 dias primeira operação" | Construção em trilhas paralelas é viável; **execução real** depende de gates não-negociáveis (Anexo II) |
| "1 a 2 specs por dia" | Cadência alta é viável **se** cada SPEC respeitar P/M/G e gates; SCOPE prioriza |

---

## 8. Trilhas de evolução (companion SCOPE traduz em features)

| Trilha | Objetivo | Primeiro resultado útil |
|---|---|---|
| **A — Núcleo Operacional Governado** | Order Gateway único + Strategy Registry + Autonomy Matrix + Risk Engine integration | 1 estratégia em paper com journal automatizado |
| **B — EA/MT5 Control Plane** | Heartbeat, status, pause/resume, command allowlist, versão/hash; bridge read-write **demo** + `cam_risk_mirror.mq5` | Controlar EA sem enviar ordem real |
| **C — Market Data Platform** | Instrument Catalog, tick/trade/book schemas, provenance, dedupe, quality | Tick histórico confiável para S1/backtest |
| **D — AI & Research Workbench** | DataCollector real, outputs estruturados, relatórios, visualizações, pattern lab | IA analisando journal real + cross-asset |
| **E — Wealth Loop / Carteira Hard** | Holdings, importação corretora, critérios DY/fundamentalistas, valorização, dividendos, rebalance sugerido | Inventário manual + conciliação corretora |
| **F — Cross-Asset / Long & Short** | Pair trade research, spread model, Risk Engine cross-asset | Backtest/research sem operação real |

Detalhamento por trilha + dependências + ordem sugerida está em [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md).

---

## 9. Roadmap intra-SPEC (`SPEC-v0.4-VISION-EVOLUTION`)

> Toda evolução da visão cabe em **uma única SPEC** com 9 blocos. **Versões posteriores (v0.5+, v1.0) NÃO são inferidas** — Founder declara quando e como.

```
SPEC-v0.4-VISION-EVOLUTION
│
├─ BL-A  Strategy Lifecycle + Autonomy + EA Control Plane Base    [Trilha A + B parcial]
├─ BL-B  Market Data Provenance + Tick Histórico                  [Trilha C — paralelo BL-A]
├─ BL-C  Paper Loop Governado + AI Real                           [Trilha A + D — depende BL-A+B]
├─ BL-D  Carteira Hard Holdings + Importação Genial               [Trilha E — paralelo]
├─ BL-E  Read-write MT5 DEMO + cam_risk_mirror.mq5                [Trilha B G3 — depende BL-A+C]
├─ BL-F  Dividendos + Fundamentalistas + Policy Engine            [Trilha E — depende BL-D]
├─ BL-G  Cross-Asset Research + Pair Trade + AI Workbench         [Trilha D+F — depende BL-B+C+F]
├─ BL-H1 Robot Orchestrator + Multiestratégia (Art. 11-A)         [Trilha A+F — desbloqueado por EMENDA-001 v2]
├─ BL-H2 Strategy Escalation Engine (Art. 11-B)                   [Trilha A — desbloqueado por EMENDA-001 v2]
└─ BL-I  Multi-EA + DSL Strategy Layer                            [Trilha A+B — depende BL-E+H]
```

> Detalhes de cada bloco em [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md) §3 e [`SPEC-v0.4-VISION-EVOLUTION.MD`](./SPEC-v0.4-VISION-EVOLUTION.MD).

---

## 10. Gates SEC-GOV permanentes

Independente da SPEC, estes guardrails ficam **sempre** vigentes:

### 10.1 Order Gateway único

```
Strategy/Robot → Risk Engine → OrderCommand → EA MT5 → Fill → Journal/Fiscal/Audit
```

**Não pode haver `OrderSend` em MQL5 fora desse fluxo.** Lint MQL5 obrigatório para verificar.

### 10.2 Conta real travada por design

- `REAL_TRADING_ALLOWED=false` por default em **toda release**
- Conta real em allowlist explícita
- Demo e real **segregados por conta + flag + comando + banner UI + audit log**
- Testes provam impossibilidade de envio acidental para real (CA equivalente ao CA15 da SPEC v0.2)

### 10.3 Risco agregado obrigatório antes de N

Antes de qualquer SPEC habilitar N estratégias/EAs simultâneos:

- Risco agregado por conta
- Risco agregado por ativo (Art. 11 — limite absoluto)
- Risco agregado por estratégia
- Risco agregado por EA
- Limite de operações global
- Prioridade entre sinais conflitantes
- Kill switch global
- Bloqueio por drawdown global

### 10.4 Dados com provenance

Todo dado ingerido registra: **fonte, tipo, ativo, ts origem, ts ingestão, hash, qualidade, gaps, custo, uso permitido**.

### 10.5 IA read-only

IA gera relatório, JSON, score, hipótese, sugestão de SPEC, visualização. **Nunca** envia ordem, **nunca** altera risco, **nunca** habilita estratégia, **nunca** promove status no registry, **nunca** justifica exceção constitucional.

### 10.6 Supply chain MQL5

Todo `.mq5`/`.ex5` versionado, com hash registrado, origem conhecida, allowlist de artefatos. Sem path arbitrário, sem reload dinâmico antes de SPEC própria.

---

## 11. Definition of Done da SPEC `v0.4-VISION-EVOLUTION`

> Esta DoD cobre **a SPEC inteira**, não a v1.0 do CaM. **v1.0 é declaração exclusiva do Founder** — esta visão não infere quando ela acontece nem o que ela inclui.

A SPEC v0.4-VISION-EVOLUTION é considerada **entregue** quando todos os 9 blocos (BL-A a BL-I) cumprirem seus respectivos gates:

- [ ] **BL-A** entregue — Strategy Registry funcional + S1 ORB plugada + EA Control Plane G2 + Autonomy Matrix + Order Gateway único + `REAL_TRADING_ALLOWED=false` testado
- [ ] **BL-B** entregue — Market Data Import com provenance + Instrument Catalog mínimo + tick histórico WIN carregado
- [ ] **BL-C** entregue — Paper Loop Governado rodando + AI DataCollector lendo dados reais + S1 em `paper_ok`
- [ ] **BL-D** entregue — Carteira Hard com holdings manuais + importação Genial funcional
- [ ] **BL-E** entregue — Bridge read-write em DEMO + `cam_risk_mirror.mq5` + paridade Python↔MQL5 testada
- [ ] **BL-F** entregue — Dividendos + 7 indicadores fundamentalistas (R-20) + Policy Engine Carteira Hard sugestivo
- [ ] **BL-G** entregue — Cross-Asset Pattern Lab + Pair Trade Research + AI Workbench
- [ ] **BL-H** entregue — Robot Orchestrator + Risk Engine cross-asset (após emenda constitucional R-19 cumprida)
- [ ] **BL-I** entregue — Multi-EA + DSL Strategy Layer

**Garantias contínuas (sempre verdes, em toda janela):**

- [ ] Cobertura ≥ 80% backend + ≥ 70% frontend (Risk Engine ≥ 95% após BL-H)
- [ ] 0 violações de contratos `import-linter`
- [ ] `REAL_TRADING_ALLOWED=false` por default em toda release
- [ ] 3 tech debts pré-listados (TD-v0.4-01..03) viram SPECs próprias ou ficam explicitamente diferidos
- [ ] Audit log integrado em 100% dos services críticos
- [ ] Manual validation checklist atualizado por bloco

> **O que esta SPEC NÃO declara:** quando começa real trading, quando vira v1.0, quando o CaM "fica pronto". Founder declara.

---

## 12. Referências cruzadas

- [`CAM-ANALISYS.MD`](./CAM-ANALISYS.MD) — análise das 11 perguntas
- [`QUESTIONS-CAM-ANALISYS.MD`](./QUESTIONS-CAM-ANALISYS.MD) — respondido pelo Founder
- [`CAM-VISION.MD`](./CAM-VISION.MD) — visão preliminar
- [`CAM-ANALISYS-REVIEW.MD`](./CAM-ANALISYS-REVIEW.MD) — review pós-respostas
- [`SCOPE-Vision-Evolution.md`](./SCOPE-Vision-Evolution.md) — companion operacional (features, trilhas, dependências)
- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — lei suprema
- [`/project/STACK-CAM-OFICIAL.md`](../STACK-CAM-OFICIAL.md) — stack canônica (Linux + MT5)
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — parâmetros operacionais
- [`/project/strategies/EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) — tese S1 (ORB 60m WIN)

---

> **Princípio operacional final:**
>
> O CaM existe para impedir que o operador quebre quando estiver convicto demais.
>
> Esta visão amplia ambição **sem trair governança**: arquitetura preparada para tudo o que Carlos descreveu, operação inicial estreita o suficiente para sobreviver ao próprio entusiasmo.
>
> Construir amplo. Liberar estreito. Constituição vence.

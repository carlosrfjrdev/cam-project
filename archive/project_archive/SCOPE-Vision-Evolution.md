---
template: SCOPE-EVOLUTION
phase: DISC
status: Vigente
version: 1.1
date: 2026-05-27
companion_of: CAM-VISION-FINAL.MD
orchestrator: Leo
target_spec: SPEC-v0.4-VISION-EVOLUTION.MD
revision_note: >
  v1.1 — Founder consolidou todos os "v0.X" propostos em SPEC única
  v0.4-VISION-EVOLUTION; cada antigo "v0.X" vira BLOCO da mesma SPEC.
  v1.0 fica sob declaração exclusiva do Founder (sem inferência).
---

# SCOPE-Vision-Evolution — Escopo evolutivo do CaM (SPEC v0.4-VISION-EVOLUTION)

> **Função:** companion operacional da [`CAM-VISION-FINAL.MD`](./CAM-VISION-FINAL.MD). Traduz a visão em **features classificadas (in/out/later)**, **trilhas paralelas**, **dependências cruzadas** e **blocos da SPEC v0.4-VISION-EVOLUTION**.
>
> **Não é SPEC.** É o backlog estruturado que alimenta a [`SPEC-v0.4-VISION-EVOLUTION.MD`](./SPEC-v0.4-VISION-EVOLUTION.MD).
>
> **Atualização v1.1 (decisão Founder 2026-05-27):**
>
> - Numeração antiga (v0.4, v0.4b, v0.5, v0.5b, v0.6, v0.6b, v0.7, v0.8, v0.9) **revogada**.
> - Tudo passa a ser **uma única SPEC** = `SPEC-v0.4-VISION-EVOLUTION.MD`.
> - Cada antiga "versão" vira um **BLOCO** dessa SPEC.
> - Versões futuras (v0.5+, v1.0) **não são inferidas** — Founder declara.

---

## 1. Princípio de organização

```
6 Trilhas paralelas (A-F)
× 30 features candidatas (F-01..F-30)
× 4 categorias (In v0.4 / In v0.5+ / Later / Out)
× Gates SEC-GOV permanentes (CAM-VISION-FINAL §10)
```

**Regra fundadora:** trilhas são **paralelas** (Carlos disse "fazer tudo junto" — entregue como construção paralela). Mas **operação inicial é estreita** (v1.0 paper + capacidade real latente).

---

## 2. Mapa de trilhas (alvo SPEC v0.4-VISION-EVOLUTION)

| Trilha | Foco | Blocos | Pré-requisito mínimo |
|---|---|---|---|
| **A — Núcleo Operacional Governado** | Strategy Registry + Order Gateway + Autonomy Matrix | BL-A, BL-C, BL-H1, BL-H2 | Nenhum (base) |
| **B — EA/MT5 Control Plane** | Pause/Resume, versão+hash, bridge R/W demo, risk_mirror | BL-A (parcial), BL-E | BL-A |
| **C — Market Data Platform** | Instrument Catalog, tick/trade/book, provenance, quality | BL-B | Nenhum (paralelo) |
| **D — AI & Research Workbench** | DataCollector real, outputs estruturados, pattern lab | BL-C, BL-G | Trilha C parcial |
| **E — Wealth Loop / Carteira Hard** | Holdings, dividendos, fundamentalistas, rebalance sugerido | BL-D, BL-F | Nenhum (paralelo) |
| **F — Cross-Asset / Long & Short** | Pair trade research, spread model, Risk Engine cross-asset | BL-G, BL-H1 | Trilha C + E |

---

## 3. Features candidatas — Catálogo completo classificado

### 3.1 BL-A — Strategy Lifecycle + Autonomy Matrix + EA Control Plane Base

| ID | Feature | Trilha | Por que aqui | Bloqueia |
|---|---|---|---|---|
| **F-01** | Strategy Registry (N-ready) | A | Sem registry, nenhuma estratégia tem status auditável | F-02, F-05, F-07, F-15 |
| **F-02** | S1 ORB 60m WIN como estratégia plugável | A | S1 aprovada pelo Founder (R-18); primeira candidata | F-05, F-07 |
| **F-03** | Backtest P&L real por tick scanning + runs persistidos | A | TD-011 + TD-015 — backtest hoje não calcula P&L real | F-05 |
| **F-05** | Evidence Pack por estratégia | A | Conecta Art. 28 a artefato verificável | F-07 promoção |
| **F-08** | EA Control Plane G2 (PAUSE_EA, RESUME_EA, versão+hash) | B | Carlos pediu "controle total dos EAs" | F-07 |
| **F-13** | Autonomy Matrix (ambiente × modo) | A | R-02 — sem matriz, "full automatic" vira ambiguidade | F-07 |
| **F-31** | Order Gateway único (forçado por design) | A | SEC-GOV permanente §10.1 | Tudo que toca ordem |
| **F-32** | `REAL_TRADING_ALLOWED=false` + allowlist | A | R-01 + SEC-GOV §10.2 | Tudo |

### 3.2 BL-B — Market Data Provenance + Tick Histórico

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-04** | Market Data Import Wizard com provenance | C | Sem dado real, backtest é teatro (alimenta F-02 BL-A) |
| **F-19** | Market Data Provenance (núcleo) | C | Provenance robusto desde o início |
| **F-33** | Instrument Catalog mínimo (WIN/WDO + extensível) | C | Universo amplo declarado; começa simples |

### 3.3 BL-C — Paper Loop Governado + AI Real

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-06** | Paper Trading Ledger persistido | A | TD-022 — paper sem histórico não sustenta decisão |
| **F-07** | Loop Governado Paper/Demo (tick → strategy → risk → fill) | A+B | Primeiro robô funcional em paper |
| **F-09** | AI Analyst com DataCollector Real | D | TD-016 — IA hoje analisa vazio |
| **F-16** | Strategy Registry N-ready (refinamento) | A | Suporte a múltiplas registradas (1 ativa) |

### 3.4 BL-D — Carteira Hard Holdings + Importação Genial

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-10** | Carteira Hard Holdings (manual via UI) | E | Carlos respondeu: "manual + importação para conciliação" |
| **F-10b** | Importação corretora **Genial** (R-17) | E | Conciliação de extrato de ações/FII |

### 3.5 BL-E — Read-write MT5 DEMO + `cam_risk_mirror.mq5`

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-12** | Bridge read-write em DEMO + `cam_risk_mirror.mq5` | B | Ensaio controlado de automação sem capital real (Genial DEMO MT5) |

### 3.6 BL-F — Dividendos + Fundamentalistas + Policy Engine

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-11** | Dividendos/JCP — manual + scraping múltiplo | E | Carlos pediu "scraping múltiplo"; depende F-10 |
| **F-22** | Fundamental Data Module (7 indicadores R-20) | E | Carlos pediu "tudo no CaM" + 7 indicadores |
| **F-24** | Carteira Hard Policy Engine (DY + critérios) | E | Critérios sugestivos + alertas (R-13) |
| **F-26** | Dividends Multi-Source Collector (governado) | E | Scraping com cache, rate limit, ToS — escopo TD R-21 |

### 3.7 BL-G — Cross-Asset Research + Pair Trade + AI Workbench

| ID | Feature | Trilha | Quando |
|---|---|---|---|
| **F-20** | Book/Tape Collector (canal `mt5.book`) | C | Schema preparado, ativado quando EA publicar book |
| **F-21** | AI Research Workbench (visualização + pattern lab) | D | Após F-09 estável |
| **F-23** | Cross-Asset Pattern Lab (ações ↔ derivativos) | D+F | Carlos: "padrões em 5/10 ações que afetam derivativo" |
| **F-25** | Rebalance Suggestion Engine | E | Sugestão, nunca execução (R-13) |
| **F-27** | Pair Trade Research Module | F | Research/backtest, sem operação real |
| **F-30** | Remote AI Provider Governance (Anthropic — OpenAI fica TD) | D | OpenAI fica TD R-22 até ADR formal |

### 3.8 BL-H1 — Robot Orchestrator + Multiestratégia (Art. 11-A)

> EMENDA-001 v2 ratificada em 2026-05-27 — Constituição v1.1 vigente. Desbloqueado.

| ID | Feature | Trilha | Pré-requisito |
|---|---|---|---|
| **F-15** | Robot Orchestrator (com conflict resolver POV §3.11) | A | EMENDA-001 v2 ✅ |
| **F-15b** | `aggregate_risk_check` validator (Art. 11-A) | A | EMENDA-001 v2 ✅ |
| **F-28** | Cross-Asset Risk Engine Extension | A+F | Necessário antes de L&S real ou hedge |
| **F-29** | Feed Investment Gate (R-11 — expectância+drawdown) | C+E | Define quando feed pago é justificado |

### 3.8b BL-H2 — Strategy Escalation Engine (Art. 11-B)

> NOVO bloco resultante da decomposição (recomendação Leo + Marty na emenda v2).

| ID | Feature | Trilha | Pré-requisito |
|---|---|---|---|
| **F-15c** | `scaling.py` — `compute_scaling_eligibility` (Pure Python) | A | EMENDA-001 v2 ✅ + BL-H1 estável |
| **F-15d** | Job APScheduler — elegibilidade pós-pregão + evento `ScalingEligibilityReady` | A | F-15c |
| **F-15e** | `cam_constitutional_scaling_events` schema + repository | A | F-15c |
| **F-15f** | UI Risk Console — histograma de tentativas-bloqueadas | A | F-15c |
| **F-15g** | `max_contracts_check` refatorado: `get_current_limits()` em vez de hardcoded | A | F-15c (Art. 11-B) |
| **F-15h** | Diretório `/project/cam-constitution/escalonamentos/` + workflow | A | EMENDA-001 v2 ✅ |

### 3.9 BL-I — Multi-EA + DSL Strategy Layer

| ID | Feature | Trilha | Por que aqui |
|---|---|---|---|
| **F-14** | EA Control Plane G4 (multi-EA simultâneo) | B | Exige risco agregado modelado (BL-H entregue) |
| **F-17** | DSL Strategy Layer | A | Depois do contrato Python estar maduro + estratégias provadas |
| **F-18** | Instrument Catalog amplo (200+ ativos) | C | Universo amplo declarado — habilitado por demanda |

### 3.10 Out — explicitamente fora desta SPEC

| Item | Razão |
|---|---|
| IA enviando ordem | Art. 35 — vedado constitucionalmente |
| MQL5 puro decidindo ordem fora do Risk Engine | R-04 + Art. 15 |
| Execução real automática em Fase 0–1 | Anexo II + Art. 28 |
| No-code visual builder | Voltaire — vira feature factory |
| HFT / scalping de alta frequência | Não é o domínio do CaM |
| Produto comercial / SaaS | CC.1 — Founder marcou "decisão futura" |
| Reload dinâmico de EA sem allowlist | SEC-GOV §10.6 |
| Múltiplos robôs simultâneos sem emenda + risco agregado | R-19 (emenda) + R-08 (risco agregado) |
| Scraping com bypass de login/CAPTCHA/ToS | R-14 |
| OpenAI sem ADR formal | R-22 — fica como tech debt |

### 3.11 Tech debts derivados das decisões

| ID | TD | Origem | Bloqueia |
|---|---|---|---|
| **TD-v0.4-01** | Scraping multi-fonte — definir fontes, ToS, rate limit, schema canônico | R-21 (decisão "TD a definir") | BL-F (F-26 com governança) |
| **TD-v0.4-02** | OpenAI provider — ADR + SPEC + análise custo/anonimização | R-22 (decisão "TD a definir") | BL-G (F-30 com OpenAI) |
| ~~TD-v0.4-03~~ | ~~Emenda constitucional Multiestratégia~~ | ~~R-19~~ | **✅ RESOLVIDO 2026-05-27 — EMENDA-001 v2 ratificada** (Constituição v1.1). BL-H decomposto em BL-H1+BL-H2. |

---

## 4. Dependências cruzadas — Blocos da SPEC v0.4-VISION-EVOLUTION

```
SPEC-v0.4-VISION-EVOLUTION
│
├─ BL-A — Strategy Lifecycle + Autonomy + EA Control Plane Base
│   ├─ F-01 Strategy Registry
│   ├─ F-02 S1 ORB (aprovada R-18)
│   ├─ F-03 Backtest P&L real
│   ├─ F-05 Evidence Pack
│   ├─ F-08 EA Control Plane G2
│   ├─ F-13 Autonomy Matrix
│   ├─ F-31 Order Gateway único
│   └─ F-32 REAL_TRADING_ALLOWED=false
│
├─ BL-B — Market Data Provenance + Tick Histórico  [paralelo a BL-A]
│   ├─ F-04 Market Data Import
│   ├─ F-19 Provenance
│   └─ F-33 Instrument Catalog mínimo
│
├─ BL-C — Paper Loop Governado + AI Real          [depende BL-A + BL-B]
│   ├─ F-06 Paper Trading Ledger
│   ├─ F-07 Paper Loop Governado
│   ├─ F-09 AI DataCollector Real
│   └─ F-16 Registry refinement
│
├─ BL-D — Carteira Hard Holdings + Genial         [paralelo a BL-C]
│   ├─ F-10 Carteira Hard Holdings
│   └─ F-10b Importação Genial (R-17)
│
├─ BL-E — Read-write MT5 DEMO + risk_mirror       [depende BL-A + BL-C]
│   └─ F-12 Bridge R/W DEMO + cam_risk_mirror.mq5
│
├─ BL-F — Dividendos + Fundamentalistas + Policy  [depende BL-D]
│   ├─ F-11 Dividendos
│   ├─ F-22 Fundamentalistas (R-20 — 7 indicadores)
│   ├─ F-24 Carteira Hard Policy Engine
│   └─ F-26 Dividend Collector (escopo TD-v0.4-01)
│
├─ BL-G — Cross-Asset Research + Pair Trade       [depende BL-B + BL-C + BL-F]
│   ├─ F-20 Book/Tape Collector
│   ├─ F-21 AI Research Workbench
│   ├─ F-23 Cross-Asset Pattern Lab
│   ├─ F-25 Rebalance Suggestion
│   ├─ F-27 Pair Trade Research
│   └─ F-30 Remote AI Governance (Anthropic / OpenAI fica TD-v0.4-02)
│
├─ BL-H — Robot Orchestrator + Risk Cross-Asset   [exige TD-v0.4-03 emenda]
│   ├─ F-15 Robot Orchestrator (após emenda multiestratégia R-19)
│   ├─ F-28 Cross-Asset Risk Engine Extension
│   └─ F-29 Feed Investment Gate
│
└─ BL-I — Multi-EA + DSL Strategy Layer           [depende BL-E + BL-H]
    ├─ F-14 EA Control Plane G4 (multi-EA)
    ├─ F-17 DSL Strategy Layer
    └─ F-18 Instrument Catalog amplo
```

> **Nota:** todos esses blocos pertencem à **mesma SPEC** (`SPEC-v0.4-VISION-EVOLUTION.MD`). Versões posteriores (v0.5+, v1.0) **não são declaradas neste SCOPE** — Founder decide quando e como.

---

## 5. Resumo executivo dos 9 blocos (SPEC v0.4-VISION-EVOLUTION)

> **SPEC única.** Cada bloco tem P/M/G + marcadores próprios, mas governança e gate Founder são únicos para a SPEC inteira.

| Bloco | Foco | Features | P/M/G | sec/qa-sec | Pré-requisito |
|---|---|---|---|---|---|
| **BL-A** | Strategy Lifecycle + Autonomy + EA Control Plane Base | F-01, F-02, F-03, F-05, F-08, F-13, F-31, F-32 | G | sec + qa-sec | — |
| **BL-B** | Market Data Provenance + Tick Histórico | F-04, F-19, F-33 | M | qa-sec | — (paralelo) |
| **BL-C** | Paper Loop Governado + AI Real | F-06, F-07, F-09, F-16 | G | sec + qa-sec | BL-A + BL-B |
| **BL-D** | Carteira Hard Holdings + Importação Genial | F-10, F-10b | M | — | — (paralelo) |
| **BL-E** | Read-write MT5 DEMO + risk_mirror | F-12 | G | sec + qa-sec **crítico** (1º envio ordem mesmo demo) | BL-A + BL-C + S1 paper ≥ 30 dias |
| **BL-F** | Dividendos + Fundamentalistas + Policy Engine | F-11, F-22, F-24, F-26 | G | qa-sec (scraping — TD-v0.4-01) | BL-D |
| **BL-G** | Cross-Asset Research + Pair Trade + AI Workbench | F-20, F-21, F-23, F-25, F-27, F-30 | G | qa-sec + ADR OpenAI (TD-v0.4-02) | BL-B + BL-C + BL-F |
| **BL-H** | Robot Orchestrator + Risk Engine Cross-Asset | F-15, F-28, F-29 | G | sec + qa-sec **+ emenda constitucional** (TD-v0.4-03) | BL-E + BL-G |
| **BL-I** | Multi-EA + DSL Strategy Layer | F-14, F-17, F-18 | G | sec | BL-E + BL-H |

> **Total:** 9 blocos · 30 features (F-01..F-33, sem F-10b duplicado) · 3 tech debts pré-listados.

---

## 6. Cadência de execução intra-SPEC

> "Fazer tudo junto" (resposta CC.2) traduzido em **trilhas paralelas dentro da mesma SPEC**. Founder mantém cadência alta sem violar pré-requisitos.

| Janela | Blocos executados em paralelo | Risco |
|---|---|---|
| **Janela 1** | BL-A + BL-B + BL-D | Baixo — trilhas A + C + E independentes |
| **Janela 2** | BL-C + BL-F | Baixo — depende de BL-A/B/D entregues |
| **Janela 3** | BL-E + BL-G | Médio — BL-E tem `sec` **crítico** (1º envio ordem demo) |
| **Janela 4** | BL-H | Alto — exige **emenda constitucional** (TD-v0.4-03) + risco agregado |
| **Janela 5** | BL-I | Alto — DSL + multi-EA exigem BL-E + BL-H estáveis |

> **Compromisso:** cada janela tem seu próprio gate intermediário do Founder antes da próxima janela iniciar.

---

## 7. Decisões resolvidas pelo Founder (2026-05-27)

> Estas decisões saíram pendentes do round anterior e foram resolvidas. Permanecem **vigentes** até nova decisão.

| ID | Decisão | Resolvido como | Impacto |
|---|---|---|---|
| **D-S1** | Aprovar formalmente S1 ORB 60m WIN? | **APROVADO** (R-18) | F-02 entra em BL-A |
| **D-Corretora** | Qual corretora vinculada? | **Genial Investimentos** (R-17) | F-10b importação Genial em BL-D; BL-E usa Genial DEMO MT5 |
| **D-Multi-Estratégia** | Emenda constitucional permitindo N? | **APROVADO COM EMENDA** (R-19) | Vira TD-v0.4-03 (texto emenda + cooldown 30d) — bloqueia BL-H |
| **D-Fundamentais-Lista** | Lista oficial dos 7 indicadores | **Inferida** (R-20): DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC | F-22 em BL-F usa essa lista |
| **D-Scraping-Fontes** | Quais fontes permitidas | **Vira TD-v0.4-01** (R-21) | F-26 em BL-F tem governança como TD |
| **D-OpenAI** | ADR aceitando OpenAI | **Vira TD-v0.4-02** (R-22) | F-30 em BL-G ativa OpenAI só após ADR; default permanece Ollama + Anthropic |
| **D-Tick-Source** | Fonte de tick histórico inicial | Importação CSV/Parquet pela Genial (via MT5) — confirmado em TODO-OPERACIONAL OP-003 | F-04 em BL-B |

---

## 8. Gates SEC-GOV por Bloco (lente Kevin)

| Bloco | Gates SEC-GOV mandatórios |
|---|---|
| BL-A | Order Gateway forçado em código + lint MQL5 + `REAL_TRADING_ALLOWED` testado |
| BL-B | Provenance obrigatório + parsing safe (HTML/CSV) + hash de lote |
| BL-C | Paper segregado de DB live + audit em cada fill paper |
| BL-D | Holdings nunca contam como margem (assert estrutural) + importação Genial sanitizada |
| **BL-E** | **Crítico** — segregação demo/real triplicada + `cam_risk_mirror.mq5` com testes de paridade + kill switch E2E demo + idempotency key |
| BL-F | Scraping com User-Agent identificado + rate limit + cache + auditoria de ToS (escopo TD-v0.4-01) |
| BL-G | OpenAI bloqueado até ADR (TD-v0.4-02) + anonimização de dados sensíveis + ContentGuard estendido para outputs estruturados |
| **BL-H** | **Crítico** — emenda constitucional cumprida (TD-v0.4-03) + risco agregado property-based testado + cooldown 30 dias antes do release |
| BL-I | DSL compila para Python canonical (lint-imports verifica) + multi-EA com mutex de execução |

---

## 9. Mudanças em documentos existentes (após VISION-FINAL aprovada)

> Lista de docs que precisam update para refletir a VISION-FINAL.

| Doc | Update necessário |
|---|---|
| `STACK-CAM-OFICIAL.md` | Adicionar nota: "OpenAI exige ADR antes de entrar (R-15)" |
| `POV-VIGENTE-v1.0.md` | Acrescentar §3.11 — Política patrimonial Carteira Hard (após v0.5b) |
| `GATE-FASE-0-PARA-1.md` | Adicionar item: "Strategy Registry com S1 em `paper_ok`" |
| `MAPPING-CONSTITUICAO-RISK-ENGINE.md` | Adicionar mapping de cross-asset risk (após v0.8) |
| `TECH-DEBT.md` | TD-013 (walk-forward multi) marcado como "alvo v0.4 expandido" |
| `RUNBOOK-INCIDENTE-TECNICO.md` | Adicionar cenários de read-write demo (após v0.6) |
| `EDGE-THESIS-S1.md` | Aguarda gate Founder §11 |

---

## 10. Métricas de sucesso da SPEC v0.4-VISION-EVOLUTION

> Métricas que indicam que cada bloco entregou o que prometeu. **Sem inferência de v1.0** — o release v1.0 é declaração exclusiva do Founder.

| Métrica | Alvo intra-SPEC | Verificado em |
|---|---|---|
| Cobertura backend total | ≥ 80% (mantém atual) | toda janela |
| Cobertura Risk Engine | ≥ 95% (sobe de ~88% atual) | BL-A + BL-H |
| Cobertura frontend | ≥ 70% | BL-A + BL-C + BL-D + BL-F |
| Contratos `import-linter` | 0 violations | toda janela |
| Tempo de subida do ambiente | ≤ 60s | BL-A |
| Testes property-based (Hypothesis) | ≥ 50.000 casos | BL-A + BL-H |
| Latência Risk Engine validate | ≤ 5ms p99 | BL-A + BL-H |
| Latência bridge ZeroMQ heartbeat | ≤ 50ms p99 | BL-E |
| Estratégias no registry | ≥ 1 com S1 em `paper_ok` | BL-C |
| Backtest runs persistidos | ≥ 10 (S1 + variações de parâmetros) | BL-A |
| Operações paper completas | ≥ 100 | BL-C |
| Aderência operacional paper | ≥ 95% (Art. 29) | BL-C |
| Carteira Hard holdings registradas | ≥ 1 | BL-D |
| Audit log integrado | 100% dos services críticos | BL-A + BL-C + BL-E |
| Tech debts ativos resolvidos | TD-v0.4-01..03 viram SPECs próprias (futuras) | BL-F + BL-G + BL-H |

---

## 11. Anti-padrões a evitar durante execução

> Riscos que apareceram nas respostas do Founder e precisam ser **explicitamente evitados** nas SPECs.

| Anti-padrão | Sintoma | Mitigação |
|---|---|---|
| **"Acelerar pulando gate"** | "Não aceito esperar" virar SPEC sem QA | Cadência alta com **gates intactos**; speed via paralelismo de trilhas |
| **"Tudo junto"** | Release operacional único com 30 features | Trilhas paralelas mas SPECs **independentes** |
| **"N estratégias já"** | Múltiplas estratégias ativas sem risco agregado | Registry N-ready, **1 ativa** — emenda Art. 28 antes de N |
| **"IA decide"** | Robô = IA = decide | Robô é **estratégia codada** (regra determinística) ≠ IA. Distinção crítica |
| **"Métrica % acerto"** | "1 mês com 90% acerto" | Expectância líquida + drawdown + aderência (R-11) — % acerto isolado é miragem |
| **"Tudo no CaM"** | Reimplementar Status Invest | Integração **seletiva** com foco em decisão cross-asset, não cópia |
| **"Real na v1.0"** | `REAL_TRADING_ALLOWED=true` por default | Travada por design (R-01) — release v1.0 = paper + latente |
| **"Múltiplos EAs operando"** | EA Control Plane G4 antes do tempo | G2 (pause/resume) primeiro, G3 (R/W demo) segundo, G4 só depois |

---

## 12. Compromissos vigentes (vinculam todas as SPECs futuras)

> Cada nova SPEC v0.4+ **declara** que respeita estes compromissos. Quem violar, abre BUG/issue.

1. **Risk Engine intocado** exceto para extensões aditivas (validators novos, sem remover existentes).
2. **Order Gateway único** — todo path de ordem passa pelo mesmo caminho.
3. **`REAL_TRADING_ALLOWED=false`** por design em toda release.
4. **1 estratégia ativa** em produção (registry N-ready, operação 1-first).
5. **Bridge MQL5 = mirror/executor** — nunca decide ordem fora do Risk Engine.
6. **IA read-only** — output estruturado, sem promoção automática.
7. **Carteira Hard = patrimônio**, nunca margem.
8. **Provenance em todo dado** ingerido.
9. **Audit trail em todo evento operacional**.
10. **Cooldown constitucional respeitado** em qualquer mudança de POV ou Constituição.
11. **Demo/Real segregados** por conta + flag + comando + banner UI + audit log.
12. **TDD First** em toda TASK de CODE.

---

## 13. Próxima ação

> Decisões do Founder (2026-05-27) consolidadas:
> - Corretora: **Genial** (R-17)
> - S1 ORB: **aprovada** (R-18)
> - Multiestratégia: **aprovada com emenda** (R-19 → TD-v0.4-03)
> - Indicadores: **lista inferida** (R-20)
> - Scraping: **TD a definir** (R-21 → TD-v0.4-01)
> - OpenAI: **TD a definir** (R-22 → TD-v0.4-02)

**Pronto para Leo invocar Albert + Nico para emitir [`SPEC-v0.4-VISION-EVOLUTION.MD`](./SPEC-v0.4-VISION-EVOLUTION.MD) cobrindo os 9 blocos (BL-A a BL-I).**

Sequência sugerida de execução:

| Janela | Blocos | Aprovação Founder |
|---|---|---|
| 1 | BL-A + BL-B + BL-D | Após PLAN |
| 2 | BL-C + BL-F | Após Janela 1 + gate intermediário |
| 3 | BL-E + BL-G | Após Janela 2 + gate intermediário + TD-v0.4-02 (OpenAI ADR) se BL-G usar |
| 4 | BL-H | Após Janela 3 + emenda constitucional cumprida (TD-v0.4-03) |
| 5 | BL-I | Após Janela 4 + cooldown |

> Cada janela tem **gate Founder intermediário**. A SPEC inteira tem **gate Founder único** ao final (Definition of Done da SPEC, não da v1.0).

---

## Referências cruzadas

- [`CAM-VISION-FINAL.MD`](./CAM-VISION-FINAL.MD) — visão final
- [`CAM-ANALISYS.MD`](./CAM-ANALISYS.MD) — análise inicial 11 perguntas
- [`QUESTIONS-CAM-ANALISYS.MD`](./QUESTIONS-CAM-ANALISYS.MD) — respostas Founder
- [`CAM-VISION.MD`](./CAM-VISION.MD) — visão preliminar (superseded por VISION-FINAL)
- [`CAM-ANALISYS-REVIEW.MD`](./CAM-ANALISYS-REVIEW.MD) — review pós-respostas
- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — lei suprema
- [`/project/STACK-CAM-OFICIAL.md`](../STACK-CAM-OFICIAL.md) — stack canônica
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — POV operacional
- [`/project/strategies/EDGE-THESIS-S1.md`](../strategies/EDGE-THESIS-S1.md) — S1 (pendente aprovação)
- [`/project/CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) — corretoras

---

> **Princípio operacional final deste SCOPE:**
>
> Trilhas paralelas. Cadência alta. Gates intactos. 1 ativa, N-ready.
>
> A ambição da visão cabe se cada SPEC respeitar seu próprio gate. **A pressa é o inimigo silencioso** — paralelismo é resposta legítima; bypass não é.

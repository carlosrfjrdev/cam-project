---
template: SPEC
phase: SPEC
status: Draft
version: 0.3
date: 2026-05-25
parent_spec: SPEC-v0.2-MT5-ENQUADRAMENTO.md
demand_id: SPEC-v0.3
pmg: M
sec: false
qa_sec: false
review_target: apps/cam-cockpit/TECH-DEBT.md
---

# SPEC v0.3 — Review do TECH-DEBT.md (auditoria + saneamento)

> **Lead:** Albert (especificação) · **Co-lead:** Linus (auditoria QA)
> **Skill:** `teczi-demand-specification`
> **Aprovador:** Founder
> **Alvo:** [`apps/cam-cockpit/TECH-DEBT.md`](../TECH-DEBT.md) — 36 entradas vigentes
>
> **Origem:** "vamos validar os débitos técnicos... avalie ele novamente e vamos verificar o que dá para sanar já agora" — Founder, 2026-05-25.

---

## 1. Contexto e propósito

O `TECH-DEBT.md` foi crescendo orgânicamente ao longo dos Blocos A–H da v0.1 e ganhou 9 entradas novas na v0.2 (TD-v0.2-01..09). Como **3 TDs foram resolvidos durante a correção de bugs do Bloco MT5** e **3 TDs ficaram CONGELADOS pela R20.05 da SPEC v0.2.1** (sem que o documento fosse atualizado), o ledger está em **drift** com o estado real.

Esta SPEC produz **auditoria sistemática** dos 36 TDs vigentes, classifica cada um em 4 categorias e propõe um **PLAN saneador** com TASKs para os que podem ser resolvidos agora sem expandir escopo arquitetural.

### O que esta SPEC **é**

- Auditoria 1-a-1 dos 36 TDs com decisão explícita por TD.
- Lista priorizada de TDs sanáveis nesta janela (sem mudança de DAS/ADR).
- Atualização formal do `TECH-DEBT.md` para refletir o estado real (RESOLVIDO / CONGELADO / OBSOLETO / MANTIDO).
- Base para PLAN v0.3 com TASKs T-TD-{N}.

### O que esta SPEC **não é**

- Não cria novos tech debts (eles vêm de SPECs de feature).
- Não revoga decisões arquiteturais — TDs que exigem mudança de DAS são MANTIDOS-ATIVOS para SPECs futuras.
- Não toca a Constituição nem a POV.
- Não muda a stack (MT5 + Linux confirmado em DECISION-MEMO §6).

---

## 2. Princípio de classificação

Cada TD recebe **exatamente uma** classificação:

| Status | Significado | Ação na auditoria |
|---|---|---|
| **RESOLVIDO** | A condição que justificava o TD não existe mais no código. | Remover do TECH-DEBT.md ou marcar como histórico. |
| **CONGELADO** | TD continua existindo mas a feature alvo foi desativada (SPEC v0.2.1 R20). Não há trabalho a fazer enquanto a feature estiver off. | Marcar `[CONGELADO desde 2026-05-25 — feature desativada]`. |
| **SANAR-AGORA** | TD ainda válido + correção cabe nesta janela (sem mudança de DAS/ADR). | Vira TASK T-TD-{N} no PLAN. |
| **MANTIDO-ATIVO** | TD ainda válido + correção exige escopo maior (DB real, nova feature, decisão Founder, etc). | Permanece no ledger com data de revisão futura. |

---

## 3. Auditoria 1-a-1 — TDs herdados da v0.1 (TD-001 a TD-027)

> Tabela canônica. Cada linha é uma decisão registrada.

| TD | Resumo | Status pós-v0.2 | Decisão SPEC v0.3 | TASK saneadora |
|---|---|---|---|---|
| **TD-001** | WIN+WIN simultâneo não bloqueado | ATIVO | **SANAR-AGORA** | T-TD-001 |
| **TD-002** | EventBus sem persistência (asyncio.Queue) | ATIVO | **MANTIDO-ATIVO** — exige Redis ou LISTEN/NOTIFY (mudança de DAS) | — |
| **TD-003** | Testes de checklists/kill_switch usam mocks (sem DB) | ATIVO | **MANTIDO-ATIVO** — exige `testcontainers-python` (decisão de stack de teste) | — |
| **TD-004** | Journal duplo JSONL sem teste de arquivo real | ATIVO | **SANAR-AGORA** | T-TD-004 |
| **TD-005** | Harvest service sem subscribe ao `DarfPaid` no lifespan | ATIVO | **SANAR-AGORA** | T-TD-005 |
| **TD-006** | `trading_window_check` com horários hardcoded WIN/WDO | ATIVO | **MANTIDO-ATIVO** — exige enriquecer POV (decisão constitucional) | — |
| **TD-007** | `profit/validate-intention` sem RiskContext real | ATIVO em v0.1 | **CONGELADO** — feature desativada por R20 da SPEC v0.2.1 | — |
| **TD-008** | `journal/import-csv` (Profit) sem DB | ATIVO em v0.1 | **CONGELADO** — feature desativada por R20 | — |
| **TD-009** | `profit/reconciliation` sem DB | ATIVO em v0.1 | **CONGELADO** — feature desativada por R20 | — |
| **TD-010** | `NotificationService` singleton em import-time | ATIVO | **SANAR-AGORA** | T-TD-010 |
| **TD-011** | `BacktestSimulator` `result_gross` sempre 0 | ATIVO | **MANTIDO-ATIVO** — exige tick scanning real (T-H07 do PLAN original — escopo M, fica para SPEC dedicada) | — |
| **TD-012** | Sharpe Ratio stub (sempre 0) | ATIVO | **SANAR-AGORA** | T-TD-012 |
| **TD-013** | Walk-forward com janela única | ATIVO | **MANTIDO-ATIVO** — exige `n_splits` + janela deslizante (parte de T-H07) | — |
| **TD-014** | DuckDB research sem instância real | ATIVO | **MANTIDO-ATIVO** — exige DuckDB instalado e config (decisão de infra) | — |
| **TD-015** | `BacktestRun` sem persistência no banco | ATIVO | **MANTIDO-ATIVO** — exige migration + `BacktestRepository` | — |
| **TD-016** | `AnalystDataCollector` lê listas vazias (sem DB) | ATIVO | **MANTIDO-ATIVO** — exige queries SQLAlchemy reais | — |
| **TD-017** | `AnthropicProvider` modelo/versão hardcoded | ATIVO | **SANAR-AGORA** | T-TD-017 |
| **TD-018** | Scheduler `ai_analyst` não ativado no lifespan | ATIVO | **MANTIDO-ATIVO** — exige aprovação Founder (gate explícito) + provider real | — |
| **TD-019** | Rotas `/analyses` e `/analyses/{date}` retornam stubs | ATIVO | **MANTIDO-ATIVO** — exige `AIAnalystRepository` (DB) | — |
| **TD-020** | `ContentGuard` sem log estruturado de violações em DB | ATIVO | **MANTIDO-ATIVO** — exige tabela `ai_analyst_violations` | — |
| **TD-021** | Frontend sem testes de integração de rota | ATIVO | **MANTIDO-ATIVO** — exige decisão sobre Playwright vs MSW (escopo de infra de teste) | — |
| **TD-022** | Paper Trading sem persistência no banco | ATIVO | **MANTIDO-ATIVO** — exige migration `cam_paper_trades` + repository | — |
| **TD-023** | `/constitution/current` retorna 404 sem seed | **RESOLVIDO TOTAL** — fallback de arquivo implementado no Bloco MT5 (`_resolve_constitution_file`) | **REMOVER** do ledger | — |
| **TD-024** | Endpoint `/settings` não implementado | **RESOLVIDO TOTAL** — implementado em `cam/api/dashboard_routes.py` (correção bugs Bloco MT5) | **REMOVER** | — |
| **TD-025** | Endpoint `/risk/status` não implementado | **RESOLVIDO TOTAL** — implementado em `dashboard_routes.py` | **REMOVER** | — |
| **TD-026** | WebSocket P&L stub | ATIVO | **SANAR-AGORA** (stub funcional emitindo zeros + flag de "real") | T-TD-026 |
| **TD-027** | Audit trail não integrado nos services | PARCIAL — `log_disabled_endpoint_attempt` integrado em `profit_integration/guard.py` (SPEC v0.2) | **SANAR-AGORA** | T-TD-027 |

### Resumo herdados v0.1

| Categoria | Quantidade |
|---|---|
| RESOLVIDO TOTAL | 3 |
| CONGELADO | 3 |
| **SANAR-AGORA** | **7** |
| MANTIDO-ATIVO | 14 |
| **Total v0.1** | **27** |

---

## 4. Auditoria 1-a-1 — TDs novos da v0.2 (TD-v0.2-01 a v0.2-09)

| TD | Resumo | Status | Decisão SPEC v0.3 | TASK |
|---|---|---|---|---|
| **TD-v0.2-01** | Bridge ZeroMQ sem autenticação | ATIVO | **MANTIDO-ATIVO** — aceito como uso local em v0.2; revisitar em v0.4 quando bridge for read-write | — |
| **TD-v0.2-02** | EA MQL5 sem testes automatizados | ATIVO | **MANTIDO-ATIVO** — limitação da plataforma; mitigar com paridade Python↔MQL5 em SPEC v0.4 | — |
| **TD-v0.2-03** | Importer HTML depende da estrutura interna do MT5 | ATIVO | **SANAR-AGORA** (parcial — adicionar samples de regressão + comentário no parser) | T-TD-v0.2-03 |
| **TD-v0.2-04** | `profit_integration/` continua compilando mesmo desativada | ATIVO | **MANTIDO-ATIVO** — preço aceito da reversibilidade R21 | — |
| **TD-v0.2-05** | Wine pode glitchar sem automação de fallback | ATIVO | **MANTIDO-ATIVO** — gatilho G-B1 cobre; automação ficaria para SPEC dedicada | — |
| **TD-v0.2-06** | Sem UI de feature flags para o Founder | ATIVO | **SANAR-AGORA** (parcial — exibir feature flags no `/settings`) | T-TD-v0.2-06 |
| **TD-v0.2-07** | Audit log de `DISABLED_ENDPOINT_ATTEMPT` sem rotação dedicada | ATIVO | **MANTIDO-ATIVO** — alinhado com retenção geral; revisitar em política unificada | — |
| **TD-v0.2-08** | Reconciliação MT5 sem persistência (stub) | ATIVO | **MANTIDO-ATIVO** — exige `JournalRepository` real (DB) | — |
| **TD-v0.2-09** | Hashes de import-report em memória (process-scoped) | ATIVO | **MANTIDO-ATIVO** — migração para DB exige tabela `cam_mt5_imports` | — |

### Resumo novos v0.2

| Categoria | Quantidade |
|---|---|
| RESOLVIDO TOTAL | 0 |
| CONGELADO | 0 |
| **SANAR-AGORA** | **2** |
| MANTIDO-ATIVO | 7 |
| **Total v0.2** | **9** |

---

## 5. Resumo da auditoria consolidada (36 TDs)

| Categoria | v0.1 | v0.2 | **Total** | % |
|---|---:|---:|---:|---:|
| RESOLVIDO TOTAL | 3 | 0 | **3** | 8% |
| CONGELADO | 3 | 0 | **3** | 8% |
| **SANAR-AGORA** | **7** | **2** | **9** | **25%** |
| MANTIDO-ATIVO | 14 | 7 | **21** | 58% |
| **TOTAL** | **27** | **9** | **36** | **100%** |

**Ganho desta SPEC:** 3 RESOLVIDOS removidos + 3 CONGELADOS marcados explicitamente + **9 SANAR-AGORA** com TASKs no PLAN = **15 movimentações** no ledger.

---

## 6. Regras (R) — desta SPEC

### R22 — Atualização obrigatória do TECH-DEBT.md

R22.01 — Após o PLAN v0.3 + CODE executados, o `TECH-DEBT.md` **DEVE** ser reescrito com a seguinte estrutura:

```markdown
# TECH-DEBT — cam-cockpit
> Atualizado em: 2026-05-25 (SPEC v0.3 — auditoria sistemática)

## Resolvidos (removidos do ledger ativo, preservados em §Resolvidos histórico)
- TD-023, TD-024, TD-025

## Congelados (feature alvo desativada — não há trabalho a fazer)
- TD-007, TD-008, TD-009 [CONGELADO desde 2026-05-25 — profit_integration desativada por SPEC v0.2.1 R20]

## Ativos
[lista dos 30 restantes]
```

R22.02 — Entradas RESOLVIDAS ganham nota de **commit/SPEC** que as resolveu (rastreabilidade).

R22.03 — Entradas CONGELADAS mantêm conteúdo original + nota "[CONGELADO em YYYY-MM-DD — motivo]".

### R23 — TDs SANAR-AGORA — escopo controlado

R23.01 — TASKs T-TD-{N} **NÃO PODEM** mudar arquitetura (DAS) nem revogar ADR vigente.

R23.02 — Cada TASK saneadora **DEVE** ter TDD First (Red → Green) e cobertura ≥ existente.

R23.03 — Se durante CODE for descoberto que a TASK saneadora exige mudança de DAS/ADR, ela **DEVE** ser **abortada** e o TD reclassificado como MANTIDO-ATIVO para SPEC futura.

### R24 — Risk Engine intocado

R24.01 — Nenhuma TASK desta SPEC pode tocar `cam/_shared/risk/` exceto para adicionar **um validator novo bem delimitado** (T-TD-001 — `total_open_contracts_check` para Art. 12º).

R24.02 — O novo validator **DEVE** entrar no pipeline na ordem correta (após `simultaneous_position_check`, antes do Grupo 3) e ter cobertura 100%.

---

## 7. TASKs sanadoras (alvo do PLAN v0.3)

> Auto-contidas. Cada TASK referencia o TD original.

### T-TD-001 — Adicionar `total_open_contracts_check` (Art. 12º implícito)

- **TD origem:** TD-001
- **Escopo:** Novo validator em `cam/_shared/risk/validators/group2_limits.py` que soma contratos abertos do mesmo ativo e bloqueia se a soma + candidato exceder o limite de fase.
- **Pipeline:** após `simultaneous_position_check` (posição 8 atual), antes do Grupo 3 (P&L).
- **Testes:** unitários + property-based (Hypothesis); atualizar `tests/test_risk_pipeline_integration.py`.
- **Marcadores:** `sec` (toca Risk Engine).

### T-TD-004 — Teste do journal duplo JSONL com `tmp_path`

- **TD origem:** TD-004
- **Escopo:** Teste em `cam/features/journal/tests/test_jsonl_fallback.py` usando `tmp_path` do pytest que valida criação do arquivo `~/.cam/journal/YYYY-MM-DD.jsonl` e que o conteúdo contém o entry serializado.
- **Marcadores:** —

### T-TD-005 — Wiring `harvest_service` ao evento `DarfPaid`

- **TD origem:** TD-005
- **Escopo:** Criar `DarfPaid` em `cam/features/fiscal/events.py` (se não existir) + publicar quando `mark_paid` é chamado + `subscribe` no `lifespan` chamando `harvest_service.handle_darf_paid`.
- **Marcadores:** —

### T-TD-010 — `NotificationService` com lazy init via factory

- **TD origem:** TD-010
- **Escopo:** Mover `notification_service = NotificationService()` do import-time para uma factory `get_notification_service()` chamada no `lifespan`. Code clients usam a factory.
- **Marcadores:** —

### T-TD-012 — Sharpe Ratio com stddev real

- **TD origem:** TD-012
- **Escopo:** `BacktestMetrics.compute()` calcula stddev dos retornos diários e Sharpe = `(mean - rf) / stddev`. CDI diário configurável via `settings.cdi_daily_rate` (default 0%). Testes com dataset conhecido.
- **Marcadores:** —

### T-TD-017 — `AnthropicProvider` lê modelo/versão de env

- **TD origem:** TD-017
- **Escopo:** Adicionar `anthropic_model`, `anthropic_api_version` em `Settings`; remover hardcode em `providers.py`.
- **Marcadores:** —

### T-TD-026 — WebSocket P&L stub funcional + flag

- **TD origem:** TD-026
- **Escopo:** `cam/api/websocket.py` envia mensagem `{"daily_pnl_gross": 0, "daily_pnl_net": 0, "open_positions": 0, "timestamp": ...}` a cada 5s. Adicionar `WEBSOCKET_PNL_REAL_DATA=false` no `.env` que, quando `true`, força backend a buscar do banco (ainda stub — placeholder para Fase 1). Frontend continua igual.
- **Marcadores:** —

### T-TD-027 — Audit log em kill_switch e bridge

- **TD origem:** TD-027
- **Escopo:** `kill_switch/service.py` chama `log_kill_switch_activated` em `activate()` e `log_kill_switch_deactivated` em `deactivate()`. `mt5_integration/service.py` chama `log_risk_decision` após cada `validate_intention`.
- **Marcadores:** —

### T-TD-v0.2-03 — Samples de regressão do importer HTML

- **TD origem:** TD-v0.2-03
- **Escopo:** Criar `cam/features/mt5_integration/tests/fixtures/mt5_report_build_{N}.html` com sample por build do MT5 testado. Cada sample gera caso em `test_importer.py`. Adiciona comentário no `importer.py` documentando dependência da estrutura.
- **Marcadores:** `qa-sec` (parsing seguro).

### T-TD-v0.2-06 — Painel de Feature Flags em `/settings`

- **TD origem:** TD-v0.2-06
- **Escopo:** Endpoint `GET /api/v1/settings` retorna campo novo `feature_flags: {profit_integration_enabled, mt5_integration_enabled}`. Frontend `SettingsPage` exibe painel "Feature Flags Ativas" lendo do `/settings`.
- **Marcadores:** —

---

## 8. Critérios de aceite (CA)

### CA21 — TECH-DEBT.md auditado e atualizado

- **CA21.1:** TECH-DEBT.md tem nova seção "Resolvidos" com TD-023, TD-024, TD-025 + nota de quando/onde foram resolvidos.
- **CA21.2:** TDs CONGELADOS (TD-007, TD-008, TD-009) têm prefixo `[CONGELADO desde 2026-05-25 — feature desativada por SPEC v0.2.1 R20]` no título.
- **CA21.3:** Cabeçalho do documento atualizado: `Atualizado em: 2026-05-25 (SPEC v0.3 — auditoria sistemática)`.
- **CA21.4:** Cada TASK T-TD-{N} executada **remove** o respectivo TD da lista ATIVOS (ou move para "Resolvidos").

### CA22 — TDs SANAR-AGORA executados sem regressão

- **CA22.1:** Backend continua com **≥ 425 testes passando** (cobertura atual pré-v0.3).
- **CA22.2:** Cada T-TD-{N} adiciona pelo menos **1 teste novo** (TDD First).
- **CA22.3:** `lint-imports` continua **2 kept / 0 broken**.
- **CA22.4:** Risk Engine continua com cobertura ≥ 80%.

### CA23 — Validator novo (T-TD-001) integrado no pipeline

- **CA23.1:** `total_open_contracts_check` aparece na lista `VALIDATORS` em `cam/_shared/risk/engine.py` na posição correta (após `simultaneous_position_check`).
- **CA23.2:** Property-based test confirma: nunca aprova candidato cuja soma `current_open_contracts(asset) + candidato.contracts > phase_limit(fase, asset)`.
- **CA23.3:** Atualização correspondente em `MAPPING-CONSTITUICAO-RISK-ENGINE.md` (Art. 12º — explícito coberto).

### CA24 — Audit trail integrado (T-TD-027)

- **CA24.1:** Após `POST /api/v1/kill-switch/activate`, `~/.cam/logs/cam-audit.log` registra `event_type=KILL_SWITCH_ACTIVATED`.
- **CA24.2:** Após `POST /api/v1/mt5/validate-intention`, registra `event_type=RISK_DECISION`.

---

## 9. P/M/G

| Campo | Valor |
|---|---|
| **Classe** | **M (Médio)** |
| **Rationale** | 9 TASKs auto-contidas, sem mudança de arquitetura, sem novas features. Cada uma toca um arquivo (raramente dois) e adiciona testes. Maior risco: T-TD-001 toca Risk Engine, mas é validator adicional sem mudar pipeline existente. P seria injusto (são 9 TASKs); G seria overengineering (não decompõe em blocos). |
| **Albert** | M confirmada |
| **Nico (PLAN futuro)** | Loop livre |

---

## 10. Marcadores SEC / QA-SEC

| Marcador | Valor | Razão |
|---|---|---|
| `sec` | **false (no nível SPEC)** | Apenas T-TD-001 toca Risk Engine (auditor Kevin no CODE dessa TASK). Demais TASKs são saneamento de stubs/wiring. |
| `qa-sec` | **false (no nível SPEC)** | Apenas T-TD-v0.2-03 (samples regressão parser HTML) tem componente qa-sec local. |

> **Decisão:** marcar SPEC como sem `sec/qa-sec` globais; aplicar marcadores **por TASK** no PLAN v0.3.

---

## 11. Riscos identificados

| Risco | Mitigação |
|---|---|
| T-TD-001 introduz comportamento que quebra strategies já validadas | Property-based testing + flag default `False` em `RiskContext.enforce_total_open_contracts` para rollout gradual; ativar via emenda formal |
| Wiring de `DarfPaid` (T-TD-005) gera loop infinito (harvest aciona darf?) | DarfPaid → harvest_recalc é unidirecional por design; teste de regressão explícito |
| Lazy init do `NotificationService` (T-TD-010) quebra subscribers já registrados | Refatorar subscribe no lifespan junto, mantendo idempotência |
| WebSocket P&L (T-TD-026) consome CPU sem necessidade | Tick fixo 5s + handler que cancela se sem cliente conectado |
| Painel de feature flags (T-TD-v0.2-06) expõe nomes internos | Apenas booleanos no response; nunca valores de tokens/secrets |

---

## 12. Delta no DVP

Sem alteração — esta SPEC é manutenção/auditoria de ledger, não muda direção estratégica.

---

## 13. Dependências externas

Nenhuma. Todas as TASKs podem ser executadas no ambiente atual.

---

## 14. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior aprova a SPEC v0.3 — Review do TECH-DEBT
    como saneamento sistemático do ledger, conforme princípios:

    a) Esta SPEC NAO cria novos TDs nem expande escopo arquitetural.

    b) Classifica os 36 TDs vigentes em 4 categorias: RESOLVIDO (3),
       CONGELADO (3), SANAR-AGORA (9), MANTIDO-ATIVO (21).

    c) Os 9 TDs SANAR-AGORA viram TASKs T-TD-{N} no PLAN v0.3 — todas
       sem mudança de DAS/ADR. Se durante CODE alguma TASK exigir
       mudança arquitetural, ABORTAR e reclassificar.

    d) TDs CONGELADOS pela R20 (Profit desativada) ganham marca explícita
       no TECH-DEBT.md — não há trabalho a fazer enquanto feature off.

    e) TDs MANTIDOS-ATIVOS permanecem no ledger com revisão futura
       (SPEC v0.4 ou Fase 1).

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`/apps/cam-cockpit/TECH-DEBT.md`](../TECH-DEBT.md) — alvo da auditoria
- [`/project/cam-cockpit/qa/QA-REVIEW-SPEC-v0.2.md`](./qa/QA-REVIEW-SPEC-v0.2.md) — review do bloco MT5 (contexto)
- [`/project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md`](./SPEC-v0.2-MT5-ENQUADRAMENTO.md) — origem dos 9 TDs novos e dos 3 CONGELADOS
- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — Arts. 12º (validator novo), 31º (audit), 25º (P&L)
- [`/project/MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../MAPPING-CONSTITUICAO-RISK-ENGINE.md) — alvo de update após T-TD-001
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — referência de limites de fase para T-TD-001

---

> **Princípio operacional desta SPEC:**
>
> Albert audita o ledger. Linus valida a categorização. O Founder libera o saneamento.
>
> Ledger sujo é dívida invisível. Auditoria sistemática é a única forma de reduzir custo de manutenção do TECH-DEBT.md sem ignorar entradas.

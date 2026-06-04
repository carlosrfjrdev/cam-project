---
template: PLAN
phase: PLAN
status: Draft
version: 0.5
date: 2026-05-29
spec_ref: ../specs/SPEC-v0.5-COCKPIT-UI.md
constitution_ref: ../../../CONSTITUICAO.md
ds_ref: ../../../the-cam/ui-design/
demand_id: PLAN-v0.5-COCKPIT-UI
pmg: G
sec: true
qa_sec: true
letscode: true
---

# PLAN v0.5 — Cockpit UI (indexador)

> **Lead:** Nico · **Co-leads:** Albert (loop P/M/G), Don (UX defesa de capital), Andy (DS), Oscar (borda HTTP) · **Aprovador:** Founder
> **Skill:** `teczi-code-planning`
> **Princípio:** PLAN agêntico DevFlow — TASKs flat numeradas (U001..U023), **TDD First por TASK**.
> **Front:** Vitest + Testing Library (componentes testados antes). **Back:** pytest TDD First (routers).

---

## 1. Resumo

Implementar a SPEC v0.5-COCKPIT-UI em **23 TASKs flat**, agrupadas em 6 blocos (BL-UI-0..5) e
4 janelas com gate Founder. A v0.5 **expõe (HTTP) e visualiza (UI)** o que a v0.4 já construiu —
sem lógica de negócio nova. Borda HTTP antes das telas. DS CAM Esmeralda + defesa de capital.

> **Decisões Founder embutidas (2026-05-29):** Full Web (não mobile-first; interação mobile via
> Robô Telegram, spec futura); revisão/inferência de telas fora da v0.4 → v0.6.

---

## 2. Referências de entrada

| Artefato | Status |
|---|---|
| [`SPEC-v0.5-COCKPIT-UI.md`](../specs/SPEC-v0.5-COCKPIT-UI.md) | **Approved** 2026-05-29 (com 2 ajustes do Founder) |
| [`REPORT-FRONTEND-GAP-v0.4.md`](../qa/v0.4/REPORT-FRONTEND-GAP-v0.4.md) | diagnóstico de origem |
| [`the-cam/ui-design/`](../../../the-cam/ui-design/) | **DS CAM** (Esmeralda; refatorado, sem branding Teczi) |
| `apps/cam-cockpit/backend/cam/api/main.py` | onde dead routes serão registrados |
| `apps/cam-cockpit/frontend/src/` | 10 páginas pré-v0.4 a re-tematizar + telas novas |
| ADR-013 | vertical slice (aplica ao front) |

---

## 3. P/M/G (Loop Albert ↔ Nico)

| Campo | Valor |
|---|---|
| Classe SPEC | **G** |
| Concordância Nico | **Sim** |
| Por bloco | BL-UI-0 **M** · BL-UI-1 **G** · BL-UI-2 **G CRÍTICO** · BL-UI-3 **G** · BL-UI-4 **G** · BL-UI-5 **G** |
| Loop | fechado sem disputa — borda HTTP + DS + 12 telas sec/qa-sec justificam G |

---

## 4. Princípios do PLAN

1. **TASKs flat U001..U023** — sem Épico/FG/Story.
2. **TDD First** — front: teste de componente (Vitest+RTL) antes; back: pytest antes do router.
3. **Borda HTTP antes da tela** — BL-UI-0 é pré-requisito duro de BL-UI-2..5.
4. **Read-only/seguro** — UI lê `cam_risk_decisions`/journal; comanda só pause/resume/kill switch; **nunca** envia ordem nem liga real (Kevin barra).
5. **DS CAM é lei** — zero hex/rem hardcoded; tudo via theme.
6. **Defesa de capital** — líquido (Art. 25º) + kill switch (Art. 18º) + EnvBanner em toda tela operacional (Don).
7. **Full Web desktop-first** — responsivo p/ visualização; interação mobile fora de escopo (Telegram futuro).
8. **Founder-only nos gates** — fim de janela + `letscode`.
9. **Sem estimativa em horas/dias/semanas.**

---

## 5. Mapa de execução — 4 Janelas

### Janela UI-1 — Borda HTTP + DS Foundation (BL-UI-0 + BL-UI-1)
```
BL-UI-0: U001 → U002 → U003 → U004 → U005 → U006 → U007 → U008
BL-UI-1: U009 → U010 → U011 → U012
```
**Gate:** Founder valida `CA-U0.1..U0.5` (endpoints vivos) + `CA-U1.1..U1.5` (tema Esmeralda + AppShell).

### Janela UI-2 — Defesa de capital (BL-UI-2) — CRÍTICA
```
BL-UI-2: U013 → U014 → U015
```
**Gate:** Founder valida `CA-U2.1..U2.4` (Order Gateway visível + banner demo/real + líquido + kill switch).

### Janela UI-3 — Núcleo + Risco (BL-UI-3 + BL-UI-4)
```
BL-UI-3: U016 → U017 → U018
BL-UI-4: U019 → U020 → U021
```
**Gate:** Founder valida `CA-U3.1..U3.3` + `CA-U4.1..U4.3`.

### Janela UI-4 — Wealth + Research (BL-UI-5)
```
BL-UI-5: U022 → U023
```
**Gate:** Founder valida `CA-U5.1..U5.3`. SDOC sob solicitação (Q11).

---

## 6. Catálogo flat das 23 TASKs

### BL-UI-0 — Borda HTTP (back)
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U001 | [Registrar `strategies_router` em main.py](./v0.5-tasks/TASK-U001-mount-strategies-router.md) | RU0.01, RU0.02 · CA-U0.1 | — |
| U002 | [Registrar `holdings_router` (carteira-hard) em main.py](./v0.5-tasks/TASK-U002-mount-holdings-router.md) | RU0.01 · CA-U0.2 | — |
| U003 | [Router Robot Orchestrator](./v0.5-tasks/TASK-U003-robot-orchestrator-router.md) | RU0.03 · CA-U0.3 | — |
| U004 | [Router Scaling/Escalonamento](./v0.5-tasks/TASK-U004-scaling-router.md) | RU0.04 · CA-U0.3 | — |
| U005 | [Router Research/AI Workbench](./v0.5-tasks/TASK-U005-research-router.md) | RU0.05 · CA-U0.3 | — |
| U006 | [Router Fundamentals/Dividendos](./v0.5-tasks/TASK-U006-fundamentals-router.md) | RU0.06 · CA-U0.3 | — |
| U007 | [Endpoint Order Gateway decisions (read-only)](./v0.5-tasks/TASK-U007-order-gateway-decisions.md) | RU0.07 · CA-U0.3, CA-U0.5 | — |
| U008 | [Expor Market Data provenance + instruments + EA control](./v0.5-tasks/TASK-U008-market-data-ea-endpoints.md) | RU0.08 · CA-U0.3 | — |

### BL-UI-1 — DS CAM Foundation (front)
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U009 | [Theme MUI Esmeralda (substitui azul/monospace)](./v0.5-tasks/TASK-U009-theme-esmeralda.md) | RU1.01, RU1.02 · CA-U1.1 | — |
| U010 | [AppShell — Header + Sidebar colapsável + Content](./v0.5-tasks/TASK-U010-appshell.md) | RU1.03 · CA-U1.2 | U009 |
| U011 | [Componentes de defesa — EnvBanner + PnlDisplay + re-tema banners](./v0.5-tasks/TASK-U011-defense-components.md) | RU1.04 · CA-U1.3 | U009 |
| U012 | [Tokens centralizados + lint no-hardcode](./v0.5-tasks/TASK-U012-tokens-lint.md) | RU1.05 · CA-U1.4, CA-U1.5 | U009 |

### BL-UI-2 — Defesa de capital (CRÍTICO)
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U013 | [Tela Order Gateway / Risk Decisions](./v0.5-tasks/TASK-U013-order-gateway-page.md) | RU2.01 · CA-U2.1 | U007, U010 |
| U014 | [EnvBanner transversal + PnlDisplay líquido em todas as telas](./v0.5-tasks/TASK-U014-env-banner-liquido.md) | RU2.02 · CA-U2.2, CA-U2.3 | U011 |
| U015 | [Kill switch presente em toda tela operacional (auditoria)](./v0.5-tasks/TASK-U015-killswitch-presence.md) | RU2.03 · CA-U2.4 | U010 |

### BL-UI-3 — Núcleo
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U016 | [Tela Strategy Registry](./v0.5-tasks/TASK-U016-strategy-registry-page.md) | RU3.01 · CA-U3.1 | U001, U010 |
| U017 | [Tela EA Control Panel (pause/resume/version/heartbeat)](./v0.5-tasks/TASK-U017-ea-control-page.md) | RU3.02 · CA-U3.2 | U008, U010 |
| U018 | [Tela Market Data / Provenance](./v0.5-tasks/TASK-U018-market-data-page.md) | RU3.03 · CA-U3.3 | U008, U010 |

### BL-UI-4 — Risco / multiestratégia
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U019 | [Risk Console v0.4 (aderência individual + agregada)](./v0.5-tasks/TASK-U019-risk-console-v04.md) | RU4.01 · CA-U4.1 | U003, U010 |
| U020 | [Tela Robot Orchestrator (robôs + conflitos)](./v0.5-tasks/TASK-U020-robot-orchestrator-page.md) | RU4.02 · CA-U4.2 | U003, U010 |
| U021 | [Tela Escalonamento (histograma tentativas-bloqueadas)](./v0.5-tasks/TASK-U021-scaling-page.md) | RU4.03 · CA-U4.3 | U004, U010 |

### BL-UI-5 — Wealth / Research
| # | TASK | Cobre | Pré-req |
|---|---|---|---|
| U022 | [Carteira Hard v0.4 (holdings + R-20 + policy + dividendos)](./v0.5-tasks/TASK-U022-carteira-hard-v04.md) | RU5.01 · CA-U5.1, CA-U5.2 | U002, U006, U010 |
| U023 | [Research / AI Workbench (Recharts)](./v0.5-tasks/TASK-U023-research-workbench.md) | RU5.02 · CA-U5.3 | U005, U010 |

---

## 7. Dependências externas / riscos

| # | Item | Mitigação |
|---|---|---|
| E1 | Re-tema pode quebrar telas pré-v0.4 | U009 + snapshot tests; re-tematização incremental |
| E2 | UI não pode abrir caminho de ordem | Kevin valida cada router (U001-U008) e cada tela; zero SUBMIT_ORDER no front |
| E3 | Recharts no bundle | lazy-load da rota research (U023) |
| E4 | Endpoints read-only vazarem dado sensível | anonimização + QA-SEC |

---

## 8. Reuso aplicado

| Reuso | Onde | Origem |
|---|---|---|
| `KillSwitchButton` + `useKillSwitch` | U015 | frontend pré-v0.4 (preservar) |
| `RiskEngineStatusBanner`, `PnlDisplay` | U011, U014 | frontend pré-v0.4 (re-tematizar) |
| Routers existentes (`strategies/routes.py`, `holdings_router.py`) | U001, U002 | v0.4 (dead routes — só montar) |
| Backend services v0.4 (orchestrator, scaling, research, fundamentals) | U003-U006 | v0.4 (só expor via router) |
| `cam_risk_decisions` table | U007, U013 | Risk Engine vigente |
| Tokens DS CAM (Esmeralda) | U009 | `the-cam/ui-design/tokens.md` |
| Vertical slice front | todas | ADR-013 |

---

## 9. Saídas esperadas

- **Backend:** 6 routers novos/montados + 2 dead routes registradas + endpoint Order Gateway decisions (read-only). Migrations: nenhuma (só exposição).
- **Frontend:** theme Esmeralda + AppShell + ~10 telas novas/re-tematizadas + componentes de defesa.
- **Testes:** pytest (routers) + Vitest/RTL (componentes), TDD First.
- **Lints:** import-linter (back) + no-hardcode-hex (front).
- **SDOC:** sob solicitação (Q11).

---

## 10. `letscode` — Gate Founder do PLAN

| Campo | Valor |
|---|---|
| Status | **`true`** (aprovado verbalmente pelo Founder) |
| Aprovado por | Founder em 2026-05-29 (execução autônoma noturna) |

```
[ ] Carlos aprova o PLAN v0.5-COCKPIT-UI:
    a) 23 TASKs flat, TDD First, 4 janelas com gate.
    b) Borda HTTP (BL-UI-0) antes das telas.
    c) DS CAM Esmeralda + defesa de capital como CAs de primeira classe.
    d) Nenhuma UI envia ordem nem liga real (Kevin).
    e) CODE inicia a Janela UI-1 após letscode=true.
```

---

## 11. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 0.5-draft | 2026-05-29 | Indexador + 23 TASKs flat — Nico (Albert sem disputa) | — |
| 0.5 | 2026-05-29 | `letscode=true` (verbal). CODE autônomo das 23 TASKs concluído: backend 749 testes, frontend 63 testes, todos verdes. Débitos em [`qa/v0.5/TECH-DEBTS-v0.5-COCKPIT-UI.md`](../qa/v0.5/TECH-DEBTS-v0.5-COCKPIT-UI.md). Gates de janela aguardam validação do Founder. | Founder (letscode) |

---

> **Princípio operacional:** Borda HTTP primeiro. Tela depois. Líquido sempre. Kill switch sempre. Esmeralda estrutura. Founder no gate.

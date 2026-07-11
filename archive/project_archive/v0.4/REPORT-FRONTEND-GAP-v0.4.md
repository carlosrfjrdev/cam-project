---
template: REPORT
phase: QA-REVIEW
demand: SPEC-v0.4-VISION-EVOLUTION
date: 2026-05-29
orquestracao: Leo
lentes: Marty/Albert (escopo) · Oscar (arquitetura) · Don (UX defesa de capital) · Linus (QA)
solicitante: Founder
status: Aguardando-Gate-Founder
---

# REPORT — Gap de Frontend da v0.4 Vision Evolution

> Solicitado pelo Founder após QA: "esperava mudança significativa no front-end; não
> encontrei Strategy Registry, Order Gateway, Control Panel, Market Data — praticamente
> nada visualmente do escopo." Orquestrado por Leo; verificado contra git, estrutura real
> e routers FastAPI montados.

---

## 1. Veredito honesto

**O Founder está certo.** A v0.4 foi entrega quase exclusivamente de **backend + MQL5**.
O frontend **não recebeu nenhuma linha nova** em toda a execução BL-A..BL-I (713 testes
verdes, todos backend). As 4 TASKs de UI (T024, T039, T049, T057) foram **todas
`Deferred-TechDebt`** — e cobriam só uma fração. A SPEC **subespecificou a UI** de uma
evolução de 9 blocos / 30+ features; o PLAN §11 consolidou em "3 telas novas/atualizadas",
que foram deferidas. **Resultado líquido: 0 telas v0.4.**

Evidências verificadas:
- **F1** — `git diff --stat main..dev -- apps/cam-cockpit/frontend/` = **vazio**. Frontend não tocado na v0.4.
- **F2** — 10 rotas no front (`app/router.tsx`), todas pré-v0.4: `/ /journal /fiscal /harvest /risk /constitution /settings /paper-trading /carteira-hard /backtest`.
- **F3** — Não existem no front: `features/strategies`, order-gateway/control-plane, `features/market-data`, robot-orchestrator, scaling/escalonamento, research-workbench.
- **F4** — Cada `features/*/` do front = 1 página; nenhum build-out v0.4.

**Quantificação:** lógica backend em **10/10** áreas · endpoint HTTP montado em **3/10** · UI v0.4 em **0/10**.
> A inteligência foi construída; o cockpit que o operador usa para vê-la e comandá-la, não.

---

## 2. Cobertura por feature v0.4

✅ pronto · 🟡 parcial · ❌ ausente · 🟡-dead = router existe no código mas **não registrado** em `main.py`

| Feature v0.4 | Backend | Endpoint montado? | Frontend | Observação |
|---|---|---|---|---|
| **Strategy Registry** (BL-A) | ✅ | 🟡-dead (`routes.py` existe, **não montado**) | ❌ | endpoint construído e **morto** |
| **Order Gateway** (BL-A) | ✅ | n/a (interno) | ❌ | operador não vê decisões / validator culpado |
| **EA Control Plane** (BL-A/E) | ✅ | 🟡 via `mt5_router` (montado) | ❌ | sem painel pause/resume/versão |
| **Market Data / Provenance** (BL-B) | ✅ | ✅ `market_data_router` montado | ❌ | endpoint OK, sem tela |
| **Paper Loop Governado** (BL-C) | ✅ | ✅ `paper_trading_router` montado | 🟡 | página pré-v0.4 não reflete o loop novo |
| **Carteira Hard Holdings** (BL-D) | ✅ | 🟡-dead (`holdings_router` **não montado**; só `ledger_router` v0.3) | 🟡 | rota `/carteira-hard` é shell pré-v0.4 |
| **Dividendos + Fundamentalistas** (BL-F) | 🟡 esqueleto (TD-v0.4-01) | ❌ sem router | ❌ | sem calendário / 7 indicadores / alertas |
| **Research / Cross-Asset** (BL-G) | ✅ | ❌ sem router | ❌ | biblioteca pura; AI Workbench sem Recharts |
| **Robot Orchestrator** (BL-H1) | ✅ | ❌ sem router | ❌ | sem painel de robôs / conflitos / aderência |
| **Escalonamento Art. 11-B** (BL-H2) | 🟡 (`scaling.py` ok; `features/scaling` só repo) | ❌ sem router | ❌ | sem histograma tentativas-bloqueadas |

**Síntese (confirmada em `main.py`):** 16 routers montados, mas só **3** servem features v0.4
(market_data, paper_trading, mt5/EA parcial). **2 dead routes** (strategies, carteira-hard) ·
**4 features sem router algum** (robot_orchestrator, scaling, research, fundamentals) · **0 UI v0.4**.

---

## 3. Causa-raiz (3 camadas)

- **Marty/Albert (SPEC):** a SPEC tratou UI como adereço, não entregável. Sem bloco de UI, sem CAs de tela — só menções pontuais (R4.05, R7.03 Recharts, R8.18, R8.06). Subdimensionamento na origem.
- **PLAN/QA (execução):** das 62 TASKs, só 4 eram UI — e **as 4 foram deferidas**. O QA-REPORT deu Go-Conditional ciente disso (ressalva 2).
- **Oscar (arquitetura) — o mais bloqueante:** mesmo querendo telas, **faltam endpoints**. `strategies` e `holdings_router` têm `routes.py` mas **nunca foram registrados** em `main.py`. `robot_orchestrator`, `scaling`, `research`, `fundamentals` **não têm router**. UI sem borda HTTP é impossível para 7 de 10 features.

> **Correção a um alarme do Leo:** o sub-agente reportou que o "backend v0.4 estaria não-commitado".
> **Verificado e refutado:** `git status` do backend está limpo, arquivos `ls-files` rastreados,
> `git diff main..dev -- backend` vazio (idêntico nos dois branches). O backend **está commitado**.
> (Nuance menor: parte entrou via commit que também tocou `main` — fato consumado, não bloqueia esta análise.)

---

## 4. Lente Don — UX como defesa de capital

**Já existe (preservado):**
- ✅ **Kill switch acessível em toda tela** (`KillSwitchButton.tsx` + `useKillSwitch.ts` no `Layout.tsx` + RiskConsole) — **Art. 18º atendido. Resposta direta ao Founder: o kill switch existe.**
- ✅ `RiskEngineStatusBanner`.
- ✅ Líquido fiscal/harvest herdado (Art. 25º).

**Inegociável que HOJE não existe:**
- ❌ Ver decisões do **Order Gateway** (caminho único da ordem — cegueira no ponto mais sensível).
- ❌ Status do **Strategy Registry** (o que está armado / em que estado).
- ❌ **Provenance** do Market Data (dado sem provenance não entra — mas operador não vê).
- ❌ Aderência individual×agregada + **histograma de tentativas-bloqueadas** (Art. 11/11-B).
- ❌ **Banner demo/real por tela** — crítico antes de qualquer DEMO live (BL-E).

> Veredito Don: as defesas de **parada** existem; as de **visibilidade** não. No CaM, não enxergar o risco é risco.

---

## 5. Recomendação

**Abrir SPEC dedicada `SPEC-v0.5-COCKPIT-UI` — NÃO uma janela dentro da v0.4** (janela
repetiria o subdimensionamento). A v0.4 é honestamente a release de **motor**; a v0.5 é a
de **cockpit**. **v1.0 não é inferida** — permanece declaração exclusiva do Founder.

**Pré-requisito arquitetural bloqueante (Oscar) — fechar a borda HTTP ANTES das telas:**
1. Registrar `strategies` router em `main.py` (dead route).
2. Registrar `holdings_router` (carteira-hard) em `main.py` (dead route).
3. Router Robot Orchestrator (BL-H1).
4. Router Scaling/Escalonamento (BL-H2).
5. Router Research / AI Workbench (BL-G).
6. Router Fundamentals/Dividendos (BL-F).
7. Endpoint Order Gateway decisions (read-only, para visibilidade).

**Telas necessárias (ordem de prioridade — UX de defesa primeiro):**
1. **Order Gateway / Risk Decisions** (CRÍTICA — visibilidade do caminho da ordem).
2. **Banner demo/real + líquido transversal** (CRÍTICA — antes de DEMO live).
3. **Strategy Registry** (alta).
4. **EA Control Panel** pause/resume/versão (alta).
5. **Market Data / Provenance** (alta).
6. **Risk Console v0.4** — aderência + multiestratégia (alta).
7. **Robot Orchestrator** — robôs/conflitos (média).
8. **Carteira Hard v0.4** — holdings + 7 indicadores + alertas policy (média).
9. **Research / AI Workbench** — Recharts (média).

> P/M/G por tela é trabalho de Albert/Nico na SPEC/PLAN — **nunca em horas/dias/semanas**.

---

## 6. Gate (decisão do Founder)

```
[ ] Aprovar abrir SPEC-v0.5-COCKPIT-UI, reconhecendo:
    (a) v0.4 = motor; v0.5 = cockpit.
    (b) pré-requisito: registrar 2 dead routes + criar ~5 routers antes das telas.
    (c) defesas de UI (Order Gateway visível, banner demo/real, provenance,
        aderência) como CAs de primeira classe (lentes Don + Albert).
    (d) v0.5 NÃO infere v1.0.

[ ] (opcional) Endurecer governança: as telas de visibilidade de risco
    (Order Gateway, aderência, banner) entram como bloqueantes antes de
    qualquer liberação de DEMO live (BL-E).
```

---

## 7. Resumo executivo (1 parágrafo)

A v0.4 entregou um **motor sólido** (backend + MQL5, 713 testes verdes), mas o **frontend não
foi tocado uma única vez**: 0 telas novas, 10 rotas todas pré-v0.4, as 4 TASKs de UI deferidas.
Pior: para **7 das 10 features** v0.4 **nem existe endpoint HTTP** — `strategies` e `carteira-hard`
têm rota escrita mas **morta** (não registrada em `main.py`); robot-orchestrator/scaling/research/
fundamentals não têm rota. Então não é só "construir tela": é **expor a inteligência primeiro**.
O **kill switch existe e está acessível** (Art. 18º ok); o que falta são as defesas de **visibilidade**.
Recomendação: **SPEC-v0.5-COCKPIT-UI dedicada**, com a borda HTTP fechada antes das telas. Decisão é do Founder.

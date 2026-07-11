---
template: SPEC
phase: SPEC
status: Approved
version: 0.5
date: 2026-05-29
approved_by_founder_at: 2026-05-29
approval_note: "Aprovada com 2 ajustes do Founder: (1) não-inferência de telas fora da v0.4 → tratada na v0.6; (2) Full Web (não mobile-first) — interação mobile via Robô Telegram (spec futura)."
parent_spec: SPEC-v0.4-VISION-EVOLUTION.MD
companions:
  - REPORT-FRONTEND-GAP-v0.4.md (qa/v0.4)
  - the-cam/ui-design/ (DS — a ser refatorado para DS CAM)
demand_id: SPEC-v0.5-COCKPIT-UI
pmg: G
sec: true
qa_sec: true
---

# SPEC v0.5 — Cockpit UI (a release do cockpit visual)

> **Lead:** Albert (especificação) · **Co-leads:** Don (UX como defesa de capital), Andy (DS visual), Oscar (borda HTTP / arquitetura front), Kevin (`sec`/`qa-sec`)
> **Orchestrator:** Leo · **Aprovador:** Founder
> **Origem:** [`REPORT-FRONTEND-GAP-v0.4.md`](../qa/v0.4/REPORT-FRONTEND-GAP-v0.4.md) — diagnóstico de que a v0.4 entregou o **motor** (backend + MQL5, 713 testes) e **0 telas**.

---

## 1. Contexto

A SPEC v0.4 entregou um motor sólido, mas **o frontend não foi tocado uma única vez**: 10 rotas, todas pré-v0.4; as 4 TASKs de UI deferidas; e — pior — **7 das 10 features v0.4 nem têm endpoint HTTP** para uma UI consumir.

A v0.5 é honestamente **a release do cockpit**: expor a inteligência já construída e dar ao operador as telas para **ver e comandar** o sistema, com **defesa de capital** como princípio de UX. Não infere v1.0 — isso permanece declaração exclusiva do Founder.

### 1.1 Achados verificados que fundam esta SPEC

| # | Achado | Evidência |
|---|---|---|
| A1 | Frontend não tocado na v0.4 | `git diff main..dev -- frontend/` vazio |
| A2 | `strategies/routes.py` existe mas **não montado** (dead route) | ausente em `cam/api/main.py` |
| A3 | `ledger/holdings_router.py` existe mas **não montado** (dead route) | ausente em `main.py` |
| A4 | `robot_orchestrator`, `scaling`, `research`, `fundamentals` **sem router** | `find features -name "*rout*"` |
| A5 | Order Gateway sem endpoint de visibilidade (read-only) | só interno |
| A6 | `theme.ts` atual **diverge do DS**: azul `#1565c0`, JetBrains Mono, fundo `#0a0a0a` | `frontend/src/app/theme.ts` |
| A7 | DS esmeralda existe em `the-cam/ui-design/` mas **branding Teczi** | `tokens.md`, `layout-directive.md` |

### 1.2 O que esta SPEC **é**

- Especificação do **cockpit visual** do CaM em blocos de UI (BL-UI-0..5).
- Fechamento da **borda HTTP** (pré-requisito): registrar dead routes + criar routers faltantes + endpoint read-only do Order Gateway.
- Adoção do **DS CAM** (paleta Esmeralda + tokens + layout shell) substituindo o tema azul/monospace atual.
- Telas com **aderência explícita ao DS** + CAs por tela.

### 1.3 O que esta SPEC **NÃO é**

- **Não declara v1.0.**
- **Não libera operação real** (`REAL_TRADING_ALLOWED=false` permanece).
- **Não cria lógica de negócio nova** — só expõe (HTTP) e visualiza (UI) o que a v0.4 já construiu.
- **Não toca** Risk Engine, Constituição, settings.
- **Não infere telas de features fora da v0.4** → **a v0.6 tratará dessa revisão e inferência** de telas de features fora do escopo v0.4 (decisão Founder 2026-05-29). Esta SPEC fica restrita ao que a v0.4 construiu.

---

## 2. Escopo

### 2.1 In

| Bloco | Foco |
|---|---|
| **BL-UI-0** | Borda HTTP — dead routes + routers faltantes + Order Gateway read-only |
| **BL-UI-1** | DS CAM Foundation — theme MUI Esmeralda + tokens + AppShell (sidebar/header) |
| **BL-UI-2** | Telas de defesa de capital (CRÍTICAS) — Order Gateway/Risk Decisions + Banner demo/real + líquido transversal |
| **BL-UI-3** | Telas operacionais núcleo — Strategy Registry + EA Control Panel + Market Data/Provenance |
| **BL-UI-4** | Telas de risco/multiestratégia — Risk Console v0.4 + Robot Orchestrator + Escalonamento (histograma) |
| **BL-UI-5** | Telas wealth/research — Carteira Hard v0.4 (holdings+R-20+policy) + Research/AI Workbench (Recharts) |

### 2.2 Out

- ❌ Lógica de negócio nova (só exposição/visualização).
- ❌ Endpoints de escrita que liguem operação real ou auto-execução.
- ❌ OpenAI (TD-v0.4-02), scraping real (TD-v0.4-01).
- ❌ Telas de operação real (Fase 2+).
- ❌ Mobile app nativo.
- ❌ Layout mobile-first (o CaM é **full web** — ver §3.5).
- ❌ Interação operacional via mobile na UI web (será via **Robô Telegram**, spec futura).

### 2.3 Later

- 🔜 Telas de operação real governada (Founder declara).
- 🔜 **Robô Telegram — interação/operação remota mobile** (spec futura a refinar e definir): a operação pelo celular se dá pelo bot Telegram, não pela UI web responsiva.
- 🔜 **v0.6** — revisão + inferência de telas de features fora do escopo v0.4.

---

## 3. Princípios vinculantes (UI)

1. **Defesa de capital antes de estética** (Don) — toda tela operacional exibe líquido (Art. 25º), kill switch acessível (Art. 18º), banner de ambiente.
2. **Read-only por padrão** — a UI v0.5 **lê e comanda controles seguros** (pause/resume, kill switch); **nunca** envia ordem nem liga real.
3. **DS CAM é lei visual** — Esmeralda + tokens + layout-directive. Zero valor atômico fora dos tokens.
4. **Borda HTTP antes da tela** — nenhuma tela sem endpoint correspondente (Oscar).
5. **Full Web (desktop-first responsivo) + Dark Mode First + WCAG AA** — o CaM é **aplicação de gestão financeira local**, não mobile-first. As telas **podem ser visualizadas em celular** (responsivo para leitura), mas a **interação/operação mobile se dá via Robô Telegram** (spec futura), nunca pela UI web no celular. Layout otimizado para desktop (tela de gestão).
6. **Vertical slice no front** (ADR-013) — `features/{x}/` self-contained.
7. **TDD First** — testes de componente (Vitest + Testing Library) antes do componente.
8. **Sem caminho de ordem na UI** — UI consome `cam_risk_decisions`/journal; não chama Order Gateway de escrita.

---

## 4. BL-UI-0 — Borda HTTP (pré-requisito bloqueante)

> Sem isso, 7 de 10 telas são impossíveis. Lead: Oscar (+Kevin sec).

### 4.1 Regras

**RU0.01 — Registrar dead routes.** Adicionar em `cam/api/main.py`:
- `app.include_router(strategies_router)` — de `cam/features/strategies/routes.py`.
- `app.include_router(holdings_router)` — de `cam/features/ledger/holdings_router.py`.

**RU0.02 — Strategy Registry endpoints** (se ausentes em `routes.py`, completar): `GET /api/v1/strategies` (lista + status), `GET /api/v1/strategies/{id}`, `POST /api/v1/strategies/{id}/promote` (com EvidencePack), `POST /api/v1/strategies/{id}/activate`. **Read + comandos governados; nunca ordem.**

**RU0.03 — Robot Orchestrator router** (NOVO): `cam/features/robot_orchestrator/routes.py` — `GET /api/v1/robots` (robôs + estratégias + prioridade), `GET /api/v1/robots/{id}/adherence` (individual + agregada).

**RU0.04 — Scaling router** (NOVO): `cam/features/scaling/routes.py` — `GET /api/v1/scaling/events`, `GET /api/v1/scaling/eligibility/{strategy_id}`, `GET /api/v1/scaling/blocked-attempts` (histograma), `POST /api/v1/scaling/revoke/{esc_id}` (T053 — já mapeado como TD-v0.4-H2.3).

**RU0.05 — Research/AI Workbench router** (NOVO): `cam/features/research/routes.py` — `GET /api/v1/research/correlation`, `POST /api/v1/research/pair-trade-backtest`, `POST /api/v1/research/workbench` (output JSON estruturado).

**RU0.06 — Fundamentals/Dividendos router** (NOVO): `cam/features/fundamentals/routes.py` — `GET /api/v1/fundamentals/{ticker}`, `GET /api/v1/dividends/calendar`, `GET /api/v1/carteira-hard/policy-alerts`.

**RU0.07 — Order Gateway visibility endpoint** (NOVO, read-only): `GET /api/v1/order-gateway/decisions` — lista de `cam_risk_decisions` (decisão, validator culpado, env, mode, ts). **Read-only — não submete ordem.**

**RU0.08 — Market Data / EA Control** (montar/expor o que falta): `GET /api/v1/market-data/provenance`, `GET /api/v1/market-data/instruments`; EA control via `mt5_router` existente (`GET_VERSION`, `PAUSE_EA`, `RESUME_EA`).

### 4.2 Critérios

- **CA-U0.1** `GET /api/v1/strategies` retorna 200 com S1 ORB (era dead route).
- **CA-U0.2** `GET /api/v1/carteira-hard/holdings` retorna 200 (era dead route).
- **CA-U0.3** Cada novo router (robots, scaling, research, fundamentals, order-gateway) responde 200 em pelo menos 1 endpoint read-only.
- **CA-U0.4** `import-linter` continua verde (routers respeitam vertical slice).
- **CA-U0.5** Nenhum endpoint novo permite envio de ordem ou liga `REAL_TRADING_ALLOWED` (Kevin valida).

**P/M/G:** M. **sec=true** (Kevin: nenhuma borda HTTP abre caminho de ordem/real).

---

## 5. BL-UI-1 — DS CAM Foundation

> Substitui o tema azul/monospace atual pelo DS Esmeralda. Lead: Andy (+Don UX).

### 5.1 Regras

**RU1.01 — Theme MUI Esmeralda.** Reescrever `frontend/src/app/theme.ts` a partir dos tokens do DS CAM:
- `palette.primary.main = #059669` (Esmeralda), `primary.dark = #047857`, `primary.light = #34D399`.
- `background.default = #1A1A1A`, `background.paper = #1F1F1F` (dark first).
- `success #10B981`, `warning #F59E0B`, `error #EF4444`, `info #0EA5E9`.
- Tipografia: **Poppins** (headings 600) + **Inter** (body 400). Remover JetBrains Mono como fonte global (monospace só em código/números técnicos).
- Border radius: botões 4px, cards 6px, inputs 4px. Focus ring 2px `#10B981`.

**RU1.02 — Founder Orange como acento editorial.** `#FF7A00` disponível como acento (`--founder-orange`) — usado APENAS em contexto "Founder note"/origem, nunca como primária, sucesso ou warning (paleta-founder §4).

**RU1.03 — AppShell** (layout-directive): Header 56px + Sidebar colapsável (208/56px) + Content Area (`p: {xs:2, md:3}`) + Breadcrumb. Sidebar persiste estado.

**RU1.04 — Componentes base de defesa**: `PnlDisplay` (sempre líquido), `KillSwitchButton` (já existe — manter acessível em todo shell), `EnvBanner` (demo/real/paper/backtest — NOVO), `RiskEngineStatusBanner` (já existe — re-tematizar).

**RU1.05 — Tokens centralizados** — nenhum hex/rem hardcoded em componentes; tudo via theme. Dark Mode First; toggle de tema persistido.

### 5.2 Critérios

- **CA-U1.1** `theme.ts` usa Esmeralda `#059669` como primary e Poppins/Inter (snapshot test do theme).
- **CA-U1.2** AppShell renderiza header + sidebar colapsável + content; estado da sidebar persiste em localStorage.
- **CA-U1.3** `EnvBanner` exibe ambiente vigente (demo/paper/backtest); banner real exige sinalização inconfundível.
- **CA-U1.4** Nenhum componente tem hex hardcoded (lint/grep no CI).
- **CA-U1.5** Contraste WCAG AA verificado nas combinações do DS.

**P/M/G:** G. **sec=false, qa-sec=true** (Don: banner de ambiente é defesa).

---

## 6. BL-UI-2 — Telas de defesa de capital (CRÍTICAS)

> Lead: Don. As defesas de **visibilidade** que hoje não existem.

### 6.1 Regras

**RU2.01 — Order Gateway / Risk Decisions** (`features/order-gateway/`): tabela de decisões (`GET /order-gateway/decisions`) — env, mode, asset, direction, decisão (APPROVED/REJECTED), **validator culpado**, motivo, ts. Filtro por env/decisão. Destaque visual para REJECTED.

**RU2.02 — Banner demo/real + líquido transversal**: `EnvBanner` fixo no shell; `PnlDisplay` líquido (Art. 25º) em toda tela com resultado. Real exige banner vermelho inconfundível + confirmação.

**RU2.03 — Kill switch** já acessível (preservar) — validar presença em toda tela operacional.

### 6.2 Critérios

- **CA-U2.1** Tela Order Gateway lista decisões com validator culpado e motivo; REJECTED destacado.
- **CA-U2.2** `EnvBanner` presente em 100% das telas operacionais; ambiente correto.
- **CA-U2.3** Todo valor monetário exibido é **líquido** (nenhum bruto sem provisão) — verificado por teste.
- **CA-U2.4** Kill switch acessível (≤ 1 toque) em toda tela operacional.

**P/M/G:** G. **sec=true CRÍTICO, qa-sec=true CRÍTICO** (ponto mais sensível: visibilidade do caminho da ordem).

---

## 7. BL-UI-3 — Telas operacionais núcleo

> Lead: Don + Andy.

### 7.1 Regras

**RU3.01 — Strategy Registry** (`features/strategies/`): lista de estratégias + status (`draft→...→retired`), is_active, EvidencePack resumido; ação de promover/ativar via endpoints governados (gate visual). S1 ORB visível.

**RU3.02 — EA Control Panel** (`features/ea-control/`): status do EA (`GET_VERSION` — versão+hash+paused), botões PAUSE_EA/RESUME_EA, heartbeat status (online/offline). Sem SUBMIT_ORDER na UI.

**RU3.03 — Market Data / Provenance** (`features/market-data/`): lista de lotes ingeridos (provenance: fonte, ts origem/ingestão, tick_count, hash, quality_flags), catálogo de instrumentos (`cam_instruments`). Quality flags visíveis (has_gaps/zero_volume/out_of_hours).

### 7.2 Critérios

- **CA-U3.1** Strategy Registry mostra S1 ORB com status e is_active; promover sem EvidencePack mostra erro `EVIDENCE_REQUIRED`.
- **CA-U3.2** EA Control Panel mostra versão+hash; PAUSE_EA/RESUME_EA refletem no status; heartbeat offline destacado.
- **CA-U3.3** Market Data lista provenance com quality flags; instrumento WIN/WDO com point_value correto.

**P/M/G:** G. **sec=true** (EA control + Registry tocam superfície sensível), **qa-sec=true**.

---

## 8. BL-UI-4 — Telas de risco / multiestratégia

> Lead: Don (+ lente Nassim no conteúdo de risco).

### 8.1 Regras

**RU4.01 — Risk Console v0.4** (`features/risk-console/` — estender existente): aderência individual × agregada (Art. 11-A/R8.06), limites vigentes (`get_current_limits`), drawdown agregado, posições abertas. Re-tematizar para DS.

**RU4.02 — Robot Orchestrator** (`features/robot-orchestrator/`): robôs + estratégias com prioridade, conflitos resolvidos (DIRECTIONAL_CONFLICT/AMBIGUOUS_TIE), estratégias suspensas (gain lock/aderência).

**RU4.03 — Escalonamento (Art. 11-B)** (`features/scaling/`): histograma de tentativas-bloqueadas por critério (R8.18/CA-H2.9), eventos de escalonamento, cooldown vigente, botão revogar (`POST /scaling/revoke`).

### 8.2 Critérios

- **CA-U4.1** Risk Console mostra aderência individual + agregada; estratégia < 95% destacada como suspensa.
- **CA-U4.2** Robot Orchestrator mostra conflitos com motivo (audit code).
- **CA-U4.3** Escalonamento mostra histograma dos 5 critérios; tentativa bloqueada visível; flag `MULTI_STRATEGY_ENABLED`/`SCALING_ENABLED` exibida (default false).

**P/M/G:** G. **sec=true** (exibe estado constitucional de limites), **qa-sec=true**.

---

## 9. BL-UI-5 — Telas wealth / research

> Lead: Andy (+ lente Barsi/Jim no conteúdo).

### 9.1 Regras

**RU5.01 — Carteira Hard v0.4** (`features/carteira-hard/` — estender): holdings + 7 indicadores R-20 (DY peso forte), calendário de dividendos, alertas do Policy Engine (banner amarelo — sugestão, nunca bloqueio, R-13), rebalance sugerido (nunca executa). Reforçar Art. 23 (não é margem) visualmente.

**RU5.02 — Research / AI Workbench** (`features/research/`): visualização Recharts (correlação cross-asset, spread de pair trade), output estruturado do AI Workbench (Anthropic/Ollama; OpenAI bloqueado).

### 9.2 Critérios

- **CA-U5.1** Carteira Hard mostra holdings + 7 indicadores + alertas policy (banner amarelo não-bloqueante).
- **CA-U5.2** Rebalance aparece como sugestão com checklist; nunca botão de execução automática.
- **CA-U5.3** Research Workbench renderiza Recharts (correlação/pair trade); chamada OpenAI mostra `OpenAINotEnabled`.

**P/M/G:** G. **sec=false, qa-sec=true.**

---

## 10. Aderência ao DS — diagnóstico atual × alvo

| Dimensão | Hoje (`theme.ts`) | Alvo (DS CAM) |
|---|---|---|
| Primary | `#1565c0` (azul) ❌ | `#059669` Esmeralda ✅ |
| Fonte | JetBrains Mono (global) ❌ | Poppins (headings) + Inter (body) ✅ |
| Background | `#0a0a0a` / `#121212` ❌ | `#1A1A1A` / `#1F1F1F` ✅ |
| Tokens | hardcoded ❌ | via theme (SSoT) ✅ |
| Layout shell | ad-hoc ❌ | AppShell layout-directive ✅ |
| Banner demo/real | inexistente ❌ | `EnvBanner` ✅ |
| Founder Orange | n/a | acento editorial `#FF7A00` (raro) ✅ |

> **Conclusão:** o frontend atual tem **baixa aderência** ao DS. BL-UI-1 corrige a fundação; BL-UI-2..5 nascem aderentes.

---

## 11. DS CAM — paleta Esmeralda (resumo que entra nesta SPEC)

> Fonte canônica: `the-cam/ui-design/tokens.md` (a ser refatorado para DS CAM, sem branding Teczi, **após verificação desta SPEC pelo Founder**).

**Primárias (Esmeralda):** `#059669` primary · `#047857` dark · `#34D399` light · `#061711` deep · `rgba(5,150,105,0.14)` soft.
**Superfícies dark:** bg `#1A1A1A` · surface-1 `#1F1F1F` · surface-2 `#2C2C2C` · elevated `#444`.
**Funcionais:** info `#0EA5E9` · success `#10B981` · warning `#F59E0B` · destructive `#EF4444`.
**Founder Orange (acento editorial):** `#FF7A00` / ember `#C2410C` / glow `#FDBA74` — raro, nunca primária.
**Tipografia:** Poppins 600 (h1–h6) · Inter 400 (body) · min 12px.
**Grid 4px, radius 4/6px, focus ring 2px, Dark Mode First, WCAG AA, Full Web (desktop-first responsivo — não mobile-first; interação mobile via Robô Telegram), MUI.**

---

## 12. Classificação P/M/G global

| Campo | Valor |
|---|---|
| Classe global | **G** |
| Rationale | 6 blocos de UI + fechamento de borda HTTP (5 routers novos + 2 dead routes) + adoção de DS + ~12 telas. Toca superfície sensível (Order Gateway/EA/limites). |
| sec | **true** (BL-UI-0, BL-UI-2, BL-UI-3, BL-UI-4) |
| qa-sec | **true** (todas — Don valida defesa de capital; Kevin valida que UI não abre caminho de ordem/real) |

---

## 13. Riscos

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| UI abrir caminho de ordem indevido | Baixa | Alto | RU0.05/RU3.02: zero SUBMIT_ORDER na UI; Kevin valida cada router (sec) |
| Migração de tema quebrar telas existentes | Média | Médio | BL-UI-1 primeiro + snapshot tests; telas antigas re-tematizadas incrementalmente |
| Endpoint novo vazar dado sensível | Baixa | Médio | read-only + anonimização (provider calls); QA-SEC |
| Recharts pesar no bundle | Baixa | Baixo | lazy load da rota research |
| Divergência DS enquanto `ui-design` não refatorado | Média | Baixo | SPEC referencia tokens atuais; refactor do DS é gate pós-verificação |

---

## 14. Sequência sugerida (janelas)

| Janela | Blocos | Gate |
|---|---|---|
| UI-1 | BL-UI-0 (borda HTTP) + BL-UI-1 (DS Foundation) | Founder valida endpoints vivos + tema Esmeralda |
| UI-2 | BL-UI-2 (defesa de capital) | Founder valida Order Gateway visível + banner demo/real |
| UI-3 | BL-UI-3 (núcleo) + BL-UI-4 (risco) | Founder valida Registry/EA/Market Data + Risk Console |
| UI-4 | BL-UI-5 (wealth/research) | Founder valida Carteira Hard + Workbench |

---

## 15. Gate Founder

```
[ ] Carlos aprova a SPEC-v0.5-COCKPIT-UI:

    a) v0.4 = motor; v0.5 = cockpit. Esta SPEC expõe (HTTP) e visualiza (UI)
       o que a v0.4 construiu — sem lógica de negócio nova.

    b) BL-UI-0 fecha a borda HTTP (2 dead routes + 5 routers + Order Gateway
       read-only) ANTES das telas.

    c) DS CAM Esmeralda substitui o tema azul/monospace atual (BL-UI-1).

    d) Defesa de capital (Order Gateway visível, banner demo/real, líquido,
       kill switch) são CAs de primeira classe (Don).

    e) REAL_TRADING_ALLOWED=false permanece; nenhuma UI envia ordem (Kevin).

    f) v1.0 NÃO é inferida.

    g) Após esta verificação → refatorar the-cam/ui-design para DS CAM
       (remover branding Teczi) com Andy + Don.

    h) Liberação para PLAN exige letscode separado.
```

---

## 16. Referências cruzadas

- [`REPORT-FRONTEND-GAP-v0.4.md`](../qa/v0.4/REPORT-FRONTEND-GAP-v0.4.md) — diagnóstico que originou esta SPEC
- [`SPEC-v0.4-VISION-EVOLUTION.MD`](./SPEC-v0.4-VISION-EVOLUTION.MD) — motor (backend) que esta SPEC expõe
- [`the-cam/ui-design/tokens.md`](../../../the-cam/ui-design/tokens.md) — DS (Esmeralda) a refatorar para DS CAM
- [`the-cam/ui-design/layout-directive.md`](../../../the-cam/ui-design/layout-directive.md) — AppShell/Sidebar/Header
- [`/CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 18 (kill switch), 23 (Carteira Hard), 25 (líquido), 35 (IA read-only)
- ADR-013 — vertical slice (aplica ao front)

---

> **Princípio operacional desta SPEC:**
>
> Expor a inteligência. Ver para defender. Esmeralda estrutura, kill switch protege, líquido não mente.
>
> O motor existe. Agora o operador ganha o painel. Construir amplo, liberar estreito. v1.0 fica para o Founder.

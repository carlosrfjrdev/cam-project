# MAP-MODULES-TCaM — Mapa dos 8 Módulos Assets* → Estado Real do Código

> **Status:** PROPOSTA (planejamento). Aguarda revisão do Founder.
> **Autor:** Leo (Chief Orchestrator)
> **Data:** 2026-06-03
> **Base:** leitura do estado real em `apps/cam-cockpit/` (backend: 21 features; frontend: 19 telas).

---

## 0. Legenda

- ✅ **Existe** — código real, funcional (ou MVP entregue)
- ⚠️ **Parcial** — existe base, precisa consolidação/recomposição
- 🔧 **Converter** — existe mas muda de semântica (ex.: trava → config)
- ❌ **Falta** — não existe; construir depois

Estado real confirmado por leitura de `nav.tsx`, `router.tsx`, árvore de
`backend/cam/features/` (21 dirs) e `frontend/src/features/` (19 dirs).

---

## 1. Backend — 21 features mapeadas

```
ai_analyst  backtest  checklists  constitution  fiscal  fundamentals  harvest
journal  kill_switch  ledger  market_data  mt5_integration  notifications
paper_trading  profit_integration  regime  research  robot_orchestrator
scaling  strategies  + _shared/{risk, autonomy, order_gateway, audit, ...}
```

## 2. Frontend — 19 telas mapeadas

```
cockpit  inspetor  quant-lab  order-gateway  risk-console  ea-control
strategies  robot-orchestrator  scaling  market-data  journal  fiscal
harvest  carteira-hard  research  backtest  paper-trading  constitution  settings
```

---

## 3. Os 8 módulos Assets* → features

### 1️⃣ Assets Cockpit — Cockpit operacional
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/cockpit/CockpitPage` + `_shared/components/{Header,AppShell,PnlDisplay}` | ✅ |
| Backend | `api/dashboard_routes.py` + `api/websocket.py` (live) | ✅ |
| Ação | Renomear "Cockpit Live" → **Assets Cockpit**; hub de monitoramento | 🔧 |

### 2️⃣ Assets Manager — Gerenciador de Ativos (carteira/posições)
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/carteira-hard` + `features/harvest` | ⚠️ |
| Backend | `features/ledger` + `features/harvest` + `holdings` (migração `bl_d_holdings`) | ⚠️ |
| Ação | **Consolidar** carteira/holdings/ledger sob um módulo de gestão de ativos. "Carteira Hard"/"Harvest" são jargão pessoal → renomear para linguagem de produto (⚖️ FOUNDER #4: entram no MVP?) | ⚠️ |

### 3️⃣ Assets RiskManager — Gerenciador de Risco configurável
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/risk-console/RiskConsolePage` + `_shared/components/{RiskEngineStatusBanner,KillSwitchButton}` | ✅ |
| Backend | `_shared/risk/{engine,validators,aggregate,limits,scaling,context,decision}` + `_shared/autonomy/matrix` + `features/kill_switch` + `_shared/order_gateway` + `features/scaling` | ✅ |
| Ação | **CONVERTER** de trava constitucional → feature configurável. Limites viram config (não constantes de lei). Ver `CONSTITUTION-DECOMMISSION.md §4.2`. **Este é o moat (Voltaire).** | 🔧 |

### 4️⃣ Assets Inspector — Inspetor de Ativos ✅ PRONTO (MVP)
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/inspetor/` (InspetorPage + CandleChart, FundamentalsPanel, DividendsPanel, RegimePanel, BookPanel, useMarketSocket) | ✅ |
| Backend | `features/fundamentals` + `features/regime` + `features/market_data` + `mt5_integration` (book/candles via ZeroMQ) | ✅ |
| Ação | Renomear "Inspetor de Ativo" → **Assets Inspector**. Já é MVP funcional (brapi.dev + EA/ZeroMQ + Markov). Pouco a fazer | ✅ |

### 5️⃣ Assets Strategy — Gestão de estratégias
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/strategies/StrategyRegistryPage` + `useStrategies` | ✅ |
| Backend | `features/strategies` (+ migração `strategy_lifecycle`) | ✅ |
| Ação | Renomear "Strategy Registry" → **Assets Strategy** | ✅ |

### 6️⃣ Assets RunTests — Backtest matemático (Python)
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/backtest/BacktestPage` + `features/paper-trading` | ✅ |
| Backend | `features/backtest/{domain,simulator,walk_forward,service,metrics}` + `features/paper_trading` | ✅ |
| Ação | Renomear "Backtest" → **Assets RunTests**. Paper trading é vizinho natural (validação) | ✅ |

### 7️⃣ Assets Experts — Gestão de Robôs MT5
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/robot-orchestrator` + `features/ea-control` | ✅ |
| Backend | `features/mt5_integration` + `features/robot_orchestrator` + EAs em `apps/cam-cockpit/mql5/` (`cam_bridge.mq5`, `cam_risk_mirror.mq5`) | ✅ |
| Ação | Renomear "Robot Orchestrator"/"EA Control" → **Assets Experts**. (`profit_integration` em standby — Profit) | ✅ |

### 8️⃣ Assets Labs — Laboratório de pesquisas ✅ PRONTO
| Camada | Componentes | Estado |
|---|---|---|
| Frontend | `features/quant-lab` (QuantLabPage, LeadLagAnalysis, LeadLagHeatmap, LagProfileChart, RunRegistry) + `features/research` (lazy) | ✅ |
| Backend | `features/research` (lead-lag) | ✅ |
| Ação | Renomear "Quant Lab"/"Research" → **Assets Labs**. Já funcional | ✅ |

---

## 4. Navegação proposta (8 módulos, ordem de valor — Peter/Don)

Substitui os 6 grupos atuais ("Pesquisa/Operação/Estratégia/Registro/Patrimônio/Sistema") por
uma IA orientada ao **cliente-trader genérico**:

```
TCaM — Teczi Cockpit Assets Manager
├── 🔍 Assets Inspector     (/inspetor)        ✅ entender o ativo
├── 🧪 Assets Labs          (/lab, /research)  ✅ pesquisar padrões
├── 📋 Assets Strategy      (/strategies)      ✅ definir estratégia
├── 📊 Assets RunTests      (/backtest, /paper) ✅ validar por evidência
├── 🤖 Assets Experts       (/robots, /ea-control) ✅ rodar robôs MT5
├── 🛡️ Assets RiskManager   (/risk, kill-switch, /scaling) 🔧 proteger (configurável)
├── 🖥️ Assets Cockpit       (/, /order-gateway, /market-data) 🔧 operar/monitorar
├── 💼 Assets Manager       (/carteira-hard, /harvest, /ledger) ⚠️ gerir carteira
└── ⚙️ Configurações        (/settings)        ✅ mantém
```

**Remove da nav:** "Constituição" (`/constitution`) — ver `CONSTITUTION-DECOMMISSION.md §4.1`.

**Itens de disciplina pessoal a reavaliar (⚖️ FOUNDER #4):** `journal`, `fiscal`, `harvest`,
`carteira-hard`, `checklists`. Candidatos a: (a) feature opcional do produto, (b) absorvidos por
Assets Manager, ou (c) fora do MVP comercial.

---

## 5. Features sem módulo direto (decidir destino)

| Feature | Hoje | Destino proposto |
|---|---|---|
| `ai_analyst` | IA auditora/analista | Capacidade transversal — pode virar "Assets AI" futuro ou enriquecer Inspector/Cockpit. **Cuidado regulatório** (Kevin §7): IA não pode "prometer lucro" |
| `journal` | Diário de operações | Feature opcional / Assets Manager (⚖️ FOUNDER #4) |
| `fiscal` + `ledger` (DARF BR) | Apuração fiscal pessoal | Diferencial BR de produto OU bagagem pessoal (⚖️ FOUNDER #4) |
| `checklists` | Ritual pré/pós mercado | Feature opcional de disciplina configurável |
| `notifications` | Telegram/alertas | Capacidade transversal — mantém |
| `constitution` | Documento soberano | **REMOVER** (§4.1 do decommission) |
| `profit_integration` | Broker Profit | **Standby** (MT5 é o ativo) |

---

## 6. Resumo executivo do mapa

- **5 de 8 módulos** prontos ou quase (Inspector ✅, Labs ✅, Strategy ✅, RunTests ✅, Experts ✅).
- **2 módulos** precisam consolidação/conversão (RiskManager 🔧, Cockpit 🔧, Manager ⚠️).
- **Nenhum módulo nasce do zero** → favorece a restrição #1 do Founder (app rodando rápido).
- **Trabalho real da Fase 1:** rebrand + recompor navegação + converter Risk de trava→config +
  remover feature `constitution` + descomissionar Constituição. **É majoritariamente
  recomposição, não construção nova.**

---

*Documento de planejamento. Nenhuma alteração de código executada. Aguarda revisão do Founder.*

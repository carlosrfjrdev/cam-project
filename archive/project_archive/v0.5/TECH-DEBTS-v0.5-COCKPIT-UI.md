---
template: TECH-DEBTS
demand: PLAN-v0.5-COCKPIT-UI
date: 2026-05-30
author: Nikola (CODE autônomo)
status: Para avaliação do Founder
---

# Débitos Técnicos — v0.5 COCKPIT-UI

> Gerados ao final do desenvolvimento autônomo das 23 TASKs (U001–U023).
> **Nenhum** débito viola a Constituição. Todos os caminhos são read/seguros —
> nenhuma tela ou endpoint submete ordem (Art. 35º), Risk Engine intocado,
> `REAL_TRADING_ALLOWED=false`.

## Resumo da entrega

| Bloco | TASKs | Testes |
|---|---|---|
| BL-UI-0 (borda HTTP) | U001–U008 | backend 713 → **749** (+36) |
| BL-UI-1..5 (frontend) | U009–U023 | frontend 12 → **63** (+51) |
| **Total** | 23 TASKs | **812 testes verdes** |

Lints: `import-linter` 2 kept / 0 broken · `ruff` (arquivos novos) limpo ·
`no-hardcode` (front) limpo · `tsc` limpo · `vite build` ok (ResearchPage em
chunk lazy isolado).

---

## Débitos — Backend (borda HTTP read-model Fase 0)

Os routers expõem o que a v0.4 construiu. Onde a v0.4 **ainda não persiste**
um dado, o endpoint retorna um read-model estável (estrutura pronta), nunca
inventa valor. Cada um vira persistência real numa demanda futura.

| ID | Onde | O que falta | Severidade |
|---|---|---|---|
| **TD-v0.5-ROBOTS** | `robot_orchestrator/routes.py` | Sem tabela `cam_robots`. `GET /robots` deriva read-model do Strategy Registry (1 estratégia = 1 robô prioridade 1). Persistência real de Robots (N estratégias, prioridade) é futura. | Média |
| **TD-v0.5-ADHERENCE** | `robot_orchestrator/routes.py` | Aderência por estratégia não persistida (vem do journal em produção). `GET /robots/{id}/adherence` retorna `individual/aggregate = null`. | Média |
| **TD-v0.5-PRICESERIES** | `research/routes.py` | Séries de preço não persistidas → `GET /research/correlation` retorna `correlation = null` + nota. `pair-trade-backtest` opera sobre séries do corpo (ok). | Baixa |
| **TD-v0.5-DIVCAL** | `fundamentals/routes.py` | `GET /dividends/calendar` sem fonte de proventos conectada (retorna `events: []`). | Baixa |
| **TD-v0.5-EASTATE** | `mt5_integration/routes.py` | Estado do EA (version/hash/paused/online) em memória (`_EA_STATE`), não persistido nem ligado a heartbeat real. Pause/Resume alteram só o flag local. | Média |
| **TD-v0.4-01** (herdado) | `fundamentals/` | `PlaceholderSource` com fixtures; scraping fundamentalista real pendente. | Baixa |
| **TD-v0.4-02** (herdado) | `ai_analyst/provider_governance` | OpenAI **bloqueado** por design até ADR formal. `workbench` retorna `OpenAINotEnabled`. (É proteção, não bug.) | — |

### Observação de lint (não-bloqueante)
O repositório backend tem ~211 avisos `ruff` **pré-existentes** em arquivos de
teste (E501, F401), fora do gate de CI atual (pytest passa sem ruff). Os
arquivos novos/editados da v0.5 estão limpos. `cam/api/main.py:168`
(import do `paper_trading`, 89 chars) é linha pré-v0.5.

---

## Débitos — Frontend

| ID | Onde | O que falta | Severidade |
|---|---|---|---|
| **TD-v0.5-RECHARTS** | `research/ResearchPage.tsx` | Recharts **não está no stack** (offline; decisão de dependência é do Founder/Grace). Correlação/spread usam placeholder SVG/CSS. Instalar `recharts` e trocar a visualização (estrutura de dados já pronta). | Média |
| **TD-v0.5-BUNDLE** | build | Bundle principal **660 kB** (> 500 kB warning). Aplicar `manualChunks` / mais code-splitting (MUI + react-query). | Baixa |
| **TD-v0.5-FONTS** | `index.html` | Fontes via Google Fonts **CDN** (online). O cockpit é local/offline-first → migrar para `@fontsource` self-hosted quando houver instalação de deps. | Baixa |
| **TD-v0.5-ENVENDPOINT** | `useEnvironment.ts` | Consulta `/dashboard/environment` que pode não existir → fallback seguro para `DEMO` (nunca REAL). Criar endpoint de ambiente real no backend. | Média |
| **TD-v0.5-TOKENS-TEST** | `tokens.test.ts` | Lint `no-hardcode` roda como script standalone (`npm run lint:no-hardcode`), não dentro do Vitest, por ausência de `@types/node`. Integrar ao CI front. | Baixa |
| **TD-v0.5-V06-INFER** | telas | Telas de features fora da v0.4 (inferência/revisão ampla) ficaram para a **v0.6** por decisão do Founder (SPEC §1.3/§2.3). | — (planejado) |

---

## O que NÃO é débito (decisões corretas, registradas)

- `REAL_TRADING_ALLOWED=false`, `MULTI_STRATEGY_ENABLED=false`,
  `SCALING_ENABLED=false` — **default constitucional**, não pendência.
- Nenhuma UI envia ordem nem liga real — **garantia**, testada (Kevin):
  `test_no_order_submission_endpoint`, `test_endpoint_is_read_only`,
  `test_no_submit_order_via_ea_endpoint`, `test_no_order_action`,
  `test_no_submit_action_in_ui`.
- Policy Engine **sugere, nunca bloqueia** (R-13) — `blocking: false` fixo.
- `cam_risk_mirror.mq5` continua o único autorizado a `OrderSend`.

---

## Recomendações de priorização (sugestão de Nico)

1. **Antes de paper trading real:** TD-v0.5-EASTATE + TD-v0.5-ENVENDPOINT
   (estado/ambiente reais antes de qualquer operação).
2. **Para a v0.6 (inferência de telas):** TD-v0.5-RECHARTS + TD-v0.5-ADHERENCE
   + TD-v0.5-ROBOTS (research e orquestração ganham profundidade visual).
3. **Higiene:** TD-v0.5-BUNDLE, TD-v0.5-FONTS, TD-v0.5-TOKENS-TEST,
   limpeza ruff dos testes backend (demanda própria de qualidade).

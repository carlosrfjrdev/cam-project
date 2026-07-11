---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-003 — React 19 + Vite + MUI como Frontend (SPA Local, sem Next.js)

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-003-react-vite-mui-frontend.md`

---

## 1. Contexto

O CaM Cockpit precisa de interface operacional local que:
- exiba P&L líquido em tempo real (Art. 25º — nunca bruto)
- tenha kill switch sempre acessível em qualquer tela (Art. 18º)
- seja SPA local servida pelo backend FastAPI (`/static/cockpit/`) — sem servidor separado
- rode exclusivamente em localhost (sem autenticação, sem cloud)
- seja mono-usuário por design

A stack Teczilabs (Monnezy) usa React + Vite + MUI — alinhamento legítimo neste caso pois o domínio de frontend do cockpit é análogo: SPA local, componentes MUI, TypeScript.

**Por que não Next.js:** o CaM não tem necessidade de SSR (Server-Side Rendering). É um cockpit local mono-usuário — SSR adiciona complexidade de deploy, build pipeline e conceitos de servidor que não fazem sentido em uma SPA local. Next.js é over-engineering para este caso.

---

## 2. Decisão

Frontend do CaM Cockpit: React 19 + Vite + MUI (SPA local). Stack completa:

| Componente | Tecnologia | Versão alvo |
|---|---|---|
| Framework | React | 19.x |
| Build tool | Vite | 6.x |
| Linguagem | TypeScript | 5.x |
| UI Library | MUI (Material UI) | 6+ ou 7 |
| Estado global | Zustand | 5.x |
| Estado server | TanStack Query | 5.x |
| Roteamento | React Router | 6.x |
| Gráficos candles | TradingView Lightweight Charts | 4.x |
| Gráficos métricas | Recharts | 2.x |
| Validação cliente | Zod | 3.x |
| Streaming | WebSocket nativo (browser) | — |
| Gerência de deps | pnpm | 9.x |

**Arquitetura frontend:** Vertical Slice espelhando o backend (`src/features/{nome}/`). Mesma regra: `features/X/` não importa `features/Y/`.

**Servida pelo backend:** FastAPI serve os assets estáticos do Vite build em produção. Em desenvolvimento, Vite dev server com proxy para backend local.

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Next.js | SSR é desnecessário para SPA local mono-usuário; adiciona complexidade de routing App Router, server components, e build pipeline sem benefício real |
| 2 | Vue.js + Vuetify | Válido tecnicamente, mas sem alinhamento com stack Teczilabs; sem motivo objetivo para diferenciar |
| 3 | Svelte/SvelteKit | Menor ecosystem de componentes de trading (TradingView charts tem melhor suporte em React); menos familiar para desenvolvimento agêntico |
| 4 | Electron | Overhead de app desktop completo para um cockpit que já é local; sem justificativa de empacotamento |
| 5 | HTML/CSS/JS puro | Inviável para a complexidade dos dashboards operacionais e gráficos em tempo real |

---

## 4. Consequências

### Positivas
- Alinhamento com stack Teczilabs (React/Vite/MUI) — reutilização de conhecimento e componentes
- TradingView Lightweight Charts é o padrão da indústria para gráficos de candle — open source, excelente performance
- Vite é significativamente mais rápido que Webpack/CRA para desenvolvimento
- Zustand é minimalista — sem boilerplate Redux para estado simples de cockpit
- TanStack Query simplifica cache e sincronização com backend
- TypeScript garante contratos com o backend (OpenAPI → geração de tipos)
- Vertical Slice no frontend espelha o backend — consistência e compreensão agêntica

### Negativas
- Sem SSR — SEO não é relevante (cockpit local), mas se eventualmente publicado precisaria de migração
- TradingView Lightweight Charts não tem todos os indicadores nativamente — alguns precisariam ser implementados manualmente

### Neutras
- Build Vite produz assets estáticos servidos por FastAPI — sem processo separado em produção
- MUI v6/v7 tem breaking changes entre versões — travar em uma versão específica no início

---

## 5. Custo de Reversão

**Médio** — o frontend é a camada de apresentação; toda lógica de negócio está no backend. Migrar de React para outro framework é custoso em UI, mas não afeta Risk Engine, journal, fiscal ou backtest.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.5
- ADRs relacionadas: ADR-013 (Vertical Slice — frontend também segue)

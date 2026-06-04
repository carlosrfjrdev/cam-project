---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-013 — Feature-Based Vertical Slice Architecture + Shared Kernel Mínimo

> **Data:** 2026-05-24
> **Status:** Aceita — revoga arquitetura hexagonal proposta na versão 0
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-013-vertical-slice-shared-kernel.md`

---

## 1. Contexto

Uma proposta anterior de arquitetura sugeria arquitetura hexagonal (ports & adapters) para o backend do CaM. Esta ADR revoga essa proposta.

O CaM é desenvolvido com suporte significativo de agentes de IA (Claude Code, personas NCC-1701). A arquitetura hexagonal, embora válida para sistemas complexos com múltiplos adapters de infra, apresenta problemas sérios para desenvolvimento agêntico:

- Em hexagonal, entender uma feature requer navegar entre `domain/`, `application/`, `infra/` — frequentemente em pastas distintas que crescem com N features
- Um agente precisaria ler múltiplos diretórios para entender uma feature completa
- Mudanças em uma feature tocam múltiplas camadas em locais diferentes
- Abstrações prematuras (ports, interfaces, use-cases ceremoniais) antes de haver razão real

Adicionalmente, o CaM tem um elemento constitucional único: o Risk Engine é autoridade transversal. Em vertical slice puro, não há mecanismo claro para forçar que toda feature consulte uma autoridade central — o Shared Kernel mínimo resolve isso.

---

## 2. Decisão

O backend e o frontend do CaM Cockpit adotam **Feature-Based Vertical Slice Architecture com Shared Kernel mínimo**.

### Backend (`cam/`)

```
cam/
├── _shared/          # SHARED KERNEL — transversal e constitucional
│   ├── risk/         # Risk Engine (Pure Python, autoridade Art. 15º)
│   ├── domain/       # Primitivas: Money, ContractCount, Phase, AssetType
│   ├── events/       # Event bus interno (asyncio.Queue)
│   ├── audit/        # Audit logger transversal (structlog)
│   ├── infra/        # DB session factory, settings (pydantic-settings)
│   └── config/       # .env loader
│
├── features/         # VERTICAL SLICES — cada pasta é auto-contida
│   ├── journal/      # README.md + domain.py + schemas.py + repository.py + service.py + routes.py + events.py + tests/
│   ├── fiscal/
│   ├── ledger/
│   ├── harvest/
│   ├── strategies/
│   ├── backtest/
│   ├── paper_trading/
│   ├── profit_integration/
│   ├── market_data/
│   ├── kill_switch/
│   ├── checklists/
│   ├── notifications/
│   ├── ai_analyst/
│   └── constitution/
│
└── api/              # FastAPI Composer — monta o app
    ├── main.py
    ├── lifespan.py
    ├── middleware.py
    └── websocket.py
```

### Frontend (`src/`)

```
src/
├── features/         # VERTICAL SLICES — espelhando backend
│   ├── cockpit/
│   ├── journal/
│   ├── risk-console/
│   ├── fiscal/
│   ├── backtest/
│   ├── paper-trading/
│   ├── harvest/
│   ├── carteira-hard/
│   ├── constitution/
│   └── settings/
├── _shared/          # Componentes, hooks, tipos transversais
├── api/              # Client da API (tipos derivados de OpenAPI)
└── app/              # Router root, providers, layout
```

### Regras Invioláveis (enforçadas por `import-linter` no CI)

1. `features/X/` NUNCA importa de `features/Y/` — sem exceção
2. Comunicação cross-feature somente via: `_shared/events/` (pub/sub), `_shared/` (kernel), composição em `api/`
3. `_shared/risk/` é autoridade — toda feature que toque execução chama `from cam._shared.risk import engine`
4. `_shared/risk/` NÃO importa de NADA além de stdlib Python (Zero I/O Policy — ADR-007)
5. `_shared/` cresce com fricção real — item entra no kernel somente se usado por 3+ features OU for mandato constitucional

### Convenção por Feature

Cada `features/{nome}/` tem:
- `README.md` — contrato obrigatório: propósito, I/O, eventos, artigos constitucionais, anti-padrões
- `domain.py` — entidades e value objects da feature
- `schemas.py` — Pydantic in/out
- `repository.py` — acesso a dados (SQLAlchemy)
- `service.py` — lógica de aplicação
- `routes.py` — FastAPI router
- `events.py` — eventos publicados e handlers
- `tests/` — unit + integration

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Arquitetura hexagonal (ports & adapters) | Agente precisa navegar entre domain/application/infra para entender 1 feature; crescimento do projeto piora a navegação; abstrações prematuras sem adapter real diferente além de mock |
| 2 | Vertical Slice puro (sem Shared Kernel) | Risk Engine precisaria estar em `features/risk/` mas seria importado por outras features — viola a regra de que features não se importam |
| 3 | MVC clássico | Mistura features diferentes na mesma camada (models/, controllers/, views/); não escala bem para N features com responsabilidades distintas |

---

## 4. Consequências

### Positivas
- Agente lê 1 pasta para entender 1 feature — menos tokens, menos drift de contexto
- Duas features podem ser desenvolvidas em paralelo sem conflito de arquivos
- README.md por feature = onboarding por feature: "como funciona o journal?" → ler 1 arquivo
- Shared Kernel explícito evita que `_shared/` vire lixão — critério claro de entrada
- Import-linter detecta qualquer violação de acoplamento no CI

### Negativas
- Duplicação intencional em alguns casos: code que seria "fatorado" em hexagonal fica duplicado em cada feature (mas é preferível à acoplamento errado)
- Equipes com background em hexagonal precisam de ajuste mental para aceitar duplicação conscientemente

### Neutras
- Frontend também segue Vertical Slice — consistência backend↔frontend de organização

---

## 5. Custo de Reversão

**Alto** — reorganizar de Vertical Slice para hexagonal exigiria mover código de N features para camadas transversais, criando múltiplos conflitos de arquivos e re-importações. Decisão de fundação.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §1 (diagrama de arquitetura)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.2
- ADRs relacionadas: ADR-007 (Risk Engine no Shared Kernel), ADR-002 (Python+FastAPI como backend)

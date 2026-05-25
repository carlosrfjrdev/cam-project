---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-011 — Monorepo Único apps/cam-cockpit/ no MVP

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-011-monorepo-cam-cockpit.md`

---

## 1. Contexto

O CaM Cockpit possui três componentes distintos: backend Python, frontend React e estratégias NTSL. Esses componentes podem viver em repositórios separados ou em um monorepo.

O projeto é mono-operador, mono-usuário e não tem equipe separada para cada componente. A fase atual (Fase 0 — Construção) é de construção de fundação — não há produto em produção ainda.

---

## 2. Decisão

**Monorepo único** em `apps/cam-cockpit/` no MVP. Separação em repositórios distintos somente quando houver justificativa real (ex: o NTSL precisar de ciclo de deploy completamente independente em Fase F4).

**Estrutura do monorepo:**

```
apps/cam-cockpit/
├── backend/         ← Python 3.12 + FastAPI
├── frontend/        ← React 19 + Vite + MUI
├── ntsl/            ← Estratégias NTSL versionadas
├── scripts/         ← dev.sh, dev.ps1, backup.sh, import_profit_csv.py
└── docker-compose.yml
```

**Repositório Git:** `github.com/carlosrfjr/cam-cockpit` (privado) — criado quando o primeiro commit de código ocorrer (atualmente o repo raiz CaM-project não é um repositório Git, conforme verificado em 2026-05-24).

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Repositório separado por componente (backend, frontend, ntsl) | Overhead de 3 repos, 3 CI/CD configs, 3 PRs coordenados para mudanças cross-componente; sem benefício para mono-operador |
| 2 | Tudo no mesmo repositório raiz CaM-project (sem separação) | Misturaria artefatos DevFlow (`/project`) com código (`/apps`); viola a separação conceitual NCC-1701 §9.3 |

---

## 4. Consequências

### Positivas
- Um único `git clone` para ter todo o ambiente
- Mudanças cross-componente (backend + frontend + NTSL) em um único PR
- Simplifica CI/CD futuro (uma pipeline, não três)
- Consistência de versioning (backend e frontend sempre em sincronia)

### Negativas
- Se o NTSL precisar de deploy independente do backend em Fase F4, exigirá configuração adicional de paths no monorepo

### Neutras
- Separação em repos pode vir depois, quando houver dor real justificando o overhead

---

## 5. Custo de Reversão

**Baixo** — separar um monorepo em repos distintos é custoso em histórico de git mas não afeta o código em si. Decisão reversível com custo de migração.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §8 (estrutura de repositórios)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §8
- CLAUDE.md raiz: separação `/apps` × `/project`

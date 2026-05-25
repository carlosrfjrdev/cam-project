# /apps — Aplicativos do CaM

Diretório raiz dos aplicativos que compõem o cockpit **CaM (The Carlos Alternative Money)**.

## Convenção

Estrutura monorepo recomendada para o MVP (Fase 0–2), conforme [`../project/STACK-CAM-OFICIAL.md`](../project/STACK-CAM-OFICIAL.md):

```
apps/
└── cam-cockpit/                  # Monorepo único no MVP
    ├── backend/                  # Python 3.12 + FastAPI
    │   └── cam/
    │       ├── _shared/          # SHARED KERNEL (risk, domain, events, audit, infra)
    │       ├── features/         # VERTICAL SLICES (journal, fiscal, ledger, ...)
    │       └── api/              # FastAPI composer
    ├── frontend/                 # React 19 + Vite + MUI (SPA local)
    │   └── src/
    │       ├── _shared/
    │       ├── features/         # VERTICAL SLICES também no frontend
    │       └── app/
    ├── ntsl/                     # Estratégias e regras espelhadas em NTSL (Profit)
    ├── scripts/                  # dev / backup / import_profit_csv
    ├── docker-compose.yml        # Postgres 16 + TimescaleDB — ATIVO desde Fase 0
    └── README.md
```

**Arquitetura: Feature-Based Vertical Slice + Shared Kernel mínimo** (ADR-013). Cada feature é uma pasta auto-contida (`domain`, `schemas`, `service`, `routes`, `events`, `tests`). Regra inviolável: `features/X/` **nunca** importa `features/Y/` — comunicação cross-feature só via `_shared/` ou eventos. Otimizado para desenvolvimento agêntico (agente lê uma pasta, não seis).

Separação em múltiplos apps só acontece se justificar (volume, isolamento de deploy). No MVP, monorepo único reduz fricção.

Nada está criado ainda — Fase 0 do CaM (`../CONSTITUICAO.md` Anexo II) é a fase de construção do cockpit.

## Regras

- **Stack vigente:** [`../project/STACK-CAM-OFICIAL.md`](../project/STACK-CAM-OFICIAL.md). **Revoga** os Combos A/B/C do catálogo Teczilabs (Java/Spring, Firebase, Next.js, MongoDB) — esses não se aplicam ao CaM.
- **Constituição vence:** todo aplicativo deve respeitar a hierarquia `Constituição > Risk Engine > Estratégia validada > IA > Operador` (Art. 36º).
- **Risk Engine soberano:** nenhum app pode enviar ordem sem autorização do Risk Engine (Arts. 15º e 35º).
- **Kill switch obrigatório:** todo app que toque execução deve expor mecanismo de interrupção imediata (Art. 18º).
- **AI vedada na execução:** IA não envia ordem, não desabilita/parametriza Risk Engine, não justifica exceção constitucional (Art. 35º).
- **Provisão fiscal em tempo real:** UIs operacionais exibem resultado **líquido de imposto provisionado**, nunca bruto (Art. 25º).
- **Cobertura de testes do Risk Engine ≥ 80%** é critério de saída da Fase 0 (Anexo II).

## Ciclo de criação de um app

Toda criação de aplicativo passa pelo DevFlow NCC-1701:

1. **PDOC** (Leo/Denis) → registra app em `/project/{codinome}/` e cria pasta aqui em `/apps/{codinome}/`.
2. **DISC → SPEC → ARCH → PLAN → CODE → QA → DEPLOY → SDOC** conforme proporcionalidade P/M/G.
3. Artefatos de processo ficam em `/project/{codinome}/`; código em `/apps/{codinome}/`.

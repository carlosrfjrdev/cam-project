# /project — Artefatos DevFlow por demanda

Diretório raiz dos artefatos de processo produzidos pelo **Teczi DevFlow NCC-1701** ao longo da construção do CaM.

Aqui mora a **intenção viva** (o que está sendo feito). O **estado real** (código construído) mora em [`/apps`](../apps/).

## Documentos canônicos no momento

| Documento | Conteúdo | Status |
|---|---|---|
| [`STACK-CAM-OFICIAL.md`](./STACK-CAM-OFICIAL.md) | Stack — variante **Windows + Profit/NTSL** | Proposto |
| [`STACK-CAM-OFICIAL-LINUX.MD`](./STACK-CAM-OFICIAL-LINUX.MD) | Stack — variante **Linux + MetaTrader 5** | Proposto |

**Decisão pendente do Founder:** escolher entre Windows+Profit OU Linux+MT5. Matriz comparativa explícita está na §13 do documento Linux+MT5. Quando a decisão for tomada, o documento não escolhido vai para `archive/`.

## Convenção de pastas

```
project/
├── cam-cockpit/                      # Projeto-mãe do cockpit
│   ├── PDOC/                         # Registro de criação do projeto
│   ├── SCOPE.md                      # Recorte In/Out/Later (Marty)
│   ├── DVP.md                        # Documento de Visão de Produto (Albert)
│   ├── DAS.md                        # Documento de Arquitetura de Solução (Oscar)
│   ├── adrs/                         # ADRs numeradas (Oscar)
│   └── demands/
│       ├── DEM-001-risk-engine-mvp/  # Cada demanda em sua pasta
│       │   ├── SPEC.md
│       │   ├── PLAN.md
│       │   ├── PROOF-PACK.md         # Conforme regra P/M/G (Cap. 14 do process.md)
│       │   ├── BUG/                  # Estado BUG (Bill) quando aplicável
│       │   └── OPS/                  # Estado OPS (Vint) quando aplicável
│       └── DEM-002-...
└── devflow/                          # Artefatos sobre o próprio DevFlow (meta)
```

## Princípio: `project` vs `codex`

(Decisão NCC-1701 §9.3)

- **`/project`** — memória do que **está sendo feito** (intenção + artefatos vivos do DevFlow).
- **`/apps`** — memória do que **foi feito** (estado real do software + doc as-is futura).

Quando o Codex Stage 1+ existir, esta separação física vira separação de domínios tecnológicos. Até lá, é organização disciplinada de pastas.

## Regras de produção

- **Founder-only nos gates** (NCC-1701 §7) — nada avança sem aprovação explícita de Carlos.
- **Proof Pack proporcional** (NCC-1701 §14): P opcional · M recomendado · G/release/incidente/arch obrigatório. Template em [`../teczi-devflow/NCC-1701/templates/PROOF-PACK.md`](../teczi-devflow/NCC-1701/templates/PROOF-PACK.md).
- **Sem estimativas em horas/dias/semanas** — apenas P/M/G (proibição explícita do Founder, NCC-1701 §1 e Q8).
- **Estado real vence intenção** — quando `codex` e `project` divergirem, código manda. DRIFT só por solicitação explícita (Howard).
- **SDOC sob demanda** — apenas em release final elegível ou solicitação explícita (Q11).
- **Reuso antes de criação** — antes de criar SCOPE/SPEC/PLAN/ADR novo, procurar decisão/artefato/padrão/componente já existente.

## Templates disponíveis

Todos em [`../teczi-devflow/NCC-1701/templates/`](../teczi-devflow/NCC-1701/templates/):

`SCOPE.md` · `DVP.md` · `DAS.md` · `ADR.md` · `INFRA-ARCH.md` · `SPEC.md` · `PLAN.md` · `BUG.md` · `OPS-EVENT.md` · `CHANGE-RECORD.md` · `DRIFT-REPORT.md` · `PROOF-PACK.md`

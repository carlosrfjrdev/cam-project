# Templates — NCC-1701

> Templates são **moldes** para artefatos reais produzidos durante operação. Cada produto Teczilabs reaproveita esses templates copiando para `/projects/{produto}/...` e preenchendo.

## Catálogo

| Template | Fase/Estado/Gov de origem | Função |
|---|---|---|
| [SCOPE.md](SCOPE.md) | DISC | Recorte de demanda In/Out/Later + perguntas abertas |
| [DVP.md](DVP.md) | DISC (refinado em SPEC) | Documento estratégico de produto |
| [DAS.md](DAS.md) | ARCH | Documento de Arquitetura de Solução |
| [ADR.md](ADR.md) | ARCH | Architecture Decision Record |
| [INFRA-ARCH.md](INFRA-ARCH.md) | ARCH (co-autoria Vint) | Decisões de infra |
| [SPEC.md](SPEC.md) | SPEC | Especificação da demanda + classificação P/M/G |
| [PLAN.md](PLAN.md) | PLAN | Plano proporcional, com TASKs se G |
| [BUG.md](BUG.md) | Estado BUG | Artefato único fast-track |
| [OPS-EVENT.md](OPS-EVENT.md) | Estado OPS | **Mínimo:** data · evento · impacto · decisão · ação · rollback (opcional) · aprendizado |
| [CHANGE-RECORD.md](CHANGE-RECORD.md) | DEPLOY (governança CHANGE) | Registro de mudança |
| [DRIFT-REPORT.md](DRIFT-REPORT.md) | SDOC sob solicitação | Divergência intenção × estado real |
| [PROOF-PACK.md](PROOF-PACK.md) | Pós-demanda M/G ou release final/incidente/arch change | Evidência operacional acumulada |

## Como usar

1. Copie o template para o diretório do produto (`/projects/{produto}/...`).
2. Renomeie com identificador (ex.: `SCOPE-DEMAND-001.md`, `BUG-001.md`).
3. Preencha as seções obrigatórias; remova as opcionais não aplicáveis.
4. Sempre que houver decisão, registrar explicitamente quem decidiu (Founder).

## Regra geral de não-uso

Cada template traz, ao final, a regra explícita de **quando NÃO usar**. Respeitar essas regras é mais importante que copiar o template.

## Estimativas — proibidas

Nenhum template aceita estimativa em horas/dias/semanas. Founder explicitamente proíbe.

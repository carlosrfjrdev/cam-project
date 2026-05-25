# Fase 03 — ARCH (Architecture)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Oscar (Vint co-autor para INFRA-ARCH)
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 3)

## 1. Propósito

Definir arquitetura da demanda, registrar decisões irreversíveis ou caras (ADRs) e produzir INFRA-ARCH quando há impacto operacional.

## 2. Quando rodar

- **Sempre que a demanda altera a arquitetura existente** (camadas, contratos públicos, integração, infra, dados).
- **Skip** quando o impacto é local e respeita a arquitetura vigente.

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Skip se sem impacto | Condicional por impacto | Recomendado quando há impacto |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| SCOPE.md aprovado | DISC | sim |
| DVP vigente do produto | DISC | quando houver |
| DAS vigente do produto | ARCH anterior | quando houver |
| ADRs vigentes | Histórico | quando houver |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `DAS.md` (novo ou atualizado) | [`../templates/DAS.md`](../templates/DAS.md) | `/projects/{produto}/architecture/` |
| `ADR-{id}.md` quando aplicável | [`../templates/ADR.md`](../templates/ADR.md) | `/projects/{produto}/architecture/adrs/` |
| `INFRA-ARCH.md` quando há impacto operacional | [`../templates/INFRA-ARCH.md`](../templates/INFRA-ARCH.md) | `/projects/{produto}/infra/` |
| Threat model lógico (se superfície sensível) | — | Anexo do DAS ou SEC-GOV |

## 5. Personas

- **Lead:** Oscar (Solution Architecture)
- **Co-lead:** Vint para INFRA-ARCH
- **Cross-cutting:** Kevin se há superfície de segurança (auth, dados, integração externa, infra)

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** DAS coerente com decisão; ADRs registradas; INFRA-ARCH presente se aplicável.
- **Critério de retorno:** decisão arquitetural sem rationale claro ou conflitando com ADR vigente sem deprecation explícita.

## 7. Skill associada

[`../skills/teczi-architecture-decision.md`](../skills/teczi-architecture-decision.md)

## 8. Operação manual (Stage 0)

1. Oscar lê SCOPE e identifica impacto arquitetural.
2. Oscar propõe decisão técnica + alternativas consideradas.
3. Se decisão irreversível/cara: registrar ADR.
4. Se impacto operacional: Vint colabora em INFRA-ARCH.
5. Se superfície sensível: Kevin produz threat model lógico.
6. Founder aprova → ARCH concluída.

## 9. Anti-padrões

- ADR para decisão trivial (ADR é para irreversível/cara).
- DAS que descreve "como está" — DAS é decisão, não inventário (inventário é SDOC/Howard).
- Decidir infra sem Vint.
- Ignorar Kevin quando há auth/dados/integração externa.

## 10. Referências

- SCOPE-FINAL §6.1
- Skill: [`../skills/teczi-architecture-decision.md`](../skills/teczi-architecture-decision.md)
- Templates: [`../templates/DAS.md`](../templates/DAS.md), [`../templates/ADR.md`](../templates/ADR.md), [`../templates/INFRA-ARCH.md`](../templates/INFRA-ARCH.md)
- Próxima fase: [`04-SPEC.md`](04-SPEC.md)

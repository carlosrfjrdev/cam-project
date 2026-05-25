# Fase 05 — PLAN (Planning)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Nico
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 5) + §7.1

## 1. Propósito

Planejar execução proporcional ao P/M/G atribuído na SPEC e resolver drift entre intenção (SPEC) e execução (CODE). Nico tem **direito formal** de criticar a classificação P/M/G de Albert.

## 2. Quando rodar

- **Toda demanda que produz código**, mas em granularidade proporcional.

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Embutido na SPEC ou curto | PLAN separado | PLAN + TASKs por bloco |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| SPEC.md aprovada | SPEC | sim |
| DAS vigente | ARCH | quando aplicável |
| ADRs aplicáveis | ARCH | quando aplicável |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `PLAN.md` da demanda | [`../templates/PLAN.md`](../templates/PLAN.md) | `/projects/{produto}/demands/{id}/` |
| Marca `letscode` (gate final de PLAN) | Campo dentro do PLAN | — |
| TASKs sequenciais se G | Subseções do PLAN | — |
| Re-classificação P/M/G se Nico identificar gargalo | Campo dentro do PLAN, com rationale | — |

### `letscode`

Marco final do PLAN. Indica que a SPEC + PLAN estão prontas para entrar em CODE.

## 5. Personas

- **Lead:** Nico (Planning & Strategy)
- **Co-lead:** Albert (loop ilimitado até consenso sobre P/M/G)
- **Cross-cutting:** —

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** PLAN proporcional, `letscode` aceso, drift SPEC↔PLAN resolvido.
- **Critério de retorno:** PLAN cerimonial (excede a demanda) ou raso demais (não cobre os blocos).

## 7. Skill associada

[`../skills/teczi-code-planning.md`](../skills/teczi-code-planning.md)

## 8. Operação manual (Stage 0)

1. Nico lê SPEC aprovada.
2. Nico avalia P/M/G — concorda ou contesta com rationale.
3. Se contestação: loop com Albert (ilimitado até consenso, Founder decide quando parar).
4. Nico produz PLAN proporcional:
   - P: embutido na SPEC ou plano curto.
   - M: PLAN separado, blocos contidos.
   - G: PLAN + TASKs sequenciais.
5. Nico marca `letscode` → Founder valida.
6. Founder aprova → CODE pode iniciar.

## 9. Anti-padrões

- PLAN com estimativa em horas/dias/semanas — **proibido** (memória `feedback-nunca-inferir-estimativas`).
- PLAN cerimonial em demanda P.
- Skip do loop Albert-Nico em P/M/G claramente ambíguo.
- `letscode` sem aprovação explícita do Founder.

## 10. Referências

- SCOPE-FINAL §6.1 e §7.1
- Skill: [`../skills/teczi-code-planning.md`](../skills/teczi-code-planning.md)
- Template: [`../templates/PLAN.md`](../templates/PLAN.md)
- Próxima fase: [`06-CODE.md`](06-CODE.md)

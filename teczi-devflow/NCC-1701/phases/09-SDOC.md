# Fase 09 — SDOC (Software Documentation)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Denis (pós-fluxo) + Howard (arqueologia / DRIFT sob solicitação)
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 9) + §12 + Q11 + Q12

## 1. Propósito

Documentar o **estado real** do software após o fluxo. Não substitui artefatos de intenção (DVP/DAS/SPEC/PLAN) — registra o que efetivamente existe no código deployado.

## 2. Quando rodar

SDOC **não roda em toda demanda**. Roda **apenas** quando:

- há **versão final elegível para release**; **ou**
- Founder/operador **solicita explicitamente**.

(Q11 Founder)

DRIFT-REPORT (Howard) roda **apenas** por solicitação explícita do Founder/operador. **Sem gatilhos automáticos, sem gatilhos "recomendados"** (Q12 Founder).

Aplicação por P/M/G:

| P | M | G |
|---|---|---|
| Apenas se Founder pedir ou release final | Idem | Idem |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| Código deployado | DEPLOY | sim |
| Repositório do produto | — | sim |
| SPEC + PLAN da demanda (para comparação intenção × real) | SPEC, PLAN | condicional |
| Solicitação explícita do Founder (se SDOC sob demanda) | Founder | sim para esse caso |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| Documentação as-is do software | — (Denis estrutura conforme produto) | `/teczi-codex/` (futuro) ou `/projects/{produto}/codex/` (Stage 0) |
| `DRIFT-REPORT.md` (quando Howard solicitado) | [`../templates/DRIFT-REPORT.md`](../templates/DRIFT-REPORT.md) | `/projects/{produto}/drift/` |

## 5. Personas

- **Lead:** Denis (pós-fluxo, documentação organizada)
- **Co-lead:** Howard (arqueologia, DRIFT-REPORT sob solicitação)
- **Cross-cutting:** —

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** documentação reflete estado real; drift declarado se houver (e direção de reconciliação decidida).
- **Critério de retorno:** documentação ainda descreve intenção em vez de realidade.

## 7. Skill associada

[`../skills/teczi-software-documentation.md`](../skills/teczi-software-documentation.md)

## 8. Operação manual (Stage 0)

1. Founder ativa SDOC (ou já é release final elegível).
2. Denis estrutura documentação as-is do produto.
3. Se Founder solicitou Howard: Howard mapeia drift entre `project` (intenção) e `codex` (real).
4. Drift é registrado em DRIFT-REPORT com direção de reconciliação proposta.
5. Founder decide: ajustar código ou ajustar intenção (princípio 7: estado real vence quando faz sentido).
6. Founder valida → SDOC concluída.

## 9. Anti-padrões

- Rodar SDOC em toda demanda — gera documentação nobre sem consumo.
- Rodar DRIFT-REPORT automaticamente após DEPLOY — Q12 Founder proíbe.
- Listar gatilhos "recomendados" para DRIFT — descartado intencionalmente (ajuste GPT-PARECER §4.2 não incorporado).
- SDOC que descreve intenção em vez de estado real — isso é DVP/DAS, não SDOC.

## 10. Referências

- SCOPE-FINAL §6.1, §12, Q11, Q12
- Skill: [`../skills/teczi-software-documentation.md`](../skills/teczi-software-documentation.md)
- Template: [`../templates/DRIFT-REPORT.md`](../templates/DRIFT-REPORT.md)
- Princípio: SCOPE-FINAL §4 (7) "Estado real vence"
- Estados relacionados: [`../states/OPS.md`](../states/OPS.md)
- Fim do fluxo numerado.

---
template: TASK
task_id: TASK-044
block: BL-H1
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.01]
covers_ca: [CA-H1.2, CA-H1.3, CA-H1.4]
features: [F-15]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-043]
---

# TASK-044 — `conflict_resolver.py` (POV §3.11) + property-based testing

## Objetivo

Implementar POV §3.11 (Resolução de Conflitos) com **6 cenários determinísticos**:
- Mesma direção/mesmo ativo → vence maior expectância 30d (CA-H1.2)
- Direção oposta/mesmo ativo → ambos rejeitados, audit `DIRECTIONAL_CONFLICT` (CA-H1.3)
- Empate de expectância dentro de 5% → ambos rejeitados, audit `AMBIGUOUS_TIE` (CA-H1.4)
- Ativos diferentes → ambos seguem para `aggregate_risk_check` (T045)
- Estratégia individual suspensa (gain lock / aderência) → skip antes do resolver
- 1 só candidato → passa direto

## TDD First (Red)

1-6. Um teste por cenário acima.
7. **Property-based 10.000+ cenários** com Hypothesis: para qualquer combinação de candidatos válida, resolver retorna ≤ N candidatos (N = max contratos pelo ativo) e **nunca** ambígua sem audit.

## Implementação alvo (Green)

- Arquivo: `cam/features/robot_orchestrator/conflict_resolver.py::resolve(candidates, context) -> ResolutionResult`.

## Não-objetivos

- ❌ Calcular expectância (vem do journal stats — usa repositório existente).

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- Módulo + 7 testes (6 unitários + 1 property-based 10k cenários).

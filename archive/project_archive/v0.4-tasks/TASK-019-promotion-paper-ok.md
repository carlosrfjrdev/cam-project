---
template: TASK
task_id: TASK-019
block: BL-C
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R3.05]
covers_ca: [CA-C.5]
features: [F-16]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-003, TASK-016]
---

# TASK-019 — Promoção `paper_ok` (≥ 100 trades + aderência ≥ 95%)

## Objetivo

Promoção a `paper_ok` **só** ocorre se EvidencePack carrega ≥ 100 paper trades + aderência média ≥ 95%.

## TDD First (Red)

1. `test_promotion_to_paper_ok_fails_with_99_trades` — `EVIDENCE_INSUFFICIENT_TRADES`.
2. `test_promotion_to_paper_ok_fails_with_adherence_94`
3. `test_promotion_to_paper_ok_succeeds_with_100_trades_and_95_adherence`
4. `test_evidence_pack_assembled_from_cam_paper_trades_repository`
5. `test_promotion_emits_audit_event_with_evidence_pack_id`

## Implementação alvo (Green)

- Editar: `cam/features/strategies/promotion.py` — adicionar `validate_paper_ok_requirements(evidence_pack)`.
- Builder: `cam/features/paper_trading/evidence_builder.py::build_paper_evidence(strategy_id) -> EvidencePack`.

## Não-objetivos

- ❌ Promoção `demo_ok` (vem em SPEC futura após BL-E rodar 30 dias).

## Marcadores

- `sec`: true (governança de estado de produção).
- `qa-sec`: true.

## Saídas

- Patch + 5 testes verdes.

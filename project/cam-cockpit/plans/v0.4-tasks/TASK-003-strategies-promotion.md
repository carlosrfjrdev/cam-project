---
template: TASK
task_id: TASK-003
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.02, R1.03]
covers_ca: [CA-A.2]
features: [F-05]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-002]
---

# TASK-003 — Promotion + EvidencePack

## Objetivo

Promoção de status de estratégia exige `EvidencePack` válido — sem evidência, registry rejeita (R1.02).

## TDD First (Red)

1. `test_promote_without_evidence_pack_raises_EVIDENCE_REQUIRED`
2. `test_promote_with_invalid_evidence_pack_raises_EVIDENCE_INVALID` — Evidence Pack com listas vazias de backtest/paper.
3. `test_promote_to_paper_ok_requires_min_100_paper_runs` — pré-requisito mínimo testado isoladamente (a validação de aderência fica em T019).
4. `test_promote_skipping_status_raises_INVALID_TRANSITION` — `draft → demo_ok` falha; tem que passar por `backtested` e `walk_forward_ok`.
5. `test_evidence_pack_persisted_with_strategy_promotion` — Evidence Pack vira artefato consultável.

## Implementação alvo (Green)

- Arquivo: `cam/features/strategies/promotion.py` + `cam/features/strategies/evidence.py`.
- `EvidencePack` dataclass: `strategy_id, status_target, backtest_runs[], walk_forward_results[], paper_results[], adherence, drawdown, expectancy_net, custom_metrics{}`.
- Persistir em `cam_evidence_packs(id, strategy_id, status_target, payload_json, hash, created_at)`.
- `Registry.promote(strategy_id, to_status, evidence_pack_id)` valida + transiciona.

## Não-objetivos

- ❌ Cálculo de aderência (T016 produz `adherence` por trade; T019 consolida promoção `paper_ok`).
- ❌ Backtest engine (T008).

## Marcadores

- `sec`: true (governa estado de produção da estratégia).
- `qa-sec`: true.

## Saídas

- Migration `cam_evidence_packs` + `promotion.py` + testes verdes.

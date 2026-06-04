---
template: TASK
task_id: TASK-010
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.08]
covers_ca: [CA-A.6]
features: [F-08]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-009]
---

# TASK-010 — `scripts/lint_mql5.sh` (Order calls fora de `cam_risk_mirror.mq5` falham CI)

## Objetivo

Garantir, via lint determinístico, que `OrderSend(`, `OrderClose(`, `PositionOpen(`, `PositionClose(`, `OrderModify(` **só** apareçam em `cam_risk_mirror.mq5` (BL-E). Em BL-A, lint falha se aparecerem em `cam_bridge.mq5`.

## TDD First (Red)

1. `test_lint_fails_when_OrderSend_in_cam_bridge_mq5` — fixture com violação proposital → exit 1.
2. `test_lint_passes_when_OrderSend_only_in_cam_risk_mirror`
3. `test_lint_detects_OrderClose_PositionOpen_PositionClose_OrderModify`
4. `test_lint_skips_comments_and_strings` — `// OrderSend example` não dispara.
5. `test_lint_emits_machine_readable_output` — saída JSON consumível pelo CI.

## Implementação alvo (Green)

- Arquivo: `scripts/lint_mql5.sh` + helper `scripts/lint_mql5.py` (parsing AST-light com regex robusto contra comentários/strings).
- Allowlist hardcoded em variável: `ALLOWED_FILE="cam_risk_mirror.mq5"`.
- Integrar em CI (`Makefile` + GitHub Actions workflow).

## Não-objetivos

- ❌ Lint Python (T047 cuida do anti auto-edição).
- ❌ Build do `.ex5`.

## Marcadores

- `sec`: true (defesa estrutural CI).
- `qa-sec`: true.

## Saídas

- Script + testes verdes + workflow CI verde.

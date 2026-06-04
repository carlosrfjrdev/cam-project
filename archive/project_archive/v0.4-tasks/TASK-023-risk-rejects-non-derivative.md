---
template: TASK
task_id: TASK-023
block: BL-D
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R4.04]
covers_ca: [CA-D.4]
features: [F-10]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-020]
---

# TASK-023 — Risk Engine rejeita não-derivativo estruturalmente (Art. 23)

## Objetivo

Holdings **nunca** entram como margem. `risk.add_open_position(asset=PETR4)` deve levantar `InvalidAssetForRisk`.

## TDD First (Red)

1. `test_risk_rejects_PETR4_as_open_position` — `InvalidAssetForRisk`.
2. `test_risk_rejects_any_non_derivative_via_cam_instruments_lookup` — instrument com `asset_class != 'futures'` → reject.
3. `test_risk_accepts_WIN_WDO_as_open_position`
4. `test_error_message_references_constituicao_art_23`

## Implementação alvo (Green)

- Editar: `cam/_shared/risk/engine.py::add_open_position` — consultar `cam_instruments.asset_class`; só `futures` é aceito.
- Exceção customizada `InvalidAssetForRisk(asset, reason)`.

## Não-objetivos

- ❌ Cross-asset risk (BL-G, T028 não toca isso).

## Marcadores

- `sec`: true CRÍTICO.
- `qa-sec`: true.

## Saídas

- Patch + 4 testes verdes.

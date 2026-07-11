---
template: TASK
task_id: TASK-025
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.02]
covers_ca: [CA-E.4]
features: [F-12]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: []
---

# TASK-025 — `cam_risk_mirror.mq5` — 18 validators em MQL5

> **CRÍTICO** — 1ª linha de defesa MQL5 antes de `OrderSend`. Kevin obrigatório.

## Objetivo

Implementar **em MQL5** todos os 18 validators do Risk Engine Python com **paridade lógica**. EA recusa `OrderSend` se Mirror reprovar.

## TDD First (Red)

> Testes ficam em **T026** (paridade Python↔MQL5). Aqui, validamos compilação + execução isolada.

1. `test_mql5_compiles_without_warnings_or_errors` — `mql5_compile.exe` exit 0.
2. `test_each_validator_function_exists_and_returns_bool`
3. `test_validators_called_in_constitutional_order` — ordem do pipeline `MAPPING-CONSTITUICAO-RISK-ENGINE.md`.
4. `test_OrderSend_only_called_after_all_validators_returned_true`
5. `test_violation_logged_with_validator_name_and_reason`

## Implementação alvo (Green)

- Arquivo: `apps/cam-cockpit/mql5/cam_risk_mirror.mq5`.
- 18 funções MQL5 espelhando: `max_contracts_check`, `kill_switch_check`, `darf_pending_check`, `gain_lock_check`, `loss_lock_check`, `cooldown_check`, `pregao_window_check`, `darf_obstruction_check`, `aggregate_risk_check` (stub até T045), `scaling_eligibility_check` (stub até T050), e os demais 8 do pipeline atual.
- Lê **limite vigente** via `cam_bridge` REQ/REP (`GET_CURRENT_LIMITS`).
- Logging em arquivo `MQL5/Files/cam_risk_mirror.log`.

## Não-objetivos

- ❌ Testes de paridade (T026).
- ❌ `SUBMIT_ORDER` command no bridge (T027).

## Marcadores

- `sec`: true **CRÍTICO**. `qa-sec`: true **CRÍTICO**.

## Saídas

- `cam_risk_mirror.mq5` compila + 5 testes isolados verdes.

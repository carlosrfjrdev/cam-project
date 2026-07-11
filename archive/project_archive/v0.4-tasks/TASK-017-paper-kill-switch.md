---
template: TASK
task_id: TASK-017
block: BL-C
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: []
covers_ca: [CA-C.2]
features: [F-07]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-016]
---

# TASK-017 — Kill switch loop paper < 1s (Art. 18)

## Objetivo

Loop paper **DEVE** parar em < 1s ao receber sinal de kill switch via cockpit (Art. 18º obrigatório).

## TDD First (Red)

1. `test_kill_switch_stops_paper_loop_in_under_1s` — cronometrar; falha CI se > 1s.
2. `test_kill_switch_closes_open_position_at_market_price`
3. `test_kill_switch_emits_audit_event_with_reason`
4. `test_kill_switch_persists_partial_trades_before_stop`
5. `test_loop_cannot_be_resumed_without_explicit_command` — `RESUME_PAPER` distinto de `RESUME_EA`.

## Implementação alvo (Green)

- Editar: `cam/features/paper_trading/service.py` — adicionar `asyncio.Event` ou similar lido a cada iteração.
- Endpoint `POST /api/v1/kill-switch/paper` dispara o evento.
- Sinal SIGTERM no processo também aciona kill switch graceful.

## Não-objetivos

- ❌ Kill switch global EA (T030, BL-E).

## Marcadores

- `sec`: true CRÍTICO.
- `qa-sec`: true.

## Saídas

- Patch em `service.py` + 5 testes verdes + endpoint funcional.

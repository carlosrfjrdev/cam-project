---
template: TASK
task_id: TASK-009
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.05]
covers_ca: [CA-A.5]
features: [F-08]
status: Completed
sec: true
qa_sec: true
predecessors: []
---

# TASK-009 — `cam_bridge.mq5` Control Plane G2: PAUSE_EA / RESUME_EA / GET_VERSION

## Objetivo

Adicionar **comandos de controle** à whitelist REQ/REP do `cam_bridge.mq5` mantendo bridge **read-only** (sem `OrderSend`).

## TDD First (Red)

1. `test_pause_ea_stops_ontick_publication` — após `PAUSE_EA`, ticks não chegam por ≥ 5s.
2. `test_resume_ea_resumes_publication` — após `RESUME_EA`, ticks retornam em ≤ 1s.
3. `test_heartbeat_continues_when_paused` — Heartbeat segue mesmo com `OnTick` pausado.
4. `test_get_version_returns_version_and_hash` — formato `{"version": "1.2.0", "hash": "<sha256>"}`.
5. `test_unknown_command_returns_NOT_WHITELISTED`
6. **Integração:** subir bridge em MT5 demo, executar 3 comandos via cockpit Python, validar respostas.

## Implementação alvo (Green)

- Editar: `apps/cam-cockpit/mql5/cam_bridge.mq5`
- Adicionar handler ZeroMQ com switch case incluindo `PAUSE_EA`, `RESUME_EA`, `GET_VERSION`.
- Hash da versão calculado em build-time (script Python pré-deploy).
- Manter **whitelist explícita** — qualquer comando fora dela retorna erro.

## Não-objetivos

- ❌ `SUBMIT_ORDER` (T027, BL-E).
- ❌ `KILL_SWITCH_ACTIVATE` (T030, BL-E).
- ❌ Multi-instance (T058, BL-I).

## Marcadores

- `sec`: true (qualquer mudança em `cam_bridge.mq5` exige Kevin intrabloco).
- `qa-sec`: true.

## Saídas

- `cam_bridge.mq5` G2 + integration tests verdes + lint MQL5 (T010) passa.

---
template: TASK
task_id: TASK-051
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.11]
covers_ca: [CA-H2.1]
features: [F-15d]
status: Deferred-TechDebt
sec: true
qa_sec: true
predecessors: [TASK-050]
---

# TASK-051 — Job APScheduler pós-pregão + evento `ScalingEligibilityReady`

## TDD First (Red)

1. `test_job_runs_after_pregao_close_for_each_active_strategy`
2. `test_job_publishes_ScalingEligibilityReady_when_eligible_true`
3. `test_job_does_not_publish_when_eligible_false_but_logs_blocked_attempt` — alimenta T057 (histograma).
4. `test_job_sends_telegram_alert_on_eligibility` — recomendação Marty.
5. `test_job_persists_audit_event_per_run`

## Implementação alvo (Green)

- Arquivo: `cam/features/scheduler/scaling_job.py`.
- Trigger APScheduler diário (18:30 BRT — após fechamento WIN).
- EventBus interno publica `ScalingEligibilityReady(strategy_id, evidence)`.

## Não-objetivos

- ❌ Aplicação manual (T053).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- Job + 5 testes verdes.

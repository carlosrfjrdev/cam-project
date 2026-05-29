---
template: TASK
task_id: TASK-029
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.04]
covers_ca: [CA-E.6]
features: [F-12]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-027]
---

# TASK-029 — `mt5.fill` → `JournalEntry` automático

## Objetivo

Fill detectado pelo `cam_bridge.mq5` (canal PUB `mt5.fill`) gera `JournalEntry` com `source=MT5_BRIDGE` (Art. 31).

## TDD First (Red)

1. `test_subscriber_receives_fill_event_from_bridge`
2. `test_subscriber_creates_journal_entry_with_source_MT5_BRIDGE`
3. `test_journal_entry_links_intent_id_to_fill_via_idempotency_key`
4. `test_journal_entry_persists_net_result_after_costs_R25`
5. `test_subscriber_idempotent_on_duplicate_fill` — bridge pode reenviar.

## Implementação alvo (Green)

- Arquivo: `cam/features/mt5_integration/fill_subscriber.py`.
- Subscriber assíncrono (background task no FastAPI lifespan).
- Cria `JournalEntry` consumindo `idempotency_key` para amarrar com intenção original.

## Não-objetivos

- ❌ DARF computation (já existe na fiscal feature).

## Marcadores

- `sec`: true. `qa-sec`: true.

## Saídas

- `fill_subscriber.py` + 5 testes verdes.

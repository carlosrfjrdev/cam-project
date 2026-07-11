---
template: TASK
task_id: TASK-002
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.01]
covers_ca: [CA-A.1, CA-C.4]
features: [F-01, F-16]
status: Completed
sec: true
qa_sec: true
predecessors: [TASK-001]
---

# TASK-002 — StrategyRegistry + constraint N-registered / 1-active

## Objetivo

Persistir estratégias registradas e garantir, em nível de DB, que **apenas 1 esteja ativa** enquanto `MULTI_STRATEGY_ENABLED=false` (default vigente).

## TDD First (Red)

1. `test_register_persists_metadata_with_default_status_draft`
2. `test_register_duplicate_id_raises`
3. `test_list_returns_all_in_insertion_order`
4. `test_get_by_id_returns_metadata`
5. `test_constraint_db_rejects_two_active_strategies` — integração com PostgreSQL real: tentar setar `is_active=true` em duas linhas dispara `IntegrityError` (unique partial index `WHERE is_active`).
6. `test_promote_to_active_deactivates_previous_active` — somente operação explícita transfere `is_active`.

## Implementação alvo (Green)

- Migration nova: `apps/cam-cockpit/backend/migrations/versions/NNN_cam_strategies.py`
  ```sql
  CREATE TABLE cam_strategies (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    asset TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    is_active BOOLEAN NOT NULL DEFAULT false,
    metadata_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
  );
  CREATE UNIQUE INDEX cam_strategies_one_active ON cam_strategies (is_active) WHERE is_active = true;
  ```
- Arquivo: `cam/features/strategies/registry.py` com `StrategyRegistry` (interfaces `register`, `list`, `get`, `set_active`).
- Repository pattern + SQLAlchemy.

## Não-objetivos

- ❌ Promoção com Evidence Pack (T003).
- ❌ Multi-active (BL-H1 / T046 quando flag `MULTI_STRATEGY_ENABLED=true`).
- ❌ Lógica de orquestrador (T043).

## Marcadores

- `sec`: true (constraint é defesa estrutural — `CA-C.4`).
- `qa-sec`: true (Linus + Kevin verificam a `unique partial index`).

## Saídas

- Migration + repository + testes verdes + 1 estratégia placeholder registrada via fixture.

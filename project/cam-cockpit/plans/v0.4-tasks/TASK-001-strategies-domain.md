---
template: TASK
task_id: TASK-001
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.01]
covers_ca: [CA-A.1]
features: [F-01]
status: Completed
sec: true
qa_sec: true
predecessors: []
---

# TASK-001 — Strategy Protocol + StrategyMetadata + StrategyStatus

> **Lead executor:** Nikola · **Intrabloco:** Linus (sempre), Kevin (sec=true).

## Objetivo

Materializar o **contrato canônico de Estratégia** no domínio: `Strategy` (Protocol), `StrategyMetadata` (dataclass) e `StrategyStatus` (Enum com 7 estados do ciclo de vida).

## TDD First — testes a escrever ANTES do código (Red)

1. `test_strategy_protocol_evaluate_returns_optional_candidate`
   - Implementação dummy retornando `None` em tick neutro → `evaluate() is None`.
   - Implementação dummy retornando `OrderCandidate` em tick gatilho → tipo correto.
2. `test_strategy_metadata_required_fields`
   - Criar `StrategyMetadata(id, name, version, asset, author)` sem nenhum campo deve falhar.
3. `test_strategy_status_enum_values_exact`
   - Enum deve ter exatamente: `draft`, `backtested`, `walk_forward_ok`, `paper_ok`, `demo_ok`, `real_authorized`, `retired` (ordem importa para promoções monotônicas).
4. `test_strategy_status_transition_only_forward_or_retired`
   - Transição `paper_ok → backtested` deve falhar (ou ser flag); `paper_ok → demo_ok` ok; qualquer estado → `retired` ok.

## Implementação alvo (Green)

- Arquivo: `apps/cam-cockpit/backend/cam/features/strategies/domain.py`
- Conteúdo: `Strategy` (Protocol com `evaluate`), `StrategyMetadata` (dataclass frozen), `StrategyStatus` (StrEnum), `OrderCandidate` (dataclass — placeholder usado por T006), `StrategyContext` (dataclass com tick atual + janela histórica + flags).
- Sem persistência (T002 cuida).
- Vertical slice — `features/strategies` não importa de outras features (ADR-013).

## Não-objetivos

- ❌ Implementar S1 ORB aqui (T007).
- ❌ Persistência em DB (T002).
- ❌ Promoção/Evidence Pack (T003).
- ❌ Order Gateway (T006).

## Marcadores

- `sec`: true (toca contrato que será consumido por Order Gateway).
- `qa-sec`: true (Linus exige cobertura de transições de status).

## Saídas esperadas

- Arquivo `domain.py` + suite de testes verde.
- Sem warnings de mypy/ruff.

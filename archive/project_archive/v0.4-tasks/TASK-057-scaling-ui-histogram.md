---
template: TASK
task_id: TASK-057
block: BL-H2
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R8.18, R8.12]
covers_ca: [CA-H2.3, CA-H2.9]
features: [F-15f]
status: Deferred-TechDebt
sec: false
qa_sec: true
predecessors: [TASK-050, TASK-053]
---

# TASK-057 — UI Risk Console — histograma de tentativas-bloqueadas + incremento +1 strict

## Objetivo

Visualização que **mostra ao Founder** quais critérios estão faltando para escalonar — recomendação Marty 3.

## TDD First (Red — UI)

1. `test_histogram_renders_5_bars_one_per_criterion_PF_WR_EXP_DD_ADH`
2. `test_histogram_shows_blocked_count_per_criterion_last_30_evaluations`
3. `test_histogram_highlights_strategy_name_when_eligible_imminent`
4. `test_ui_displays_proposed_limit_with_plus_1_increment_only` — botão de aplicar bloqueado se diferente.
5. `test_ui_links_to_ESC_file_template_when_eligibility_ready`

## Implementação alvo (Green)

- Tela: extensão de `RiskConsolePage.tsx` (T049) — seção "Escalonamento".
- Endpoint: `GET /api/v1/scaling/blocked-attempts?strategy_id=...` retornando histograma.

## Não-objetivos

- ❌ Aplicar escalonamento via UI (workflow é manual via arquivo).

## Marcadores

- `sec`: false. `qa-sec`: true.

## Saídas

- UI + endpoint + 5 testes verdes.

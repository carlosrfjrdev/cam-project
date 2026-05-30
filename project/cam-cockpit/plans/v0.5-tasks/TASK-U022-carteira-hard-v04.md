---
task_id: TASK-U022
block: BL-UI-5
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU5.01]
covers_ca: [CA-U5.1, CA-U5.2]
status: Pending
sec: false
qa_sec: true
predecessors: [TASK-U002, TASK-U006, TASK-U010]
---

# TASK-U022 — Carteira Hard v0.4 (holdings + R-20 + policy + dividendos)

> Lente Barsi. Art. 23º (não é margem) reforçado visualmente.

## Objetivo
Estender `features/carteira-hard/CarteiraHardPage.tsx` com 7 indicadores R-20 (DY peso forte), calendário de dividendos, alertas Policy Engine (banner amarelo — sugestão, nunca bloqueio), rebalance sugerido (nunca executa).

## TDD First (Red — Vitest+RTL)
1. `test_holdings_with_7_indicators` — DY destacado.
2. `test_policy_alerts_yellow_non_blocking` — R-13.
3. `test_rebalance_is_suggestion_with_checklist` — nunca botão de execução automática.
4. `test_carteira_hard_not_margin_note` — reforço visual Art. 23º.
5. `test_dividends_calendar`.

## Green
- Estender página + `useCarteiraHard` → `/carteira-hard/holdings`, `/fundamentals`, `/dividends/calendar`, `/carteira-hard/policy-alerts`. Re-tema.

## Não-objetivos
- ❌ Endpoints (U002, U006). ❌ execução de rebalance.

## Marcadores
- `sec`: false · `qa-sec`: true.

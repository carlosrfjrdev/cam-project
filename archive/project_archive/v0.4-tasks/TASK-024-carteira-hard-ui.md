---
template: TASK
task_id: TASK-024
block: BL-D
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R4.05]
covers_ca: [CA-D.1]
features: [F-10]
status: Deferred-TechDebt
sec: false
qa_sec: false
predecessors: [TASK-021]
---

# TASK-024 — UI `/carteira-hard` (listagem)

## Objetivo

Tela React + MUI para listar holdings, saldo R$ + total estimado (sem cotação ao vivo — BL-F integra).

## TDD First (Red — UI tests com Vitest + Testing Library)

1. `test_renders_empty_state_when_no_holdings`
2. `test_renders_holding_rows_with_ticker_quantity_avg_price`
3. `test_displays_total_estimated_in_BRL`
4. `test_button_add_holding_opens_dialog`
5. `test_form_submit_calls_POST_endpoint_with_correct_payload`
6. `test_import_genial_button_triggers_file_picker`

## Implementação alvo (Green)

- Diretório: `apps/cam-cockpit/frontend/src/features/carteira-hard/`
- Componentes: `CarteiraHardPage.tsx`, `HoldingsTable.tsx`, `AddHoldingDialog.tsx`, `ImportGenialButton.tsx`.
- Hook `useHoldings()` (React Query + MUI).

## Não-objetivos

- ❌ Cotação ao vivo (BL-F).
- ❌ Policy Engine alerts UI (T033).

## Marcadores

- `sec`: false. `qa-sec`: false (tela apenas leitura/CRUD básico).

## Saídas

- Página funcional + 6 testes UI verdes.

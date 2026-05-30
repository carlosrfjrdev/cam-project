---
task_id: TASK-U012
block: BL-UI-1
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU1.05]
covers_ca: [CA-U1.4, CA-U1.5]
status: Pending
sec: false
qa_sec: true
predecessors: [TASK-U009]
---

# TASK-U012 — Tokens centralizados + lint no-hardcode

## Objetivo
Garantir que nenhum componente tenha hex/rem hardcoded; tudo via theme. WCAG AA verificado.

## TDD First (Red)
1. `test_lint_no_hardcoded_hex` — script falha se `#RRGGBB` aparecer fora de `theme.ts`/tokens.
2. `test_wcag_aa_contrast` — combinações DS (esmeralda sobre dark, texto) ≥ 4.5:1.
3. `test_theme_toggle_persists` — dark/light persistido.

## Green
- Script `scripts/lint_no_hardcode.mjs` no CI front. Helper de contraste nos testes.
- Dark Mode First; toggle persistido.

## Não-objetivos
- ❌ Telas. ❌ novos tokens (DS é SSoT).

## Marcadores
- `sec`: false · `qa-sec`: true.

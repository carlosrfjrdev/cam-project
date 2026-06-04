---
task_id: TASK-U009
block: BL-UI-1
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU1.01, RU1.02]
covers_ca: [CA-U1.1]
status: Done
sec: false
qa_sec: true
predecessors: []
---

# TASK-U009 — Theme MUI Esmeralda (substitui azul/monospace)

> Lead: Andy. Fonte: `the-cam/ui-design/tokens.md` + `mui-theme-cam.md`.

## Objetivo
Reescrever `frontend/src/app/theme.ts` a partir do DS CAM. Hoje usa azul `#1565c0` + JetBrains Mono + `#0a0a0a` — diverge do DS.

## TDD First (Red — Vitest)
1. `test_theme_primary_is_esmeralda` — `palette.primary.main === '#059669'`.
2. `test_theme_backgrounds` — default `#1A1A1A`, paper `#1F1F1F`.
3. `test_theme_functional_colors` — success `#10B981`, warning `#F59E0B`, error `#EF4444`, info `#0EA5E9`.
4. `test_theme_typography_poppins_inter` — headings Poppins, body Inter (não monospace global).
5. `test_founder_orange_token_present` — `#FF7A00` disponível como acento (não primary).
6. `test_radius_and_focus_ring` — botões 4px, cards 6px, focus ring 2px `#10B981`.

## Green
- `theme.ts` Esmeralda dark-first; Poppins+Inter via `@fontsource`; monospace só para números técnicos (variant custom).
- Founder Orange como token de acento (`palette.augmentColor` ou custom), nunca primary/success/warning.

## Não-objetivos
- ❌ AppShell (U010). ❌ telas.

## Marcadores
- `sec`: false · `qa-sec`: true (Don: base do banner/defesa).

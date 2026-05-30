---
task_id: TASK-U010
block: BL-UI-1
plan_ref: ../PLAN-v0.5-COCKPIT-UI.md
spec_rules: [RU1.03]
covers_ca: [CA-U1.2]
status: Pending
sec: false
qa_sec: true
predecessors: [TASK-U009]
---

# TASK-U010 — AppShell (Header + Sidebar colapsável + Content)

> Fonte: `the-cam/ui-design/layout-directive.md` (adaptado single-operator, full web).

## Objetivo
AppShell do cockpit: Header 56px + Sidebar colapsável (208/56px) + Content Area + Breadcrumb. Sem multi-tenant.

## TDD First (Red — Vitest+RTL)
1. `test_appshell_renders_header_sidebar_content`.
2. `test_sidebar_collapse_toggle` — expande/colapsa; ícone Chevron.
3. `test_sidebar_state_persists_localstorage`.
4. `test_collapsed_shows_tooltip_on_hover`.
5. `test_no_tenant_elements` — sem troca de tenant/gestão de usuários (single-operator).
6. `test_desktop_first_layout` — otimizado desktop; mobile degrada para visualização.

## Green
- `_shared/components/AppShell.tsx` + `Sidebar.tsx` + `Header.tsx`. Estado via store leve (Zustand ou context) + localStorage.
- Itens de menu = rotas do cockpit (incluindo as novas telas v0.5).

## Não-objetivos
- ❌ Conteúdo das telas (BL-UI-2..5). ❌ interação mobile (Telegram futuro).

## Marcadores
- `sec`: false · `qa-sec`: true.

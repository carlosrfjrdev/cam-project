# Shadows & Elevation — DS CAM

## Princípio
Profundidade é **construída** (tonal layering), não projetada (drop shadow). Em dark, um card em `--surface-1` sobre `--background` já tem profundidade.

## Regras
- Cards (dark): sem sombra — usar shift tonal + borda `--border`.
- Modal/Dialog: sombra real `--shadow-modal` (0 20px 40px rgba(0,0,0,.4)).
- Floating (tooltip/popover): `--surface-2` + opacidade ~90% (+ blur opcional).
- Light theme: sombras suaves permitidas (`shadow-sm/md/lg`).

## Para IA
Não aplicar `box-shadow` em cards no dark. Hover de card = mudar borda para `rgba(5,150,105,.4)`, não sombra.

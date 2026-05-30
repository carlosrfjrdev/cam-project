# Grids & Spacing — DS CAM

## Grid
4px obrigatório. Tokens `--space-1..16` (4,8,12,16,24,32,48,64). Valores arbitrários proibidos (7px → 8px).

## Layout
**Full Web, desktop-first.** Não mobile-first. Breakpoints: <768 mobile (só visualização), ≥768 tablet, ≥1024 desktop (3+ colunas), ≥1280 wide. Interação mobile = Robô Telegram (spec futura), não a UI web.

## Contexto
- Padding card: 24–32px. Padding seção: 64–96px. Gaps: 16/24/32.
- Content area do cockpit: max ~1100–1280px; tabelas densas para gestão.

## Para IA
Gerar layouts desktop-first; mobile degrada para 1 coluna de leitura. Touch target ≥44px quando houver toque.

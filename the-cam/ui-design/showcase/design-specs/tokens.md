# Tokens — DS CAM (SSoT)

## Regra de ouro
Valores atômicos (hex, rem, px, ms) existem só em `assets/tokens.css` (espelha `the-cam/ui-design/tokens.md`). Demais arquivos referenciam via `var(--token)`.

## Grupos
- Cor: ver `colors.md`.
- Tipografia: head Poppins 600; body Inter 400; mono JetBrains (só números técnicos). Escala: h1 2.625 / h2 2 / h3 1.5 / body 1 / dense .875 / small .8125 / caption .75 rem. Mínimo absoluto 12px.
- Espaço: grid 4px (`--space-1..16`). Valores fora da escala proibidos.
- Raio: btn/input 4px, card 6px. Sem `rounded-full` nem cantos vivos.
- Foco: ring 2px `--ring #10B981`, nunca remover.
- Motion: 150/200/250ms ease; preferir transform/opacity.

## Para IA
Ao gerar componente, consumir tokens; nunca hardcode hex/rem. Dark Mode First, Full Web (desktop-first).

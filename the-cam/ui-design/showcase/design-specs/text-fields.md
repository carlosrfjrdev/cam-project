# TextField — DS CAM
**MUI:** `TextField` (variant="outlined").
## Anatomia
Label (visível) + input + helper/error opcional.
## Tipos
text, email, password, number, multiline (textarea).
## Estados
default · focus (border `--ring` + ring 2px `--primary-soft`) · error (border `--destructive` + mensagem) · disabled (opacity .5).
## Tokens
bg `--surface-2`, border `--border`, radius `--radius-input` 4px, foco `--ring`.
## A11y
Label sempre visível ou `aria-label`. Erro em texto+cor (não só cor). Touch ≥44px.
## CaM
Campos numéricos (contratos/preço) podem usar mono. Validação de limite (Art. 11) mostra erro vermelho.

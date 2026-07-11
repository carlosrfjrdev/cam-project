# Dialog — DS CAM
**MUI:** `Dialog` (era "Modal").
## Anatomia
overlay rgba(0,0,0,.3) + card (`--elevated`, sombra modal) + botão X obrigatório (top-right) + ações.
## Comportamento
fecha por X, overlay e Escape. Não empilhar. ~maxWidth sm (512px).
## CaM
Confirmações destrutivas SEMPRE via Dialog (kill switch, revogar escalonamento), nunca toast. Botão destrutivo `--destructive`.

# Colors — DS CAM

## Propósito
Sistema de cor do cockpit CaM. Esmeralda = identidade (não "verde de lucro"). Founder Orange = acento editorial raro do operador. Funcionais ancoram defesa de capital.

## Tokens
- Primária: `--primary #059669`, `--primary-dark #047857`, `--primary-light #34D399`, `--primary-deep #061711`, `--primary-soft rgba(5,150,105,.14)`.
- Superfícies (dark): `--background #1A1A1A`, `--surface-1 #1F1F1F`, `--surface-2 #2C2C2C`, `--surface-3 #3A3A3A`, `--elevated #444`.
- Funcionais: `--success #10B981`, `--destructive #EF4444` (loss), `--warning #F59E0B`, `--info #0EA5E9` (IA).
- Founder: `--founder-orange #FF7A00`, `--founder-ember #C2410C`, `--founder-glow #FDBA74`.

## Regras (para IA)
- Máx. 1 CTA primário (Esmeralda) por seção. Proibido Esmeralda em texto longo.
- Loss SEMPRE em `--destructive`; ganho em `--success`. Cor nunca é o único indicador (use ícone/label) — WCAG AA.
- Founder Orange só quando Carlos/origem/provocação estão semanticamente presentes; nunca primária/sucesso/warning.
- Contraste mínimo 4.5:1 texto, 3:1 gráfico.

## MUI mapping
`theme.palette.primary=#059669`, `success/error/warning/info` conforme tokens. Founder Orange via `palette.augmentColor` custom, não como primary.

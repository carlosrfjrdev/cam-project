# Feature: fiscal

## Propósito

Apuração mensal de IR Day Trade, geração de DARFs e controle de compensação de prejuízo acumulado. DARF atrasada bloqueia operações via Risk Engine (Art. 26º).

## Artigos Constitucionais

- **Art. 26º** — DARF atrasada bloqueia novas operações
- **Art. 27º** — Compensação de prejuízo acumulado obrigatória
- **Art. 25º** — Resultados sempre líquidos de imposto

## I/O

**Inputs:**
- `GET /api/v1/fiscal/apuration/{month}` — apuração do mês
- `GET /api/v1/fiscal/darfs` — listagem de DARFs
- `PATCH /api/v1/fiscal/darfs/{id}/mark-paid` — marcar como paga (dispara harvest)

**Cálculo IR Day Trade:**
- Alíquota: 20% sobre lucro líquido mensal
- IRRF: 1% retido na fonte como antecipação
- Compensação de prejuízo: saldo acumulado abate base de cálculo

## Eventos Consumidos

- `JournalEntryCreated` — atualiza provisão fiscal em tempo real

## Eventos Publicados

- `DarfPaid` — consumido por `harvest` para recalcular buckets
- `DarfOverdue` — consumido por `notifications` para alerta Telegram

## Anti-padrões

- Calcular IR apenas no fechamento mensal sem provisão incremental
- Permitir operação quando DARF está OVERDUE (violação Art. 26º)
- Ignorar compensação de prejuízo acumulado no cálculo

---
template: EVIDENCE
phase: P&D / Research Lane — gate de dados R0
produto: CaM
codinome: research-cubo-leadlag
data: 2026-06-03
fonte: comando PROBE_TICKS (EA cam_bridge v0.40) via GET /api/v1/mt5/probe-ticks
gate: R0 — viabilidade de OFI/tick (flag de agressor)
---

# Evidência — Disponibilidade da flag de agressor no feed MT5 (Genial)

> Resultado empírico que **decide o escopo** do Cubo de Lead-Lag: a Tese 1
> (Cubo Rápido / OFI) exige o lado agressor (`ε_k ∈ {+1,−1}`). Em vez de assumir
> no papel que "MT5 não entrega agressor" (suposição inicial do SCOPE v0.5),
> **medimos** via `CopyTicks(COPY_TICKS_ALL)` lendo `MqlTick.flags`.

## Pergunta

O feed do MT5 da Genial entrega a flag de agressor (`TICK_FLAG_BUY`=32 /
`TICK_FLAG_SELL`=64) por tick, com timestamp em ms?

## Método

`PROBE_TICKS` (EA, read-only) → `CopyTicks(symbol, COPY_TICKS_ALL, 0, 500)` →
conta flags por bit. Mercado aberto, 2026-06-03.

## Resultado

| Símbolo | copied | aggressor_available | n_buy | n_sell | span | nota |
|---|---|---|---|---|---|---|
| **WIN$** (contínuo) | 500 | ✅ **true** | 176 | 224 | 7,4 s | índice — fluxo denso |
| **WINM26** (vencimento) | 500 | ✅ **true** | 319 | 140 | 3,0 s | índice — fluxo denso |
| **PETR4** (ação) | 500 | ✅ **true** | 319 | 72 | 254,8 s | ação — fluxo de tick **esparso** |

Decodificação de flags observados na amostra:
- `1080` = 1024 + **32 (BUY)** + 16 (VOLUME) + 8 (LAST) → tick comprador agressor
- `1112` = 1024 + **64 (SELL)** + 16 (VOLUME) + 8 (LAST) → tick vendedor agressor
- `1026` = 1024 + 2 (BID) → atualização de bid (sem trade)

## Veredito

**O feed entrega o agressor em FUTURO e AÇÃO.** O dado primário do Cubo Rápido
(OFI assinado, event-time, ms) **existe** no CaM via MT5/Genial.

**Consequência de escopo:**
- OFI/tick **promovido de LATER → IN** na v0.5 (a tese completa fica viável).
- Hayashi-Yoshida (mata-Epps), Granger e lead-lag HRY ficam viáveis (têm tick
  assíncrono com `t_msc`).
- A `TickPersister` (já grava `cam_market_ticks`) precisa passar a **persistir o
  `flags`** (agressor) — hoje grava só price/volume. Entra no PLAN/CODE.

## Caveat honesto (Nassim/Voltaire)

A **liquidez de tick varia muito por ativo**: WIN faz 500 ticks em ~5s; PETR4 em
~255s. Isso afeta o horizonte τ explorável e a capacidade por ativo — ações de
menor giro terão janelas de evento mais longas e amostra de tick menor. O dado
existe, mas **a microestrutura não é uniforme** — o event study terá de
condicionar por liquidez do alvo (já previsto em `CaM-RESEARCH §10`).

> Esta evidência alimenta o gate R0. Não promove estratégia, não autoriza
> operação. Research-only.

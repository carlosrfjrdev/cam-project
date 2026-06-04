# FEATURE-FLAGS-LEDGER — Histórico de ativação/desativação de features

> **Origem:** SPEC v0.2.1 R21.04
> **Mutex:** R21.03 — apenas UMA camada de integração broker (Profit OU MT5) ativa por vez
>
> Cada linha é uma transição imutável. Para corrigir registro incorreto,
> abrir nova entrada de "correção" (não editar entrada antiga).

---

## Ledger

| # | Data | Flag | De → Para | Motivação | Aprovador |
|---|---|---|---|---|---|
| 001 | 2026-05-25 | `PROFIT_INTEGRATION_ENABLED` | `(novo)` → `false` | Adoção MT5 conforme DECISION-MEMO §6 — princípio de coexistência (SPEC v0.2.1) | Founder |
| 002 | 2026-05-25 | `MT5_INTEGRATION_ENABLED` | `(novo)` → `true` | Adoção MT5 conforme DECISION-MEMO §6 | Founder |
| 003 | 2026-05-27 | `MULTI_STRATEGY_ENABLED` | `(reservado)` → `false` (default) | Flag criada por EMENDA-001 v2 (Art. 11-A). Default `false` mantém comportamento 1-strategy-active. Ativação exige BL-H1 entregue + rastreabilidade dupla (ledger constitucional + esta entrada) | Founder |
| 004 | 2026-05-27 | `SCALING_ENABLED` | `(reservado)` → `false` (default) | Flag criada por EMENDA-001 v2 (Art. 11-B). Default `false` mantém `max_contracts_check` lendo limite default hardcoded (2+2). Ativação exige BL-H2 entregue + 1ª aprovação de escalonamento em `escalonamentos/` | Founder |

---

## Como propor toggle

1. Decisão formal registrada (motivação escrita em arquivo separado se for mudança significativa).
2. Editar `.env` do backend.
3. Restart backend — mutex R21.03 valida.
4. **Adicionar entrada no ledger acima** (append-only, nunca editar histórico).

---

## Flags atuais conhecidas

| Flag | Default | Onde lida | Descrição |
|---|---|---|---|
| `PROFIT_INTEGRATION_ENABLED` | `false` | `cam._shared.config.settings` | Habilita endpoints `/api/v1/profit/*` (legado) |
| `MT5_INTEGRATION_ENABLED` | `true` | `cam._shared.config.settings` | Habilita endpoints `/api/v1/mt5/*` (atual) |
| `MULTI_STRATEGY_ENABLED` | `false` | `cam._shared.config.settings` (a criar em BL-H1) | Habilita orquestrador multiestratégia (Art. 11-A). Ativar exige BL-H1 entregue e estratégias com aderência individual ≥ 95% |
| `SCALING_ENABLED` | `false` | `cam._shared.config.settings` (a criar em BL-H2) | Habilita `scaling_eligibility_check` + leitura de limite vigente diferente do default (Art. 11-B). Ativar exige BL-H2 entregue e 1ª aprovação de escalonamento |

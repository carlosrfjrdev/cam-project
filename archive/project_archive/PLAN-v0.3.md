---
template: PLAN
phase: PLAN
status: Approved (letscode)
version: 0.3
date: 2026-05-25
parent_spec: SPEC-v0.3-TECH-DEBT-REVIEW.md
pmg: M
sec: false
qa_sec: false
---

# PLAN v0.3 — Saneamento Tech Debts (9 TASKs sanadoras + atualização ledger)

> **Lead:** Nico · **Skill:** `teczi-code-planning`
> **Origem:** [`SPEC-v0.3-TECH-DEBT-REVIEW.md`](./SPEC-v0.3-TECH-DEBT-REVIEW.md)
> **TDD First:** Nikola escreve testes antes de cada TASK.

## 1. P/M/G

| Campo | Valor |
|---|---|
| Classe SPEC | **M** |
| Concordância Nico | **Sim — M.** 9 TASKs auto-contidas, sem mudança de DAS/ADR. |

## 2. TASKs (flat)

| # | TASK | Saída esperada | Marcadores |
|---|---|---|---|
| T-TD-001 | Adicionar `total_open_contracts_check` em `cam/_shared/risk/validators/group2_limits.py` (Art. 12º explícito) + entrada no pipeline; property-based test | `sec` |
| T-TD-004 | Teste do journal duplo JSONL com `tmp_path` (`cam/features/journal/tests/test_jsonl_fallback.py`) | — |
| T-TD-005 | Criar `DarfPaid` event + subscribe `harvest_service.handle_darf_paid` no lifespan | — |
| T-TD-010 | `get_notification_service()` factory + lazy init; remover singleton import-time | — |
| T-TD-012 | `BacktestMetrics.sharpe_ratio` com stddev real + CDI configurável | — |
| T-TD-017 | `AnthropicProvider` lê `anthropic_model` e `anthropic_api_version` de `Settings` | — |
| T-TD-026 | WebSocket P&L `/api/v1/ws/pnl` emite mensagem a cada 5s (stub funcional) | — |
| T-TD-027 | `kill_switch/service` chama `log_kill_switch_*`; `mt5_integration/service` chama `log_risk_decision` | — |
| T-TD-v0.2-03 | Fixture HTML sample + teste de regressão do parser | `qa-sec` |
| T-TD-v0.2-06 | `GET /settings` adiciona `feature_flags`; SettingsPage exibe painel | — |

## 3. TASKs documentais (R22)

| # | TASK | Saída |
|---|---|---|
| T-TD-DOC-01 | Atualizar `TECH-DEBT.md`: remover TD-023/024/025 (RESOLVIDOS) + marcar TD-007/008/009 como CONGELADOS + atualizar header |
| T-TD-DOC-02 | Atualizar `MAPPING-CONSTITUICAO-RISK-ENGINE.md`: Art. 12º agora tem `total_open_contracts_check` explícito |
| T-TD-DOC-03 | Atualizar `MANUAL-VALIDATION-CHECKLIST.md`: novos cenários para validators novos + audit log + feature flags |

## 4. Sequência

A → unitário/atômico, executar em qualquer ordem; documentais por último.

## 5. `letscode`

`true` — Founder confirmou "ja faça plan e code da spec completa, vou sair agora" (2026-05-25).

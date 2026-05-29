---
template: TASK
task_id: TASK-026
block: BL-E
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R5.02]
covers_ca: [CA-E.4]
features: [F-12]
status: Completed
sec: true
sec_critical: true
qa_sec: true
qa_sec_critical: true
predecessors: [TASK-025]
---

# TASK-026 — `tests/test_risk_mirror_parity.py` — 100+ cenários canônicos

> **CRÍTICO** — Paridade Python↔MQL5 é o que viabiliza envio de ordem demo.

## TDD First (Red)

100 cenários canônicos, cada um carregando:
- `OrderIntent` (asset, direction, contracts, sl_points)
- Estado vigente: kill_switch, gain_lock, loss_lock, cooldown, DARF, pregão_window, posições abertas, limite vigente.
- **Expectativa:** mesma decisão `Approved/Rejected` + mesmo `culprit_validator` em Python e MQL5.

Categorias mínimas:
- 10 cenários de aprovação limpa.
- 18 cenários (1 por validator) com **falha intencional naquele validator** — culprit deve casar.
- 30 cenários de borda (limite exato, timestamp exato de janela).
- 20 cenários de combinação multi-violação — primeiro reprovador deve ser identificado.
- 22 cenários gerados via Hypothesis com seed fixo para reprodutibilidade.

## Implementação alvo (Green)

- Arquivo: `apps/cam-cockpit/backend/tests/test_risk_mirror_parity.py`.
- Harness que:
  1. Roda `risk_validate` Python.
  2. Envia `EVAL_RISK_MIRROR` via bridge para EA em MT5 demo (modo teste).
  3. Compara decisões → `assert python_decision == mql5_decision and python_culprit == mql5_culprit`.

## Não-objetivos

- ❌ `SUBMIT_ORDER` (T027) — paridade é validation-only.

## Marcadores

- `sec`: true CRÍTICO. `qa-sec`: true CRÍTICO.

## Saídas

- 100 cenários, **TODOS** verdes. Falha = T027 não pode iniciar.

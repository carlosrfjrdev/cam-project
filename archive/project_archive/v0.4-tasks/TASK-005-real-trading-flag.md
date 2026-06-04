---
template: TASK
task_id: TASK-005
block: BL-A
plan_ref: ../PLAN-v0.4-VISION-EVOLUTION.md
spec_rules: [R1.06]
covers_ca: [CA-A.8]
features: [F-32]
status: Completed
sec: true
qa_sec: true
predecessors: []
---

# TASK-005 — `REAL_TRADING_ALLOWED=false` + `REAL_TRADING_ACCOUNTS` allowlist

## Objetivo

Adicionar variáveis de configuração que travam operação real **por design** e mantêm allowlist explícita de contas autorizadas (vazia por default).

## TDD First (Red)

1. `test_default_REAL_TRADING_ALLOWED_is_false`
2. `test_default_REAL_TRADING_ACCOUNTS_is_empty_list`
3. `test_settings_rejects_real_trading_allowed_true_without_accounts` — valida `if REAL_TRADING_ALLOWED=true and REAL_TRADING_ACCOUNTS=[] → ValueError`.
4. `test_settings_rejects_unknown_env_var_format` — guarda contra typos em `.env`.
5. `test_audit_log_emitted_on_real_trading_flag_flip` — qualquer toggle emite registro com timestamp + ator (mesmo que ator seja "Founder").

## Implementação alvo (Green)

- Editar: `cam/_shared/config/__init__.py`
  ```python
  REAL_TRADING_ALLOWED: bool = False
  REAL_TRADING_ACCOUNTS: list[str] = []
  ```
- Validação Pydantic ou similar para `.env` parsing seguro.
- Audit hook simples (registra mudança em `cam_audit_events`).

## Não-objetivos

- ❌ Implementar Order Gateway consumindo a flag (T006 faz).
- ❌ UI exibindo banner (vem em BL-E + T030).

## Marcadores

- `sec`: true CRÍTICO — flag de defesa em profundidade.
- `qa-sec`: true.

## Saídas

- Settings + 5 testes verdes + 1 entrada nova em `FEATURE-FLAGS-LEDGER.md` se mudar default (não deve mudar — `false` permanece).

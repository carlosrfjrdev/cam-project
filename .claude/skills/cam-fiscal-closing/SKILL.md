---
name: cam-fiscal-closing
description: "CaM Fiscal Closing (DRAFT). Acionar para apuração fiscal mensal: provisão (resultado sempre líquido), DARF, IR 20% day trade/IRRF 1%, compensação de prejuízo, conciliação. Lead Luca. Ancoragem Arts. 24º-27º (líquido sempre, journal obrigatório). CaM-only."
phase: cam-financeiro
lead_persona: Luca
co_lead_persona: Founder (confirmação de pagamento DARF)
status: draft (esqueleto — procedimento detalhado vira demanda própria)
---

# Skill — cam-fiscal-closing (DRAFT)

> Skill do **mundo financeiro do CaM** (CaM-only). Lead: **Luca**. Esqueleto.

## 1. Propósito

Fechamento fiscal mensal do CaM: apurar, **provisionar (líquido sempre)**, gerar DARF, compensar prejuízo, conciliar. Garantir Art. 25º (líquido, nunca bruto) em todo resultado.

## 2. Quando acionar

- Fechamento mensal (apuração de IR).
- Pagamento de DARF (libera bloqueio de operação — Art. 26º).
- Conciliação de extrato de corretora.

## 3. Lead + co-personas

- **Lead:** Luca (verdade contábil).
- **Co:** Founder (confirma pagamento de DARF).

## 4. Procedimento (rascunho)

1. **Apuração mensal** — consolidar trades do mês (journal duplo DB+JSONL).
2. **IR 20% day trade / IRRF 1%** — calcular.
3. **Compensação de prejuízo** — aplicar saldo de prejuízo acumulado.
4. **DARF** — gerar guia; resultado sempre **líquido** de provisão.
5. **Conciliação** — bater journal vs extrato de corretora.
6. **Confirmação Founder** — pagamento de DARF registrado (desbloqueia operação).

## 5. Artefatos in/out

- **In:** journal do mês (DB+JSONL), extrato de corretora.
- **Out:** apuração mensal, DARF, ledger atualizado, status de compliance fiscal.

## 6. Gates

- DARF atrasada **bloqueia novas operações** (Art. 26º) — enforçado pelo Risk Engine.
- Todo resultado exibido é líquido (Art. 25º).

## 7. Ancoragem constitucional

- **Arts. 24º–27º** (fiscal), **Art. 25º** (líquido sempre), **Art. 31º** (journal obrigatório), Art. 10º (tesouraria/buckets).

> Procedimento detalhado = demanda futura. Este é o esqueleto DRAFT.

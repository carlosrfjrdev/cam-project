---
name: cam-risk-modeling
description: "CaM Risk Modeling (DRAFT). Acionar para modelar risco financeiro: risco agregado, position sizing, risco de ruína, drawdown, exposição cross-asset. Lead Nassim. Define os parâmetros que o Risk Engine enforça (não é o Risk Engine). Ancoragem Arts. 11º/16º, R-08. CaM-only."
phase: cam-financeiro
lead_persona: Nassim
co_lead_persona: Kevin (enforce técnico no código), Founder (gate)
status: draft (esqueleto — procedimento detalhado vira demanda própria)
---

# Skill — cam-risk-modeling (DRAFT)

> Skill do **mundo financeiro do CaM** (CaM-only). Lead: **Nassim**. Esqueleto.

## 1. Propósito

Modelar o **risco financeiro** da operação: quanto arriscar, qual sizing, qual drawdown agregado máximo, qual exposição cross-asset, qual risco de ruína. Nassim **define** os parâmetros; o **Risk Engine apenas aplica**.

## 2. Quando acionar

- Antes de habilitar multiestratégia (R-08 — risco agregado antes de N).
- Revisão de sizing, drawdown agregado ou exposição cross-asset.
- Mudança de regime (Ray) que altera o perfil de risco.

## 3. Lead + co-personas

- **Lead:** Nassim (estrategista de risco financeiro).
- **Co:** Kevin (garante que o código não fure os limites definidos), Founder (gate).

## 4. Procedimento (rascunho)

1. **"O que me quebra?"** — mapear risco de ruína e tail risk.
2. **Position sizing** — por risco de ruína, não por convicção.
3. **Drawdown agregado** — limite máximo por estratégia e agregado.
4. **Exposição cross-asset** — WIN+WDO+Carteira; correlação.
5. **Parametrização** — entregar parâmetros que o Risk Engine enforça (Arts. 11/16).
6. **`⛔ GATE` Founder** + enforce técnico por Kevin.

## 5. Artefatos in/out

- **In:** perfil da operação, regime (Ray), estratégias ativas, capital.
- **Out:** parâmetros de risco (limites, sizing, drawdown) para o Risk Engine.

## 6. Gates

- `⛔ GATE` Founder antes de alterar qualquer limite.
- **Fronteira:** Nassim define; Risk Engine (código) aplica; Kevin garante o enforce. Tetos absolutos (Art. 11-B) são blindados.

## 7. Ancoragem constitucional

- **Arts. 11º / 11-A / 11-B** (limites), **Art. 16º** (limites de perda), **R-08** (risco agregado).

> Procedimento detalhado = demanda futura. Este é o esqueleto DRAFT.

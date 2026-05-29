# .claude/skills/ — Skills operacionais do CaM

> Duas famílias por **perímetro** (ADR-001 repo-wide):
>
> - **`teczi-*`** → compartilháveis com a Teczilabs (framework NCC-1701).
> - **`cam-*`** → **CaM-only** (mundo financeiro) — não sincronizam para a Teczi (Art. 8º).
> - **`strategy-session`** → institucional (Power Strategy Session).
>
> **Todas as `cam-*` nascem `status: draft` / Stage 0 (execução manual via Founder).**
> Nenhuma habilita operação automática ou real; nenhuma toca Risk Engine, Constituição,
> settings ou `REAL_TRADING_ALLOWED`.

---

## Skills `teczi-*` (DevFlow NCC-1701) — 11 + discovery

`teczi-project-creation` · `teczi-project-discovery` · `teczi-architecture-decision` ·
`teczi-demand-specification` · `teczi-code-planning` · `teczi-code-execution` ·
`teczi-quality-assurance` · `teczi-deploy` · `teczi-software-documentation` ·
`teczi-bug-fix` · `teczi-security-governance` · `teczi-discovery-software`

---

## Skills `cam-*` (mundo financeiro) — 10, todas DRAFT / Stage 0

### Operacionais (estrutura do mundo financeiro)

| # | Skill | Ritual | Lead (+co) | Ancoragem |
|---|---|---|---|---|
| 1 | [`cam-strategy-lab`](cam-strategy-lab/SKILL.md) | Tese de edge → backtest → walk-forward → Evidence Pack → gate | Jim (+Nassim, Voltaire, Founder) | Arts. 28º–30º |
| 2 | [`cam-risk-modeling`](cam-risk-modeling/SKILL.md) | Risco agregado, sizing, ruína, drawdown | Nassim (+Kevin, Founder) | Arts. 11º/16º, R-08 |
| 3 | [`cam-fiscal-closing`](cam-fiscal-closing/SKILL.md) | Apuração mensal, provisão, DARF, compensação | Luca (+Founder) | Arts. 24º–27º |
| 4 | [`cam-session-ritual`](cam-session-ritual/SKILL.md) | Checklist pré/pós-mercado + journal | Daniel (+Luca) | Arts. 31º–33º |
| 5 | [`cam-market-data-intake`](cam-market-data-intake/SKILL.md) | Ingestão com provenance, dedupe, quality | Ada (+Wyck) | Pilar 4 + gate de dados |
| 6 | [`cam-carteira-hard-review`](cam-carteira-hard-review/SKILL.md) | Revisão Carteira Hard (R-20), rebalance sugerido | Barsi (+Luca, Founder) | Art. 23º, Pilar 5, R-20 |

### Inteligência (read-only — produzem hipótese, nunca ordem)

| # | Skill | Ritual | Lead (+co) | Ancoragem |
|---|---|---|---|---|
| 7 | [`cam-prosperity-scan`](cam-prosperity-scan/SKILL.md) | Caça oportunidade → **hipótese (read-only, nunca ordem)** | Mammon (+Jim, Founder) | **Art. 35º (a trava vive aqui)** |
| 8 | [`cam-market-regime`](cam-market-regime/SKILL.md) | Classificação de regime (tendência/lateral/vol) — read-only | Ray (+Sun) | Arts. 34º–35º |
| 9 | [`cam-flow-analysis`](cam-flow-analysis/SKILL.md) | Fluxo/tape/book intraday → Cross-Asset Pattern Lab | Wyck (+Jim) | Pilar 4 |
| 10 | [`cam-decision-postmortem`](cam-decision-postmortem/SKILL.md) | RCA de erro de decisão (paralelo ao teczi-bug-fix) | Daniel (+Founder) | Art. 4º, 32º–33º |

> **Founder ampliou de 4 → 10 skills** (Adendo 02). As 6 antes declaradas como *later*
> foram promovidas a DRAFT ativo. Procedimento detalhado de cada uma = demanda própria.

---

## Invariantes de perímetro e segurança

- `cam-*` e `/personas` são **CaM-only** — nunca sincronizar com a Teczilabs (ADR-001, Art. 8º).
- **Trava read-only do Mammon (Art. 35º)** vive em `cam-prosperity-scan` (e no agent/persona do Mammon).
- **Dureza do Daniel** (diagnóstico frio, não coach) em `cam-session-ritual` + `cam-decision-postmortem`.
- Todas Stage 0: processo manual, não automação. "Construir amplo, liberar estreito."

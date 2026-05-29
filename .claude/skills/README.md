# .claude/skills/ — Skills operacionais do CaM

> Duas famílias por **perímetro** (ADR-001 repo-wide):
>
> - **`teczi-*`** → compartilháveis com a Teczilabs (framework NCC-1701).
> - **`cam-*`** → **CaM-only** (mundo financeiro) — não sincronizam para a Teczi (Art. 8º).
> - **`strategy-session`** → institucional (Power Strategy Session).

---

## Skills `teczi-*` (DevFlow NCC-1701) — 11 + discovery

`teczi-project-creation` · `teczi-project-discovery` · `teczi-architecture-decision` ·
`teczi-demand-specification` · `teczi-code-planning` · `teczi-code-execution` ·
`teczi-quality-assurance` · `teczi-deploy` · `teczi-software-documentation` ·
`teczi-bug-fix` · `teczi-security-governance` · `teczi-discovery-software`

---

## Skills `cam-*` (mundo financeiro) — CaM-only

### Ativas (esqueleto DRAFT — procedimento detalhado vira demanda própria)

| Skill | Ritual | Lead (+co) | Ancoragem |
|---|---|---|---|
| [`cam-strategy-lab`](cam-strategy-lab/SKILL.md) | Tese de edge → backtest → walk-forward → Evidence Pack → gate | Jim (+Nassim, Voltaire, Founder) | Arts. 28º–30º |
| [`cam-risk-modeling`](cam-risk-modeling/SKILL.md) | Risco agregado, sizing, ruína, drawdown | Nassim (+Kevin, Founder) | Arts. 11º/16º, R-08 |
| [`cam-fiscal-closing`](cam-fiscal-closing/SKILL.md) | Apuração mensal, provisão, DARF, compensação | Luca (+Founder) | Arts. 24º–27º |
| [`cam-prosperity-scan`](cam-prosperity-scan/SKILL.md) | Caça oportunidade → **hipótese (read-only, nunca ordem)** | Mammon (+Jim, Founder) | **Art. 35º (a trava vive aqui)** |

### Later — declaradas, **não construídas** ("construir amplo, ativar por demanda")

| Skill (later) | Ritual previsto | Lead provável |
|---|---|---|
| `cam-session-ritual` | Ritual de abertura/fechamento de pregão (checklists pré/pós) | Daniel + Don |
| `cam-market-data-intake` | Ingestão governada de dados de mercado (provenance, quality) | Ada + Wyck |
| `cam-carteira-hard-review` | Revisão periódica da Carteira Hard (dividendos, rebalance sugerido) | Barsi |
| `cam-market-regime` | Classificação de regime de mercado (macro, ciclo, volatilidade) | Ray |
| `cam-flow-analysis` | Análise de fluxo/tape/book L2 intraday | Wyck |
| `cam-decision-postmortem` | Post-mortem de loss focado no processo de decisão | Daniel |

> As 6 *later* **não devem ser criadas agora** — só serão construídas quando o Founder declarar a demanda.

---

## Regra de perímetro

`cam-*` e `/personas` são **CaM-only**. Nunca sincronizar com a Teczilabs (ADR-001, Art. 8º).

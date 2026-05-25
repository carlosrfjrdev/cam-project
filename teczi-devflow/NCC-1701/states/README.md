# Estados não numerados — NCC-1701

> Estados são **modos de operação** que não seguem a sequência das 9 fases.
> Eles entram quando há gatilho (BUG: defeito real; OPS: evento operacional).

## Catálogo

| Estado | Lead | Quando entrar | Resumo |
|---|---|---|---|
| [BUG](BUG.md) | Bill | Defeito ou regressão real | **Fast-track** com RCA proporcional, artefato único `BUG-{id}.md` |
| [OPS](OPS.md) | Vint | Evento operacional (deploy, infra, ambiente, incidente) | **Não refinado** até produto final · OPS-EVENT mínimo |

## Diferença em relação a fases

| Aspecto | Fases (1-9) | Estados (BUG, OPS) |
|---|---|---|
| Sequência | Numeradas, ordem sugerida | Sem ordem; entram por gatilho |
| Gates | Founder em cada saída | Founder Go/No-Go pontual |
| Artefatos | Múltiplos (SCOPE, SPEC, PLAN, etc.) | Geralmente artefato único |
| Cerimônia | Proporcional ao P/M/G | **Mínima** por princípio |

## Governanças transversais relacionadas

- [SEC-GOV](../governance/SEC-GOV.md) — pode ser acionada por BUG crítico (security incident) ou evento OPS (CVE crítico, incidente de dados).
- [CHANGE](../governance/CHANGE.md) — registra mudança quando BUG vai para DEPLOY.

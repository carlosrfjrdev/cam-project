# Estado — BUG

> **Codinome:** NCC-1701 · **Status:** Draft · **Tipo:** Estado não numerado
> **Lead:** Bill (orquestrador único)
> **Decisão herdada:** SCOPE-FINAL §6.2 + Q-feedback Founder sobre fast-track

## 1. Propósito

Conduzir **correção rápida** de defeito real ou regressão, com RCA proporcional e artefato único. Evitar arrastar bug por SPEC/PLAN/CODE/QA cerimoniais quando a correção é localizada e clara.

## 2. Quando entrar no estado

- Defeito reproduzível em produto vigente.
- Regressão detectada em QA, OPS ou pelo Founder/usuário.
- Comportamento divergente do contrato vigente (SPEC ou DAS).

**Não usar BUG para:**
- Pedido de melhoria (vai para SPEC normal).
- Nova funcionalidade (vai para DISC/SPEC).
- Dívida técnica conhecida (registra em tech-debt, não BUG).

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| Descrição do defeito (passos, esperado, real) | Founder / QA / OPS | sim |
| Ambiente onde ocorre | — | sim |
| SPEC/contrato violado (se identificável) | Histórico | quando aplicável |

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `BUG-{id}.md` (artefato único: RCA + fix + reteste) | [`../templates/BUG.md`](../templates/BUG.md) | `/projects/{produto}/bugs/` |
| Commit de correção | — | Repo do produto |
| Entrada no CHANGE-RECORD do próximo DEPLOY | [`../templates/CHANGE-RECORD.md`](../templates/CHANGE-RECORD.md) | `/projects/{produto}/changes/` |
| `PROOF-PACK.md` se bug crítico/incidente | [`../templates/PROOF-PACK.md`](../templates/PROOF-PACK.md) | obrigatório (R2 desta versão) |

## 5. Personas

- **Lead:** Bill (orquestrador único do fast-track)
- **Cross-cutting:** Nikola implementa fix; Linus reteste; Kevin se security; Vint se incidente operacional.

## 6. Critério de saída

- **Quem decide:** Founder
- **Critério de fechamento:** RCA registrado, fix mergeado, reteste verde, CHANGE-RECORD entrado, PROOF-PACK se aplicável.
- **Critério de retorno:** RCA superficial, fix sem reteste, ou regressão induzida pela correção.

## 7. Skill associada

[`../skills/teczi-bug-fix.md`](../skills/teczi-bug-fix.md)

## 8. Operação manual (Stage 0)

1. Founder/QA/OPS reporta defeito reproduzível.
2. Bill confirma reprodução e classifica severidade (informal: alta/média/baixa).
3. Bill conduz RCA proporcional:
   - alta: RCA completa (causa raiz, escopo de impacto, lição).
   - média: RCA curta (causa + correção).
   - baixa: nota direta sem RCA formal.
4. Nikola implementa fix.
5. Linus reteste (escopo do bug + regressão próxima).
6. Kevin se security; Vint se operacional.
7. Bill consolida tudo em `BUG-{id}.md` (artefato único).
8. Founder valida → fix vai para DEPLOY → CHANGE-RECORD entra.
9. Se crítico/incidente: PROOF-PACK obrigatório.

## 9. Anti-padrões

- Abrir BUG para nova funcionalidade.
- Fragmentar fast-track em SPEC + PLAN + CODE + QA + DEPLOY separados — é estado **único** com artefato único.
- Skip do reteste "porque é uma correção simples".
- Esquecer de entrar no CHANGE-RECORD.
- Não acionar SEC-GOV quando bug é security incident (gatilho explícito).

## 10. Referências

- SCOPE-FINAL §6.2
- Skill: [`../skills/teczi-bug-fix.md`](../skills/teczi-bug-fix.md)
- Template: [`../templates/BUG.md`](../templates/BUG.md)
- Governanças relacionadas: [`../governance/CHANGE.md`](../governance/CHANGE.md), [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)

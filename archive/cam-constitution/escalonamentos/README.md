# escalonamentos/ — Registros de Escalonamento Condicional (Art. 11-B)

> Cada arquivo neste diretório é um **escalonamento condicional do limite por default** ratificado pelo Founder, conforme [Art. 11-B](../../../CONSTITUICAO.md) da Constituição (v1.1+, pós EMENDA-001 v2).

---

## O que é um escalonamento

Diferente de uma **emenda** (que muda a Constituição), um **escalonamento** **não muda a Constituição**. Ele apenas **eleva temporariamente o limite vigente** do Art. 11º, dentro do que o Art. 11-B autoriza.

Exemplo: limite default é 2 contratos WIN. Operador, após cumprir os 5 critérios da Art. 11-B (a), formaliza escalonamento elevando para 3 WIN. Após 30 pregões com 3 WIN, se cumprir novamente os critérios, pode propor escalonamento para 4 WIN. E assim sucessivamente até o teto absoluto de 5 (item f).

---

## Pré-condições para ratificar um escalonamento

Conforme Art. 11-B (a..g):

1. **Critério empírico cumprido** (a) — métrica composta de 30 pregões:
   - Profit Factor ≥ 1,8
   - Win rate ≥ 55%
   - Expectância líquida ≥ 1,5 × custo fixo mensal
   - Drawdown ≤ 10% do Bucket Derivativo
   - Aderência ≥ 95%
2. **Risk Engine sinalizou eligibility=true** (b) via `cam/_shared/risk/scaling.py::compute_scaling_eligibility`
3. **Incremento estrito +1** (c) — proibido pular 2→4
4. **Assinatura simbólica em estado frio** (c) — Founder, com pregão fechado
5. **Cooldown reverso** (d):
   - 7 dias padrão
   - 21 dias se win streak ativo no momento da elegibilidade

---

## Convenção de nome

```
ESC-NNN-YYYY-MM-DD.md
```

Onde:
- `NNN` = número sequencial (001, 002, ...)
- `YYYY-MM-DD` = data da assinatura simbólica do Founder

---

## Template mínimo de arquivo

```markdown
---
template: ESCALONAMENTO
phase: GOVERNANCE
status: Proposed
esc_id: ESC-NNN
strategy_id: <UUID da estratégia (ou "agregado" se multiestratégia)>
date_proposed: YYYY-MM-DD
date_cooldown_ends: YYYY-MM-DD (proposed + 7 ou 21 dias)
date_in_force: (preenchido após cooldown sem revogação)
asset: WIN | WDO
limit_current: 2 (default) | N (escalonado vigente)
limit_proposed: limit_current + 1
win_streak_active_at_eligibility: true | false
---

# ESC-NNN — Escalonamento {WIN|WDO} {current}→{proposed} para {strategy_id}

## 1. Referência ao ScalingEvidence

ID do `ScalingEvidence` produzido pelo Risk Engine: <UUID>

Evidência (snapshot):

| Métrica | Valor medido | Critério mínimo (Art. 11-B a) | OK? |
|---|---|---|---|
| Profit Factor | x,xx | ≥ 1,8 | ✅/❌ |
| Win Rate | xx,x% | ≥ 55% | ✅/❌ |
| Expectância líquida (vs custo fixo) | x,xx× | ≥ 1,5× | ✅/❌ |
| Drawdown máximo | x,x% do Bucket Derivativo | ≤ 10% | ✅/❌ |
| Aderência operacional | xx,x% | ≥ 95% | ✅/❌ |

Período: pregões NNNN a NNNN (30 consecutivos).

## 2. Novo limite proposto

De **{current}** contratos {WIN|WDO} para **{proposed}** contratos {WIN|WDO}.

Incremento: +1 (estrito).

## 3. Motivação (mínimo 3 frases)

{frase 1}
{frase 2}
{frase 3}

## 4. Cooldown reverso

- Início: YYYY-MM-DD HH:MM
- Duração: 7 dias (padrão) ou 21 dias (se win streak ativo)
- Fim previsto: YYYY-MM-DD HH:MM
- Win streak ativo no momento da elegibilidade? Sim/Não
- Revogação durante cooldown permitida sem ônus: SIM

## 5. Assinatura simbólica do Founder

Em estado frio (pregão fechado, fora de D+0 de evento emocional):

- Data: ___/___/______
- Assinatura: ______________________

## 6. Aplicação (após cooldown)

- [ ] Cooldown cumprido sem revogação
- [ ] `cam_constitutional_scaling_events` registrou evento `IN_FORCE`
- [ ] FEATURE-FLAGS-LEDGER atualizada (se primeira ativação de SCALING_ENABLED)
- [ ] POV §3.12 (Limites Vigentes) atualizada com novo limite vigente

## 7. Reversão (preenchido se ocorrer)

- Data da reversão automática: ___
- Critério(s) que falharam: ___
- Drawdown durante período escalonado: ___ (será contado em dobro na próxima janela)
- Kill switch soft acionado (1 pregão bloqueado): Sim/Não
```

---

## Status atual (2026-05-27)

> **Diretório vazio.** Art. 11-B está vigente mas:
>
> - `cam/_shared/risk/scaling.py` ainda não foi implementado (BL-H2 da SPEC v0.4)
> - Job APScheduler pós-pregão ainda não foi wired
> - `cam_constitutional_scaling_events` (schema) ainda não foi migrado
> - `SCALING_ENABLED=false` por default no FEATURE-FLAGS-LEDGER
>
> **Primeiro escalonamento só é possível** após BL-H2 entregue + 1 estratégia operacional cumprindo a métrica composta por 30 pregões consecutivos. Realisticamente, isso fica para depois da Fase 2 (operação real inicial) — Anexo II da Constituição.

---

## Referências cruzadas

- [`/CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Art. 11-B
- [`/project/cam-constitution/README.md`](../README.md) — visão do diretório
- [`/project/cam-constitution/emendas/TD-v0.4-03-MULTIESTRATEGIA-v2.md`](../emendas/TD-v0.4-03-MULTIESTRATEGIA-v2.md) — emenda que criou Art. 11-B
- [`/project/POV-VIGENTE-v1.0.md`](../../POV-VIGENTE-v1.0.md) §3.12 — Limites Vigentes e Escalonamentos Aprovados
- [`/project/cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD`](../../cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD) — BL-H2 (Strategy Escalation Engine)

---

> **Princípio operacional:**
>
> Escalonamento é catraca de subida — análogo à Sangria do Art. 22º que é catraca de descida.
>
> Cada escalonamento exige evidência empírica forte, sinalização Risk Engine, formalização operador em estado frio, cooldown reverso e tem reversão automática se métricas caírem. Não é "subir o limite por estar ganhando" — é "subir o limite porque o sistema provou competência sustentada".

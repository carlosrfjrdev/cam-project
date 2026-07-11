---
template: EMENDA-CONSTITUCIONAL
phase: GOVERNANCE
status: Proposed
emenda_id: EMENDA-001
related_td: TD-v0.4-03
date_proposed: 2026-05-27
proposer: Carlos Rodrigues Ferreira Junior
protocol_version: 2.0
---

# EMENDA-001 — Multiestratégia Simultânea Autorizada

> Vinculada a `TD-v0.4-03` da SPEC v0.4-VISION-EVOLUTION (BL-H — Robot Orchestrator).
> Sem esta emenda ratificada, BL-H não entrega.

---

## 1. Necessidade exposta pelo Founder

A visão consolidada do CaM (`CAM-VISION-FINAL.MD`) declara que a arquitetura precisa ser **N-ready** (suportar N estratégias) mesmo que a operação inicial seja **1-first** (apenas 1 estratégia ativa). O `Robot Orchestrator` (BL-H da SPEC v0.4) é a peça que materializa essa capacidade — orquestra múltiplas estratégias com regras de prioridade, conflitos e risco agregado.

A Constituição vigente, em sua forma atual, **não trata multiestratégia explicitamente**. Os Arts. 11º (limite absoluto 2 WIN + 2 WDO) e 12º (1 contrato em Fases 1-2, sem simultaneidade WIN+WDO) **são interpretáveis como vedação implícita** a múltiplas estratégias operando em paralelo, mesmo quando a soma de contratos respeita o teto absoluto.

A necessidade real é tornar **explícita** a permissão de multiestratégia operando simultaneamente, desde que: (a) soma de contratos respeite Art. 11º intocável, (b) risco agregado seja modelado em código, (c) prioridade entre sinais conflitantes seja definida em POV. Sem essa explicitação, BL-H é inseguro de implementar (interpretação ambígua), e o sistema fica preso a 1 estratégia para sempre — contradizendo a visão N-ready aprovada em `R-19`.

---

## 2. Artigo(s) afetado(s)

- **Art. 11º** — alterado (texto vigente preservado em valor: 2+2 contratos absoluto)
- **Art. 11-A** — novo (criado por esta emenda)
- Implicitamente: Art. 12º (esclarecimento de "simultaneidade")

---

## 3. Texto vigente

### Art. 11º — Limite absoluto de contratos (vigente)

> O CaM nunca poderá operar acima de:
>
> - **2 contratos de mini índice (WIN)**;
> - **2 contratos de mini dólar (WDO)**.
>
> Este limite é absoluto e não poderá ser ultrapassado por saldo, confiança, sequência de ganhos, oportunidade de mercado, emoção, tentativa de recuperação ou decisão manual impulsiva.

### Art. 12º — Exposição na fase inicial (vigente)

> Na fase inicial real (Fase 2 — Anexo II), o CaM operará no máximo **1 contrato de mini índice OU 1 contrato de mini dólar**. A operação simultânea WIN + WDO é vedada na fase inicial.

---

## 4. Texto proposto

### Art. 11º — Limite absoluto de contratos (texto mantido)

> O CaM nunca poderá operar acima de:
>
> - **2 contratos de mini índice (WIN)**;
> - **2 contratos de mini dólar (WDO)**.
>
> Este limite é absoluto e não poderá ser ultrapassado por saldo, confiança, sequência de ganhos, oportunidade de mercado, emoção, tentativa de recuperação ou decisão manual impulsiva.
>
> **O limite se aplica à SOMA AGREGADA de contratos abertos** (Art. 11-A) — independentemente de quantas estratégias estejam operando simultaneamente.

### Art. 11-A — Multiestratégia simultânea (novo)

> Múltiplas estratégias podem operar simultaneamente no CaM, desde que:
>
> 1. **A soma de contratos abertos respeite o Art. 11º** (intocável: 2 WIN + 2 WDO no agregado, independente do número de estratégias).
> 2. **O risco agregado esteja modelado** em `cam/_shared/risk/aggregate.py` (módulo Pure Python, Zero I/O, com property-based testing) cobrindo no mínimo: exposição total por ativo, drawdown projetado se todos os candidatos forem aprovados, soma de operações abertas vs limite de fase.
> 3. **A prioridade entre sinais conflitantes** (mesma direção ou direções opostas no mesmo ativo) esteja definida explicitamente na POV vigente, em seção dedicada (POV §3.11 — Resolução de Conflitos).
> 4. **Cada estratégia em produção** tenha cumprido todos os gates do Art. 28º individualmente (backtest, walk-forward, paper, Risk Engine, contingência) antes de ser ativada.
> 5. **Kill switch global** (Art. 18º) propaga para TODAS as estratégias ativas simultaneamente — nenhuma estratégia pode ignorar kill switch sob alegação de "minha estratégia não foi a causa".

### Art. 12º — Esclarecimento (sem alteração de texto, apenas interpretação)

> A vedação de "operação simultânea WIN + WDO" em Fase 1-2 (Art. 12º) refere-se a **abrir simultaneamente posições em WIN e WDO**, e **NÃO** à operação simultânea de múltiplas estratégias que individualmente respeitem essa vedação. Em Fase 3+, operação simultânea WIN+WDO entre estratégias é permitida desde que o agregado respeite Art. 11º e Art. 11-A.

---

## 5. Impacto sistêmico esperado

| Componente | Impacto |
|---|---|
| `cam/_shared/risk/aggregate.py` | **NOVO módulo** — calcula risco agregado entre estratégias |
| `cam/features/robot_orchestrator/` | **NOVA feature** — BL-H da SPEC v0.4 |
| `cam/features/strategies/registry.py` | Permite `is_active=true` em N estratégias (era constraint 1) |
| POV vigente | **Nova §3.11** — resolução de conflitos entre sinais |
| `cam_strategies` (schema DB) | Permitir N rows com `is_active=true` (remove unique constraint) |
| `MAPPING-CONSTITUICAO-RISK-ENGINE.md` | Adicionar mapping de Art. 11-A → `aggregate_risk_check` |
| Order Gateway | Ganha lógica de orquestração de candidatos cross-strategy |
| Kill switch | Propagação global garantida via teste E2E |
| Property-based testing | Hypothesis cobrir 10.000+ cenários de risco agregado |

**Dependências:**

- SPEC v0.4 BL-A (Strategy Registry) já entregue
- SPEC v0.4 BL-C (Paper Loop Governado) com ≥ 1 estratégia em `paper_ok` ≥ 30 dias
- SPEC v0.4 BL-E (Read-write MT5 DEMO) entregue e validado

---

## 6. Crítica do Conselho Estratégico

### 6.1 Sun (estratégia / mercado)

Multiestratégia é **prática consolidada** em fundos de trading sistemático no Brasil e no mundo. CTA's (Commodity Trading Advisors), quants e gestoras quant operam dezenas de estratégias simultâneas — não por luxo, mas porque **diversificação de modelos** é a melhor proteção contra regime change. Uma estratégia ORB pode performar bem em janelas de tendência e zerar em range; uma mean reversion compensa nessas janelas. Operar **apenas 1 estratégia** é equivalente a apostar tudo num único setup — exatamente o que a Constituição existe para impedir.

A emenda é coerente com a tese estratégica do CaM. **Sun recomenda APROVAR**, com ressalva: a primeira multiestratégia em real exigirá que pelo menos uma das estratégias tenha track record demonstrável (S1 ORB com ≥ 100 trades paper + ≥ 60 dias de operação). Não basta ter N estratégias no registry — cada uma precisa de **evidência individual** antes de entrar no orquestrador real.

### 6.2 Voltaire (devil's advocate)

Existem **três modos de falha** que esta emenda não resolve sozinha — e que precisam ser vigiados na implementação de BL-H:

**M1 — Diluição de aderência.** Com 1 estratégia, aderência (Art. 29º) é trivial de medir e atribuir. Com N estratégias, se uma viola regra e outra cumpre, qual aderência conta? A emenda não responde isso. Recomendação: aderência calculada **por estratégia individual** + aderência **agregada do orquestrador** (média ponderada pelo número de trades). Operador acompanha as duas.

**M2 — Correlação encoberta.** Multiestratégia parece diversificação, mas se todas as estratégias compram WIN em rompimento de máxima, são "uma estratégia disfarçada de três". Risco agregado vira ilusão. Recomendação: além do Art. 11-A item 2 (risco agregado modelado), **medir correlação entre os retornos das estratégias** em janela rolling de 30 dias. Se correlação > 0.7 entre 2 estratégias ativas, sistema **alerta e bloqueia ativação de nova estratégia correlacionada**.

**M3 — Conflito de sinais com lógica oculta.** "Prioridade entre sinais conflitantes definida em POV" (item 3) parece simples, mas na prática é onde bugs nascem. Estratégia A diz "comprar WIN", estratégia B diz "vender WIN no mesmo segundo". Quem ganha? Empate? Cancela ambos? POV precisa ter **regra determinística e testável** com property-based testing antes de BL-H ir para paper.

Apesar dos 3 modos, **Voltaire aprova a emenda** — não por concordar com o desejo da expansão, mas porque a emenda **explicita** o que hoje está implícito e ambíguo. Implícito é pior. Recomendação final: aprovar **com cláusula adicional** de revisão obrigatória após 90 dias da primeira operação multiestratégia real.

### 6.3 Leo (orquestrador-chefe)

Esta emenda **destrava** BL-H — sem ela, o Robot Orchestrator é interpretativo demais para sobreviver a uma revisão Kevin. Do ponto de vista de orquestração de projeto, ela materializa o que `R-19` da VISION-FINAL já reconheceu: o Founder quer N estratégias, a arquitetura precisa permitir, e o caminho legal precisa estar registrado.

Impacto na cadência: BL-H é o segundo bloco mais complexo da SPEC v0.4 (depois de BL-E). Com a emenda aprovada, BL-H entra na Janela 4 da SPEC, depois de BL-E (DEMO read-write) estar estável. Sem a emenda, BL-H fica em loop indefinido — o que **trava também BL-I** (Multi-EA + DSL), pelas dependências cruzadas.

**Leo aprova** com observação de processo: a emenda deve ter **rastreabilidade dupla** — entrada no ledger constitucional (Passo 3) E entrada no `apps/cam-cockpit/FEATURE-FLAGS-LEDGER.md` quando `MULTI_STRATEGY_ENABLED` for ativada em produção. Sem essa rastreabilidade dupla, a feature pode ser ativada "por engano" via deploy sem que a emenda esteja em vigor.

### 6.4 Mammon (capital / custos)

Do ponto de vista de capital sobre R$ 5.000 declarados (Art. 7º), multiestratégia é **neutra ou positiva** em custos — não muda corretagem por trade nem feed de dados. **O risco financeiro real** é outro: com N estratégias, **frequência de trades pode subir N×**, e cada trade carrega corretagem + IRRF + spread. Se as estratégias operam o mesmo ativo, o capital de risco também cresce proporcionalmente.

A emenda mitiga isso no item 1 (soma respeita Art. 11º) e item 4 (cada estratégia cumpre Art. 28º antes de ativar). **Não mitiga** o fato de que **mais trades = mais custo fiscal**. IR Day Trade 20% incide sobre cada trade lucrativo. Se 3 estratégias geram 30 trades/mês (10 cada), o custo fiscal é ~3× maior que 1 estratégia gerando 10 trades.

**Mammon aprova com 1 recomendação operacional:** o `FeedInvestmentGate` (R-11 — expectância+drawdown+aderência por 30 dias) deve ser **aplicado por estratégia ativa**, não apenas no agregado. Estratégia que não bate R-11 individualmente não pode entrar no orquestrador, mesmo que o agregado esteja positivo. Isso evita que uma estratégia ruim seja "carregada" por outra boa.

### 6.5 Marty (escopo / discovery)

A emenda é tecnicamente bem formada — necessidade clara, texto preciso, impacto mapeado. **Marty aprova o escopo da emenda em si**. Mas levanta 2 pontos de discovery que precisam ficar registrados:

**Discovery D1 — Quantas estratégias começam ativas?** A emenda permite N, mas não declara N=2, N=3 ou N=10. Recomendação: BL-H entrega a capacidade, mas o **primeiro deploy operacional** com multiestratégia ativa N=2 (S1 ORB + S2 a definir). Crescer para N=3+ exige nova revisão pelo Founder.

**Discovery D2 — Setup A+ revisitado?** Art. 11º hoje permite 2 contratos APENAS em Setup A+ (Fase 4 — Glossário Constitucional). Multiestratégia complica: estratégia A pode pedir 1 contrato fora de Setup A+, estratégia B pede mais 1 contrato fora de Setup A+. Soma = 2, agregado respeita Art. 11º. Mas viola **espírito** de Setup A+ (que existe para limitar 2 contratos a momentos de máxima confluência). A emenda **não trata** essa tensão. Recomendação: adicionar item 6 ao Art. 11-A esclarecendo:

> *6. A regra de Setup A+ (Art. 11º + Anexo II Fase 4 + POV) aplica-se à SOMA de contratos do agregado, não a cada estratégia individual. 2 contratos no agregado em Fase 4 exigem que pelo menos 1 dos sinais conflitantes seja classificado como Setup A+ pela estratégia geradora.*

**Marty aprova condicionada** à adição do item 6 acima OU à declaração explícita pelo Founder de que esse esclarecimento fica para SPEC futura.

---

## 7. Decisão do Founder

```
[ ] APROVADA — sem alterações
[ ] APROVADA com adição do item 6 sugerido por Marty (Setup A+ no agregado)
[ ] REPROVADA — motivação:
    _________________________________________________
[x] REVISAR — novo texto proposto em arquivo separado:
    Referente ao item apontado por marty, realmente não é a cada estratégia, é global para evitar riscos, mas a trava de 2 contratos foi feita por medo da experiencia anterior... precisamos de um escape de oportunidade que o avaliador de risco nos dará... pensei uma taxa de acerto de 90% na estratédia por 20 pregões seguidos, autoriza o aumento, mas este deve ser formalizado pelo operador, no caso eu o founder isto é se o risco da estratégia sinalizar sucesso na operação real.

Motivação registrada para o ledger:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 8. Aplicação (preenchido apenas se aprovada)

- [ ] CONSTITUICAO.md editada — Art. 11º atualizado + Art. 11-A criado
- [ ] Apêndice B (Histórico de Versões) atualizado — versão 1.1
- [ ] POV-VIGENTE atualizada — §3.11 Resolução de Conflitos criada
- [ ] MAPPING-CONSTITUICAO-RISK-ENGINE.md atualizado — Art. 11-A mapeado
- [ ] `cam/_shared/risk/aggregate.py` priorizado no PLAN de BL-H
- [ ] Constraint DB de `cam_strategies.is_active` ajustada
- [ ] Ledger §3 do PROTOCOLO-EMENDA-CONSTITUCIONAL atualizado
- [ ] FEATURE-FLAGS-LEDGER atualizada com `MULTI_STRATEGY_ENABLED`
- [ ] Recomendações dos críticos endereçadas:
  - [ ] Sun — primeira multiestratégia exige track record demonstrável de 1+ estratégia
  - [ ] Voltaire M1 — aderência calculada por estratégia + agregada
  - [ ] Voltaire M2 — alerta de correlação > 0.7 entre estratégias
  - [ ] Voltaire M3 — POV §3.11 com regra determinística + property-based test
  - [ ] Voltaire cláusula — revisão obrigatória 90 dias após 1ª operação real
  - [ ] Leo — rastreabilidade dupla (ledger + feature flag)
  - [ ] Mammon — FeedInvestmentGate por estratégia individual
  - [ ] Marty D1 — primeiro deploy operacional com N=2
  - [ ] Marty D2 — item 6 do Art. 11-A ou declaração de SPEC futura

---

## Referências cruzadas

- [`/CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Arts. 11º, 12º, 18º, 28º, 29º, Anexo II
- [`/project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../../PROTOCOLO-EMENDA-CONSTITUCIONAL.md) — v2.0 simplificado
- [`/project/cam-cockpit/CAM-VISION-FINAL.MD`](../../cam-cockpit/CAM-VISION-FINAL.MD) — R-19 Multiestrategia aprovada com emenda
- [`/project/cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD`](../../cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD) — BL-H bloqueado por esta emenda
- [`/project/POV-VIGENTE-v1.0.md`](../../POV-VIGENTE-v1.0.md) — POV a estender com §3.11

---

> **Princípio operacional desta emenda:**
>
> Necessidade exposta. 5 críticas registradas. Founder decide.
>
> Multiestratégia destrava o Robot Orchestrator (BL-H). Sem ela, BL-H e BL-I ficam suspensos.

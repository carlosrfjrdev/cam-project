# Estado — OPS

> **Codinome:** NCC-1701 · **Status:** Draft (não refinado) · **Tipo:** Estado não numerado
> **Lead:** Vint
> **Decisão herdada:** SCOPE-FINAL §6.2 + §13 + Q15 Founder

## 1. Propósito

Reconhecer que o produto **vive em operação** após deploy. OPS é o estado contínuo onde acontecem: deploys recorrentes, ajustes de ambiente, incidentes, mudanças de infra, rotação de chaves, alertas.

## 2. Quando entrar no estado

OPS é **contínuo** após o primeiro DEPLOY de um produto. Qualquer evento operacional acontece dentro dele:

- incidente de produção;
- indisponibilidade ou degradação;
- bug em produção (entra também em BUG);
- rollback;
- intervenção manual;
- CVE crítica;
- rotação de chave;
- alerta de capacidade;
- decisão operacional emergencial.

## 3. Política de refinamento — **NÃO refinar ainda**

Q15 Founder: *"Ops não será refinada até pelo menos um produto em versão final... mantenha sugestão inferida por enquanto"*.

Portanto, esta versão **não traz**:
- taxonomia completa de tipos de evento;
- classificação de severidade formal (informal: alta/média/baixa);
- fluxo de roteamento;
- SLOs ou monitoramento estruturado;
- playbooks de incidente;
- escalation matrix.

**O que existe agora:** template `OPS-EVENT.md` mínimo para não perder histórico (R3 desta versão · ajuste GPT-PARECER §5.5 incorporado).

## 4. Saídas

| Artefato | Template | Persistência |
|---|---|---|
| `OPS-EVENT-{id}.md` mínimo (por evento relevante) | [`../templates/OPS-EVENT.md`](../templates/OPS-EVENT.md) | `/projects/{produto}/ops/` |
| `BUG-{id}.md` se evento gerou bug | [`../templates/BUG.md`](../templates/BUG.md) | `/projects/{produto}/bugs/` |
| Acionamento SEC-GOV se gatilho | — | [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md) |
| `PROOF-PACK.md` se incidente | [`../templates/PROOF-PACK.md`](../templates/PROOF-PACK.md) | obrigatório (R2) |

## 5. Personas

- **Lead:** Vint (Infrastructure & Cloud)
- **Cross-cutting:** Bill se gerou bug; Kevin se security incident; Steve/Tom se exige comunicação/release adicional.

## 6. Critério de saída de um evento OPS

- **Quem decide:** Founder
- **Critério de fechamento:** OPS-EVENT registrado com decisão e ação tomada; bug associado fechado (se houver); SEC-GOV resolvido (se acionado).
- **Critério de retorno:** evento aberto sem decisão, sem ação ou sem aprendizado registrado.

## 7. Skill associada

Não há skill própria para OPS na v6.0. Eventos OPS hoje são conduzidos manualmente por Vint + Founder. Se uma skill nascer, será proposta em subversão futura quando OPS for refinado.

## 8. Operação manual (Stage 0)

1. Evento operacional ocorre.
2. Vint avalia se vale registrar como OPS-EVENT (proporcional — eventos triviais podem ficar fora).
3. Vint preenche `OPS-EVENT-{id}.md` mínimo: data, evento, impacto, decisão, ação tomada, rollback (se houver), aprendizado.
4. Se houver bug: abrir `BUG-{id}.md` (estado BUG).
5. Se houver gatilho SEC-GOV (CVE crítica, security incident, data incident, etc.): acionar Kevin.
6. Se incidente: PROOF-PACK obrigatório.
7. Founder valida → evento fechado.

## 9. Anti-padrões

- Criar taxonomia OPS completa antes de produto em versão final — Q15 Founder.
- Definir SLO/SLI sem base operacional real.
- Tentar inferir severidade formal sem evidência.
- Registrar todo deploy bem-sucedido como OPS-EVENT — só eventos relevantes.

## 10. Referências

- SCOPE-FINAL §6.2, §13, Q15
- Template mínimo: [`../templates/OPS-EVENT.md`](../templates/OPS-EVENT.md)
- Estado relacionado: [`BUG.md`](BUG.md)
- Governança relacionada: [`../governance/SEC-GOV.md`](../governance/SEC-GOV.md)
- Dívida consciente: refinamento de OPS aparece na SPEC §11 (D3)

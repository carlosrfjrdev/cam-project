---
template: POV
phase: SPEC
status: Draft
version: 1.0
date: 2026-05-25
---

# POV-VIGENTE — Política Operacional Vigente do CaM

> **Versão:** 1.0
> **Lead:** Albert (especificação)
> **Suporte:** Denis (documentação)
> **Skill:** `teczi-demand-specification`
> **Aprovador:** Founder
> **Vinculação constitucional:** Arts. 37º (POV separada), 39º (cooldowns), 6º (preservar mais capital)
>
> **Status documental:** Esta POV v1.0 é a **extração formal** dos parâmetros numéricos do Anexo III da Constituição para documento próprio, conforme mandato do Art. 37º. **Sem alteração de valores.** Versionamento independente da Constituição se inicia aqui.

---

## 1. Identificação e vinculação constitucional

| Campo | Valor |
|---|---|
| Documento | POV — Política Operacional Vigente |
| Versão | 1.0 |
| Data de emissão | 2026-05-25 |
| Constituição vinculada | [`CONSTITUICAO.md`](../CONSTITUICAO.md) v1.0 |
| Origem dos valores | Anexo III da Constituição v1.0 (replicação integral, sem alteração) |
| Cooldown de alteração padrão | 3 dias (Art. 39º) |
| Cooldown de alteração que reduza proteção | 14 dias (Art. 39º) |
| Fase operacional vigente | Fase 0 — Construção (Anexo II) |
| Próxima revisão obrigatória | Junto da revisão anual da Constituição (Art. 40º), após 365 dias da Fase 2 OU sob solicitação do Founder |

### Hierarquia

```
Constituição (lei suprema, Art. 43º)
       ↓
POV (este documento — parâmetros operacionais)
       ↓
Risk Engine (executa POV + Constituição)
       ↓
Estratégia validada (opera dentro da POV)
       ↓
IA (não pode alterar POV — Art. 35º)
       ↓
Operador em decisão manual (sob hierarquia)
```

---

## 2. Princípio

A POV **opera dentro dos limites da Constituição e nunca pode contrariá-la** (Art. 37º).

### Regras invioláveis (não-negociáveis pela POV)

- **Art. 11º:** Limite absoluto de **2 contratos WIN + 2 contratos WDO**. A POV **não pode** elevar esse teto. Pode reduzir.
- **Art. 12º:** Operação simultânea WIN + WDO **vedada** em fases iniciais (Fase 1 e Fase 2). A POV **não pode** liberar.
- **Art. 16º:** Limites de perda diária (3%), semanal (7%), mensal (15%) são valores de partida — a POV pode **reduzir** (mais protetivo) mas nunca aumentar sem emenda constitucional via Art. 38º.
- **Art. 17º:** Gain Lock diário 2% é valor de partida — a POV pode **reduzir** mas nunca aumentar.
- **Art. 26º:** DARF atrasada bloqueia operações. A POV não pode adicionar exceções.
- **Art. 32º/33º:** Checklist obrigatório. A POV pode **expandir** itens, nunca remover.

### Diferença operacional entre Constituição e POV

| Aspecto | Constituição | POV |
|---|---|---|
| Tipo de mudança | Estrutural, semântica | Numérica, paramétrica |
| Cooldown padrão | 7 dias (Art. 38º) | 3 dias (Art. 39º) |
| Cooldown se reduz proteção | 30 dias | 14 dias |
| Processo | Emenda constitucional | Alteração de POV registrada |
| Onde registra | Ledger constitucional | Ledger de alterações da POV (§4.3) |
| Quem aprova | Founder em estado frio com pregão fechado | Founder em estado frio com pregão fechado |

---

## 3. Parâmetros vigentes (POV v1.0)

> Replicação integral do Anexo III da Constituição. **Sem alteração de valores.** Qualquer divergência futura entre este documento e o Anexo III deve ser resolvida em favor desta POV (pois é o documento operacional vivo), com nota explícita ao Founder.

### 3.1 Exposição por fase

| Fase | Regra de exposição | Artigo constitucional |
|---|---|---|
| **Fase 0 — Construção** | Sem trade real. Sem paper trading. | Anexo II |
| **Fase 1 — Paper Trading** | 1 contrato simulado por vez. WIN OU WDO, sem alternância no mesmo dia. | Art. 12º + Anexo II |
| **Fase 2 — Trade Real Inicial** | 1 contrato real. WIN OU WDO. Sem simultaneidade. Capital efetivo: R$ 1.500. | Arts. 11º, 12º + Anexo II |
| **Fase 3 — Trade Real Padrão** | 1 contrato padrão. WIN + WDO simultâneos permitidos com risco somado dentro do limite diário. | Art. 11º + Anexo II |
| **Fase 4 — Expansão Controlada** | 1 contrato padrão. **2 contratos permitidos apenas em Setup A+** (definição §3.10). | Art. 11º + Anexo II |

### 3.2 Limites de perda (sobre capital total declarado de R$ 5.000)

| Janela | Percentual | Valor absoluto | Ação ao atingir |
|---|---:|---:|---|
| **Diária** | 3% | R$ 150,00 | Bloqueia novas operações até o próximo pregão |
| **Semanal** | 7% | R$ 350,00 | Bloqueia novas operações até a próxima segunda-feira |
| **Mensal / Fase** | 15% | R$ 750,00 | Congela a fase atual, suspende trade real, retorna à fase anterior com revisão formal |

> **Origem:** Art. 16º. **Tipo:** valores invioláveis enquanto Art. 16º permanecer com 3/7/15%. POV pode reduzir (mais protetivo), nunca aumentar sem emenda constitucional.

### 3.3 Gain Lock

| Janela | Percentual | Valor absoluto | Ação ao atingir |
|---|---:|---:|---|
| **Diária** | 2% | R$ 100,00 | Encerra o dia. Bloqueia novas operações. |

> **Origem:** Art. 17º. **Tipo:** POV pode reduzir (mais protetivo), nunca aumentar sem emenda constitucional.

### 3.4 Operações máximas por dia

| Fase | Máximo de operações/dia |
|---|---:|
| Fase 1 | 3 |
| Fase 2 | 3 |
| Fase 3 | 5 |
| Fase 4 | 5 |

> **Origem:** Art. 20º + Anexo III. **Tipo:** POV pode reduzir, aumentar exige emenda constitucional via Art. 38º (proteção contra overtrade).

### 3.5 Stops padrão (parâmetro de estratégia)

| Ativo | Stop mínimo | Stop máximo |
|---|---:|---:|
| **WIN** | 150 pontos | 250 pontos |
| **WDO** | 3 pontos | 7 pontos |

> **Origem:** Anexo III. **Tipo:** parâmetro de estratégia — ajustável por backtest. Strategy concreta (DOC 4) define valor exato dentro da faixa.
> **Valor do ponto WIN:** R$ 0,20/ponto/contrato (especificação B3).
> **Valor do ponto WDO:** R$ 10,00/ponto/contrato (especificação B3).

### 3.6 Janelas vedadas de operação

| Janela vedada | Origem |
|---|---|
| Primeiros **15 minutos** pós-abertura do pregão | Anexo III |
| Últimos **10 minutos** antes do fechamento do pregão | Anexo III |
| Durante e **30 min antes/depois** de eventos macro de alto impacto: **Copom, FOMC, Payroll EUA, IPCA**, eventos extraordinários | Anexo III + extensão operacional |
| Pregão reduzido oficial da B3 (feriados, dia D-1 de feriado) | Extensão operacional — confirmar manualmente no calendário B3 vigente |

> **Origem:** Anexo III. **Tipo:** POV pode adicionar janelas (mais protetivo), remoção exige justificativa registrada com cooldown de 14 dias (reduz proteção).

### 3.7 Harvest Rule (sobre lucro líquido mensal após DARF)

| Destino | Percentual | Condição |
|---|---:|---|
| **Carteira Hard** | 60% | Aquisição de ativos de longo prazo (ações de dividendo, FIIs) |
| **Buffer Operacional** | 40% | Até atingir linha de base de **R$ 1.000,00** |
| **Carteira Hard (após Buffer restaurado)** | 100% do excedente | Quando Buffer já está em R$ 1.000 |

> **Origem:** Art. 21º + Anexo III. **Janela de execução:** mensal pós-apuração fiscal (SPEC R4.07). **Aprovação:** gate Founder obrigatório.

### 3.8 Sangria do Bucket Derivativo

| Parâmetro | Valor |
|---|---|
| **Disparo** | Bucket Derivativo atinge **R$ 4.500,00** (150% do valor base de R$ 3.000) |
| **Excedente sangrado** | R$ 1.500,00 |
| **Para Carteira Hard** | 80% do excedente = R$ 1.200,00 |
| **Para Buffer / Provisão fiscal** | 20% do excedente = R$ 300,00 |
| **Pós-sangria** | Bucket Derivativo retorna a R$ 3.000,00 |

> **Origem:** Art. 22º + Anexo III. **Mecanismo:** automático ao atingir o disparo, sujeito a confirmação Founder na execução real.

### 3.9 Aderência mínima para evolução de fase

| Métrica | Valor mínimo |
|---|---|
| **Aderência operacional** | **95%** (no máximo 1 violação a cada 20 operações) |
| Janela de medição | Toda a fase em curso |
| Origem | Art. 29º + Anexo III |

### 3.10 Setup A+ (a definir após Fase 3)

| Campo | Status |
|---|---|
| **Definição técnica** | **A definir após Fase 3.** |
| Requisito mínimo | Confluência objetiva de **pelo menos 3 fatores** (volatilidade, tendência de fundo, horário, contexto macro, etc.) |
| Forma final | Critério escrito, auditável, congelado em POV antes do uso real |
| Aplicabilidade | Único caso em que se permite 2 contratos em fases avançadas (Fase 4) |
| Origem | Glossário + Art. 11º + Anexo III |

> **Pendência declarada:** Sem definição técnica do Setup A+, a Fase 4 não pode operar 2 contratos. O Risk Engine bloqueia por design (validator `setup_a_plus_check`). Definição final será incluída em **POV v1.1** ou superior quando o Founder concluir a Fase 3.

### 3.11 Resolução de Conflitos entre Sinais (Multiestratégia — Art. 11-A item 3)

| Cenário | Regra de resolução determinística |
|---|---|
| **Sinais MESMA direção, MESMO ativo** | Soma de contratos respeita Art. 11º (default ou escalonado). Estratégia com maior **expectância líquida histórica** (últimos 30 pregões) tem prioridade se o agregado ultrapassar o limite — outra estratégia é parcialmente atendida ou rejeitada |
| **Sinais DIREÇÃO OPOSTA, MESMO ativo** | **Ambos rejeitados** + alerta "conflito direcional" + audit log (`event_type=DIRECTIONAL_CONFLICT`). Operador investiga manualmente |
| **Sinais MESMO momento, ATIVOS DIFERENTES (WIN/WDO)** | Avaliado pelo `aggregate_risk_check` — se soma + simultaneidade respeita Art. 11º + Art. 12º (e fase atual), ambos aprovados; caso contrário, prioridade por expectância |
| **Empate de expectância (tolerância 5%)** | **Kill-switch ambíguo** — sistema rejeita ambos, registra `event_type=AMBIGUOUS_TIE`, alerta operador. Conservadorismo (Art. 6º) |
| **Estratégia com aderência individual < 95%** | Sinal rejeitado mesmo se agregado caberia — estratégia suspensa do orquestrador até aderência recuperar (Art. 11-A item 7) |
| **Correlação > 0,7 entre 2 estratégias ativas** | Ativação de **nova** estratégia correlacionada é bloqueada; estratégias já ativas continuam mas geram alerta (Art. 11-A item 8) |

Toda regra acima **DEVE** ser implementada com property-based testing em `cam/_shared/risk/aggregate.py` antes de qualquer estratégia operar em paper governado.

### 3.12 Limites Vigentes e Escalonamentos Aprovados (Art. 11-B)

| Campo | Valor |
|---|---|
| **Limite vigente WIN** | 2 contratos (default) |
| **Limite vigente WDO** | 2 contratos (default) |
| **Escalonamentos aprovados ativos** | Nenhum |
| **Última proposta de escalonamento** | — |
| **Tetos absolutos (Art. 11-B item f)** | 5 WIN, 5 WDO, 3% drawdown diário — só elevável por revisão integral da Constituição |
| **Janela de elegibilidade** | 30 pregões consecutivos com métricas compostas (PF ≥ 1,8 + WR ≥ 55% + Expectância ≥ 1,5× custo fixo + DD ≤ 10% + Aderência ≥ 95%) |
| **Cooldown reverso padrão** | 7 dias |
| **Cooldown reverso se win streak ativo** | 21 dias |
| **Penalidade anti-reincidência** | DD durante escalonado conta em dobro para próxima janela |
| **Diretório de registros** | [`/project/cam-constitution/escalonamentos/`](../cam-constitution/escalonamentos/) (vazio até primeiro escalonamento) |

> Esta seção é **atualizada automaticamente** sempre que um escalonamento for ratificado, revogado durante cooldown ou revertido automaticamente.

### 3.13 Gain Lock Individual por Estratégia (Mammon — recomendação aprovada)

Quando o orquestrador estiver operando com **2 ou mais estratégias ativas** (Art. 11-A) e/ou em **estado escalonado** (Art. 11-B vigente), além do gain lock diário de 2% do capital declarado (§3.3):

| Métrica | Valor |
|---|---|
| **Gain lock individual por estratégia** | **5% do capital declarado em um único dia** |
| **Ação ao atingir** | Estratégia individual é suspensa do orquestrador pelo restante do pregão. Outras estratégias continuam operando |
| **Razão** | Evita que uma estratégia entre em modo "ilusão de competência" + carregue o agregado sem que o operador perceba |

---

## 4. Governança da POV

### 4.1 Processo de alteração

Toda alteração da POV segue o ritual:

1. **Pré-condição:** pregão fechado (mesma exigência de emenda constitucional — Art. 38º por analogia).
2. **Pré-condição:** Founder não está em D+0 de loss expressivo nem D+0 de gain expressivo.
3. **Proposta:** alteração registrada em arquivo separado `POV-AMENDMENT-NNN.md` em `/project/pov-amendments/` (a ser criado quando a primeira alteração for proposta) com:
    - Campo alterado (referência exata: §3.X.Y deste documento)
    - Valor anterior
    - Valor proposto
    - Motivação escrita (mínimo 3 frases)
    - Análise de impacto sobre Arts. 6º, 11º, 16º, 17º, 29º (que valores devem ser respeitados)
4. **Cooldown:** início imediato (carimbo de tempo de proposta = início do cooldown).
5. **Aprovação:** Founder confirma ao final do cooldown, com novo carimbo de tempo.
6. **Aplicação:** edita este documento, atualiza versão (`POV v1.0 → POV v1.1`), atualiza tabela §5.
7. **Registro:** entrada no ledger §4.3.

### 4.2 Cooldowns por tipo de alteração (Art. 39º)

| Tipo de alteração | Cooldown | Exemplos |
|---|---|---|
| **Padrão** | **3 dias** | Reduzir limite de perda diária de 3% para 2%; reduzir gain lock; adicionar janela vedada; refinar Setup A+ |
| **Reduz proteção** | **14 dias** | Aumentar limite de perda; aumentar máximo de operações; reduzir cooldown; remover janela vedada |
| **Toca limite absoluto Art. 11º** | **Não pode via POV** | Aumentar 2 WIN / 2 WDO → exige emenda constitucional pelo Art. 38º com cooldown de 30 dias |

### 4.3 Ledger de alterações da POV

> Histórico imutável de todas as alterações da POV. Cada linha é uma **versão**.

| Versão | Data | Campo alterado | Valor anterior | Valor novo | Motivação | Aprovador | Cooldown aplicado |
|---|---|---|---|---|---|---|---|
| 1.0 | 2026-05-25 | — | (replicação integral do Anexo III) | (idem) | Materialização do Art. 37º — POV como doc separado | Founder (assinatura pendente) | N/A (versão inicial) |
| **1.1** | **2026-05-27** | **§3.11, §3.12, §3.13 (novas)** | (não existiam) | Resolução de Conflitos · Limites Vigentes · Gain Lock Individual | EMENDA-001 v2 ratificada (Constituição v1.1) | Founder | N/A (parâmetros derivados de emenda constitucional) |

> Entradas futuras devem ser appendadas abaixo, **nunca editadas retroativamente**.

### 4.4 Restrições explícitas da POV

A POV **NÃO PODE**:

1. Alterar o limite absoluto do Art. 11º (2 WIN / 2 WDO) — exige emenda constitucional.
2. Reduzir cobertura de testes do Risk Engine (responsabilidade técnica, não POV).
3. Remover validators do Risk Engine — apenas ajustar parâmetros que os alimentam.
4. Alterar a hierarquia do Art. 36º (Constituição > Risk Engine > Estratégia > IA > Operador).
5. Justificar exceções operacionais em D+0 (Art. 4º — coragem excessiva é o inimigo).
6. Ser alterada por código automatizado, IA ou processo agêntico — apenas pelo Founder em estado frio.
7. Substituir a obrigação fiscal (Arts. 24º–26º) — alterações fiscais seguem legislação, não POV.

---

## 5. Histórico de versões

| Versão | Status | Data emissão | Data revogação | Principais mudanças vs. anterior |
|---|---|---|---|---|
| **1.0** | **Vigente** | 2026-05-25 | — | Versão inicial — extração formal do Anexo III da Constituição v1.0 para documento próprio (Art. 37º) |

> Próxima versão (1.1) será criada quando a primeira alteração de parâmetro for aprovada pelo Founder após cooldown.

---

## 6. Vínculo cruzado com a Constituição

**Anexo III da Constituição:** Após esta POV v1.0 entrar em vigor, o Anexo III da Constituição passa a ser **fundacional** e a POV é o documento operacional vivo. Recomendação para Denis na próxima edição da Constituição:

```
[ADD ao final do Anexo III, sem substituir o conteúdo existente]

> Nota operacional: os parâmetros numéricos vigentes a partir de 2026-05-25
> estão extraídos para `/project/POV-VIGENTE-v1.0.md`, conforme mandato do
> Art. 37º. Este Anexo é fundacional (não sofre alterações paramétricas
> sem emenda constitucional via Art. 38º); a POV é o documento operacional
> vivo, alterável via Art. 39º.
```

> **Esta nota é adição não-substitutiva.** A Constituição mantém todo o conteúdo do Anexo III como referência fundacional histórica.

### Mapeamento §3 desta POV ↔ artigos constitucionais

| Seção desta POV | Artigos vinculados |
|---|---|
| §3.1 Exposição por fase | Arts. 11º, 12º + Anexo II |
| §3.2 Limites de perda | Art. 16º |
| §3.3 Gain Lock | Art. 17º |
| §3.4 Operações máximas | Art. 20º |
| §3.5 Stops padrão | Art. 14º + parâmetro de estratégia |
| §3.6 Janelas vedadas | Anexo III + extensão operacional |
| §3.7 Harvest Rule | Art. 21º |
| §3.8 Sangria | Art. 22º |
| §3.9 Aderência | Art. 29º |
| §3.10 Setup A+ | Art. 11º + Glossário |

---

## 7. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior aprova a POV v1.0 como documento operacional
    vivo do CaM e reconhece que:

    a) A POV v1.0 não altera nenhum valor presente no Anexo III da Constituição —
       é replicação formal para versionamento independente conforme Art. 37º.

    b) A partir desta aprovação, alterações de parâmetros numéricos operacionais
       seguem o Art. 39º (cooldown 3 dias padrão, 14 dias se reduz proteção)
       e são registradas no ledger §4.3 deste documento.

    c) O Anexo III da Constituição permanece como referência fundacional histórica,
       sem revogação. Em divergência futura, prevalece esta POV (com nota explícita).

    d) Setup A+ permanece como pendência declarada (§3.10), a ser definido após
       Fase 3 e incluído em POV v1.1+.

    Data: ___/___/______

    Assinatura simbólica: ______________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) — Arts. 6º, 11º, 12º, 14º, 16º, 17º, 20º, 21º, 22º, 26º, 29º, 32º, 33º, 36º, 37º, 38º, 39º + Anexos II e III
- [`apps/cam-cockpit/backend/cam/_shared/risk/validators/`](../apps/cam-cockpit/backend/cam/_shared/risk/validators/) — validators que consomem estes parâmetros
- [`project/cam-cockpit/SPEC.md`](./cam-cockpit/SPEC.md) — contratos do Risk Engine que dependem desta POV
- [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md) — decisão-mãe que define plataforma onde a POV é executada

---

> **Princípio operacional deste documento:**
>
> A Constituição é lei. A POV é o regulamento. O Risk Engine é o juiz.
>
> Nenhum parâmetro entra em vigor sem cooldown. Nenhum cooldown é negociável.

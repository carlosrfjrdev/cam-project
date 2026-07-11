---
template: PROTOCOLO
phase: GOVERNANCE
status: Vigente
version: 2.0
date: 2026-05-27
constituent_act: true
predecessor: v1.0 (revogada por ato constituinte do Founder em 2026-05-27)
---

# PROTOCOLO-EMENDA-CONSTITUCIONAL — Versão Simplificada

> **Ato constituinte de 2026-05-27.** Carlos Rodrigues Ferreira Junior, exercendo poder constituinte originário (Art. 43º — "A única autoridade superior à Constituição é o próprio operador em estado frio"), simplifica este protocolo enquanto **o CaM ainda não opera no mercado**.
>
> **Lead da redação:** Kevin · Denis · Leo
> **Skill:** `teczi-security-governance` + `teczi-software-documentation`

---

## 0. Vigência condicionada

Este protocolo simplificado **vigora enquanto o CaM estiver em construção pré-operacional**, ou seja, enquanto:

- `REAL_TRADING_ALLOWED=false` for o default obrigatório, **E**
- nenhuma operação real (com capital declarado em risco) tiver sido executada via CaM.

**Quando o CaM entrar em Fase 1 com operação real autorizada pelo Founder, este protocolo é automaticamente revisado** (Art. 40º — revisão anual). Em estado operacional, o protocolo pode (e provavelmente deve) ganhar guardrails adicionais (cooldowns, restrições D+0, etc).

---

## 1. Princípio

**A Constituição é lei. O Founder é o constituinte.** Enquanto o CaM não operar, evoluir a Constituição é prerrogativa direta do Founder mediada por crítica do **Conselho Estratégico**.

O protocolo simplificado garante 3 coisas:

| O que garante | Como |
|---|---|
| **Necessidade real** | Founder expõe a necessidade por escrito antes de qualquer texto de emenda |
| **Crítica honesta** | Conselho Estratégico (Sun · Voltaire · Leo · Mammon · Marty) registra opinião contraditória antes da decisão |
| **Decisão registrada** | Founder aprova OU reprova com motivação no ledger constitucional |

Sem necessidade exposta → sem crítica → sem aprovação. O ritual é breve, mas existente.

---

## 2. Fluxo operacional (3 passos)

```
PASSO 1 — NECESSIDADE EXPOSTA PELO FOUNDER
       ↓
PASSO 2 — CRÍTICA DO CONSELHO ESTRATÉGICO + MAMMON
       ↓
PASSO 3 — APROVAÇÃO OU REPROVAÇÃO DA EMENDA PELO FOUNDER
```

### Passo 1 — Necessidade exposta pelo Founder

Founder cria arquivo em `/project/cam-constitution/emendas/{ID}-{slug}.md` com:

- **Necessidade** — o que motivou a emenda (3-5 frases).
- **Artigo(s) afetado(s)** — referência exata.
- **Texto vigente** — cópia do trecho atual.
- **Texto proposto** — novo texto.
- **Impacto sistêmico esperado** — features/SPECs que dependem da emenda.

> Sem este arquivo, não há emenda em curso.

### Passo 2 — Crítica do Conselho Estratégico + Mammon

O Conselho Estratégico **DEVE** registrar opinião escrita no mesmo arquivo da emenda. Membros obrigatórios:

| Persona | Papel na crítica |
|---|---|
| **Sun** (estratégia/mercado) | A emenda faz sentido na realidade de mercado? Edge competitivo afetado? |
| **Voltaire** (devil's advocate) | Modos de falha, anti-padrões, razões para NÃO fazer |
| **Leo** (orquestrador-chefe) | Impacto sistêmico, dependências, capacidade de execução |
| **Mammon** (capital/custos) | Custo financeiro, edge mínimo, preservação de capital |
| **Marty** (escopo/discovery) | Escopo, faseamento, refinamento, ambiguidade |

Cada persona escreve 1-2 parágrafos. **Sem 5 críticas registradas, Passo 3 não acontece.**

> **Forma operacional hoje:** Leo invoca cada persona via `Agent` tool, consolida no arquivo da emenda.

### Passo 3 — Aprovação ou reprovação pelo Founder

Founder lê a necessidade + as 5 críticas e decide:

- **APROVAR** — emenda entra em vigor imediatamente; Constituição é editada; ledger atualizado.
- **REPROVAR** — emenda arquivada com motivo registrado.
- **REVISAR** — Founder propõe novo texto; volta ao Passo 2.

Não há cooldown obrigatório enquanto CaM não operar. Founder em estado frio é o juiz.

---

## 3. Ledger constitucional

> Histórico imutável de todas as emendas confirmadas. Cada linha = uma emenda **aprovada**.

| # | Data | Artigo(s) | Resumo | Aprovador | Arquivo |
|---|---|---|---|---|---|
| **001** | **2026-05-27** | **Art. 11º + Art. 11-A + Art. 11-B** | **EMENDA-001 v2 — Multiestratégia simultânea + escalonamento condicional do limite por default. APROVADA com TODAS as recomendações do Conselho Estratégico (Sun, Voltaire, Leo, Mammon, Marty) incorporadas. Eleva Constituição para v1.1.** | Founder | [`/project/cam-constitution/emendas/TD-v0.4-03-MULTIESTRATEGIA-v2.md`](./cam-constitution/emendas/TD-v0.4-03-MULTIESTRATEGIA-v2.md) |

### Formato canônico de entrada

```
| NNN | YYYY-MM-DD | Art. XXº | Resumo curto | Founder | emendas/EMENDA-NNN-{slug}.md |
```

### Imutabilidade

- Entradas appendadas em ordem cronológica.
- **Nunca editar histórico.** Para corrigir registro incorreto, abrir nova entrada de "correção".
- Reprovações também são registradas (em seção separada §4).

---

## 4. Reprovações registradas

> Emendas que foram propostas mas reprovadas no Passo 3. Preserva memória do que **não** foi feito.

| # | Data | Resumo | Motivo da reprovação | Arquivo |
|---|---|---|---|---|
| — | — | — | (vazio) | — |

---

## 5. POV vs Constituição

| Tipo de mudança | Onde | Protocolo |
|---|---|---|
| **Parâmetro numérico operacional** (stop padrão, gain lock, janela vedada, etc.) | `POV-VIGENTE-vX.md` | Edição direta com nota no ledger da POV (Art. 39º) |
| **Artigo constitucional** (limite absoluto, hierarquia, processo) | `CONSTITUICAO.md` | Este protocolo simplificado (Passos 1→2→3) |

**Regra heurística:**
- Valor escrito **na Constituição** → emenda.
- Valor delegado **à POV** → alteração de POV.

---

## 6. Template de emenda (mínimo)

Arquivo a salvar em `/project/cam-constitution/emendas/{ID}-{slug}.md`:

```markdown
---
template: EMENDA-CONSTITUCIONAL
phase: GOVERNANCE
status: Proposed
emenda_id: EMENDA-NNN
related_td: TD-v0.X-NN  (opcional)
date_proposed: YYYY-MM-DD
proposer: Carlos Rodrigues Ferreira Junior
---

# EMENDA-NNN — {Título Curto}

## 1. Necessidade exposta pelo Founder

{3-5 frases descrevendo a necessidade real}

## 2. Artigo(s) afetado(s)

- Art. NNº — {nome do artigo}

## 3. Texto vigente

> (cópia exata)

## 4. Texto proposto

> (novo texto)

## 5. Impacto sistêmico esperado

- {SPEC/feature/módulo impactado 1}
- {SPEC/feature/módulo impactado 2}

## 6. Crítica do Conselho Estratégico

### 6.1 Sun (estratégia/mercado)
{1-2 parágrafos}

### 6.2 Voltaire (devil's advocate)
{1-2 parágrafos}

### 6.3 Leo (orquestrador-chefe)
{1-2 parágrafos}

### 6.4 Mammon (capital/custos)
{1-2 parágrafos}

### 6.5 Marty (escopo/discovery)
{1-2 parágrafos}

## 7. Decisão do Founder

[ ] APROVADA — data, motivação
[ ] REPROVADA — data, motivação
[ ] REVISAR — propor novo texto

## 8. Aplicação (se aprovada)

- [ ] CONSTITUICAO.md editada
- [ ] Apêndice B (Histórico de Versões) atualizado
- [ ] Documentos dependentes atualizados (lista)
- [ ] Código atualizado (lista de arquivos)
- [ ] Ledger §3 deste protocolo atualizado
```

---

## 7. Anti-padrões (5 essenciais)

1. **Editar Constituição diretamente sem registrar emenda** — invisível, não-auditável.
2. **Tomar decisão sem as 5 críticas do Conselho Estratégico** — viola Passo 2.
3. **Reescrever história do ledger** — entradas são imutáveis (§3).
4. **Confundir POV com Constituição** — valor numérico delegado à POV não vira emenda.
5. **Justificar emenda com "outro trader faz"** — emenda exige motivação própria, não imitação.

---

## 8. Diferenças em relação ao protocolo v1.0 (revogado)

| Aspecto | v1.0 (revogado) | v2.0 (vigente — pré-operacional) |
|---|---|---|
| Cooldown padrão | 7 dias | Nenhum enquanto CaM não opera |
| Cooldown se reduz proteção | 30 dias | Nenhum enquanto CaM não opera |
| Tipos de emenda (restritiva/expansiva) | 2 categorias rígidas | Categoria única (decisão Founder) |
| Pré-condições (D+0 loss/gain, pregão fechado) | Obrigatórias | Não-aplicáveis (CaM não opera ainda) |
| Passos do fluxo | 8 | 3 |
| Crítica formal externa | Implícita | **Obrigatória — 5 personas do Conselho** |
| Template | Extenso | Enxuto (§6) |

> **Motivo da simplificação:** Carlos como constituinte, atuando enquanto CaM ainda é construção (não operacional), removeu burocracia que protege contra estados emocionais **que ainda não podem existir** porque não há trade em curso. Quando trade real existir, o protocolo é revisado (§0).

---

## 9. Gate Founder (este protocolo)

```
[ ] Carlos Rodrigues Ferreira Junior, como constituinte originário do CaM,
    aprova este protocolo v2.0 como ato constituinte registrado em 2026-05-27.

    Reconhece que:

    a) O protocolo v1.0 fica REVOGADO.

    b) O protocolo v2.0 é simplificado (3 passos) ENQUANTO o CaM
       não estiver em operação real (REAL_TRADING_ALLOWED=false).

    c) Quando o CaM entrar em Fase 1 com operação real autorizada,
       este protocolo é AUTOMATICAMENTE revisado (Art. 40º) — pode
       (e provavelmente deve) ganhar cooldowns e restrições adicionais.

    d) A Constituição CaM permanece soberana (Art. 43º) — apenas o
       processo de emenda foi simplificado.
```

---

## Referências cruzadas

- [`/CONSTITUICAO.md`](../CONSTITUICAO.md) — lei suprema; Arts. 38º, 39º, 40º, 43º
- [`/project/cam-constitution/emendas/`](./cam-constitution/emendas/) — emendas propostas (a popular)
- [`/project/POV-VIGENTE-v1.0.md`](./POV-VIGENTE-v1.0.md) — POV vigente (parâmetros numéricos)
- [`/project/cam-cockpit/CAM-VISION-FINAL.MD`](./cam-cockpit/CAM-VISION-FINAL.MD) — visão que originou TD-v0.4-03 (multiestratégia)
- [`/project/cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD`](./cam-cockpit/SPEC-v0.4-VISION-EVOLUTION.MD) — BL-H bloqueado até emenda multiestratégia ratificada

---

> **Princípio operacional deste protocolo:**
>
> Necessidade exposta. Crítica honesta. Decisão registrada.
>
> Quando o CaM operar, o protocolo endurece. Hoje, ele acompanha a velocidade de construção sem deixar de existir.

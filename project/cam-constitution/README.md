---
template: README
phase: GOVERNANCE
status: Vigente
version: 1.0
date: 2026-05-27
---

# cam-constitution — Governança Constitucional do CaM

> Este diretório materializa a **governança constitucional** do CaM Cockpit: o processo de emenda, o Conselho Estratégico que critica propostas, os registros de escalonamento de limites e os arquivos das emendas em curso.
>
> **A Constituição em si** vive em [`/CONSTITUICAO.md`](../../CONSTITUICAO.md). Este diretório é a **mecânica de evolução** dessa Constituição.

---

## 1. Estrutura do diretório

```
project/cam-constitution/
├── README.md                                  ← este arquivo
├── emendas/                                   ← emendas propostas e aprovadas
│   ├── TD-v0.4-03-MULTIESTRATEGIA.md          (EMENDA-001 v1 — revisada)
│   ├── TD-v0.4-03-MULTIESTRATEGIA-v2.md       (EMENDA-001 v2 — em conselho)
│   └── ... (futuras EMENDA-NNN)
└── escalonamentos/                            ← se Art. 11-B for ratificado, registros de escalonamento vão aqui
    └── (vazio até primeira aplicação)
```

**Documentos vinculados (em outros diretórios):**

- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — lei suprema vigente
- [`/project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../PROTOCOLO-EMENDA-CONSTITUCIONAL.md) — protocolo v2.0 vigente (3 passos)
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — Política Operacional Vigente (parâmetros)
- [`/project/MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../MAPPING-CONSTITUICAO-RISK-ENGINE.md) — matriz artigo ↔ código

---

## 2. O Protocolo de Emenda (resumo)

A versão completa está em [`PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../PROTOCOLO-EMENDA-CONSTITUCIONAL.md). Resumo:

### Fluxo de 3 passos

```
PASSO 1 — NECESSIDADE EXPOSTA PELO FOUNDER
       ↓
PASSO 2 — CRÍTICA DO CONSELHO ESTRATÉGICO + MAMMON
       ↓
PASSO 3 — APROVAÇÃO OU REPROVAÇÃO DA EMENDA PELO FOUNDER
```

### Vigência condicionada

Este protocolo **simplificado** vigora **enquanto o CaM ainda não opera no mercado** (`REAL_TRADING_ALLOWED=false` + nenhuma operação real executada).

Quando o CaM entrar em **Fase 1 com operação real autorizada**, o protocolo é automaticamente revisado (Art. 40º — revisão anual) e pode ganhar guardrails adicionais (cooldowns, restrições D+0, etc).

> **Motivo da simplificação:** o protocolo v1.0 (revogado por ato constituinte em 2026-05-27) trazia cooldowns de 7/30 dias e tipos rígidos de emenda — proteções contra estados emocionais que **ainda não podem existir** porque não há trade em curso. Em construção pré-operacional, governança rápida é compatível com responsabilidade. Quando trade real existir, o protocolo endurece.

### Onde vai cada coisa

| Mudança | Vai em | Como autoriza |
|---|---|---|
| **Artigo constitucional** (limite absoluto, hierarquia, processo) | `CONSTITUICAO.md` | Emenda — passa pelos 3 passos deste protocolo |
| **Parâmetro numérico operacional** (stop padrão, gain lock, janela vedada) | `POV-VIGENTE-vX.md` | Edição direta com nota no ledger da POV (Art. 39º) |
| **Limite de contratos elevado acima do default** | `escalonamentos/{ID}.md` | Art. 11-B (se ratificado — pendente EMENDA-001 v2) |
| **Feature de software** | SPEC + PLAN + CODE | Skill DevFlow correspondente |

---

## 3. O Conselho Estratégico

O Conselho Estratégico é convocado **pelo Leo** (orquestrador-chefe) sempre que uma emenda constitucional é proposta. Sua função é **registrar crítica honesta antes da decisão do Founder** — não votar a emenda, mas iluminar trade-offs que o Founder pode ter ignorado na proposição.

### Composição (5 personas, todas obrigatórias)

| Persona | Cor | Lente principal |
|---|---|---|
| **Sun** | Strategy | Realidade de mercado; competitividade; evidência empírica de quanto o pedido faz sentido no contexto financeiro brasileiro |
| **Voltaire** | Devil's Advocate | Modos de falha; anti-padrões; razões para NÃO fazer; viés de sobrevivência |
| **Leo** | Orquestrador | Impacto sistêmico cross-feature; dependências; cadência de SPECs; capacidade de execução |
| **Mammon** | Capital | Custo financeiro; preservação de capital sobre os R$ 5.000 declarados; edge mínimo |
| **Marty** | Discovery/Escopo | Ambiguidade; faseamento; refinamento; granularidade; o que falta declarar |

### Por que essas 5 personas

- **Sun** representa o **fora** do sistema (mercado real); sem Sun, a emenda fica auto-referencial.
- **Voltaire** representa a **contradição saudável**; sem Voltaire, decisão vira eco do desejo do Founder.
- **Leo** representa a **integração**; sem Leo, emendas viram silos sem dependências mapeadas.
- **Mammon** representa o **dinheiro**; sem Mammon, decisões podem virar romantismo sem ROI.
- **Marty** representa o **rigor de escopo**; sem Marty, ambiguidade vira bug em produção.

### Como o Conselho funciona

1. **Founder cria** o arquivo de emenda em `emendas/` (Passo 1 do protocolo).
2. **Leo convoca** cada persona via `Agent` tool (skill correspondente) e consolida críticas no mesmo arquivo, seção §6.
3. Cada persona escreve **1-2 parágrafos** com sua leitura e voto:
   - ✅ Aprovar (incondicional)
   - ✅ Aprovar condicional (lista de condições)
   - ⚠️ Aprovar com observação
   - ❌ Reprovar (com motivo)
4. **Sem as 5 críticas registradas**, o Passo 3 (decisão Founder) não acontece.

### O Conselho **não vota** a emenda

O voto é do Founder. O Conselho **registra opinião contraditória** — função iluminadora, não decisória. Mesmo que todas as 5 personas aprovem, Founder pode reprovar. Mesmo que todas reprovem, Founder pode aprovar (Art. 43º — "A única autoridade superior à Constituição é o próprio operador em estado frio").

---

## 4. Tipos de artefato neste diretório

### 4.1 Emendas

Arquivo: `emendas/{ID}.md`

Cada emenda tem 9 seções (template em PROTOCOLO §6):

1. Necessidade exposta pelo Founder
2. Artigo(s) afetado(s)
3. Texto vigente
4. Texto proposto
5. Impacto sistêmico esperado
6. Crítica do Conselho Estratégico (5 personas)
7. Decisão do Founder
8. Aplicação (se aprovada)
9. Histórico (versões da emenda — Founder pode revisar quantas vezes quiser; conselho re-convocado em cada versão)

### 4.2 Escalonamentos (se Art. 11-B ratificado pela EMENDA-001 v2)

Arquivo: `escalonamentos/{ID}.md`

Diferente de emenda — escalonamento **não muda a Constituição**, apenas eleva temporariamente o limite vigente dentro do que o Art. 11-B autoriza. Cada escalonamento registra:

1. Referência ao `ScalingEvidence` produzido pelo Risk Engine (Art. 11-B item b)
2. Limite proposto (incremental — proibido pular passos)
3. Motivação registrada
4. Cooldown reverso (7 dias para revogação sem ônus)
5. Assinatura simbólica do Founder em estado frio

Reversão automática (Art. 11-B item e) registra evento adicional no mesmo arquivo (sem criar arquivo novo).

---

## 5. Status atual (2026-05-27)

### Constituição vigente

- **Versão:** **1.1 — Pós EMENDA-001 v2** (ratificada 2026-05-27)
- **Artigos:** 43 artigos originais + **Art. 11-A** + **Art. 11-B** novos + 3 Anexos + Apêndices A (memória v0.1) e B (histórico de versões atualizado)
- **Versão anterior:** 1.0 — Constituinte (ratificada 2026-05-24) — substituída pela v1.1

### Emendas ratificadas

| # | ID | Título | Data | Status |
|---|---|---|---|---|
| 001 | **EMENDA-001 v2** | Multiestratégia Simultânea + Escalonamento Condicional do Art. 11º | 2026-05-27 | ✅ **RATIFICADA** com TODAS as recomendações do Conselho Estratégico incorporadas |

### Emendas em andamento

> Nenhuma no momento.

### Escalonamentos aprovados

> Nenhum até a data. Art. 11-B está vigente mas sem aplicações — BL-H2 da SPEC v0.4 ainda precisa entregar `cam/_shared/risk/scaling.py` antes do primeiro `ScalingEvidence` ser computável.

### Ledger constitucional

Primeira entrada registrada em `/project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md` §3 (EMENDA-001 v2).

---

## 6. Princípios operacionais deste diretório

1. **Imutabilidade do histórico.** Emendas aprovadas, reprovadas e versões intermediárias nunca são apagadas — vão para `emendas/` com sufixo de versão.
2. **Transparência total.** Não há decisão constitucional "off-the-record". Tudo vira arquivo neste diretório.
3. **Crítica antes de decisão.** Founder não decide sem o Conselho ter registrado opinião.
4. **Founder soberano.** Conselho ilumina; Founder decide. (Art. 43º)
5. **Diretório vivo.** Quando CaM operar e protocolo endurecer, este README é atualizado para refletir a nova etapa de governança.

---

## 7. Convenções de nome

| Tipo | Padrão | Exemplo |
|---|---|---|
| Emenda nova | `EMENDA-NNN-{slug}.md` | `EMENDA-002-GAIN-LOCK-DUAL.md` |
| Revisão de emenda existente | `{nome-original}-v{N}.md` | `TD-v0.4-03-MULTIESTRATEGIA-v2.md` |
| Emenda vinculada a tech debt | prefixo `TD-vX.Y-NN-{slug}.md` | `TD-v0.4-03-MULTIESTRATEGIA.md` |
| Escalonamento | `ESC-NNN-{data}.md` | `ESC-001-2026-08-15.md` |

---

## 8. Como propor uma nova emenda

1. Identifique a necessidade. Escreva em 3-5 frases. Sem isso, não comece.
2. Crie o arquivo em `emendas/EMENDA-NNN-{slug}.md` usando o template do [`PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../PROTOCOLO-EMENDA-CONSTITUCIONAL.md) §6.
3. Convoque Leo: `@leo, emenda nova em emendas/EMENDA-NNN — convoca conselho`.
4. Leo invoca Sun, Voltaire, Mammon, Marty (Leo já está presente) — cada um escreve sua crítica na §6 do arquivo.
5. Leia as 5 críticas em estado frio.
6. Decida no §7: aprovar, aprovar condicional, reprovar ou revisar.
7. Se revisar: edite o arquivo (`-v2`, `-v3`...), Leo re-convoca o conselho.
8. Se aprovar: cumpra §8 (aplicação) — edite Constituição, ledger, código.

---

## 9. Boundaries — o que este diretório NÃO é

- ❌ Não é repositório de POV (parâmetros operacionais) — POV vive em `/project/POV-VIGENTE-vX.md`
- ❌ Não é runbook operacional — runbooks vivem em `/project/runbooks/`
- ❌ Não é SPEC/PLAN de feature — esses vivem em `/project/cam-cockpit/`
- ❌ Não é texto da Constituição em si — a Constituição vive em `/CONSTITUICAO.md` (raiz)
- ❌ Não é repositório de decisões cotidianas — apenas emendas/escalonamentos formais

---

## 10. Referências cruzadas

- [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — lei suprema vigente
- [`/project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../PROTOCOLO-EMENDA-CONSTITUCIONAL.md) — protocolo v2.0
- [`/project/POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) — POV operacional
- [`/project/MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../MAPPING-CONSTITUICAO-RISK-ENGINE.md) — matriz artigo ↔ código
- [`/teczi-devflow/personas/`](../../teczi-devflow/personas/) — definições completas das personas do Conselho

---

> **Princípio operacional final:**
>
> A Constituição é lei. O Founder é constituinte. O Conselho ilumina. Este diretório registra tudo.
>
> Enquanto o CaM não operar, governança rápida. Quando operar, governança endurece. Em ambos os estados, **tudo é registrado**.

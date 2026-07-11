---
template: DESIGN-REVIEW
phase: PLAN (co-participante)
status: PROPOSTA — direção criativa (Andy)
produto: TCaM (cam-cockpit)
id: DESIGN-REVIEW-FRONTEND
slug: design-review-frontend-complexidade
data: 2026-06-03
autor: Andy (design visual / direção criativa)
solicitante: Founder
contexto: Feedback do Founder — "em front, está muito complexa as telas geradas sem ganho significativo"
informa: SCOPE-STRATEGYLAB-TRIAD §2 (telas Strategy / RunTests / Experts)
---

# Design Review — Frontend TCaM: complexidade sem ganho

> **Premissa que muda tudo:** o CaM era painel de **um** especialista (o Founder, que sabe o
> que cada número significa). O TCaM é **produto para terceiros**. Um terceiro abre a tela e
> não tem o contexto que o Founder tem na cabeça. **Toda densidade que era "ok porque eu sei
> ler" virou ruído.** Esta review parte daí.

Eu li o código real, não a intenção. As telas não estão "feias" — estão **sobrecarregadas**.
O problema não é estética, é **edição**: ninguém cortou. Cada feature empilhou tudo que tinha
para mostrar numa única coluna vertical de `Paper` atrás de `Paper`. Isso é o oposto de design.
Design é decidir o que **não** mostrar.

---

## 1. Diagnóstico honesto — onde está complexo demais (com arquivo)

### 1.1 O padrão-vício: "pilha de Papers" (todas as telas)

Todas as telas seguem o mesmo molde: `<Box>` → `Typography h5` → `Paper` → `Paper` → `Paper`…
empilhados verticalmente, **todos com o mesmo peso visual**. Não há hierarquia: o gráfico
principal e um aviso de rodapé ocupam o mesmo tipo de caixa, mesma elevação, mesma margem.

- `InspetorPage.tsx` (L88-234): são **5 Papers** empilhados (busca, cabeçalho+gráfico, book,
  fundamentos+dividendos, regime). Quando o ativo carrega, a tela vira um scroll infinito onde
  tudo grita igual. **Não há "a manchete"** — o preço/gráfico deveria dominar; em vez disso
  divide atenção com 7 cards de indicadores, uma tabela de book, uma tabela de dividendos, uma
  matriz de transição e um Alert de caveat de 4 linhas.
- `QuantLabPage.tsx` (L46-186): 3 Papers fixos (Ingestão, Data Health, Registro) + 2 componentes
  pesados injetados (`LeadLagAnalysis`, `RunRegistry`). **Quatro tabelas** podem aparecer
  simultaneamente na mesma página vertical.

**Veredito:** a "complexidade sem ganho" que o Founder sentiu é literalmente isto — empilhamento
sem priorização. Não é que tenha informação demais; é que **nada está subordinado a nada**.

### 1.2 Pior ponto #1 — `LeadLagAnalysis.tsx`: a tela que fala com o autor, não com o usuário

Este é o exemplo mais agudo de "painel de especialista vazado para produto":

- **Jargão cru na superfície** (L149-153, L192-198): colunas `melhor |C|`, `δ (barras)`, `DSR`,
  e um `Alert` de 6 linhas explicando "FDR", "data-snooping", "mata-Epps (HY)", "deflação
  estatística". Isso é a transcrição de uma conversa entre Jim e Voltaire — não é UI. Um terceiro
  não faz ideia do que é DSR e a tela **não o ajuda**, só o intimida.
- **Densidade tripla simultânea** (L131-191): heatmap + (condicional) gráfico de perfil + tabela
  de 6 colunas — os três visíveis ao mesmo tempo, mais 4 chips de status (L111-124) acima. São
  **quatro representações dos mesmos dados** competindo na mesma dobra.
- **Chips como prosa** (L60-66): `sobrevivente`, `morta (FDR)`, `dado insuficiente` — vocabulário
  interno usado como label de UI.

### 1.3 Pior ponto #2 — `RegimePanel.tsx`: caveat maior que o conteúdo

- O `Alert severity="warning"` (L96-100) tem **4 linhas de ressalva técnica** ("rótulo defasado",
  "janelas sobrepostas autocorrelacionam", "Sharpe bruto", "filtro macro grosseiro") — **mais
  texto do que o dado que ele qualifica**. A intenção (honestidade) é nobre, mas em produto isso
  vira parede de texto que ninguém lê e que faz a tela parecer um aviso legal.
- Logo acima, a **matriz de transição** (L65-85): uma tabela Markov 3×3 com percentuais. Para o
  Founder é leitura; para um terceiro é uma matriz de probabilidade sem onboarding. Mais o
  "mix de longo prazo" (L87-94) e `data.attribution` em caption. **Quatro blocos de informação
  densa** num painel que deveria responder uma pergunta: "esse ativo está em tendência ou não?".

### 1.4 Pior ponto #3 — `RiskConsolePage.tsx`: tudo é uma linha `label / valor`

- O Paper "POV Vigente" (L51-91): **8 linhas** `Stack direction=row justify=space-between` com
  `label` à esquerda e valor à direita. É uma planilha disfarçada de card. Não há agrupamento
  visual, não há o que importa em destaque — "Máx Contratos WIN: 2" tem o mesmo peso de
  "Conformidade Fiscal: OK". Numa tela de **risco**, o que está perigoso deveria saltar; aqui
  tudo é cinza uniforme.
- Convive com **3 tabelas** na mesma página (Aderência, Decisões) + um Paper "Kill Switch —
  Histórico" (L95-101) que é só um título com placeholder e **nenhum conteúdo** — caixa vazia
  ocupando espaço e atenção.

### 1.5 Sintomas transversais

| Sintoma | Onde | Efeito no usuário |
|---|---|---|
| `Typography h5` + `body2` de subtítulo repetidos em **toda** página | Inspetor L90-95, QuantLab L48-56 | Cada tela "se reapresenta"; nenhuma assume o protagonista |
| Chips usados como texto corrido / caveats | LeadLag L60-66, Regime L43, Dividends L38 | Chip vira ruído, perde a função de "status rápido" |
| Tabelas densas como exibição default | RunRegistry, LeadLag, Risk, QuantLab health | "Sou ferramenta de analista", não "sou produto" |
| Jargão sem tradução | DSR, FDR, |C|, δ, "agressor", "stationary" | Exclui quem não é o autor da tela |
| Margem lateral fixa `px:"5%"` em Inspetor/Lab vs `p:3` no resto | Inspetor L89, Cockpit L41 | Inconsistência de container entre telas |
| `Paper` sem hierarquia de elevação/contraste | todas | Tudo no mesmo plano = nada em foco |

---

## 2. Princípios de simplificação para o TCaM

Cinco regras. Servem de critério de aceite visual para qualquer tela nova (incluindo a tríade).

1. **Uma manchete por tela.** Cada tela responde **uma** pergunta dominante e tem **um** elemento
   visual que domina (≈60% da atenção da primeira dobra). Inspetor = o gráfico. RunTests = a curva
   de equity. Strategy = a lista. Todo o resto é coadjuvante e visualmente menor.
2. **Progressive disclosure por padrão.** O que é de especialista **começa fechado**. Matriz de
   transição, DSR, caveats estatísticos, parâmetros avançados, tabelas longas → atrás de
   "Mostrar detalhes" / Accordion / aba secundária. A tela default mostra a **conclusão**, não a
   **evidência**. Quem quer a evidência clica.
3. **Conclusão antes de evidência.** Não mostre a matriz Markov 3×3; mostre **"Tendência de alta
   (forte)"** e ofereça a matriz no expand. Não mostre 6 colunas de correlação; mostre **"VALE3
   lidera PETR4 em ~5 barras"** e ofereça a tabela no expand.
4. **Sem jargão na superfície.** Termo técnico (DSR, FDR, δ, |C|) só aparece em camada de detalhe,
   sempre com tooltip/legenda. Na superfície: linguagem de resultado em português. Caveat de
   honestidade vira **um chip "estimativa"/"bruto" com tooltip**, não um parágrafo.
5. **Cortar antes de agrupar, agrupar antes de mostrar.** Para cada bloco pergunte: (a) dá pra
   **cortar**? (b) se não, dá pra **fundir** com o vizinho? (c) só então mostre — e decida se é
   superfície ou detalhe. Caixa vazia (Kill Switch placeholder) = cortar já.

> **Métrica de design simples:** se a primeira dobra tem **mais de 3 blocos** competindo por
> atenção igual, a tela falhou. Reduza a 1 manchete + no máximo 2 apoios.

---

## 3. Diretrizes para a tríade StrategyLab (desenhar simples desde o início)

A tríade (`SCOPE-STRATEGYLAB-TRIAD` §2) é **G** e atravessa 10 estratégias, multi-símbolo,
otimizador. É exatamente o tipo de escopo que, sem disciplina, repete o erro do LeadLag elevado
ao cubo. Wireframes textuais com o **mínimo viável** — a regra é: o usuário avança por **fluxo**
(escolher → rodar → ver resultado), não por **scroll de tudo ao mesmo tempo**.

### 3.1 Assets Strategy — "minhas estratégias"

**Pergunta da tela:** qual estratégia eu quero olhar/ajustar/otimizar?
**Manchete:** a **lista/grid de estratégias**. É só isso na primeira dobra.

```
┌─────────────────────────────────────────────────────────┐
│  Estratégias                          [ + nova ] [busca] │   ← título seco, sem subtítulo-prosa
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ D1       │ │ D3       │ │ S1       │ │ LS2      │    │   ← cards uniformes, 1 linha de status
│  │ ORB-30   │ │ WIN×WDO  │ │ Momentum │ │ Pair     │    │
│  │ WIN  ●ok │ │ par ●ok  │ │ cesta    │ │ par      │    │   ● = status (1 chip, 1 cor)
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────┘
        clicar num card → painel de detalhe (drawer lateral ou rota)
```

- **Manchete:** grid de cards. Cada card = nome curto + família + símbolo(s) + **um** chip de
  status. Nada mais. Multi-símbolo aparece como "par" / "cesta" (uma palavra), não duas linhas.
- **Secundário (no detalhe, não na lista):** parâmetros da estratégia. Abre em **drawer** ao
  clicar no card. Form simples, label→campo. Avançados num accordion "Parâmetros avançados".
- **On-demand (botão explícito):** "Otimizar". O otimizador é a peça perigosa (Nassim) — então a
  UI dele é **deliberadamente sóbria**: dispara → mostra **uma** recomendação ("sugerido: janela
  20, stop 1.5×ATR") + um selo de robustez ("testou 240 combinações · OOS ok · superfície chata")
  como **3 chips**, não como dump da grade inteira. O Founder decide adotar; sem auto-apply.
  **Não** mostrar a superfície inteira de busca por default — isso é o detalhe atrás de "ver
  varredura".

### 3.2 Assets RunTests — "rodei, e aí?"

**Pergunta da tela:** essa estratégia, nesse período, deu o quê?
**Manchete:** a **curva de equity**. Domina a dobra. Tudo abaixo é apoio.

```
┌─────────────────────────────────────────────────────────┐
│  Backtest · D1 ORB-30 · WIN · 2024-01→2024-12   [rodar] │   ← config compacta em 1 linha
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │                                                   │    │
│  │        CURVA DE EQUITY  (manchete)                │    │   ← 1 gráfico grande domina
│  │                                                   │    │
│  └─────────────────────────────────────────────────┘    │
│  [WR 54%] [Profit Factor 1.4] [Trades 88] [DD -6%]      │   ← 4 métricas-chave como tira de chips
│                                                          │
│  ▸ Trades (88)            ← accordion FECHADO por default │   ← tabela longa escondida
│  ▸ Walk-forward (OOS)     ← accordion FECHADO            │
│  [bruto] ← chip com tooltip "sem custo/IR — não é edge líquido"
└─────────────────────────────────────────────────────────┘
```

- **Manchete:** equity. Uma só. Grande.
- **Apoio imediato:** 4 métricas-chave como **tira de chips/stat-cards** (WR, PF, nº trades, DD).
  Não uma tabela de métricas — uma tira. Máximo 4-5.
- **Detalhe escondido:** a **lista de trades** (que no LeadLag/Risk vira tabelão default) entra
  **fechada** num accordion "Trades (N)". Walk-forward idem. Para multi-símbolo, a tabela de
  trades mostra "par como unidade" (decisão Q10 do SCOPE) — uma linha por trade-par; pernas
  separadas só no expand da linha.
- **A trava de honestidade do MVP-bruto** (Jim/Voltaire) — crítica e **não pode virar parágrafo**:
  um **chip `bruto`** persistente ao lado do título, tooltip "valores brutos: sem custo, sem IR —
  não confirma edge líquido". Uma palavra na superfície, a ressalva completa no hover. Isso resolve
  a tensão "honestidade × poluição" que o RegimePanel errou.

### 3.3 Assets Experts — "meus robôs estão rodando?"

**Pergunta da tela:** quais robôs existem, qual o estado de cada um?
**Manchete:** a **lista de robôs com status ao vivo** (a coisa mais próxima de um "operacional").

```
┌─────────────────────────────────────────────────────────┐
│  Robôs (Experts)                         [conexão MT5 ●] │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │ D1 ORB-30 · WIN     ● rodando   [DEMO]   ⏻       │    │   ← linha = robô; status grande,
│  │ D3 WIN×WDO · par    ○ parado    [DEMO]   ⏻       │    │     guard-rail DEMO sempre visível
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ▸ Logs / fills do robô selecionado   ← detalhe on-click │
└─────────────────────────────────────────────────────────┘
```

- **Manchete:** lista de robôs, status grande e legível (rodando/parado), **selo DEMO sempre
  visível** (guard-rail de conta do SCOPE §2.4 vira affordance visual, não letra miúda).
- **Secundário:** logs/fills do robô selecionado — abrem ao clicar, não todos de uma vez.
- **Cuidado especial:** esta é a única das três que **toca execução**. O selo DEMO e o
  estado conexão-MT5 são os dois únicos elementos que podem ter cor forte. Resto sóbrio. Botão de
  parar (kill por robô) é o único acento de ação destacado.

> **Regra de ouro da tríade:** Strategy → RunTests → Experts é um **fluxo** (defino → testo →
> opero). Cada tela tem **uma** manchete e empurra o detalhe para drawer/accordion/clique.
> Se em qualquer das três aparecerem 3+ tabelas na vertical, repetimos o erro do LeadLag.

---

## 4. Quick wins nas telas existentes (sem reescrever)

Mudanças cirúrgicas, baixo risco, alto efeito de "respiro":

1. **Inspetor — colapsar Regime e Book em accordion fechado.** `InspetorPage.tsx` L184-231:
   envolver `BookPanel`, `FundamentalsPanel`/`DividendsPanel` e `RegimePanel` em `Accordion`
   fechados por default, deixando só **gráfico + preço** abertos. A manchete (gráfico) passa a
   dominar imediatamente. Esforço mínimo, ganho enorme.
2. **RegimePanel — caveat vira chip+tooltip.** `RegimePanel.tsx` L96-100: trocar o `Alert` de 4
   linhas por um `Chip "leitura, não sinal"` com `Tooltip` contendo o texto. Mover a matriz de
   transição L65-85 para dentro de "▸ Ver matriz de transição". Superfície fica: estado atual +
   1 número de sinal. O resto on-demand.
3. **LeadLagAnalysis — esconder heatmap+tabela atrás de tabs.** `LeadLagAnalysis.tsx` L131-191:
   uma única visão default (a **tabela enxuta**, 3 colunas: Fonte / lidera em δ / veredito-em-PT),
   com heatmap e perfil C(δ) em tab/accordion "Visão detalhada". Traduzir labels: `melhor |C|` →
   "força", `δ` → "defasagem". Mover o `Alert` glossário L192-198 para um "?" tooltip no título.
4. **RiskConsole — matar a caixa vazia + destacar o que é perigo.** `RiskConsolePage.tsx`
   L95-101: remover o Paper "Kill Switch — Histórico" placeholder (caixa sem conteúdo) até existir
   dado. No "POV Vigente" L51-91, dar **peso visual só ao que pode estar fora do limite** (cor no
   valor quando há violação), deixando o resto secundário.
5. **QuantLab — Data Health colapsado quando há dados.** `QuantLabPage.tsx` L95-174: as duas
   tabelas de health são diagnóstico, não conteúdo principal. Accordion fechado por default
   (abre se vazio/erro). A manchete da página passa a ser a análise, não o relatório de saúde.
6. **Padronizar o container.** Unificar `px:"5%"`/`p:3` num único wrapper de página (ver §5).
   Tira a inconsistência de margem entre Inspetor/Lab e o resto.

---

## 5. Design system mínimo (tokens + padrões reutilizáveis)

O tema já existe e é bom (`theme.ts` — DS CAM Esmeralda, dark-first, tokens de cor/raio/fonte
definidos). O que **falta** não é token de cor — é **padrão de composição**. Proponho 4
componentes-padrão que matam 80% da inconsistência e da densidade. Todos reutilizáveis pela tríade.

### 5.1 `<PageHeader title actions? />`
Substitui o par `Typography h5` + `body2`-subtítulo repetido em toda tela. **Título seco, sem
parágrafo de subtítulo.** Ações (botões/chips de status) à direita. Uma manchete textual por tela.
Mata: Inspetor L90-95, QuantLab L48-56, e a "reapresentação" de cada página.

### 5.2 `<PageContainer>`
Wrapper único de página: `px` responsivo padrão + `py` + maxWidth opcional. Acaba com
`px:"5%"` vs `p:3`. **Uma** densidade de margem no produto inteiro.

### 5.3 `<StatStrip items=[{label, value, tone?}] />`
A tira de 3-5 métricas-chave (WR, PF, DD…). **Substitui** o anti-padrão "8 linhas label/valor"
do RiskConsole e o "matriz de números" do Regime. Um número grande, label pequeno, no máximo 5.
É a forma canônica de "resumo numérico" — RunTests, Regime, Risk usam a mesma.

### 5.4 `<DetailDisclosure title>` (accordion fechado padronizado)
O recipiente canônico de **tudo que é detalhe/evidência/tabela longa**. Fechado por default,
mesma tipografia de cabeçalho, mesmo espaçamento. É onde vão: matriz Markov, tabela de trades,
heatmap, walk-forward, logs de robô, parâmetros avançados, glossários de jargão.

### 5.5 Regras de densidade (tokens de comportamento)

| Token | Regra |
|---|---|
| **Tabela** | `size="small"` sempre; **máx ~6 colunas** na superfície; >6 ou >10 linhas → dentro de `DetailDisclosure` |
| **Chip** | só para **status/estado** (1 palavra) — nunca para frase, caveat ou explicação |
| **Caveat / honestidade** | 1 chip na superfície + texto completo no `Tooltip`. Nunca `Alert` multi-linha como conteúdo permanente |
| **Jargão** | proibido na superfície; só em `DetailDisclosure` ou `Tooltip`, sempre traduzido em PT na 1ª aparição |
| **Cor forte** (founderOrange/error/warning) | reservada a **1-2 elementos** por tela (perigo, ação principal, selo DEMO). Não decorar |
| **Paper/elevação** | a manchete usa contraste maior; apoios usam `surface1` plano. Hierarquia visível |
| **Primeira dobra** | máx 1 manchete + 2 apoios competindo. 3+ blocos iguais = refatorar |

> Esses 4 componentes + 7 regras são o **mínimo** para a tríade nascer consistente. Não é um DS
> grande — é o suficiente para que Strategy/RunTests/Experts não repitam a pilha-de-Papers.

---

## Resumo executivo (retorno ao Founder)

**Os 3 piores pontos de complexidade hoje:**
1. **`LeadLagAnalysis.tsx`** — jargão de especialista cru na superfície (DSR, FDR, |C|, δ) +
   heatmap + gráfico + tabela de 6 colunas + glossário de 6 linhas, **tudo visível ao mesmo
   tempo**. É uma conversa técnica vazada para a UI.
2. **`RegimePanel.tsx`** — caveat (`Alert` de 4 linhas) **maior que o dado**, mais matriz Markov
   3×3 + mix de longo prazo + attribution: quatro blocos densos para responder uma pergunta
   simples ("tendência ou não?").
3. **Padrão transversal "pilha de Papers"** (Inspetor 5, QuantLab 3+2, RiskConsole 3 tabelas +
   caixa vazia) — empilhamento vertical **sem hierarquia**: nada é manchete, tudo grita igual.
   É a causa-raiz da sensação de "complexo sem ganho".

**Princípios de simplificação (5):** uma manchete por tela · progressive disclosure por padrão ·
conclusão antes de evidência · zero jargão na superfície · cortar → agrupar → só então mostrar.

**Diretrizes da tríade nova:**
- **Strategy** = manchete é a **lista de cards** (1 chip de status cada); parâmetros e otimizador
  on-demand em drawer; otimizador mostra **1 recomendação + selo de robustez**, não a grade.
- **RunTests** = manchete é a **curva de equity**; 4-5 métricas como tira de chips; trades e
  walk-forward em accordion fechado; **chip `bruto`+tooltip** carrega a honestidade do MVP (não
  parágrafo).
- **Experts** = manchete é a **lista de robôs** com status grande e **selo DEMO sempre visível**;
  logs on-click. É a única que toca execução — sobriedade máxima, cor forte só em DEMO/parar.
- **Regra de ouro:** as três são um **fluxo** (defino→testo→opero), cada uma com **uma** manchete.
  3+ tabelas na vertical em qualquer delas = repetimos o erro.

**Ferramenta de consistência:** 4 componentes-padrão (`PageHeader`, `PageContainer`, `StatStrip`,
`DetailDisclosure`) + 7 regras de densidade. O tema (`theme.ts`) já é bom; falta padrão de
**composição**, não de cor.

> Design é editar. O front atual mostra tudo o que sabe; o produto precisa mostrar o que **importa**
> e esconder o resto a um clique de distância. — Andy

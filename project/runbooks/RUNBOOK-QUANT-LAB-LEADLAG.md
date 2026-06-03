---
template: RUNBOOK
produto: CaM — The Carlos Alternative Money
slice: Quant Lab — Lead-Lag (Research Lane v0.5)
relacionados: SPEC-v0.5-LEADLAG-RESEARCH, ADR-015, RUNBOOK-MT5-INSPETOR
date: 2026-06-03
status: Vigente
---

# RUNBOOK — Quant Lab: como usar e interpretar o Lead-Lag

> **O que é isto.** O Quant Lab é um **laboratório de pesquisa read-only**. Ele NÃO
> opera, NÃO envia ordem, NÃO sugere entrada. Ele responde **uma** pergunta:
> *"o movimento de um ativo-fonte tende a anteceder o movimento de um ativo-alvo —
> e, se sim, com qual defasagem e isso é real ou ruído?"*
>
> **A regra de ouro:** o Quant Lab é uma **máquina de matar hipóteses**, não de
> confirmar. Quando ele diz "nada sobreviveu", isso é um **resultado bom** — ele te
> impediu de operar ruído. Edge de verdade é raro; ceticismo é a função.

---

## 1. O fluxo em 3 passos

```
1) INGERIR  → puxa candles + ticks do MT5 para o banco de pesquisa (research_*)
2) ANALISAR → mede a correlação defasada fonte→alvo em várias defasagens (δ)
3) LER      → heatmap + perfil + tabela com veredito estatístico
```

### Passo 1 — Ingerir (aba "Ingestão de dados")
1. Abra **Quant Lab** (`/lab`) com o MT5 aberto e o EA `cam_bridge` atachado.
2. O campo de universo já vem com os 8 papéis seed (WIN$, WDO$, VALE3, ITUB4,
   PETR4, AXIA3, BBDC4, B3SA3). Edite à vontade.
3. Clique **"Ingerir do MT5"**. Aguarde — a 1ª vez de cada símbolo baixa o
   histórico (pode demorar).
4. Confira o **Data Health**: quantas barras por símbolo/TF e a **liquidez de
   tick** (quantos ticks têm o lado agressor). Se um ativo tem poucas barras,
   a análise dele vai dar "dado insuficiente" — é esperado.

> **Por que ingerir de novo?** Cada ingestão acrescenta dados. Quanto mais
> histórico acumulado, mais barras → análises mais confiáveis. Rode periodicamente.

### Passo 2 — Analisar (aba "Lead-Lag — correlação defasada")
- **Alvo:** o ativo que você quer prever (ex.: PETR4).
- **Timeframe:** a escala. M5 = reação intradiária; H1/D1 = swing.
- **δ máx (barras):** até quantas barras de defasagem testar. 50 = "os últimos 50
  timeframes anteriores". A fonte em `t−δ` é comparada ao alvo em `t`.
- Clique **Analisar**. O sistema testa **cada fonte → alvo** em **cada δ de 1 a 50**.

### Passo 3 — Ler os resultados (abaixo)

---

## 2. Como ler o HEATMAP (a visão de relance)

Linhas = fontes. Colunas = defasagem δ (1, 2, 3, …). Cor de cada quadrinho:

| Cor | Significado |
|---|---|
| 🟢 **Verde** | A fonte sobe e o alvo **sobe** δ barras depois (lead-lag positivo) |
| 🔴 **Vermelho** | A fonte sobe e o alvo **cai** δ barras depois (relação inversa) |
| ⬜ **Cinza** | Dado insuficiente naquela célula (não confunda com "sem relação") |
| **Borda branca** | **Sobrevivente estatística** — passou o teste de falsa descoberta |

**O que procurar:** uma **faixa verde (ou vermelha) forte e consistente** numa
fonte, concentrada em alguns δ. Isso sugere que aquela fonte realmente antecede o
alvo. Cores fracas e espalhadas = ruído. **Borda branca é o que importa** — sem
ela, é só exploração.

> Passe o mouse sobre qualquer quadrinho para ver o valor exato (C, n, veredito).

---

## 3. Como ler o PERFIL C(δ) (clique numa fonte)

Clique numa fonte na tabela → aparece o gráfico de barras **correlação × δ**.

- **Eixo X:** defasagem δ (em barras). **Eixo Y:** correlação (+ para cima, − para baixo).
- **A barra mais alta** (destacada em branco) é a defasagem onde a fonte mais
  "lidera" o alvo. Ex.: pico em δ=3 → a fonte tende a anteceder o alvo em ~3 barras.
- **Verde forte** = sobrevivente; verde/vermelho fraco = medido mas não sobreviveu.

**Interpretação prática:** se VALE3→PETR4 tem pico em δ=2 no M5, significa que,
historicamente, um movimento da VALE3 foi seguido por movimento da PETR4 ~10 min
depois (2 barras de 5 min). **Isso é uma HIPÓTESE de pesquisa, não um sinal de
trade.** Falta provar que sobrevive a custo, latência e tempo (próximas fases).

---

## 4. Como ler a TABELA e os VEREDITOS

| Coluna | O que é |
|---|---|
| **melhor \|C\|** | a maior correlação (em módulo) daquela fonte, entre todos os δ |
| **δ (barras)** | a defasagem onde ocorreu essa melhor correlação |
| **n** | tamanho da amostra (nº de pontos usados). Pouco n = pouca confiança |
| **DSR** | Deflated Sharpe Ratio ∈ [0,1] — ver abaixo |
| **veredito** | o resultado do teste estatístico |

### Os 3 veredictos (e o que fazer com cada um)

| Veredito | Cor | Significa | O que fazer |
|---|---|---|---|
| **sobrevivente** | 🟢 verde | A correlação passou o controle de falsa descoberta (FDR) entre TODAS as células testadas | Hipótese **candidata**. Anote. Ainda NÃO é edge — falta event study líquido + walk-forward |
| **morta (FDR)** | 🔴 vermelho | Mediu uma correlação, mas ela **não resistiu** ao número de tentativas. Provável ruído | **Descarte.** Foi pescaria — você testou 400 células, achar uma "boa" por acaso é esperado |
| **dado insuficiente** | ⬜ cinza | Amostra abaixo do piso. Não dá para afirmar nada | Ingira mais histórico ou use TF menor (mais barras) |

### O DSR (Deflated Sharpe Ratio) — o número mais importante
- É a **probabilidade de que o resultado seja real**, depois de descontar o fato de
  você ter testado **muitas** combinações.
- **DSR alto (> 0,95)** = forte evidência de que não é sorte. **DSR baixo** = provável
  artefato de tanto procurar.
- **Por que "deflated"?** Se você testa 400 células, algumas vão parecer ótimas só
  por acaso. O DSR penaliza isso: quanto mais tentativas, mais alta a barra.

### O contador de tentativas (no topo e no Run Registry)
- "tentativas: 400" = você testou 8 fontes × 50 δ. Cada teste é uma chance de achar
  ruído que parece sinal.
- O **contador global** (Run Registry) soma TODAS as suas análises. Ele lembra: quanto
  mais você procura, mais cético o sistema fica. **Isso é proposital** — é o que
  separa pesquisa honesta de pescaria.

---

## 5. O que você PROVAVELMENTE vai ver no começo (e por que é normal)

Com pouco histórico ingerido e o universo seed:
- **Muitos "dado insuficiente"**, especialmente em TFs grandes (H1/D1 têm poucas barras).
- **Poucos ou zero "sobreviventes".** Com 400 tentativas, o FDR é severo.

**Isso NÃO é o sistema falhando — é o sistema funcionando.** Ele está se recusando a
chamar ruído de sinal. Para sobreviventes reais você precisa de:
1. **Mais corpus** (ingira ao longo de vários dias/semanas);
2. **TFs menores** (M1/M5 dão muito mais barras → mais poder estatístico);
3. **Paciência** — edge cross-asset real é raro. Achar 1 que sobrevive vale mais que
   100 que não sobrevivem.

---

## 6. O Run Registry (histórico)

Toda análise fica registrada (imutável — evidência nunca é apagada). Mostra:
- alvo, nº de fontes, δ máx, tentativas, veredito da run (com sobrevivente / morta / dado insuf.);
- o **contador global de tentativas** que alimenta o DSR.

Status da run:
- **com sobrevivente** = pelo menos 1 célula passou o FDR;
- **morta (FDR)** = mediu tudo, nada passou (resultado honesto e útil);
- **dado insuficiente** = não havia amostra para concluir.

---

## 7. Limites honestos (o que isto AINDA não faz)

Esta é a fatia de **pesquisa de correlação + validação estatística**. Ainda NÃO é
um sistema de trade. Faltam, por design (fases futuras):
- **Event study líquido** com custo/slippage/IR — correlação ≠ lucro;
- **Latência real** — um edge que vive menos que o tempo de execução é inútil;
- **Hayashi-Yoshida no fluxo** (mata-Epps em tick) — o núcleo existe, falta acoplar;
- **Swing/rolagem, Fibonacci, síntese regime×gatilho** — núcleos prontos, não plugados ao run;
- **Promoção a paper/live** — jamais automática; passa por gate do Founder + Risk Engine.

**Nunca** trate um "sobrevivente" como autorização de operar. É o começo de uma
investigação, não o fim.

---

## 8. Glossário rápido

| Termo | Tradução |
|---|---|
| **Lead-lag** | um ativo se move antes do outro |
| **δ (delta)** | a defasagem, em nº de barras |
| **C(δ)** | correlação na defasagem δ |
| **OFI** | desequilíbrio de fluxo (compradores − vendedores) |
| **FDR** | controle de falsas descobertas entre muitos testes |
| **DSR** | Sharpe "deflacionado" pelo nº de tentativas — prob. de ser real |
| **Epps** | efeito que cria lead-lag fantasma ao reamostrar tick (HY mata isso) |
| **sobrevivente** | célula que passou o controle estatístico — candidata, não edge |

---

## Referências
- SPEC: `project/cam-cockpit/specs/SPEC-v0.5-LEADLAG-RESEARCH.md`
- Tese: `project/cam-cockpit/research/leadlag/CaM-RESEARCH-CUBO-LEADLAG.md`
- ADR-015 (Research Lane isolada): `project/cam-cockpit/adrs/`
- Setup MT5: `project/runbooks/RUNBOOK-MT5-INSPETOR.md`

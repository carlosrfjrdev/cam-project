---
template: EDGE-THESIS
phase: P&D / Research Lane
status: Draft (hipótese — não promovido)
produto: CaM
codinome: research-leadlag ("O Cubo")
vive_em: project/cam-cockpit/research/EDGE-THESIS-LEADLAG-CUBE.md
data: 2026-06-01
lead: Mentor de Estratégia (criação) · Founder (aprovação)
---

# EDGE-THESIS — Cubo de Lead-Lag Cross-Asset

> Tese de **research**, pré-estratégia. Não é estratégia promovida, não toca o
> cockpit live, não consome capital real. Roda na research lane (DuckDB/Parquet),
> isolada das tabelas do live por design (Art. de separação research↔live).

---

## 1. Tese central (uma frase)

O fluxo de agressão (delta comprador/vendedor) se propaga de um **conjunto de ativos-fonte** para um **ativo-alvo** com uma defasagem τ; quando essa propagação tem expectância líquida positiva e persiste por um tempo maior que a latência de execução, ela é explorável intraday.

---

## 2. O Cubo (modelo conceitual)

Estrutura de descoberta = tensor de três eixos:

```
         fonte (F)  ×  alvo (D)  ×  lag (τ)   →   métrica de edge
```

- **Fonte (F):** um ativo OU um *conjunto* {A, B, C} de ativos. Conjunto só agrega
  se trouxer informação **ortogonal** (preditores correlacionados entre si = 1 fator,
  não N). Diversidade ou jusante mecânica é o que dá lift.
- **Alvo (D):** qualquer ativo do universo. Livre. (não é fixo em WIN)
- **Lag (τ):** grade de defasagens candidatas — ex.: 0.5s, 1s, 2s, 3s, 5s, 10s, 30s.
- **Métrica de edge por célula:** começa em correlação defasada do fluxo assinado;
  evolui para expectância líquida do alvo após evento na fonte (§7).

O cubo é **motor de descoberta**: varre, ranqueia as células, e só as melhores
viram hipótese operável. A *natureza dos preditores* informa o instrumento (§8):
preditor sistêmico (pesos do índice) → futuro de índice; preditor idiossincrático → o alvo específico.

---

## 3. Hipóteses explícitas (pré-registradas)

Registrar ANTES de testar protege contra data snooping (§10).

- **H1 (existência):** Existe ≥1 célula (F→D, τ) com correlação defasada do fluxo
  significativa e **estável fora da amostra**.
- **H2 (expectância):** Após um evento de agressão em F, o retorno de D no horizonte τ
  tem **expectância líquida > 0** (custos + IR incluídos), não apenas % de acerto > 50%.
- **H3 (não é causa comum):** A relação F→D **sobrevive ao controle** de drivers comuns
  (WDO, futuro de índice US/ES, macro). Senão, F e D só estavam no mesmo barco.
- **H4 (executável):** O edge **persiste por tempo > latência** de execução (MT5/Profit).
  Se o edge vive 300ms, é terreno de co-located — fora do escopo (CaM não é HFT).
- **H5 (refutação a derrubar):** A relação é **artefato de reamostragem** (Epps effect),
  não fluxo real. A derrubar com estimador assíncrono (Hayashi-Yoshida).

> Critério de honestidade: a tese só avança se H1–H4 passam **e** H5 é derrubada.

---

## 4. Dados necessários

| Dado | Detalhe |
|---|---|
| Tick por símbolo | Times & Trades com **flag de agressor** (comprador/vendedor) da B3 |
| Timestamp | Precisão de ms, **clock sincronizado** entre símbolos (crítico) |
| Universo N | Blue chips do Ibov + WIN + WDO + (ES como controle) — N a definir |
| Janela histórica | Mínimo p/ ter dias suficientes em regimes distintos (TBD pelo Founder) |
| Book (opcional v2) | Imbalance bid/ask para enriquecer o sinal de fluxo |
| Armazenamento | Parquet particionado por dia/símbolo; query via DuckDB. **Nunca** grava em tabela do live |

Aberto (Founder): tamanho de N, profundidade da janela histórica, lista inicial de alvos candidatos.

---

## 5. Universo e definições

- **Sinal de fluxo:** delta de agressão = (volume agressor comprador − vendedor) por janela curta.
- **Evento:** delta de agressão da fonte estoura limiar (ex.: > k desvios na janela rolante).
- **Predictor set:** combinação de fontes; pesos estimados (regressão/ensemble), não ad hoc.
- **Forward return de D:** retorno de D em +τ medido a partir do instante do evento.

---

## 6. Pipeline de medição (do barato ao caro)

**Fase A — Varredura do cubo (correlação defasada).**
Cross-correlation do fluxo assinado de cada F contra cada D em toda a grade de τ.
Saída: ranking de células candidatas. Rápido, interpretável, primeira foto de quem lidera quem.

**Fase B — Mata-artefato (Hayashi-Yoshida).**
Reestima a correlação das células top com estimador para tick **assíncrono**.
Se a célula só existia por reamostragem (Epps), morre aqui. (Derruba ou confirma H5.)

**Fase C — Causalidade direcional.**
Granger no fluxo (F ajuda a prever D além do próprio passado de D?).
Opcional: transfer entropy para capturar não-linearidade.

**Fase D — Event study (o coração).**
Para cada célula sobrevivente: distribuição do forward return de D em +1s/+3s/+5s/+10s/+30s
após evento em F. Produz:
- **curva de decaimento do edge** (por quanto tempo dura) → testa H4;
- **expectância líquida** por horizonte = p·ganho − (1−p)·perda − custos − IR → testa H2.

**Fase E — Controles de causa comum.**
Reroda Fase D condicionando/neutralizando WDO + ES + macro. Testa H3.

**Fase F — Validação honesta.**
Out-of-sample + walk-forward. Correção para múltiplos testes (você varreu muitas células).
Mede **capacidade** (quanto capital o sinal aguenta antes do próprio impacto matar o edge).

---

## 7. Camada de execução (sinal ≠ instrumento)

O cubo decide **o quê** e **quando**. O instrumento é decisão separada, por fricção:

| Critério | À vista (ação D) | Futuro (WIN/WDO) | Opção (fase 2) |
|---|---|---|---|
| Movimento idiossincrático de D | ✅ | — | ✅ (single name) |
| Movimento sistêmico (mercado) | — | ✅ | — |
| Alavancagem sobre banca pequena | fraca | ✅ forte | ✅ (com theta) |
| Custo por trade (surf rápido) | maior | ✅ mínimo | spread alto na B3 |
| Short simétrico/grátis | precisa aluguel | ✅ | ✅ (via put) |
| Sinal de volatilidade (não direção) | — | — | ✅ |

Regra prática: **preditores sistêmicos → índice futuro; preditores idiossincráticos → o alvo à vista.**
Opções entram só para single-name sem aluguel ou para propagação de volatilidade — não no v1.

---

## 8. Sizing (o "jogar a banca", traduzido pra quant)

Probabilidade boa **não basta** — o que dimensiona a posição é a **expectância e a variância** medidas,
não a convicção. Tamanho da entrada cresce com o edge medido (lógica fração-de-Kelly), não é all-in fixo.
Concentrar 100% da banca intraday numa única propagação é variância máxima; o sizing sai do número, não do feeling.
(Isto é research; a operação real depois passa pelo Risk Engine.)

---

## 9. Critério de "promove ou mata" (go/no-go)

**Promove para fase de paper** se TODAS:
1. Célula(s) com edge **estável out-of-sample** após correção de múltiplos testes.
2. Decaimento do edge (Fase D) **> latência real** de execução (H4).
3. Expectância líquida positiva após custos + IR no horizonte operável (H2).
4. Relação sobrevive ao controle de causa comum (H3) e ao Hayashi-Yoshida (H5 derrubada).
5. Capacidade compatível com o capital pretendido.

**Mata** se: edge desaparece OOS, decaimento < latência, expectância ≤ 0 líquida, ou
relação some ao controlar drivers comuns. Matar cedo é vitória — economiza capital e tempo.

> Alinha com R-11: gatilho é **expectância líquida positiva**, não % de acerto cru.

---

## 10. Riscos e armadilhas

- **Assincronicidade / Epps:** reamostrar tick fabrica lead-lag fantasma → Hayashi-Yoshida.
- **Data snooping:** varrer o cubo inteiro acha "padrão" no ruído → pré-registro + OOS + correção.
- **Causa comum:** F e D reagindo ao mesmo gatilho → controles (WDO/ES).
- **Regime:** a propagação pode existir só na abertura/fechamento/alta vol e inverter no resto → condicionar por regime.
- **Microestrutura do alvo:** se D for ilíquido, slippage no horizonte de segundos come o edge → exigir liquidez mínima.
- **Capacidade:** edge pequeno satura rápido; medir antes de sonhar com tamanho.

---

## 11. Roadmap de research

1. Definir universo N, janela e alvos candidatos (Founder).
2. Pipeline de ingestão tick → Parquet com flag de agressor + clock check.
3. Fase A (varredura) → ranking de células.
4. Fases B–C (mata-artefato + causalidade) nas top.
5. Fase D (event study) → curva de decaimento + expectância.
6. Fases E–F (controles + validação honesta).
7. Decisão go/no-go (§9). Se go → EDGE-THESIS de estratégia + camada de execução.

---

## 12. Fora de escopo agora

- Execução real (research only; live depende de fase + Risk Engine).
- Opções (parkeado p/ fase 2: single-name e volatilidade).
- Multi-alvo simultâneo / portfólio de sinais (depois de 1 célula provada).
- HFT / sub-segundo (CaM não é HFT por design — foco em τ de 1–30s).

---

## 13. Histórico de versões

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 0.1 | 2026-06-01 | Draft inicial da tese do Cubo | (pendente Founder) |
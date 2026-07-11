# Análise de operações manuais — WINM26 (08/06 a 17/06/2026)

> Fonte: `Dados Operações.csv` (conta 226437). 95 trades, todos WINM26.
> Lente financeira: Daniel (RCA de decisão) + Jim (edge) + Nassim (risco).
> **Não é coach emocional — é diagnóstico frio de processo.**

## 1. Números-chave (resultado BRUTO, antes de custos)

| Métrica | Valor |
|---|---|
| Trades | 95 (41 W / 52 L / 2 zero) |
| Resultado bruto | **−R$ 17,00** (≈ flat; negativo após emolumentos/corretagem) |
| Win rate | 44,1% |
| Payoff (média gain ÷ média loss) | 1,25 (R$ 35,41 / R$ 28,25) |
| Profit factor | **0,99** (sem edge — é cara-ou-coroa com custo) |
| Maior gain / maior loss | +R$ 98 / −R$ 68 |

## 2. Onde o dinheiro vazou (os 3 furos decisivos)

### 🔴 Furo nº1 — Dobrar a mão DENTRO do drawdown
| Tamanho | Trades | Resultado | Win rate |
|---|---|---|---|
| **1 contrato** | 57 | **+R$ 429** | 49,1% |
| **2 contratos** | 38 | **−R$ 446** | 36,1% |

A partir de **16/06** você passou de 1 → 2 contratos — exatamente quando começou a
perder. Com 1 contrato você era **lucrativo**. Dobrou a mão para "recuperar" e
transformou +429 em −17. Isto é martingale emocional: aumentar exposição no pior
momento.

### 🔴 Furo nº2 — Sem trava de perdas seguidas (tilt)
| Dia | Trades | Resultado | Maior sequência de loss |
|---|---|---|---|
| 16/06 | 19 | **−R$ 297** | **9 losses seguidas** |
| 17/06 | 28 | −R$ 120 | 4 |
| 12/06 | 9 | +R$ 133 | 4 |
| 08/06 | 8 | −R$ 166 | 3 |

9 perdas em sequência em 16/06 e ninguém puxou o freio. Os dois piores dias (16 e 17)
são também os de **maior número de trades** — clássico revenge trading / overtrade.

### 🔴 Furo nº3 — Trades-relâmpago e contra o fluxo
- **17 trades com duração ≤ 30s → −R$ 172.** Entrada sem tese, saída no susto.
- **Lado vendido: −R$ 149 (WR 40%)** num período em que o WIN SUBIU (169.4k → 171k).
  Você brigou contra a tendência do dia vendendo em mercado de alta.

## 3. Onde está o seu edge (use a favor)

| Janela | Resultado |
|---|---|
| **11h** | **+R$ 158** (melhor janela — WR 56%) |
| 09h–10h | −R$ 171 (pior — e onde você MAIS opera: 54 trades) |
| 12h | −R$ 114 |
| Tarde (14h–17h) | +R$ 110 |

Você concentra volume justamente no horário que te machuca (abertura 9–10h) e
sub-explora o horário em que ganha (11h).

## 4. Correções (acionáveis no próprio CAM)

1. **Voltar a 1 contrato** até ter ≥ 5 dias consistentes. **Nunca** aumentar mão em
   drawdown — escalonamento só após sequência de dias verdes (Scaling do CAM).
2. **Stop de perdas seguidas + stop diário** no Kill Switch / Risk Engine do CAM
   (ex.: 3 losses seguidas OU −R$ 150 no dia = encerra o dia, sem exceção).
3. **Teto de trades/dia** (ex.: 6–8). Qualidade > quantidade — 28 trades num dia é o
   sintoma, não a estratégia.
4. **Proibir o trade ≤ 30s sem gatilho.** Checklist pré-clique: tese, nível, invalidação.
5. **Operar a favor do fluxo do dia.** Reduzir venda em dia de alta clara.
6. **Concentrar no horário de edge (11h+)** e validar a hipótese com os ticks extraídos
   (item 5).

## 5. Próximo passo técnico — extração de ticks (em andamento)

- CAM no ar (API :8000, DB :5434). Extrator pronto:
  `apps/cam-cockpit/backend/scripts/extract_ticks.py`.
- **Pendente:** atachar o EA `cam_bridge` a um gráfico WINM26 no MT5
  (AutoTrading ON). Com a bridge ONLINE, rodar:
  ```
  uv run python scripts/extract_ticks.py --symbol WINM26 --from 2026-06-08 --persist
  ```
  → gera CSV por dia em `project/tcam/analysis/ticks/` e grava em `cam_market_ticks`.
- Com os ticks: Wyck valida o fluxo/agressor da janela 11h e Jim testa se há edge
  estatístico real antes de você voltar a operar size.

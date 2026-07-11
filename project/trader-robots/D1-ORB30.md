---
template: FICHA-ROBO
robo: D1 — ORB-30
dominio: trader-robots
data: 2026-06-05
---

# Ficha do Robô — D1 "ORB-30"

Estratégia de **breakout do range de abertura a favor da tendência**, com stop
móvel. Robô de **regime de tendência** (no lateral fica de fora ou é pareado com
a D2/VWAP — ver [híbrido](#7-variantes)).

> **Política:** ver [POLITICA-ROBOS.md](./POLITICA-ROBOS.md) (autonomia, validação
> tripla, ciclo de vida, ±20%).

---

## 1. Tese

Em **dias de tendência**, o preço estica além da máxima/mínima dos primeiros
minutos do pregão e segue na direção do rompimento. O robô entra na quebra **a
favor da tendência recente** e usa **stop móvel** para deixar o vencedor correr.
Em **lateral** (chop), o rompimento é falso e a estratégia perde — por isso o
**filtro de regime** (a D1 só opera quando o mercado está direcional).

- **Perfil:** baixa taxa de acerto, payoff alto (poucos trades grandes carregam).
- **Win rate** não é métrica de sucesso — é **expectância** + **drawdown**
  (ver conselho em `project/tcam/...`). Acerto alto seria a estratégia errada.

---

## 2. Lógica (passo a passo)

1. **Range de abertura (OR):** nos primeiros `OrMinutos` (ex.: 30) do pregão,
   mede a máxima (`OR_high`) e a mínima (`OR_low`) da sessão.
2. **Filtro de tendência:** só opera **a favor** da tendência das últimas
   `FiltroTendBarras` barras: compra se `Close > Close[N atrás]`; vende se menor.
3. **Filtro de regime (opcional / no híbrido):** Efficiency Ratio diário ≥ limiar
   = tendência (opera); abaixo = lateral (fica de fora).
4. **Entrada (a mercado):** quando o `Close` rompe `OR_high` (compra) ou `OR_low`
   (venda), na primeira barra após o rompimento. **1 trade por direção por dia.**
5. **Saída:**
   - **Stop inicial:** `StopInicialPts` da entrada.
   - **Stop móvel (trailing):** segue o pico a `StopMovelPts`; só anda a favor,
     nunca recua (trava lucro).
   - **Alvo fixo (opcional):** `AlvoFixoPts` (0 = sem alvo, deixa correr).
   - **Flat na sessão:** zera no fim do pregão (sem overnight).

---

## 3. Parâmetros (nomes do EA MQL5 `cam_d1_orb30_exec`)

| Parâmetro | Default | Descrição |
|---|---|---|
| `InpContratos` | 1 | Quantidade de contratos por ordem (WIN/WDO: 1 = 1 contrato) |
| `InpOR_Minutos` | 30 | Janela do range de abertura (min) |
| `InpD1_StopInicial_Pts` / `InpStopInicial_Pts` | 300 | Stop inicial em pontos |
| `InpD1_AlvoFixo_Pts` / `InpAlvoFixo_Pts` | 0 | Alvo fixo em pontos (0 = sem alvo) |
| `InpD1_StopMovel_Pts` / `InpStopMovel_Pts` | 1000 | Stop móvel (trailing) em pontos (0 = off) |
| `InpFiltroTendencia_Barras` / `InpD1_FiltroTend_Barras` | 2500 | Filtro de tendência (N barras ≈ 5 dias) |
| `InpRangeMinimoOR_Pts` | 0 | Range mínimo do OR para operar (0 = off) |
| Sessão | 09:00 / 17:00 / 17:55 | Abertura / corte de entrada / fechamento |

> **Config CAMPEÃ (WINM26 mar-jun, otimizada pelo Founder no MT5 por volume
> financeiro, confirmada no CAM):** stop **300** / trail **1000** / tendência
> **2500**. Resultado: acerto ~38%, **payoff 3.6:1**, **+R$3.007** com maxDD só
> **−R$463** (cabe em 10% com ~R$4.600/contrato). Mesmos valores nos três ambientes.
>
> ⚠️ **Acerto de 38% é a assinatura do arquétipo, não defeito.** A config de "89% de
> acerto" (stop1000/tp200) lucra MENOS (+R$956) e inverte o payoff p/ 0.2:1, com cauda
> de −1000 latente que não disparou na amostra. Mais dias contra (37) que a favor (23)
> é esperado: perde miúdo (−R$57 méd.), ganha grande (+R$204 méd.).

---

## 4. Os três ambientes (validação tripla)

| Ambiente | Arquivo | Papel |
|---|---|---|
| **CAM (Python)** | `cam/features/strategy_lab/strategies/d1_orb30.py` + `backtest_engine.py` | Referência matemática (backtest bruto + paridade) |
| **MetaTrader (MQL5)** | `apps/trader-robots/mql5/experts/cam_d1_orb30_exec.mq5` | Executor tick (DEMO) |
| — gravador de paridade | `cam_d1_orb30.mq5` | Exporta ledger p/ casar com o CAM |
| — executor + regime | `cam_d1_orb30_sinais.mq5` | Executor com filtro de regime embutido |
| **Profit (NTSL)** | `apps/trader-robots/ntsl/cam_d1_orb30/cam_d1_orb30_exec.src` | Executor B3 (Profit Pro) |

---

## 5. Status atual (por ambiente)

| Ambiente | Status | Observação |
|---|---|---|
| CAM (Python) | **BACKTEST** | Config campeã 300/1000/2500 → 71 trades, +R$3.007, maxDD −R$463 |
| MetaTrader (MQL5) | **BACKTEST** | Otimizado pelo Founder → 66 trades, +R$3.124 (volume financeiro) |
| Profit (NTSL) | **BACKTEST** | Convergiu: 56 trades, ~+R$2.000 (mesma amostra mar-jun) |

**Status do robô:** **BACKTEST → convergência CONFIRMADA** (Profit ≈ MT5 ≈ CAM,
dentro de ±10%). A validação tripla da D1 está **fechada na config anterior**
(700/800/5000); falta reconfirmar a convergência na config campeã (300/1000/2500)
antes de **ELEGIVEL**.

---

## 6. Pendências de validação

- [x] Convergência MQL5 ↔ NTSL ↔ CAM (mar-jun, config 700/800/5000): **±10% OK**.
- [ ] Reconfirmar convergência tripla na config campeã (300/1000/2500).
- [ ] Paridade CAM ↔ gravador MQL5 (PASS no painel Paridade).
- [ ] Backtest líquido (custo + IR) antes de ELEGIVEL.
- [ ] **Out-of-sample real:** dez-fev é warmup do filtro (2500 barras), não amostra
      independente. Ingerir mais histórico (WINJ/WINV/2024) p/ stress da cauda.

---

## 6.1 Recuperação após loss — regime switch, NÃO martingale

Análise empírica (WINM26 mar-jun, D1 campeã × D2 VWAP fade):

| Achado | Valor |
|---|---|
| Nos 37 dias que a D1 perde, a D2 fez | **+R$1.952** (positiva em 21) |
| Correlação diária D1 × D2 | **−0,35** (se complementam) |
| D2 sozinha (params atuais, não afinada) | +R$64 |
| Carteira D1+D2 rodando **sempre** | +R$3.071 / maxDD −R$890 (não ajuda) |

**Leitura:** a recuperação certa é **trocar para a D2 no regime lateral** (onde ela
tem edge comprovado), não rodar as duas sempre (empata e piora o DD) e **jamais**
aumentar volume após perda (martingale = ruína). Mecanismo: (a) **limite de perda
diária** (defensivo); (b) **regime switch** D1↔D2 via Efficiency Ratio
(`cam_hibrido_orb30_vwap`). **Pré-requisito:** afinar + validar a D2 antes de
confiar nela como perna de recuperação.

---

## 7. Variantes

- **`cam_d1_orb30_sinais`** — D1 + filtro de regime (Efficiency Ratio): só opera
  em tendência; fica de fora no lateral.
- **`cam_hibrido_orb30_vwap`** — D1 (tendência) **+** D2 VWAP fade (lateral) no
  mesmo robô, trocando por regime. Cobre os dois mundos. **É a base da recuperação
  por regime** (ver §6.1): a D2 lucra nos dias que a D1 sangra (anti-correlação −0,35).

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
| `InpD1_StopInicial_Pts` / `InpStopInicial_Pts` | 700 | Stop inicial em pontos |
| `InpD1_AlvoFixo_Pts` / `InpAlvoFixo_Pts` | 0 | Alvo fixo em pontos (0 = sem alvo) |
| `InpD1_StopMovel_Pts` / `InpStopMovel_Pts` | 800 | Stop móvel (trailing) em pontos (0 = off) |
| `InpFiltroTendencia_Barras` / `InpD1_FiltroTend_Barras` | 4000–5000 | Filtro de tendência (N barras) |
| `InpRangeMinimoOR_Pts` | 0 | Range mínimo do OR para operar (0 = off) |
| Sessão | 09:00 / 17:00 / 17:55 | Abertura / corte de entrada / fechamento |

> **Config validada pelo Founder (WINM26, MT5 tick):** stop 700 / trail 800 /
> tendência 4000–5000, ~9% de drawdown. Mesmos valores nos três ambientes (paridade).

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
| CAM (Python) | **BACKTEST** | Backtest + walk-forward OK; edge regime-dependente comprovado |
| MetaTrader (MQL5) | **BACKTEST** | Founder validando no Strategy Tester (config 700/800/5000) |
| Profit (NTSL) | **INDEV** | Replicação criada (2026-06-05); ajuste de sintaxe no editor do Profit |

**Status do robô:** **BACKTEST** (em validação tripla). Próximo gate: convergência
dos três → **ELEGIVEL**.

---

## 6. Pendências de validação

- [ ] Paridade CAM ↔ gravador MQL5 (PASS no painel Paridade).
- [ ] Convergência MQL5 ↔ NTSL (mesmo período/parâmetros).
- [ ] Resolver mismatch tick/barra do WINM26 no MT5 (re-sincronizar histórico).
- [ ] Backtest líquido (custo + IR) antes de ELEGIVEL.

---

## 7. Variantes

- **`cam_d1_orb30_sinais`** — D1 + filtro de regime (Efficiency Ratio): só opera
  em tendência; fica de fora no lateral.
- **`cam_hibrido_orb30_vwap`** — D1 (tendência) **+** D2 VWAP fade (lateral) no
  mesmo robô, trocando por regime. Cobre os dois mundos.

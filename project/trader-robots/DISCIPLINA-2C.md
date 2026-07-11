---
template: FICHA-ROBO
robo: Disciplina 2C
dominio: trader-robots
data: 2026-06-30
status: INDEV
---

# Ficha do Robô — "Disciplina 2C"

**Gestor de SAÍDA disciplinada** para entradas **manuais**, em 2 contratos. Não
decide entrada — a edge do trader está na leitura de entrada; o robô **tira o
emocional da saída**, que é onde o capital vaza.

> **Política:** ver [POLITICA-ROBOS.md](./POLITICA-ROBOS.md) (autonomia, validação
> tripla, ciclo de vida, ±20%). **DEMO-only** até status TESTE.

---

## 1. Tese (por que existe)

Diagnóstico da massa real (`data/trade-reports/trades-30dias.csv`, 355 ops WIN, 2
contratos): acerto ~50%, mas **payoff realizado 0,83–0,90:1** — o trader arrisca
~100 pts para tirar ~50 (inverso do 1:3 que acredita operar). O edge existe (38
trades ≥150 pts, vários de +300/+500 em minutos), mas ele **corta o vencedor cedo**
(52% dos ganhos ≤50 pts) e **doa em overtrading** (09h e 12h sangram; dias de 50–84
ops perdem). O problema **não é a estratégia, é a assimetria de saída** — emocional.

**Solução:** mecanizar a saída em 2 pernas + guard-rails, removendo a decisão da
mão no calor do momento.

---

## 2. Lógica (passo a passo)

Sobre a posição aberta (manual) no símbolo:

1. **Stop inicial único** (`StopPts`) protege as 2 pernas.
2. **Perna 1** (`Leg1Contratos`, ex.: 1): sai no **alvo curto** (`Alvo1Pts`) —
   mata a ansiedade, trava o scalp que o trader gosta.
3. Ao realizar a P1: **stop da Perna 2 vai a breakeven** (`entrada ± BreakevenOffset`).
4. **Perna 2** (resto): **corre com trailing** (`TrailPts`, nunca abaixo do
   breakeven) até o **alvo longo** (`Alvo2Pts`) — captura os 300/500 que ele
   sabe pegar.

**Guard-rails (disciplina):**
- **Janela de não-operar** (default 09:00–09:30 — leilão/ruído que mais sangra):
  posição aberta nela é **encerrada**.
- **Máx ops/dia** (default 10): acima, novas posições são encerradas.
- **Stop diário em R$** (default 300): atingido, encerra e bloqueia o resto do dia
  *(MQL5 implementado via histórico de deals; NTSL = TODO, ver §5)*.
- **Flat no fim do pregão** (default 17:55): sem overnight.

---

## 3. Parâmetros (calibrados pelo MOTOR, não chutados)

> ⚠️ **Os defaults são PROVISÓRIOS.** Stop e alvos saem da análise **MAE/MFE ×
> regime** do motor estatístico do CAM (`features/trade_analyzer/motor.py` /
> `scripts/analyze_trades_motor.py`) — decisão do Founder: o stop não é chute,
> sai do dado. Rodar o motor com candles reais ANTES de fixar e antes de TESTE.
> A pergunta-chave que o motor responde: *em regime lateral, 80 pts é pullback
> certo?* → use o p75/p90 da MAE dos vencedores por regime como stop mínimo.

| Parâmetro (MQL5 / NTSL) | Default | Descrição |
|---|---|---|
| `InpStop_Pts` / `StopPts` | 80 | Stop inicial (pts) |
| `InpAlvo1_Pts` / `Alvo1Pts` | 100 | Alvo da Perna 1 (curto) |
| `InpAlvo2_Pts` / `Alvo2Pts` | 300 | Alvo da Perna 2 (runner) |
| `InpTrail_Pts` / `TrailPts` | 80 | Trailing da P2 após breakeven (0 = off) |
| `InpLeg1_Contratos` / `Leg1Contratos` | 1 | Contratos da Perna 1 (resto = P2) |
| `InpBreakeven_Offset_Pts` / `BreakevenOffsetPts` | 0 | Offset do breakeven |
| Janela não-operar | 09:00–09:30 | Bloqueio de entrada (sangria nos dados) |
| `InpMaxOpsDia` / `MaxOpsDia` | 10 | Máx operações/dia |
| `InpStopDiario_BRL` | 300 | Stop diário em R$ (MQL5) |
| Fechamento | 17:55 | Flat compulsório |

---

## 4. Os três ambientes (validação tripla)

| Ambiente | Arquivo | Papel |
|---|---|---|
| **MetaTrader (MQL5)** | `apps/trader-robots/mql5/experts/cam_disciplina_2c.mq5` | Gestor de saída para entradas manuais (magic 0), DEMO-only. Guard-rails completos (inclui stop diário via histórico de deals). |
| **Profit (NTSL)** | `apps/trader-robots/ntsl/cam_disciplina_2c/cam_disciplina_2c_exec.src` | Par de paridade (2 pernas + breakeven + trailing + janela/flat/ops-dia). |
| **CAM (Python)** | `features/trade_analyzer/motor.py` (`simulate_bracket` / `run_motor`) | Referência matemática: simula o bracket sobre os trades reais e **calibra** stop/alvo por regime. |

---

## 5. Status atual e pendências

**Status do robô:** **INDEV** (DEMO-only). Mecanismo construído nos 3 ambientes;
ainda não validado em execução.

| Ambiente | Status | Observação |
|---|---|---|
| CAM (Python) | **PRONTO (motor)** | `simulate_bracket` + `run_motor` testados (30 testes verdes). Falta rodar com candles reais (precisa bridge MT5/ProfitDLL). |
| MetaTrader (MQL5) | **INDEV** | Compilar no MetaEditor + rodar em DEMO; validar 2 pernas, breakeven, trailing e guard-rails. |
| Profit (NTSL) | **INDEV** | Validar no Profit: semântica de posição manual vs estratégia; preço de entrada (aproximado por Close — ver cabeçalho do `.src`). |

**Pendências de validação (antes de ELEGIVEL → TESTE):**
- [ ] **Calibrar stop/alvos pelo motor** (MAE/MFE × regime) com candles reais — gate do Founder.
- [ ] MQL5: compilar e testar em conta DEMO (2 pernas + breakeven + trailing + guard-rails).
- [ ] NTSL: confirmar no Profit se a estratégia enxerga posição manual; senão, usar
      brackets nativos do Profit com os mesmos parâmetros (o `.src` vira só paridade de backtest).
- [ ] NTSL: implementar **stop diário em R$** quando confirmada a função de P&L da conta (hoje TODO).
- [ ] Convergência tripla (±10% entre ambientes; ±20% real vs backtest).
- [ ] Backtest/forward **líquido** (custo + IR) antes de liberar real (gate do Founder).

---

## 6. Relação com o motor estatístico

Este robô é a **Camada 1** (executor) do plano "motor + robô". A **Camada 2** é o
motor estatístico (`trade_analyzer`) que produz os parâmetros: rode-o no relatório
de operações para obter a tabela **regime → (stop, alvo, expectância)** + **MAE dos
vencedores por regime**, e use esses números como defaults aqui. O motor desenha a
regra; o robô garante que o emocional não a quebre.

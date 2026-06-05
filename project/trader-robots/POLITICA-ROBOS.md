---
template: POLITICA
dominio: trader-robots
status: Ativa
data: 2026-06-05
autor: Founder (Carlos)
---

# Política de Robôs — Trader Robots (CaM)

Governança dos robôs de trading do CaM: como são construídos, validados,
aprovados e operados. Vale para todos os robôs em `/apps/trader-robots/`.

---

## 1. Princípio — autonomia total

> **Todo robô é AUTÔNOMO — da análise à execução.**

Um robô recebe o mercado e decide e executa **sozinho**, sem humano no loop
operacional: lê o dado → classifica o regime → gera o sinal → dimensiona →
envia a ordem → gerencia a saída (stop/alvo/trailing) → zera no fim do pregão.
O humano atua **fora** do loop: define a estratégia, valida, aprova/reprova e
monitora — não clica em cada ordem.

---

## 2. Validação tripla — Profit × MetaTrader × CAM

Todo robô é implementado em **três ambientes independentes** que devem
**convergir**. A convergência é a prova de que a lógica está correta (redundância
dissimilar / N-version programming): três caminhos de implementação diferentes
chegando ao mesmo resultado.

| Ambiente | Linguagem | Pasta | Papel |
|---|---|---|---|
| **Profit** (Nelogica) | NTSL | `apps/trader-robots/ntsl/` | Execução/backtest na B3 (conta Profit Pro) |
| **MetaTrader 5** | MQL5 | `apps/trader-robots/mql5/` | Execução/backtest tick (Strategy Tester) |
| **CAM** | Python | `apps/cam-cockpit/backend` (StrategyLab) | Backtest matemático + paridade |

**Dinâmica:** o mesmo robô roda backtest nos três e os resultados são comparados.
Divergência grande entre os ambientes = **bug a investigar** (fill, dado, custo,
lógica). Convergência = lógica confiável.

---

## 3. Ciclo de vida (status)

```
  INDEV  ──►  BACKTEST  ──►  ELEGIVEL  ──►  TESTE  ──►  APROVADO
                                                  │
                                                  └──►  REPROVADO
     ▲                                                     │
     └──────────────────  REVISION  ◄──────────────────────┘
```

| Status | Significado |
|---|---|
| **INDEV** | Em desenvolvimento. Lógica sendo escrita/ajustada nos ambientes. |
| **BACKTEST** | Em validação. Backtest nos três ambientes; convergência conferida. |
| **ELEGIVEL** | Pronto para teste real. Passou no backtest com convergência aceitável. |
| **TESTE** | Em teste em conta **REAL** (capital reduzido), operando autônomo. |
| **APROVADO** | O teste real ficou dentro de **±20%** do backtest. Robô liberado. |
| **REPROVADO** | O teste real divergiu **mais de ±20%** do backtest (sem causa sanada). |
| **REVISION** | O robô **gerou prejuízo independente do regime de mercado** → lógica/edge quebrado; volta para revisão (INDEV/BACKTEST). |

---

## 4. Critérios de decisão

### 4.1 Aprovação (TESTE → APROVADO/REPROVADO)
O resultado em **conta real** (status TESTE) deve ficar dentro de **±20% do
backtest** no mesmo período/condição.
- **Dentro de ±20%** → **APROVADO** (o backtest representa a realidade; o robô é
  confiável).
- **Fora de ±20%** → **REPROVADO** — investigar a causa da divergência antes de
  qualquer nova tentativa: modelo de fill/slippage, custo (corretagem/emolumentos/
  IR), qualidade do dado (mismatch tick/barra), latência, horário.

> A meta de ±20% reconhece que backtest nunca é igual ao real (slippage, custo,
> fila de execução), mas exige que a diferença seja **pequena e explicável** —
> não uma surpresa.

### 4.2 Revisão (→ REVISION)
Se o robô **gera prejuízo independentemente do regime de mercado** — perde em
tendência **e** em lateral, ou em qualquer condição — então **não há edge** (ou
está quebrado) e ele vai para **REVISION**. Um robô só é aceitável se **não
perde no seu regime-alvo**; um robô que perde em todo regime é defeito, não azar.

> Corolário: robô regime-dependente (ex.: ORB-30 ganha em tendência, perde em
> lateral) **não** vai para REVISION por perder no regime errado — desde que
> tenha um **filtro de regime** que o desligue fora do alvo (ou seja pareado com
> outro robô que cubra o regime oposto, ex.: híbrido ORB+VWAP).

---

## 5. Boas práticas obrigatórias por robô

1. **Guard-rail de conta** — durante INDEV/BACKTEST/ELEGIVEL, o robô só opera em
   **DEMO** (recusa conta real). Só em TESTE/APROVADO opera real, por ato
   explícito do Founder.
2. **Parâmetros idênticos** nos três ambientes (a paridade exige isso).
3. **Resultado BRUTO vs LÍQUIDO** — o backtest do CAM é bruto (sem custo/IR); a
   aprovação considera o **líquido** (o teste real já é líquido). A divergência
   esperada inclui o custo.
4. **Sizing por margem/risco** — o nº de contratos é função do capital, da margem
   da corretora e do drawdown tolerado (≤ limite do Founder), nunca um número
   solto.
5. **Documentação** — cada robô tem uma ficha de estratégia em
   `/project/trader-robots/` (lógica, parâmetros, status atual nos 3 ambientes).

---

## 6. Registro de status

Cada robô mantém seu status atual na sua ficha (`/project/trader-robots/<robo>.md`),
com a data e a evidência da transição (resultado de backtest, resultado de teste
real, motivo de REVISION/REPROVAÇÃO).

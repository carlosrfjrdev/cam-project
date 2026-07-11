"""
Funções puras do Regime de Markov — SPEC-Inspetor R-21..R-26.

ATRIBUIÇÃO (R-23): framework de Roan (@RohOnChain), refatorado por
Lewis Jackson (`markov_regime.py`). Aqui vendorizado como funções puras,
SEM o caminho yfinance e SEM o instalador `markov-hedge-fund-method.md`
(proibido — R-24). Alimentado pela série de close dos candles do CaM.

Caveats honestos (R-26), expostos no payload, não escondidos:
- rótulo é tendência DEFASADA; janelas sobrepostas autocorrelacionam → a
  "persistência" da matriz é em parte artefato;
- o backtest usa sign(sinal) e NÃO modela custo/spread → Sharpe é bruto;
- regime diário é filtro macro grosseiro.

Zero I/O, zero dependências externas (math/statistics puro).
"""
from __future__ import annotations

import math

STATES: tuple[str, str, str] = ("Bull", "Sideways", "Bear")
_IDX = {s: i for i, s in enumerate(STATES)}


def label_regimes(
    closes: list[float], window: int = 20, threshold: float = 0.05
) -> list[str]:
    """
    Rotula cada ponto (a partir de `window`) pelo retorno acumulado de `window`
    períodos vs ±threshold. Retorna lista de rótulos alinhada a closes[window:].
    """
    labels: list[str] = []
    for i in range(window, len(closes)):
        base = closes[i - window]
        if base == 0:
            labels.append("Sideways")
            continue
        ret = closes[i] / base - 1.0
        if ret > threshold:
            labels.append("Bull")
        elif ret < -threshold:
            labels.append("Bear")
        else:
            labels.append("Sideways")
    return labels


def build_transition_matrix(labels: list[str]) -> list[list[float]]:
    """Matriz de transição 3×3 por contagem (MLE), normalizada por linha."""
    counts = [[0.0] * 3 for _ in range(3)]
    for a, b in zip(labels, labels[1:], strict=False):
        counts[_IDX[a]][_IDX[b]] += 1.0
    matrix: list[list[float]] = []
    for row in counts:
        total = sum(row)
        if total == 0:
            # estado nunca observado como origem → uniforme (sem informação)
            matrix.append([1 / 3, 1 / 3, 1 / 3])
        else:
            matrix.append([c / total for c in row])
    return matrix


def stationary_distribution(
    matrix: list[list[float]], iterations: int = 1000, tol: float = 1e-12
) -> list[float]:
    """Distribuição estacionária via power iteration (mix de longo prazo)."""
    dist = [1 / 3, 1 / 3, 1 / 3]
    for _ in range(iterations):
        nxt = [
            sum(dist[i] * matrix[i][j] for i in range(3)) for j in range(3)
        ]
        s = sum(nxt)
        if s > 0:
            nxt = [x / s for x in nxt]
        if max(abs(nxt[k] - dist[k]) for k in range(3)) < tol:
            dist = nxt
            break
        dist = nxt
    return dist


def signal_from_matrix(matrix: list[list[float]], current_state: str) -> float:
    """
    Sinal ∈ [−1, 1] = P(Bull | atual) − P(Bear | atual), a partir da linha do
    estado corrente. Descritivo, não preditivo.
    """
    row = matrix[_IDX.get(current_state, _IDX["Sideways"])]
    return round(row[_IDX["Bull"]] - row[_IDX["Bear"]], 6)


def walk_forward_backtest(
    closes: list[float], window: int = 20, threshold: float = 0.05
) -> dict[str, float | None]:
    """
    Backtest walk-forward SEM lookahead: em cada passo, monta a matriz só com
    dados até t, deriva o sinal do estado atual e toma posição sign(sinal) para
    o retorno do próximo período. NÃO modela custo/spread (Sharpe bruto — R-26).
    Retorna {sharpe, max_drawdown} anualizados (√252).
    """
    labels = label_regimes(closes, window, threshold)
    if len(labels) < 5:
        return {"sharpe": None, "max_drawdown": None}

    # retornos diários alinhados aos rótulos (label[k] ↔ close[window+k])
    rets: list[float] = []
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    strat_returns: list[float] = []

    for k in range(1, len(labels)):
        # matriz com rótulos até k-1 (sem ver o futuro)
        m = build_transition_matrix(labels[: k])
        sig = signal_from_matrix(m, labels[k - 1])
        pos = 1.0 if sig > 0 else (-1.0 if sig < 0 else 0.0)
        c_prev = closes[window + k - 1]
        c_now = closes[window + k]
        day_ret = (c_now / c_prev - 1.0) if c_prev else 0.0
        r = pos * day_ret
        strat_returns.append(r)
        equity *= 1.0 + r
        peak = max(peak, equity)
        if peak > 0:
            max_dd = min(max_dd, equity / peak - 1.0)
        rets.append(r)

    if len(strat_returns) < 2:
        return {"sharpe": None, "max_drawdown": None}

    mean = sum(strat_returns) / len(strat_returns)
    var = sum((x - mean) ** 2 for x in strat_returns) / (len(strat_returns) - 1)
    std = math.sqrt(var)
    sharpe = (mean / std * math.sqrt(252)) if std > 0 else None

    return {
        "sharpe": round(sharpe, 4) if sharpe is not None else None,
        "max_drawdown": round(max_dd, 4),
    }


def analyze(
    closes: list[float], window: int = 20, threshold: float = 0.05
) -> dict:
    """Pipeline completo. Retorna dict pronto para o schema da rota."""
    labels = label_regimes(closes, window, threshold)
    if len(labels) < window:
        return {
            "insufficient_data": True,
            "points": len(closes),
            "labels": len(labels),
        }
    matrix = build_transition_matrix(labels)
    current = labels[-1]
    stat = stationary_distribution(matrix)
    signal = signal_from_matrix(matrix, current)
    wf = walk_forward_backtest(closes, window, threshold)
    return {
        "insufficient_data": False,
        "current_state": current,
        "states": list(STATES),
        "transition_matrix": matrix,
        "stationary": dict(zip(STATES, [round(x, 4) for x in stat], strict=True)),
        "signal": signal,
        "walk_forward": wf,
    }

"""
Classificação de regime INTRADAY no momento da entrada — funções puras.

Responde à pergunta do Founder: "80 pts é pullback certo dependendo do regime?".
O eixo que decide isso é **tendência vs lateralização** no curto prazo, não o
regime macro diário (esse é o Markov de `features/regime`, que continua válido
como overlay D1).

Medida: **Efficiency Ratio (Kaufman)** sobre `lookback` candles — razão entre o
deslocamento líquido e o caminho total percorrido:

    ER = |close[t] - close[t-N]| / Σ|close[i] - close[i-1]|

ER → 1: movimento direcional limpo (tendência). ER → 0: vai-e-volta (lateral /
ruído, onde um stop curto vira pullback garantido). Há precedente no robô
`cam_d1_orb30_sinais.mq5` (RegimeER). Zero I/O.
"""
from __future__ import annotations

from collections.abc import Sequence

# Rótulos de regime intraday.
TENDENCIA_ALTA = "TENDENCIA_ALTA"
TENDENCIA_BAIXA = "TENDENCIA_BAIXA"
LATERAL = "LATERAL"
INDEFINIDO = "INDEFINIDO"

DEFAULT_LOOKBACK = 15          # ~30 min em M2
DEFAULT_TREND_THRESHOLD = 0.45  # ER acima disso = tendência


def efficiency_ratio(closes: Sequence[float], lookback: int) -> float | None:
    """
    Efficiency Ratio de Kaufman sobre os últimos `lookback` closes.

    Retorna None se não há candles suficientes ou o caminho total é zero.
    """
    if lookback <= 0:
        raise ValueError("lookback deve ser > 0")
    if len(closes) < lookback + 1:
        return None
    seg = closes[-(lookback + 1):]
    net = abs(seg[-1] - seg[0])
    path = sum(abs(seg[i] - seg[i - 1]) for i in range(1, len(seg)))
    if path == 0:
        return None
    return net / path


def classify(
    closes: Sequence[float],
    lookback: int = DEFAULT_LOOKBACK,
    trend_threshold: float = DEFAULT_TREND_THRESHOLD,
) -> str:
    """
    Classifica o regime no fim da série `closes` (use closes ATÉ a entrada).

    - ER >= threshold e subindo  → TENDENCIA_ALTA
    - ER >= threshold e caindo   → TENDENCIA_BAIXA
    - ER <  threshold            → LATERAL
    - dados insuficientes        → INDEFINIDO
    """
    er = efficiency_ratio(closes, lookback)
    if er is None:
        return INDEFINIDO
    if er < trend_threshold:
        return LATERAL
    seg = closes[-(lookback + 1):]
    return TENDENCIA_ALTA if seg[-1] >= seg[0] else TENDENCIA_BAIXA


def closes_until(candles: Sequence[dict], cutoff_ts: float) -> list[float]:
    """Closes dos candles com `ts <= cutoff_ts` (para classificar no instante da entrada)."""
    return [c["c"] for c in candles if c["ts"] <= cutoff_ts]


def label_trade(
    candles: Sequence[dict],
    entry_ts: float,
    lookback: int = DEFAULT_LOOKBACK,
    trend_threshold: float = DEFAULT_TREND_THRESHOLD,
) -> str:
    """Rótulo de regime de UM trade: classifica usando só os closes até a entrada."""
    return classify(closes_until(candles, entry_ts), lookback, trend_threshold)

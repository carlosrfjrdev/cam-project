"""
Análise de Lead-Lag — núcleo puro (SPEC v0.5 R-19, R-20, R-22, R-25, R-29, R-31).

Funções **puras** (zero I/O), testáveis sem banco. Sub-versão 0.5.2 (cubo rápido /
OFI + correlação defasada). A validação estatística plena (DSR/FDR/SPA, walk-forward,
Hayashi-Yoshida) é 0.5.3 — aqui entregamos a MEDIÇÃO honesta + o contador de
tentativas + o veredito "dado insuficiente".

Honestidade (R-29 anti-look-ahead, R-31 dado insuficiente, R-33 só descritivo):
- correlação defasada usa retorno do alvo medido ESTRITAMENTE depois do sinal;
- abaixo do piso amostral → INSUFFICIENT_DATA (não "sem edge", não "edge");
- nenhuma função emite sinal/ordem/sizing — só evidência descritiva.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Piso amostral default abaixo do qual o veredito é INSUFFICIENT_DATA (R-31).
# Parametrizável por run; este é o default conservador.
DEFAULT_MIN_SAMPLES = 30


# --------------------------------------------------------------------------- #
# OFI — Order Flow Imbalance assinado (R-19)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SignedTrade:
    """Negócio com lado agressor (do flags) e volume. t_msc = timestamp em ms."""
    t_msc: int
    aggressor: int  # +1 comprador, -1 vendedor, 0 indefinido
    volume: int


def ofi(trades: list[SignedTrade]) -> float:
    """
    OFI bruto numa janela: x = Σ ε_k·v_k (R-19). Ticks indefinidos (ε=0) não
    contribuem. Sem normalização.
    """
    return float(sum(t.aggressor * t.volume for t in trades))


def ofi_normalized(trades: list[SignedTrade]) -> float:
    """
    OFI normalizado x̃ = (Σ ε_k·v_k) / (Σ v_k) ∈ [−1, 1] (R-19). Σ v_k usa o
    volume de TODOS os trades (inclui indefinidos no denominador, como o fluxo
    total observado). 0 se não há volume.
    """
    total = sum(t.volume for t in trades)
    if total <= 0:
        return 0.0
    return ofi(trades) / total


def ofi_series(
    trades: list[SignedTrade], window_ms: int, step_ms: int
) -> list[tuple[int, float]]:
    """
    Série de OFI normalizado em janela rolante (não é candle — R-19). Retorna
    [(t_fim_janela, x̃)]. `trades` devem estar ordenados por t_msc.
    """
    if not trades:
        return []
    t0 = trades[0].t_msc
    t_end = trades[-1].t_msc
    out: list[tuple[int, float]] = []
    t = t0 + window_ms
    while t <= t_end:
        win = [tr for tr in trades if t - window_ms < tr.t_msc <= t]
        out.append((t, ofi_normalized(win)))
        t += step_ms
    return out


# --------------------------------------------------------------------------- #
# Retornos e correlação defasada (R-20, R-25)
# --------------------------------------------------------------------------- #
def log_returns(prices: list[float]) -> list[float]:
    """Log-retornos r(t) = ln p(t) − ln p(t−1). Preços > 0."""
    out: list[float] = []
    for i in range(1, len(prices)):
        p0, p1 = prices[i - 1], prices[i]
        if p0 > 0 and p1 > 0:
            out.append(math.log(p1 / p0))
        else:
            out.append(0.0)
    return out


def pearson(xs: list[float], ys: list[float]) -> float:
    """Correlação de Pearson. NaN se n<2 ou variância nula."""
    n = min(len(xs), len(ys))
    if n < 2:
        return float("nan")
    xs, ys = xs[:n], ys[:n]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=False))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


@dataclass(frozen=True)
class LagCell:
    """Resultado de uma célula (fonte→alvo, defasagem δ)."""
    delta: int
    correlation: float
    n_samples: int
    verdict: str  # OK | INSUFFICIENT_DATA


def lagged_correlation(
    source_signal: list[float],
    target_returns: list[float],
    delta: int,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> LagCell:
    """
    Correlação defasada C(δ) = Corr( signal(t−δ), target_return(t) ), δ ≥ 1
    (R-20/R-25). **Anti-look-ahead (R-29):** o sinal em t−δ prediz o retorno do
    alvo em t, medido estritamente depois. Alinha as séries pela defasagem.

    `source_signal` e `target_returns` são séries alinhadas no mesmo índice de
    tempo (mesma grade). Veredito INSUFFICIENT_DATA abaixo do piso (R-31).
    """
    if delta < 1:
        raise ValueError("delta deve ser ≥ 1 (anti-look-ahead, R-29)")
    # sinal atrasado δ posições prevê o alvo atual
    src = source_signal[:-delta] if delta < len(source_signal) else []
    tgt = target_returns[delta:]
    n = min(len(src), len(tgt))
    if n < min_samples:
        return LagCell(delta=delta, correlation=float("nan"),
                       n_samples=n, verdict="INSUFFICIENT_DATA")
    corr = pearson(src[:n], tgt[:n])
    if math.isnan(corr):
        return LagCell(delta=delta, correlation=float("nan"),
                       n_samples=n, verdict="INSUFFICIENT_DATA")
    return LagCell(delta=delta, correlation=corr, n_samples=n, verdict="OK")


def lag_profile(
    source_signal: list[float],
    target_returns: list[float],
    delta_grid: list[int],
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> list[LagCell]:
    """Perfil de correlação sobre a grade de defasagens (o '3º eixo' do cubo)."""
    return [
        lagged_correlation(source_signal, target_returns, d, min_samples)
        for d in sorted(set(delta_grid))
        if d >= 1
    ]


# --------------------------------------------------------------------------- #
# Event study assinado — expectância líquida (R-22)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class EventStudy:
    horizon: int
    n_events: int
    mu_gross: float      # expectância bruta do retorno assinado
    mu_net: float        # líquida (− custo round-trip)
    hit_rate: float      # informativo, NUNCA prova isolada (Art. 28)
    verdict: str


def _zscore(series: list[float], window: int) -> list[float]:
    """Padronização rolante z(t) = (x−μ)/σ na janela (R-22)."""
    out: list[float] = []
    for i in range(len(series)):
        lo = max(0, i - window + 1)
        win = series[lo : i + 1]
        if len(win) < 2:
            out.append(0.0)
            continue
        mu = sum(win) / len(win)
        sd = math.sqrt(sum((x - mu) ** 2 for x in win) / (len(win) - 1))
        out.append((series[i] - mu) / sd if sd > 0 else 0.0)
    return out


def event_study(
    source_signal: list[float],
    target_returns: list[float],
    horizon: int,
    kappa: float = 2.0,
    cost: float = 0.0,
    zwindow: int = 50,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> EventStudy:
    """
    Event study assinado (R-22): evento quando |z_F(t)|>κ; sinal s=sgn(z_F(t));
    retorno assinado do alvo g = s·r_D(t+h). Expectância LÍQUIDA μ̂ = mean(g) −
    custo. **Anti-look-ahead (R-29):** o retorno do alvo é medido a partir de
    t+1 (estritamente depois do evento). hit_rate é informativo, não prova (R-22).
    """
    z = _zscore(source_signal, zwindow)
    gs: list[float] = []
    for t in range(len(z)):
        if abs(z[t]) <= kappa:
            continue
        s = 1.0 if z[t] > 0 else -1.0
        # retorno do alvo do evento (t) até t+horizon, medido após o evento
        idx = t + horizon
        if idx >= len(target_returns):
            continue
        # soma de log-retornos de t+1..t+horizon (estritamente depois)
        fwd = sum(target_returns[t + 1 : idx + 1])
        gs.append(s * fwd)
    n = len(gs)
    if n < min_samples:
        return EventStudy(horizon=horizon, n_events=n, mu_gross=float("nan"),
                          mu_net=float("nan"), hit_rate=float("nan"),
                          verdict="INSUFFICIENT_DATA")
    mu_gross = sum(gs) / n
    mu_net = mu_gross - cost
    hit = sum(1 for g in gs if g > 0) / n
    return EventStudy(horizon=horizon, n_events=n, mu_gross=mu_gross,
                      mu_net=mu_net, hit_rate=hit, verdict="OK")


# --------------------------------------------------------------------------- #
# Trial accounting (R-30, faseado) — contador honesto
# --------------------------------------------------------------------------- #
def count_trials(
    n_sources: int, n_targets: int, n_deltas: int, reruns: int = 1
) -> int:
    """
    N_t = |fontes| × |alvos| × |grade δ| × reruns (R-30). O contador é exposto;
    a deflação estatística plena (DSR) é 0.5.3. Aqui contamos honestamente.
    """
    return max(0, n_sources) * max(0, n_targets) * max(0, n_deltas) * max(1, reruns)

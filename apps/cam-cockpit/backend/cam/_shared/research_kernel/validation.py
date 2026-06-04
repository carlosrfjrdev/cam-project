"""
Validação estatística honesta — núcleo puro (SPEC v0.5 R-30/R-32, §5.1).

Sub-versão 0.5.3 (a camada de FALSIFICAÇÃO). Funções puras, sem I/O. Implementa:
- Sharpe ratio + Deflated Sharpe Ratio (Bailey & López de Prado) — penaliza o nº
  de tentativas (deflaciona o data-snooping do cubo);
- FDR Benjamini-Hochberg — controla a taxa de falsa descoberta entre células;
- walk-forward split (treino/teste/passo) + purged CV com embargo;
- Hayashi-Yoshida (mata-Epps) — covariância assíncrona sem reamostragem.

ATRIBUIÇÃO: DSR de Bailey & López de Prado (2014); HY de Hayashi & Yoshida (2005).
Implementação própria a partir das fórmulas (CaM-RESEARCH §5.1, §3.3).

Honestidade (R-30): o denominador da DSR é o nº REAL de tentativas. Abaixo do
piso de amostra, o veredito é "dado insuficiente", nunca "edge".
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Euler–Mascheroni (γ) — usado no SR esperado sob a hipótese nula (DSR).
_EULER_GAMMA = 0.5772156649015329


# --------------------------------------------------------------------------- #
# Normal padrão (CDF / inversa) — sem scipy (Risk Engine / slice leve)
# --------------------------------------------------------------------------- #
def norm_cdf(x: float) -> float:
    """CDF da normal padrão via erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """
    Inversa da CDF normal padrão (quantil). Algoritmo de Acklam — precisão ~1e-9.
    """
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# --------------------------------------------------------------------------- #
# Sharpe + momentos
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SharpeStats:
    sharpe: float       # não anualizado (por período)
    n: int
    skew: float
    kurtosis: float     # curtose (não-excesso; normal = 3)


def sharpe_stats(returns: list[float]) -> SharpeStats:
    """Sharpe por período + skew/curtose (entram na DSR)."""
    n = len(returns)
    if n < 2:
        return SharpeStats(float("nan"), n, 0.0, 3.0)
    mu = sum(returns) / n
    var = sum((r - mu) ** 2 for r in returns) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return SharpeStats(float("nan"), n, 0.0, 3.0)
    sr = mu / sd
    m3 = sum((r - mu) ** 3 for r in returns) / n
    m4 = sum((r - mu) ** 4 for r in returns) / n
    skew = m3 / (sd ** 3) if sd > 0 else 0.0
    kurt = m4 / (var ** 2) if var > 0 else 3.0
    return SharpeStats(sr, n, skew, kurt)


# --------------------------------------------------------------------------- #
# Deflated Sharpe Ratio (Bailey & López de Prado) — R-30
# --------------------------------------------------------------------------- #
def expected_max_sharpe(n_trials: int, var_sr: float) -> float:
    """
    SR esperado do MÁXIMO sob H0 (todos os SR têm média 0), dado N_t tentativas.
    SR0 = sqrt(var_sr) · [(1-γ)·Z⁻¹(1 - 1/N) + γ·Z⁻¹(1 - 1/(N·e))]  (§5.1)
    """
    n = max(2, n_trials)
    z1 = norm_ppf(1 - 1.0 / n)
    z2 = norm_ppf(1 - 1.0 / (n * math.e))
    return math.sqrt(max(var_sr, 0.0)) * ((1 - _EULER_GAMMA) * z1 + _EULER_GAMMA * z2)


def deflated_sharpe_ratio(
    observed_sr: float,
    n_obs: int,
    skew: float,
    kurtosis: float,
    n_trials: int,
    benchmark_sr: float | None = None,
) -> float:
    """
    DSR (Bailey & López de Prado, 2014). Probabilidade de que o SR observado seja
    > que o esperado sob H0 ajustado por N_t tentativas, corrigido por skew/kurt.

    DSR = Z( (SR_obs − SR0)·sqrt(n−1) / sqrt(1 − γ3·SR_obs + (γ4−1)/4·SR_obs²) )

    Retorna prob ∈ [0,1] (ex.: exigir DSR > 0.95). NaN se amostra/insumos ruins.
    """
    if n_obs < 2 or math.isnan(observed_sr):
        return float("nan")
    # variância dos SR entre tentativas: aproximação 1/n_obs quando não medida.
    var_sr = 1.0 / n_obs
    sr0 = benchmark_sr if benchmark_sr is not None else expected_max_sharpe(
        n_trials, var_sr
    )
    denom = 1.0 - skew * observed_sr + ((kurtosis - 1.0) / 4.0) * observed_sr ** 2
    if denom <= 0:
        return float("nan")
    z = (observed_sr - sr0) * math.sqrt(n_obs - 1) / math.sqrt(denom)
    return norm_cdf(z)


# --------------------------------------------------------------------------- #
# FDR — Benjamini-Hochberg (R-30, §5.1)
# --------------------------------------------------------------------------- #
def benjamini_hochberg(p_values: list[float], q: float = 0.05) -> list[bool]:
    """
    Controle de FDR (BH). Retorna máscara de rejeições de H0 (descobertas) na
    ordem original. q = taxa de falsa descoberta tolerada.
    """
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    thresh_k = -1
    for rank, idx in enumerate(order, start=1):
        if p_values[idx] <= (rank / m) * q:
            thresh_k = rank
    rejected = [False] * m
    if thresh_k > 0:
        for rank, idx in enumerate(order, start=1):
            if rank <= thresh_k:
                rejected[idx] = True
    return rejected


def corr_pvalue(corr: float, n: int) -> float:
    """
    p-valor bicaudal de uma correlação de Pearson (t de Student → normal aprox.).
    Conservador para n moderado; suficiente para o gate de FDR.
    """
    if n < 3 or math.isnan(corr) or abs(corr) >= 1.0:
        return 1.0
    t = corr * math.sqrt((n - 2) / (1 - corr * corr))
    # aproximação normal da t (n-2 g.l.); conservadora para o gate
    return 2.0 * (1.0 - norm_cdf(abs(t)))


# --------------------------------------------------------------------------- #
# Walk-forward + purged CV (R-32)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class WalkForwardSplit:
    train_start: int
    train_end: int    # exclusivo
    test_start: int
    test_end: int     # exclusivo


def walk_forward_splits(
    n: int, train: int, test: int, step: int, embargo: int = 0
) -> list[WalkForwardSplit]:
    """
    Splits walk-forward rolantes com embargo (purga entre treino e teste — R-32).
    O embargo remove `embargo` observações entre o fim do treino e o início do
    teste (evita vazamento por autocorrelação de labels).
    """
    splits: list[WalkForwardSplit] = []
    start = 0
    while start + train + embargo + test <= n:
        tr_end = start + train
        te_start = tr_end + embargo
        te_end = te_start + test
        splits.append(WalkForwardSplit(start, tr_end, te_start, te_end))
        start += step
    return splits


# --------------------------------------------------------------------------- #
# Hayashi-Yoshida (mata-Epps) — R-21/R-32, §3.3
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TickObs:
    """Observação de preço assíncrona: (t_msc, price)."""
    t_msc: int
    price: float


def _log_increments(obs: list[TickObs]) -> list[tuple[int, int, float]]:
    """Incrementos log entre observações consecutivas: (t_ini, t_fim, Δlog)."""
    out: list[tuple[int, int, float]] = []
    for i in range(1, len(obs)):
        p0, p1 = obs[i - 1].price, obs[i].price
        if p0 > 0 and p1 > 0:
            out.append((obs[i - 1].t_msc, obs[i].t_msc, math.log(p1 / p0)))
    return out


def hayashi_yoshida_cov(a: list[TickObs], b: list[TickObs]) -> float:
    """
    Covariação integrada HY entre dois processos observados de forma ASSÍNCRONA
    (R-21). Soma Δaᵢ·Δbⱼ quando os intervalos (tᵢ₋₁,tᵢ] e (tⱼ₋₁,tⱼ] se sobrepõem.
    Sem reamostragem → sem viés de Epps.
    """
    inc_a = _log_increments(a)
    inc_b = _log_increments(b)
    cov = 0.0
    for ia0, ia1, da in inc_a:
        for ib0, ib1, db in inc_b:
            # intervalos (ia0, ia1] e (ib0, ib1] se sobrepõem?
            if ia1 > ib0 and ib1 > ia0:
                cov += da * db
    return cov


def hayashi_yoshida_corr(a: list[TickObs], b: list[TickObs]) -> float:
    """Correlação HY: cov_HY / sqrt(var_HY(a)·var_HY(b)). NaN se variância nula."""
    cov = hayashi_yoshida_cov(a, b)
    va = hayashi_yoshida_cov(a, a)
    vb = hayashi_yoshida_cov(b, b)
    if va <= 0 or vb <= 0:
        return float("nan")
    return cov / math.sqrt(va * vb)


def survives_epps(naive_corr: float, hy_corr: float, tol: float = 0.5) -> bool:
    """
    H5 (R-21): a correlação ingênua sobrevive ao HY? Se o HY colapsa para ~0
    enquanto a ingênua era alta, a relação era artefato de Epps (reamostragem).
    `tol` = fração mínima da correlação ingênua que o HY deve preservar.
    """
    if math.isnan(naive_corr) or math.isnan(hy_corr):
        return False
    if abs(naive_corr) < 1e-9:
        return abs(hy_corr) < 1e-9
    return abs(hy_corr) >= tol * abs(naive_corr)

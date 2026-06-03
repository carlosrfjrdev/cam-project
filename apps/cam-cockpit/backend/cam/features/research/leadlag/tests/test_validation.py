"""Testes do núcleo de validação estatística (R-30/R-32, §5.1) — puros."""
import math

from cam.features.research.leadlag.validation import (
    TickObs,
    benjamini_hochberg,
    corr_pvalue,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    hayashi_yoshida_corr,
    norm_cdf,
    norm_ppf,
    sharpe_stats,
    survives_epps,
    walk_forward_splits,
)


# ---- normal ----
def test_norm_cdf_simetria() -> None:
    assert abs(norm_cdf(0.0) - 0.5) < 1e-12
    assert abs(norm_cdf(1.96) - 0.975) < 1e-3


def test_norm_ppf_inversa() -> None:
    for p in (0.025, 0.5, 0.975):
        assert abs(norm_cdf(norm_ppf(p)) - p) < 1e-6


# ---- sharpe ----
def test_sharpe_stats() -> None:
    s = sharpe_stats([0.01, 0.02, -0.01, 0.015, 0.005])
    assert s.n == 5
    assert not math.isnan(s.sharpe)


def test_sharpe_variancia_nula() -> None:
    s = sharpe_stats([0.01] * 10)
    assert math.isnan(s.sharpe)


# ---- DSR: mais tentativas → barra mais alta (R-30) ----
def test_expected_max_sharpe_cresce_com_tentativas() -> None:
    var = 0.01
    assert expected_max_sharpe(1000, var) > expected_max_sharpe(10, var)


def test_dsr_penaliza_muitas_tentativas() -> None:
    # mesmo SR observado, mais tentativas → DSR menor (mais cético).
    dsr_poucas = deflated_sharpe_ratio(0.15, 200, 0.0, 3.0, n_trials=5)
    dsr_muitas = deflated_sharpe_ratio(0.15, 200, 0.0, 3.0, n_trials=5000)
    assert dsr_muitas < dsr_poucas


def test_dsr_em_faixa_probabilidade() -> None:
    dsr = deflated_sharpe_ratio(0.2, 250, 0.0, 3.0, n_trials=100)
    assert 0.0 <= dsr <= 1.0


# ---- FDR Benjamini-Hochberg ----
def test_bh_rejeita_pequenos_pvalues() -> None:
    pv = [0.001, 0.002, 0.5, 0.8, 0.9]
    rej = benjamini_hochberg(pv, q=0.05)
    assert rej[0] is True and rej[1] is True
    assert rej[3] is False and rej[4] is False


def test_bh_nada_rejeitado_quando_todos_altos() -> None:
    rej = benjamini_hochberg([0.6, 0.7, 0.8], q=0.05)
    assert rej == [False, False, False]


def test_bh_vazio() -> None:
    assert benjamini_hochberg([], q=0.05) == []


def test_corr_pvalue_alta_corr_baixo_p() -> None:
    p = corr_pvalue(0.9, 100)
    assert p < 0.01


# ---- walk-forward ----
def test_walk_forward_splits_com_embargo() -> None:
    splits = walk_forward_splits(n=200, train=100, test=20, step=20, embargo=5)
    assert len(splits) > 0
    s = splits[0]
    assert s.train_end == 100
    assert s.test_start == 105   # embargo de 5
    assert s.test_end == 125
    # sem sobreposição treino/teste
    assert s.test_start > s.train_end


def test_walk_forward_vazio_se_dados_curtos() -> None:
    assert walk_forward_splits(n=50, train=100, test=20, step=20) == []


# ---- Hayashi-Yoshida (mata-Epps) ----
def test_hy_corr_sincronos_positivos() -> None:
    # dois processos sobem juntos em instantes alinhados → HY corr > 0
    a = [TickObs(i * 100, 100.0 + i) for i in range(20)]
    b = [TickObs(i * 100, 50.0 + i * 0.5) for i in range(20)]
    hy = hayashi_yoshida_corr(a, b)
    assert hy > 0.5


def test_survives_epps_detecta_artefato() -> None:
    # correlação ingênua alta, HY ~0 → NÃO sobrevive (era Epps)
    assert survives_epps(naive_corr=0.8, hy_corr=0.02) is False
    # HY preserva a correlação → sobrevive
    assert survives_epps(naive_corr=0.8, hy_corr=0.7) is True

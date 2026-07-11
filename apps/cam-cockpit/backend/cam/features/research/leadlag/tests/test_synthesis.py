"""Testes da síntese regime × gatilho (R-28) — puros."""
from cam.features.research.leadlag.synthesis import gated_signal, synthesize


def test_gated_signal_zera_fora_do_regime() -> None:
    g = gated_signal([True, False, True], [1.0, 1.0, 1.0])
    assert g == [1.0, 0.0, 1.0]


def test_composicao_supera_partes() -> None:
    n = 100
    # regime favorável na 1ª metade; gatilho acerta a direção lá.
    regime = [i < 50 for i in range(n)]
    trigger = [1.0] * n
    # alvo: sobe no regime favorável, ruído fora.
    target = [0.01 if i < 50 else (-0.01 if i % 2 else 0.01) for i in range(n)]
    r = synthesize(regime, trigger, target, min_samples=10)
    # composição (gatilho dentro do regime) deve bater o gatilho sozinho
    assert r.mu_combined >= r.mu_trigger
    assert r.verdict in ("SURVIVOR", "NO_LIFT")


def test_sem_lift_quando_composicao_nao_supera() -> None:
    n = 60
    regime = [True] * n  # regime sempre favorável → composição = gatilho
    trigger = [1.0] * n
    target = [0.001] * n
    r = synthesize(regime, trigger, target, min_samples=10)
    # composição == gatilho (não supera) → NO_LIFT
    assert r.verdict == "NO_LIFT"


def test_dado_insuficiente() -> None:
    r = synthesize([True] * 5, [1.0] * 5, [0.01] * 5, min_samples=30)
    assert r.verdict == "INSUFFICIENT_DATA"

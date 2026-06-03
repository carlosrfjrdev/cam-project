"""Testes da série contínua / rolagem WIN/WDO (R-14) — puros."""
from cam.features.research.leadlag.continuous import (
    ContractBar,
    build_continuous,
    classify_mode,
)


def _seg(
    contract: str, base_ts: int, prices: list[float], atr: float
) -> list[ContractBar]:
    return [
        ContractBar(contract=contract, ts=base_ts + i * 86400, close=p, atr=atr)
        for i, p in enumerate(prices)
    ]


def test_continuo_ratio_remove_salto() -> None:
    # contrato antigo termina em 100, novo começa em 110 (gap de 10)
    old = _seg("WINM26", 0, [98, 99, 100], atr=5.0)
    new = _seg("WINQ26", 3 * 86400, [110, 111, 112], atr=5.0)
    cs = build_continuous([old, new], splice_method="ratio")
    closes = [p for _, p in cs.closes]
    # série ajustada deve ser contínua (sem salto de ~10)
    diffs = [abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))]
    assert max(diffs) < 5.0  # sem o salto bruto de 10
    assert len(cs.roll_points) == 1
    assert cs.roll_points[0].from_c == "WINM26"
    assert cs.roll_points[0].to_c == "WINQ26"


def test_teste_de_salto_reporta_gap_em_atr() -> None:
    old = _seg("A", 0, [100], atr=2.0)
    new = _seg("B", 86400, [110], atr=2.0)  # gap 10, atr 2 → 5 ATR
    cs = build_continuous([old, new], splice_method="ratio")
    assert cs.max_gap_in_atr == 5.0


def test_splice_none_preserva_salto() -> None:
    old = _seg("A", 0, [100], atr=5.0)
    new = _seg("B", 86400, [110], atr=5.0)
    cs = build_continuous([old, new], splice_method="none", max_jump_atr=1.0)
    closes = [p for _, p in cs.closes]
    # com 'none' o salto bruto permanece e o teste de salto reprova (gap 2 ATR > 1)
    assert max(closes) == 110.0
    assert cs.passes_jump_test is False


def test_segmentos_vazios() -> None:
    cs = build_continuous([], splice_method="ratio")
    assert cs.closes == []
    assert cs.passes_jump_test is True


def test_classify_mode() -> None:
    assert classify_mode("M5") == "intraday"
    assert classify_mode("D1") == "swing"
    assert classify_mode("H1") == "both"

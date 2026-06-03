"""Testes do hash composto / batch (R-16/R-03) — puros, determinísticos."""
from cam.features.research.leadlag.snapshot import batch_hash, composite_hash


def test_composite_hash_deterministico() -> None:
    h1 = composite_hash("raw1", "cal-v1", ["M1", "M5"], "rule1")
    h2 = composite_hash("raw1", "cal-v1", ["M5", "M1"], "rule1")  # ordem TF
    assert h1 == h2  # timeframes ordenados internamente


def test_composite_hash_muda_com_regra() -> None:
    base = composite_hash("raw1", "cal-v1", ["M1"], "rule1")
    diff = composite_hash("raw1", "cal-v1", ["M1"], "rule2")  # regra diferente
    assert base != diff  # mudar regra → novo hash (nova run)


def test_composite_hash_muda_com_raw() -> None:
    a = composite_hash("rawA", "cal-v1", ["M1"], "rule1")
    b = composite_hash("rawB", "cal-v1", ["M1"], "rule1")
    assert a != b


def test_batch_hash_deterministico() -> None:
    rows = [{"s": "WIN$", "p": 100, "v": 3}, {"s": "WIN$", "p": 101, "v": 5}]
    assert batch_hash(rows) == batch_hash(list(rows))

"""
TDD First — TASK-010 (BL-A): lint_mql5.py.

Verifica que o lint detecta OrderSend/OrderClose/PositionOpen/PositionClose/
OrderModify em arquivos .mq5/.mqh fora da allowlist.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_SCRIPT = REPO_ROOT / "scripts" / "lint_mql5.py"


def _run(mql5_dir: Path) -> tuple[int, dict]:
    # sys.executable (não "python3") — cross-platform: no Windows o alias
    # python3 não existe e o subprocess retornaria stdout vazio.
    result = subprocess.run(
        [sys.executable, str(LINT_SCRIPT), "--mql5-dir", str(mql5_dir), "--json"],
        capture_output=True,
        text=True,
    )
    parsed = json.loads(result.stdout)
    return result.returncode, parsed


class TestLintMQL5:
    def test_clean_dir_returns_zero(self, tmp_path: Path):
        ok_file = tmp_path / "cam_bridge.mq5"
        ok_file.write_text(
            "// CamBridge — read-only\nvoid OnTimer() { Print(\"ok\"); }\n"
        )
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_detects_OrderSend_outside_allowlist(self, tmp_path: Path):
        bad = tmp_path / "cam_bridge.mq5"
        bad.write_text(
            "void OnTimer() {\n"
            "  MqlTradeRequest req;\n"
            "  OrderSend(req, result);\n"  # violação
            "}\n"
        )
        code, data = _run(tmp_path)
        assert code == 1
        assert any(v["function"] == "OrderSend" for v in data["violations"])

    def test_allows_OrderSend_in_cam_risk_mirror(self, tmp_path: Path):
        ok = tmp_path / "cam_risk_mirror.mq5"
        ok.write_text(
            "void Eval() {\n"
            "  OrderSend(req, result);\n"  # permitido só aqui
            "}\n"
        )
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_allows_orders_in_cam_d1_orb30_exec(self, tmp_path: Path):
        # ADR-SL-04 — executor D1 puro tambem pode enviar ordem (DEMO-only).
        ok = tmp_path / "cam_d1_orb30_exec.mq5"
        ok.write_text(
            "void f() {\n"
            "  g_trade.PositionClose(_Symbol);\n"  # permitido aqui
            "}\n"
        )
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_recorder_cam_d1_orb30_stays_forbidden(self, tmp_path: Path):
        # o GRAVADOR de paridade NAO pode enviar ordem (fora da allowlist).
        bad = tmp_path / "cam_d1_orb30.mq5"
        bad.write_text("void f() { OrderSend(req, res); }\n")
        code, data = _run(tmp_path)
        assert code == 1
        assert any(v["function"] == "OrderSend" for v in data["violations"])

    def test_allows_orders_in_cam_d1_orb30_sinais(self, tmp_path: Path):
        # ADR-SL-04 — executor D1 + regime embutido (DEMO-only) pode enviar ordem.
        ok = tmp_path / "cam_d1_orb30_sinais.mq5"
        ok.write_text("void f() { g_trade.PositionClose(_Symbol); }\n")
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_allows_orders_in_cam_d2_vwap_exec(self, tmp_path: Path):
        # ADR-SL-04 — executor D2 tambem pode enviar ordem (DEMO-only).
        ok = tmp_path / "cam_d2_vwap_exec.mq5"
        ok.write_text("void f() { g_trade.PositionClose(_Symbol); }\n")
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_allows_orders_in_cam_hibrido(self, tmp_path: Path):
        # ADR-SL-04 — executor hibrido D1+D2 pode enviar ordem (DEMO-only).
        ok = tmp_path / "cam_hibrido_orb30_vwap.mq5"
        ok.write_text("void f() { g_trade.PositionClose(_Symbol); }\n")
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_recorder_cam_d2_vwap_stays_forbidden(self, tmp_path: Path):
        bad = tmp_path / "cam_d2_vwap.mq5"
        bad.write_text("void f() { OrderSend(req, res); }\n")
        code, data = _run(tmp_path)
        assert code == 1

    def test_detects_OrderClose_PositionOpen_PositionClose_OrderModify(
        self, tmp_path: Path
    ):
        bad = tmp_path / "cam_bridge.mq5"
        bad.write_text(
            "void f1() { OrderClose(t, v, p, slip); }\n"
            "void f2() { PositionOpen(); }\n"
            "void f3() { PositionClose(t); }\n"
            "void f4() { OrderModify(t, p, sl, tp, exp); }\n"
        )
        code, data = _run(tmp_path)
        assert code == 1
        funcs = {v["function"] for v in data["violations"]}
        assert funcs == {"OrderClose", "PositionOpen",
                         "PositionClose", "OrderModify"}

    def test_ignores_comments(self, tmp_path: Path):
        ok = tmp_path / "cam_bridge.mq5"
        ok.write_text(
            "// OrderSend não deve disparar aqui\n"
            "/* exemplo: OrderSend(...) */\n"
            "void OnTimer() { Print(\"OrderSend é proibido\"); }\n"
        )
        code, data = _run(tmp_path)
        assert code == 0
        assert data["violations"] == []

    def test_ignores_strings(self, tmp_path: Path):
        ok = tmp_path / "cam_bridge.mq5"
        ok.write_text(
            'void f() { Print("OrderSend não dispara dentro de string"); }\n'
        )
        code, data = _run(tmp_path)
        assert code == 0

    def test_machine_readable_json_has_files_list(self, tmp_path: Path):
        f = tmp_path / "cam_bridge.mq5"
        f.write_text("void OnTimer() {}\n")
        code, data = _run(tmp_path)
        assert "checked_files" in data
        assert any(p.endswith("cam_bridge.mq5") for p in data["checked_files"])
        assert "violations" in data

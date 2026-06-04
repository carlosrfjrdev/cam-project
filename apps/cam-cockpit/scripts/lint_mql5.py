#!/usr/bin/env python3
"""
lint_mql5.py — TASK-010 (BL-A SPEC v0.4).

Lint determinístico que falha CI se chamadas de envio de ordem aparecerem
em qualquer arquivo .mq5/.mqh fora da allowlist.

Funções proibidas fora da allowlist:
    OrderSend, OrderClose, PositionOpen, PositionClose, OrderModify

Em BL-A, `cam_risk_mirror.mq5` ainda não existe — então o lint funciona como
**zero-tolerance** (nenhum .mq5/.mqh pode usar essas funções).

Em BL-E (T025) o allowlist foi habilitado para `cam_risk_mirror.mq5`.

StrategyLab Onda 1 (ADR-SL-04) adiciona `cam_d1_orb30_exec.mq5` à allowlist —
o EA EXECUTOR da estratégia D1 (opera de verdade, DEMO-only). O EA gravador de
paridade `cam_d1_orb30.mq5` continua FORA da allowlist (não envia ordem).

CLI:
    python scripts/lint_mql5.py [--mql5-dir PATH] [--json]

Exit codes:
    0  OK — nenhuma violação.
    1  Violações encontradas.
    2  Erro de invocação.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Funções monitoradas (case-sensitive — MQL5 é case-sensitive)
_FORBIDDEN_FUNCS = (
    "OrderSend",
    "OrderClose",
    "PositionOpen",
    "PositionClose",
    "OrderModify",
)

# Arquivos permitidos a usar OrderSend etc.:
#   - cam_risk_mirror.mq5   (BL-E T025) — executor com Risk Engine espelho.
#   - cam_d1_orb30_exec.mq5 (ADR-SL-04) — executor D1 puro (DEMO-only, sem risco).
_ALLOWED_FILES = {"cam_risk_mirror.mq5", "cam_d1_orb30_exec.mq5"}


def _strip_comments_and_strings(line: str) -> str:
    """
    Remove comentários (// e /* */) e strings literais para evitar falsos-positivos
    quando uma menção a OrderSend aparece dentro de string ou comentário.

    Implementação simples para linha única — MQL5 não permite /* */
    multi-linha sem fechamento.
    """
    # Remove // comment
    idx = line.find("//")
    if idx != -1:
        line = line[:idx]
    # Remove /* ... */
    line = re.sub(r"/\*.*?\*/", "", line)
    # Remove conteúdo de strings ("…")
    line = re.sub(r'"[^"]*"', '""', line)
    return line


_CALL_RE = re.compile(
    r"\b(" + "|".join(_FORBIDDEN_FUNCS) + r")\s*\("
)


def lint_file(path: Path) -> list[dict]:
    """Retorna lista de violações: [{file, line, function, snippet}]."""
    violations: list[dict] = []
    if path.name in _ALLOWED_FILES:
        return violations
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations
    for lineno, raw in enumerate(text.splitlines(), start=1):
        sanitized = _strip_comments_and_strings(raw)
        for match in _CALL_RE.finditer(sanitized):
            violations.append({
                "file": str(path),
                "line": lineno,
                "function": match.group(1),
                "snippet": raw.strip()[:140],
            })
    return violations


def find_mql5_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        list(root.rglob("*.mq5")) + list(root.rglob("*.mqh"))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mql5-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "mql5",
        help="Diretório raiz dos arquivos MQL5 (.mq5/.mqh)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída JSON consumível por CI.",
    )
    args = parser.parse_args(argv)

    files = find_mql5_files(args.mql5_dir)
    all_violations: list[dict] = []
    for fp in files:
        all_violations.extend(lint_file(fp))

    if args.json:
        sys.stdout.write(json.dumps({
            "checked_files": [str(f) for f in files],
            "violations": all_violations,
        }, indent=2) + "\n")
    else:
        for v in all_violations:
            sys.stdout.write(
                f"❌ {v['file']}:{v['line']}: "
                f"{v['function']} chamado em arquivo não-permitido.\n"
                f"   → {v['snippet']}\n"
            )
        if not all_violations:
            sys.stdout.write(
                f"✅ lint_mql5: {len(files)} arquivo(s) — sem violações.\n"
            )
        else:
            sys.stdout.write(
                f"\n❌ lint_mql5: {len(all_violations)} violação(ões) em "
                f"{len(set(v['file'] for v in all_violations))} arquivo(s).\n"
            )

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())

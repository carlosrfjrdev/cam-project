"""
Importador de relatorio MT5 — SPEC v0.2 §R15.

Aceita HTML (Reports do MT5), XML e CSV exportados pelo terminal.
Deduplicacao por hash da operacao (SHA-256 dos campos canonicos).

qa-sec: parser HTML usa stdlib html.parser, NAO executa <script>.
"""
import csv
import hashlib
import io
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from html.parser import HTMLParser
from typing import Iterable


@dataclass(frozen=True)
class ParsedTrade:
    """Trade parseado de um relatorio MT5, ainda nao persistido."""

    open_time: datetime
    close_time: datetime
    symbol: str
    direction: str  # LONG | SHORT
    contracts: int
    entry_price: Decimal
    exit_price: Decimal
    stop_loss: Decimal | None
    take_profit: Decimal | None
    commission: Decimal
    swap: Decimal
    profit: Decimal


# ---------------------------------------------------------------------------
# Normalizacao de simbolos MT5 (sufixos do broker — WIN$N, WDO$, etc.)
# ---------------------------------------------------------------------------
_SYMBOL_NORMALIZER = re.compile(r"^(WIN|WDO)[\$NFGHJKMQUVXZ\d]*$")


def _normalize_symbol(raw: str) -> str:
    raw = raw.strip().upper()
    m = _SYMBOL_NORMALIZER.match(raw)
    return m.group(1) if m else raw


def _parse_mt5_datetime(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y.%m.%d %H:%M:%S")


def _direction_from_type(t: str) -> str:
    t = t.strip().lower()
    return "LONG" if t == "buy" else "SHORT"


# ---------------------------------------------------------------------------
# HTML parser (stdlib, sem JS execution)
# ---------------------------------------------------------------------------
class _MT5HTMLTableExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._current_row: list[str] = []
        self._current_cell: list[str] = []
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._in_script = True
            return
        if tag == "table":
            self._in_table = True
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._current_cell = []

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
            return
        if tag == "table":
            self._in_table = False
        elif tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_row:
                self.rows.append(self._current_row)
        elif tag in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._current_row.append("".join(self._current_cell).strip())

    def handle_data(self, data):
        if self._in_script:
            return  # ignora qualquer conteudo dentro de script — qa-sec
        if self._in_cell:
            self._current_cell.append(data)


def parse_html(content: str) -> list[ParsedTrade]:
    """Parseia relatorio HTML do MT5 (Reports → Save as HTML)."""
    parser = _MT5HTMLTableExtractor()
    parser.feed(content)
    return _rows_to_trades(parser.rows)


def parse_csv(content: str) -> list[ParsedTrade]:
    """Parseia relatorio CSV do MT5."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    return _rows_to_trades(rows)


def parse_xml(content: str) -> list[ParsedTrade]:
    """Parseia relatorio XML do MT5 — stub minimo."""
    # Implementacao xml.etree.ElementTree em TASK futura — v0.2.1 prioriza HTML/CSV
    return []


def _rows_to_trades(rows: list[list[str]]) -> list[ParsedTrade]:
    """Converte linhas tabulares (HTML <tr> ou CSV) em ParsedTrades validos."""
    trades: list[ParsedTrade] = []
    if not rows:
        return trades

    # Identifica cabecalho — heuristica: linha que contem "Time" e "Symbol"
    header_idx = -1
    for i, row in enumerate(rows):
        cells = [c.lower() for c in row]
        if "time" in cells and "symbol" in cells:
            header_idx = i
            break
    if header_idx < 0:
        return trades

    for row in rows[header_idx + 1:]:
        if len(row) < 12:
            continue
        try:
            trade = ParsedTrade(
                open_time=_parse_mt5_datetime(row[0]),
                symbol=_normalize_symbol(row[1]),
                direction=_direction_from_type(row[2]),
                contracts=int(row[3]),
                entry_price=Decimal(row[4]),
                stop_loss=Decimal(row[5]) if row[5] else None,
                take_profit=Decimal(row[6]) if row[6] else None,
                close_time=_parse_mt5_datetime(row[7]),
                exit_price=Decimal(row[8]),
                commission=Decimal(row[9]),
                swap=Decimal(row[10]),
                profit=Decimal(row[11]),
            )
            trades.append(trade)
        except (ValueError, IndexError, KeyError):
            # qa-sec: linha invalida nao derruba o parser inteiro
            continue
    return trades


# ---------------------------------------------------------------------------
# Deduplicacao
# ---------------------------------------------------------------------------
def compute_trade_hash(trade: ParsedTrade) -> str:
    """SHA-256 dos campos canonicos para deteccao de duplicata (SPEC R15.02)."""
    canonical = (
        f"{trade.open_time.isoformat()}|{trade.symbol}|{trade.direction}|"
        f"{trade.contracts}|{trade.entry_price}|{trade.exit_price}"
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def deduplicate(
    candidates: Iterable[ParsedTrade], existing_hashes: set[str]
) -> list[ParsedTrade]:
    """Retorna apenas os trades cujo hash nao esta em existing_hashes."""
    out = []
    seen = set(existing_hashes)
    for t in candidates:
        h = compute_trade_hash(t)
        if h in seen:
            continue
        seen.add(h)
        out.append(t)
    return out

"""
Registro de estratégias do StrategyLab — catálogo + despacho (puro, zero I/O).

Onda 1 expõe D1 (ORB-30) fim-a-fim. As demais (D2/D3/V1/V2/S1/S2/LS1/LS2/LS3)
entram nas Ondas 2-5 — listadas como `runnable=False` até terem o par
Python+MQL5 escrito e a paridade verde (ADR-SL-01).

`param_space` alimenta o otimizador on-demand (sugere, não aplica — R-05/R-08).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from cam._shared.research_kernel.bars import Bar
from cam.features.strategy_lab.backtest_engine import run_d1_backtest
from cam.features.strategy_lab.domain import LegTrade, Unit
from cam.features.strategy_lab.strategies.d1_orb30 import D1Params, generate_signals


@dataclass(frozen=True)
class StrategyDef:
    id: str
    name: str
    unit: Unit
    timeframe: str
    description: str
    default_params: dict
    param_space: dict[str, list] = field(default_factory=dict)
    runnable: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit.value,
            "timeframe": self.timeframe,
            "description": self.description,
            "default_params": self.default_params,
            "param_space": self.param_space,
            "runnable": self.runnable,
        }


# --- catálogo (Onda 1: só D1 runnable) ------------------------------------- #
_D1 = StrategyDef(
    id="D1",
    name="ORB-30 (Opening Range Breakout)",
    unit=Unit.SINGLE,
    timeframe="M1",
    description=(
        "Quebra do range dos primeiros 30 min do pregão; entrada na quebra com "
        "SL e TP ESTÁTICOS em pontos (relativos à entrada); flat no fim da sessão."
    ),
    # Modo estático por padrão (SL/TP fixos em pontos). Para WIN, 1 ponto do
    # índice; ajuste stop_points/target_points conforme o ativo/risco.
    default_params={"or_minutes": 30, "stop_points": 200.0, "target_points": 400.0},
    param_space={
        "or_minutes": [15, 30],
        "stop_points": [100.0, 150.0, 200.0, 300.0],
        "target_points": [200.0, 300.0, 400.0, 600.0],
    },
    runnable=True,
)

_CATALOG: dict[str, StrategyDef] = {
    _D1.id: _D1,
    # Ondas 2-5 (ainda sem par MQL5 + paridade) — listadas, não-runnable:
    "D2": StrategyDef("D2", "Pullback de tendência (intraday)", Unit.SINGLE,
                      "M1", "Reentrada a favor da tendência após pullback.",
                      {}, {}, runnable=False),
    "D3": StrategyDef("D3", "Long-short de par (spread intraday)", Unit.PAIR,
                      "M1", "Spread WIN×WDO; par como unidade.",
                      {}, {}, runnable=False),
    "V1": StrategyDef("V1", "Reversão à média (banda)", Unit.SINGLE,
                      "M1", "Compra/venda no extremo da banda.",
                      {}, {}, runnable=False),
    "V2": StrategyDef("V2", "Fade de exaustão", Unit.SINGLE,
                      "M1", "Reverte movimento esticado.",
                      {}, {}, runnable=False),
    "S1": StrategyDef("S1", "Cesta de momentum (swing)", Unit.BASKET,
                      "D1", "Cesta ranqueada por momentum.",
                      {}, {}, runnable=False),
    "S2": StrategyDef("S2", "Breakout de canal (swing)", Unit.SINGLE,
                      "D1", "Rompimento de canal de N dias.",
                      {}, {}, runnable=False),
    "LS1": StrategyDef("LS1", "Long-short setorial", Unit.PAIR,
                       "D1", "Par long/short dentro de setor.",
                       {}, {}, runnable=False),
    "LS2": StrategyDef("LS2", "Long-short por cointegração", Unit.PAIR,
                       "D1", "Par cointegrado; reversão do spread.",
                       {}, {}, runnable=False),
    "LS3": StrategyDef("LS3", "Long-short de índice×ativo", Unit.PAIR,
                       "D1", "Hedge de beta índice contra ativo.",
                       {}, {}, runnable=False),
}


def list_strategies() -> list[StrategyDef]:
    return list(_CATALOG.values())


def get(strategy_id: str) -> StrategyDef | None:
    return _CATALOG.get(strategy_id.upper())


def _d1_params(params: dict) -> D1Params:
    base = D1Params()
    return D1Params(
        or_minutes=int(params.get("or_minutes", base.or_minutes)),
        target_r=float(params.get("target_r", base.target_r)),
        stop_points=float(params.get("stop_points", base.stop_points)),
        target_points=float(params.get("target_points", base.target_points)),
        session_open=base.session_open,
        session_close=base.session_close,
        entry_until=base.entry_until,
    )


def run(
    strategy_id: str,
    bars: list[Bar],
    params: dict,
    point_value: float,
    qty: int,
) -> list[LegTrade]:
    """
    Despacha o backtest da estratégia sobre as barras (já carregadas). Onda 1:
    só D1. Determinístico; a MESMA rotina serve o otimizador (in-memory).
    """
    sid = strategy_id.upper()
    if sid == "D1":
        p = _d1_params(params)
        signals = generate_signals(bars, p)
        return run_d1_backtest(bars, signals, p, point_value=point_value, qty=qty)
    raise NotImplementedError(
        f"Estratégia '{sid}' ainda não é runnable (Ondas 2-5 — ADR-SL-01)."
    )

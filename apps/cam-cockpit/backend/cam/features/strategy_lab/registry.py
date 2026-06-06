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
from cam.features.strategy_lab.strategies.d2_vwap import D2Params
from cam.features.strategy_lab.strategies.d2_vwap import (
    generate_signals as generate_signals_d2,
)


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
        "Quebra do range dos primeiros 30 min, A FAVOR da tendência (~1 dia); "
        "SL inicial + STOP MÓVEL (trailing); TP fixo opcional; flat na sessão."
    ),
    # Default = CAMPEÃO otimizado pelo Founder no MT5 (volume financeiro) e
    # confirmado no CAM (WINM26 mar-jun): SL 300 (corta perda curta), sem TP,
    # trailing 1000 (deixa o ganho correr), gate de tendência ~5 dias (2500
    # barras M1). Acerto ~38% mas PAYOFF 3.6:1 -> +R$3007 com maxDD só -R$463.
    # Acerto baixo é a assinatura do arquétipo trend; não é defeito (ver D1-ORB30.md).
    default_params={
        "or_minutes": 30, "stop_points": 300.0, "target_points": 0.0,
        "trail_points": 1000.0, "trend_filter_bars": 2500, "min_or_points": 0.0,
    },
    param_space={
        "stop_points": [300.0, 500.0, 700.0],
        "trail_points": [800.0, 1000.0, 1200.0],  # 0 = sem stop móvel
        "trend_filter_bars": [2500, 4000, 5000],  # 0 = sem gate; >2500 melhores
    },
    runnable=True,
)

_D2 = StrategyDef(
    id="D2",
    name="VWAP Mean-Reversion fade (WDO)",
    unit=Unit.SINGLE,
    timeframe="M1",
    description=(
        "Fade da esticada: opera CONTRA quando o preço estica ±k·σ do VWAP da "
        "sessão; alvo no VWAP; stop além de k_stop·σ; sem runner. Múltiplos/dia."
    ),
    # Default = config otimizada pelo Founder no MT5 (volume financeiro, 02/03-05/06):
    # fade a 1σ, stop sigma "largo" (k_stop=30 ≈ desligado, quem protege é o trailing),
    # warmup 170 barras, alvo fixo 300, stop móvel 900. MT5: 78 trades, +R$1500,
    # acerto 75,68%, DD 13,14%. Perna de RECUPERAÇÃO no regime lateral (anti-corr D1).
    default_params={
        "k_entry": 1.0, "k_stop": 30.0, "warmup_bars": 170,
        "stop_points": 0.0, "target_points": 300.0, "trail_points": 900.0,
    },
    param_space={
        "k_entry": [1.0, 1.5, 2.0],
        "k_stop": [3.0, 30.0],                  # 30 ≈ sem stop sigma (trailing protege)
        "warmup_bars": [30, 90, 170],
        "target_points": [200.0, 300.0, 400.0],  # 0 = alvo no VWAP
        "trail_points": [600.0, 900.0, 1200.0],   # 0 = sem stop móvel
    },
    runnable=True,
)

_CATALOG: dict[str, StrategyDef] = {
    _D1.id: _D1,
    _D2.id: _D2,
    # Ondas 2-5 (ainda sem par MQL5 + paridade) — listadas, não-runnable:
    "D3": StrategyDef("D3", "Spread/lead-lag WIN×WDO (par)", Unit.PAIR,
                      "M1", "Spread market-neutral WIN×WDO; par como unidade "
                      "(multi-símbolo — Onda 2).",
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
    # Fallback nos default_params do CATÁLOGO (não nos defaults do dataclass),
    # para que params={} reproduza o default anunciado (gate, trailing etc.).
    params = {**_D1.default_params, **params}
    base = D1Params()
    return D1Params(
        or_minutes=int(params.get("or_minutes", base.or_minutes)),
        target_r=float(params.get("target_r", base.target_r)),
        stop_points=float(params.get("stop_points", base.stop_points)),
        target_points=float(params.get("target_points", base.target_points)),
        trail_points=float(params.get("trail_points", base.trail_points)),
        min_or_points=float(params.get("min_or_points", base.min_or_points)),
        trend_filter_bars=int(params.get("trend_filter_bars", base.trend_filter_bars)),
        session_open=base.session_open,
        session_close=base.session_close,
        entry_until=base.entry_until,
    )


def _d2_params(params: dict) -> D2Params:
    params = {**_D2.default_params, **params}
    base = D2Params()
    return D2Params(
        k_entry=float(params.get("k_entry", base.k_entry)),
        k_stop=float(params.get("k_stop", base.k_stop)),
        warmup_bars=int(params.get("warmup_bars", base.warmup_bars)),
        stop_points=float(params.get("stop_points", base.stop_points)),
        target_points=float(params.get("target_points", base.target_points)),
        trail_points=float(params.get("trail_points", base.trail_points)),
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
    Despacha o backtest da estratégia sobre as barras (já carregadas). Single-
    symbol: D1 (ORB) e D2 (VWAP fade) reusam o MESMO motor (run_d1_backtest é
    agnóstico — consome sinais). Determinístico; a MESMA rotina serve o otimizador.
    """
    sid = strategy_id.upper()
    if sid == "D1":
        p = _d1_params(params)
        signals = generate_signals(bars, p)
        return run_d1_backtest(bars, signals, p, point_value=point_value, qty=qty)
    if sid == "D2":
        p2 = _d2_params(params)
        signals = generate_signals_d2(bars, p2)
        return run_d1_backtest(bars, signals, p2, point_value=point_value, qty=qty)
    raise NotImplementedError(
        f"Estratégia '{sid}' ainda não é runnable (par/multi-símbolo — Onda 2)."
    )

"""
Domínio do Backtest Engine — entidades e value objects.

Restrição constitucional CA7.5: o backtest usa o MESMO Risk Engine do
ambiente live. Impossível rodar com Risk Engine desligado.

Art. 25º: IR 20% provisionado sobre lucros simulados.
Corretagem obrigatória em cada trade.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from cam._shared.domain.primitives import Money, Phase

IR_RATE = Decimal("0.20")


@dataclass
class BacktestConfig:
    """Configuração de uma execução de backtest."""

    strategy_name: str
    date_from: datetime
    date_to: datetime
    phase: Phase
    brokerage_per_contract: Decimal = Decimal("2.50")
    asset: str = "WIN"
    # TASK-008 (BL-A) — tick scanning P&L real
    # point_value: R$ por ponto (WIN=0.20, WDO=10.00).
    # take_profit_points: distância em pontos para TP. None = só SL ou EOD.
    point_value: Decimal = Decimal("0.20")
    take_profit_points: Decimal | None = None


@dataclass
class BacktestTrade:
    """
    Trade simulado. Aplica IR 20% sobre lucros (Art. 25º) e
    desconta corretagem obrigatória.
    """

    asset: str
    direction: str
    contracts: int
    entry_price: Decimal
    exit_price: Decimal
    result_gross: Money
    brokerage: Money
    risk_decision: str = "APPROVED"
    timestamp: datetime | None = None

    @property
    def tax_provisioned(self) -> Money:
        """IR 20% apenas sobre lucro (Art. 25º). Zero em perda."""
        if self.result_gross.amount > 0:
            return Money(self.result_gross.amount * IR_RATE)
        return Money(Decimal("0.00"))

    @property
    def result_net(self) -> Money:
        """Resultado líquido = bruto - corretagem - IR provisionado."""
        return Money(
            self.result_gross.amount
            - self.brokerage.amount
            - self.tax_provisioned.amount
        )


@dataclass
class BacktestMetrics:
    """Métricas agregadas de um conjunto de trades simulados."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl_gross: Money
    total_pnl_net: Money
    max_drawdown: Money
    sharpe_ratio: Decimal
    win_rate: Decimal
    profit_factor: Decimal

    @classmethod
    def compute(cls, trades: list["BacktestTrade"]) -> "BacktestMetrics":
        """Calcula métricas a partir da lista de trades simulados."""
        if not trades:
            zero = Money(Decimal("0.00"))
            return cls(
                0, 0, 0, zero, zero, zero,
                Decimal("0"), Decimal("0"), Decimal("0"),
            )

        wins = [t for t in trades if t.result_net.amount > 0]
        losses = [t for t in trades if t.result_net.amount <= 0]

        gross = sum((t.result_gross.amount for t in trades), Decimal("0"))
        net = sum((t.result_net.amount for t in trades), Decimal("0"))
        win_net = sum((t.result_net.amount for t in wins), Decimal("0"))
        loss_net = abs(sum((t.result_net.amount for t in losses), Decimal("0")))

        # Equity curve para cálculo de max drawdown
        equity = Decimal("0")
        peak = Decimal("0")
        max_dd = Decimal("0")
        for t in trades:
            equity += t.result_net.amount
            if equity > peak:
                peak = equity
            dd = peak - equity
            if dd > max_dd:
                max_dd = dd

        pf = (win_net / loss_net) if loss_net > 0 else Decimal("999")
        wr = Decimal(len(wins)) / Decimal(len(trades)) if trades else Decimal("0")

        # T-TD-012 (SPEC v0.3) — Sharpe Ratio real
        # Sharpe = (retorno_medio - rf) / stddev_retornos
        # rf (risk-free rate): CDI diario configuravel, default 0
        sharpe = Decimal("0")
        if len(trades) > 1:
            from cam._shared.config import settings as _cam_settings
            returns = [t.result_net.amount for t in trades]
            mean_ret = sum(returns, Decimal("0")) / Decimal(len(returns))
            cdi_daily = Decimal(str(getattr(_cam_settings, "cdi_daily_rate", 0)))
            variance = sum(
                ((r - mean_ret) ** 2 for r in returns), Decimal("0")
            ) / Decimal(len(returns) - 1)
            if variance > 0:
                # sqrt manual (Decimal nao tem sqrt nativo)
                stddev = Decimal(str(float(variance) ** 0.5))
                if stddev > 0:
                    sharpe = (mean_ret - cdi_daily) / stddev

        return cls(
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            total_pnl_gross=Money(gross),
            total_pnl_net=Money(net),
            max_drawdown=Money(max_dd),
            sharpe_ratio=sharpe,
            win_rate=wr,
            profit_factor=pf,
        )


@dataclass
class BacktestRun:
    """Execução completa de um backtest."""

    id: str
    config: BacktestConfig
    trades: list[BacktestTrade] = field(default_factory=list)
    status: str = "PENDING"  # PENDING | RUNNING | COMPLETED | FAILED

    @property
    def metrics(self) -> BacktestMetrics:
        """Métricas calculadas a partir dos trades registrados."""
        return BacktestMetrics.compute(self.trades)

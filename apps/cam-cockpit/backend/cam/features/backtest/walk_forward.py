"""
Walk-Forward Analysis para o Backtest Engine.

Divide a série histórica em janelas de otimização e validação
para evitar overfitting de parâmetros de estratégia.

Implementação atual: janela única (single-pass).
Walk-forward multi-janela planejado para T-H07.
"""
from dataclasses import dataclass


@dataclass
class WalkForwardRunner:
    """
    Divide ticks em janela de otimização e validação.

    Atributos:
        optimization_pct: fração da série usada para otimização (padrão 70%)
        validation_pct: fração reservada para validação out-of-sample (padrão 30%)
    """

    optimization_pct: float = 0.7
    validation_pct: float = 0.3

    def split(self, ticks: list) -> list[tuple[list, list]]:
        """
        Divide a série de ticks em janelas (otimização, validação).

        Implementação atual: janela única.
        Walk-forward com múltiplas janelas deslizantes: T-H07.

        Args:
            ticks: série histórica completa de ticks

        Returns:
            Lista de tuplas (optimization_ticks, validation_ticks).
            Atualmente retorna sempre uma única tupla.
        """
        n = len(ticks)
        opt_end = int(n * self.optimization_pct)
        return [(ticks[:opt_end], ticks[opt_end:])]

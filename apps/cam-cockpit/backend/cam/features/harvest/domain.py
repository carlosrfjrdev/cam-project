"""
Domínio da feature harvest — Arts. 21º, 22º da Constituição.

Harvest Rule: distribuição mensal do lucro líquido pós-fiscal.
- 60% → Carteira Hard
- 40% → Buffer Operacional (até linha de base R$ 1.000)
- Após buffer restaurado: 100% excedente → Carteira Hard

Sangria do Bucket Derivativo: disparada quando bucket ≥ R$ 4.500.
- Excedente = bucket_atual - R$ 3.000 (base)
- 80% → Carteira Hard
- 20% → Buffer

REGRA FUNDAMENTAL: Harvest não é automático.
O sistema PROPÕE — execução requer gate Founder (R4.07).
"""
from dataclasses import dataclass
from decimal import Decimal

from cam._shared.domain.primitives import Money

# Percentuais do Harvest Rule (Art. 21º)
HARVEST_CARTEIRA_HARD_PCT = Decimal("0.60")
HARVEST_BUFFER_PCT = Decimal("0.40")

# Thresholds do Bucket Derivativo (Art. 22º)
SANGRIA_TRIGGER = Decimal("4500.00")       # gatilho de sangria
BUCKET_BASELINE = Decimal("3000.00")       # base do bucket derivativo
BUFFER_BASELINE = Decimal("1000.00")       # linha de base do buffer operacional

# Percentuais da Sangria (Art. 22º)
SANGRIA_CARTEIRA_HARD_PCT = Decimal("0.80")
SANGRIA_BUFFER_PCT = Decimal("0.20")


@dataclass
class HarvestProposal:
    """
    Proposta de distribuição mensal (Harvest Rule).

    Gerada pelo sistema — nunca executada automaticamente.
    Requer aprovação explícita do Founder (R4.07).
    """

    net_monthly_profit: Money
    carteira_hard_amount: Money
    buffer_amount: Money


@dataclass
class SangriaResult:
    """
    Resultado de uma sangria do Bucket Derivativo.

    Gerada quando bucket_derivativo ≥ R$ 4.500.
    """

    excess: Money
    carteira_hard_amount: Money
    buffer_amount: Money


class HarvestCalculator:
    """
    Calcula a proposta de harvest mensal.

    Regras:
    1. Buffer abaixo da baseline (R$ 1.000): 40% vai para buffer, 60% para Carteira Hard
    2. Buffer na ou acima da baseline: 100% vai para Carteira Hard
    3. Se 40% > valor necessário para completar buffer: excedente vai para Carteira Hard
    """

    def __init__(
        self,
        net_monthly_profit: Money,
        buffer_current: Money,
        buffer_baseline: Money,
    ) -> None:
        self.profit = net_monthly_profit
        self.buffer_current = buffer_current
        self.buffer_baseline = buffer_baseline

    def calculate(self) -> HarvestProposal:
        """
        Calcula a proposta de distribuição.

        Não executa — apenas propõe. Gate Founder obrigatório (R4.07).
        """
        buffer_needed = max(
            Decimal("0"),
            self.buffer_baseline.amount - self.buffer_current.amount,
        )

        if buffer_needed <= Decimal("0"):
            # Buffer na baseline ou acima → 100% para Carteira Hard
            return HarvestProposal(
                net_monthly_profit=self.profit,
                carteira_hard_amount=Money(self.profit.amount),
                buffer_amount=Money(Decimal("0.00")),
            )

        # Calcula quanto iria para o buffer pela regra 40%
        buffer_pct = self.profit.amount * HARVEST_BUFFER_PCT

        # Buffer recebe apenas o necessário, limitado ao percentual de 40%
        actual_buffer = min(buffer_pct, buffer_needed)
        actual_carteira = self.profit.amount - actual_buffer

        return HarvestProposal(
            net_monthly_profit=self.profit,
            carteira_hard_amount=Money(actual_carteira),
            buffer_amount=Money(actual_buffer),
        )


class SangriaCalculator:
    """
    Calcula a sangria do Bucket Derivativo.

    Gatilho: bucket_atual >= R$ 4.500.
    Excedente = bucket_atual - baseline (R$ 3.000).
    """

    def __init__(
        self,
        bucket_derivativo_current: Money,
        bucket_derivativo_baseline: Money,
    ) -> None:
        self.current = bucket_derivativo_current
        self.baseline = bucket_derivativo_baseline

    def calculate(self) -> SangriaResult | None:
        """
        Calcula a sangria.

        Retorna None se o bucket não atingiu o gatilho de R$ 4.500.
        Retorna SangriaResult com os valores a redistribuir.
        """
        if self.current.amount < SANGRIA_TRIGGER:
            return None

        excess = Money(self.current.amount - self.baseline.amount)
        return SangriaResult(
            excess=excess,
            carteira_hard_amount=Money(excess.amount * SANGRIA_CARTEIRA_HARD_PCT),
            buffer_amount=Money(excess.amount * SANGRIA_BUFFER_PCT),
        )

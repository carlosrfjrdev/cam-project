"""
Domínio da feature fiscal — Arts. 24º, 25º, 26º, 27º da Constituição.

Regras fiscais:
- IR Day Trade: 20% sobre lucro mensal líquido (Art. 24º)
- IRRF: 1% retido na fonte como antecipação — deduzido do DARF
- DARF com status OVERDUE → tax_compliance=False → Risk Engine bloqueia (Art. 26º)
- Compensação de prejuízo: saldo negativo acumulado deduz base de cálculo (Art. 27º)
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from cam._shared.domain.primitives import Money

# IR Day Trade — Art. 24º
IR_DAY_TRADE_RATE = Decimal("0.20")


class DarfStatus(StrEnum):
    """Status de uma DARF."""

    PENDING = "PENDING"    # Gerada, aguarda pagamento
    PAID = "PAID"          # Paga — compliance OK
    OVERDUE = "OVERDUE"    # Não paga após vencimento — bloqueia operações (Art. 26º)


@dataclass
class FiscalApuration:
    """
    Apuração fiscal mensal de Day Trade.

    Calcula:
    - net_result: resultado bruto - custos
    - taxable_base: net_result - compensação de prejuízo (nunca negativo)
    - ir_due: 20% da taxable_base (quando positivo)
    - darf_value: ir_due - irrf_retained (nunca negativo)
    """

    month: str
    gross_result: Money
    costs: Money
    irrf_retained: Money
    loss_compensation: Money

    @property
    def net_result(self) -> Money:
        """Resultado líquido de custos (antes do IR)."""
        return Money(self.gross_result.amount - self.costs.amount)

    @property
    def taxable_base(self) -> Money:
        """
        Base tributável.

        = net_result - loss_compensation
        Nunca negativa — compensação não gera crédito (mínimo zero).
        """
        base = self.net_result.amount - self.loss_compensation.amount
        return Money(max(Decimal("0.00"), base))

    @property
    def ir_due(self) -> Money:
        """
        IR devido no mês.

        20% da taxable_base quando net_result > 0.
        Zero quando há resultado negativo (Art. 24º — IR Day Trade).
        """
        if self.net_result.amount <= Decimal("0"):
            return Money(Decimal("0.00"))
        return Money(self.taxable_base.amount * IR_DAY_TRADE_RATE)

    @property
    def darf_value(self) -> Money:
        """
        Valor da DARF a pagar.

        = ir_due - irrf_retained
        Nunca negativa — IRRF maior que IR = crédito para próximo mês
        (simplificação para Fase 0).
        """
        value = self.ir_due.amount - self.irrf_retained.amount
        return Money(max(Decimal("0.00"), value))


@dataclass
class Darf:
    """
    Guia DARF mensal.

    Status OVERDUE → tax_compliance=False → Risk Engine bloqueia (Art. 26º).
    """

    month: str
    value: Money
    due_date: str
    status: DarfStatus = DarfStatus.PENDING
    paid_at: str | None = None

    def is_compliant(self) -> bool:
        """
        Retorna False se DARF está OVERDUE (Art. 26º).

        PENDING e PAID são considerados compliance.
        """
        return self.status != DarfStatus.OVERDUE


@dataclass
class LossCompensation:
    """
    Saldo compensável de prejuízo (Art. 27º).

    Acumulado de resultados negativos que pode ser deduzido
    da base de cálculo do IR nos meses seguintes.
    """

    accumulated_loss: Money  # sempre positivo (representa o valor do prejuízo)
    reference_month: str

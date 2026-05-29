"""
Domínio da feature journal — Art. 25º e 31º da Constituição.

JournalEntry é a unidade básica de registro operacional.
Toda operação executada DEVE ter um JournalEntry correspondente (Art. 31º).

Regras de cálculo:
- imposto_provisionado = 20% do resultado_bruto QUANDO positivo; 0 quando negativo
- resultado_liquido = resultado_bruto - custos - imposto_provisionado

Art. 25º: resultado_liquido é sempre calculado e exposto — nunca apenas o bruto.
"""
from dataclasses import dataclass
from decimal import Decimal

from cam._shared.domain.primitives import Money

# IR Day Trade: 20% sobre lucro bruto (Art. 24º da Constituição)
IR_DAY_TRADE_RATE = Decimal("0.20")


@dataclass
class JournalEntry:
    """
    Registro de uma operação executada.

    Uma vez criado, é imutável — sem UPDATE nem DELETE.
    Correções são registradas via JournalCorrection com referência ao entry original.
    """

    asset: str                      # WIN | WDO
    direction: str                  # LONG | SHORT
    contracts: int
    entry_price: Decimal
    exit_price: Decimal
    result_gross: Money
    costs: Money
    strategy: str
    setup: str
    adherence: str | None = None   # aderencia às regras
    emotional_note: str | None = None
    lesson: str | None = None
    source: str = "MANUAL"         # MANUAL | CSV_IMPORT | NTSL_CALLBACK

    @property
    def tax_provisioned(self) -> Money:
        """
        IR provisionado sobre o resultado bruto.

        20% quando resultado_bruto > 0 (Day Trade — Art. 24º).
        0 quando resultado_bruto <= 0 (sem IR em loss).
        """
        if self.result_gross.amount > Decimal("0"):
            return Money(self.result_gross.amount * IR_DAY_TRADE_RATE)
        return Money(Decimal("0.00"))

    @property
    def result_net(self) -> Money:
        """
        Resultado líquido da operação — Art. 25º.

        resultado_liquido = resultado_bruto - custos - imposto_provisionado

        Este campo SEMPRE deve ser exibido junto ao resultado_bruto.
        Exibir apenas o bruto é violação do Art. 25º.
        """
        return Money(
            self.result_gross.amount
            - self.costs.amount
            - self.tax_provisioned.amount
        )


@dataclass
class JournalCorrection:
    """
    Correção de um JournalEntry com erro.

    Registrada como novo registro com referência ao original.
    O entry original permanece imutável (Art. 31º — audit trail).
    """

    original_entry_id: str
    correction_reason: str
    corrected_fields: dict


class JournalSource:
    """Fontes possíveis de um JournalEntry."""

    MANUAL = "MANUAL"
    CSV_IMPORT = "CSV_IMPORT"
    NTSL_CALLBACK = "NTSL_CALLBACK"

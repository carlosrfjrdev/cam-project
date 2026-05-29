"""
Primitivas de domínio transversais do CaM.

Estas classes são o vocabulário compartilhado entre o Risk Engine e as features.
Residem no Shared Kernel porque são utilizadas por 3+ features e pelo Risk Engine
(mandato constitucional — ADR-013).

Zero dependência de I/O — Pure Python apenas.
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class AssetType(StrEnum):
    """Ativos negociáveis no CaM. Art. 11 limita a 2 contratos de cada."""

    WIN = "WIN"  # Mini Índice Bovespa
    WDO = "WDO"  # Mini Dólar


class Direction(StrEnum):
    """Direção da operação."""

    LONG = "LONG"
    SHORT = "SHORT"


class Phase(StrEnum):
    """
    Fase operacional do CaM. Determina limites de contratos e regras de operação.
    Referência: Constituição Anexo II.
    """

    FASE_0 = "FASE_0"  # Construção — sem trade real
    FASE_1 = "FASE_1"  # Paper Trading
    FASE_2 = "FASE_2"  # 1 contrato
    FASE_3 = "FASE_3"  # 2 contratos (consolidação)
    FASE_4 = "FASE_4"  # 2 contratos (Setup A+)


@dataclass(frozen=True)
class Money:
    """
    Value object monetário. Imutável. Sempre em BRL por padrão.

    O CaM exige que resultados operacionais sejam expressos em Money
    para garantir que aritmética de Decimal seja usada (sem float).
    """

    amount: Decimal
    currency: str = "BRL"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Moedas incompatíveis: {self.currency} != {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Moedas incompatíveis: {self.currency} != {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        return Money(self.amount * factor, self.currency)

    def __lt__(self, other: "Money") -> bool:
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        return self.amount >= other.amount

    def is_positive(self) -> bool:
        return self.amount > Decimal("0")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0")

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    @classmethod
    def zero(cls) -> "Money":
        return cls(Decimal("0"))

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency})"


@dataclass(frozen=True)
class ContractCount:
    """
    Value object para quantidade de contratos. Nunca negativo.
    Art. 11: máximo absoluto de 2 WIN / 2 WDO — enforçado no Risk Engine.
    """

    value: int

    def __post_init__(self) -> None:
        assert self.value >= 0, f"ContractCount não pode ser negativo: {self.value}"

    def __add__(self, other: "ContractCount") -> "ContractCount":
        return ContractCount(self.value + other.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContractCount):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __le__(self, other: "ContractCount") -> bool:
        return self.value <= other.value

    def __lt__(self, other: "ContractCount") -> bool:
        return self.value < other.value

    def __gt__(self, other: "ContractCount") -> bool:
        return self.value > other.value

    def __ge__(self, other: "ContractCount") -> bool:
        return self.value >= other.value

    def __repr__(self) -> str:
        return f"ContractCount({self.value})"


@dataclass(frozen=True)
class OpenPosition:
    """Representa uma posição aberta no momento da validação pelo Risk Engine."""

    asset: AssetType
    contracts: ContractCount
    direction: Direction
    entry_price: Decimal

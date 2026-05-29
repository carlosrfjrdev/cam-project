"""
Domínio da feature profit_integration.

Entidades e value objects para F1 (validação de intenção)
e F2 (importação de CSV do Profit).

Art. 35º: este módulo NÃO contém código de envio de ordem.
A IA nunca envia ordens — apenas valida a intenção do operador.
"""
from dataclasses import dataclass


@dataclass
class IntentionValidationResult:
    """
    Resultado da validação de intenção pelo Risk Engine (F1).

    decision: "APPROVED" | "REJECTED"
    reason: motivo da rejeição (None se aprovado)
    validator: nome do validador que rejeitou (None se aprovado)
    """

    decision: str
    reason: str | None = None
    validator: str | None = None

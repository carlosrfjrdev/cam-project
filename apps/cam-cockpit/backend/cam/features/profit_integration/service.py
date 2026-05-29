"""
Lógica de aplicação da feature profit_integration.

F1 — Validação de intenção:
    Recebe intenção do operador → chama Risk Engine → retorna decisão.
    Art. 35º: esta feature NÃO envia ordens. Apenas valida a intenção.
    Toda intenção passa pelo Risk Engine (Art. 15º).

F2 — Importação CSV:
    Ver csv_importer.py e reconciliation.py.
"""
from decimal import Decimal

from cam._shared.domain.primitives import AssetType, ContractCount, Direction
from cam._shared.risk import Approved, OrderCandidate
from cam._shared.risk import validate as risk_validate


class ProfitIntegrationService:
    """
    Service principal da integração com Profit/Nelogica.

    Em F1, opera como gateway de validação: operador declara intenção,
    Risk Engine decide. Nenhuma ordem é enviada automaticamente (Art. 35º).
    """

    def __init__(self, risk_engine=None):
        # risk_engine é injetável para testes; em produção usa o módulo risk
        # O parâmetro é aceito mas o engine canônico é sempre o módulo _shared.risk
        # (mantido para compatibilidade com assinatura de teste)
        self._risk_engine = risk_engine

    async def validate_intention(
        self,
        asset: str,
        direction: str,
        contracts: int,
        intended_stop_points: Decimal,
        risk_context_builder,
    ) -> dict:
        """
        Valida a intenção de operação contra o Risk Engine.

        Parâmetros:
            asset: "WIN" | "WDO"
            direction: "LONG" | "SHORT"
            contracts: número de contratos pretendidos
            intended_stop_points: stop loss pretendido em pontos
            risk_context_builder: callable que retorna RiskContext populado

        Retorna:
            {"decision": "APPROVED"|"REJECTED", "reason": str|None,
             "validator": str|None}

        Art. 15º: Risk Engine bloqueia? CaM não opera. Sem exceções.
        Art. 35º: IA não envia ordem — apenas valida.
        """
        candidate = OrderCandidate(
            asset=AssetType(asset),
            direction=Direction(direction),
            contracts=ContractCount(contracts),
            intended_stop_loss_points=intended_stop_points,
        )
        context = risk_context_builder()

        # Usa engine injetado (testes) ou o módulo canônico (produção)
        if self._risk_engine is not None:
            result = self._risk_engine.validate(candidate, context)
        else:
            result = risk_validate(candidate, context)

        if isinstance(result, Approved):
            return {"decision": "APPROVED", "reason": None, "validator": None}

        return {
            "decision": "REJECTED",
            "reason": result.reason,
            "validator": result.validator,
        }

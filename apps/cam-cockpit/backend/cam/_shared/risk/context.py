"""
Tipos de entrada do Risk Engine: OrderCandidate e RiskContext.

O chamador (service da feature) é responsável por construir o RiskContext
consultando o banco de dados antes de chamar o engine. O engine em si
é Pure Python — Zero I/O.
"""
from dataclasses import dataclass, field
from datetime import time
from decimal import Decimal

from cam._shared.domain.primitives import (
    AssetType,
    ContractCount,
    Direction,
    Money,
    OpenPosition,
    Phase,
)


@dataclass(frozen=True)
class OrderCandidate:
    """
    Candidato a operação que será submetido ao pipeline de validators.

    Todos os campos são imutáveis. O candidato descreve a intenção
    antes de qualquer validação.
    """

    asset: AssetType
    direction: Direction
    contracts: ContractCount
    intended_stop_loss_points: Decimal
    is_setup_a_plus: bool = False


@dataclass
class RiskContext:
    """
    Snapshot do estado do sistema no momento da validação.

    O CHAMADOR (service da feature) é responsável por:
    - Ler o estado do banco de dados
    - Construir este objeto com dados atualizados
    - Passar para validate()

    O Risk Engine nunca lê banco, nunca faz I/O. Toda informação
    chega via este objeto.

    Campos:
        kill_switch_active: kill switch manual/automático ativado (Art. 18º)
        phase: fase operacional atual do CaM (Anexo II)
        pre_market_checklist_done: checklist pré-mercado do dia preenchido (Art. 32º)
        post_market_checklist_done: checklist pós-mercado do pregão anterior (Art. 33º)
        tax_compliance_ok: False se DARF atrasada (Art. 26º)
        total_capital: capital total declarado (R$ 5.000 na Fase 0)
        daily_pnl: P&L líquido do dia (negativo = loss)
        weekly_pnl: P&L líquido da semana
        monthly_pnl: P&L líquido do mês
        daily_operations_count: operações já executadas hoje
        last_operation_result: resultado da última operação (Art. 13º — anti-martingale)
        last_operation_contracts: contratos da última op (comparação anti-martingale)
        open_positions: posições abertas no momento da validação
        strategy_authorized_for_phase: estratégia autorizada na fase atual (Art. 30º)
        circuit_breaker_triggered: circuit breaker configurável (padrão off)
        current_time: horário atual p/ verificação de janelas vedadas (None = pula)
    """

    # Estado do sistema
    kill_switch_active: bool
    phase: Phase

    # Checklists do dia
    pre_market_checklist_done: bool
    post_market_checklist_done: bool

    # Compliance fiscal (Art. 26º)
    tax_compliance_ok: bool

    # Capital e limites
    total_capital: Money
    daily_pnl: Money
    weekly_pnl: Money
    monthly_pnl: Money

    # Operações do dia
    daily_operations_count: int
    last_operation_result: Money | None
    last_operation_contracts: ContractCount | None

    # Posições abertas
    open_positions: list[OpenPosition] = field(default_factory=list)

    # Autorização de fase
    strategy_authorized_for_phase: bool = True

    # Circuit breaker
    circuit_breaker_triggered: bool = False

    # Janela de negociação (None = não verifica — modo teste)
    current_time: time | None = None

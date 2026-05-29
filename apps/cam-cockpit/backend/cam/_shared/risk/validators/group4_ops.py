"""
Grupo 4 — Regras Operacionais (posições 13–17 do pipeline).

Validators que verificam regras operacionais específicas: contagem diária,
anti-martingale, janelas de negociação, restrições de setup e circuit breaker.

Artigos constitucionais cobertos:
    Art. 13º — Proibição de Martingale
    Art. 20º — Limite de operações por dia
    POV v1.0 — Janelas vedadas (primeiros 15min, últimos 10min)

HORÁRIOS DE FECHAMENTO B3 (constantes — não configuráveis):
    WIN (Mini Índice): fechamento do contrato regular às 17:50
    WDO (Mini Dólar): fechamento às 18:15

Zero I/O — Pure Python.
"""
from datetime import time

from cam._shared.domain.primitives import AssetType, Phase
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, Rejected, RiskDecision

# Limite de operações por fase (Art. 20º)
_PHASE_MAX_OPERATIONS: dict[Phase, int] = {
    Phase.FASE_0: 0,  # sem trade real na construção
    Phase.FASE_1: 3,
    Phase.FASE_2: 3,
    Phase.FASE_3: 5,
    Phase.FASE_4: 5,
}

# Janelas vedadas de negociação (POV v1.0 — não configuráveis)
# Abertura B3: ambos os ativos
_OPENING_BLACKOUT_START = time(9, 0)   # 09:00 (abertura B3)
_OPENING_BLACKOUT_END = time(9, 15)    # 09:15 (fim dos primeiros 15min)

# Fechamento WIN (Mini Índice Regular) — 17:50
_WIN_CLOSING_BLACKOUT_START = time(17, 40)  # 10min antes de 17:50
_WIN_CLOSING_BLACKOUT_END = time(17, 50)

# Fechamento WDO (Mini Dólar) — 18:15
_WDO_CLOSING_BLACKOUT_START = time(18, 5)   # 10min antes de 18:15
_WDO_CLOSING_BLACKOUT_END = time(18, 15)

# Fases onde 2 contratos exigem Setup A+ confirmado
_SETUP_A_PLUS_REQUIRED_PHASES: frozenset[Phase] = frozenset({Phase.FASE_4})
_SETUP_A_PLUS_CONTRACT_THRESHOLD = 2


def daily_operations_count_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 13 — Art. 20º.

    Limita o número máximo de operações por dia por fase.
    Fases 1 e 2: máximo 3 operações.
    Fases 3 e 4: máximo 5 operações.

    daily_operations_count representa o número de operações JÁ completadas.
    Se já está no limite, a próxima é bloqueada.
    """
    phase_max = _PHASE_MAX_OPERATIONS.get(context.phase, 3)
    if context.daily_operations_count >= phase_max:
        return Rejected(
            reason=f"Limite de operações diárias atingido (Art. 20º): "
            f"{context.daily_operations_count}/{phase_max} ops na "
            f"{context.phase.value}. Retorne no próximo pregão.",
            validator="daily_operations_count_check",
        )
    return Approved()


def martingale_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 14 — Art. 13º.

    Proibido aumentar quantidade de contratos imediatamente após uma perda.
    Verifica se a última operação teve resultado negativo E o candidato
    quer mais contratos que a última operação.

    Se não há histórico (last_operation_result is None), o validator passa.
    """
    no_last = (
        context.last_operation_result is None
        or context.last_operation_contracts is None
    )
    if no_last:
        return Approved()

    # Só verifica se a última operação foi um loss
    if not context.last_operation_result.is_negative():
        return Approved()

    # Verifica se está tentando aumentar contratos após o loss
    if candidate.contracts > context.last_operation_contracts:
        last_res = context.last_operation_result.amount
        last_qty = context.last_operation_contracts.value
        new_qty = candidate.contracts.value
        return Rejected(
            reason=f"Martingale bloqueado (Art. 13º): última op R$ {last_res:.2f} "
            f"(loss). Tentativa de aumentar {last_qty}→{new_qty} contratos. "
            "Aumento após loss é proibido.",
            validator="martingale_check",
        )
    return Approved()


def trading_window_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 15 — POV v1.0.

    Bloqueia operações em janelas vedadas de negociação:
    - Primeiros 15min após abertura B3 (09:00–09:15)
    - Últimos 10min antes do fechamento WIN (17:40–17:50)
    - Últimos 10min antes do fechamento WDO (18:05–18:15)

    Se current_time é None, o validator pula — permite testes sem horário real.
    Em produção, o chamador deve injetar datetime.now().time().
    """
    if context.current_time is None:
        return Approved()

    t = context.current_time

    # Janela vedada de abertura (ambos os ativos)
    if _OPENING_BLACKOUT_START <= t < _OPENING_BLACKOUT_END:
        start = _OPENING_BLACKOUT_START.strftime("%H:%M")
        end = _OPENING_BLACKOUT_END.strftime("%H:%M")
        return Rejected(
            reason=f"Janela vedada de abertura (POV): {t.strftime('%H:%M')} "
            f"nos primeiros 15min pós-abertura B3 ({start}–{end}). "
            "Aguarde a janela de negociação normal.",
            validator="trading_window_check",
        )

    # Janela vedada de fechamento — específica por ativo
    if candidate.asset == AssetType.WIN:
        if _WIN_CLOSING_BLACKOUT_START <= t < _WIN_CLOSING_BLACKOUT_END:
            start = _WIN_CLOSING_BLACKOUT_START.strftime("%H:%M")
            end = _WIN_CLOSING_BLACKOUT_END.strftime("%H:%M")
            return Rejected(
                reason=f"Janela vedada de fechamento WIN (POV): {t.strftime('%H:%M')} "
                f"nos últimos 10min antes do fechamento ({start}–{end}). "
                "Não abra posição que não poderá ser encerrada.",
                validator="trading_window_check",
            )

    elif candidate.asset == AssetType.WDO:
        if _WDO_CLOSING_BLACKOUT_START <= t < _WDO_CLOSING_BLACKOUT_END:
            start = _WDO_CLOSING_BLACKOUT_START.strftime("%H:%M")
            end = _WDO_CLOSING_BLACKOUT_END.strftime("%H:%M")
            return Rejected(
                reason=f"Janela vedada de fechamento WDO (POV): {t.strftime('%H:%M')} "
                f"nos últimos 10min antes do fechamento ({start}–{end}). "
                "Não abra posição que não poderá ser encerrada.",
                validator="trading_window_check",
            )

    return Approved()


def setup_a_plus_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 16.

    Na Fase 4, operar com 2 contratos requer Setup A+ confirmado.
    Em fases anteriores, phase_contracts_check já bloqueia 2 contratos em F1/F2.
    Na Fase 3, 2 contratos são permitidos sem exigência de Setup A+.
    """
    if (
        context.phase in _SETUP_A_PLUS_REQUIRED_PHASES
        and candidate.contracts.value >= _SETUP_A_PLUS_CONTRACT_THRESHOLD
        and not candidate.is_setup_a_plus
    ):
        qty = candidate.contracts.value
        return Rejected(
            reason=f"Setup A+ obrigatório na {context.phase.value} para "
            f"{qty} contratos. Confirme Setup A+ antes de operar com "
            "2 contratos na Fase 4. 1 contrato não requer Setup A+.",
            validator="setup_a_plus_check",
        )
    return Approved()


def circuit_breaker_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 17 — Circuit breaker configurável.

    Circuit breaker é acionado por condições específicas configuradas
    pelo operador ou pelo sistema. Padrão: desativado (circuit_breaker_triggered=False).

    Quando ativado, bloqueia todas as operações até ser manualmente desativado.
    Diferente do kill switch (Art. 18º), o circuit breaker é temporário e
    pode ser configurado para acionamento automático.
    """
    if context.circuit_breaker_triggered:
        return Rejected(
            reason="Circuit breaker acionado — operações bloqueadas. "
            "Verifique o motivo e desative manualmente após análise.",
            validator="circuit_breaker_check",
        )
    return Approved()

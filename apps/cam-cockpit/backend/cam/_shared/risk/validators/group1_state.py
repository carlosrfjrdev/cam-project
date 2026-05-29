"""
Grupo 1 — Guardas de Estado (posições 1–5 do pipeline).

Validators que verificam o estado global do sistema antes de qualquer
análise de limites ou regras operacionais. São os guardas mais
prioritários: qualquer falha aqui encerra o pipeline imediatamente.

Artigos constitucionais cobertos:
    Art. 18º — Kill Switch
    Art. 26º — Bloqueio por inadimplência fiscal (DARF atrasada)
    Art. 30º — Autorização de estratégia por fase
    Art. 32º — Checklist pré-mercado
    Art. 33º — Checklist pós-mercado

Zero I/O — Pure Python.
"""
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, Rejected, RiskDecision


def kill_switch_active_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 1 — Art. 18º.

    Kill switch ativo bloqueia TUDO, sem exceção, sem análise de contexto.
    Preservar capital é sempre justificativa suficiente (Art. 18º).
    """
    if context.kill_switch_active:
        return Rejected(
            reason="Kill switch ativo — toda operação bloqueada (Art. 18º). "
            "Desative o kill switch explicitamente para retomar.",
            validator="kill_switch_active_check",
        )
    return Approved()


def pre_market_checklist_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 2 — Art. 32º.

    Checklist pré-mercado do dia corrente deve estar preenchido antes
    de qualquer operação. Garante que o operador iniciou o dia com
    revisão de contexto.
    """
    if not context.pre_market_checklist_done:
        return Rejected(
            reason="Checklist pré-mercado do dia não preenchido (Art. 32º). "
            "Preencha o checklist antes de operar.",
            validator="pre_market_checklist_check",
        )
    return Approved()


def post_market_checklist_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 3 — Art. 33º.

    Checklist pós-mercado do pregão anterior deve existir. Garante
    continuidade de auditoria e que o operador fechou o dia anterior
    com registro completo.
    """
    if not context.post_market_checklist_done:
        return Rejected(
            reason="Checklist pós-mercado do pregão anterior ausente (Art. 33º). "
            "Registre o fechamento do pregão anterior antes de operar.",
            validator="post_market_checklist_check",
        )
    return Approved()


def tax_compliance_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 4 — Art. 26º.

    DARF atrasada bloqueia novas operações até regularização.
    Obrigação fiscal não é negociável.
    """
    if not context.tax_compliance_ok:
        return Rejected(
            reason="DARF atrasada — operações bloqueadas até regularização "
            "fiscal (Art. 26º). Regularize a DARF pendente para retomar.",
            validator="tax_compliance_check",
        )
    return Approved()


def phase_authorization_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 5 — Art. 30º.

    A estratégia candidata deve estar autorizada para a fase operacional
    atual. Fases têm perfis de risco e regras distintos.
    """
    if not context.strategy_authorized_for_phase:
        return Rejected(
            reason=f"Estratégia não autorizada para a fase atual "
            f"({context.phase.value}) (Art. 30º). "
            "Valide a estratégia para esta fase antes de operar.",
            validator="phase_authorization_check",
        )
    return Approved()

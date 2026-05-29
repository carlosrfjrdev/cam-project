"""
Grupo 3 — Limites de P&L (posições 9–12 do pipeline).

Validators que verificam limites de perda e ganho do dia, semana e mês.
Todos os limites são calculados como percentual do capital total declarado,
garantindo que escalam automaticamente quando o capital muda.

Artigos constitucionais cobertos:
    Art. 16º — Limites de perda (3% diário, 7% semanal, 15% mensal)
    Art. 17º — Gain Lock (2% de ganho diário encerra o dia)

PERCENTUAIS (POV v1.0 — Anexo III):
    DAILY_LOSS_LIMIT_PCT   = 3%
    WEEKLY_LOSS_LIMIT_PCT  = 7%
    MONTHLY_LOSS_LIMIT_PCT = 15%
    GAIN_LOCK_PCT          = 2%

Os percentuais não são hardcoded como os limites de contratos do Art. 11º,
mas para a implementação atual seguem os valores da POV v1.0. Em versão
futura poderão ser lidos da POV vigente (cam_pov_versions) pelo chamador
e passados via RiskContext.

Zero I/O — Pure Python.
"""
from decimal import Decimal

from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, Rejected, RiskDecision

# Percentuais da POV v1.0 (Anexo III da Constituição)
DAILY_LOSS_LIMIT_PCT: Decimal = Decimal("0.03")    # Art. 16º — 3%
WEEKLY_LOSS_LIMIT_PCT: Decimal = Decimal("0.07")   # Art. 16º — 7%
MONTHLY_LOSS_LIMIT_PCT: Decimal = Decimal("0.15")  # Art. 16º — 15%
GAIN_LOCK_PCT: Decimal = Decimal("0.02")           # Art. 17º — 2%


def daily_loss_limit_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 9 — Art. 16º.

    Se o P&L diário atingir ou ultrapassar -3% do capital total,
    bloqueia novas operações até o próximo pregão.

    O limite é calculado como percentual do capital declarado para
    escalar automaticamente com mudanças de capital.
    """
    limit = context.total_capital.amount * DAILY_LOSS_LIMIT_PCT
    if context.daily_pnl.amount <= -limit:
        pct = DAILY_LOSS_LIMIT_PCT * 100
        return Rejected(
            reason=f"Limite de perda diária atingido (Art. 16º): "
            f"P&L do dia = R$ {context.daily_pnl.amount:.2f} "
            f"(limite = -{pct:.0f}% = R$ -{limit:.2f}). "
            "Operações bloqueadas até o próximo pregão.",
            validator="daily_loss_limit_check",
        )
    return Approved()


def weekly_loss_limit_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 10 — Art. 16º.

    Se o P&L semanal atingir ou ultrapassar -7% do capital total,
    bloqueia novas operações até a próxima segunda-feira.
    """
    limit = context.total_capital.amount * WEEKLY_LOSS_LIMIT_PCT
    if context.weekly_pnl.amount <= -limit:
        pct = WEEKLY_LOSS_LIMIT_PCT * 100
        return Rejected(
            reason=f"Limite de perda semanal atingido (Art. 16º): "
            f"P&L da semana = R$ {context.weekly_pnl.amount:.2f} "
            f"(limite = -{pct:.0f}% = R$ -{limit:.2f}). "
            "Operações bloqueadas até a próxima segunda-feira.",
            validator="weekly_loss_limit_check",
        )
    return Approved()


def monthly_loss_limit_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 11 — Art. 16º.

    Se o P&L mensal atingir ou ultrapassar -15% do capital total,
    congela a fase atual e suspende trade real até revisão formal.

    Este é o limite mais severo — representa uma perda mensal significativa
    que exige intervenção e revisão da estratégia operacional.
    """
    limit = context.total_capital.amount * MONTHLY_LOSS_LIMIT_PCT
    if context.monthly_pnl.amount <= -limit:
        pct = MONTHLY_LOSS_LIMIT_PCT * 100
        return Rejected(
            reason=f"Limite de perda mensal/fase atingido (Art. 16º): "
            f"P&L do mês = R$ {context.monthly_pnl.amount:.2f} "
            f"(limite = -{pct:.0f}% = R$ -{limit:.2f}). "
            "Fase CONGELADA — revisão formal necessária antes de retomar.",
            validator="monthly_loss_limit_check",
        )
    return Approved()


def gain_lock_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 12 — Art. 17º.

    Ao atingir ganho diário de 2% do capital declarado, o CaM encerra o dia.
    Lucro realizado é protegido contra excesso de confiança e overtrade.

    O gain lock é acionado quando daily_pnl >= 2% do capital.
    """
    lock_threshold = context.total_capital.amount * GAIN_LOCK_PCT
    if context.daily_pnl.amount >= lock_threshold:
        pct = GAIN_LOCK_PCT * 100
        return Rejected(
            reason=f"Gain Lock ativado (Art. 17º): "
            f"P&L do dia = R$ {context.daily_pnl.amount:.2f} "
            f"(gain lock = +{pct:.0f}% = R$ +{lock_threshold:.2f}). "
            "Lucro do dia protegido — dia encerrado. Retorne amanhã.",
            validator="gain_lock_check",
        )
    return Approved()

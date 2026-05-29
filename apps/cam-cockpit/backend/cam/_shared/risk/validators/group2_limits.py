"""
Grupo 2 — Limites de Contratos e Posição (posições 6–8 do pipeline).

Validators que verificam limites de quantidade de contratos e
simultaneidade de posições. Cobrem o Art. 11º (absolutamente intocável)
e Art. 12º (regras por fase).

CONSTANTES CONSTITUCIONAIS (Art. 11º — INTOCÁVEL):
    MAX_WIN_CONTRACTS = 2
    MAX_WDO_CONTRACTS = 2

    Estas constantes NUNCA devem ser lidas de banco, config, env ou parâmetro.
    São hardcoded por mandato constitucional. Qualquer tentativa de
    parametrizá-las é violação do Art. 11º.

Artigos constitucionais cobertos:
    Art. 11º — Limite absoluto de contratos (MAX = 2 WIN / 2 WDO)
    Art. 12º — Exposição na fase inicial (máx 1 contrato em F1/F2, sem simultâneo)

Zero I/O — Pure Python.
"""
from cam._shared.domain.primitives import AssetType, Phase
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, Rejected, RiskDecision

# Art. 11º — INTOCÁVEL. Hardcoded. Nunca ler de banco/config/env/parâmetro.
# Mudança exige emenda constitucional formal (Art. 38º).
MAX_WIN_CONTRACTS: int = 2
MAX_WDO_CONTRACTS: int = 2

# Limites de contratos por fase (Art. 12º e Anexo II da Constituição)
# Fase 0: sem trade real (construção) — bloqueado por phase_authorization_check
# Fase 1: paper trading, max 1 contrato por ativo
# Fase 2: primeiro real, max 1 contrato por ativo
# Fase 3: consolidação, max 2 contratos
# Fase 4: escalada com Setup A+, max 2 contratos
_PHASE_MAX_CONTRACTS: dict[Phase, int] = {
    Phase.FASE_0: 0,  # sem trade real na Fase 0
    Phase.FASE_1: 1,
    Phase.FASE_2: 1,
    Phase.FASE_3: 2,
    Phase.FASE_4: 2,
}

# Fases onde WIN+WDO simultâneo é vedado (Art. 12º)
_SIMULTANEOUS_FORBIDDEN_PHASES: frozenset[Phase] = frozenset(
    {Phase.FASE_1, Phase.FASE_2}
)


def max_contracts_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 6 — Art. 11º — INTOCÁVEL.

    Verifica o limite absoluto de contratos: máximo 2 WIN / 2 WDO.
    Este limite NÃO pode ser sobrescrito por nenhuma POV, configuração ou parâmetro.
    Qualquer quantidade > 2 é bloqueada independentemente de qualquer outra condição.
    """
    is_win = candidate.asset == AssetType.WIN
    is_wdo = candidate.asset == AssetType.WDO
    qty = candidate.contracts.value
    if is_win and qty > MAX_WIN_CONTRACTS:
        return Rejected(
            reason=f"Art. 11º VIOLADO: máximo {MAX_WIN_CONTRACTS} contratos WIN. "
            f"Solicitado: {qty}. "
            "Limite absoluto e intocável — não pode ser sobrescrito.",
            validator="max_contracts_check",
        )
    if is_wdo and qty > MAX_WDO_CONTRACTS:
        return Rejected(
            reason=f"Art. 11º VIOLADO: máximo {MAX_WDO_CONTRACTS} contratos WDO. "
            f"Solicitado: {qty}. "
            "Limite absoluto e intocável — não pode ser sobrescrito.",
            validator="max_contracts_check",
        )
    return Approved()


def phase_contracts_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 7 — Art. 12º e Anexo II.

    Cada fase tem seu próprio limite de contratos, mais restritivo que o Art. 11º
    nas fases iniciais. O engine aplica o limite da fase atual.
    """
    phase_max = _PHASE_MAX_CONTRACTS.get(context.phase, 1)

    if candidate.contracts.value > phase_max:
        return Rejected(
            reason=f"Limite de contratos da {context.phase.value} excedido "
            f"(Art. 12º). Máximo: {phase_max} contrato(s). "
            f"Solicitado: {candidate.contracts.value}.",
            validator="phase_contracts_check",
        )
    return Approved()


def simultaneous_position_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 8 — Art. 12º.

    WIN+WDO simultâneo é vedado nas fases iniciais (Fase 1 e 2).
    Nas fases 3 e 4, simultâneo é permitido dentro dos limites de contratos.

    Verifica se há posição aberta em ativo diferente do candidato em fase vedada.
    """
    if context.phase not in _SIMULTANEOUS_FORBIDDEN_PHASES:
        return Approved()

    # Verificar se há posição aberta em ativo diferente do candidato
    for position in context.open_positions:
        if position.asset != candidate.asset:
            return Rejected(
                reason=f"Operação simultânea WIN+WDO vedada na "
                f"{context.phase.value} (Art. 12º). "
                f"Posição aberta em {position.asset.value}. "
                f"Feche antes de operar {candidate.asset.value}.",
                validator="simultaneous_position_check",
            )
    return Approved()


def total_open_contracts_check(
    candidate: OrderCandidate, context: RiskContext
) -> RiskDecision:
    """
    Validator 8.5 — Art. 12o explicito (TD-001 resolvido pela SPEC v0.3).

    Soma de contratos ABERTOS do mesmo ativo + contratos do candidato
    nao pode exceder o limite da fase. Cobre o cenario: Carlos ja tem
    1 WIN aberto e tenta abrir outro WIN em Fase 2 (limite=1) — DEVE
    REJEITAR.

    Pure Python — Zero I/O.
    """
    phase_max = _PHASE_MAX_CONTRACTS.get(context.phase, 1)
    open_same_asset = sum(
        p.contracts.value for p in context.open_positions if p.asset == candidate.asset
    )
    total = open_same_asset + candidate.contracts.value
    if total > phase_max:
        return Rejected(
            reason=(
                f"Soma total de contratos {candidate.asset.value} excederia "
                f"limite da {context.phase.value} (Art. 12o). "
                f"Abertos: {open_same_asset}; solicitado: {candidate.contracts.value}; "
                f"limite: {phase_max}."
            ),
            validator="total_open_contracts_check",
        )
    return Approved()

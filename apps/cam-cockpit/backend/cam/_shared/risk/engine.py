"""
Risk Engine — Autoridade máxima sobre operações (Art. 15º).

Pipeline de validators constitucionais executados em sequência.
Primeiro Rejected encerra o pipeline — o engine retorna imediatamente
sem executar os validators restantes.

INVARIANTES:
- Pure Python — Zero I/O
- Stateless — não mantém estado entre chamadas
- Determinístico — mesma entrada sempre produz mesma saída
- A ordem dos validators é constitucional (SPEC R1.06)
"""
from cam._shared.risk.context import OrderCandidate, RiskContext
from cam._shared.risk.decision import Approved, RiskDecision
from cam._shared.risk.validators.group1_state import (
    kill_switch_active_check,
    phase_authorization_check,
    post_market_checklist_check,
    pre_market_checklist_check,
    tax_compliance_check,
)
from cam._shared.risk.validators.group2_limits import (
    max_contracts_check,
    phase_contracts_check,
    simultaneous_position_check,
    total_open_contracts_check,
)
from cam._shared.risk.validators.group3_pnl import (
    daily_loss_limit_check,
    gain_lock_check,
    monthly_loss_limit_check,
    weekly_loss_limit_check,
)
from cam._shared.risk.validators.group4_ops import (
    circuit_breaker_check,
    daily_operations_count_check,
    martingale_check,
    setup_a_plus_check,
    trading_window_check,
)

# Lista canônica de validators na ordem exata da SPEC R1.06.
# A ordem é lei — não alterar sem atualizar a SPEC e obter aprovação do Founder.
_VALIDATORS = [
    # Grupo 1 — Guardas de estado (posições 1–5)
    kill_switch_active_check,         # 1  — Art. 18º
    pre_market_checklist_check,       # 2  — Art. 32º
    post_market_checklist_check,      # 3  — Art. 33º
    tax_compliance_check,             # 4  — Art. 26º
    phase_authorization_check,        # 5  — Art. 30º
    # Grupo 2 — Limites de contratos e posição (posições 6–8)
    max_contracts_check,              # 6  — Art. 11º INTOCÁVEL
    phase_contracts_check,            # 7  — Art. 12º / Anexo II
    simultaneous_position_check,      # 8  — Art. 12º
    total_open_contracts_check,       # 8.5 — Art. 12º explicito (TD-001, SPEC v0.3)
    # Grupo 3 — Limites de P&L (posições 9–12)
    daily_loss_limit_check,           # 9  — Art. 16º (3% diário)
    weekly_loss_limit_check,          # 10 — Art. 16º (7% semanal)
    monthly_loss_limit_check,         # 11 — Art. 16º (15% mensal/fase)
    gain_lock_check,                  # 12 — Art. 17º (2% gain lock)
    # Grupo 4 — Regras operacionais (posições 13–17)
    daily_operations_count_check,     # 13 — Art. 20º
    martingale_check,                 # 14 — Art. 13º
    trading_window_check,             # 15 — POV v1.0
    setup_a_plus_check,               # 16 — Setup A+ obrigatório em F4
    circuit_breaker_check,            # 17 — configurável
]


_DERIVATIVE_ASSETS = {"WIN", "WDO", "IND", "DOL"}


def _assert_derivative_only(candidate: OrderCandidate, context: RiskContext) -> None:
    """
    Defesa estrutural Art. 23 (TASK-023 BL-D + QA-FIND-SEC-10).

    Holdings de patrimônio (PETR4, ITUB4, ...) nunca podem aparecer no
    Risk Engine. AssetType (StrEnum) já restringe ao construir candidato
    via API tipada — esta verificação cobre o caminho onde dicts vindos de
    fora do tipo são serializados para candidate.

    Lança AssertionError (bug crítico — não deveria acontecer em código sano).
    """
    asset_str = str(getattr(candidate.asset, "value", candidate.asset)).upper()
    if asset_str not in _DERIVATIVE_ASSETS:
        raise AssertionError(
            f"Risk Engine recebeu asset não-derivativo '{asset_str}' "
            f"(Art. 23 — Carteira Hard nunca entra em margem). "
            f"Derivativos permitidos: {sorted(_DERIVATIVE_ASSETS)}."
        )
    for pos in context.open_positions:
        pos_asset_str = str(getattr(pos.asset, "value", pos.asset)).upper()
        if pos_asset_str not in _DERIVATIVE_ASSETS:
            raise AssertionError(
                f"Risk Engine recebeu open_position com asset não-derivativo "
                f"'{pos_asset_str}' (Art. 23). Caller violou contrato."
            )


def validate(candidate: OrderCandidate, context: RiskContext) -> RiskDecision:
    """
    Executa o pipeline de validators constitucionais.

    Retorna Approved se todos os validators passaram.
    Retorna o primeiro Rejected encontrado, encerrando o pipeline.

    O CHAMADOR é responsável por:
    - Construir OrderCandidate e RiskContext com dados atuais do banco
    - Persistir o resultado em cam_risk_decisions após a chamada
    - Bloquear a operação se o resultado for Rejected

    O engine NÃO:
    - Faz queries ao banco
    - Lê arquivos ou configurações em disco
    - Faz chamadas HTTP
    - Persiste nada
    """
    # Defesa estrutural Art. 23 antes do pipeline (QA-FIND-SEC-10).
    _assert_derivative_only(candidate, context)

    for validator_fn in _VALIDATORS:
        result = validator_fn(candidate, context)
        if not result.approved:
            return result

    return Approved()

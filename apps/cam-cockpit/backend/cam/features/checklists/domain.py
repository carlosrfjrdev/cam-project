"""
Domínio da feature checklists — Arts. 32º e 33º da Constituição.

Checklist pré-mercado: obrigatório antes de qualquer operação do dia.
Checklist pós-mercado: obrigatório após o último pregão do dia.

Itens baseados na SPEC R10.03 e R10.04.
"""
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Itens obrigatórios — SPEC R10.03
# ---------------------------------------------------------------------------
REQUIRED_PRE_MARKET_ITEMS: list[str] = [
    "sistema_operacional_ok",
    "profit_conectado",
    "conexao_internet_estavel",
    "risk_engine_ativo",
    "capital_verificado",
    "plano_do_dia_definido",
    "estado_emocional_adequado",
    "nao_ha_noticias_criticas_pendentes",
    "kill_switch_disponivel",
    "contratos_maximos_respeitados",
]

# ---------------------------------------------------------------------------
# Itens obrigatórios — SPEC R10.04
# ---------------------------------------------------------------------------
REQUIRED_POST_MARKET_ITEMS: list[str] = [
    "todas_posicoes_encerradas",
    "journal_preenchido",
    "resultado_registrado",
    "aderencia_avaliada",
    "estado_emocional_registrado",
    "licao_do_dia_registrada",
    "decisao_harvest_registrada",
    "ledger_atualizado",
]


@dataclass
class PreMarketChecklist:
    """
    Checklist pré-mercado do dia.

    Deve ser completado com todos os itens obrigatórios antes de
    qualquer operação. O Risk Engine valida via pre_market_checklist_check.
    """

    date: str
    items: dict[str, bool] = field(default_factory=dict)

    def is_complete(self) -> bool:
        """Retorna True se todos os itens obrigatórios estão marcados como True."""
        return all(self.items.get(item, False) for item in REQUIRED_PRE_MARKET_ITEMS)


@dataclass
class PostMarketChecklist:
    """
    Checklist pós-mercado do pregão.

    Deve ser completado após o último pregão do dia. O Risk Engine valida
    via post_market_checklist_check no pregão seguinte.
    """

    date: str
    items: dict[str, bool] = field(default_factory=dict)
    result_summary: dict | None = None

    def is_complete(self) -> bool:
        """Retorna True se todos os itens obrigatórios estão marcados como True."""
        return all(self.items.get(item, False) for item in REQUIRED_POST_MARKET_ITEMS)

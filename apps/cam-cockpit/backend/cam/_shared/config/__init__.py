"""
Configuração centralizada do CaM via pydantic-settings.

Carrega variáveis do .env automaticamente.
Nunca expõe secrets em logs — pydantic-settings os trata como SecretStr se necessário.
"""
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações do CaM Cockpit.

    Todos os valores sensíveis (tokens, keys) devem viver no .env.
    O .env NUNCA é commitado (pré-commit hook bloqueia + .gitignore).
    """

    database_url: str = "postgresql+psycopg://cam:cam@localhost:5434/cam_db"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    cam_journal_dir: Path = Path.home() / ".cam" / "journal"

    # ---------------------------------------------------------------------
    # Camada de integração com broker (SPEC v0.2.1 — coexistência)
    # Apenas UMA pode estar True por vez (mutex R21.03).
    # ---------------------------------------------------------------------
    profit_integration_enabled: bool = False
    mt5_integration_enabled: bool = True

    # Bridge MT5 ZeroMQ
    mt5_bridge_host: str = "127.0.0.1"
    mt5_bridge_pub_port: int = 5556
    mt5_bridge_req_port: int = 5557
    mt5_wine_prefix: Path = Path.home() / ".wine"
    mt5_terminal_path: str = ""

    # Inspetor de Ativo (ADR-014) — fundamentos via brapi.dev
    # Token opcional (free tier funciona sem token p/ vários tickers).
    # NUNCA commitado — vive no .env.
    brapi_token: str = ""
    brapi_base_url: str = "https://brapi.dev/api"
    # Conecta a bridge ZeroMQ no startup do app (lifespan). Em CI/dev sem MT5,
    # deixar False evita sockets ociosos; em produção Windows, True.
    mt5_bridge_autoconnect: bool = False

    # T-TD-012 — CDI diario (risk-free rate) para Sharpe Ratio; default 0
    cdi_daily_rate: float = 0.0

    # T-TD-017 — Anthropic model/version configuraveis
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_api_version: str = "2023-06-01"

    # Trade Analyzer — OpenAI (provider selecionavel na UI). Sem default fixo:
    # o usuario escolhe Claude ou OpenAI a cada analise. Key vive no .env.
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    # Limite de tokens de saída da IA (Trade Analyzer). Default alto para não
    # cortar a narrativa/tabelas. Configurável no .env.
    ai_max_tokens: int = 4096

    # ---------------------------------------------------------------------
    # Profit bridge (ProfitDLL) — ticks READ-ONLY do Profit/Nelogica.
    # Lane de market-data, independente do mutex de execucao R21.03.
    # Segredos vivem no .env (nunca commitados).
    # ---------------------------------------------------------------------
    profit_dll_enabled: bool = False
    profit_dll_path: str = ""          # caminho do ProfitDLL.dll (Win64)
    profit_dll_key: str = ""           # chave de ativacao (Nelogica)
    profit_username: str = ""          # usuario da conta (email/documento)
    profit_password: str = ""          # senha da conta
    profit_default_exchange: str = "F"  # B3 derivativos (WIN/WDO) = F

    # T-TD-026 — WebSocket P&L modo real-data
    websocket_pnl_real_data: bool = False

    # ---------------------------------------------------------------------
    # Operação real — DEFESA EM PROFUNDIDADE (TASK-005, BL-A SPEC v0.4)
    #
    # `real_trading_allowed=False` é o default obrigatório por design
    # (SPEC v0.4 §3.3 + Constituição Art. 35º + R-01).
    #
    # `real_trading_accounts` é allowlist de logins MT5 autorizados a operar
    # real. Vazio por default. Habilitar `real_trading_allowed=true` com
    # allowlist vazia levanta ValueError no startup (impede meia-configuração).
    # ---------------------------------------------------------------------
    real_trading_allowed: bool = False
    real_trading_accounts: list[str] = []

    # ---------------------------------------------------------------------
    # Multiestratégia / Escalonamento (EMENDA-001 v2 — defaults `false`)
    # ---------------------------------------------------------------------
    multi_strategy_enabled: bool = False  # BL-H1 T046
    scaling_enabled: bool = False         # BL-H2 T056

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @field_validator("real_trading_accounts", mode="before")
    @classmethod
    def _split_accounts(cls, v):  # type: ignore[no-untyped-def]
        """Aceita string CSV em .env (ex.: 'acc1,acc2,acc3') ou lista nativa."""
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                return []
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return v

    @model_validator(mode="after")
    def _validate_real_trading_consistency(self) -> "Settings":
        """
        Bloqueia configuração ambígua: real_trading_allowed=true exige
        allowlist não-vazia. Forçar isso aqui evita ativação acidental via
        edição parcial do .env.
        """
        if self.real_trading_allowed and not self.real_trading_accounts:
            raise ValueError(
                "real_trading_allowed=true requer real_trading_accounts "
                "não-vazio. Defina a allowlist explicitamente no .env."
            )
        return self


settings = Settings()


def validate_integration_mutex(profit_enabled: bool, mt5_enabled: bool) -> None:
    """
    R21.03 — apenas UMA camada de integração broker pode estar ATIVA por vez.

    Chamada no startup do backend (lifespan). Levanta RuntimeError com mensagem
    clara para o Founder se ambas estiverem ativas simultaneamente.

    Estados aceitos:
        (True, False)  — Profit ativo (legado, SPEC v0.1)
        (False, True)  — MT5 ativo (SPEC v0.2 default)
        (False, False) — Manutenção (nenhum ativo — endpoints retornam 410/503)

    Estado proibido:
        (True, True)   — viola R21.03

    Args:
        profit_enabled: Settings.profit_integration_enabled
        mt5_enabled: Settings.mt5_integration_enabled

    Raises:
        RuntimeError: se ambas as flags estiverem True.
    """
    if profit_enabled and mt5_enabled:
        raise RuntimeError(
            "R21.03 violado — PROFIT_INTEGRATION_ENABLED e MT5_INTEGRATION_ENABLED "
            "não podem estar ambos true simultaneamente. "
            "Edite .env e mantenha apenas UMA camada de integração broker ativa."
        )

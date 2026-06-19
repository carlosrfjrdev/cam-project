"""
Providers de LLM para a IA Auditora do CaM.

Providers disponíveis:
- OllamaProvider: LLM local via Ollama (preferencial — sem custo, sem latência de rede)
- AnthropicProvider: Claude via API Anthropic (fallback cloud)
- ProviderWithFallback: Decorator de fallback automático entre dois providers

A IA opera em modo read-only e auditoria — nunca executa ordens (Arts. 34-36).
"""
import httpx

from cam._shared.audit import get_logger

log = get_logger("ai_analyst.providers")


class OllamaProvider:
    """
    Provider para LLM local via Ollama.

    Requer Ollama rodando em base_url com o modelo especificado.
    Timeout generoso (120s) para modelos locais de 7-13B parâmetros.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
    ) -> None:
        self.base_url = base_url
        self.model = model

    async def analyze(self, prompt: str) -> str:
        """
        Envia prompt ao Ollama e retorna resposta como string.

        Raises:
            Exception: se Ollama não estiver disponível ou retornar erro
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]


class AnthropicProvider:
    """
    Provider para Claude via API Anthropic.

    Usado como fallback quando Ollama não está disponível.
    Requer ANTHROPIC_API_KEY configurada no ambiente.
    """

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        api_version: str | None = None,
    ) -> None:
        # T-TD-017 (SPEC v0.3) — model e api_version configuraveis via Settings
        from cam._shared.config import settings as _cam_settings
        self.api_key = api_key
        self.model = model or _cam_settings.anthropic_model
        self.api_version = api_version or _cam_settings.anthropic_api_version

    async def analyze(self, prompt: str) -> str:
        """
        Envia prompt à API Anthropic e retorna resposta como string.

        Raises:
            Exception: se API Anthropic não estiver disponível ou retornar erro
        """
        from cam._shared.config import settings as _cam_settings
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.api_version,
                },
                json={
                    "model": self.model,
                    "max_tokens": _cam_settings.ai_max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]


class OpenAIProvider:
    """
    Provider para GPT via API OpenAI (chat completions).

    Usado pelo Trade Analyzer quando o usuário escolhe OpenAI na UI.
    Requer OPENAI_API_KEY configurada no .env.
    """

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        from cam._shared.config import settings as _cam_settings
        self.api_key = api_key
        self.model = model or _cam_settings.openai_model
        self.base_url = (base_url or _cam_settings.openai_base_url).rstrip("/")

    async def analyze(self, prompt: str) -> str:
        from cam._shared.config import settings as _cam_settings
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    # GPT-5.x/o-series exigem max_completion_tokens (max_tokens dá 400)
                    # e o budget inclui tokens de raciocínio → folga grande.
                    "max_completion_tokens": _cam_settings.openai_max_completion_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if response.status_code >= 400:
                raise RuntimeError(
                    f"OpenAI {response.status_code}: {response.text[:300]}"
                )
            return response.json()["choices"][0]["message"]["content"]


class DeepSeekProvider:
    """
    Provider para DeepSeek (API OpenAI-compatible: /chat/completions).
    Requer DEEPSEEK_API_KEY no .env. Modelos: deepseek-chat, deepseek-reasoner.
    """

    def __init__(
        self, api_key: str, model: str = "deepseek-chat", base_url: str | None = None
    ) -> None:
        from cam._shared.config import settings as _cam_settings
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or _cam_settings.deepseek_base_url).rstrip("/")

    async def analyze(self, prompt: str) -> str:
        from cam._shared.config import settings as _cam_settings
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "max_tokens": _cam_settings.ai_max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class ProviderWithFallback:
    """
    Decorator de fallback automático entre dois providers.

    Se o provider primário falhar por qualquer motivo, tenta o fallback
    e loga o evento para rastreabilidade.

    Exemplo:
        provider = ProviderWithFallback(
            primary=OllamaProvider(),
            fallback=AnthropicProvider(api_key="..."),
        )
        result = await provider.analyze(prompt)
    """

    def __init__(self, primary, fallback) -> None:
        self.primary = primary
        self.fallback = fallback

    async def analyze(self, prompt: str) -> str:
        """
        Tenta primary; em caso de falha, usa fallback.

        Raises:
            Exception: apenas se o fallback também falhar
        """
        try:
            return await self.primary.analyze(prompt)
        except Exception as e:
            log.warning("ai_analyst.provider_fallback", error=str(e))
            return await self.fallback.analyze(prompt)

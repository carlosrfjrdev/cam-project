"""
ContentGuard — Verificador de conteúdo proibido (Arts. 34-36 da Constituição).

Todo output da IA Auditora deve passar por esta verificação antes de ser entregue.
Conteúdo proibido é descartado e logado como violação.

A IA NÃO PODE:
- Enviar ordem de compra/venda
- Desabilitar ou parametrizar o Risk Engine
- Justificar exceção constitucional
"""
import re

PROHIBITED_PATTERNS = [
    r"\b(comprar?|vender?|compre|venda|buy|sell)\b.*\b(win|wdo|contrato|posição)\b",
    r"\b(recomend[ao]|sugir[ao]|deveria|should)\b.*\b(operar|entrar|sair|abrir|fechar)\b",
    (
        r"\b(ignore[m]?|ignoring|desabilit[ae]|bypass|desligar?)\b"
        r".*\b(stop|risco|risk engine|limite)\b"
    ),
    r"\bexceção\b.*\b(constitucional|regra|limite|risco)\b",
    r"\bjustificável\b.*\b(ignorar|exceção|burlar)\b",
    r"\bmantenha\b.*\b(posição|contrato)\b.*\b(stop|limite)\b",
]

# Frases diretas proibidas (checagem por substring, mais rápida e confiável)
DIRECT_FORBIDDEN_PHRASES = [
    "recomendo",
    "você deveria",
    "deveria comprar",
    "deveria vender",
    "ignore o stop",
    "ignore o risco",
    "risk engine pode ser ignorado",
    "exceção à regra",
    "exceção constitucional",
    "pode ser ignorado",
    "seria justificável",
]


class ContentGuard:
    """
    Verifica se o output da IA contém conteúdo proibido pelos Arts. 34-36.

    Uso:
        guard = ContentGuard()
        if guard.has_prohibited_content(text):
            log_violation(text)
        else:
            deliver(text)
    """

    def __init__(self) -> None:
        self._patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL) for p in PROHIBITED_PATTERNS
        ]

    def has_prohibited_content(self, text: str) -> bool:
        """Retorna True se o texto contém conteúdo proibido pela Constituição."""
        text_lower = text.lower()

        # Checagem rápida por frases diretas
        for phrase in DIRECT_FORBIDDEN_PHRASES:
            if phrase in text_lower:
                return True

        # Checagem por padrões regex compostos
        for pattern in self._patterns:
            if pattern.search(text):
                return True

        return False

    def sanitize_or_reject(self, text: str) -> tuple[str | None, bool]:
        """
        Verifica e rejeita conteúdo proibido.

        Returns:
            (text, False) se o conteúdo é permitido
            (None, True) se o conteúdo é proibido e deve ser descartado
        """
        if self.has_prohibited_content(text):
            return None, True
        return text, False

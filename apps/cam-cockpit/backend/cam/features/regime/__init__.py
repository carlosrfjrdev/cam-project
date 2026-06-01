"""
Feature `regime` — overlay de Regime de Markov read-only (ADR-014 / SPEC-Inspetor BL-8).

"Assistente de pesquisa" (Arts. 13/34–36, ADR-006): mostra estado/matriz/sinal,
NUNCA emite ordem nem dimensiona posição (papéis B/C ficam fora — Parte VII).

Slice auto-contido (ADR-013): lê `cam_inspector_candles` (tabela de banco), não
importa outras features. Matemática pura vendorizada com atribuição (ver domain.py).
"""

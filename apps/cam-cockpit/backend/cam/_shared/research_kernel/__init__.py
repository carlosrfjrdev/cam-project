"""
Research Kernel — primitivas puras compartilhadas (ADR-SL-02).

Funções determinísticas, zero I/O, reutilizáveis por múltiplas features sem
violar o import-linter (feature→feature proibido). Promovidas de
`features/research/leadlag/` para servir também o `strategy_lab`.

- `bars`     — barras canônicas M1→TF determinísticas (fuso America/Sao_Paulo).
- `validation` — DSR, FDR (Benjamini-Hochberg), walk-forward, Hayashi-Yoshida.
"""

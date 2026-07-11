"""
Lead-Lag Research Lane (SPEC v0.5 / ADR-015) — sub-versão 0.5.1 (Dados/R0).

Slice de descoberta estatística **read-only**, ISOLADO do live (ADR-015):
- não importa execução nem broker (import-linter enforce);
- escreve apenas em schema research_*;
- não emite sinal/ordem/sizing (Arts. 34º–36º).

0.5.1 entrega: ingestão parametrizável MT5→research_*, barras canônicas M1 →
derivadas determinísticas, ticks com agressor, snapshot/hash, quality checks,
Data Health. Análise (OFI, ρ defasado) vem em 0.5.2.
"""

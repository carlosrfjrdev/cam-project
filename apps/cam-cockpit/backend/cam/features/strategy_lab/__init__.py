"""
StrategyLab — Assets Strategy + RunTests + Experts (SPEC-STRATEGYLAB-TRIAD).

Feature de produto (TCaM): gestão de estratégias, backtest matemático de
VALORES BRUTOS (sem custo/IR/slippage — MVP), otimizador on-demand, e camada de
paridade Python↔EA MT5 (dupla implementação deliberada — ADR-SL-01).

Isolamento (ADR-SL-02/03): este slice NÃO importa `mt5_integration` nem execução
— a orquestração do EA é feita na borda (`cam/api/`) ou por evento. Reusa o
`_shared/research_kernel` (barras canônicas + validação) e a ingestão `research_*`.
Motor de backtest é NOVO e não importa `_shared.risk` (modo bruto desacoplado).
"""

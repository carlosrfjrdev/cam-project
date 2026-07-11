# strategy_lab — Assets Strategy + RunTests + Experts

> **Status:** EM CONSTRUÇÃO (Onda 1 — D1 ORB-30 fim-a-fim)
> **SPEC:** `project/tcam/demands/STRATEGYLAB-v0.6/SPEC-STRATEGYLAB-TRIAD.md`
> **ADRs:** ADR-SL-01 (dupla implementação, sem codegen), ADR-SL-02 (persistência+motor bruto), ADR-SL-03 (execução multi-símbolo MT5)

## Propósito

Tríade do StrategyLab do CaM (produto TCaM):
- **Assets Strategy** — gestão das estratégias, parâmetros, otimizador on-demand que **sugere** (não aplica).
- **Assets RunTests** — backtest matemático Python de **valores brutos** (entrada/saída/gain/loss/volume; sem custo/IR/slippage) + walk-forward + paridade.
- **Assets Experts** — gestão dos robôs MT5 (EA executor, conta DEMO).

## Princípios (engenharia — Constituição descomissionada)

- **MVP de valores brutos:** resultado é bruto. Custo/IR/slippage = Later. Toda saída leva o rótulo `BRUTO`.
- **Dupla implementação deliberada:** a estratégia é escrita em Python (aqui) E em MQL5 (EA), independentes. A **paridade** é o detector de dessincronização (gate bloqueante).
- **Reuso:** barras canônicas + validação vêm de `_shared/research_kernel`; ingestão de `research_*`; orquestração de EA via `mt5_integration` (sem import direto — borda/evento).
- **Par como unidade:** D3/LS são contabilizados pelo par (spread), pernas para auditoria.

## I/O (rotas `/api/v1/strategy-lab/*`)

Listar estratégias · ver/editar params · rodar backtest · rodar otimização (on-demand) ·
ver resultado/equity/trades · rodar/comparar paridade · gerir EAs.

## Anti-padrões

- ❌ Importar `mt5_integration` ou execução no backend (R-26).
- ❌ Importar `_shared.risk` no motor de backtest (modo bruto desacoplado — R-12).
- ❌ Codegen MQL5 (decisão do Founder: dupla implementação manual).
- ❌ Modelar custo/IR/slippage no MVP (valores brutos).

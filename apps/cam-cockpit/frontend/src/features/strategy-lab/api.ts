/**
 * API do StrategyLab (Assets Strategy + RunTests + Experts) — Onda 1 (D1).
 * O api client já prefixa /api/v1. Valores BRUTOS (sem custo/IR).
 */
import { api } from "../../api/client";

// --------------------------------------------------------------------------- //
// Assets Strategy — catálogo
// --------------------------------------------------------------------------- //
export interface StrategyDef {
  id: string;
  name: string;
  unit: "single" | "pair" | "basket";
  timeframe: string;
  description: string;
  default_params: Record<string, unknown>;
  param_space: Record<string, Array<number | string>>;
  runnable: boolean;
}

export interface StrategyList {
  strategies: StrategyDef[];
  label: string;
}

export const fetchStrategies = () =>
  api.get<StrategyList>("/strategy-lab/strategies");

// --------------------------------------------------------------------------- //
// Assets Strategy — conjuntos de parâmetros (gestão — R-04)
// --------------------------------------------------------------------------- //
export interface ParamSet {
  id: number;
  strategy_id: string;
  params: Record<string, number | string>;
  origin: string; // manual | suggested
  optimization_id?: number | null;
  created_at?: string;
}

export const fetchParamSets = (strategyId: string) =>
  api.get<{ param_sets: ParamSet[] }>(
    `/strategy-lab/strategies/${strategyId}/param-sets`,
  );

export const postParamSet = (
  strategyId: string,
  params: Record<string, number | string>,
) =>
  api.post<ParamSet>(`/strategy-lab/strategies/${strategyId}/param-sets`, {
    params,
  });

// --------------------------------------------------------------------------- //
// Assets RunTests — backtest + resultado
// --------------------------------------------------------------------------- //
export interface GrossMetrics {
  n_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  pnl_bruto_total: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number | null;
  payoff: number | null;
  max_drawdown: number;
  volume_financeiro: number;
}

export interface BacktestResult {
  run_id: number;
  strategy_id: string;
  symbol: string;
  timeframe: string;
  mode: string;
  label: string;
  n_bars: number;
  metrics: GrossMetrics;
  error?: string;
  message?: string;
}

export interface BacktestRequest {
  symbol: string;
  timeframe?: string;
  params?: Record<string, unknown>;
  point_value?: number;
  qty?: number;
}

export const postBacktest = (strategyId: string, body: BacktestRequest) =>
  api.post<BacktestResult>(`/strategy-lab/strategies/${strategyId}/backtest`, body);

export interface LegTrade {
  pair_id: number;
  leg: string;
  symbol: string;
  ts_entry: string;
  price_entry: number;
  ts_exit: string;
  price_exit: number;
  qty: number;
  exit_reason: string;
  pnl_bruto: number;
  volume_financeiro: number;
}

export interface RunDetail {
  run: Record<string, unknown>;
  trades: LegTrade[];
  label: string;
}

export const fetchRun = (runId: number) =>
  api.get<RunDetail>(`/strategy-lab/runs/${runId}`);

export interface EquityCurve {
  run_id: number;
  label: string;
  equity_curve: number[];
}

export const fetchEquity = (runId: number) =>
  api.get<EquityCurve>(`/strategy-lab/runs/${runId}/equity-curve`);

export interface RunSummary {
  id: number;
  strategy_id: string;
  symbols: string[];
  unit: string;
  timeframe: string;
  mode: string;
  metrics: GrossMetrics | null;
  status: string;
  created_at: string;
}

export const fetchRuns = (strategyId?: string) =>
  api.get<{ runs: RunSummary[] }>(
    `/strategy-lab/runs${strategyId ? `?strategy_id=${strategyId}` : ""}`,
  );

// --------------------------------------------------------------------------- //
// Assets Strategy — otimizador on-demand (SUGERE, não aplica)
// --------------------------------------------------------------------------- //
export interface OptimizeRequest {
  symbol: string;
  timeframe?: string;
  method?: "grid" | "random";
  random_n?: number;
  seed?: number;
  min_trades?: number;
  point_value?: number;
  qty?: number;
}

export interface OptimizeResult {
  strategy_id: string;
  symbol: string;
  verdict: "SUGGEST" | "INSUFFICIENT_DATA";
  best_params: Record<string, unknown>;
  best_score: number | null;
  n_trials: number;
  deflated_sharpe: number | null;
  no_cliff: boolean;
  suggested_param_set_id: number | null;
  note: string;
  error?: string;
}

export const postOptimize = (strategyId: string, body: OptimizeRequest) =>
  api.post<OptimizeResult>(`/strategy-lab/strategies/${strategyId}/optimize`, body);

// --------------------------------------------------------------------------- //
// Assets Experts — paridade Python ↔ EA
// --------------------------------------------------------------------------- //
export interface ParityDivergence {
  pair_id: number;
  dimension: string;
  python: unknown;
  ea: unknown;
  hint: string;
}

export interface ParityReport {
  run_id: number;
  label: string;
  verdict: "PASS" | "FAIL";
  n_python: number;
  n_ea: number;
  matched: number;
  divergences: ParityDivergence[];
}

export interface ParityRequest {
  ea_ledger: Array<Record<string, unknown>>;
  tick_size: number;
}

/**
 * POST paridade. O backend retorna 200 (PASS) ou 409 (FAIL) — AMBOS trazem o
 * relatório no corpo. Por isso não usamos o api client (que lança em !ok):
 * lemos o JSON nos dois casos e só lançamos em 4xx/5xx inesperados.
 */
export async function postParity(
  runId: number,
  body: ParityRequest,
): Promise<ParityReport> {
  const res = await fetch(`/api/v1/strategy-lab/runs/${runId}/parity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 200 || res.status === 409) {
    return (await res.json()) as ParityReport;
  }
  const err = await res.json().catch(() => ({ error: res.statusText }));
  throw new Error(err.error ?? err.detail ?? `HTTP ${res.status}`);
}

/**
 * Parser do CSV exportado por cam_d1_orb30.mq5 (delimitador ';', cabeçalho
 * canônico). Converte para o schema de ledger que a rota de paridade consome.
 */
export function parseEaLedgerCsv(text: string): Array<Record<string, unknown>> {
  const lines = text.trim().split(/\r?\n/).filter((l) => l.trim());
  if (lines.length < 2) return [];
  const header = lines[0].split(";").map((h) => h.trim());
  const rows: Array<Record<string, unknown>> = [];
  for (const line of lines.slice(1)) {
    const cells = line.split(";");
    const row: Record<string, unknown> = {};
    header.forEach((h, i) => {
      row[h] = (cells[i] ?? "").trim();
    });
    rows.push(row);
  }
  return rows;
}

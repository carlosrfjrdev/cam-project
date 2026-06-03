/**
 * API do Quant Lab (Research Lane / Lead-Lag) — SPEC v0.5.1. Read-only.
 * O api client já prefixa /api/v1.
 */
import { api } from "../../api/client";

export interface BarCoverage {
  symbol: string;
  timeframe: string;
  n: number;
  first_ts: string | null;
  last_ts: string | null;
}

export interface TickCoverage {
  symbol: string;
  n_ticks: number;
  n_aggressor: number;
  first_ts: string | null;
  last_ts: string | null;
}

export interface DataHealth {
  seed_universe: string[];
  bars: BarCoverage[];
  ticks: TickCoverage[];
}

export interface IngestResult {
  snapshot_id: number;
  composite_hash: string;
  symbols: string[];
  total_bars: number;
  total_ticks: number;
  per_symbol: Record<string, { m1?: number; bars?: number; ticks?: number; error?: string }>;
}

export interface IngestRequest {
  sources?: string[];
  timeframes?: string[];
  count?: number;
  with_ticks?: boolean;
  tick_count?: number;
}

export const fetchDataHealth = () => api.get<DataHealth>("/research/data-health");

export const postIngest = (body: IngestRequest) =>
  api.post<IngestResult>("/research/ingest", body);

// ---- 0.5.2: análise de lead-lag (correlação defasada) ----
export interface RunRequest {
  sources: string[];
  target: string;
  delta_grid?: number[];
  timeframe?: string;
  min_samples?: number;
  cost?: number;
}

export interface RunSummary {
  run_id: number;
  n_trials: number;
  status: string;
  sources: string[];
  target: string;
  delta_grid: number[];
  timeframe: string;
  cells: number;
  survivors: number;
}

export interface CellResult {
  source: string;
  target: string;
  timeframe: string;
  delta_or_tau: number;
  correlation: number | null;
  mu_net: number | null;
  n_samples: number;
  dsr: number | null;
  fdr_q: number | null;
  verdict: string; // SURVIVOR | KILLED | INSUFFICIENT_DATA
}

export interface RunResult {
  run: Record<string, unknown>;
  results: CellResult[];
}

export const postRun = (body: RunRequest) =>
  api.post<RunSummary>("/research/runs", body);

export const fetchRun = (runId: number) =>
  api.get<RunResult>(`/research/runs/${runId}`);

export const fetchTrials = () =>
  api.get<{ total_trials: number }>("/research/stats/trials");

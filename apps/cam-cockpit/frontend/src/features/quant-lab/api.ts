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

/**
 * API do Inspetor de Ativo (ADR-014 / SPEC-Inspetor). Read-only.
 * Tipos espelham os contratos do backend (mt5_integration + fundamentals + regime).
 */
import { api } from "../../api/client";

export type AssetType = "stock" | "fii" | "future" | "unknown";

export interface SymbolMeta {
  ticker: string;
  mt5_symbol: string;
  type: AssetType;
  has_fundamentals: boolean;
}

export interface Candle {
  time: number; // unix seconds (UTCTimestamp)
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CandlesResponse {
  symbol: string;
  timeframe: string;
  candles: Candle[];
}

export interface DividendEvent {
  date: string | null;
  type: string;
  value: number | null;
}

export interface DividendProjectionModel {
  annual: number | null;
  yield: number | null;
  label: string;
  years_used?: number[];
}

export interface Fundamentals {
  ticker: string;
  source: string;
  type: AssetType;
  dy: string | null;
  pl: string | null;
  pvp: string | null;
  roe: string | null;
  div_liq_ebitda: string | null;
  payout: string | null;
  roic: string | null;
  dividends_history: DividendEvent[];
  dividend_projection: {
    run_rate_12m: DividendProjectionModel;
    dy_avg_3_5y: DividendProjectionModel;
  } | null;
}

export interface RegimeResponse {
  symbol: string;
  timeframe: string;
  params: { window: number; threshold: number };
  insufficient_data: boolean;
  current_state: string | null;
  states: string[] | null;
  transition_matrix: number[][] | null;
  stationary: Record<string, number> | null;
  signal: number | null;
  walk_forward: { sharpe: number | null; max_drawdown: number | null } | null;
  disclaimer: string;
  attribution: string;
}

export const TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"] as const;
export type Timeframe = (typeof TIMEFRAMES)[number];

// NOTE: o api client já prefixa "/api/v1" (BASE_URL) — paths aqui são relativos.
export const fetchSymbols = () => api.get<{ symbols: string[] }>("/mt5/symbols");

export const fetchSymbolMeta = (ticker: string) =>
  api.get<SymbolMeta>(`/mt5/symbol/${encodeURIComponent(ticker)}`);

export const fetchCandles = (symbol: string, timeframe: string, count = 300) =>
  api.get<CandlesResponse>(
    `/mt5/candles?symbol=${encodeURIComponent(symbol)}&timeframe=${timeframe}&count=${count}`,
  );

export const fetchFundamentals = (ticker: string) =>
  api.get<Fundamentals>(`/fundamentals/${encodeURIComponent(ticker)}`);

export const fetchRegime = (symbol: string) =>
  api.get<RegimeResponse>(`/regime/${encodeURIComponent(symbol)}`);

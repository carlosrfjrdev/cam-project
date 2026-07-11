/**
 * Hooks de dados do Inspetor de Ativo. react-query (read-only).
 */
import { useQuery } from "@tanstack/react-query";
import {
  fetchCandles,
  fetchFundamentals,
  fetchRegime,
  fetchSymbolMeta,
} from "./api";

export function useSymbolMeta(ticker: string | null) {
  return useQuery({
    queryKey: ["inspetor", "meta", ticker],
    queryFn: () => fetchSymbolMeta(ticker as string),
    enabled: !!ticker,
  });
}

export function useCandles(symbol: string | null, timeframe: string) {
  return useQuery({
    queryKey: ["inspetor", "candles", symbol, timeframe],
    queryFn: () => fetchCandles(symbol as string, timeframe),
    enabled: !!symbol,
    refetchInterval: 30_000, // R-09: atualização periódica; WS cobre o tick ao vivo
    retry: false,
  });
}

export function useFundamentals(ticker: string | null, hasFundamentals: boolean) {
  return useQuery({
    queryKey: ["inspetor", "fundamentals", ticker],
    queryFn: () => fetchFundamentals(ticker as string),
    enabled: !!ticker && hasFundamentals,
    retry: false,
  });
}

export function useRegime(symbol: string | null, isStock: boolean) {
  return useQuery({
    queryKey: ["inspetor", "regime", symbol],
    queryFn: () => fetchRegime(symbol as string),
    enabled: !!symbol && isStock,
    retry: false,
  });
}

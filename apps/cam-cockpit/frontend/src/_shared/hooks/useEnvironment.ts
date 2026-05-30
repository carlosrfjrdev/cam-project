/**
 * useEnvironment — TASK-U011 (BL-UI-1).
 *
 * Resolve o ambiente operacional vigente para a UI. Fase 0: REAL_TRADING_ALLOWED
 * é false por design, então o ambiente nunca é REAL. Consulta o backend de forma
 * tolerante; na ausência de endpoint, assume DEMO (nunca REAL silenciosamente).
 */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";

export type TradingEnv = "BACKTEST" | "PAPER" | "DEMO" | "REAL";

interface EnvResponse {
  env?: TradingEnv;
  real_trading_allowed?: boolean;
}

export function useEnvironment(): { env: TradingEnv; realAllowed: boolean } {
  const { data } = useQuery({
    queryKey: ["environment"],
    queryFn: () => api.get<EnvResponse>("/dashboard/environment"),
    retry: 0,
    staleTime: 60_000,
  });

  const realAllowed = data?.real_trading_allowed ?? false;
  // Defesa: só é REAL se o backend afirmar AND real estiver liberado.
  const env: TradingEnv =
    data?.env === "REAL" && realAllowed ? "REAL" : data?.env ?? "DEMO";
  return { env, realAllowed };
}

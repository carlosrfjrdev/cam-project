/** Hook read-only das decisões do Risk Engine — TASK-U013 (BL-UI-2). */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface RiskDecision {
  id: string;
  decision: "APPROVED" | "REJECTED";
  validator: string | null;
  reason: string | null;
  asset: string | null;
  direction: string | null;
  contracts: number | null;
  env: string | null;
  mode: string | null;
  created_at: string | null;
}

export interface DecisionFilters {
  env?: string;
  decision?: string;
}

export function useOrderGatewayDecisions(filters: DecisionFilters = {}) {
  const params = new URLSearchParams();
  if (filters.env) params.set("env", filters.env);
  if (filters.decision) params.set("decision", filters.decision);
  const qs = params.toString();

  return useQuery({
    queryKey: ["order-gateway-decisions", filters],
    queryFn: () =>
      api.get<RiskDecision[]>(`/order-gateway/decisions${qs ? `?${qs}` : ""}`),
    refetchInterval: 10_000,
  });
}

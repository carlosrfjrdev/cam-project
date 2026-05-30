/** Hooks da Carteira Hard v0.4 — TASK-U022 (BL-UI-5). */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface Holding {
  id: string;
  ticker: string;
  asset_class: string;
  quantity: string;
  avg_price: string;
  source: string;
}

export interface PolicyAlert {
  ticker: string;
  level: number;
  code: string;
  message: string;
  suggestion: string;
}

export interface PolicyAlertsResponse {
  alerts: PolicyAlert[];
  blocking: boolean;
}

export interface DividendsCalendar {
  events: { ticker: string; ex_date: string; value: string }[];
  note?: string;
}

export function useHoldings() {
  return useQuery({
    queryKey: ["carteira-hard-holdings"],
    queryFn: () => api.get<Holding[]>("/carteira-hard/holdings"),
  });
}

export function usePolicyAlerts() {
  return useQuery({
    queryKey: ["carteira-hard-policy-alerts"],
    queryFn: () => api.get<PolicyAlertsResponse>("/carteira-hard/policy-alerts"),
  });
}

export function useDividendsCalendar() {
  return useQuery({
    queryKey: ["dividends-calendar"],
    queryFn: () => api.get<DividendsCalendar>("/dividends/calendar"),
  });
}

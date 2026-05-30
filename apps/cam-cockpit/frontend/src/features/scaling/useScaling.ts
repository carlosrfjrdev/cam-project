/** Hooks do Escalonamento — TASK-U021 (BL-UI-4). */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface ScalingEvent {
  id: string;
  ts: string | null;
  event_type: string;
  strategy_id: string | null;
  proposed_limit_win: number | null;
  proposed_limit_wdo: number | null;
  cooldown_days: number | null;
  cooldown_ends_at: string | null;
  notes: string | null;
}

export interface BlockedAttempts {
  histogram: Record<string, number>;
  criteria: string[];
}

export function useScalingEvents() {
  return useQuery({
    queryKey: ["scaling-events"],
    queryFn: () => api.get<ScalingEvent[]>("/scaling/events"),
  });
}

export function useBlockedAttempts() {
  return useQuery({
    queryKey: ["scaling-blocked"],
    queryFn: () => api.get<BlockedAttempts>("/scaling/blocked-attempts"),
  });
}

export function useRevokeScaling() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (escId: string) =>
      api.post(`/scaling/revoke/${escId}`, { reason: "Revogação via cockpit" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scaling-events"] }),
  });
}

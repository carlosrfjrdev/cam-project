/** Hooks do EA Control Panel — TASK-U017 (BL-UI-3). */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface EaState {
  ea_id: string;
  asset: string;
  version: string;
  hash: string;
  paused: boolean;
  online: boolean;
}

export function useEaStatus() {
  return useQuery({
    queryKey: ["ea-status"],
    queryFn: () => api.get<{ eas: EaState[] }>("/mt5/ea/status"),
    refetchInterval: 5_000,
  });
}

export function useEaControl() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["ea-status"] });
  const pause = useMutation({
    mutationFn: (id: string) => api.post(`/mt5/ea/${id}/pause`, {}),
    onSuccess: invalidate,
  });
  const resume = useMutation({
    mutationFn: (id: string) => api.post(`/mt5/ea/${id}/resume`, {}),
    onSuccess: invalidate,
  });
  return { pause, resume };
}

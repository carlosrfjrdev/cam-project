/** Hooks do Strategy Registry — TASK-U016 (BL-UI-3). */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface Strategy {
  id: string;
  name: string;
  version: string;
  asset: string;
  author: string;
  status: string;
  is_active: boolean;
  metadata: Record<string, unknown>;
}

export function useStrategies() {
  return useQuery({
    queryKey: ["strategies"],
    queryFn: () => api.get<Strategy[]>("/strategies"),
  });
}

export function useActivateStrategy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.post(`/strategies/${id}/activate`, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["strategies"] }),
  });
}

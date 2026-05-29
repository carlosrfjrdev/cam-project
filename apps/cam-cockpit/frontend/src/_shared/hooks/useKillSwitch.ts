import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { KillSwitchStatus } from "../../api/types";

export function useKillSwitch() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["kill-switch"],
    queryFn: () => api.get<KillSwitchStatus>("/kill-switch/status"),
    refetchInterval: 5_000,
  });

  const activate = useMutation({
    mutationFn: (reason: string) =>
      api.post("/kill-switch/activate", { reason }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["kill-switch"] }),
  });

  const deactivate = useMutation({
    mutationFn: () =>
      api.post("/kill-switch/deactivate", { confirm: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["kill-switch"] }),
  });

  return {
    isActive: data?.active ?? false,
    status: data,
    isLoading,
    activate: activate.mutate,
    deactivate: deactivate.mutate,
  };
}

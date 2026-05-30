/** Hooks do Research / AI Workbench — TASK-U023 (BL-UI-5). */
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface CorrelationResult {
  asset_a: string;
  asset_b: string;
  correlation: number | null;
  sample_size: number;
  window_days: number;
  note?: string;
}

export interface WorkbenchResult {
  call_id: string;
  provider: string;
  model: string;
  prompt_hash: string;
  anonymized: boolean;
  ts: string;
}

export function useCorrelation(assetA = "WIN", assetB = "WDO") {
  return useQuery({
    queryKey: ["research-correlation", assetA, assetB],
    queryFn: () =>
      api.get<CorrelationResult>(
        `/research/correlation?asset_a=${assetA}&asset_b=${assetB}`,
      ),
  });
}

export function useWorkbench() {
  return useMutation({
    mutationFn: (body: { provider: string; prompt: string }) =>
      api.post<WorkbenchResult>("/research/workbench", body),
  });
}

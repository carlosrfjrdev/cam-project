/** Hooks do Robot Orchestrator — TASK-U020 (BL-UI-4). */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface RobotStrategy {
  strategy_id: string;
  name: string;
  priority: number;
  is_active: boolean;
  status: string;
  suspended: boolean;
}

export interface Robot {
  id: string;
  name: string;
  strategies: RobotStrategy[];
}

export interface RobotsResponse {
  multi_strategy_enabled: boolean;
  robots: Robot[];
}

export function useRobots() {
  return useQuery({
    queryKey: ["robots"],
    queryFn: () => api.get<RobotsResponse>("/robots"),
  });
}

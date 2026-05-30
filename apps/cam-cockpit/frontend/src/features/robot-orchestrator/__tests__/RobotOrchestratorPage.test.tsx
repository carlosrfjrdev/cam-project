/** TDD First — TASK-U020 (BL-UI-4): Robot Orchestrator page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { RobotOrchestratorPage } from "../RobotOrchestratorPage";
import * as client from "../../../api/client";

const ROBOTS = {
  multi_strategy_enabled: false,
  robots: [{
    id: "r1", name: "ORB 60m WIN",
    strategies: [
      { strategy_id: "s1", name: "ORB 60m WIN", priority: 1, is_active: true, status: "paper_ok", suspended: false },
      { strategy_id: "s2", name: "Reversão", priority: 2, is_active: false, status: "demo_ok", suspended: true },
    ],
  }],
};

beforeEach(() => vi.restoreAllMocks());

describe("RobotOrchestratorPage", () => {
  it("lista robôs com estratégias e prioridade", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(ROBOTS);
    renderWithProviders(<RobotOrchestratorPage />);
    await waitFor(() => expect(screen.getByTestId("robot-card")).toBeInTheDocument());
    expect(screen.getByText("Reversão")).toBeInTheDocument();
  });

  it("marca estratégias suspensas", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(ROBOTS);
    renderWithProviders(<RobotOrchestratorPage />);
    await waitFor(() => expect(screen.getByTestId("suspended-strategy")).toBeInTheDocument());
  });

  it("mostra flag MULTI_STRATEGY_ENABLED (default OFF)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(ROBOTS);
    renderWithProviders(<RobotOrchestratorPage />);
    await waitFor(() => expect(screen.getByTestId("multi-strategy-flag")).toHaveTextContent("OFF"));
  });
});

/** TDD First — TASK-U019 (BL-UI-4): Risk Console v0.4 (aderência). */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { RiskConsolePage } from "../RiskConsolePage";
import * as client from "../../../api/client";

const ROBOTS = {
  multi_strategy_enabled: false,
  robots: [{
    id: "r1", name: "ORB", strategies: [
      { strategy_id: "s1", name: "ORB 60m WIN", priority: 1, is_active: true, status: "paper_ok", suspended: false },
      { strategy_id: "s2", name: "Reversão", priority: 2, is_active: false, status: "demo_ok", suspended: true },
    ],
  }],
};

beforeEach(() => vi.restoreAllMocks());

function mockApi() {
  vi.spyOn(client.api, "get").mockImplementation((path: string) => {
    if (path.includes("/robots")) return Promise.resolve(ROBOTS) as Promise<unknown>;
    if (path.includes("/risk/status")) return Promise.resolve({ current_phase: 1, tax_compliant: true }) as Promise<unknown>;
    return Promise.resolve([]) as Promise<unknown>;
  });
}

describe("RiskConsolePage — aderência v0.4", () => {
  it("mostra aderência individual e agregada", async () => {
    mockApi();
    renderWithProviders(<RiskConsolePage />);
    await waitFor(() => expect(screen.getByTestId("adherence-panel")).toBeInTheDocument());
    expect(screen.getByTestId("aggregate-adherence")).toBeInTheDocument();
    await waitFor(() => expect(screen.getAllByTestId("adherence-row").length).toBeGreaterThan(0));
  });

  it("estratégia abaixo de 95% marcada como suspensa", async () => {
    mockApi();
    renderWithProviders(<RiskConsolePage />);
    await waitFor(() => expect(screen.getByTestId("suspended-adherence")).toBeInTheDocument());
  });

  it("mostra limites vigentes (default 2+2)", async () => {
    mockApi();
    renderWithProviders(<RiskConsolePage />);
    await waitFor(() => expect(screen.getByTestId("current-limits")).toHaveTextContent("WIN 2"));
  });
});

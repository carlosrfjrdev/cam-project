/** TDD First — TASK-U021 (BL-UI-4): Escalonamento page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { ScalingPage } from "../ScalingPage";
import * as client from "../../../api/client";

const BLOCKED = { histogram: { PF: 2, WR: 1, EXP: 0, DD: 3, ADH: 0, OTHER: 0 }, criteria: ["PF", "WR", "EXP", "DD", "ADH"] };
const EVENTS = [{
  id: "e1", ts: null, event_type: "IN_FORCE", strategy_id: "s1",
  proposed_limit_win: 3, proposed_limit_wdo: 3, cooldown_days: 7,
  cooldown_ends_at: null, notes: null,
}];

beforeEach(() => vi.restoreAllMocks());

describe("ScalingPage", () => {
  it("mostra histograma com 5 critérios", async () => {
    vi.spyOn(client.api, "get").mockImplementation((path: string) =>
      Promise.resolve(path.includes("blocked") ? BLOCKED : EVENTS) as Promise<unknown>,
    );
    renderWithProviders(<ScalingPage />);
    await waitFor(() => {
      const bars = screen.getAllByTestId("histogram-bar");
      const crits = bars.map((b) => b.getAttribute("data-criterion"));
      for (const c of ["PF", "WR", "EXP", "DD", "ADH"]) expect(crits).toContain(c);
    });
  });

  it("exibe flag SCALING (OFF)", async () => {
    vi.spyOn(client.api, "get").mockImplementation((path: string) =>
      Promise.resolve(path.includes("blocked") ? BLOCKED : EVENTS) as Promise<unknown>,
    );
    renderWithProviders(<ScalingPage />);
    await waitFor(() => expect(screen.getByTestId("scaling-flag")).toHaveTextContent("OFF"));
  });

  it("evento IN_FORCE tem botão revogar", async () => {
    vi.spyOn(client.api, "get").mockImplementation((path: string) =>
      Promise.resolve(path.includes("blocked") ? BLOCKED : EVENTS) as Promise<unknown>,
    );
    renderWithProviders(<ScalingPage />);
    await waitFor(() => expect(screen.getByRole("button", { name: /revogar/i })).toBeInTheDocument());
  });
});

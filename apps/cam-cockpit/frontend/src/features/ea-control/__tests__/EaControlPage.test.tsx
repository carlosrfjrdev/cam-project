/** TDD First — TASK-U017 (BL-UI-3): EA Control page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { EaControlPage } from "../EaControlPage";
import * as client from "../../../api/client";

const STATUS = {
  eas: [
    { ea_id: "cam_risk_mirror_win", asset: "WIN", version: "0.4.0", hash: "abc", paused: false, online: false },
    { ea_id: "cam_risk_mirror_wdo", asset: "WDO", version: "0.4.0", hash: "def", paused: true, online: true },
  ],
};

beforeEach(() => vi.restoreAllMocks());

describe("EaControlPage", () => {
  it("mostra versão e hash", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(STATUS);
    renderWithProviders(<EaControlPage />);
    await waitFor(() => expect(screen.getByText(/v0.4.0 · abc/)).toBeInTheDocument());
  });

  it("reflete estado paused/ativo", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(STATUS);
    renderWithProviders(<EaControlPage />);
    await waitFor(() => {
      const flags = screen.getAllByTestId("ea-paused");
      expect(flags.some((f) => f.getAttribute("data-paused") === "true")).toBe(true);
    });
  });

  it("destaca heartbeat offline", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(STATUS);
    renderWithProviders(<EaControlPage />);
    await waitFor(() => {
      const hb = screen.getAllByTestId("ea-heartbeat");
      expect(hb.some((h) => h.getAttribute("data-online") === "false")).toBe(true);
    });
  });

  it("não tem botão de envio de ordem (Kevin)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(STATUS);
    renderWithProviders(<EaControlPage />);
    await waitFor(() => screen.getByText(/v0.4.0 · abc/));
    for (const b of screen.queryAllByRole("button")) {
      expect(b.textContent?.toLowerCase() ?? "").not.toMatch(/ordem|comprar|vender|submit/);
    }
  });
});

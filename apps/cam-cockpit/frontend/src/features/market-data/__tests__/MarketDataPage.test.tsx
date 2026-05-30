/** TDD First — TASK-U018 (BL-UI-3): Market Data page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { MarketDataPage } from "../MarketDataPage";
import * as client from "../../../api/client";

const PROVENANCE = [{
  import_id: "p1", source: "Profit CSV", source_url: null, asset: "WIN",
  ts_origin_min: null, ts_origin_max: null, ts_ingestion: null,
  tick_count: 1200, hash: "deadbeef", quality_flags: { has_gaps: true },
  license_terms_ack: true,
}];
const INSTRUMENTS = [{
  ticker: "WINFUT", asset_class: "futures", exchange: "B3",
  contract_size: "1", tick_size: "5", point_value: "0.20", active: true,
}];

beforeEach(() => vi.restoreAllMocks());

describe("MarketDataPage", () => {
  it("lista instrumentos com point_value", async () => {
    vi.spyOn(client.api, "get").mockImplementation((path: string) =>
      Promise.resolve(path.includes("instruments") ? INSTRUMENTS : PROVENANCE) as Promise<unknown>,
    );
    renderWithProviders(<MarketDataPage />);
    await waitFor(() => expect(screen.getByText("WINFUT")).toBeInTheDocument());
    expect(screen.getByText("0.20")).toBeInTheDocument();
  });

  it("destaca quality flags problemáticas", async () => {
    vi.spyOn(client.api, "get").mockImplementation((path: string) =>
      Promise.resolve(path.includes("instruments") ? INSTRUMENTS : PROVENANCE) as Promise<unknown>,
    );
    renderWithProviders(<MarketDataPage />);
    await waitFor(() => {
      const flags = screen.getAllByTestId("quality-flag");
      expect(flags.some((f) => f.getAttribute("data-problem") === "true")).toBe(true);
    });
  });
});

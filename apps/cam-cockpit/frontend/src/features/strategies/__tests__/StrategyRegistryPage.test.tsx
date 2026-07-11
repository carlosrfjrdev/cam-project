/** TDD First — TASK-U016 (BL-UI-3): Strategy Registry page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { StrategyRegistryPage } from "../StrategyRegistryPage";
import * as client from "../../../api/client";

const S1 = [{
  id: "s1", name: "ORB 60m WIN", version: "1.0", asset: "WIN",
  author: "carlos", status: "paper_ok", is_active: false, metadata: {},
}];

beforeEach(() => vi.restoreAllMocks());

describe("StrategyRegistryPage", () => {
  it("lista estratégias com status e is_active (S1 ORB)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(S1);
    renderWithProviders(<StrategyRegistryPage />);
    await waitFor(() => expect(screen.getByText("ORB 60m WIN")).toBeInTheDocument());
    expect(screen.getByText("paper_ok")).toBeInTheDocument();
  });

  it("ativar exige confirmação (gate visual)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(S1);
    renderWithProviders(<StrategyRegistryPage />);
    await waitFor(() => screen.getByText("ORB 60m WIN"));
    fireEvent.click(screen.getByRole("button", { name: /ativar/i }));
    expect(screen.getByText(/Ativar estratégia\?/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /confirmar ativação/i })).toBeInTheDocument();
  });

  it("não tem botão de ordem (Kevin)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(S1);
    renderWithProviders(<StrategyRegistryPage />);
    await waitFor(() => screen.getByText("ORB 60m WIN"));
    for (const b of screen.queryAllByRole("button")) {
      expect(b.textContent?.toLowerCase() ?? "").not.toMatch(/comprar|vender|enviar ordem|submit/);
    }
  });
});

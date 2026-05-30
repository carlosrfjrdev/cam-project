/** TDD First — TASK-U013 (BL-UI-2, SEC CRÍTICO): Order Gateway page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { OrderGatewayPage } from "../OrderGatewayPage";
import * as client from "../../../api/client";

const DECISIONS = [
  {
    id: "1", decision: "REJECTED", validator: "max_contracts_check",
    reason: "Limite 2 WIN excedido", asset: "WIN", direction: "BUY",
    contracts: 3, env: "demo", mode: "auto", created_at: "2026-05-29T10:00:00Z",
  },
  {
    id: "2", decision: "APPROVED", validator: null, reason: null,
    asset: "WDO", direction: "SELL", contracts: 1, env: "demo",
    mode: "auto", created_at: "2026-05-29T10:01:00Z",
  },
];

beforeEach(() => vi.restoreAllMocks());

describe("OrderGatewayPage", () => {
  it("lista decisões com validator e motivo", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(DECISIONS);
    renderWithProviders(<OrderGatewayPage />);
    await waitFor(() => expect(screen.getByText("max_contracts_check")).toBeInTheDocument());
    expect(screen.getByText(/Limite 2 WIN excedido/)).toBeInTheDocument();
  });

  it("destaca linhas REJECTED", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(DECISIONS);
    renderWithProviders(<OrderGatewayPage />);
    await waitFor(() => {
      const rows = screen.getAllByTestId("decision-row");
      expect(rows.some((r) => r.getAttribute("data-rejected") === "true")).toBe(true);
    });
  });

  it("não tem nenhum botão de envio de ordem (Kevin)", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(DECISIONS);
    renderWithProviders(<OrderGatewayPage />);
    await waitFor(() => screen.getByText("max_contracts_check"));
    const buttons = screen.queryAllByRole("button");
    for (const b of buttons) {
      expect(b.textContent?.toLowerCase() ?? "").not.toMatch(/enviar|ordem|comprar|vender|submit/);
    }
  });

  it("mostra estado vazio", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue([]);
    renderWithProviders(<OrderGatewayPage />);
    await waitFor(() => expect(screen.getByText(/Nenhuma decisão registrada/)).toBeInTheDocument());
  });
});

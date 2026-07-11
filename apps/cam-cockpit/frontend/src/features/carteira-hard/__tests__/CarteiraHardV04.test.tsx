/** TDD First — TASK-U022 (BL-UI-5): Carteira Hard v0.4. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { CarteiraHardPage } from "../CarteiraHardPage";
import * as client from "../../../api/client";

const HOLDINGS = [{ id: "h1", ticker: "PETR4", asset_class: "equity", quantity: "100", avg_price: "30.00", source: "MANUAL_UI" }];
const POLICY = { alerts: [{ ticker: "PETR4", level: 1, code: "DY_LOW", message: "DY baixo", suggestion: "reavaliar" }], blocking: false };

beforeEach(() => vi.restoreAllMocks());

function mockApi() {
  vi.spyOn(client.api, "get").mockImplementation((path: string) => {
    if (path.includes("/carteira-hard/holdings")) return Promise.resolve(HOLDINGS) as Promise<unknown>;
    if (path.includes("/policy-alerts")) return Promise.resolve(POLICY) as Promise<unknown>;
    if (path.includes("/dividends")) return Promise.resolve({ events: [], note: "sem proventos" }) as Promise<unknown>;
    return Promise.resolve(null) as Promise<unknown>;
  });
}

describe("CarteiraHardPage v0.4", () => {
  it("reforça Art. 23º (não é margem)", () => {
    mockApi();
    renderWithProviders(<CarteiraHardPage />);
    expect(screen.getByTestId("art23-note")).toHaveTextContent(/nunca/i);
  });

  it("lista holdings", async () => {
    mockApi();
    renderWithProviders(<CarteiraHardPage />);
    await waitFor(() => expect(screen.getByTestId("holding-row")).toBeInTheDocument());
    expect(within(screen.getByTestId("holding-row")).getByText("PETR4")).toBeInTheDocument();
  });

  it("policy alerts em amarelo e não-bloqueante (R-13)", async () => {
    mockApi();
    renderWithProviders(<CarteiraHardPage />);
    await waitFor(() => expect(screen.getByTestId("policy-alerts")).toBeInTheDocument());
    expect(screen.getByTestId("policy-alerts")).toHaveTextContent(/sugestão, nunca bloqueio/i);
  });

  it("rebalance é sugestão, nunca execução automática", () => {
    mockApi();
    renderWithProviders(<CarteiraHardPage />);
    expect(screen.getByTestId("rebalance-suggestion")).toHaveTextContent(/nunca.*executa/i);
  });

  it("mostra calendário de dividendos", () => {
    mockApi();
    renderWithProviders(<CarteiraHardPage />);
    expect(screen.getByTestId("dividends-calendar")).toBeInTheDocument();
  });
});

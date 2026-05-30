/** TDD First — TASK-U011 (BL-UI-1): EnvBanner + defesa. */
import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { EnvBanner } from "../EnvBanner";
import { PnlDisplay } from "../PnlDisplay";

describe("EnvBanner — defesa de ambiente (Don)", () => {
  it("exibe DEMO/PAPER/BACKTEST corretamente", () => {
    renderWithProviders(<EnvBanner env="DEMO" />);
    expect(screen.getByTestId("env-banner")).toHaveAttribute("data-env", "DEMO");
    expect(screen.getByText(/DEMO/)).toBeInTheDocument();
  });

  it("ambiente REAL é inconfundível (role=alert + texto forte)", () => {
    renderWithProviders(<EnvBanner env="REAL" />);
    const banner = screen.getByTestId("env-banner");
    expect(banner).toHaveAttribute("data-env", "REAL");
    expect(banner).toHaveAttribute("role", "alert");
    expect(screen.getByText(/DINHEIRO REAL/)).toBeInTheDocument();
  });

  it("ambiente não-real não usa role=alert", () => {
    renderWithProviders(<EnvBanner env="PAPER" />);
    expect(screen.getByTestId("env-banner")).toHaveAttribute("role", "status");
  });
});

describe("PnlDisplay — sempre líquido (Art. 25º), loss em vermelho", () => {
  it("exibe líquido e marca negativo", () => {
    renderWithProviders(<PnlDisplay grossAmount={-500} netAmount={-600} />);
    expect(screen.getByText(/líquido/i)).toBeInTheDocument();
    expect(screen.getByTestId("pnl-net")).toHaveAttribute("data-negative", "true");
  });
});

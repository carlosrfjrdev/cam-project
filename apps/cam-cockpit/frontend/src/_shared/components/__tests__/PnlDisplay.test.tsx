import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PnlDisplay } from "../PnlDisplay";

describe("PnlDisplay — Art. 25º: sempre exibe líquido", () => {
  it("exibe resultado líquido e bruto", () => {
    render(<PnlDisplay grossAmount={1000} netAmount={800} currency="BRL" />);
    expect(screen.getByText(/líquido/i)).toBeInTheDocument();
    expect(screen.getByText(/bruto/i)).toBeInTheDocument();
  });

  it("nunca exibe apenas o resultado bruto sem o líquido", () => {
    render(<PnlDisplay grossAmount={1000} netAmount={800} currency="BRL" />);
    const elements = screen.getAllByRole("generic");
    const hasNetLabel = elements.some(el => el.textContent?.toLowerCase().includes("líquido"));
    expect(hasNetLabel).toBe(true);
  });

  it("exibe valores negativos com sinalização visual", () => {
    render(<PnlDisplay grossAmount={-500} netAmount={-600} currency="BRL" />);
    expect(screen.getByTestId("pnl-net")).toHaveAttribute("data-negative", "true");
  });

  it("formata valores em reais brasileiros", () => {
    render(<PnlDisplay grossAmount={1234.56} netAmount={987.65} currency="BRL" />);
    expect(screen.getByTestId("pnl-net")).toHaveTextContent("R$");
  });
});

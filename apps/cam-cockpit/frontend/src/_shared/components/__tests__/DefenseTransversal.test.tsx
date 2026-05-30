/**
 * TDD First — TASK-U014 + U015 (BL-UI-2): defesa transversal no AppShell.
 *
 * EnvBanner (ambiente) e Kill Switch (Art. 18º) presentes em TODA rota
 * operacional. PnlDisplay sempre líquido (Art. 25º).
 */
import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { AppShell } from "../AppShell";

describe("Defesa transversal (AppShell)", () => {
  it("U014 — EnvBanner presente no shell (toda rota)", () => {
    renderWithProviders(<AppShell><div>x</div></AppShell>);
    expect(screen.getByTestId("env-banner")).toBeInTheDocument();
  });

  it("U014 — banner de ambiente sempre informa o ambiente vigente", () => {
    renderWithProviders(<AppShell><div>x</div></AppShell>);
    expect(screen.getByTestId("env-banner")).toHaveTextContent(/AMBIENTE:/);
  });

  it("U015 — kill switch presente no shell (≤ 1 toque, Art. 18º)", () => {
    renderWithProviders(<AppShell><div>x</div></AppShell>);
    const killBtn = screen.getByRole("button", { name: /kill switch/i });
    expect(killBtn).toBeInTheDocument();
    // Acessível em qualquer rota operacional — está no header fixo.
    expect(killBtn).toBeVisible();
  });
});

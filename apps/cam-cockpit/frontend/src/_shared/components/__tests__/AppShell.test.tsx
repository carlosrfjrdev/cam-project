/** TDD First — TASK-U010 (BL-UI-1): AppShell. */
import { describe, it, expect, beforeEach } from "vitest";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { AppShell } from "../AppShell";

beforeEach(() => localStorage.clear());

describe("AppShell", () => {
  it("renderiza header, sidebar e conteúdo", () => {
    renderWithProviders(<AppShell><div>conteúdo-x</div></AppShell>);
    expect(screen.getByTestId("cam-sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("sidebar-toggle")).toBeInTheDocument();
    expect(screen.getByText("conteúdo-x")).toBeInTheDocument();
  });

  it("colapsa/expande a sidebar pelo toggle", () => {
    renderWithProviders(<AppShell><div /></AppShell>);
    const sidebar = screen.getByTestId("cam-sidebar");
    expect(sidebar).toHaveAttribute("data-collapsed", "false");
    fireEvent.click(screen.getByTestId("sidebar-toggle"));
    expect(screen.getByTestId("cam-sidebar")).toHaveAttribute("data-collapsed", "true");
  });

  it("persiste o estado da sidebar no localStorage", () => {
    renderWithProviders(<AppShell><div /></AppShell>);
    fireEvent.click(screen.getByTestId("sidebar-toggle"));
    expect(localStorage.getItem("cam.sidebar.collapsed")).toBe("true");
  });

  it("não exibe elementos de multi-tenant (single-operator)", () => {
    renderWithProviders(<AppShell><div /></AppShell>);
    expect(screen.queryByText(/tenant/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/trocar (empresa|organização)/i)).not.toBeInTheDocument();
  });

  it("exibe o kill switch no shell (Art. 18º, toda rota)", () => {
    renderWithProviders(<AppShell><div /></AppShell>);
    expect(screen.getByText(/kill switch/i)).toBeInTheDocument();
  });
});

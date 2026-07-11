import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../components/Sidebar";
import { MVP_NAV_ITEMS, NAV_ITEMS } from "../nav";
import { UiProvider } from "../state/uiStore";

function renderSidebar() {
  return render(
    <UiProvider>
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    </UiProvider>,
  );
}

describe("Sidebar (MVP Inspetor)", () => {
  it("renderiza apenas os itens visíveis no MVP quando expandido", () => {
    renderSidebar();
    for (const item of MVP_NAV_ITEMS) {
      expect(screen.getByText(item.label)).toBeInTheDocument();
    }
    expect(screen.getByText("Inspetor de Ativo")).toBeInTheDocument();
  });

  it("oculta as telas não-MVP do sidebar (sem deletá-las)", () => {
    renderSidebar();
    const hidden = NAV_ITEMS.filter((i) => !i.visibleInMvp);
    for (const item of hidden) {
      expect(screen.queryByText(item.label)).not.toBeInTheDocument();
    }
  });
});

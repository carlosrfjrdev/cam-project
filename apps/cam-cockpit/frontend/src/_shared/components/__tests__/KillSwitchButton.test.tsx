import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { KillSwitchButton } from "../KillSwitchButton";

describe("KillSwitchButton — Art. 18º", () => {
  it("exibe botão de kill switch sempre visível", () => {
    render(<KillSwitchButton isActive={false} onActivate={vi.fn()} onDeactivate={vi.fn()} />);
    expect(screen.getByRole("button", { name: /kill switch/i })).toBeInTheDocument();
  });

  it("mostra chip ATIVO quando kill switch está ativo", () => {
    render(<KillSwitchButton isActive={true} onActivate={vi.fn()} onDeactivate={vi.fn()} />);
    expect(screen.getByText(/ativo/i)).toBeInTheDocument();
  });

  it("abre diálogo de confirmação ao clicar — proteção contra acionamento acidental", () => {
    render(<KillSwitchButton isActive={false} onActivate={vi.fn()} onDeactivate={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: /kill switch/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("chama onActivate ao confirmar diálogo com switch inativo", () => {
    const onActivate = vi.fn();
    render(<KillSwitchButton isActive={false} onActivate={onActivate} onDeactivate={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: /kill switch/i }));
    // confirmar no dialog
    const confirmBtn = screen.getByRole("button", { name: /ativar kill switch/i });
    fireEvent.click(confirmBtn);
    expect(onActivate).toHaveBeenCalledOnce();
  });

  it("chama onDeactivate ao confirmar diálogo com switch ativo", () => {
    const onDeactivate = vi.fn();
    render(<KillSwitchButton isActive={true} onActivate={vi.fn()} onDeactivate={onDeactivate} />);
    fireEvent.click(screen.getByRole("button", { name: /kill switch/i }));
    const confirmBtn = screen.getByRole("button", { name: /desativar/i });
    fireEvent.click(confirmBtn);
    expect(onDeactivate).toHaveBeenCalledOnce();
  });
});

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskEngineStatusBanner } from "../RiskEngineStatusBanner";

describe("RiskEngineStatusBanner — Art. 15º", () => {
  it("exibe banner vermelho quando kill switch está ativo", () => {
    render(<RiskEngineStatusBanner killSwitchActive={true} riskEngineBlocked={false} />);
    const banner = screen.getByRole("alert");
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent(/kill switch ativo/i);
  });

  it("exibe banner quando Risk Engine bloqueou operação", () => {
    render(<RiskEngineStatusBanner killSwitchActive={false} riskEngineBlocked={true} blockReason="Limite diário atingido" />);
    expect(screen.getByRole("alert")).toHaveTextContent(/limite diário atingido/i);
  });

  it("não exibe banner quando sistema operacional", () => {
    render(<RiskEngineStatusBanner killSwitchActive={false} riskEngineBlocked={false} />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});

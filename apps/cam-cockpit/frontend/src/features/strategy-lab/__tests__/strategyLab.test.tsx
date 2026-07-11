/** StrategyLab Onda 1 — parser de paridade (crítico) + smoke das telas. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { parseEaLedgerCsv } from "../api";
import { AssetsStrategyPage } from "../AssetsStrategyPage";
import * as client from "../../../api/client";

const STRATEGIES = {
  label: "BRUTO",
  strategies: [
    {
      id: "D1", name: "ORB-30 (Opening Range Breakout)", unit: "single",
      timeframe: "M1", description: "Quebra do range…",
      default_params: { or_minutes: 30, target_r: 1.0 },
      param_space: { or_minutes: [15, 30], target_r: [0.5, 1.0] },
      runnable: true,
    },
    {
      id: "D3", name: "Long-short de par", unit: "pair", timeframe: "M1",
      description: "Spread…", default_params: {}, param_space: {}, runnable: false,
    },
  ],
};

beforeEach(() => vi.restoreAllMocks());

describe("parseEaLedgerCsv (paridade Py↔EA)", () => {
  it("lê o CSV canônico do EA com delimitador ';'", () => {
    const csv = [
      "pair_id;leg;symbol;ts_entry;price_entry;ts_exit;price_exit;qty;exit_reason;pnl_bruto;volume_financeiro",
      "0;long;WIN$;2026-06-03T09:36:00;102.0;2026-06-03T09:40:00;110.0;1;target;1.60;42.40",
    ].join("\n");
    const rows = parseEaLedgerCsv(csv);
    expect(rows).toHaveLength(1);
    expect(rows[0].leg).toBe("long");
    expect(rows[0].symbol).toBe("WIN$");
    expect(rows[0].exit_reason).toBe("target");
    expect(rows[0].ts_entry).toBe("2026-06-03T09:36:00");
  });

  it("ignora CSV vazio ou só com cabeçalho", () => {
    expect(parseEaLedgerCsv("")).toHaveLength(0);
    expect(parseEaLedgerCsv("pair_id;leg;symbol")).toHaveLength(0);
  });
});

describe("AssetsStrategyPage", () => {
  it("mostra cards do catálogo com chip de status", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(STRATEGIES as unknown);
    renderWithProviders(<AssetsStrategyPage />);
    await waitFor(() => expect(screen.getByText("D1")).toBeInTheDocument());
    expect(screen.getByText("pronta")).toBeInTheDocument();
    expect(screen.getByText("em breve")).toBeInTheDocument();
  });
});

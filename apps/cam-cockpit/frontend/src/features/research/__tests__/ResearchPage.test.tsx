/** TDD First — TASK-U023 (BL-UI-5): Research / AI Workbench page. */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "../../../test/renderWithProviders";
import { ResearchPage } from "../ResearchPage";
import * as client from "../../../api/client";

const CORR = { asset_a: "WIN", asset_b: "WDO", correlation: 0.42, sample_size: 30, window_days: 30 };

beforeEach(() => vi.restoreAllMocks());

describe("ResearchPage", () => {
  it("renderiza visualização de correlação", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(CORR);
    renderWithProviders(<ResearchPage />);
    expect(screen.getByTestId("correlation-chart")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/0\.420/)).toBeInTheDocument());
  });

  it("workbench retorna output estruturado", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(CORR);
    vi.spyOn(client.api, "post").mockResolvedValue({
      call_id: "c1", provider: "ollama", model: "default",
      prompt_hash: "abcdef0123456789aa", anonymized: true, ts: "2026-05-29T10:00:00Z",
    });
    renderWithProviders(<ResearchPage />);
    fireEvent.change(screen.getByLabelText("Prompt"), { target: { value: "analise" } });
    fireEvent.click(screen.getByRole("button", { name: /analisar/i }));
    await waitFor(() => expect(screen.getByTestId("workbench-output")).toBeInTheDocument());
  });

  it("OpenAI mostra not-enabled", async () => {
    vi.spyOn(client.api, "get").mockResolvedValue(CORR);
    vi.spyOn(client.api, "post").mockRejectedValue(new Error("OpenAINotEnabled"));
    renderWithProviders(<ResearchPage />);
    fireEvent.change(screen.getByLabelText("Prompt"), { target: { value: "x" } });
    fireEvent.click(screen.getByRole("button", { name: /analisar/i }));
    await waitFor(() => expect(screen.getByTestId("openai-not-enabled")).toBeInTheDocument());
  });
});

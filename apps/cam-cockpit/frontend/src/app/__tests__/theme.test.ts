/** TDD First — TASK-U009 (BL-UI-1): theme MUI Esmeralda. */
import { describe, it, expect } from "vitest";
import { theme } from "../theme";

describe("theme DS CAM Esmeralda", () => {
  it("primary é Esmeralda #059669", () => {
    expect(theme.palette.primary.main).toBe("#059669");
  });

  it("backgrounds dark do DS", () => {
    expect(theme.palette.background.default).toBe("#1A1A1A");
    expect(theme.palette.background.paper).toBe("#1F1F1F");
  });

  it("cores funcionais do DS", () => {
    expect(theme.palette.success.main).toBe("#10B981");
    expect(theme.palette.warning.main).toBe("#F59E0B");
    expect(theme.palette.error.main).toBe("#EF4444");
    expect(theme.palette.info.main).toBe("#0EA5E9");
  });

  it("tipografia: headings Poppins, corpo Inter (não monospace global)", () => {
    expect(theme.typography.fontFamily).toContain("Inter");
    expect(theme.typography.fontFamily).not.toContain("monospace");
    expect(String(theme.typography.h4.fontFamily)).toContain("Poppins");
  });

  it("Founder Orange #FF7A00 é acento, nunca primary/success/warning", () => {
    expect(theme.palette.founderOrange.main).toBe("#FF7A00");
    expect(theme.palette.primary.main).not.toBe("#FF7A00");
    expect(theme.palette.success.main).not.toBe("#FF7A00");
    expect(theme.palette.warning.main).not.toBe("#FF7A00");
  });

  it("raio (btn 4px, card 6px) e focus ring 2px #10B981", () => {
    expect(theme.shape.borderRadius).toBe(4);
    expect(theme.cam.radiusCard).toBe(6);
    expect(theme.cam.focusRing).toContain("#10B981");
  });
});

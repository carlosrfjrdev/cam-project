/**
 * TDD First — TASK-U012 (BL-UI-1): tokens centralizados + WCAG AA.
 *
 * O lint no-hardcode roda como script standalone (`node scripts/lint_no_hardcode.mjs`,
 * integrado ao `npm run lint:no-hardcode`) — não é executado aqui para manter o
 * teste puro (sem dependência de @types/node).
 */
import { describe, it, expect } from "vitest";
import { camTokens } from "../../app/theme";

// Contraste relativo (WCAG) entre duas cores hex.
function luminance(hex: string): number {
  const c = hex.replace("#", "");
  const rgb = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16) / 255);
  const lin = rgb.map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}
function contrast(a: string, b: string): number {
  const la = luminance(a);
  const lb = luminance(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

describe("tokens DS CAM", () => {
  it("texto branco sobre background dark tem contraste >= 4.5", () => {
    expect(contrast("#FFFFFF", camTokens.background)).toBeGreaterThanOrEqual(4.5);
  });

  it("texto branco grande/bold sobre error (REAL) tem contraste >= 3.0 (WCAG large text)", () => {
    // Banner REAL usa texto grande e bold (peso 800), cujo limiar WCAG é 3:1.
    expect(contrast("#FFFFFF", camTokens.error)).toBeGreaterThanOrEqual(3.0);
  });

  it("primary Esmeralda sobre dark tem contraste suficiente para UI (>= 3.0)", () => {
    expect(contrast(camTokens.primaryLight, camTokens.background)).toBeGreaterThanOrEqual(3.0);
  });
});

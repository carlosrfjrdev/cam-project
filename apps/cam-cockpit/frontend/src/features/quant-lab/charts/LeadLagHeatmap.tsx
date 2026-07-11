/**
 * Heatmap do cubo (fatia fonte × δ) — a visão de relance do lead-lag.
 * Linhas = fontes, colunas = defasagem δ. Cor divergente: vermelho (−) →
 * cinza (0) → verde (+). Célula com borda branca = sobrevivente estatística.
 * SVG puro (sem lib).
 */
import { Box, Typography } from "@mui/material";
import type { CellResult } from "../api";

interface Props {
  sources: string[];
  cells: CellResult[];
}

function colorFor(c: number | null, maxAbs: number): string {
  if (c === null) return "#2a2f3a"; // dado insuficiente — cinza escuro
  const t = Math.max(-1, Math.min(1, c / maxAbs));
  if (t >= 0) {
    // cinza → verde
    const g = Math.round(80 + t * 130);
    return `rgb(${Math.round(60 - t * 30)},${g},${Math.round(90 - t * 20)})`;
  }
  // cinza → vermelho
  const r = Math.round(80 + -t * 130);
  return `rgb(${r},${Math.round(60 - -t * 30)},${Math.round(90 - -t * 20)})`;
}

export function LeadLagHeatmap({ sources, cells }: Props) {
  const deltas = Array.from(new Set(cells.map((c) => c.delta_or_tau))).sort(
    (a, b) => a - b,
  );
  if (deltas.length === 0 || sources.length === 0) return null;

  const byKey = new Map<string, CellResult>();
  for (const c of cells) byKey.set(`${c.source}|${c.delta_or_tau}`, c);
  const maxAbs = Math.max(
    0.05,
    ...cells.map((c) => Math.abs(c.correlation ?? 0)),
  );

  const cell = 16;
  const padL = 70;
  const padT = 4;
  const W = padL + deltas.length * cell + 8;
  const H = padT + sources.length * cell + 22;

  return (
    <Box sx={{ overflowX: "auto" }}>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Cubo (fatia): fonte × defasagem δ — cor = correlação
      </Typography>
      <svg width={W} height={H} role="img">
        {sources.map((src, r) => (
          <g key={src}>
            <text x={0} y={padT + r * cell + cell - 4} fontSize={10} fill="#cdd3dc">
              {src}
            </text>
            {deltas.map((d, ci) => {
              const c = byKey.get(`${src}|${d}`);
              const corr = c?.correlation ?? null;
              const survivor = c?.verdict === "SURVIVOR";
              return (
                <rect
                  key={d}
                  x={padL + ci * cell}
                  y={padT + r * cell}
                  width={cell - 1}
                  height={cell - 1}
                  fill={colorFor(corr, maxAbs)}
                  stroke={survivor ? "#fff" : "none"}
                  strokeWidth={survivor ? 1.5 : 0}
                >
                  <title>
                    {src} · δ={d} · {corr === null ? "dado insuf." : `C=${corr.toFixed(3)}`}
                    {c ? ` · ${c.verdict}` : ""}
                  </title>
                </rect>
              );
            })}
          </g>
        ))}
        {/* rótulos δ (a cada 5) */}
        {deltas.map((d, ci) =>
          ci % 5 === 0 ? (
            <text
              key={d}
              x={padL + ci * cell + 1}
              y={H - 6}
              fontSize={9}
              fill="#9aa4b2"
            >
              {d}
            </text>
          ) : null,
        )}
      </svg>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
        Verde = a fonte sobe e o alvo sobe δ barras depois. Vermelho = sobe e o alvo cai.
        Borda branca = sobrevivente. Cinza = dado insuficiente. Eixo X = δ (barras).
      </Typography>
    </Box>
  );
}

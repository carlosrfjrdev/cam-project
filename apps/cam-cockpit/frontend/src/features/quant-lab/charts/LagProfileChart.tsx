/**
 * Perfil de correlação defasada C(δ) — o gráfico-chave do lead-lag.
 * Barras: eixo X = defasagem δ (em barras), eixo Y = correlação.
 * Onde a barra é mais alta = a defasagem em que a fonte mais "lidera" o alvo.
 * SVG puro (sem lib). Verde = correlação +, vermelho = −.
 */
import { Box, Typography } from "@mui/material";
import type { CellResult } from "../api";

interface Props {
  source: string;
  target: string;
  cells: CellResult[]; // células de uma fonte → alvo, em vários δ
  height?: number;
}

export function LagProfileChart({ source, target, cells, height = 180 }: Props) {
  const data = cells
    .filter((c) => c.source === source && c.correlation !== null)
    .sort((a, b) => a.delta_or_tau - b.delta_or_tau);

  if (data.length === 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Sem correlação mensurável para {source} → {target} (dado insuficiente).
        </Typography>
      </Box>
    );
  }

  const W = 560;
  const H = height;
  const padL = 38;
  const padB = 24;
  const padT = 10;
  const plotW = W - padL - 8;
  const plotH = H - padB - padT;
  const maxAbs = Math.max(0.05, ...data.map((d) => Math.abs(d.correlation ?? 0)));
  const barW = plotW / data.length;
  const zeroY = padT + plotH / 2;

  // melhor célula (maior |C|) destacada
  let best = data[0];
  for (const d of data) {
    if (Math.abs(d.correlation ?? 0) > Math.abs(best.correlation ?? 0)) best = d;
  }

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        {source} → {target}: correlação por defasagem δ
      </Typography>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} role="img">
        {/* eixo zero */}
        <line x1={padL} y1={zeroY} x2={W - 8} y2={zeroY} stroke="#888" strokeWidth={1} />
        {/* rótulos Y */}
        <text x={4} y={padT + 8} fontSize={10} fill="#9aa4b2">+{maxAbs.toFixed(2)}</text>
        <text x={4} y={zeroY + 3} fontSize={10} fill="#9aa4b2">0</text>
        <text x={4} y={H - padB + 2} fontSize={10} fill="#9aa4b2">−{maxAbs.toFixed(2)}</text>

        {data.map((d, i) => {
          const c = d.correlation ?? 0;
          const h = (Math.abs(c) / maxAbs) * (plotH / 2);
          const x = padL + i * barW + 1;
          const y = c >= 0 ? zeroY - h : zeroY;
          const isBest = d.delta_or_tau === best.delta_or_tau;
          const survivor = d.verdict === "SURVIVOR";
          const color = survivor
            ? "#1faa73"
            : c >= 0
              ? "#3a7d5c"
              : "#a14a5a";
          return (
            <g key={d.delta_or_tau}>
              <rect
                x={x}
                y={y}
                width={Math.max(1, barW - 2)}
                height={h}
                fill={color}
                opacity={isBest ? 1 : 0.65}
                stroke={isBest ? "#fff" : "none"}
                strokeWidth={isBest ? 1 : 0}
              >
                <title>
                  δ={d.delta_or_tau} · C={c.toFixed(3)} · n={d.n_samples} · {d.verdict}
                </title>
              </rect>
              {/* rótulo δ a cada ~5 barras */}
              {i % Math.ceil(data.length / 10) === 0 && (
                <text
                  x={x + barW / 2}
                  y={H - padB + 12}
                  fontSize={9}
                  fill="#9aa4b2"
                  textAnchor="middle"
                >
                  {d.delta_or_tau}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <Typography variant="caption" color="text.secondary">
        Pico em δ={best.delta_or_tau} (C={best.correlation?.toFixed(3)}): a fonte tende a
        anteceder o alvo em ~{best.delta_or_tau} barra(s). Barra branca = melhor δ; verde
        forte = sobrevivente estatística.
      </Typography>
    </Box>
  );
}

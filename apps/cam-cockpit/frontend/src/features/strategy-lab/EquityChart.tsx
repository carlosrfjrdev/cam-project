/**
 * EquityChart — curva de equity bruta (manchete do RunTests, Design Review §3.2).
 *
 * SVG inline, zero-dependência. Área preenchida + linha; baseline em zero. Cor
 * pelo sinal do resultado final (verde positivo / vermelho negativo). É o ÚNICO
 * elemento que domina a primeira dobra — tudo abaixo é apoio.
 */
import { useTheme } from "@mui/material/styles";
import { Box, Typography } from "@mui/material";

interface EquityChartProps {
  data: number[];
  height?: number;
}

export function EquityChart({ data, height = 280 }: EquityChartProps) {
  const theme = useTheme();

  if (data.length < 2) {
    return (
      <Box
        sx={{
          height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "1px dashed",
          borderColor: "divider",
          borderRadius: 1,
        }}
      >
        <Typography color="text.secondary">
          Sem trades suficientes para desenhar a curva.
        </Typography>
      </Box>
    );
  }

  const W = 1000; // viewBox virtual; o SVG escala responsivo
  const H = height;
  const pad = 8;
  const min = Math.min(0, ...data);
  const max = Math.max(0, ...data);
  const span = max - min || 1;

  const x = (i: number) => pad + (i / (data.length - 1)) * (W - 2 * pad);
  const y = (v: number) => pad + (1 - (v - min) / span) * (H - 2 * pad);
  const yZero = y(0);

  const linePts = data.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  const areaPts = `${x(0)},${yZero} ${linePts} ${x(data.length - 1)},${yZero}`;

  const final = data[data.length - 1];
  const color = final >= 0 ? theme.palette.success.main : theme.palette.error.main;

  return (
    <Box sx={{ width: "100%" }} data-testid="equity-chart">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        width="100%"
        height={H}
        role="img"
        aria-label="Curva de equity bruta"
      >
        {/* baseline zero */}
        <line
          x1={pad}
          x2={W - pad}
          y1={yZero}
          y2={yZero}
          stroke={theme.palette.divider}
          strokeWidth={1}
          strokeDasharray="4 4"
        />
        <polygon points={areaPts} fill={color} fillOpacity={0.12} />
        <polyline
          points={linePts}
          fill="none"
          stroke={color}
          strokeWidth={2}
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    </Box>
  );
}

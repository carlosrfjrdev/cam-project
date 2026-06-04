/**
 * StatStrip — tira de 3-5 métricas-chave (Design Review §5.3, Andy).
 *
 * Substitui o anti-padrão "8 linhas label/valor" e "matriz de números". Número
 * grande, label pequeno, no máximo ~5. Forma canônica de "resumo numérico".
 * `tone` dá cor SÓ quando importa (perigo/positivo) — resto neutro.
 */
import { Box, Paper, Stack, Typography } from "@mui/material";

export type StatTone = "default" | "success" | "warning" | "danger";

export interface StatItem {
  label: string;
  value: string | number;
  tone?: StatTone;
}

const toneColor: Record<StatTone, string> = {
  default: "text.primary",
  success: "success.main",
  warning: "warning.main",
  danger: "error.main",
};

export function StatStrip({ items }: { items: StatItem[] }) {
  return (
    <Stack
      direction="row"
      spacing={1}
      sx={{ flexWrap: "wrap", gap: 1, my: 1 }}
      data-testid="stat-strip"
    >
      {items.map((it) => (
        <Paper
          key={it.label}
          elevation={0}
          sx={{
            px: 2,
            py: 1,
            minWidth: 96,
            flex: "1 1 auto",
            bgcolor: "background.paper",
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          <Typography variant="caption" color="text.secondary" noWrap>
            {it.label}
          </Typography>
          <Box>
            <Typography
              variant="h6"
              sx={{ color: toneColor[it.tone ?? "default"], fontWeight: 600 }}
            >
              {it.value}
            </Typography>
          </Box>
        </Paper>
      ))}
    </Stack>
  );
}

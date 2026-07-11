/**
 * Painel dos 7 indicadores R-20 (R-12/R-13). Só para Ação/FII.
 * Campo ausente → "N/A". FII: P/L, ROE, Dívida/EBITDA, ROIC tipicamente N/A.
 */
import { Box, Card, CardContent, Grid, Tooltip, Typography } from "@mui/material";
import type { Fundamentals } from "../api";

const LABELS: Record<string, { label: string; pct?: boolean; fiiNa?: boolean }> = {
  dy: { label: "DY", pct: true },
  pl: { label: "P/L", fiiNa: true },
  pvp: { label: "P/VP" },
  roe: { label: "ROE", pct: true, fiiNa: true },
  div_liq_ebitda: { label: "Dív.Líq/EBITDA", fiiNa: true },
  payout: { label: "Payout", pct: true },
  roic: { label: "ROIC", pct: true, fiiNa: true },
};

function fmt(value: string | null, pct?: boolean): string {
  if (value === null || value === undefined) return "N/A";
  const n = Number(value);
  if (Number.isNaN(n)) return "N/A";
  return pct ? `${(n * 100).toFixed(2)}%` : n.toFixed(2);
}

export function FundamentalsPanel({ data }: { data: Fundamentals }) {
  const isFii = data.type === "fii";
  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "baseline", gap: 1, mb: 1 }}>
        <Typography variant="h6">Fundamentos</Typography>
        <Typography variant="caption" color="text.secondary">
          fonte: {data.source}
        </Typography>
      </Box>
      <Grid container spacing={1.5}>
        {Object.entries(LABELS).map(([key, meta]) => {
          const raw = (data as unknown as Record<string, string | null>)[key];
          const na = raw === null && isFii && meta.fiiNa;
          return (
            <Grid item xs={6} sm={4} md={3} key={key}>
              <Tooltip title={na ? "Indicador não aplicável para FIIs" : ""} arrow>
                <Card variant="outlined" sx={{ textAlign: "center" }}>
                  <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
                    <Typography variant="caption" color="text.secondary">
                      {meta.label}
                    </Typography>
                    <Typography variant="h6">{fmt(raw, meta.pct)}</Typography>
                  </CardContent>
                </Card>
              </Tooltip>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}

import { Box, Grid, Paper, Typography, LinearProgress, Chip, Stack, Divider } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { PnlDisplay } from "../../_shared/components/PnlDisplay";
import { usePnlWebSocket } from "../../_shared/hooks/useWebSocket";
import type { RiskStatus } from "../../api/types";

function LimitGauge({ label, value, limit, warningAt = 0.7 }: {
  label: string;
  value: number;
  limit: number;
  warningAt?: number;
}) {
  const ratio = limit > 0 ? Math.min(Math.abs(value) / Math.abs(limit), 1) : 0;
  const color = ratio >= 1 ? "error" : ratio >= warningAt ? "warning" : "success";
  return (
    <Box>
      <Stack direction="row" justifyContent="space-between">
        <Typography variant="caption" color="text.secondary">{label}</Typography>
        <Typography variant="caption" color={`${color}.main`}>
          {(ratio * 100).toFixed(0)}%
        </Typography>
      </Stack>
      <LinearProgress variant="determinate" value={ratio * 100} color={color} sx={{ height: 8, borderRadius: 1 }} />
    </Box>
  );
}

export function CockpitPage() {
  const { pnl, connected } = usePnlWebSocket();
  const { data: riskStatus } = useQuery({
    queryKey: ["risk-status"],
    queryFn: () => api.get<RiskStatus>("/risk/status"),
    refetchInterval: 10_000,
  });

  const dailyGross = pnl?.daily_pnl_gross ?? 0;
  const dailyNet = pnl?.daily_pnl_net ?? 0;

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <Typography variant="h4" fontWeight={700}>Cockpit Live</Typography>
        <Chip
          label={connected ? "WS ONLINE" : "WS OFFLINE"}
          color={connected ? "success" : "error"}
          size="small"
        />
        {riskStatus && (
          <Chip
            label={`FASE ${riskStatus.current_phase}`}
            color="primary"
            size="small"
          />
        )}
      </Stack>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="overline" color="text.secondary">P&L do Dia</Typography>
            <PnlDisplay grossAmount={dailyGross} netAmount={dailyNet} size="large" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="overline" color="text.secondary" gutterBottom>Limites de Risco</Typography>
            <Stack spacing={2} mt={1}>
              <LimitGauge
                label="Perda Diária (3%)"
                value={dailyNet < 0 ? dailyNet : 0}
                limit={-(riskStatus?.daily_loss_limit ?? 150)}
              />
              <LimitGauge
                label="Perda Semanal (7%)"
                value={riskStatus?.daily_loss_limit ?? 0}
                limit={riskStatus?.weekly_loss_limit ?? 350}
              />
              <LimitGauge
                label="Perda Mensal (15%)"
                value={riskStatus?.daily_loss_limit ?? 0}
                limit={riskStatus?.monthly_loss_limit ?? 750}
              />
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="overline" color="text.secondary" gutterBottom>Status Operacional</Typography>
            <Stack spacing={1} mt={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Posições Abertas</Typography>
                <Typography variant="body2" fontWeight={700}>{pnl?.open_positions ?? 0}</Typography>
              </Stack>
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Gain Lock</Typography>
                <Chip
                  label={riskStatus?.gain_lock_reached ? "ATINGIDO" : "Livre"}
                  color={riskStatus?.gain_lock_reached ? "warning" : "success"}
                  size="small"
                />
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Conformidade Fiscal</Typography>
                <Chip
                  label={riskStatus?.tax_compliant !== false ? "OK" : "PENDENTE"}
                  color={riskStatus?.tax_compliant !== false ? "success" : "error"}
                  size="small"
                />
              </Stack>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

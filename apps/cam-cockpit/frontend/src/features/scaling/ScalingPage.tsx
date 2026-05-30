/**
 * Escalonamento — TASK-U021 (BL-UI-4).
 *
 * Histograma de tentativas-bloqueadas por critério (5 critérios Art. 11-B:
 * PF/WR/EXP/DD/ADH), eventos, cooldown vigente e botão revogar. Flag
 * SCALING_ENABLED (default false) — escalonamento nunca é ativado pela UI.
 */
import {
  Box, Typography, Stack, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Button, Alert, LinearProgress, Chip,
} from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import {
  useScalingEvents, useBlockedAttempts, useRevokeScaling,
} from "./useScaling";

function Histogram({ data }: { data: Record<string, number> }) {
  const max = Math.max(1, ...Object.values(data));
  return (
    <Stack spacing={1}>
      {Object.entries(data).map(([crit, count]) => (
        <Box key={crit} data-testid="histogram-bar" data-criterion={crit}>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="caption">{crit}</Typography>
            <Typography variant="caption">{count}</Typography>
          </Stack>
          <LinearProgress
            variant="determinate"
            value={(count / max) * 100}
            color="warning"
            sx={{ height: 8, borderRadius: 1 }}
          />
        </Box>
      ))}
    </Stack>
  );
}

export function ScalingPage() {
  const { data: events } = useScalingEvents();
  const { data: blocked } = useBlockedAttempts();
  const revoke = useRevokeScaling();
  const evts = events ?? [];
  const histogram = blocked?.histogram ?? {};

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <TrendingUpIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Escalonamento</Typography>
        <Chip label="SCALING: OFF" size="small" data-testid="scaling-flag" />
      </Stack>

      <Alert severity="info" sx={{ mb: 2 }}>
        Escalonamento constitucional (Art. 11-B). A UI nunca ativa escalonamento —
        apenas audita tentativas e permite revogar (preserva capital).
      </Alert>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Tentativas bloqueadas por critério</Typography>
        <Histogram data={histogram} />
      </Paper>

      <Typography variant="h6" sx={{ mb: 1 }}>Eventos</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Tipo</TableCell>
              <TableCell>WIN</TableCell>
              <TableCell>WDO</TableCell>
              <TableCell>Cooldown</TableCell>
              <TableCell align="right">Ação</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {evts.length === 0 && (
              <TableRow><TableCell colSpan={5}>
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>Nenhum evento.</Typography>
              </TableCell></TableRow>
            )}
            {evts.map((e) => (
              <TableRow key={e.id} data-testid="scaling-event-row">
                <TableCell><Chip label={e.event_type} size="small" /></TableCell>
                <TableCell>{e.proposed_limit_win ?? "—"}</TableCell>
                <TableCell>{e.proposed_limit_wdo ?? "—"}</TableCell>
                <TableCell>{e.cooldown_days ? `${e.cooldown_days}d` : "—"}</TableCell>
                <TableCell align="right">
                  {e.event_type === "IN_FORCE" && (
                    <Button size="small" color="warning" variant="outlined"
                      onClick={() => revoke.mutate(e.id)}>
                      Revogar
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

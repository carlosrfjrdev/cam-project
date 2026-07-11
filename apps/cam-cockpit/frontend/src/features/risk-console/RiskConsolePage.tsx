import {
  Box, Typography, Paper, Stack, Grid, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Alert,
} from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { RiskStatus } from "../../api/types";
import { useRobots } from "../robot-orchestrator/useRobots";

interface RiskDecisionEntry {
  id: string;
  trade_date: string;
  asset: string;
  decision: "APPROVED" | "REJECTED";
  validator: string | null;
  reason: string | null;
  created_at: string;
}

export function RiskConsolePage() {
  const { data: riskStatus } = useQuery({
    queryKey: ["risk-status"],
    queryFn: () => api.get<RiskStatus>("/risk/status"),
    refetchInterval: 10_000,
  });

  const { data: decisions } = useQuery({
    queryKey: ["risk-decisions"],
    queryFn: () => api.get<RiskDecisionEntry[]>("/risk/decisions"),
  });

  // U019 — aderência individual × agregada (R8.06) via Robot Orchestrator.
  const { data: robotsData } = useRobots();
  const strategies = (robotsData?.robots ?? []).flatMap((r) => r.strategies);
  const aggregateSuspended = strategies.some((s) => s.suspended);

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <Typography variant="h4" fontWeight={700}>Risk Console</Typography>
        <Chip label="READ ONLY" icon={<LockIcon />} size="small" color="warning" />
      </Stack>

      <Alert severity="info" sx={{ mb: 3 }}>
        Os parâmetros do Risk Engine são definidos pela POV vigente e pela Constituição (Arts. 11º, 15º). Não são editáveis via UI (CA5.4 / Art. 35º).
      </Alert>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>POV Vigente</Typography>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Fase Atual</Typography>
                <Chip label={`Fase ${riskStatus?.current_phase ?? "—"}`} color="primary" size="small" />
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Máx. Contratos WIN</Typography>
                <Typography variant="body2" fontWeight={700}>2 (Art. 11º — intocável)</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Máx. Contratos WDO</Typography>
                <Typography variant="body2" fontWeight={700}>2 (Art. 11º — intocável)</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Perda Diária Máx.</Typography>
                <Typography variant="body2">3% do capital</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Perda Semanal Máx.</Typography>
                <Typography variant="body2">7% do capital</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Perda Mensal Máx.</Typography>
                <Typography variant="body2">15% do capital</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Gain Lock</Typography>
                <Typography variant="body2">2% do capital</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Conformidade Fiscal</Typography>
                <Chip
                  label={riskStatus?.tax_compliant !== false ? "OK" : "PENDENTE"}
                  color={riskStatus?.tax_compliant !== false ? "success" : "error"}
                  size="small"
                />
              </Stack>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Kill Switch — Histórico</Typography>
            <Typography variant="body2" color="text.secondary">
              Histórico de ativações/desativações do kill switch
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mb: 3 }} data-testid="adherence-panel">
        <Stack direction="row" alignItems="center" spacing={2} mb={1}>
          <Typography variant="h6">Aderência — individual × agregada (R8.06)</Typography>
          <Chip
            label={`Limite vigente: WIN 2 · WDO 2`}
            size="small"
            color="primary"
            data-testid="current-limits"
          />
          <Chip
            label={aggregateSuspended ? "AGREGADA: ATENÇÃO" : "AGREGADA: OK"}
            size="small"
            color={aggregateSuspended ? "warning" : "success"}
            data-testid="aggregate-adherence"
          />
        </Stack>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Estratégia</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Aderência individual</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {strategies.length === 0 && (
                <TableRow><TableCell colSpan={3}>
                  <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                    Nenhuma estratégia ativa.
                  </Typography>
                </TableCell></TableRow>
              )}
              {strategies.map((s) => (
                <TableRow key={s.strategy_id} data-testid="adherence-row">
                  <TableCell>{s.name}</TableCell>
                  <TableCell>{s.status}</TableCell>
                  <TableCell>
                    {s.suspended
                      ? <Chip label="SUSPENSA (< 95%)" size="small" color="warning" data-testid="suspended-adherence" />
                      : <Chip label="OK (≥ 95%)" size="small" color="success" variant="outlined" />}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Typography variant="h6" gutterBottom>Decisões do Risk Engine</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Data/Hora</TableCell>
              <TableCell>Ativo</TableCell>
              <TableCell>Decisão</TableCell>
              <TableCell>Validator</TableCell>
              <TableCell>Motivo</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {decisions?.map(d => (
              <TableRow key={d.id} hover>
                <TableCell>{new Date(d.created_at).toLocaleString("pt-BR")}</TableCell>
                <TableCell>{d.asset}</TableCell>
                <TableCell>
                  <Chip
                    label={d.decision}
                    color={d.decision === "APPROVED" ? "success" : "error"}
                    size="small"
                  />
                </TableCell>
                <TableCell>{d.validator ?? "—"}</TableCell>
                <TableCell>{d.reason ?? "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

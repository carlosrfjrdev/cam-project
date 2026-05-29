import {
  Box, Typography, Paper, Stack, Grid, Button, TextField, MenuItem,
  Select, FormControl, InputLabel, Alert, Chip, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, LinearProgress,
} from "@mui/material";
import BarChartIcon from "@mui/icons-material/BarChart";
import LockIcon from "@mui/icons-material/Lock";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { BacktestConfig, BacktestRun } from "../../api/types";

function formatBRL(v: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);
}

function formatPct(v: number) {
  return `${(v * 100).toFixed(2)}%`;
}

export function BacktestPage() {
  const qc = useQueryClient();
  const [config, setConfig] = useState<BacktestConfig>({
    strategy_name: "",
    start_date: "2024-01-01",
    end_date: "2024-12-31",
    initial_capital: 5000,
    phase: 1,
  });
  const [selectedRun, setSelectedRun] = useState<BacktestRun | null>(null);

  const { data: runs } = useQuery({
    queryKey: ["backtest-runs"],
    queryFn: () => api.get<BacktestRun[]>("/backtest/runs"),
  });

  const runBacktest = useMutation({
    mutationFn: (cfg: BacktestConfig) => api.post<BacktestRun>("/backtest/run", cfg),
    onSuccess: (run) => {
      qc.invalidateQueries({ queryKey: ["backtest-runs"] });
      setSelectedRun(run);
    },
  });

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <BarChartIcon sx={{ fontSize: 32 }} />
        <Typography variant="h4" fontWeight={700}>Backtest Engine</Typography>
      </Stack>

      <Alert severity="info" sx={{ mb: 3 }}>
        O backtest usa o mesmo Risk Engine do ambiente live (Art. 15º / CA7.5).
        Não existe opção para desligar o Risk Engine ou alterar limites constitucionais.
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Configuração</Typography>
            <Stack spacing={2}>
              <TextField
                label="Estratégia"
                size="small"
                value={config.strategy_name}
                onChange={e => setConfig(c => ({ ...c, strategy_name: e.target.value }))}
                placeholder="Ex: Reversão Média 5m"
              />
              <TextField
                label="Data Início"
                type="date"
                size="small"
                value={config.start_date}
                onChange={e => setConfig(c => ({ ...c, start_date: e.target.value }))}
              />
              <TextField
                label="Data Fim"
                type="date"
                size="small"
                value={config.end_date}
                onChange={e => setConfig(c => ({ ...c, end_date: e.target.value }))}
              />
              <TextField
                label="Capital Inicial (R$)"
                type="number"
                size="small"
                value={config.initial_capital}
                onChange={e => setConfig(c => ({ ...c, initial_capital: Number(e.target.value) }))}
              />
              <FormControl size="small">
                <InputLabel>Fase Simulada</InputLabel>
                <Select value={config.phase} label="Fase Simulada" onChange={e => setConfig(c => ({ ...c, phase: Number(e.target.value) }))}>
                  <MenuItem value={1}>Fase 1 (1 contrato)</MenuItem>
                  <MenuItem value={2}>Fase 2 (1 contrato)</MenuItem>
                  <MenuItem value={3}>Fase 3 (2 contratos)</MenuItem>
                  <MenuItem value={4}>Fase 4 (2 contratos)</MenuItem>
                </Select>
              </FormControl>

              {/* CA7.5 — sem campo para desligar Risk Engine */}
              <Stack direction="row" alignItems="center" spacing={1} sx={{ p: 1.5, bgcolor: "action.hover", borderRadius: 1 }}>
                <LockIcon fontSize="small" color="warning" />
                <Typography variant="caption" color="text.secondary">
                  Risk Engine sempre ativo no backtest (CA7.5)
                </Typography>
              </Stack>

              <Button
                variant="contained"
                onClick={() => runBacktest.mutate(config)}
                disabled={runBacktest.isPending || !config.strategy_name}
                size="large"
              >
                Executar Backtest
              </Button>
            </Stack>
          </Paper>
        </Grid>

        {selectedRun && (
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                <Typography variant="h6">Resultado: {selectedRun.config.strategy_name}</Typography>
                <Chip label={selectedRun.status} color={selectedRun.status === "COMPLETED" ? "success" : "warning"} size="small" />
              </Stack>

              <Grid container spacing={2}>
                {[
                  { label: "Total de Trades", value: String(selectedRun.metrics.total_trades) },
                  { label: "Win Rate", value: formatPct(selectedRun.metrics.win_rate) },
                  { label: "P&L Bruto", value: formatBRL(selectedRun.metrics.total_pnl_gross) },
                  { label: "P&L Líquido", value: formatBRL(selectedRun.metrics.total_pnl_net) },
                  { label: "Max Drawdown", value: formatPct(selectedRun.metrics.max_drawdown) },
                  { label: "Sharpe Ratio", value: selectedRun.metrics.sharpe_ratio.toFixed(2) },
                  { label: "Fator de Lucro", value: selectedRun.metrics.profit_factor.toFixed(2) },
                ].map(m => (
                  <Grid item xs={6} sm={4} key={m.label}>
                    <Box sx={{ textAlign: "center", p: 1.5, bgcolor: "action.hover", borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary" display="block">{m.label}</Typography>
                      <Typography variant="body1" fontWeight={700}>{m.value}</Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              <Box mt={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  P&L Líquido sempre exibido (Art. 25º)
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(Math.max(selectedRun.metrics.win_rate * 100, 0), 100)}
                  color={selectedRun.metrics.win_rate > 0.5 ? "success" : "error"}
                  sx={{ height: 8, borderRadius: 1 }}
                />
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>

      <Box mt={3}>
        <Typography variant="h6" gutterBottom>Histórico de Runs</Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Data</TableCell>
                <TableCell>Estratégia</TableCell>
                <TableCell>Período</TableCell>
                <TableCell align="right">Trades</TableCell>
                <TableCell align="right">Win Rate</TableCell>
                <TableCell align="right">P&L Líquido</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runs?.map(run => (
                <TableRow
                  key={run.id}
                  hover
                  onClick={() => setSelectedRun(run)}
                  sx={{ cursor: "pointer", bgcolor: selectedRun?.id === run.id ? "action.selected" : undefined }}
                >
                  <TableCell>{new Date(run.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  <TableCell>{run.config.strategy_name}</TableCell>
                  <TableCell>{run.config.start_date} → {run.config.end_date}</TableCell>
                  <TableCell align="right">{run.metrics.total_trades}</TableCell>
                  <TableCell align="right">{formatPct(run.metrics.win_rate)}</TableCell>
                  <TableCell align="right" sx={{ color: run.metrics.total_pnl_net >= 0 ? "success.main" : "error.main", fontWeight: 700 }}>
                    {formatBRL(run.metrics.total_pnl_net)}
                  </TableCell>
                  <TableCell>
                    <Chip label={run.status} color={run.status === "COMPLETED" ? "success" : "default"} size="small" />
                  </TableCell>
                </TableRow>
              ))}
              {(!runs || runs.length === 0) && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">Nenhum backtest executado ainda</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}

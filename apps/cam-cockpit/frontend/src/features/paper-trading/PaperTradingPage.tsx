import {
  Box, Typography, Paper, Stack, Grid, Button, Chip, TextField,
  MenuItem, Select, FormControl, InputLabel, Alert, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
} from "@mui/material";
import ScienceIcon from "@mui/icons-material/Science";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../../api/client";
import { PnlDisplay } from "../../_shared/components/PnlDisplay";
import type { PaperTradeSimulation } from "../../api/types";

interface SimulationForm {
  asset: string;
  direction: string;
  contracts: number;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  strategy: string;
}

export function PaperTradingPage() {
  const [form, setForm] = useState<SimulationForm>({
    asset: "WIN",
    direction: "LONG",
    contracts: 1,
    entry_price: 0,
    stop_loss: 0,
    take_profit: 0,
    strategy: "",
  });
  const [result, setResult] = useState<PaperTradeSimulation | null>(null);

  const simulate = useMutation({
    mutationFn: (data: SimulationForm) =>
      api.post<PaperTradeSimulation>("/paper-trading/simulate-operation", data),
    onSuccess: (data) => setResult(data),
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* CA5.5 — badge SIMULACAO grande e visível, nunca confundível com live */}
      <Box
        sx={{
          position: "fixed",
          top: 70,
          right: 16,
          zIndex: 1200,
          pointerEvents: "none",
        }}
      >
        <Chip
          label="SIMULAÇÃO — PAPER TRADING"
          icon={<ScienceIcon />}
          color="error"
          sx={{
            fontWeight: 900,
            fontSize: 14,
            px: 2,
            py: 1,
            height: "auto",
            border: "2px solid",
            borderColor: "error.main",
            backgroundColor: "rgba(211, 47, 47, 0.15)",
          }}
        />
      </Box>

      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <ScienceIcon sx={{ fontSize: 32, color: "error.main" }} />
        <Typography variant="h4" fontWeight={700} color="error.main">Paper Trading</Typography>
        <Chip label="SIMULAÇÃO" color="error" size="small" sx={{ fontWeight: 700 }} />
      </Stack>

      <Alert severity="warning" sx={{ mb: 3, fontWeight: 700 }}>
        MODO SIMULAÇÃO — Nenhuma ordem real é enviada ao Profit. Todas as regras do Risk Engine estão ativas.
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, border: "2px solid", borderColor: "error.light" }}>
            <Typography variant="h6" gutterBottom color="error.main">Simular Operação</Typography>
            <Stack spacing={2}>
              <Stack direction="row" spacing={2}>
                <FormControl size="small" sx={{ minWidth: 80 }}>
                  <InputLabel>Ativo</InputLabel>
                  <Select value={form.asset} label="Ativo" onChange={e => setForm(f => ({ ...f, asset: e.target.value }))}>
                    <MenuItem value="WIN">WIN</MenuItem>
                    <MenuItem value="WDO">WDO</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 80 }}>
                  <InputLabel>Direção</InputLabel>
                  <Select value={form.direction} label="Direção" onChange={e => setForm(f => ({ ...f, direction: e.target.value }))}>
                    <MenuItem value="LONG">LONG</MenuItem>
                    <MenuItem value="SHORT">SHORT</MenuItem>
                  </Select>
                </FormControl>
                <TextField
                  label="Contratos"
                  type="number"
                  size="small"
                  value={form.contracts}
                  onChange={e => setForm(f => ({ ...f, contracts: Number(e.target.value) }))}
                  sx={{ width: 100 }}
                  inputProps={{ min: 1, max: 2 }}
                />
              </Stack>
              <TextField label="Preço Entrada" type="number" size="small" value={form.entry_price} onChange={e => setForm(f => ({ ...f, entry_price: Number(e.target.value) }))} />
              <TextField label="Stop Loss" type="number" size="small" value={form.stop_loss} onChange={e => setForm(f => ({ ...f, stop_loss: Number(e.target.value) }))} />
              <TextField label="Take Profit" type="number" size="small" value={form.take_profit} onChange={e => setForm(f => ({ ...f, take_profit: Number(e.target.value) }))} />
              <TextField label="Estratégia" size="small" value={form.strategy} onChange={e => setForm(f => ({ ...f, strategy: e.target.value }))} />
              <Button
                variant="contained"
                color="error"
                onClick={() => simulate.mutate(form)}
                disabled={simulate.isPending}
                size="large"
              >
                Simular (Paper)
              </Button>
            </Stack>
          </Paper>
        </Grid>

        {result && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Resultado da Simulação</Typography>
              {result.approved ? (
                <>
                  <Chip label="APROVADO PELO RISK ENGINE" color="success" sx={{ mb: 2 }} />
                  <PnlDisplay grossAmount={result.simulated_result_gross} netAmount={result.simulated_result_net} size="medium" />
                </>
              ) : (
                <>
                  <Chip label="BLOQUEADO PELO RISK ENGINE" color="error" sx={{ mb: 2 }} />
                  <Alert severity="error">{result.reason}</Alert>
                </>
              )}
            </Paper>
          </Grid>
        )}
      </Grid>

      <Box mt={3}>
        <Typography variant="h6" gutterBottom>Histórico de Simulações (Sessão)</Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Ativo</TableCell>
                <TableCell>Direção</TableCell>
                <TableCell>Contratos</TableCell>
                <TableCell>Risk Engine</TableCell>
                <TableCell align="right">P&L Simulado (Líquido)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary">
                    Simulações da sessão atual aparecem aqui
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}

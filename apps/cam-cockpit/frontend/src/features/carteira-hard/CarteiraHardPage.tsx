import {
  Box, Typography, Paper, Stack, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Alert,
} from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { BucketSnapshot } from "../../api/types";

function formatBRL(v: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);
}

interface HarvestHistory {
  id: string;
  executed_at: string;
  net_profit: number;
  carteira_hard_transfer: number;
  buffer_transfer: number;
}

export function CarteiraHardPage() {
  const { data: snapshot } = useQuery({
    queryKey: ["bucket-snapshot"],
    queryFn: () => api.get<BucketSnapshot>("/harvest/snapshot"),
  });

  const { data: history } = useQuery({
    queryKey: ["harvest-history"],
    queryFn: () => api.get<HarvestHistory[]>("/harvest/history"),
  });

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <AccountBalanceIcon sx={{ fontSize: 32, color: "primary.main" }} />
        <Typography variant="h4" fontWeight={700}>Carteira Hard</Typography>
      </Stack>

      <Alert severity="info" sx={{ mb: 3 }}>
        Carteira Hard recebe 60% de cada harvest executado. Capital preservado — fora do ciclo operacional.
        Ativos externos (renda variável, FIIs) são registrados manualmente.
      </Alert>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Snapshot Patrimonial</Typography>
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="body1" color="text.secondary">Saldo Carteira Hard</Typography>
            <Typography variant="h4" fontWeight={700} color="primary.main">
              {formatBRL(snapshot?.carteira_hard ?? 0)}
            </Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">Último Harvest</Typography>
            <Typography variant="body2">
              {snapshot?.last_harvest_at
                ? new Date(snapshot.last_harvest_at).toLocaleDateString("pt-BR")
                : "Nenhum harvest executado"}
            </Typography>
          </Stack>
        </Stack>
      </Paper>

      <Typography variant="h6" gutterBottom>Histórico de Entradas por Harvest</Typography>
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Data</TableCell>
              <TableCell align="right">Lucro Líquido Total</TableCell>
              <TableCell align="right">Transferido (60%)</TableCell>
              <TableCell align="right">Buffer (40%)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history?.map(h => (
              <TableRow key={h.id} hover>
                <TableCell>{new Date(h.executed_at).toLocaleDateString("pt-BR")}</TableCell>
                <TableCell align="right">{formatBRL(h.net_profit)}</TableCell>
                <TableCell align="right" sx={{ color: "primary.main", fontWeight: 700 }}>
                  {formatBRL(h.carteira_hard_transfer)}
                </TableCell>
                <TableCell align="right">{formatBRL(h.buffer_transfer)}</TableCell>
              </TableRow>
            ))}
            {(!history || history.length === 0) && (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <Typography variant="body2" color="text.secondary">Nenhum harvest executado ainda</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Ativos Externos (Registro Manual)</Typography>
        <Chip label="PLACEHOLDER" size="small" color="default" sx={{ mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          Ativos externos (renda variável, FIIs, etc.) são registrados manualmente aqui.
          Fora do escopo do cockpit no Bloco atual — implementar em Fase 1+ conforme necessidade.
        </Typography>
      </Paper>
    </Box>
  );
}

import {
  Box, Typography, Paper, Stack, Grid, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Button, Alert,
} from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { FiscalApuration, Darf } from "../../api/types";

function StatusChip({ status }: { status: string }) {
  const colorMap: Record<string, "warning" | "success" | "error"> = {
    PENDING: "warning",
    PAID: "success",
    OVERDUE: "error",
  };
  return <Chip label={status} color={colorMap[status] ?? "default"} size="small" />;
}

function toNumber(v: string | number | null | undefined): number {
  if (v === null || v === undefined) return 0;
  const n = typeof v === "string" ? Number(v) : v;
  return Number.isFinite(n) ? n : 0;
}

function formatBRL(v: string | number | null | undefined) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(toNumber(v));
}

export function FiscalPage() {
  const qc = useQueryClient();
  const currentMonth = new Date().toISOString().slice(0, 7);

  const { data: apuration, error: apurationError } = useQuery({
    queryKey: ["fiscal-apuration", currentMonth],
    queryFn: () => api.get<FiscalApuration>(`/fiscal/apuration/${currentMonth}`),
    retry: false,
  });

  const { data: darfs } = useQuery({
    queryKey: ["darfs"],
    queryFn: () => api.get<Darf[]>("/fiscal/darfs"),
  });

  const markPaid = useMutation({
    mutationFn: (month: string) => api.patch(`/fiscal/darfs/${month}/mark-paid`, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["darfs"] }),
  });

  const overdueCount = darfs?.filter(d => d.status === "OVERDUE").length ?? 0;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} mb={3}>Ledger Fiscal</Typography>

      {overdueCount > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {overdueCount} DARF(s) em atraso — operações bloqueadas pelo Risk Engine (Art. 26º)
        </Alert>
      )}

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Apuração Mensal — {currentMonth}</Typography>
            {apuration ? (
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Resultado Bruto</Typography>
                  <Typography variant="body2" color={toNumber(apuration.gross_result) >= 0 ? "success.main" : "error.main"} fontWeight={700}>
                    {formatBRL(apuration.gross_result)}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Resultado Líquido</Typography>
                  <Typography variant="body2" fontWeight={700} color={toNumber(apuration.net_result) >= 0 ? "success.main" : "error.main"}>
                    {formatBRL(apuration.net_result)}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">Base Tributável</Typography>
                  <Typography variant="body2" fontWeight={700}>{formatBRL(apuration.taxable_base)}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">IR Day Trade (20%)</Typography>
                  <Typography variant="body2" color="warning.main">{formatBRL(apuration.ir_due)}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between" sx={{ pt: 1, borderTop: 1, borderColor: "divider" }}>
                  <Typography variant="body1" fontWeight={700}>DARF a Pagar</Typography>
                  <Typography variant="body1" fontWeight={700} color={toNumber(apuration.darf_value) > 0 ? "warning.main" : "text.primary"}>
                    {formatBRL(apuration.darf_value)}
                  </Typography>
                </Stack>
              </Stack>
            ) : apurationError ? (
              <Alert severity="info">Sem apuração para {currentMonth}. Registre operações para gerar.</Alert>
            ) : (
              <Typography variant="body2" color="text.secondary">Carregando...</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      <Typography variant="h6" gutterBottom>Histórico de DARFs</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Competência</TableCell>
              <TableCell align="right">Valor</TableCell>
              <TableCell>Vencimento</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Pago em</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {darfs?.map(darf => (
              <TableRow key={darf.month} hover>
                <TableCell>{darf.month}</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700 }}>{formatBRL(darf.value)}</TableCell>
                <TableCell>{darf.due_date}</TableCell>
                <TableCell><StatusChip status={darf.status} /></TableCell>
                <TableCell>{darf.paid_at ?? "—"}</TableCell>
                <TableCell>
                  {darf.status !== "PAID" && (
                    <Button size="small" variant="outlined" color="success" onClick={() => markPaid.mutate(darf.month)}>
                      Marcar como Paga
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {(!darfs || darfs.length === 0) && (
              <TableRow><TableCell colSpan={6} align="center">
                <Typography variant="body2" color="text.secondary">Nenhuma DARF gerada ainda</Typography>
              </TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

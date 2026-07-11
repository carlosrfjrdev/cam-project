import {
  Box, Typography, Paper, Stack, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Alert,
} from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { BucketSnapshot } from "../../api/types";
import {
  useHoldings, usePolicyAlerts, useDividendsCalendar,
} from "./useCarteiraHard";

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

  // U022 — lente Barsi: holdings R-20, policy alerts, dividendos.
  const { data: holdings } = useHoldings();
  const { data: policy } = usePolicyAlerts();
  const { data: dividends } = useDividendsCalendar();
  const holdingsRows = holdings ?? [];
  const alerts = policy?.alerts ?? [];

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <AccountBalanceIcon sx={{ fontSize: 32, color: "primary.main" }} />
        <Typography variant="h4" fontWeight={700}>Carteira Hard</Typography>
      </Stack>

      <Alert severity="warning" sx={{ mb: 2 }} data-testid="art23-note">
        <b>Art. 23º:</b> Carteira Hard é patrimônio preservado — <b>nunca</b> serve
        de margem para operação alavancada. Capital fora do ciclo de risco.
      </Alert>

      <Alert severity="info" sx={{ mb: 3 }}>
        Carteira Hard recebe 60% de cada harvest executado. Capital preservado — fora do ciclo operacional.
        Ativos externos (renda variável, FIIs) são registrados manualmente.
      </Alert>

      {alerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }} data-testid="policy-alerts">
          <b>Policy Engine (sugestão, nunca bloqueio — R-13):</b>
          <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
            {alerts.map((a, i) => (
              <li key={i}>
                <b>{a.ticker}</b> — {a.message} <i>({a.suggestion})</i>
              </li>
            ))}
          </ul>
        </Alert>
      )}

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

      <Typography variant="h6" gutterBottom>Holdings (R-20 — DY em destaque)</Typography>
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Ticker</TableCell>
              <TableCell>Classe</TableCell>
              <TableCell align="right">Quantidade</TableCell>
              <TableCell align="right">Preço médio</TableCell>
              <TableCell>Origem</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {holdingsRows.length === 0 && (
              <TableRow><TableCell colSpan={5} align="center">
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                  Nenhum ativo registrado.
                </Typography>
              </TableCell></TableRow>
            )}
            {holdingsRows.map((h) => (
              <TableRow key={h.id} hover data-testid="holding-row">
                <TableCell>{h.ticker}</TableCell>
                <TableCell>{h.asset_class}</TableCell>
                <TableCell align="right">{h.quantity}</TableCell>
                <TableCell align="right">{h.avg_price}</TableCell>
                <TableCell><Chip label={h.source} size="small" variant="outlined" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Stack direction={{ xs: "column", md: "row" }} spacing={3}>
        <Paper sx={{ p: 3, flex: 1 }} data-testid="dividends-calendar">
          <Typography variant="h6" gutterBottom>Calendário de Dividendos</Typography>
          {(dividends?.events ?? []).length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              {dividends?.note ?? "Sem proventos no horizonte."}
            </Typography>
          ) : (
            <ul>
              {dividends!.events.map((e, i) => (
                <li key={i}>{e.ticker} — {e.ex_date} — {e.value}</li>
              ))}
            </ul>
          )}
        </Paper>

        <Paper sx={{ p: 3, flex: 1 }} data-testid="rebalance-suggestion">
          <Typography variant="h6" gutterBottom>Rebalanceamento sugerido</Typography>
          <Alert severity="info" sx={{ mb: 1 }}>
            Sugestão para revisão manual. O cockpit <b>nunca executa</b>
            rebalanceamento automático.
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Use a sugestão como checklist. Nenhum botão de execução automática.
          </Typography>
        </Paper>
      </Stack>
    </Box>
  );
}

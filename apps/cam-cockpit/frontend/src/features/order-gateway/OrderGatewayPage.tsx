/**
 * Order Gateway / Risk Decisions — TASK-U013 (BL-UI-2, SEC CRÍTICO).
 *
 * Visibilidade do ponto mais sensível do sistema, SOMENTE leitura. Mostra cada
 * decisão do Risk Engine com o validator culpado e o motivo. REJECTED em
 * destaque vermelho. **Nenhuma ação de ordem nesta tela** (Kevin, Art. 35º).
 */
import { useState } from "react";
import {
  Box, Typography, Paper, Stack, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, MenuItem, Select, FormControl, InputLabel, Alert,
  alpha,
} from "@mui/material";
import GavelIcon from "@mui/icons-material/Gavel";
import {
  useOrderGatewayDecisions,
  type DecisionFilters,
} from "./useOrderGatewayDecisions";

export function OrderGatewayPage() {
  const [filters, setFilters] = useState<DecisionFilters>({});
  const { data, isLoading } = useOrderGatewayDecisions(filters);
  const rows = data ?? [];

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <GavelIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Order Gateway</Typography>
        <Chip label="READ-ONLY" size="small" color="primary" variant="outlined" />
      </Stack>

      <Alert severity="info" sx={{ mb: 2 }}>
        Histórico de decisões do Risk Engine. Esta tela é apenas auditoria — não
        envia nem cancela ordens (Art. 35º).
      </Alert>

      <Stack direction="row" spacing={2} mb={2}>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Ambiente</InputLabel>
          <Select
            label="Ambiente"
            value={filters.env ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, env: e.target.value || undefined }))}
          >
            <MenuItem value="">Todos</MenuItem>
            <MenuItem value="demo">Demo</MenuItem>
            <MenuItem value="paper">Paper</MenuItem>
            <MenuItem value="backtest">Backtest</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Decisão</InputLabel>
          <Select
            label="Decisão"
            value={filters.decision ?? ""}
            onChange={(e) => setFilters((f) => ({ ...f, decision: e.target.value || undefined }))}
          >
            <MenuItem value="">Todas</MenuItem>
            <MenuItem value="APPROVED">Aprovadas</MenuItem>
            <MenuItem value="REJECTED">Rejeitadas</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Decisão</TableCell>
              <TableCell>Ativo</TableCell>
              <TableCell>Direção</TableCell>
              <TableCell>Ambiente</TableCell>
              <TableCell>Validator</TableCell>
              <TableCell>Motivo</TableCell>
              <TableCell>Quando</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={7}>
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                    {isLoading ? "Carregando…" : "Nenhuma decisão registrada."}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {rows.map((r) => {
              const rejected = r.decision === "REJECTED";
              return (
                <TableRow
                  key={r.id}
                  data-testid="decision-row"
                  data-rejected={rejected ? "true" : "false"}
                  sx={rejected ? { bgcolor: (t) => alpha(t.palette.error.main, 0.1) } : undefined}
                >
                  <TableCell>
                    <Chip
                      label={r.decision}
                      size="small"
                      color={rejected ? "error" : "success"}
                    />
                  </TableCell>
                  <TableCell>{r.asset ?? "—"}</TableCell>
                  <TableCell>{r.direction ?? "—"}</TableCell>
                  <TableCell>{r.env ?? "—"}</TableCell>
                  <TableCell>{r.validator ?? "—"}</TableCell>
                  <TableCell>
                    <Typography variant="caption" color={rejected ? "error.light" : "text.secondary"}>
                      {r.reason ?? "—"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {r.created_at ? new Date(r.created_at).toLocaleString("pt-BR") : "—"}
                    </Typography>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

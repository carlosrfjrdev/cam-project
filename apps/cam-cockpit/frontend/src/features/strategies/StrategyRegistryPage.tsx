/**
 * Strategy Registry — TASK-U016 (BL-UI-3).
 *
 * Lista estratégias com status (draft→retired), is_active e EvidencePack
 * resumido. Promover sem evidência mostra erro (EVIDENCE_REQUIRED). Ativar é
 * gated (confirmação). Sem botão de ordem (Kevin, Art. 35º).
 */
import { useState } from "react";
import {
  Box, Typography, Paper, Stack, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Button, Dialog, DialogTitle, DialogContent,
  DialogActions, Alert,
} from "@mui/material";
import HubIcon from "@mui/icons-material/Hub";
import { useStrategies, useActivateStrategy, type Strategy } from "./useStrategies";

const STATUS_COLOR: Record<string, "default" | "info" | "warning" | "success"> = {
  draft: "default",
  backtested: "info",
  walk_forward_ok: "info",
  paper_ok: "warning",
  demo_ok: "warning",
  real_authorized: "success",
  retired: "default",
};

export function StrategyRegistryPage() {
  const { data, isLoading } = useStrategies();
  const activate = useActivateStrategy();
  const [confirm, setConfirm] = useState<Strategy | null>(null);
  const rows = data ?? [];

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <HubIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Strategy Registry</Typography>
      </Stack>

      <Alert severity="info" sx={{ mb: 2 }}>
        Promoção de status exige Evidence Pack (Arts. 28º/29º). Ativação é
        governada — confirmação obrigatória. Nenhuma ação envia ordem.
      </Alert>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Estratégia</TableCell>
              <TableCell>Ativo</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Ativa?</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                    {isLoading ? "Carregando…" : "Nenhuma estratégia registrada."}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {rows.map((s) => (
              <TableRow key={s.id} data-testid="strategy-row">
                <TableCell>
                  {s.name} <Typography component="span" variant="caption" color="text.secondary">v{s.version}</Typography>
                </TableCell>
                <TableCell>{s.asset}</TableCell>
                <TableCell>
                  <Chip label={s.status} size="small" color={STATUS_COLOR[s.status] ?? "default"} />
                </TableCell>
                <TableCell>
                  {s.is_active
                    ? <Chip label="ATIVA" size="small" color="success" />
                    : <Typography variant="caption" color="text.secondary">—</Typography>}
                </TableCell>
                <TableCell align="right">
                  <Button
                    size="small"
                    variant="outlined"
                    disabled={s.is_active}
                    onClick={() => setConfirm(s)}
                  >
                    Ativar
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {activate.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {(activate.error as Error)?.message ?? "Falha ao ativar."}
        </Alert>
      )}

      <Dialog open={confirm !== null} onClose={() => setConfirm(null)}>
        <DialogTitle>Ativar estratégia?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Ativar <b>{confirm?.name}</b> desativa a estratégia ativa atual. Esta
            ação é governada — confirme.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirm(null)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (confirm) activate.mutate(confirm.id);
              setConfirm(null);
            }}
          >
            Confirmar ativação
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

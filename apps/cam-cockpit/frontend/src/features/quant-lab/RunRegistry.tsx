/**
 * Run Registry (0.5.7) — histórico de análises de research com veredito e o
 * contador GLOBAL de tentativas (alimenta a deflação estatística). READ-ONLY.
 *
 * Honestidade (Don/Voltaire): o contador global em destaque lembra que toda
 * busca soma ao denominador do DSR — a estatística honesta fica inevitável.
 */
import { useQuery } from "@tanstack/react-query";
import {
  Box, Chip, CircularProgress, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, Typography,
} from "@mui/material";
import { api } from "../../api/client";

interface RunRow {
  id: number;
  lens: string | null;
  mode: string | null;
  sources: string[];
  target: string;
  delta_grid: number[];
  n_trials: number;
  status: string;
  created_at: string;
}

const statusChip = (s: string) => {
  if (s === "done") return <Chip size="small" color="success" label="com sobrevivente" />;
  if (s === "killed") return <Chip size="small" color="error" variant="outlined" label="morta (FDR)" />;
  if (s === "insufficient_data")
    return <Chip size="small" variant="outlined" label="dado insuficiente" />;
  return <Chip size="small" label={s} />;
};

export function RunRegistry() {
  const runs = useQuery({
    queryKey: ["research", "runs"],
    queryFn: () => api.get<{ runs: RunRow[] }>("/research/runs"),
    refetchInterval: 10_000,
  });
  const trials = useQuery({
    queryKey: ["research", "trials"],
    queryFn: () => api.get<{ total_trials: number }>("/research/stats/trials"),
    refetchInterval: 10_000,
  });

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <Typography variant="h6">Registro de análises</Typography>
        {trials.data && (
          <Chip
            size="small"
            color="warning"
            label={`tentativas acumuladas: ${trials.data.total_trials}`}
          />
        )}
      </Box>
      <Typography variant="caption" color="text.secondary">
        Toda análise soma ao denominador do DSR. Runs são imutáveis (evidência preservada).
      </Typography>

      {runs.isLoading && <CircularProgress size={20} sx={{ mt: 1 }} />}
      {runs.data && runs.data.runs.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Nenhuma análise ainda.
        </Typography>
      )}
      {runs.data && runs.data.runs.length > 0 && (
        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>#</TableCell>
              <TableCell>Alvo</TableCell>
              <TableCell>Fontes</TableCell>
              <TableCell align="right">δ máx</TableCell>
              <TableCell align="right">tentativas</TableCell>
              <TableCell>veredito</TableCell>
              <TableCell>quando</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {runs.data.runs.map((r) => (
              <TableRow key={r.id}>
                <TableCell>{r.id}</TableCell>
                <TableCell>{r.target}</TableCell>
                <TableCell>{(r.sources ?? []).length}</TableCell>
                <TableCell align="right">
                  {r.delta_grid?.length ? Math.max(...r.delta_grid) : "—"}
                </TableCell>
                <TableCell align="right">{r.n_trials}</TableCell>
                <TableCell>{statusChip(r.status)}</TableCell>
                <TableCell>{r.created_at?.slice(0, 16) ?? "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Paper>
  );
}

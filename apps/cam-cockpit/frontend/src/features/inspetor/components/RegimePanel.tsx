/**
 * Bloco de Regime de Markov (read-only) — R-21/R-26. Só para ações.
 * Caveats SEMPRE visíveis (não escondidos). "histórico, não preditivo".
 */
import {
  Alert, Box, Chip, Table, TableBody, TableCell, TableHead, TableRow, Typography,
} from "@mui/material";
import type { RegimeResponse } from "../api";

const STATE_COLOR: Record<string, "success" | "warning" | "error" | "default"> = {
  Bull: "success",
  Sideways: "warning",
  Bear: "error",
};

export function RegimePanel({ data }: { data: RegimeResponse }) {
  if (data.insufficient_data) {
    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Regime de Mercado
        </Typography>
        <Alert severity="info">
          Dados insuficientes. Carregue candles diários (timeframe D1) deste ativo para
          computar o regime.
        </Alert>
      </Box>
    );
  }

  const m = data.transition_matrix ?? [];
  const states = data.states ?? ["Bull", "Sideways", "Bear"];

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        <Typography variant="h6">Regime de Mercado</Typography>
        <Chip
          size="small"
          label={data.current_state ?? "—"}
          color={STATE_COLOR[data.current_state ?? ""] ?? "default"}
        />
        <Chip size="small" variant="outlined" label="histórico, não preditivo" />
      </Box>

      <Box sx={{ display: "flex", gap: 3, flexWrap: "wrap", mb: 2 }}>
        <Box>
          <Typography variant="caption" color="text.secondary">Sinal (P(Bull)−P(Bear))</Typography>
          <Typography variant="h6">{data.signal?.toFixed(3) ?? "—"}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Sharpe (walk-forward, bruto)</Typography>
          <Typography variant="h6">{data.walk_forward?.sharpe?.toFixed(2) ?? "—"}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">Max Drawdown</Typography>
          <Typography variant="h6">
            {data.walk_forward?.max_drawdown != null
              ? `${(data.walk_forward.max_drawdown * 100).toFixed(1)}%`
              : "—"}
          </Typography>
        </Box>
      </Box>

      <Typography variant="subtitle2">Matriz de transição (de → para)</Typography>
      <Table size="small" sx={{ maxWidth: 420, mb: 1 }}>
        <TableHead>
          <TableRow>
            <TableCell />
            {states.map((s) => (
              <TableCell key={s} align="right">{s}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {m.map((row, i) => (
            <TableRow key={states[i]}>
              <TableCell>{states[i]}</TableCell>
              {row.map((v, j) => (
                <TableCell key={j} align="right">{(v * 100).toFixed(0)}%</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {data.stationary && (
        <Typography variant="body2" color="text.secondary">
          Mix de longo prazo:{" "}
          {Object.entries(data.stationary)
            .map(([s, v]) => `${s} ${(v * 100).toFixed(0)}%`)
            .join(" · ")}
        </Typography>
      )}

      <Alert severity="warning" sx={{ mt: 2 }}>
        Rótulo é tendência <b>defasada</b>; janelas sobrepostas autocorrelacionam (persistência
        em parte é artefato). Backtest <b>não modela custo/spread</b> (Sharpe bruto). Regime diário
        é filtro macro grosseiro. Leitura, <b>não</b> sinal de execução.
      </Alert>
      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
        {data.attribution}
      </Typography>
    </Box>
  );
}

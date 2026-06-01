/**
 * Histórico de dividendos + 2 estimativas rotuladas (R-14).
 */
import {
  Box, Chip, Table, TableBody, TableCell, TableHead, TableRow, Typography,
} from "@mui/material";
import type { Fundamentals } from "../api";

function money(v: number | null): string {
  return v === null || v === undefined ? "—" : `R$ ${v.toFixed(2)}`;
}
function pct(v: number | null): string {
  return v === null || v === undefined ? "—" : `${(v * 100).toFixed(2)}%`;
}

export function DividendsPanel({ data }: { data: Fundamentals }) {
  const proj = data.dividend_projection;
  const history = (data.dividends_history ?? []).slice(0, 12);

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Dividendos
      </Typography>

      {proj && (
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 2 }}>
          {[
            { title: "Run-rate 12m", m: proj.run_rate_12m },
            { title: "DY-médio 3–5a", m: proj.dy_avg_3_5y },
          ].map(({ title, m }) => (
            <Box
              key={title}
              sx={{ border: "1px solid", borderColor: "divider", borderRadius: 1, p: 1.5, minWidth: 170 }}
            >
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Typography variant="subtitle2">{title}</Typography>
                <Chip size="small" label="estimativa" color="warning" variant="outlined" />
              </Box>
              <Typography variant="h6">{money(m.annual)}/ano</Typography>
              <Typography variant="caption" color="text.secondary">
                yield {pct(m.yield)}
              </Typography>
            </Box>
          ))}
        </Box>
      )}

      {history.length > 0 ? (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Data</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell align="right">Valor</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.map((d, i) => (
              <TableRow key={`${d.date}-${i}`}>
                <TableCell>{d.date ?? "—"}</TableCell>
                <TableCell>{d.type}</TableCell>
                <TableCell align="right">{money(d.value)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Sem histórico de proventos disponível.
        </Typography>
      )}
    </Box>
  );
}

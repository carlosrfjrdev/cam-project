/**
 * Painel de análise Lead-Lag (0.5.2) — lança run de correlação defasada e
 * exibe o perfil C(δ) por fonte. READ-ONLY, vocabulário de pesquisa.
 *
 * Honestidade na UI (Don/Voltaire): contador de tentativas em destaque;
 * "dado insuficiente" é estado distinto (chip cinza), não "sem edge".
 */
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Alert, Box, Button, Chip, MenuItem, Paper, Stack, Table, TableBody,
  TableCell, TableHead, TableRow, TextField, Typography,
} from "@mui/material";
import { fetchRun, postRun, type CellResult, type RunSummary } from "./api";

const TFS = ["M1", "M5", "M15", "M30", "H1"];

export function LeadLagAnalysis({ universe }: { universe: string[] }) {
  const [target, setTarget] = useState(universe[2] ?? "PETR4");
  const [timeframe, setTimeframe] = useState("M5");
  const [maxDelta, setMaxDelta] = useState(50);
  const [summary, setSummary] = useState<RunSummary | null>(null);
  const [cells, setCells] = useState<CellResult[]>([]);

  const sources = universe.filter((s) => s !== target);

  const run = useMutation({
    mutationFn: async () => {
      const s = await postRun({
        sources,
        target,
        delta_grid: Array.from({ length: maxDelta }, (_, i) => i + 1),
        timeframe,
      });
      const r = await fetchRun(s.run_id);
      return { s, cells: r.results };
    },
    onSuccess: ({ s, cells: c }) => {
      setSummary(s);
      setCells(c);
    },
  });

  // por fonte: prioriza SURVIVOR; senão a melhor |C| medida (descritivo, não sinal)
  const bestBySource = new Map<string, CellResult>();
  for (const c of cells) {
    if (c.correlation === null) continue;
    const cur = bestBySource.get(c.source);
    const better =
      !cur ||
      (c.verdict === "SURVIVOR" && cur.verdict !== "SURVIVOR") ||
      (c.verdict === cur.verdict &&
        Math.abs(c.correlation) > Math.abs(cur.correlation ?? 0));
    if (better) bestBySource.set(c.source, c);
  }

  const verdictChip = (v: string) => {
    if (v === "SURVIVOR")
      return <Chip size="small" color="success" label="sobrevivente" />;
    if (v === "KILLED")
      return <Chip size="small" color="error" variant="outlined" label="morta (FDR)" />;
    return <Chip size="small" variant="outlined" label="dado insuficiente" />;
  };

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Lead-Lag — correlação defasada (0.5.2)
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Hipótese: qual fonte lidera o alvo, e com qual defasagem δ (em barras).
        Evidência descritiva — não é sinal de operação.
      </Typography>

      <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1, flexWrap: "wrap" }}>
        <TextField
          select size="small" label="Alvo" value={target}
          onChange={(e) => setTarget(e.target.value)} sx={{ minWidth: 120 }}
        >
          {universe.map((s) => (
            <MenuItem key={s} value={s}>{s}</MenuItem>
          ))}
        </TextField>
        <TextField
          select size="small" label="Timeframe" value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)} sx={{ minWidth: 100 }}
        >
          {TFS.map((t) => (
            <MenuItem key={t} value={t}>{t}</MenuItem>
          ))}
        </TextField>
        <TextField
          size="small" type="number" label="δ máx (barras)" value={maxDelta}
          onChange={(e) => setMaxDelta(Math.max(1, Number(e.target.value)))}
          sx={{ width: 130 }}
        />
        <Button variant="contained" onClick={() => run.mutate()} disabled={run.isPending}>
          {run.isPending ? "Analisando…" : "Analisar"}
        </Button>
      </Stack>

      {run.isError && (
        <Alert severity="warning" sx={{ mt: 1 }}>Falha na análise.</Alert>
      )}

      {summary && (
        <Box sx={{ mt: 2 }}>
          <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
            <Chip size="small" label={`run #${summary.run_id}`} />
            <Chip size="small" color="info" label={`tentativas: ${summary.n_trials}`} />
            <Chip
              size="small"
              color={summary.survivors > 0 ? "success" : "default"}
              label={`sobreviventes: ${summary.survivors}`}
            />
            <Chip
              size="small"
              color={summary.status === "done" ? "success" : "default"}
              label={summary.status}
            />
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Fontes → {summary.target} @ {summary.timeframe}. O contador de tentativas
            entra na deflação estatística (0.5.3).
          </Typography>

          <Table size="small" sx={{ mt: 1 }}>
            <TableHead>
              <TableRow>
                <TableCell>Fonte</TableCell>
                <TableCell align="right">melhor |C|</TableCell>
                <TableCell align="right">δ (barras)</TableCell>
                <TableCell align="right">n</TableCell>
                <TableCell align="right">DSR</TableCell>
                <TableCell>veredito</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sources.map((src) => {
                const best = bestBySource.get(src);
                if (!best) {
                  return (
                    <TableRow key={src}>
                      <TableCell>{src}</TableCell>
                      <TableCell align="right">—</TableCell>
                      <TableCell align="right">—</TableCell>
                      <TableCell align="right">—</TableCell>
                      <TableCell align="right">—</TableCell>
                      <TableCell>{verdictChip("INSUFFICIENT_DATA")}</TableCell>
                    </TableRow>
                  );
                }
                return (
                  <TableRow key={src}>
                    <TableCell>{src}</TableCell>
                    <TableCell align="right">{best.correlation?.toFixed(3) ?? "—"}</TableCell>
                    <TableCell align="right">{best.delta_or_tau}</TableCell>
                    <TableCell align="right">{best.n_samples}</TableCell>
                    <TableCell align="right">
                      {best.dsr != null ? best.dsr.toFixed(2) : "—"}
                    </TableCell>
                    <TableCell>{verdictChip(best.verdict)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          <Alert severity="info" sx={{ mt: 2 }}>
            <b>Sobrevivente</b> = correlação que passou o controle de falsa descoberta (FDR)
            entre todas as células testadas. <b>Morta (FDR)</b> = mediu correlação, mas não
            resistiu ao denominador de tentativas. <b>DSR</b> deflaciona o data-snooping.
            Correlação ≠ edge: o event study líquido + walk-forward + mata-Epps (HY) entram
            na promoção a paper. Matar é evidência (Voltaire).
          </Alert>
        </Box>
      )}
    </Paper>
  );
}

/**
 * Market Data / Provenance — TASK-U018 (BL-UI-3).
 *
 * Lotes ingeridos (fonte, ts, tick_count, hash, quality_flags) + catálogo de
 * instrumentos (WIN/WDO com point_value). Flags problemáticas destacadas.
 */
import {
  Box, Typography, Paper, Stack, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip,
} from "@mui/material";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import { useProvenance, useInstruments, type Provenance } from "./useMarketData";

const PROBLEM_FLAGS = ["has_gaps", "zero_volume", "out_of_hours"];

function QualityFlags({ flags }: { flags: Provenance["quality_flags"] }) {
  const entries = Object.entries(flags ?? {}).filter(([, v]) => v === true);
  if (entries.length === 0) {
    return <Chip label="OK" size="small" color="success" variant="outlined" />;
  }
  return (
    <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
      {entries.map(([k]) => (
        <Chip
          key={k}
          label={k}
          size="small"
          color={PROBLEM_FLAGS.includes(k) ? "warning" : "default"}
          data-testid="quality-flag"
          data-problem={PROBLEM_FLAGS.includes(k) ? "true" : "false"}
        />
      ))}
    </Stack>
  );
}

export function MarketDataPage() {
  const { data: prov } = useProvenance();
  const { data: instruments } = useInstruments();
  const provenance = prov ?? [];
  const instr = instruments ?? [];

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <ShowChartIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Market Data</Typography>
      </Stack>

      <Typography variant="h6" sx={{ mb: 1 }}>Instrumentos</Typography>
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Ticker</TableCell>
              <TableCell>Classe</TableCell>
              <TableCell>Bolsa</TableCell>
              <TableCell align="right">Point Value</TableCell>
              <TableCell>Ativo</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {instr.length === 0 && (
              <TableRow><TableCell colSpan={5}>
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>Nenhum instrumento.</Typography>
              </TableCell></TableRow>
            )}
            {instr.map((i) => (
              <TableRow key={i.ticker} data-testid="instrument-row">
                <TableCell>{i.ticker}</TableCell>
                <TableCell>{i.asset_class}</TableCell>
                <TableCell>{i.exchange}</TableCell>
                <TableCell align="right" sx={{ fontFamily: (t) => t.cam.fontMono }}>{i.point_value}</TableCell>
                <TableCell>{i.active ? "sim" : "não"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="h6" sx={{ mb: 1 }}>Proveniência de lotes</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Fonte</TableCell>
              <TableCell>Ativo</TableCell>
              <TableCell align="right">Ticks</TableCell>
              <TableCell>Hash</TableCell>
              <TableCell>Quality flags</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {provenance.length === 0 && (
              <TableRow><TableCell colSpan={5}>
                <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>Nenhum lote ingerido.</Typography>
              </TableCell></TableRow>
            )}
            {provenance.map((p) => (
              <TableRow key={p.import_id} data-testid="provenance-row">
                <TableCell>{p.source}</TableCell>
                <TableCell>{p.asset}</TableCell>
                <TableCell align="right">{p.tick_count}</TableCell>
                <TableCell sx={{ fontFamily: (t) => t.cam.fontMono, maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {p.hash}
                </TableCell>
                <TableCell><QualityFlags flags={p.quality_flags} /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

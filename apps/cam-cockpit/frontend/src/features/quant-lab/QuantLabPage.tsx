/**
 * Quant Lab — Research Lane (Lead-Lag) · UI-R0 (SPEC v0.5.1).
 *
 * READ-ONLY, isolado do Cockpit Live. Badge RESEARCH permanente (Don). Data
 * Health ANTES de qualquer leitura otimista — sem heatmap nesta sub-versão.
 * Vocabulário de pesquisa; ZERO affordance de ordem/Risk Engine.
 */
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert, Box, Button, Chip, CircularProgress, Divider, Paper, Stack,
  Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography,
} from "@mui/material";
import ScienceIcon from "@mui/icons-material/Science";
import {
  fetchDataHealth, postIngest, type IngestResult,
} from "./api";
import { LeadLagAnalysis } from "./LeadLagAnalysis";

const DEFAULT_UNIVERSE = "WIN$, WDO$, VALE3, ITUB4, PETR4, AXIA3, BBDC4, B3SA3";

export function QuantLabPage() {
  const qc = useQueryClient();
  const [universe, setUniverse] = useState(DEFAULT_UNIVERSE);
  const [lastIngest, setLastIngest] = useState<IngestResult | null>(null);

  const health = useQuery({
    queryKey: ["research", "data-health"],
    queryFn: fetchDataHealth,
    retry: false,
  });

  const ingest = useMutation({
    mutationFn: () =>
      postIngest({
        sources: universe.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean),
        with_ticks: true,
      }),
    onSuccess: (res) => {
      setLastIngest(res);
      qc.invalidateQueries({ queryKey: ["research", "data-health"] });
    },
  });

  return (
    <Box sx={{ px: "5%", py: 2, width: "100%", boxSizing: "border-box" }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
        <ScienceIcon color="secondary" />
        <Typography variant="h5">Quant Lab</Typography>
        <Chip size="small" color="secondary" label="RESEARCH" />
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Laboratório de pesquisa Lead-Lag — descoberta estatística read-only.
        Isolado do Cockpit Live. Nenhuma ação aqui envia ordem.
      </Typography>

      {/* Ingestão parametrizável (UNIV) */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Ingestão de dados (R0)
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Universo (parametrizável) — extrai do MT5, persiste em research_*, deriva barras.
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
          <TextField
            size="small"
            fullWidth
            value={universe}
            onChange={(e) => setUniverse(e.target.value)}
            label="Símbolos (vírgula)"
          />
          <Button
            variant="contained"
            onClick={() => ingest.mutate()}
            disabled={ingest.isPending}
          >
            {ingest.isPending ? "Ingerindo…" : "Ingerir do MT5"}
          </Button>
        </Stack>
        {ingest.isError && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            Falha na ingestão. Verifique se o MT5 está aberto e o EA cam_bridge atachado.
          </Alert>
        )}
        {lastIngest && (
          <Alert severity="success" sx={{ mt: 1 }}>
            Snapshot #{lastIngest.snapshot_id} — {lastIngest.total_bars} barras,{" "}
            {lastIngest.total_ticks} ticks. hash {lastIngest.composite_hash.slice(0, 12)}…
          </Alert>
        )}
      </Paper>

      {/* Data Health ANTES de qualquer análise (Don) */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Data Health
        </Typography>
        {health.isLoading && <CircularProgress size={20} />}
        {health.isError && (
          <Typography variant="body2" color="text.secondary">
            Sem dados de research ainda — rode a ingestão acima.
          </Typography>
        )}
        {health.data && (
          <>
            <Typography variant="subtitle2" sx={{ mt: 1 }}>
              Cobertura de barras
            </Typography>
            {health.data.bars.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Nenhuma barra ingerida. Estado: vazio (não é "sem edge" — é sem dado).
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Símbolo</TableCell>
                    <TableCell>TF</TableCell>
                    <TableCell align="right">Barras</TableCell>
                    <TableCell>Primeira</TableCell>
                    <TableCell>Última</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {health.data.bars.map((b) => (
                    <TableRow key={`${b.symbol}-${b.timeframe}`}>
                      <TableCell>{b.symbol}</TableCell>
                      <TableCell>{b.timeframe}</TableCell>
                      <TableCell align="right">{b.n}</TableCell>
                      <TableCell>{b.first_ts?.slice(0, 16) ?? "—"}</TableCell>
                      <TableCell>{b.last_ts?.slice(0, 16) ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2">
              Liquidez de tick por ativo (agressor)
            </Typography>
            {health.data.ticks.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Nenhum tick ingerido.
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Símbolo</TableCell>
                    <TableCell align="right">Ticks</TableCell>
                    <TableCell align="right">Com agressor</TableCell>
                    <TableCell align="right">% agressor</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {health.data.ticks.map((t) => (
                    <TableRow key={t.symbol}>
                      <TableCell>{t.symbol}</TableCell>
                      <TableCell align="right">{t.n_ticks}</TableCell>
                      <TableCell align="right">{t.n_aggressor}</TableCell>
                      <TableCell align="right">
                        {t.n_ticks ? ((t.n_aggressor / t.n_ticks) * 100).toFixed(0) : 0}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </>
        )}
      </Paper>

      {/* 0.5.2 — análise de lead-lag sobre os dados ingeridos */}
      {health.data && health.data.bars.length > 0 && (
        <LeadLagAnalysis
          universe={universe.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean)}
        />
      )}
    </Box>
  );
}

/**
 * Dataset — ingestão de dados do MT5 (candles + ticks) para o sistema.
 *
 * Centraliza a ENTRADA de dados (antes vivia no Quant Lab). O /lab mantém só as
 * ANÁLISES. Candles paginados (cam_bridge 0.4.1) + ticks em bulk (GET_TICKS).
 */
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert, Button, Checkbox, Divider, FormControlLabel, Paper, Stack,
  Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography,
} from "@mui/material";
import StorageIcon from "@mui/icons-material/Storage";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { fetchDataHealth, postIngest, type IngestResult } from "../quant-lab/api";

const DEFAULT_UNIVERSE = "WINM26";

export function DatasetPage() {
  const qc = useQueryClient();
  const [universe, setUniverse] = useState(DEFAULT_UNIVERSE);
  const [count, setCount] = useState(40000);
  const [withTicks, setWithTicks] = useState(false);
  const [tickCount, setTickCount] = useState(500000);
  const [lastIngest, setLastIngest] = useState<IngestResult | null>(null);

  const health = useQuery({
    queryKey: ["dataset", "data-health"],
    queryFn: fetchDataHealth,
    retry: false,
  });

  const ingest = useMutation({
    mutationFn: () =>
      postIngest({
        sources: universe.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean),
        count,
        with_ticks: withTicks,
        tick_count: tickCount,
      }),
    onSuccess: (res) => {
      setLastIngest(res);
      qc.invalidateQueries({ queryKey: ["dataset", "data-health"] });
    },
  });

  return (
    <PageContainer>
      <PageHeader title="Dataset" icon={<StorageIcon color="secondary" />} />
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Ingestão de dados do MT5 para o sistema — candles (M1 + derivadas) e ticks.
        Fonte única de entrada de dados; as análises vivem no Quant Lab.
      </Typography>

      {/* Ingestão */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Ingerir do MT5
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Extrai do MT5 (via cam_bridge), persiste M1 canônico + derivadas, e os
          ticks (com agressor) quando marcado. Requer MT5 + EA cam_bridge aberto.
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1, flexWrap: "wrap", gap: 1 }}>
          <TextField
            size="small" sx={{ minWidth: 220, flex: 1 }} value={universe}
            onChange={(e) => setUniverse(e.target.value)} label="Símbolos (vírgula)"
          />
          <TextField
            size="small" type="number" label="Barras (M1)" value={count}
            onChange={(e) => setCount(Number(e.target.value))} sx={{ width: 130 }}
          />
          <TextField
            size="small" type="number" label="Ticks (máx)" value={tickCount}
            onChange={(e) => setTickCount(Number(e.target.value))}
            sx={{ width: 130 }} disabled={!withTicks}
          />
          <Button
            variant="contained" onClick={() => ingest.mutate()} disabled={ingest.isPending}
          >
            {ingest.isPending ? "Ingerindo…" : "Ingerir"}
          </Button>
        </Stack>
        <FormControlLabel
          control={
            <Checkbox size="small" checked={withTicks}
              onChange={(e) => setWithTicks(e.target.checked)} />
          }
          label="Incluir ticks (bulk via GET_TICKS — pesado; só p/ análises de fluxo/Lead-Lag)"
          sx={{ mt: 0.5 }}
        />
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

      {/* Data Health */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Data Health
        </Typography>
        {health.isError && (
          <Typography variant="body2" color="text.secondary">
            Sem dados ainda — rode a ingestão acima.
          </Typography>
        )}
        {health.data && (
          <>
            <Typography variant="subtitle2" sx={{ mt: 1 }}>Cobertura de barras</Typography>
            {health.data.bars.length === 0 ? (
              <Typography variant="body2" color="text.secondary">Nenhuma barra ingerida.</Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Símbolo</TableCell><TableCell>TF</TableCell>
                    <TableCell align="right">Barras</TableCell>
                    <TableCell>Primeira</TableCell><TableCell>Última</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {health.data.bars.map((b) => (
                    <TableRow key={`${b.symbol}-${b.timeframe}`}>
                      <TableCell>{b.symbol}</TableCell><TableCell>{b.timeframe}</TableCell>
                      <TableCell align="right">{b.n}</TableCell>
                      <TableCell>{b.first_ts?.slice(0, 16) ?? "—"}</TableCell>
                      <TableCell>{b.last_ts?.slice(0, 16) ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2">Liquidez de tick por ativo (agressor)</Typography>
            {health.data.ticks.length === 0 ? (
              <Typography variant="body2" color="text.secondary">Nenhum tick ingerido.</Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Símbolo</TableCell><TableCell align="right">Ticks</TableCell>
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
    </PageContainer>
  );
}

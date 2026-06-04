/**
 * Dataset — ingestão de dados do MT5 (candles + ticks) para o sistema.
 *
 * Centraliza a ENTRADA de dados (antes vivia no Quant Lab). O /lab mantém só as
 * ANÁLISES. Candles paginados (cam_bridge 0.4.1) + ticks em bulk (GET_TICKS).
 */
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert, Button, Checkbox, Dialog, DialogActions, DialogContent,
  DialogContentText, DialogTitle, Divider, FormControlLabel, IconButton,
  Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField,
  Tooltip, Typography,
} from "@mui/material";
import StorageIcon from "@mui/icons-material/Storage";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import {
  fetchDataHealth, postIngest, purgeDataset, type IngestResult,
} from "../quant-lab/api";

const DEFAULT_UNIVERSE = "WINM26";

export function DatasetPage() {
  const qc = useQueryClient();
  const [universe, setUniverse] = useState(DEFAULT_UNIVERSE);
  const [count, setCount] = useState(40000);
  const [withTicks, setWithTicks] = useState(false);
  const [tickCount, setTickCount] = useState(500000);
  const [lastIngest, setLastIngest] = useState<IngestResult | null>(null);
  const [confirmAll, setConfirmAll] = useState(false);

  const health = useQuery({
    queryKey: ["dataset", "data-health"],
    queryFn: fetchDataHealth,
    retry: false,
  });

  const purge = useMutation({
    mutationFn: (symbol?: string) => purgeDataset(symbol),
    onSuccess: () => {
      setConfirmAll(false);
      qc.invalidateQueries({ queryKey: ["dataset", "data-health"] });
    },
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
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
          <Typography variant="h6">Data Health</Typography>
          <Button
            size="small" color="error" variant="outlined"
            startIcon={<DeleteForeverIcon />}
            onClick={() => setConfirmAll(true)}
            disabled={purge.isPending || !health.data || health.data.bars.length === 0}
          >
            Limpar tudo
          </Button>
        </Stack>
        {purge.isError && (
          <Alert severity="warning" sx={{ mb: 1 }}>Falha ao limpar o dataset.</Alert>
        )}
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
                    <TableCell />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {health.data.bars.map((b) => (
                    <TableRow key={`${b.symbol}-${b.timeframe}`}>
                      <TableCell>{b.symbol}</TableCell><TableCell>{b.timeframe}</TableCell>
                      <TableCell align="right">{b.n}</TableCell>
                      <TableCell>{b.first_ts?.slice(0, 16) ?? "—"}</TableCell>
                      <TableCell>{b.last_ts?.slice(0, 16) ?? "—"}</TableCell>
                      <TableCell align="right" sx={{ py: 0 }}>
                        <Tooltip title={`Limpar ${b.symbol} (todos os TFs + ticks)`}>
                          <span>
                            <IconButton
                              size="small" color="error"
                              onClick={() => purge.mutate(b.symbol)}
                              disabled={purge.isPending}
                            >
                              <DeleteOutlineIcon fontSize="small" />
                            </IconButton>
                          </span>
                        </Tooltip>
                      </TableCell>
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

      <Dialog open={confirmAll} onClose={() => setConfirmAll(false)}>
        <DialogTitle>Limpar TODO o dataset?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Remove todas as barras e ticks de todos os papéis (research_bars +
            research_ticks). As análises/runs do Quant Lab são mantidas. Ação
            irreversível.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmAll(false)}>Cancelar</Button>
          <Button
            color="error" variant="contained"
            onClick={() => purge.mutate(undefined)}
            disabled={purge.isPending}
          >
            {purge.isPending ? "Limpando…" : "Limpar tudo"}
          </Button>
        </DialogActions>
      </Dialog>
    </PageContainer>
  );
}

import { useState, useRef } from "react";
import {
  Box, Typography, Paper, Stack, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, TextField, MenuItem, Select,
  FormControl, InputLabel, Alert, CircularProgress,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { PnlDisplay } from "../../_shared/components/PnlDisplay";
import type { JournalEntry, ImportResult } from "../../api/types";

const ASSET_OPTIONS = ["WIN", "WDO"];
const DIRECTION_OPTIONS = ["LONG", "SHORT"];

function directionColor(dir: string) {
  return dir === "LONG" ? "success" : "error";
}

// Valor do ponto B3: WIN R$ 0,20 · WDO R$ 10,00 (por contrato)
function pointValue(asset: string): number {
  return asset === "WIN" ? 0.2 : 10;
}

function calculateResultGross(asset: string, direction: string, contracts: number, entryPrice: number, exitPrice: number): number {
  const delta = direction === "LONG" ? exitPrice - entryPrice : entryPrice - exitPrice;
  return delta * contracts * pointValue(asset);
}

export function JournalPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [importMessage, setImportMessage] = useState<ImportResult | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [form, setForm] = useState({
    trade_date: new Date().toISOString().split("T")[0],
    asset: "WIN",
    direction: "LONG",
    contracts: 1,
    entry_price: 0,
    exit_price: 0,
    costs: 0,
    strategy: "",
    setup: "",
    notes: "",
  });

  const { data: entries, isLoading, error } = useQuery({
    queryKey: ["journal-entries"],
    queryFn: () => api.get<JournalEntry[]>("/journal/entries"),
    retry: false,
  });

  const createEntry = useMutation({
    mutationFn: (data: typeof form) => {
      const result_gross = calculateResultGross(data.asset, data.direction, data.contracts, data.entry_price, data.exit_price);
      const payload = {
        asset: data.asset,
        direction: data.direction,
        contracts: data.contracts,
        entry_price: data.entry_price,
        exit_price: data.exit_price,
        result_gross,
        costs: data.costs,
        strategy: data.strategy,
        setup: data.setup || data.strategy || "manual",
        emotional_note: data.notes || null,
      };
      return api.post("/journal/entries", payload);
    },
    onSuccess: () => {
      setSubmitError(null);
      qc.invalidateQueries({ queryKey: ["journal-entries"] });
    },
    onError: (err: Error) => setSubmitError(err.message),
  });

  const importCsv = useMutation({
    mutationFn: (file: File) => api.uploadFile<ImportResult>("/journal/import-csv", file),
    onSuccess: (result) => {
      setImportMessage(result);
      qc.invalidateQueries({ queryKey: ["journal-entries"] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) importCsv.mutate(file);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" fontWeight={700}>Journal</Typography>
        <Stack direction="row" spacing={2}>
          <input ref={fileRef} type="file" accept=".csv" hidden onChange={handleFileChange} />
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => fileRef.current?.click()}
            disabled={importCsv.isPending}
          >
            Importar CSV Profit
          </Button>
        </Stack>
      </Stack>

      {importMessage && (
        <Alert severity="info" sx={{ mb: 2 }} onClose={() => setImportMessage(null)}>
          Importação concluída: {importMessage.imported} importadas, {importMessage.duplicates} duplicatas ignoradas, {importMessage.errors} erros
        </Alert>
      )}

      {submitError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSubmitError(null)}>
          Falha ao registrar entrada: {submitError}
        </Alert>
      )}

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Não foi possível carregar entradas: {(error as Error).message}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Nova Entrada Manual</Typography>
        <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
          <TextField label="Data" type="date" value={form.trade_date} onChange={e => setForm(f => ({ ...f, trade_date: e.target.value }))} size="small" />
          <FormControl size="small" sx={{ minWidth: 80 }}>
            <InputLabel>Ativo</InputLabel>
            <Select value={form.asset} label="Ativo" onChange={e => setForm(f => ({ ...f, asset: e.target.value }))}>
              {ASSET_OPTIONS.map(a => <MenuItem key={a} value={a}>{a}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 80 }}>
            <InputLabel>Direção</InputLabel>
            <Select value={form.direction} label="Direção" onChange={e => setForm(f => ({ ...f, direction: e.target.value }))}>
              {DIRECTION_OPTIONS.map(d => <MenuItem key={d} value={d}>{d}</MenuItem>)}
            </Select>
          </FormControl>
          <TextField label="Contratos" type="number" value={form.contracts} onChange={e => setForm(f => ({ ...f, contracts: Number(e.target.value) }))} size="small" sx={{ width: 100 }} inputProps={{ min: 1, max: 2 }} />
          <TextField label="Entrada" type="number" value={form.entry_price} onChange={e => setForm(f => ({ ...f, entry_price: Number(e.target.value) }))} size="small" sx={{ width: 120 }} />
          <TextField label="Saída" type="number" value={form.exit_price} onChange={e => setForm(f => ({ ...f, exit_price: Number(e.target.value) }))} size="small" sx={{ width: 120 }} />
          <TextField label="Custos" type="number" value={form.costs} onChange={e => setForm(f => ({ ...f, costs: Number(e.target.value) }))} size="small" sx={{ width: 100 }} />
          <TextField label="Estratégia" value={form.strategy} onChange={e => setForm(f => ({ ...f, strategy: e.target.value }))} size="small" sx={{ width: 160 }} />
          <TextField label="Setup" value={form.setup} onChange={e => setForm(f => ({ ...f, setup: e.target.value }))} size="small" sx={{ width: 140 }} placeholder="A+ / B / outro" />
          <TextField label="Notas" value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} size="small" sx={{ width: 200 }} />
          <Button variant="contained" onClick={() => createEntry.mutate(form)} disabled={createEntry.isPending}>
            Registrar
          </Button>
        </Stack>
      </Paper>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Data</TableCell>
              <TableCell>Ativo</TableCell>
              <TableCell>Dir.</TableCell>
              <TableCell align="right">Contratos</TableCell>
              <TableCell align="right">Entrada</TableCell>
              <TableCell align="right">Saída</TableCell>
              <TableCell align="right">Bruto</TableCell>
              <TableCell align="right">IR Prov.</TableCell>
              <TableCell align="right">Líquido</TableCell>
              <TableCell>Estratégia</TableCell>
              <TableCell>Fonte</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading && (
              <TableRow><TableCell colSpan={11} align="center"><CircularProgress size={24} /></TableCell></TableRow>
            )}
            {entries?.map((entry, idx) => {
              const num = (v: unknown) => Number(v ?? 0);
              const gross = num(entry.result_gross);
              const net = num(entry.result_net);
              const tax = num(entry.tax_provisioned);
              return (
                <TableRow key={entry.id ?? idx} hover>
                  <TableCell>{entry.trade_date ?? "—"}</TableCell>
                  <TableCell><Chip label={entry.asset} size="small" /></TableCell>
                  <TableCell><Chip label={entry.direction} color={directionColor(entry.direction)} size="small" /></TableCell>
                  <TableCell align="right">{entry.contracts}</TableCell>
                  <TableCell align="right">{num(entry.entry_price).toLocaleString("pt-BR")}</TableCell>
                  <TableCell align="right">{num(entry.exit_price).toLocaleString("pt-BR")}</TableCell>
                  <TableCell align="right">
                    <PnlDisplay grossAmount={gross} netAmount={net} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    {tax > 0 ? (
                      <Typography variant="body2" color="warning.main">R$ {tax.toFixed(2)}</Typography>
                    ) : "—"}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color={net >= 0 ? "success.main" : "error.main"} fontWeight={700}>
                      R$ {net.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell>{entry.strategy}</TableCell>
                  <TableCell><Chip label={entry.source} size="small" variant="outlined" /></TableCell>
                </TableRow>
              );
            })}
            {!isLoading && entries?.length === 0 && (
              <TableRow><TableCell colSpan={11} align="center">
                <Typography variant="body2" color="text.secondary">Nenhuma entrada registrada — comece preenchendo o formulário acima</Typography>
              </TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

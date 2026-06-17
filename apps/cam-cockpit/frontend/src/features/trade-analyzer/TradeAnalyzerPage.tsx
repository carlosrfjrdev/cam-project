/**
 * Trade Analyzer — sobe o report de operações e a IA (Claude ou OpenAI, escolhida
 * aqui) aponta erros e correções.
 *
 * Os TICKS DO DIA vêm automaticamente do MT5 (bridge) — não há upload de ticks.
 * Métricas são calculadas no backend (números confiáveis); a narrativa é da IA.
 */
import { useState } from "react";
import {
  Paper, Stack, Typography, Button, MenuItem, TextField, Alert,
  CircularProgress, Table, TableBody, TableCell, TableHead, TableRow, Chip,
} from "@mui/material";
import PsychologyIcon from "@mui/icons-material/Psychology";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import { useQuery } from "@tanstack/react-query";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { Markdown } from "../../_shared/components/Markdown";
import { api } from "../../api/client";

interface ProviderInfo {
  id: string; label: string; model: string; configured: boolean;
}
interface LastTick {
  asset: string | null; timestamp: string | null; source: string | null; bridge_online: boolean;
}
interface AnalyzeResult {
  provider: string; model: string; narrative: string;
  metrics: Record<string, unknown>; symbol: string;
  tick_summary: Record<string, unknown> | null; tick_status: string;
}

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function StatBox({ label, value, danger }: { label: string; value: string; danger?: boolean }) {
  return (
    <Paper sx={{ p: 1.5, minWidth: 120 }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography variant="h6" color={danger ? "error.main" : "text.primary"}
        sx={{ fontFamily: (t) => t.cam?.fontMono }}>
        {value}
      </Typography>
    </Paper>
  );
}

export function TradeAnalyzerPage() {
  const { data: provData } = useQuery({
    queryKey: ["trade-analyzer-providers"],
    queryFn: () => api.get<{ providers: ProviderInfo[] }>("/trade-analyzer/providers"),
  });
  const { data: lastTick } = useQuery({
    queryKey: ["trade-analyzer-last-tick"],
    queryFn: () => api.get<LastTick>("/trade-analyzer/last-tick"),
    refetchInterval: 15000,
  });
  const providers = provData?.providers ?? [];

  const [report, setReport] = useState<File | null>(null);
  const [provider, setProvider] = useState("anthropic");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);

  const selected = providers.find((p) => p.id === provider);

  async function run() {
    if (!report) { setError("Selecione o report de operações (CSV)."); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const r = await api.uploadForm<AnalyzeResult>(
        "/trade-analyzer/analyze", { report }, { provider },
      );
      setResult(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha na análise.");
    } finally {
      setLoading(false);
    }
  }

  const m = result?.metrics as Record<string, number> | undefined;
  const byQty = (result?.metrics?.by_qty ?? []) as Array<Record<string, number>>;
  const tick = result?.tick_summary as Record<string, unknown> | null;

  return (
    <PageContainer maxWidth={1100}>
      <PageHeader
        title="Trade Analyzer"
        icon={<PsychologyIcon color="primary" />}
        actions={<>
          <Chip
            size="small"
            icon={<FiberManualRecordIcon sx={{ fontSize: 12 }} />}
            color={lastTick?.bridge_online ? "success" : "default"}
            variant={lastTick?.bridge_online ? "filled" : "outlined"}
            label={
              lastTick?.timestamp
                ? `MT5: último tick ${fmtDate(lastTick.timestamp)}`
                : lastTick?.bridge_online
                  ? "MT5 online (sem tick ainda)"
                  : "MT5 offline"
            }
          />
          {selected && (
            <Chip
              size="small"
              color={selected.configured ? "success" : "warning"}
              label={selected.configured ? `${selected.model} pronto` : "sem API key (.env)"}
            />
          )}
        </>}
      />

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
          <Button variant="outlined" component="label" size="small">
            {report ? `✓ ${report.name}` : "Report de operações (CSV)"}
            <input hidden type="file" accept=".csv"
              onChange={(e) => setReport(e.target.files?.[0] ?? null)} />
          </Button>
          <TextField select size="small" label="IA" value={provider}
            onChange={(e) => setProvider(e.target.value)} sx={{ minWidth: 200 }}>
            {providers.map((p) => (
              <MenuItem key={p.id} value={p.id}>
                {p.label}{p.configured ? "" : " (sem key)"}
              </MenuItem>
            ))}
          </TextField>
          <Button variant="contained" onClick={run} disabled={loading || !report}>
            {loading ? <CircularProgress size={20} /> : "Analisar"}
          </Button>
          <Typography variant="caption" color="text.secondary">
            Ticks do dia entram automaticamente do MT5.
          </Typography>
        </Stack>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && result.tick_status !== "ok" && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Ticks do MT5 não incluídos: {result.tick_status}. A análise seguiu só com o report.
        </Alert>
      )}

      {m && (
        <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
          <StatBox label="Símbolo" value={result?.symbol ?? "—"} />
          <StatBox label="Trades" value={String(m.total_trades)} />
          <StatBox label="Resultado bruto" value={`R$ ${m.gross_result}`} danger={m.gross_result < 0} />
          <StatBox label="Win rate" value={`${m.win_rate}%`} />
          <StatBox label="Payoff" value={String(m.payoff)} />
          <StatBox label="Profit factor" value={String(m.profit_factor)} danger={m.profit_factor < 1} />
          <StatBox label="Max perdas seguidas" value={String(m.max_loss_streak)} danger={m.max_loss_streak >= 4} />
          <StatBox label="Ultracurtos ≤30s" value={`${m.ultrashort_count} (R$ ${m.ultrashort_result})`} danger={m.ultrashort_result < 0} />
          {tick && <StatBox label="Ticks MT5" value={String(tick.total_ticks ?? 0)} />}
        </Stack>
      )}

      {byQty.length > 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Resultado por mão (contratos)</Typography>
          <Table size="small">
            <TableHead>
              <TableRow><TableCell>Mão</TableCell><TableCell align="right">Trades</TableCell>
                <TableCell align="right">Resultado</TableCell><TableCell align="right">Win rate</TableCell></TableRow>
            </TableHead>
            <TableBody>
              {byQty.map((q) => (
                <TableRow key={q.qty}>
                  <TableCell>{q.qty}</TableCell>
                  <TableCell align="right">{q.trades}</TableCell>
                  <TableCell align="right" sx={{ color: q.result < 0 ? "error.main" : "success.main" }}>R$ {q.result}</TableCell>
                  <TableCell align="right">{q.win_rate}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      {result?.narrative && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Análise da IA — {result.provider} ({result.model})
          </Typography>
          <Markdown>{result.narrative}</Markdown>
        </Paper>
      )}
    </PageContainer>
  );
}

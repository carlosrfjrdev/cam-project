/**
 * Operation Analyzer (CASCA) — entra com a estratégia e o CAM SINALIZA as operações.
 * Os TICKS e CANDLES do dia vêm AUTOMATICAMENTE do MT5 (bridge) — sem upload.
 * Em tela: risco analisado, melhor horário e mão. Alvo sempre R:R 1:3.
 * SEM bloqueios de Risk Manager (risco é análise, não trava).
 *
 * ⚠️ Casca: a engine de sinais ainda é STUB no backend.
 */
import { useState } from "react";
import {
  Paper, Stack, Typography, Button, TextField, Alert, Chip,
  CircularProgress, Table, TableBody, TableCell, TableHead, TableRow,
} from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { api } from "../../api/client";

interface Signal {
  time: string; side: string; entry: number; stop: number; target: number;
  rr: string; size: number; risk_points: number; rationale: string;
}
interface SignalResponse {
  status: string; symbol: string; strategy: string;
  inputs: Record<string, string | number>;
  risk_analysis: {
    suggested_size: number; best_hour: string; risk_per_trade: number;
    max_risk_session: number; rr_policy: string; risk_manager_blocking: boolean;
  };
  signals: Signal[];
  notes: string;
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <Paper sx={{ p: 1.5, minWidth: 150 }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography variant="h6" sx={{ fontFamily: (t) => t.cam?.fontMono }}>{value}</Typography>
    </Paper>
  );
}

export function OperationAnalyzerPage() {
  const [strategy, setStrategy] = useState("");
  const [symbol, setSymbol] = useState("WINM26");
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SignalResponse | null>(null);

  async function run() {
    setLoading(true); setError(null); setResult(null);
    try {
      const r = await api.uploadForm<SignalResponse>(
        "/operation-analyzer/signal", {},
        { strategy: strategy || "(não informada)", symbol, date },
      );
      setResult(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Falha ao sinalizar.");
    } finally {
      setLoading(false);
    }
  }

  const tickStatus = result?.inputs?.tick_status as string | undefined;

  return (
    <PageContainer maxWidth={1100}>
      <PageHeader
        title="Operation Analyzer"
        icon={<InsightsIcon color="primary" />}
        actions={<>
          <Chip size="small" color="info" label="R:R sempre 1:3" />
          <Chip size="small" variant="outlined" label="sem bloqueio de risco" />
          <Chip size="small" color="warning" label="CASCA (STUB)" />
        </>}
      />

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
          <TextField size="small" label="Símbolo" value={symbol}
            onChange={(e) => setSymbol(e.target.value)} sx={{ width: 130 }} />
          <TextField size="small" type="date" label="Dia" value={date}
            onChange={(e) => setDate(e.target.value)} InputLabelProps={{ shrink: true }}
            sx={{ width: 160 }} helperText="vazio = hoje" />
          <TextField size="small" label="Estratégia" value={strategy}
            onChange={(e) => setStrategy(e.target.value)} sx={{ minWidth: 240 }}
            placeholder="ex.: ORB 11h, rompimento + retorno" />
          <Button variant="contained" onClick={run} disabled={loading}>
            {loading ? <CircularProgress size={20} /> : "Sinalizar"}
          </Button>
          <Typography variant="caption" color="text.secondary">
            Ticks e candles do dia entram automaticamente do MT5.
          </Typography>
        </Stack>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <>
          {tickStatus && tickStatus !== "ok" && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Dados do MT5 indisponíveis: {tickStatus}.
            </Alert>
          )}
          {result.status === "STUB" && (
            <Alert severity="info" sx={{ mb: 2 }}>{result.notes}</Alert>
          )}
          <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
            <StatBox label="Mão sugerida" value={`${result.risk_analysis.suggested_size} contrato(s)`} />
            <StatBox label="Melhor horário" value={result.risk_analysis.best_hour} />
            <StatBox label="Risco por operação" value={`R$ ${result.risk_analysis.risk_per_trade}`} />
            <StatBox label="Risco máx. sessão" value={`R$ ${result.risk_analysis.max_risk_session}`} />
            <StatBox label="Política R:R" value={result.risk_analysis.rr_policy} />
            <StatBox label="Ticks MT5" value={String(result.inputs.ticks_rows ?? 0)} />
            <StatBox label="Candles MT5" value={String(result.inputs.candles_rows ?? 0)} />
          </Stack>

          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Sinais</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Horário</TableCell><TableCell>Lado</TableCell>
                  <TableCell align="right">Entrada</TableCell><TableCell align="right">Stop</TableCell>
                  <TableCell align="right">Alvo (1:3)</TableCell><TableCell align="right">Risco (pts)</TableCell>
                  <TableCell align="right">Mão</TableCell><TableCell>Racional</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.signals.map((s, i) => (
                  <TableRow key={i}>
                    <TableCell>{s.time}</TableCell>
                    <TableCell>
                      <Chip size="small" label={s.side}
                        color={s.side === "LONG" ? "success" : "error"} variant="outlined" />
                    </TableCell>
                    <TableCell align="right">{s.entry}</TableCell>
                    <TableCell align="right">{s.stop}</TableCell>
                    <TableCell align="right">{s.target}</TableCell>
                    <TableCell align="right">{s.risk_points}</TableCell>
                    <TableCell align="right">{s.size}</TableCell>
                    <TableCell>{s.rationale}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </>
      )}
    </PageContainer>
  );
}

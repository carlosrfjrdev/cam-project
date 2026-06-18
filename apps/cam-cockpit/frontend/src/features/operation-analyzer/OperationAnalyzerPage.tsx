/**
 * Operation Analyzer — importa os dados do MT5 (todos os timeframes) e exibe o
 * gráfico (estilo Inspetor/TradingView) com indicadores e topos/fundos.
 *
 * Fluxo: seleciona o ativo → integração MT5 traz os candles (M1..D1) → gráfico
 * com EMA 9/20/50/200, SMA 200, VWAP diária/semanal e linhas horizontais nos
 * topos/fundos (D1, H1, M10, M2). Sem bloqueio de Risk Manager (read-only).
 */
import { useState } from "react";
import {
  Paper, Stack, Typography, TextField, Button, Alert, Chip, CircularProgress,
  ToggleButton, ToggleButtonGroup, Table, TableBody, TableCell, TableHead, TableRow,
} from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import { useQuery } from "@tanstack/react-query";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { api } from "../../api/client";
import { OperationChart, type ChartData } from "./OperationChart";

const TFS = ["M1", "M2", "M5", "M10", "M15", "M30", "H1", "H4", "D1"];
const LEVEL_TFS = new Set(["D1", "H1", "M10", "M2"]);

export function OperationAnalyzerPage() {
  const [symbolInput, setSymbolInput] = useState("WINM26");
  const [symbol, setSymbol] = useState<string | null>(null);
  const [tf, setTf] = useState("M5");

  const { data, isFetching, error } = useQuery({
    queryKey: ["operation-chart", symbol, tf],
    queryFn: () =>
      api.get<ChartData>(`/operation-analyzer/chart?symbol=${symbol}&timeframe=${tf}`),
    enabled: symbol != null,
    retry: false,
  });

  return (
    <PageContainer maxWidth={1200}>
      <PageHeader
        title="Operation Analyzer"
        icon={<InsightsIcon color="primary" />}
        actions={<>
          <Chip size="small" color="info" label="dados MT5" />
          <Chip size="small" variant="outlined" label="sem bloqueio de risco" />
        </>}
      />

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
          <TextField
            size="small" label="Ativo" value={symbolInput}
            onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && setSymbol(symbolInput.trim())}
            sx={{ width: 160 }}
          />
          <Button variant="contained" onClick={() => setSymbol(symbolInput.trim())}>
            Carregar do MT5
          </Button>
          <ToggleButtonGroup
            size="small" exclusive value={tf}
            onChange={(_e, v) => v && setTf(v)}
          >
            {TFS.map((t) => (
              <ToggleButton key={t} value={t} sx={{ px: 1.2 }}>
                {t}{LEVEL_TFS.has(t) ? "*" : ""}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
          <Typography variant="caption" color="text.secondary">
            * timeframes com detecção de topos/fundos
          </Typography>
        </Stack>
      </Paper>

      {symbol == null && (
        <Alert severity="info">Selecione um ativo e clique em “Carregar do MT5”.</Alert>
      )}

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error instanceof Error ? error.message : "Falha ao carregar o gráfico."}
        </Alert>
      )}

      {symbol != null && !error && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
            <Typography variant="subtitle1">{symbol} · {tf}</Typography>
            {isFetching && <CircularProgress size={16} />}
          </Stack>
          {data && <OperationChart data={data} />}
        </Paper>
      )}

      {data && data.level_tf && data.levels.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Topos/fundos detectados ({tf})
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nível</TableCell><TableCell>Tipo</TableCell>
                <TableCell align="right">Toques</TableCell><TableCell>Período</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.levels.map((lv, i) => (
                <TableRow key={i}>
                  <TableCell sx={{ fontFamily: (t) => t.cam?.fontMono }}>{lv.price}</TableCell>
                  <TableCell>
                    <Chip size="small" variant="outlined"
                      label={lv.kind}
                      color={lv.kind === "resistance" ? "error" : lv.kind === "support" ? "success" : "default"} />
                  </TableCell>
                  <TableCell align="right">{lv.touches}</TableCell>
                  <TableCell sx={{ fontSize: 11, color: "text.secondary" }}>
                    {lv.first_ts?.slice(0, 16)?.replace("T", " ")} → {lv.last_ts?.slice(0, 16)?.replace("T", " ")}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </PageContainer>
  );
}

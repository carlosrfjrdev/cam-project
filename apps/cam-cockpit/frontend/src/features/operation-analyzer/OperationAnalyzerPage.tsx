/**
 * Operation Analyzer — importa os dados do MT5 (e PERSISTE), exibe o gráfico
 * (TradingView) com indicadores e topos/fundos por timeframe (cada TF com sua cor).
 * Controles de variável (span/tolerância/toques/máx. níveis) abaixo do gráfico.
 */
import { useState } from "react";
import {
  Paper, Stack, Typography, TextField, Button, Alert, Chip, CircularProgress,
  ToggleButton, ToggleButtonGroup, Table, TableBody, TableCell, TableHead, TableRow,
  Divider,
} from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import { useQuery } from "@tanstack/react-query";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { api } from "../../api/client";
import { OperationChart, TF_COLOR, type ChartData } from "./OperationChart";

const TFS = ["M1", "M2", "M5", "M10", "M15", "M30", "H1", "H4", "D1"];

interface Params { span: number; tolPct: number; minTouches: number; topN: number }
const DEFAULTS: Params = { span: 3, tolPct: 0.15, minTouches: 2, topN: 12 };

export function OperationAnalyzerPage() {
  const [symbolInput, setSymbolInput] = useState("WINM26");
  const [symbol, setSymbol] = useState<string | null>(null);
  const [tf, setTf] = useState("M5");
  const [draft, setDraft] = useState<Params>(DEFAULTS);
  const [applied, setApplied] = useState<Params>(DEFAULTS);

  const p = applied;
  const { data, isFetching, error } = useQuery({
    queryKey: ["operation-chart", symbol, tf, p],
    queryFn: () =>
      api.get<ChartData>(
        `/operation-analyzer/chart?symbol=${symbol}&timeframe=${tf}` +
          `&span=${p.span}&tol=${p.tolPct / 100}&min_touches=${p.minTouches}&top_n=${p.topN}`,
      ),
    enabled: symbol != null,
    retry: false,
  });

  const allLevels = data
    ? Object.entries(data.levels_by_tf).flatMap(([t, lv]) => lv.map((l) => ({ ...l, tf: t })))
    : [];

  const numField = (label: string, key: keyof Params, step = 1) => (
    <TextField
      size="small" type="number" label={label} value={draft[key]}
      onChange={(e) => setDraft({ ...draft, [key]: Number(e.target.value) })}
      inputProps={{ step }} sx={{ width: 150 }}
    />
  );

  return (
    <PageContainer maxWidth={1200}>
      <PageHeader
        title="Operation Analyzer"
        icon={<InsightsIcon color="primary" />}
        actions={<>
          <Chip size="small" color="info" label="dados MT5 (persistido)" />
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
          <ToggleButtonGroup size="small" exclusive value={tf} onChange={(_e, v) => v && setTf(v)}>
            {TFS.map((t) => (
              <ToggleButton key={t} value={t} sx={{ px: 1.2 }}>{t}</ToggleButton>
            ))}
          </ToggleButtonGroup>
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
            {data && (
              <Typography variant="caption" color="text.secondary">
                · {data.persisted_bars} barras persistidas
              </Typography>
            )}
          </Stack>
          {data && <OperationChart data={data} />}
        </Paper>
      )}

      {/* Controles de variável (abaixo do gráfico) */}
      {symbol != null && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Parâmetros dos topos/fundos
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
            {numField("Janela (span)", "span")}
            {numField("Tolerância (%)", "tolPct", 0.05)}
            {numField("Mín. toques", "minTouches")}
            {numField("Máx. níveis/TF", "topN")}
            <Button variant="outlined" onClick={() => setApplied(draft)}>Aplicar</Button>
            <Button size="small" onClick={() => { setDraft(DEFAULTS); setApplied(DEFAULTS); }}>
              Reset
            </Button>
            <Typography variant="caption" color="text.secondary" sx={{ maxWidth: 360 }}>
              span = janela do pivô; tolerância = % p/ agrupar níveis próximos; mín.
              toques filtra níveis fracos.
            </Typography>
          </Stack>
        </Paper>
      )}

      {allLevels.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Topos/fundos por timeframe</Typography>
          <Divider sx={{ mb: 1 }} />
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>TF</TableCell><TableCell>Nível</TableCell><TableCell>Tipo</TableCell>
                <TableCell align="right">Toques</TableCell><TableCell>Período</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {allLevels.map((lv, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Chip size="small" label={lv.tf}
                      sx={{ bgcolor: TF_COLOR[lv.tf], color: "#fff", fontWeight: 700 }} />
                  </TableCell>
                  <TableCell sx={{ fontFamily: (t) => t.cam?.fontMono }}>{lv.price}</TableCell>
                  <TableCell>{lv.kind}</TableCell>
                  <TableCell align="right">{lv.touches}</TableCell>
                  <TableCell sx={{ fontSize: 11, color: "text.secondary" }}>
                    {lv.first_ts?.slice(0, 16).replace("T", " ")} → {lv.last_ts?.slice(0, 16).replace("T", " ")}
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

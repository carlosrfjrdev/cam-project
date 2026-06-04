/**
 * Assets RunTests — "rodei, e aí?" (Design Review §3.2, Andy).
 *
 * Manchete: a CURVA DE EQUITY (domina a dobra). Apoio: 4-5 métricas como tira
 * de chips (StatStrip). Trades em accordion FECHADO. Chip `bruto`+tooltip
 * carrega a honestidade do MVP — nunca parágrafo.
 */
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Box, Button, Chip, MenuItem, Stack, Table, TableBody, TableCell,
  TableHead, TableRow, TextField, Tooltip, Typography,
} from "@mui/material";
import BarChartIcon from "@mui/icons-material/BarChart";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { StatStrip, type StatItem } from "../../_shared/components/StatStrip";
import { DetailDisclosure } from "../../_shared/components/DetailDisclosure";
import { EquityChart } from "./EquityChart";
import {
  fetchEquity, fetchRun, fetchRuns, fetchStrategies, postBacktest, postWalkForward,
  type BacktestResult, type GrossMetrics, type WalkForwardResult,
} from "./api";

function GrossChip() {
  return (
    <Tooltip title="Valores brutos: sem custo, sem IR — não confirma edge líquido.">
      <Chip size="small" variant="outlined" label="bruto" />
    </Tooltip>
  );
}

export function AssetsRunTestsPage() {
  const [strategyId, setStrategyId] = useState("D1");
  const [symbol, setSymbol] = useState("WIN$");
  const [timeframe, setTimeframe] = useState("M1");
  // Parâmetros DINÂMICOS: vêm dos default_params da estratégia selecionada.
  const [params, setParams] = useState<Record<string, number>>({});
  const [runId, setRunId] = useState<number | null>(null);

  const strategies = useQuery({
    queryKey: ["strategy-lab", "strategies"],
    queryFn: fetchStrategies,
    retry: false,
  });
  const runnable = strategies.data?.strategies.filter((s) => s.runnable) ?? [];
  const selectedDef = strategies.data?.strategies.find((s) => s.id === strategyId);

  // ao trocar de estratégia, carrega os parâmetros padrão dela.
  useEffect(() => {
    if (selectedDef) {
      const init: Record<string, number> = {};
      for (const [k, v] of Object.entries(selectedDef.default_params)) {
        init[k] = Number(v);
      }
      setParams(init);
      setTimeframe(selectedDef.timeframe || "M1");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [strategyId, strategies.data]);

  const qc = useQueryClient();
  const backtest = useMutation({
    mutationFn: (): Promise<BacktestResult> =>
      postBacktest(strategyId, { symbol, timeframe, params }),
    onSuccess: (r) => {
      setRunId(r.error ? null : r.run_id);
      qc.invalidateQueries({ queryKey: ["strategy-lab", "runs"] });
    },
  });

  const runs = useQuery({
    queryKey: ["strategy-lab", "runs"],
    queryFn: () => fetchRuns(),
    retry: false,
  });

  const equity = useQuery({
    queryKey: ["strategy-lab", "equity", runId],
    queryFn: () => fetchEquity(runId!),
    enabled: runId !== null,
    retry: false,
  });

  const run = useQuery({
    queryKey: ["strategy-lab", "run", runId],
    queryFn: () => fetchRun(runId!),
    enabled: runId !== null,
    retry: false,
  });

  const walkForward = useMutation({
    mutationFn: (): Promise<WalkForwardResult> =>
      postWalkForward(strategyId, { symbol, timeframe, params }),
  });

  // métrica vem da mutation fresca OU do run salvo (clique no histórico).
  const m: GrossMetrics | null | undefined =
    backtest.data?.metrics ??
    (run.data?.run?.metrics as GrossMetrics | null | undefined);
  const stats: StatItem[] = m
    ? [
        { label: "Trades", value: m.n_trades },
        { label: "Acerto", value: `${(m.win_rate * 100).toFixed(0)}%` },
        {
          label: "Profit Factor",
          value: m.profit_factor === null ? "∞" : m.profit_factor.toFixed(2),
        },
        {
          label: "Resultado bruto",
          value: m.pnl_bruto_total.toFixed(2),
          tone: m.pnl_bruto_total >= 0 ? "success" : "danger",
        },
        { label: "Drawdown", value: m.max_drawdown.toFixed(2), tone: "warning" },
      ]
    : [];

  return (
    <PageContainer maxWidth={1100}>
      <PageHeader
        title="Backtest"
        icon={<BarChartIcon color="secondary" />}
        actions={<GrossChip />}
      />

      {/* Config compacta em 1 linha (Design Review §3.2) */}
      <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1, mb: 2 }}>
        <TextField
          select size="small" label="Estratégia" value={strategyId}
          onChange={(e) => setStrategyId(e.target.value)} sx={{ minWidth: 140 }}
        >
          {runnable.map((s) => (
            <MenuItem key={s.id} value={s.id}>{s.id} · {s.name}</MenuItem>
          ))}
          {runnable.length === 0 && <MenuItem value="D1">D1</MenuItem>}
        </TextField>
        <TextField
          size="small" label="Símbolo" value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())} sx={{ width: 110 }}
        />
        <TextField
          size="small" label="TF" value={timeframe}
          onChange={(e) => setTimeframe(e.target.value.toUpperCase())} sx={{ width: 80 }}
        />
        {/* Parâmetros dinâmicos da estratégia selecionada (D1, D2, …). */}
        {Object.keys(params).map((k) => (
          <TextField
            key={k}
            size="small"
            type="number"
            label={k}
            value={params[k]}
            onChange={(e) =>
              setParams((p) => ({ ...p, [k]: Number(e.target.value) }))
            }
            sx={{ width: 130 }}
          />
        ))}
        <Button
          variant="contained"
          onClick={() => backtest.mutate()}
          disabled={backtest.isPending}
        >
          {backtest.isPending ? "Rodando…" : "Rodar"}
        </Button>
      </Stack>

      {backtest.data?.error === "NO_DATA" && (
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          {backtest.data.message ?? "Sem dado para este símbolo."} Ingerir no Quant Lab antes.
        </Typography>
      )}
      {backtest.isError && (
        <Typography color="error" sx={{ mb: 2 }}>
          Falha ao rodar o backtest.
        </Typography>
      )}

      {/* Manchete: curva de equity */}
      {runId !== null && (
        <>
          <EquityChart data={equity.data?.equity_curve ?? []} />

          {/* Apoio: 4-5 métricas como tira de chips */}
          <StatStrip items={stats} />

          {/* Detalhe escondido: tabela de trades (par como unidade) */}
          <DetailDisclosure title="Trades" count={run.data?.trades.length}>
            {run.data && run.data.trades.length > 0 ? (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Lado</TableCell>
                    <TableCell>Entrada</TableCell>
                    <TableCell align="right">Preço</TableCell>
                    <TableCell>Saída</TableCell>
                    <TableCell align="right">Preço</TableCell>
                    <TableCell>Motivo</TableCell>
                    <TableCell align="right">Bruto</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {run.data.trades.map((t, i) => (
                    <TableRow key={`${t.pair_id}-${t.symbol}-${i}`}>
                      <TableCell>{t.pair_id}</TableCell>
                      <TableCell>{t.leg}</TableCell>
                      <TableCell>{t.ts_entry?.slice(0, 16)}</TableCell>
                      <TableCell align="right">{Number(t.price_entry).toFixed(1)}</TableCell>
                      <TableCell>{t.ts_exit?.slice(0, 16)}</TableCell>
                      <TableCell align="right">{Number(t.price_exit).toFixed(1)}</TableCell>
                      <TableCell>{t.exit_reason}</TableCell>
                      <TableCell
                        align="right"
                        sx={{ color: Number(t.pnl_bruto) >= 0 ? "success.main" : "error.main" }}
                      >
                        {Number(t.pnl_bruto).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhum trade neste período.
              </Typography>
            )}
          </DetailDisclosure>

          {/* Walk-forward OOS: consistência temporal (accordion fechado) */}
          <DetailDisclosure title="Walk-forward (OOS)">
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Roda o backtest em janelas rolantes para ver se o resultado se
              mantém ao longo do tempo — ou se veio de um só período.
            </Typography>
            <Button
              size="small"
              variant="outlined"
              onClick={() => walkForward.mutate()}
              disabled={walkForward.isPending}
            >
              {walkForward.isPending ? "Rodando…" : "Rodar walk-forward"}
            </Button>

            {walkForward.data && !walkForward.data.error && (
              <Box sx={{ mt: 2 }}>
                <StatStrip
                  items={[
                    { label: "Janelas", value: walkForward.data.aggregate.n_windows },
                    {
                      label: "Positivas",
                      value: walkForward.data.aggregate.positive_windows,
                    },
                    {
                      label: "Consistência",
                      value: `${(walkForward.data.aggregate.consistency * 100).toFixed(0)}%`,
                      tone:
                        walkForward.data.aggregate.consistency >= 0.5
                          ? "success"
                          : "warning",
                    },
                  ]}
                />
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Janela</TableCell>
                      <TableCell>Início</TableCell>
                      <TableCell>Fim</TableCell>
                      <TableCell align="right">Trades</TableCell>
                      <TableCell align="right">Bruto</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {walkForward.data.windows.map((w) => (
                      <TableRow key={w.window}>
                        <TableCell>{w.window}</TableCell>
                        <TableCell>{w.ts_start.slice(0, 10)}</TableCell>
                        <TableCell>{w.ts_end.slice(0, 10)}</TableCell>
                        <TableCell align="right">{w.n_trades}</TableCell>
                        <TableCell
                          align="right"
                          sx={{ color: w.pnl_bruto >= 0 ? "success.main" : "error.main" }}
                        >
                          {w.pnl_bruto.toFixed(2)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </DetailDisclosure>
        </>
      )}

      {runId === null && !backtest.isPending && (
        <Box
          sx={{
            mt: 4, p: 6, textAlign: "center", border: "1px dashed",
            borderColor: "divider", borderRadius: 1,
          }}
        >
          <Typography color="text.secondary">
            Configure acima e clique <strong>Rodar</strong> para ver a curva de equity.
          </Typography>
        </Box>
      )}

      {/* Histórico: backtests recentes (clique recarrega) */}
      {runs.data && runs.data.runs.length > 0 && (
        <DetailDisclosure title="Backtests recentes" count={runs.data.runs.length}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>#</TableCell>
                <TableCell>Estratégia</TableCell>
                <TableCell>Símbolo</TableCell>
                <TableCell>Quando</TableCell>
                <TableCell align="right">Trades</TableCell>
                <TableCell align="right">Bruto</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {runs.data.runs.map((r) => {
                const pnl = r.metrics?.pnl_bruto_total ?? 0;
                return (
                  <TableRow
                    key={r.id}
                    hover
                    selected={r.id === runId}
                    sx={{ cursor: "pointer" }}
                    onClick={() => setRunId(r.id)}
                  >
                    <TableCell>{r.id}</TableCell>
                    <TableCell>{r.strategy_id}</TableCell>
                    <TableCell>{r.symbols?.join(", ")}</TableCell>
                    <TableCell>{r.created_at?.slice(0, 16).replace("T", " ")}</TableCell>
                    <TableCell align="right">{r.metrics?.n_trades ?? "—"}</TableCell>
                    <TableCell
                      align="right"
                      sx={{ color: pnl >= 0 ? "success.main" : "error.main" }}
                    >
                      {r.metrics ? pnl.toFixed(2) : "—"}
                    </TableCell>
                    <TableCell>
                      <Chip size="small" variant="outlined" label="abrir" />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </DetailDisclosure>
      )}
    </PageContainer>
  );
}

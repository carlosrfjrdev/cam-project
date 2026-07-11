/**
 * Trade Analyzer — Histórico de análises.
 *
 * Lista as análises persistidas (data, símbolo, IA, resultado). Selecionar uma
 * abre o detalhe: download do arquivo original + a análise da IA (markdown).
 */
import { useState } from "react";
import {
  Paper, Stack, Typography, Table, TableBody, TableCell, TableHead, TableRow,
  Chip, Button, CircularProgress, Divider, Link,
} from "@mui/material";
import HistoryIcon from "@mui/icons-material/History";
import DownloadIcon from "@mui/icons-material/Download";
import { useQuery } from "@tanstack/react-query";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { Markdown } from "../../_shared/components/Markdown";
import { api } from "../../api/client";

interface HistoryItem {
  id: number; created_at: string | null; provider: string; model: string;
  symbol: string | null; report_filename: string;
  total_trades: number | null; gross_result: number | null;
  win_rate: number | null; profit_factor: number | null;
}
interface HistoryDetail extends HistoryItem {
  metrics: Record<string, unknown>; narrative: string;
  tick_summary: Record<string, unknown> | null; tick_status: string | null;
}

const API_BASE = "/api/v1";

function fmt(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

export function TradeAnalyzerHistoryPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data: list, isLoading } = useQuery({
    queryKey: ["trade-analyzer-history"],
    queryFn: () => api.get<HistoryItem[]>("/trade-analyzer/history?limit=200"),
  });

  const { data: detail, isFetching } = useQuery({
    queryKey: ["trade-analyzer-history", selectedId],
    queryFn: () => api.get<HistoryDetail>(`/trade-analyzer/history/${selectedId}`),
    enabled: selectedId != null,
  });

  const items = list ?? [];
  const m = detail?.metrics as Record<string, number> | undefined;
  const byQty = (detail?.metrics?.by_qty ?? []) as Array<Record<string, number>>;

  return (
    <PageContainer maxWidth={1100}>
      <PageHeader title="Trade Analyzer — Histórico" icon={<HistoryIcon color="primary" />} />

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>Análises salvas</Typography>
        {isLoading ? (
          <CircularProgress size={22} />
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Data</TableCell><TableCell>Símbolo</TableCell>
                <TableCell>IA</TableCell><TableCell align="right">Trades</TableCell>
                <TableCell align="right">Resultado</TableCell><TableCell align="right">WR</TableCell>
                <TableCell align="right">PF</TableCell><TableCell>Arquivo</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.length === 0 && (
                <TableRow><TableCell colSpan={8}>
                  <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                    Nenhuma análise salva ainda. Rode uma no Trade Analyzer.
                  </Typography>
                </TableCell></TableRow>
              )}
              {items.map((it) => (
                <TableRow
                  key={it.id}
                  hover
                  selected={it.id === selectedId}
                  onClick={() => setSelectedId(it.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell>{fmt(it.created_at)}</TableCell>
                  <TableCell>{it.symbol ?? "—"}</TableCell>
                  <TableCell><Chip size="small" label={it.provider} variant="outlined" /></TableCell>
                  <TableCell align="right">{it.total_trades ?? "—"}</TableCell>
                  <TableCell align="right" sx={{ color: (it.gross_result ?? 0) < 0 ? "error.main" : "success.main" }}>
                    {it.gross_result != null ? `R$ ${it.gross_result}` : "—"}
                  </TableCell>
                  <TableCell align="right">{it.win_rate != null ? `${it.win_rate}%` : "—"}</TableCell>
                  <TableCell align="right">{it.profit_factor ?? "—"}</TableCell>
                  <TableCell sx={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {it.report_filename}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Paper>

      {selectedId != null && (
        <Paper sx={{ p: 2 }}>
          {isFetching && !detail ? (
            <CircularProgress size={22} />
          ) : detail ? (
            <>
              <Stack direction="row" alignItems="center" justifyContent="space-between" flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
                <Typography variant="subtitle1">
                  {detail.symbol} — {fmt(detail.created_at)} · {detail.provider} ({detail.model})
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  component={Link}
                  href={`${API_BASE}/trade-analyzer/history/${detail.id}/report`}
                >
                  Baixar arquivo ({detail.report_filename})
                </Button>
              </Stack>

              {m && (
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1.5 }}>
                  <Chip size="small" label={`Trades: ${m.total_trades}`} />
                  <Chip size="small" color={m.gross_result < 0 ? "error" : "success"} label={`R$ ${m.gross_result}`} />
                  <Chip size="small" label={`WR ${m.win_rate}%`} />
                  <Chip size="small" color={m.profit_factor < 1 ? "error" : "default"} label={`PF ${m.profit_factor}`} />
                  {byQty.map((q) => (
                    <Chip key={q.qty} size="small" variant="outlined"
                      label={`${q.qty} mão: R$ ${q.result}`} />
                  ))}
                </Stack>
              )}

              <Divider sx={{ my: 1 }} />
              <Markdown>{detail.narrative}</Markdown>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">Não foi possível carregar.</Typography>
          )}
        </Paper>
      )}
    </PageContainer>
  );
}

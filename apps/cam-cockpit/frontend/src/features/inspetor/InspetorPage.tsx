/**
 * Inspetor de Ativo (MVP) — ADR-014 / SPEC-Inspetor.
 *
 * Busca → gráfico (candles + tick/book ao vivo MT5) + fundamentos (Ação/FII)
 * + 2 estimativas de dividendo + overlay de Regime (ações). 100% READ-ONLY:
 * nenhuma ação envia ordem (Art. 35º).
 */
import { useCallback, useEffect, useState } from "react";
import {
  Alert, Box, Button, Chip, CircularProgress, Divider, Paper, Stack,
  TextField, ToggleButton, ToggleButtonGroup, Typography,
} from "@mui/material";
import { useMarketSocket, type MarketFrame } from "./useMarketSocket";
import { TIMEFRAMES, type Timeframe } from "./api";
import { useCandles, useFundamentals, useRegime, useSymbolMeta } from "./useInspetor";
import { CandleChart } from "./components/CandleChart";
import { FundamentalsPanel } from "./components/FundamentalsPanel";
import { DividendsPanel } from "./components/DividendsPanel";
import { RegimePanel } from "./components/RegimePanel";
import { BookPanel, type BookSnapshot } from "./components/BookPanel";

interface LiveTick {
  bid?: number;
  ask?: number;
  last?: number;
}

export function InspetorPage() {
  const [input, setInput] = useState("");
  const [symbol, setSymbol] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<Timeframe>("D1");
  const [tick, setTick] = useState<LiveTick>({});
  const [book, setBook] = useState<BookSnapshot | null>(null);
  const [wsState, setWsState] = useState<"ONLINE" | "OFFLINE">("OFFLINE");

  const meta = useSymbolMeta(symbol);
  const candles = useCandles(symbol, timeframe);
  const isStock = meta.data?.type === "stock";
  const hasFundamentals = !!meta.data?.has_fundamentals;
  const fundamentals = useFundamentals(symbol, hasFundamentals);
  const regime = useRegime(symbol, isStock);

  const onFrame = useCallback((msg: MarketFrame) => {
    if (msg.type === "tick") {
      setTick({ bid: msg.bid, ask: msg.ask, last: msg.last });
      setWsState("ONLINE");
    } else if (msg.type === "book") {
      setBook({ bids: msg.bids ?? [], asks: msg.asks ?? [] });
    } else if (msg.type === "status") {
      setWsState(msg.state === "ONLINE" ? "ONLINE" : "OFFLINE");
    }
  }, []);

  useMarketSocket(symbol, onFrame);

  // O regime lê cam_inspector_candles, populada pelo fetch de candles D1.
  // Como as queries disparam em paralelo, refaz o regime quando os candles D1
  // chegam (a persistência já ocorreu no backend antes da resposta).
  useEffect(() => {
    if (isStock && timeframe === "D1" && candles.isSuccess) {
      regime.refetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candles.dataUpdatedAt, isStock, timeframe]);

  const submit = () => {
    const t = input.trim().toUpperCase();
    if (!t) return;
    setTick({});
    setBook(null);
    setSymbol(t);
  };

  return (
    <Box sx={{ px: "5%", py: 2, width: "100%", boxSizing: "border-box" }}>
      <Typography variant="h5" sx={{ mb: 0.5 }}>
        Inspetor de Ativo
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Pesquise um papel e veja gráfico, fundamentos e regime. Leitura apenas — sem ordens.
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <TextField
            size="small"
            fullWidth
            placeholder="Ex.: PETR4, MXRF11, WIN$"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            inputProps={{ "data-testid": "symbol-search" }}
          />
          <Button variant="contained" onClick={submit}>
            Buscar
          </Button>
        </Stack>
      </Paper>

      {!symbol && (
        <Alert severity="info">Digite um símbolo e clique em Buscar.</Alert>
      )}

      {symbol && (
        <>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
              <Typography variant="h6">{symbol}</Typography>
              {meta.data && (
                <Chip size="small" label={meta.data.type} variant="outlined" />
              )}
              <Chip
                size="small"
                label={`WS ${wsState}`}
                color={wsState === "ONLINE" ? "success" : "default"}
              />
              {tick.last != null && (
                <Chip size="small" color="primary" label={`Último ${tick.last.toFixed(2)}`} />
              )}
              {tick.bid != null && tick.ask != null && (
                <Typography variant="caption" color="text.secondary">
                  bid {tick.bid.toFixed(2)} / ask {tick.ask.toFixed(2)}
                </Typography>
              )}
              <Box sx={{ flexGrow: 1 }} />
              <ToggleButtonGroup
                size="small"
                exclusive
                value={timeframe}
                onChange={(_, v) => v && setTimeframe(v)}
              >
                {TIMEFRAMES.map((tf) => (
                  <ToggleButton key={tf} value={tf} sx={{ px: 1 }}>
                    {tf}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Stack>

            <Divider sx={{ my: 1.5 }} />

            {candles.isLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                <CircularProgress />
              </Box>
            )}
            {candles.isError && (
              <Alert severity="warning">
                Sem dado de mercado. Verifique se o MT5 está aberto e o EA cam_bridge atachado
                (WS {wsState}).
              </Alert>
            )}
            {candles.data && <CandleChart candles={candles.data.candles} />}
          </Paper>

          {(book || meta.data?.type === "future" || meta.data?.type === "stock") && (
            <Paper sx={{ p: 2, mb: 2 }}>
              <BookPanel book={book} />
            </Paper>
          )}

          {hasFundamentals && (
            <Paper sx={{ p: 2, mb: 2 }}>
              {fundamentals.isLoading ? (
                <CircularProgress size={20} />
              ) : fundamentals.data ? (
                <>
                  <FundamentalsPanel data={fundamentals.data} />
                  <Divider sx={{ my: 2 }} />
                  <DividendsPanel data={fundamentals.data} />
                </>
              ) : (
                <>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Fundamentos
                  </Typography>
                  <Alert severity="info">
                    Dados não disponíveis — a brapi.dev não cobre este ativo.
                  </Alert>
                </>
              )}
            </Paper>
          )}

          {/* Regime é independente dos fundamentos (brapi). Sempre aparece para ações. */}
          {isStock && (
            <Paper sx={{ p: 2, mb: 2 }}>
              {regime.isLoading ? (
                <CircularProgress size={20} />
              ) : regime.data ? (
                <RegimePanel data={regime.data} />
              ) : (
                <>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Regime de Mercado
                  </Typography>
                  <Alert severity="info">
                    Regime indisponível no momento. Carregue candles diários (D1) deste ativo.
                  </Alert>
                </>
              )}
            </Paper>
          )}
        </>
      )}
    </Box>
  );
}

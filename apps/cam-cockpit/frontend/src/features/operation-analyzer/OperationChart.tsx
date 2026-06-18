/**
 * OperationChart — candles MT5 (lightweight-charts/TradingView) com overlays:
 * EMA 9/20/50/200, SMA 200, VWAP diária e semanal, e linhas horizontais nos
 * topos/fundos detectados em D1/H1/M10/M2 — CADA TIMEFRAME COM SUA COR.
 */
import { useEffect, useRef } from "react";
import {
  createChart, ColorType, LineStyle, type IChartApi,
} from "lightweight-charts";
import { Box, Stack, Chip, Typography } from "@mui/material";

export interface Candle {
  time: number; open: number; high: number; low: number; close: number; volume?: number;
}
export interface LinePoint { time: number; value: number }
export interface Level {
  price: number; kind: string; touches: number; first_ts?: string; last_ts?: string;
}
export interface ChartData {
  symbol: string; timeframe: string;
  candles: Candle[];
  overlays: Record<string, LinePoint[]>;
  levels_by_tf: Record<string, Level[]>;
  level_tfs: string[];
  persisted_bars: number;
  params: { span: number; tol: number; min_touches: number; top_n: number };
}

const OVERLAY_STYLE: Record<string, { color: string; label: string; width: number }> = {
  ema9: { color: "#f5b301", label: "EMA 9", width: 1 },
  ema20: { color: "#ff7043", label: "EMA 20", width: 1 },
  ema50: { color: "#42a5f5", label: "EMA 50", width: 1 },
  ema200: { color: "#ab47bc", label: "EMA 200", width: 2 },
  sma200: { color: "#bdbdbd", label: "SMA 200", width: 2 },
  vwap_daily: { color: "#26c6da", label: "VWAP dia", width: 2 },
  vwap_weekly: { color: "#66bb6a", label: "VWAP sem", width: 2 },
};

// Cor por timeframe das linhas de topo/fundo (R do Founder).
export const TF_COLOR: Record<string, string> = {
  D1: "#ff1744",   // vermelho
  H1: "#ff9100",   // laranja
  M10: "#d500f9",  // magenta
  M2: "#00b0ff",   // azul
};

export function OperationChart({
  data,
  height = 480,
  enabledLevelTfs,
}: {
  data: ChartData;
  height?: number;
  /** TFs cujos topos/fundos devem aparecer. Default: todos os de levels_by_tf. */
  enabledLevelTfs?: string[];
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const enabled = enabledLevelTfs ?? Object.keys(data.levels_by_tf);
  const enabledKey = enabled.slice().sort().join(",");

  useEffect(() => {
    if (!containerRef.current || !data.candles.length) return;
    const chart = createChart(containerRef.current, {
      height,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9aa4b2",
      },
      grid: {
        vertLines: { color: "rgba(120,130,150,0.08)" },
        horzLines: { color: "rgba(120,130,150,0.08)" },
      },
      timeScale: { timeVisible: true, borderColor: "rgba(120,130,150,0.2)" },
      rightPriceScale: { borderColor: "rgba(120,130,150,0.2)" },
      crosshair: { mode: 0 },
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#1faa73", downColor: "#e0556e", borderVisible: false,
      wickUpColor: "#1faa73", wickDownColor: "#e0556e",
    });
    candleSeries.setData(data.candles.map((c) => ({
      time: c.time as never, open: c.open, high: c.high, low: c.low, close: c.close,
    })));

    for (const [key, style] of Object.entries(OVERLAY_STYLE)) {
      const pts = data.overlays[key];
      if (!pts?.length) continue;
      const s = chart.addLineSeries({
        color: style.color, lineWidth: style.width as never,
        priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false,
      });
      s.setData(pts.map((p) => ({ time: p.time as never, value: p.value })));
    }

    // topos/fundos de cada TF → linha horizontal na cor do TF (só os ativos)
    for (const [tf, levels] of Object.entries(data.levels_by_tf)) {
      if (!enabled.includes(tf)) continue;
      const color = TF_COLOR[tf] ?? "#9aa4b2";
      for (const lv of levels) {
        candleSeries.createPriceLine({
          price: lv.price,
          color,
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `${tf} ${lv.kind === "resistance" ? "R" : lv.kind === "support" ? "S" : "·"}×${lv.touches}`,
        });
      }
    }

    chart.timeScale().fitContent();
    chartRef.current = chart;
    const onResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [data, height, enabledKey]);

  if (!data.candles.length) {
    return (
      <Box sx={{ height, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Typography color="text.secondary">Sem candles para exibir.</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
        {Object.entries(OVERLAY_STYLE).map(([k, s]) =>
          data.overlays[k]?.length ? (
            <Chip key={k} size="small" variant="outlined"
              label={s.label} sx={{ borderColor: s.color, color: s.color }} />
          ) : null,
        )}
      </Stack>
      <Box ref={containerRef} sx={{ width: "100%" }} data-testid="operation-chart" />
    </Box>
  );
}

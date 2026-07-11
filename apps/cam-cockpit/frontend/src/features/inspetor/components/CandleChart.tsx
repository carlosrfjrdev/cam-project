/**
 * Gráfico de candles (TradingView lightweight-charts). API imperativa —
 * compatível com React 19 via ref + efeito. R-04 / SPEC-Inspetor.
 */
import { useEffect, useRef } from "react";
import { createChart, ColorType, type IChartApi } from "lightweight-charts";
import { Box, Typography } from "@mui/material";
import type { Candle } from "../api";

interface Props {
  candles: Candle[];
  height?: number;
}

export function CandleChart({ candles, height = 380 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
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
    });
    const series = chart.addCandlestickSeries({
      upColor: "#1faa73",
      downColor: "#e0556e",
      borderVisible: false,
      wickUpColor: "#1faa73",
      wickDownColor: "#e0556e",
    });
    series.setData(
      candles.map((c) => ({
        time: c.time as never,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      })),
    );
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
  }, [candles, height]);

  if (!candles.length) {
    return (
      <Box sx={{ height, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Typography color="text.secondary">Sem candles para exibir.</Typography>
      </Box>
    );
  }

  return <Box ref={containerRef} sx={{ width: "100%" }} data-testid="candle-chart" />;
}

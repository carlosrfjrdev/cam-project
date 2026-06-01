/**
 * WebSocket de market data ao vivo do Inspetor (tick/book/status).
 * Conecta a `ws://host/api/v1/mt5/ws/market/{symbol}` quando há símbolo.
 * Reconecta automaticamente; limpa ao trocar de símbolo / desmontar.
 */
import { useEffect, useRef } from "react";

export interface MarketFrame {
  type: "tick" | "book" | "status";
  state?: "ONLINE" | "OFFLINE";
  symbol?: string;
  bid?: number;
  ask?: number;
  last?: number;
  bids?: { price: number; vol: number }[];
  asks?: { price: number; vol: number }[];
}

export function useMarketSocket(
  symbol: string | null,
  onFrame: (frame: MarketFrame) => void,
) {
  const cbRef = useRef(onFrame);
  cbRef.current = onFrame;

  useEffect(() => {
    if (!symbol) return;
    let ws: WebSocket | null = null;
    let closed = false;
    let retry: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      if (closed) return;
      const path = `/api/v1/mt5/ws/market/${encodeURIComponent(symbol)}`;
      ws = new WebSocket(`ws://${window.location.host}${path}`);
      ws.onmessage = (event) => {
        try {
          cbRef.current(JSON.parse(event.data) as MarketFrame);
        } catch {
          // frame malformado — ignora
        }
      };
      ws.onclose = () => {
        if (!closed) retry = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws?.close();
    };
    connect();

    return () => {
      closed = true;
      if (retry) clearTimeout(retry);
      ws?.close();
    };
  }, [symbol]);
}

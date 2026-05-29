import { useEffect, useRef, useState } from "react";

interface PnlUpdate {
  daily_pnl_gross: number;
  daily_pnl_net: number;
  open_positions: number;
  timestamp: string;
}

export function usePnlWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const [pnl, setPnl] = useState<PnlUpdate | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/pnl`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as PnlUpdate;
        setPnl(data);
      } catch {
        // ignore malformed frames
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  return { pnl, connected };
}

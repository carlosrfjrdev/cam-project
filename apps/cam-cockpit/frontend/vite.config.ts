import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        // WebSocket do Inspetor vive em /api/v1/mt5/ws/market/{symbol}
        // (e o WS de P&L em /api/v1/ws/pnl). Sem ws:true o upgrade falha
        // silenciosamente e tick/book ao vivo ficam mudos.
        ws: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
  },
});

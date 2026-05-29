import {
  Box, Typography, Paper, Stack, TextField, Button, Alert, Divider,
  Grid, Chip,
} from "@mui/material";
import LockIcon from "@mui/icons-material/Lock";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { MT5BridgeStatus } from "../../api/types";

interface Settings {
  telegram_configured: boolean;
  profit_csv_path: string | null;
  ollama_configured: boolean;
  database_connected: boolean;
}

export function SettingsPage() {
  const qc = useQueryClient();
  const [telegramToken, setTelegramToken] = useState("");
  const [chatId, setChatId] = useState("");
  const [csvPath, setCsvPath] = useState("");

  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: () => api.get<Settings>("/settings"),
  });

  const { data: mt5Status } = useQuery({
    queryKey: ["mt5-bridge-status"],
    queryFn: () => api.get<MT5BridgeStatus>("/mt5/bridge/status"),
    refetchInterval: 3000,
    retry: false,
  });

  const updateSettings = useMutation({
    mutationFn: (data: object) => api.patch("/settings", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings"] }),
  });

  const restartBridge = useMutation({
    mutationFn: () => api.post("/mt5/bridge/restart", { confirm: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mt5-bridge-status"] }),
  });

  const stateColor = (s?: string) =>
    s === "ONLINE" ? "success" : s === "RECONNECTING" ? "warning" : "error";

  const handleSaveTelegram = () => {
    updateSettings.mutate({ telegram_bot_token: telegramToken, telegram_chat_id: chatId });
    setTelegramToken("");
    setChatId("");
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} mb={3}>Configurações</Typography>

      <Alert severity="warning" sx={{ mb: 3 }}>
        Os parâmetros do Risk Engine (limites de perda, máx. contratos) NÃO são configuráveis aqui (Art. 35º / CA5.4).
        Alterações na Política Operacional Vigente requerem processo formal de emenda constitucional.
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" alignItems="center" spacing={1} mb={2}>
              <Typography variant="h6">Telegram Bot</Typography>
              <Chip
                label={settings?.telegram_configured ? "Configurado" : "Não configurado"}
                color={settings?.telegram_configured ? "success" : "warning"}
                size="small"
              />
            </Stack>
            <Stack spacing={2}>
              <TextField
                label="Bot Token (não exibido após salvar)"
                type="password"
                value={telegramToken}
                onChange={e => setTelegramToken(e.target.value)}
                fullWidth
                size="small"
                placeholder="123456789:ABCdef..."
              />
              <TextField
                label="Chat ID"
                value={chatId}
                onChange={e => setChatId(e.target.value)}
                fullWidth
                size="small"
                placeholder="-100123456"
              />
              <Button variant="contained" onClick={handleSaveTelegram} disabled={!telegramToken || !chatId}>
                Salvar Credenciais Telegram
              </Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Integração Profit</Typography>
            <Stack spacing={2}>
              <TextField
                label="Caminho padrão CSV do Profit"
                value={csvPath}
                onChange={e => setCsvPath(e.target.value)}
                fullWidth
                size="small"
                placeholder="C:\Users\...\Profit\exports\"
              />
              <Button variant="outlined" onClick={() => updateSettings.mutate({ profit_csv_path: csvPath })}>
                Salvar Caminho
              </Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderLeft: 3, borderColor: stateColor(mt5Status?.state) + ".main" }}>
            <Stack direction="row" alignItems="center" spacing={2} mb={2}>
              <Typography variant="h6">Bridge MT5 (ZeroMQ)</Typography>
              <Chip
                label={mt5Status?.state ?? "—"}
                color={stateColor(mt5Status?.state)}
                size="small"
                sx={{ fontWeight: 700 }}
              />
            </Stack>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Host</Typography>
                <Typography variant="body2">{mt5Status?.host ?? "—"}:{mt5Status?.pub_port ?? "—"} / {mt5Status?.req_port ?? "—"}</Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Último heartbeat</Typography>
                <Typography variant="body2">
                  {mt5Status?.last_heartbeat_age_ms != null
                    ? `há ${(mt5Status.last_heartbeat_age_ms / 1000).toFixed(1)}s`
                    : "—"}
                </Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Latência média REQ/REP</Typography>
                <Typography variant="body2">
                  {mt5Status?.avg_latency_ms != null
                    ? `${mt5Status.avg_latency_ms.toFixed(1)} ms`
                    : "—"}
                </Typography>
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2" color="text.secondary">Path do MT5</Typography>
                <Typography variant="body2" sx={{ fontSize: 11 }}>{mt5Status?.mt5_path ?? "(detectar via Wine)"}</Typography>
              </Stack>
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Button
              variant="outlined"
              startIcon={<RestartAltIcon />}
              onClick={() => restartBridge.mutate()}
              disabled={restartBridge.isPending}
              size="small"
            >
              Reiniciar bridge
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Camadas de Integração</Typography>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">MT5 Integration</Typography>
                <Chip label="ATIVA" color="success" size="small" sx={{ fontWeight: 700 }} />
              </Stack>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">Profit Integration</Typography>
                <Chip label="DESATIVADA" color="default" size="small" variant="outlined" />
              </Stack>
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Typography variant="caption" color="text.secondary">
              SPEC v0.2.1 — princípio de coexistência. Apenas uma camada ativa por vez (mutex R21.03).
              Reativar Profit requer edição de <code>.env</code> + restart.
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Status dos Serviços</Typography>
            <Stack spacing={1}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Banco de Dados (PostgreSQL)</Typography>
                <Chip label={settings?.database_connected ? "Conectado" : "Desconectado"} color={settings?.database_connected ? "success" : "error"} size="small" />
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Ollama (IA Local)</Typography>
                <Chip label={settings?.ollama_configured ? "Online" : "Offline"} color={settings?.ollama_configured ? "success" : "warning"} size="small" />
              </Stack>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">Telegram Bot</Typography>
                <Chip label={settings?.telegram_configured ? "Configurado" : "Não configurado"} color={settings?.telegram_configured ? "success" : "warning"} size="small" />
              </Stack>
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" alignItems="center" spacing={1}>
              <LockIcon fontSize="small" color="warning" />
              <Typography variant="caption" color="text.secondary">
                Parâmetros do Risk Engine são somente leitura nesta tela (Art. 35º)
              </Typography>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

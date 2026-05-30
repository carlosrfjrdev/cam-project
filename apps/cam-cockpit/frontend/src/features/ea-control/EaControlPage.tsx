/**
 * EA Control Panel — TASK-U017 (BL-UI-3).
 *
 * Status do EA (versão+hash+paused), PAUSE/RESUME e heartbeat (online/offline).
 * **Sem SUBMIT_ORDER** — o único arquivo que envia ordem é cam_risk_mirror.mq5
 * (Kevin, Constituição).
 */
import {
  Box, Typography, Stack, Card, CardContent, Button, Chip, Alert,
} from "@mui/material";
import MemoryIcon from "@mui/icons-material/Memory";
import { useEaStatus, useEaControl, type EaState } from "./useEaControl";

function EaCard({ ea }: { ea: EaState }) {
  const { pause, resume } = useEaControl();
  return (
    <Card data-testid="ea-card" sx={{ minWidth: 260 }}>
      <CardContent>
        <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography variant="h6">{ea.asset}</Typography>
          <Chip
            label={ea.online ? "ONLINE" : "OFFLINE"}
            size="small"
            color={ea.online ? "success" : "default"}
            data-testid="ea-heartbeat"
            data-online={ea.online ? "true" : "false"}
          />
        </Stack>
        <Typography variant="caption" color="text.secondary" display="block">
          {ea.ea_id}
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: (t) => t.cam.fontMono }}>
          v{ea.version} · {ea.hash}
        </Typography>
        <Chip
          label={ea.paused ? "PAUSADO" : "ATIVO"}
          size="small"
          color={ea.paused ? "warning" : "primary"}
          sx={{ mt: 1 }}
          data-testid="ea-paused"
          data-paused={ea.paused ? "true" : "false"}
        />
        <Stack direction="row" spacing={1} mt={2}>
          <Button
            size="small"
            variant="outlined"
            color="warning"
            disabled={ea.paused}
            onClick={() => pause.mutate(ea.ea_id)}
          >
            Pausar
          </Button>
          <Button
            size="small"
            variant="outlined"
            color="success"
            disabled={!ea.paused}
            onClick={() => resume.mutate(ea.ea_id)}
          >
            Retomar
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}

export function EaControlPage() {
  const { data, isLoading } = useEaStatus();
  const eas = data?.eas ?? [];

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <MemoryIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">EA Control Panel</Typography>
      </Stack>

      <Alert severity="info" sx={{ mb: 2 }}>
        Controle seguro do Expert Advisor. Pausar/retomar não envia ordem — apenas
        suspende a operação do robô (preserva capital).
      </Alert>

      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        {eas.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            {isLoading ? "Carregando…" : "Nenhum EA registrado."}
          </Typography>
        )}
        {eas.map((ea) => <EaCard key={ea.ea_id} ea={ea} />)}
      </Stack>
    </Box>
  );
}

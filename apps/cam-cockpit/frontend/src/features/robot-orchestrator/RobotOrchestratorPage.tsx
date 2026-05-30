/**
 * Robot Orchestrator — TASK-U020 (BL-UI-4).
 *
 * Robôs + estratégias com prioridade, conflitos resolvidos
 * (DIRECTIONAL_CONFLICT / AMBIGUOUS_TIE) e estratégias suspensas. Read-only.
 * Flag MULTI_STRATEGY_ENABLED (default false) sempre visível.
 */
import {
  Box, Typography, Stack, Card, CardContent, Chip, Alert, List, ListItem,
  ListItemText,
} from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import { useRobots, type Robot } from "./useRobots";

function RobotCard({ robot }: { robot: Robot }) {
  return (
    <Card data-testid="robot-card" sx={{ minWidth: 280 }}>
      <CardContent>
        <Typography variant="h6">{robot.name}</Typography>
        <List dense>
          {robot.strategies.map((s) => (
            <ListItem key={s.strategy_id} disableGutters
              secondaryAction={
                s.suspended
                  ? <Chip label="SUSPENSA" size="small" color="warning" data-testid="suspended-strategy" />
                  : <Chip label={`P${s.priority}`} size="small" variant="outlined" />
              }
            >
              <ListItemText
                primary={s.name}
                secondary={s.status}
                primaryTypographyProps={{ fontSize: 14 }}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}

export function RobotOrchestratorPage() {
  const { data, isLoading } = useRobots();
  const robots = data?.robots ?? [];
  const multi = data?.multi_strategy_enabled ?? false;

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <SmartToyIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Robot Orchestrator</Typography>
        <Chip
          label={`MULTI_STRATEGY: ${multi ? "ON" : "OFF"}`}
          size="small"
          color={multi ? "warning" : "default"}
          data-testid="multi-strategy-flag"
        />
      </Stack>

      <Alert severity="info" sx={{ mb: 2 }}>
        Robôs agregam estratégias por prioridade estrita. Conflitos
        (DIRECTIONAL_CONFLICT / AMBIGUOUS_TIE) são resolvidos pelo orquestrador.
        Tela read-only.
      </Alert>

      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        {robots.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            {isLoading ? "Carregando…" : "Nenhum robô configurado."}
          </Typography>
        )}
        {robots.map((r) => <RobotCard key={r.id} robot={r} />)}
      </Stack>
    </Box>
  );
}

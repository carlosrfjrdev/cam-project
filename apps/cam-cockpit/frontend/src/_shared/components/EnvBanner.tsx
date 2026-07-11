/**
 * EnvBanner — TASK-U011 (BL-UI-1). Defesa de capital (Don).
 *
 * Exibe o ambiente operacional em TODA tela. REAL é inconfundível (vermelho,
 * texto forte) — o operador nunca confunde demo com dinheiro real.
 *
 * Sem hex hardcoded: cores derivam do theme DS (U012, no-hardcode lint).
 */
import { Box, Typography, useTheme, alpha } from "@mui/material";
import type { Theme } from "@mui/material";
import { useEnvironment, type TradingEnv } from "../hooks/useEnvironment";

interface EnvVisual {
  label: string;
  bg: string;
  fg: string;
  emphasis: boolean;
}

function visualFor(env: TradingEnv, t: Theme): EnvVisual {
  switch (env) {
    case "REAL":
      return {
        label: "● REAL — DINHEIRO REAL ●",
        bg: t.palette.error.main,
        fg: t.palette.error.contrastText,
        emphasis: true,
      };
    case "PAPER":
      return {
        label: "PAPER TRADING",
        bg: alpha(t.palette.warning.main, 0.14),
        fg: t.palette.warning.main,
        emphasis: false,
      };
    case "BACKTEST":
      return {
        label: "BACKTEST",
        bg: t.cam.surface2,
        fg: t.palette.text.secondary,
        emphasis: false,
      };
    case "DEMO":
    default:
      return {
        label: "DEMO",
        bg: alpha(t.palette.primary.main, 0.14),
        fg: t.palette.primary.light,
        emphasis: false,
      };
  }
}

export function EnvBanner({ env: envProp }: { env?: TradingEnv }) {
  const theme = useTheme();
  const resolved = useEnvironment();
  const env = envProp ?? resolved.env;
  const v = visualFor(env, theme);

  return (
    <Box
      role={v.emphasis ? "alert" : "status"}
      data-testid="env-banner"
      data-env={env}
      sx={{
        bgcolor: v.bg,
        color: v.fg,
        px: 3,
        py: v.emphasis ? 1 : 0.5,
        textAlign: "center",
        fontWeight: v.emphasis ? 800 : 600,
        letterSpacing: v.emphasis ? 2 : 1,
        borderBottom: v.emphasis
          ? `2px solid ${theme.palette.error.dark}`
          : `1px solid ${alpha(theme.palette.common.white, 0.06)}`,
      }}
    >
      <Typography variant="caption" sx={{ fontWeight: "inherit", letterSpacing: "inherit" }}>
        AMBIENTE: {v.label}
        {v.emphasis && " — confirme antes de qualquer ação"}
      </Typography>
    </Box>
  );
}

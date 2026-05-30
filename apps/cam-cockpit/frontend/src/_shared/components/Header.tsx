/**
 * Header do cockpit — TASK-U010 (BL-UI-1). Altura 56px.
 * Hamburger (colapsa sidebar) + wordmark CaM + kill switch (Art. 18º, ≤1 toque).
 */
import { AppBar, Toolbar, IconButton, Typography, Box, Tooltip } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { useUiStore } from "../state/uiStore";
import { useKillSwitch } from "../hooks/useKillSwitch";
import { KillSwitchButton } from "./KillSwitchButton";

export const HEADER_HEIGHT = 56;

export function Header() {
  const { toggleSidebar } = useUiStore();
  const { isActive, activate, deactivate } = useKillSwitch();

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        zIndex: (t) => t.zIndex.drawer + 1,
        bgcolor: "background.paper",
        borderBottom: "1px solid",
        borderColor: "divider",
      }}
    >
      <Toolbar variant="dense" sx={{ minHeight: HEADER_HEIGHT, height: HEADER_HEIGHT }}>
        <IconButton
          edge="start"
          aria-label="alternar menu"
          data-testid="sidebar-toggle"
          onClick={toggleSidebar}
          sx={{ mr: 1 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          sx={{ fontWeight: 600, letterSpacing: 1, color: "text.primary" }}
        >
          Ca<Box component="span" sx={{ color: "primary.main" }}>M</Box>
        </Typography>
        <Typography variant="caption" sx={{ ml: 1.5, color: "text.secondary", flexGrow: 1 }}>
          Carlos Alternative Money
        </Typography>

        <Tooltip title="Kill switch — Art. 18º (acionável sem justificar oportunidade perdida)">
          <span>
            <KillSwitchButton
              isActive={isActive}
              onActivate={activate}
              onDeactivate={deactivate}
            />
          </span>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
}

/**
 * Sidebar colapsável — TASK-U010 (BL-UI-1).
 * Expandida 208px / colapsada 56px. Colapsada exibe tooltip no hover.
 */
import { useNavigate, useLocation } from "react-router-dom";
import {
  Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  Tooltip, Typography, Box,
} from "@mui/material";
import { NAV_ITEMS } from "../nav";
import { useUiStore } from "../state/uiStore";

export const SIDEBAR_WIDTH = 208;
export const SIDEBAR_COLLAPSED = 56;
const HEADER_HEIGHT = 56;

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed } = useUiStore();
  const width = sidebarCollapsed ? SIDEBAR_COLLAPSED : SIDEBAR_WIDTH;

  let lastGroup = "";

  return (
    <Drawer
      variant="permanent"
      data-testid="cam-sidebar"
      data-collapsed={sidebarCollapsed ? "true" : "false"}
      sx={{
        width,
        flexShrink: 0,
        whiteSpace: "nowrap",
        "& .MuiDrawer-paper": {
          width,
          boxSizing: "border-box",
          top: HEADER_HEIGHT,
          height: `calc(100% - ${HEADER_HEIGHT}px)`,
          overflowX: "hidden",
          transition: "width 200ms ease",
        },
      }}
    >
      <List dense sx={{ pt: 1 }}>
        {NAV_ITEMS.map((item) => {
          const showGroup = !sidebarCollapsed && item.group !== lastGroup;
          lastGroup = item.group;
          const selected = location.pathname === item.path;
          return (
            <Box key={item.path}>
              {showGroup && (
                <Typography
                  variant="caption"
                  sx={{ px: 2, pt: 1, display: "block", color: "text.secondary", letterSpacing: 1 }}
                >
                  {item.group.toUpperCase()}
                </Typography>
              )}
              <ListItem disablePadding>
                <Tooltip
                  title={sidebarCollapsed ? item.label : ""}
                  placement="right"
                  arrow
                >
                  <ListItemButton
                    selected={selected}
                    onClick={() => navigate(item.path)}
                    sx={{ minHeight: 40, justifyContent: sidebarCollapsed ? "center" : "flex-start" }}
                  >
                    <ListItemIcon sx={{ minWidth: 0, mr: sidebarCollapsed ? 0 : 2, justifyContent: "center" }}>
                      {item.icon}
                    </ListItemIcon>
                    {!sidebarCollapsed && (
                      <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 13 }} />
                    )}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            </Box>
          );
        })}
      </List>
    </Drawer>
  );
}

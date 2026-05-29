import { ReactNode, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText,
  AppBar, Toolbar, Typography, Stack, Divider, Tooltip,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import BookIcon from "@mui/icons-material/Book";
import ReceiptIcon from "@mui/icons-material/Receipt";
import SavingsIcon from "@mui/icons-material/Savings";
import ShieldIcon from "@mui/icons-material/Shield";
import GavelIcon from "@mui/icons-material/Gavel";
import SettingsIcon from "@mui/icons-material/Settings";
import ScienceIcon from "@mui/icons-material/Science";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import BarChartIcon from "@mui/icons-material/BarChart";
import { KillSwitchButton } from "./KillSwitchButton";
import { RiskEngineStatusBanner } from "./RiskEngineStatusBanner";
import { useKillSwitch } from "../hooks/useKillSwitch";

const DRAWER_WIDTH = 220;

const NAV_ITEMS = [
  { label: "Cockpit Live", path: "/", icon: <DashboardIcon /> },
  { label: "Journal", path: "/journal", icon: <BookIcon /> },
  { label: "Ledger Fiscal", path: "/fiscal", icon: <ReceiptIcon /> },
  { label: "Harvest", path: "/harvest", icon: <SavingsIcon /> },
  { label: "Risk Console", path: "/risk", icon: <ShieldIcon /> },
  { label: "Constituição", path: "/constitution", icon: <GavelIcon /> },
  { label: "Paper Trading", path: "/paper-trading", icon: <ScienceIcon /> },
  { label: "Carteira Hard", path: "/carteira-hard", icon: <AccountBalanceIcon /> },
  { label: "Backtest", path: "/backtest", icon: <BarChartIcon /> },
  { label: "Configurações", path: "/settings", icon: <SettingsIcon /> },
];

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { isActive, activate, deactivate } = useKillSwitch();
  const [lastBlockReason] = useState<string | null>(null);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ fontWeight: 700, mr: 2, letterSpacing: 2 }}>
            CaM
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            Carlos Alternative Money
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Tooltip title="Art. 18º — Acionável sem justificar oportunidade perdida">
              <span>
                <KillSwitchButton
                  isActive={isActive}
                  onActivate={activate}
                  onDeactivate={deactivate}
                />
              </span>
            </Tooltip>
          </Stack>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", top: 64 },
        }}
      >
        <List dense>
          {NAV_ITEMS.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 13 }} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, mt: 8, minWidth: 0 }}>
        <RiskEngineStatusBanner
          killSwitchActive={isActive}
          riskEngineBlocked={!!lastBlockReason}
          blockReason={lastBlockReason ?? undefined}
        />
        {children}
      </Box>
    </Box>
  );
}

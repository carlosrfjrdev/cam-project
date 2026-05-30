/**
 * AppShell do cockpit — TASK-U010 (BL-UI-1). Full Web, desktop-first.
 * Header (56px) + Sidebar colapsável + Breadcrumb + Content Area.
 *
 * Defesa de capital transversal: EnvBanner (ambiente) e RiskEngineStatusBanner
 * (kill switch) ficam acima do conteúdo, visíveis em toda rota (U014/U015).
 * Single-operator — sem multi-tenant.
 */
import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { Box, Breadcrumbs, Typography } from "@mui/material";
import { Header, HEADER_HEIGHT } from "./Header";
import { Sidebar } from "./Sidebar";
import { EnvBanner } from "./EnvBanner";
import { RiskEngineStatusBanner } from "./RiskEngineStatusBanner";
import { useKillSwitch } from "../hooks/useKillSwitch";
import { NAV_ITEMS } from "../nav";

function useCrumbLabel(pathname: string): string {
  const match = NAV_ITEMS.find((i) => i.path === pathname);
  if (match) return match.label;
  if (pathname === "/") return "Cockpit Live";
  return pathname.replace("/", "").replace(/-/g, " ") || "Cockpit";
}

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const { isActive } = useKillSwitch();
  const crumb = useCrumbLabel(location.pathname);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <Header />
      <Sidebar />
      <Box
        component="main"
        sx={{ flexGrow: 1, minWidth: 0, mt: `${HEADER_HEIGHT}px`, display: "flex", flexDirection: "column" }}
      >
        {/* Defesa de capital — sempre no topo, toda rota operacional */}
        <EnvBanner />
        <RiskEngineStatusBanner
          killSwitchActive={isActive}
          riskEngineBlocked={false}
        />

        <Box sx={{ px: 3, pt: 2 }}>
          <Breadcrumbs aria-label="trilha">
            <Typography variant="body2" color="text.secondary">CaM</Typography>
            <Typography variant="body2" color="text.primary">{crumb}</Typography>
          </Breadcrumbs>
        </Box>

        <Box sx={{ flexGrow: 1 }}>{children}</Box>
      </Box>
    </Box>
  );
}

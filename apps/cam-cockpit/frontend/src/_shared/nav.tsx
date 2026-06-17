/**
 * Configuração de navegação do cockpit — TASK-U010 (BL-UI-1).
 * Single-operator: sem troca de tenant nem gestão de usuários.
 */
import type { ReactNode } from "react";
import DashboardIcon from "@mui/icons-material/Dashboard";
import GavelIcon from "@mui/icons-material/Gavel";
import HubIcon from "@mui/icons-material/Hub";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import ShieldIcon from "@mui/icons-material/Shield";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import MemoryIcon from "@mui/icons-material/Memory";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import BookIcon from "@mui/icons-material/Book";
import ReceiptIcon from "@mui/icons-material/Receipt";
import SavingsIcon from "@mui/icons-material/Savings";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import ScienceIcon from "@mui/icons-material/Science";
import BiotechIcon from "@mui/icons-material/Biotech";
import BarChartIcon from "@mui/icons-material/BarChart";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import SettingsIcon from "@mui/icons-material/Settings";
import TravelExploreIcon from "@mui/icons-material/TravelExplore";
import TuneIcon from "@mui/icons-material/Tune";
import StorageIcon from "@mui/icons-material/Storage";
import PsychologyIcon from "@mui/icons-material/Psychology";
import InsightsIcon from "@mui/icons-material/Insights";
import HistoryIcon from "@mui/icons-material/History";

export interface NavItem {
  label: string;
  path: string;
  icon: ReactNode;
  group: string;
  /**
   * MVP Inspetor de Ativo (SCOPE-Inspetor-Consolidado §2). Quando `true`, o item
   * aparece no sidebar. As telas não-MVP ficam ocultas (sem deletar código —
   * rota continua registrada em router.tsx, acessível por URL direta).
   */
  visibleInMvp?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Inspetor de Ativo", path: "/inspetor", icon: <TravelExploreIcon />, group: "Pesquisa", visibleInMvp: true },
  { label: "Dataset", path: "/dataset", icon: <StorageIcon />, group: "Pesquisa", visibleInMvp: true },
  { label: "Quant Lab", path: "/lab", icon: <ScienceIcon />, group: "Pesquisa", visibleInMvp: true },
  { label: "Trade Analyzer", path: "/trade-analyzer", icon: <PsychologyIcon />, group: "Pesquisa", visibleInMvp: true },
  { label: "↳ Históricos", path: "/trade-analyzer/history", icon: <HistoryIcon />, group: "Pesquisa", visibleInMvp: true },
  { label: "Operation Analyzer", path: "/operation-analyzer", icon: <InsightsIcon />, group: "Pesquisa", visibleInMvp: true },

  { label: "Estratégias", path: "/strategy-lab/strategies", icon: <HubIcon />, group: "StrategyLab", visibleInMvp: true },
  { label: "Backtest (RunTests)", path: "/strategy-lab/runtests", icon: <TuneIcon />, group: "StrategyLab", visibleInMvp: true },
  { label: "Robôs (Experts)", path: "/strategy-lab/experts", icon: <SmartToyIcon />, group: "StrategyLab", visibleInMvp: true },

  { label: "Cockpit Live", path: "/", icon: <DashboardIcon />, group: "Operação", visibleInMvp: true },
  { label: "Order Gateway", path: "/order-gateway", icon: <GavelIcon />, group: "Operação" },
  { label: "Risk Console", path: "/risk", icon: <ShieldIcon />, group: "Operação" },
  { label: "EA Control", path: "/ea-control", icon: <MemoryIcon />, group: "Operação" },

  { label: "Strategy Registry", path: "/strategies", icon: <HubIcon />, group: "Estratégia" },
  { label: "Robot Orchestrator", path: "/robots", icon: <SmartToyIcon />, group: "Estratégia" },
  { label: "Escalonamento", path: "/scaling", icon: <TrendingUpIcon />, group: "Estratégia" },
  { label: "Market Data", path: "/market-data", icon: <ShowChartIcon />, group: "Estratégia" },

  { label: "Journal", path: "/journal", icon: <BookIcon />, group: "Registro" },
  { label: "Ledger Fiscal", path: "/fiscal", icon: <ReceiptIcon />, group: "Registro" },
  { label: "Harvest", path: "/harvest", icon: <SavingsIcon />, group: "Registro" },

  { label: "Carteira Hard", path: "/carteira-hard", icon: <AccountBalanceIcon />, group: "Patrimônio" },
  { label: "Research", path: "/research", icon: <BiotechIcon />, group: "Patrimônio" },
  { label: "Backtest", path: "/backtest", icon: <BarChartIcon />, group: "Patrimônio" },
  { label: "Paper Trading", path: "/paper-trading", icon: <ScienceIcon />, group: "Patrimônio" },

  { label: "Constituição", path: "/constitution", icon: <MenuBookIcon />, group: "Sistema", visibleInMvp: true },
  { label: "Configurações", path: "/settings", icon: <SettingsIcon />, group: "Sistema", visibleInMvp: true },
];

/** Telas visíveis no MVP do Inspetor. Trocar `visibleInMvp` revela cada tela. */
export const MVP_NAV_ITEMS = NAV_ITEMS.filter((i) => i.visibleInMvp);

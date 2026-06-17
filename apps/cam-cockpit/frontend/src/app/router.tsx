import { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import { AppShell } from "../_shared/components/AppShell";
import { CockpitPage } from "../features/cockpit/CockpitPage";
import { JournalPage } from "../features/journal/JournalPage";
import { FiscalPage } from "../features/fiscal/FiscalPage";
import { HarvestPage } from "../features/harvest/HarvestPage";
import { RiskConsolePage } from "../features/risk-console/RiskConsolePage";
import { ConstitutionPage } from "../features/constitution/ConstitutionPage";
import { SettingsPage } from "../features/settings/SettingsPage";
import { PaperTradingPage } from "../features/paper-trading/PaperTradingPage";
import { CarteiraHardPage } from "../features/carteira-hard/CarteiraHardPage";
import { BacktestPage } from "../features/backtest/BacktestPage";
import { OrderGatewayPage } from "../features/order-gateway/OrderGatewayPage";
import { StrategyRegistryPage } from "../features/strategies/StrategyRegistryPage";
import { EaControlPage } from "../features/ea-control/EaControlPage";
import { MarketDataPage } from "../features/market-data/MarketDataPage";
import { RobotOrchestratorPage } from "../features/robot-orchestrator/RobotOrchestratorPage";
import { ScalingPage } from "../features/scaling/ScalingPage";
import { InspetorPage } from "../features/inspetor/InspetorPage";
import { QuantLabPage } from "../features/quant-lab/QuantLabPage";
import { DatasetPage } from "../features/dataset/DatasetPage";
import { AssetsStrategyPage } from "../features/strategy-lab/AssetsStrategyPage";
import { AssetsRunTestsPage } from "../features/strategy-lab/AssetsRunTestsPage";
import { AssetsExpertsPage } from "../features/strategy-lab/AssetsExpertsPage";
import { TradeAnalyzerPage } from "../features/trade-analyzer/TradeAnalyzerPage";
import { TradeAnalyzerHistoryPage } from "../features/trade-analyzer/TradeAnalyzerHistoryPage";
import { OperationAnalyzerPage } from "../features/operation-analyzer/OperationAnalyzerPage";

// U023 — Research carrega Recharts: rota lazy (bundle isolado).
const ResearchPage = lazy(() =>
  import("../features/research/ResearchPage").then((m) => ({ default: m.ResearchPage })),
);

export function AppRouter() {
  return (
    <AppShell>
      <Suspense
        fallback={
          <Box sx={{ display: "flex", justifyContent: "center", p: 6 }}>
            <CircularProgress />
          </Box>
        }
      >
        <Routes>
          <Route path="/" element={<CockpitPage />} />
          <Route path="/inspetor" element={<InspetorPage />} />
          <Route path="/trade-analyzer" element={<TradeAnalyzerPage />} />
          <Route path="/trade-analyzer/history" element={<TradeAnalyzerHistoryPage />} />
          <Route path="/operation-analyzer" element={<OperationAnalyzerPage />} />
          <Route path="/dataset" element={<DatasetPage />} />
          <Route path="/lab" element={<QuantLabPage />} />
          <Route path="/strategy-lab/strategies" element={<AssetsStrategyPage />} />
          <Route path="/strategy-lab/runtests" element={<AssetsRunTestsPage />} />
          <Route path="/strategy-lab/experts" element={<AssetsExpertsPage />} />
          <Route path="/order-gateway" element={<OrderGatewayPage />} />
          <Route path="/risk" element={<RiskConsolePage />} />
          <Route path="/ea-control" element={<EaControlPage />} />
          <Route path="/strategies" element={<StrategyRegistryPage />} />
          <Route path="/robots" element={<RobotOrchestratorPage />} />
          <Route path="/scaling" element={<ScalingPage />} />
          <Route path="/market-data" element={<MarketDataPage />} />
          <Route path="/journal" element={<JournalPage />} />
          <Route path="/fiscal" element={<FiscalPage />} />
          <Route path="/harvest" element={<HarvestPage />} />
          <Route path="/carteira-hard" element={<CarteiraHardPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
          <Route path="/paper-trading" element={<PaperTradingPage />} />
          <Route path="/constitution" element={<ConstitutionPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}

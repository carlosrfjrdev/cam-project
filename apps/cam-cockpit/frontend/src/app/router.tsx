import { Routes, Route } from "react-router-dom";
import { Layout } from "../_shared/components/Layout";
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

export function AppRouter() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<CockpitPage />} />
        <Route path="/journal" element={<JournalPage />} />
        <Route path="/fiscal" element={<FiscalPage />} />
        <Route path="/harvest" element={<HarvestPage />} />
        <Route path="/risk" element={<RiskConsolePage />} />
        <Route path="/constitution" element={<ConstitutionPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/paper-trading" element={<PaperTradingPage />} />
        <Route path="/carteira-hard" element={<CarteiraHardPage />} />
        <Route path="/backtest" element={<BacktestPage />} />
      </Routes>
    </Layout>
  );
}

// Backend API types

export interface HealthResponse {
  status: string;
}

export interface KillSwitchStatus {
  active: boolean;
  last_action: string | null;
  last_reason: string | null;
}

export interface RiskDecision {
  approved: boolean;
  reason: string | null;
  validator: string | null;
}

export interface JournalEntry {
  id: string;
  trade_date: string;
  asset: string;
  direction: "BUY" | "SELL";
  contracts: number;
  entry_price: number;
  exit_price: number;
  result_gross: number;
  costs: number;
  tax_provisioned: number;
  result_net: number;
  strategy: string;
  source: "MANUAL" | "CSV_IMPORT";
  notes: string | null;
  created_at: string;
}

// Backend retorna Decimal serializado como string. Tratar com Number() na UI.
export interface FiscalApuration {
  month: string;
  gross_result: string | number;
  net_result: string | number;
  taxable_base: string | number;
  ir_due: string | number;
  darf_value: string | number;
}

export interface Darf {
  month: string;
  value: string | number;
  due_date: string;
  status: "PENDING" | "PAID" | "OVERDUE";
  paid_at: string | null;
  is_compliant: boolean;
}

export interface BucketSnapshot {
  bucket_derivativo: number;
  buffer_operacional: number;
  carteira_hard: number;
  last_harvest_at: string | null;
}

export interface HarvestProposal {
  net_profit: number;
  carteira_hard_transfer: number;
  buffer_transfer: number;
  proposed_at: string;
}

export interface BacktestConfig {
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  phase: number;
}

export interface BacktestMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_pnl_gross: number;
  total_pnl_net: number;
  max_drawdown: number;
  sharpe_ratio: number;
  profit_factor: number;
}

export interface BacktestRun {
  id: string;
  config: BacktestConfig;
  metrics: BacktestMetrics;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  created_at: string;
}

export interface PaperTradeSimulation {
  approved: boolean;
  reason: string | null;
  simulated_result_gross: number;
  simulated_result_net: number;
}

export interface ConstitutionVersion {
  version: string;
  content: string;
  effective_date: string;
  hash: string;
}

export interface RiskStatus {
  kill_switch_active: boolean;
  daily_pnl_net: number;
  daily_loss_limit: number;
  weekly_loss_limit: number;
  monthly_loss_limit: number;
  gain_lock_reached: boolean;
  current_phase: number;
  tax_compliant: boolean;
  open_positions: number;
}

export interface ImportResult {
  imported: number;
  duplicates: number;
  errors: number;
}

// MT5 integration (SPEC v0.2)
export interface MT5BridgeStatus {
  state: "ONLINE" | "OFFLINE" | "RECONNECTING";
  last_heartbeat_at: string | null;
  last_heartbeat_age_ms: number | null;
  avg_latency_ms: number | null;
  host: string;
  pub_port: number;
  req_port: number;
  mt5_path: string | null;
}

export interface MT5Position {
  symbol: string;
  contracts: number;
  direction: "LONG" | "SHORT";
  entry_price: string | number;
  current_price: string | number;
  pnl_gross: string | number;
  pnl_net: string | number;
  opened_at: string;
}

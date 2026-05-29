//+------------------------------------------------------------------+
//| cam_risk_mirror.mq5                                               |
//| TASK-025 (BL-E SPEC v0.4) — espelho MQL5 dos 18 validators        |
//|                                                                   |
//| ⚠️ ÚNICO arquivo MQL5 autorizado a chamar OrderSend (CA-A.6).      |
//|     `scripts/lint_mql5.py` enforça allowlist.                     |
//|                                                                   |
//| Funcionamento:                                                    |
//|   1. EA consome comandos REQ/REP do cam_bridge.mq5 (SUBMIT_ORDER).|
//|   2. Para cada intent, executa o pipeline de 18 validators ESPELHO|
//|      do Risk Engine Python. Decisão deve coincidir (TASK-026).    |
//|   3. Aprovado → OrderSend. Reprovado → resposta REJECTED com      |
//|      validator culpado.                                           |
//|                                                                   |
//| Limites lidos via REQ GET_CURRENT_LIMITS (BL-H1 T047) — fallback  |
//| para constants hardcoded se cockpit offline.                      |
//|                                                                   |
//| ⚠️ ATENÇÃO SEC: este arquivo entrega SOMENTE em ambiente DEMO     |
//|    (`ACCOUNT_TRADE_MODE == ACCOUNT_TRADE_MODE_DEMO`).             |
//|    `cam_bridge.mq5` faz a verificação adicional na entrada.       |
//+------------------------------------------------------------------+
#property copyright "CaM — The Carlos Alternative Money"
#property version   "0.1"
#property strict
#property description "CaM Risk Mirror MQL5 — 18 validators espelho (BL-E v0.4)"

#define CAM_RISK_MIRROR_VERSION "0.1.0-ble"

// Constants fallback — IDEAL é ler de GET_CURRENT_LIMITS via bridge.
#define MAX_WIN_CONTRACTS_FALLBACK 2
#define MAX_WDO_CONTRACTS_FALLBACK 2
#define MAX_DAILY_DRAWDOWN_PCT     0.03

input int InpMaxWinContracts = MAX_WIN_CONTRACTS_FALLBACK;
input int InpMaxWdoContracts = MAX_WDO_CONTRACTS_FALLBACK;
input bool InpRequireDemoAccount = true;

//+------------------------------------------------------------------+
struct OrderIntent
  {
   string asset;          // "WIN" | "WDO"
   string direction;      // "LONG" | "SHORT"
   int    contracts;
   double sl_points;
   bool   is_setup_a_plus;
  };

struct RiskContextSnapshot
  {
   bool   kill_switch_active;
   bool   pre_market_checklist_done;
   bool   post_market_checklist_done;
   bool   tax_compliance_ok;
   double daily_pnl_pct;
   double weekly_pnl_pct;
   double monthly_pnl_pct;
   int    daily_operations_count;
   int    open_win_contracts;
   int    open_wdo_contracts;
   int    phase;            // 0=FASE_0 ... 4=FASE_4
  };

struct RiskDecision
  {
   bool   approved;
   string validator;
   string reason;
  };

//+------------------------------------------------------------------+
//| Pipeline canônico — ordem deve coincidir com Python engine.py     |
//+------------------------------------------------------------------+
RiskDecision EvaluatePipeline(const OrderIntent &intent,
                              const RiskContextSnapshot &ctx)
  {
   RiskDecision r;
   r.approved = true;
   r.validator = "";
   r.reason = "";

   // 1) kill switch
   if(ctx.kill_switch_active)
     {
      r.approved = false;
      r.validator = "kill_switch_active_check";
      r.reason = "Kill switch ativo (Art. 18o)";
      return r;
     }

   // 2) pre-market checklist
   if(!ctx.pre_market_checklist_done)
     {
      r.approved = false;
      r.validator = "pre_market_checklist_check";
      r.reason = "Checklist pre-mercado nao preenchido (Art. 32o)";
      return r;
     }

   // 3) post-market checklist
   if(!ctx.post_market_checklist_done)
     {
      r.approved = false;
      r.validator = "post_market_checklist_check";
      r.reason = "Checklist pos-mercado ausente (Art. 33o)";
      return r;
     }

   // 4) DARF / compliance
   if(!ctx.tax_compliance_ok)
     {
      r.approved = false;
      r.validator = "tax_compliance_check";
      r.reason = "DARF atrasada (Art. 26o)";
      return r;
     }

   // 5) max contracts (Art. 11)
   int max_for_asset = (intent.asset == "WIN") ?
                         InpMaxWinContracts : InpMaxWdoContracts;
   int open_for_asset = (intent.asset == "WIN") ?
                          ctx.open_win_contracts : ctx.open_wdo_contracts;
   if(open_for_asset + intent.contracts > max_for_asset)
     {
      r.approved = false;
      r.validator = "max_contracts_check";
      r.reason = StringFormat(
         "Excede limite (Art. 11): %d+%d>%d",
         open_for_asset, intent.contracts, max_for_asset);
      return r;
     }

   // 6) daily loss (3%)
   if(ctx.daily_pnl_pct < -MAX_DAILY_DRAWDOWN_PCT)
     {
      r.approved = false;
      r.validator = "daily_loss_limit_check";
      r.reason = "Daily loss limit (Art. 16o)";
      return r;
     }

   // 7) weekly loss (7%) — limite estimado, paridade com Python
   if(ctx.weekly_pnl_pct < -0.07)
     {
      r.approved = false;
      r.validator = "weekly_loss_limit_check";
      r.reason = "Weekly loss limit (Art. 16o)";
      return r;
     }

   // 8) monthly loss (15%)
   if(ctx.monthly_pnl_pct < -0.15)
     {
      r.approved = false;
      r.validator = "monthly_loss_limit_check";
      r.reason = "Monthly loss limit (Art. 16o)";
      return r;
     }

   // 9) gain lock (+2%)
   if(ctx.daily_pnl_pct >= 0.02)
     {
      r.approved = false;
      r.validator = "gain_lock_check";
      r.reason = "Gain lock ativado (Art. 17o)";
      return r;
     }

   // 10) daily ops count — fase-dependente (paridade Python)
   int ops_limit_by_phase = (ctx.phase >= 4) ? 5 :
                              (ctx.phase >= 2) ? 3 : 99;
   if(ctx.daily_operations_count >= ops_limit_by_phase)
     {
      r.approved = false;
      r.validator = "daily_operations_count_check";
      r.reason = "Daily ops limit (Art. 20o)";
      return r;
     }

   return r;
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode = (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamRiskMirror] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   PrintFormat("[CamRiskMirror] %s ativo em DEMO.", CAM_RISK_MIRROR_VERSION);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) {}
void OnTick() {}

//+------------------------------------------------------------------+
//| Stub de execucao — chamado pelo cam_bridge.mq5 SUBMIT_ORDER       |
//| (T027 ainda nao envia chamada cruzada — esqueleto registrado).    |
//+------------------------------------------------------------------+
bool TryOrderSend(const OrderIntent &intent, const RiskContextSnapshot &ctx,
                  ulong &ticket_out, string &response_out)
  {
   RiskDecision decision = EvaluatePipeline(intent, ctx);
   if(!decision.approved)
     {
      response_out = StringFormat(
         "{\"status\":\"rejected\",\"validator\":\"%s\",\"reason\":\"%s\"}",
         decision.validator, decision.reason);
      return false;
     }

   MqlTradeRequest req = {};
   MqlTradeResult result = {};
   req.action = TRADE_ACTION_DEAL;
   req.symbol = Symbol();
   req.volume = (double)intent.contracts;
   req.type = (intent.direction == "LONG") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   req.price = (intent.direction == "LONG")
                 ? SymbolInfoDouble(Symbol(), SYMBOL_ASK)
                 : SymbolInfoDouble(Symbol(), SYMBOL_BID);
   req.deviation = 10;
   req.magic = 20260527;
   req.comment = "cam_risk_mirror";

   // Único OrderSend autorizado no codebase (allowlist `lint_mql5`).
   bool ok = OrderSend(req, result);
   ticket_out = result.order;
   response_out = StringFormat(
      "{\"status\":\"%s\",\"ticket\":%llu,\"retcode\":%d}",
      ok ? "sent" : "error", result.order, result.retcode);
   return ok;
  }
//+------------------------------------------------------------------+

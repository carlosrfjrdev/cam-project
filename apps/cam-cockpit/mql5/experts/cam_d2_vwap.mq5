//+------------------------------------------------------------------+
//| cam_d2_vwap.mq5                                                   |
//| StrategyLab — D2 (VWAP Mean-Reversion fade, WDO) — GRAVADOR.     |
//|                                                                   |
//| ADR-SL-01/04: lado MQL5 da dupla implementacao. Implementa A MAO  |
//| a MESMA logica de cam/features/strategy_lab/strategies/d2_vwap.py |
//| (referencia). GRAVADOR de paridade: NAO envia ordem; exporta o    |
//| ledger canonico CSV p/ casar com o backtest Python. Fora da       |
//| allowlist de OrderSend do lint_mql5.                              |
//|                                                                   |
//| Logica (ficha D2): VWAP e sigma CUMULATIVOS da sessao (ponderado  |
//| por volume; typical=(h+l+c)/3). FADE na tocada de +-k_entry*sigma |
//| (short na esticada pra cima, long pra baixo); alvo = VWAP; stop = |
//| VWAP +- k_stop*sigma (congelados no fill). Sem runner. warmup     |
//| antes de operar. 1 sinal por excursao (re-arma ao voltar a banda).|
//|                                                                   |
//| Paridade: subset C1-C6 (fill next-bar-open, pior caso intrabar,   |
//| gap honesto). Valores BRUTOS. SEC: guard-rail DEMO (sem ordem).   |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D2 VWAP fade — gravador de ledger p/ paridade (sem OrderSend)"

#define CAM_D2_VWAP_VERSION "0.1.0"

//--- Parametros (espelham D2Params do Python) -----------------------
input double InpKEntry           = 2.0;    // esticada de entrada (em sigma)
input double InpKStop            = 3.0;    // stop alem de k_stop*sigma
input int    InpWarmupBars       = 30;     // barras minimas na sessao p/ sigma
input int    InpSessionOpenHour  = 9;
input int    InpSessionOpenMin   = 0;
input int    InpEntryUntilHour   = 17;
input int    InpEntryUntilMin    = 0;
input int    InpSessionCloseHour = 17;
input int    InpSessionCloseMin  = 55;
//--- Contabilizacao bruta -------------------------------------------
input double InpPointValue       = 5.0;    // valor financeiro de 1 ponto (WDO ~ 5)
input int    InpQty              = 1;
input string InpLedgerFile       = "cam_d2_vwap_ledger.csv";
input bool   InpRequireDemoAccount = true;

//--- Estado: VWAP/sigma cumulativos da sessao -----------------------
string   g_session    = "";
double   g_sum_pv     = 0.0;
double   g_sum_v      = 0.0;
double   g_sum_pv2    = 0.0;
int      g_n          = 0;
bool     g_armed_long = true;
bool     g_armed_short= true;

// sinal pendente (consumido no open seguinte)
bool     g_pending      = false;
int      g_pending_side = 0;
double   g_pending_stop = 0.0;
double   g_pending_tgt  = 0.0;

// posicao aberta
bool     g_pos_open     = false;
int      g_pos_side     = 0;
datetime g_pos_ts_entry = 0;
double   g_pos_entry    = 0.0;
double   g_pos_stop     = 0.0;
double   g_pos_tgt      = 0.0;
int      g_pair_id      = 0;

datetime g_last_bar     = 0;
int      g_file         = INVALID_HANDLE;
int      g_trades_out   = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD2Vwap] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_file = FileOpen(InpLedgerFile, FILE_WRITE | FILE_CSV | FILE_ANSI, ';');
   if(g_file == INVALID_HANDLE)
     {
      PrintFormat("[CamD2Vwap] Falha ao abrir ledger '%s'.", InpLedgerFile);
      return(INIT_FAILED);
     }
   FileWrite(g_file, "pair_id", "leg", "symbol", "ts_entry", "price_entry",
             "ts_exit", "price_exit", "qty", "exit_reason", "pnl_bruto",
             "volume_financeiro");
   PrintFormat("[CamD2Vwap] %s ativo. Symbol=%s -> ledger '%s'.",
               CAM_D2_VWAP_VERSION, _Symbol, InpLedgerFile);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(g_pos_open)
     {
      double cl = iClose(_Symbol, _Period, 1);
      datetime t = iTime(_Symbol, _Period, 1);
      if(cl > 0.0) RecordExit(t, cl, "session");
     }
   if(g_file != INVALID_HANDLE)
     {
      FileClose(g_file);
      PrintFormat("[CamD2Vwap] Ledger fechado: %d trade(s).", g_trades_out);
     }
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar) return;
   g_last_bar = cur;
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iOpen(_Symbol,_Period,1), iHigh(_Symbol,_Period,1),
              iLow(_Symbol,_Period,1), iClose(_Symbol,_Period,1),
              (double)iVolume(_Symbol,_Period,1));
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double o, double h, double l, double c, double vol)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      g_session = session;
      g_sum_pv = 0.0; g_sum_v = 0.0; g_sum_pv2 = 0.0; g_n = 0;
      g_armed_long = true; g_armed_short = true;
      if(g_pos_open) RecordExit(t, o, "session");
     }

   // acumula VWAP/sigma da sessao (inclui esta barra) — antes de avaliar sinal.
   double tp = (h + l + c) / 3.0;
   double v  = (vol > 0.0) ? vol : 1.0;
   g_sum_pv  += tp * v;
   g_sum_v   += v;
   g_sum_pv2 += tp * tp * v;
   g_n++;

   // 1) saida da posicao aberta (pior caso; alvo/stop congelados).
   if(g_pos_open)
     {
      double xp; string rs;
      if(ResolveExit(o, h, l, c, t, xp, rs)) RecordExit(t, xp, rs);
     }

   // 2) entrada: pendente do bar anterior -> open desta (next-bar-open).
   if(!g_pos_open && g_pending)
     {
      g_pos_open = true; g_pos_side = g_pending_side; g_pos_ts_entry = t;
      g_pos_entry = o; g_pos_stop = g_pending_stop; g_pos_tgt = g_pending_tgt;
     }
   g_pending = false;

   // 3) janela + warmup + sigma.
   int tod = MinutesOfDay(t);
   int beg = InpSessionOpenHour*60 + InpSessionOpenMin;
   int cut = InpEntryUntilHour*60 + InpEntryUntilMin;
   if(tod < beg || tod >= cut) return;
   if(g_n < InpWarmupBars || g_sum_v <= 0.0) return;

   double vwap = g_sum_pv / g_sum_v;
   double var  = MathMax(0.0, g_sum_pv2 / g_sum_v - vwap * vwap);
   double sg   = MathSqrt(var);
   if(sg <= 0.0) return;

   double ue = vwap + InpKEntry * sg;
   double le = vwap - InpKEntry * sg;

   // re-arma dentro da banda; senao dispara o fade (congela alvo=VWAP, stop=k_stop*sg).
   if(c >= le && c <= ue)
     { g_armed_long = true; g_armed_short = true; return; }

   if(g_pos_open) return;

   if(g_armed_short && c > ue)
     {
      g_armed_short = false; g_pending = true; g_pending_side = -1;
      g_pending_stop = vwap + InpKStop * sg; g_pending_tgt = vwap;
     }
   else if(g_armed_long && c < le)
     {
      g_armed_long = false; g_pending = true; g_pending_side = +1;
      g_pending_stop = vwap - InpKStop * sg; g_pending_tgt = vwap;
     }
  }

//+------------------------------------------------------------------+
//| Saida pior caso (C5/C6). Alvo/stop congelados; sempre ha alvo.    |
//+------------------------------------------------------------------+
bool ResolveExit(double o, double h, double l, double c, datetime t,
                 double &xprice, string &reason)
  {
   bool is_long = (g_pos_side > 0);
   double stop = g_pos_stop, tgt = g_pos_tgt;
   if(is_long)
     {
      if(o <= stop) { xprice=o; reason="stop";   return true; }
      if(o >= tgt)  { xprice=o; reason="target"; return true; }
      if(l <= stop) { xprice=stop; reason="stop";   return true; }
      if(h >= tgt)  { xprice=tgt;  reason="target"; return true; }
     }
   else
     {
      if(o >= stop) { xprice=o; reason="stop";   return true; }
      if(o <= tgt)  { xprice=o; reason="target"; return true; }
      if(h >= stop) { xprice=stop; reason="stop";   return true; }
      if(l <= tgt)  { xprice=tgt;  reason="target"; return true; }
     }
   int tod = MinutesOfDay(t);
   if(tod >= InpSessionCloseHour*60 + InpSessionCloseMin)
     { xprice=c; reason="session"; return true; }
   return false;
  }

//+------------------------------------------------------------------+
void RecordExit(datetime ts_exit, double price_exit, string reason)
  {
   double dir = (g_pos_side > 0) ? 1.0 : -1.0;
   double pnl = (price_exit - g_pos_entry) * dir * (double)InpQty * InpPointValue;
   double volf = (MathAbs(g_pos_entry) + MathAbs(price_exit)) * (double)InpQty * InpPointValue;
   string leg = (g_pos_side > 0) ? "long" : "short";
   if(g_file != INVALID_HANDLE)
     {
      FileWrite(g_file, IntegerToString(g_pair_id), leg, _Symbol,
                FmtTs(g_pos_ts_entry), DoubleToString(g_pos_entry, _Digits),
                FmtTs(ts_exit), DoubleToString(price_exit, _Digits),
                IntegerToString(InpQty), reason,
                DoubleToString(pnl, 2), DoubleToString(volf, 2));
      g_trades_out++;
     }
   g_pair_id++; g_pos_open = false; g_pos_side = 0;
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t) { MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
string FmtTs(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02dT%02d:%02d:%02d", s.year,s.mon,s.day,s.hour,s.min,s.sec); }
//+------------------------------------------------------------------+

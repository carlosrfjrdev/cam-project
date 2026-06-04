//+------------------------------------------------------------------+
//| cam_d2_vwap_exec.mq5                                              |
//| StrategyLab — D2 (VWAP Mean-Reversion fade, WDO) — EXECUTOR.     |
//|                                                                   |
//| ADR-SL-04: executor real da D2. Opera o FADE a mercado com SL/TP  |
//| (CTrade), visivel no Strategy Tester. Mesma logica de d2_vwap.py  |
//| (referencia) e do gravador cam_d2_vwap.mq5. Estrategia PURA, sem  |
//| Risk Engine nesta onda. Na allowlist do lint_mql5 (envia ordem).  |
//|                                                                   |
//| Logica: VWAP+sigma cumulativos da sessao; quando o preco estica   |
//| +-k_entry*sigma, FADE a mercado (short na esticada pra cima, long |
//| pra baixo); TP = VWAP; SL = VWAP +- k_stop*sigma. Sem runner.     |
//|                                                                   |
//| SEC: guard-rail duplo DEMO (input + ACCOUNT_TRADE_MODE).          |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D2 VWAP fade — EXECUTOR (opera; DEMO-only)"

#include <Trade/Trade.mqh>

#define CAM_D2_EXEC_VERSION "0.1.0"

input double InpKEntry           = 2.0;
input double InpKStop            = 3.0;
input int    InpWarmupBars       = 30;
input int    InpSessionOpenHour  = 9;
input int    InpSessionOpenMin   = 0;
input int    InpEntryUntilHour   = 17;
input int    InpEntryUntilMin    = 0;
input int    InpSessionCloseHour = 17;
input int    InpSessionCloseMin  = 55;
input double InpLots             = 1.0;
input long   InpMagic            = 20260604;
input ulong  InpDeviationPoints  = 10;
input bool   InpRequireDemoAccount = true;

CTrade   g_trade;
string   g_session    = "";
double   g_sum_pv=0.0, g_sum_v=0.0, g_sum_pv2=0.0;
int      g_n=0;
bool     g_armed_long=true, g_armed_short=true;
datetime g_last_bar=0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD2Exec] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpDeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   PrintFormat("[CamD2Exec] %s ativo. Symbol=%s Lots=%.2f.",
               CAM_D2_EXEC_VERSION, _Symbol, InpLots);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar) return;
   g_last_bar = cur;
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iHigh(_Symbol,_Period,1), iLow(_Symbol,_Period,1),
              iClose(_Symbol,_Period,1), (double)iVolume(_Symbol,_Period,1));
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double h, double l, double c, double vol)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      g_session = session;
      g_sum_pv=0.0; g_sum_v=0.0; g_sum_pv2=0.0; g_n=0;
      g_armed_long=true; g_armed_short=true;
     }

   double tp = (h + l + c) / 3.0;
   double v  = (vol > 0.0) ? vol : 1.0;
   g_sum_pv += tp*v; g_sum_v += v; g_sum_pv2 += tp*tp*v; g_n++;

   int tod = MinutesOfDay(t);
   int s_close = InpSessionCloseHour*60 + InpSessionCloseMin;
   // flat compulsorio no fim da sessao.
   if(tod >= s_close)
     {
      if(HasPosition()) g_trade.PositionClose(_Symbol);
      return;
     }

   int beg = InpSessionOpenHour*60 + InpSessionOpenMin;
   int cut = InpEntryUntilHour*60 + InpEntryUntilMin;
   if(tod < beg || tod >= cut) return;
   if(g_n < InpWarmupBars || g_sum_v <= 0.0) return;

   double vwap = g_sum_pv/g_sum_v;
   double var  = MathMax(0.0, g_sum_pv2/g_sum_v - vwap*vwap);
   double sg   = MathSqrt(var);
   if(sg <= 0.0) return;

   double ue = vwap + InpKEntry*sg;
   double le = vwap - InpKEntry*sg;

   if(c >= le && c <= ue)
     { g_armed_long=true; g_armed_short=true; return; }

   if(HasPosition()) return;

   // FADE a mercado. TP=VWAP, SL=VWAP+-k_stop*sigma (congelados).
   if(g_armed_short && c > ue)
     {
      g_armed_short=false;
      double sl=NormTick(vwap + InpKStop*sg), tpx=NormTick(vwap);
      if(!g_trade.Sell(InpLots, _Symbol, 0.0, sl, tpx, "cam_d2_exec"))
         PrintFormat("[CamD2Exec] Sell falhou ret=%d", g_trade.ResultRetcode());
     }
   else if(g_armed_long && c < le)
     {
      g_armed_long=false;
      double sl=NormTick(vwap - InpKStop*sg), tpx=NormTick(vwap);
      if(!g_trade.Buy(InpLots, _Symbol, 0.0, sl, tpx, "cam_d2_exec"))
         PrintFormat("[CamD2Exec] Buy falhou ret=%d", g_trade.ResultRetcode());
     }
  }

//+------------------------------------------------------------------+
bool HasPosition()
  {
   if(!PositionSelect(_Symbol)) return false;
   return (PositionGetInteger(POSITION_MAGIC) == InpMagic);
  }

double NormTick(double price)
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts <= 0.0) ts = _Point;
   return NormalizeDouble(MathRound(price/ts)*ts, _Digits);
  }

int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

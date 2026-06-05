//+------------------------------------------------------------------+
//| cam_d1_orb30_sinais.mq5                                          |
//| StrategyLab — D1 (ORB-30) — EXECUTOR com SINAIS embutidos.       |
//|                                                                   |
//| ADR-SL-04: executor "one shot one kill" — robo autossuficiente.  |
//| E o cam_d1_orb30_exec + o GATE DE REGIME (Efficiency Ratio diario)|
//| embutido e LIGADO por padrao: so opera quando o mercado esta em   |
//| TENDENCIA (ER alto); fica de fora em mercado LATERAL (ER baixo).  |
//| O cam_d1_orb30_exec (sem regime) permanece intacto.               |
//|                                                                   |
//| Opera a estrategia PURA a mercado (CTrade), DEMO-only. Na         |
//| allowlist do lint_mql5 (envia ordem).                             |
//|                                                                   |
//| Logica:                                                           |
//|   OR-30; quebra long se close>OR_high / short se <OR_low; FILTRO  |
//|   DE TENDENCIA (so a favor de N barras); FILTRO DE REGIME (ER     |
//|   diario >= min); entra A MERCADO; SL inicial + STOP MOVEL; TP    |
//|   fixo opcional; 1 disparo/direcao/dia; flat no fim da sessao.    |
//|                                                                   |
//| Regime: ER(N dias)=|close[1]-close[1+N]|/soma|variacao diaria|    |
//|   (PERIOD_D1). >= InpRegimeErMin => TENDENCIA (opera).            |
//|                                                                   |
//| SEC: guard-rail duplo DEMO (input + ACCOUNT_TRADE_MODE).          |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D1 ORB-30 — executor + regime ER embutido (DEMO-only)"

#include <Trade/Trade.mqh>

#define CAM_D1_SINAIS_VERSION "0.1.0"

//--- Estrategia (espelha D1Params) ----------------------------------
input int    InpOrMinutes        = 30;
input double InpStopPoints        = 700.0;  // SL inicial (pontos da entrada)
input double InpTargetPoints      = 0.0;    // TP fixo (pontos); 0 = sem TP
input double InpTrailPoints        = 800.0;  // stop movel (pontos atras do pico); 0=off
input int    InpTrendFilterBars   = 5000;   // so a favor da tendencia de N barras; 0=off
input double InpMinOrPoints        = 0.0;    // range minimo do OR; 0=off
input int    InpSessionOpenHour  = 9;
input int    InpSessionOpenMin   = 0;
input int    InpEntryUntilHour   = 17;
input int    InpEntryUntilMin    = 0;
input int    InpSessionCloseHour = 17;
input int    InpSessionCloseMin  = 55;
//--- GATE DE REGIME (Efficiency Ratio diario) — ligado por padrao ---
input bool   InpUseRegimeFilter   = true;   // so opera em tendencia
input int    InpRegimeErDays       = 10;     // janela do ER (dias)
input double InpRegimeErMin         = 0.35;   // ER >= isto => tendencia
//--- Execucao -------------------------------------------------------
input double InpLots             = 1.0;
input long   InpMagic            = 20260605;
input ulong  InpDeviationPoints  = 10;
input bool   InpShowPanel        = true;
input bool   InpRequireDemoAccount = true;

CTrade   g_trade;
string   g_session     = "";
double   g_or_high     = 0.0;
double   g_or_low      = 0.0;
bool     g_or_ready    = false;
bool     g_long_armed  = true;
bool     g_short_armed = true;
datetime g_last_bar    = 0;
double   g_max_favor   = 0.0;

// Serie diaria construida INTERNAMENTE a partir do M1 (nao depende de PERIOD_D1,
// que falha no Strategy Tester). Pre-seed do historico no OnInit p/ live.
#define CAM_DAILY_MAX 400
double   g_daily[CAM_DAILY_MAX];
int      g_daily_n     = 0;
string   g_last_daily  = "";       // data (YYYY-MM-DD) do ultimo close ja gravado
double   g_run_close   = 0.0;      // ultimo close da sessao corrente
bool     g_have_run    = false;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD1Sinais] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpDeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   SeedDaily();   // pre-seed da serie diaria (best-effort; tester completa ao vivo)
   PrintFormat("[CamD1Sinais] %s ativo. Symbol=%s regime=%s diarias_seed=%d.",
               CAM_D1_SINAIS_VERSION, _Symbol,
               (InpUseRegimeFilter ? "ON" : "OFF"), g_daily_n);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { if(InpShowPanel) Comment(""); }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar)
     {
      if(InpShowPanel) UpdatePanel();
      return;
     }
   g_last_bar = cur;
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iHigh(_Symbol,_Period,1), iLow(_Symbol,_Period,1),
              iClose(_Symbol,_Period,1));
   if(InpShowPanel) UpdatePanel();
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double h, double l, double c)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      // grava o close final da sessao que terminou na serie diaria interna.
      if(g_have_run && g_session != "") PushDaily(g_session, g_run_close);
      g_session = session;
      g_or_ready = false; g_long_armed = true; g_short_armed = true;
     }
   g_run_close = c; g_have_run = true;   // ultimo close da sessao corrente

   // stop movel a cada barra com posicao aberta.
   if(InpTrailPoints > 0 && HasPosition())
      ManageTrailing(h, l);

   int tod     = MinutesOfDay(t);
   int or_beg  = InpSessionOpenHour*60 + InpSessionOpenMin;
   int or_end  = or_beg + InpOrMinutes;
   int cut     = InpEntryUntilHour*60 + InpEntryUntilMin;
   int s_close = InpSessionCloseHour*60 + InpSessionCloseMin;

   // flat compulsorio no fim da sessao.
   if(tod >= s_close)
     {
      if(HasPosition()) g_trade.PositionClose(_Symbol);
      return;
     }

   // opening range.
   if(tod >= or_beg && tod < or_end)
     {
      if(!g_or_ready) { g_or_high=h; g_or_low=l; g_or_ready=true; }
      else { g_or_high=MathMax(g_or_high,h); g_or_low=MathMin(g_or_low,l); }
      return;
     }
   if(!g_or_ready) return;
   if(tod >= cut) return;

   double rng = g_or_high - g_or_low;
   if(rng <= 0.0) return;
   if(InpMinOrPoints > 0 && rng < InpMinOrPoints) return;
   if(HasPosition()) return;

   bool up   = TrendOk(c, +1);
   bool down = TrendOk(c, -1);
   bool regime_ok = (!InpUseRegimeFilter) || RegimeOk();

   bool static_exits = (InpStopPoints > 0);
   if(g_long_armed && c > g_or_high && up && regime_ok)
     {
      g_long_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_exits ? ref - InpStopPoints : g_or_low;
      double tp  = static_exits
                   ? (InpTargetPoints > 0 ? ref + InpTargetPoints : 0.0)
                   : g_or_high;
      if(g_trade.Buy(InpLots, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_sinais"))
         g_max_favor = ref;
      else
         PrintFormat("[CamD1Sinais] Buy falhou ret=%d", g_trade.ResultRetcode());
     }
   else if(g_short_armed && c < g_or_low && down && regime_ok)
     {
      g_short_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_exits ? ref + InpStopPoints : g_or_high;
      double tp  = static_exits
                   ? (InpTargetPoints > 0 ? ref - InpTargetPoints : 0.0)
                   : g_or_low;
      if(g_trade.Sell(InpLots, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_sinais"))
         g_max_favor = ref;
      else
         PrintFormat("[CamD1Sinais] Sell falhou ret=%d", g_trade.ResultRetcode());
     }
  }

//+------------------------------------------------------------------+
void ManageTrailing(double h, double l)
  {
   if(!PositionSelect(_Symbol)) return;
   if(PositionGetInteger(POSITION_MAGIC) != InpMagic) return;
   long type = PositionGetInteger(POSITION_TYPE);
   double cur_sl = PositionGetDouble(POSITION_SL);
   double cur_tp = PositionGetDouble(POSITION_TP);
   double new_sl = cur_sl;
   if(type == POSITION_TYPE_BUY)
     {
      g_max_favor = MathMax(g_max_favor, h);
      double cand = NormTick(g_max_favor - InpTrailPoints);
      if(cand > cur_sl) new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0) g_max_favor = l;
      g_max_favor = MathMin(g_max_favor, l);
      double cand = NormTick(g_max_favor + InpTrailPoints);
      if(cur_sl <= 0.0 || cand < cur_sl) new_sl = cand;
     }
   if(new_sl != cur_sl) g_trade.PositionModify(_Symbol, new_sl, cur_tp);
  }

//+------------------------------------------------------------------+
bool TrendOk(double c_now, int side)
  {
   int n = InpTrendFilterBars;
   if(n <= 0) return true;
   double ref = iClose(_Symbol, _Period, 1 + n);
   if(ref <= 0.0) return false;
   return (side>0) ? (c_now > ref) : (c_now < ref);
  }

//+------------------------------------------------------------------+
//| Regime: ER diario >= min => tendencia (opera). Espelha o Python.  |
//| ER calculado da serie diaria INTERNA (g_daily) — robusto no tester|
//| (nao depende de PERIOD_D1).                                       |
//+------------------------------------------------------------------+
bool RegimeOk() { double er = RegimeER(); return (er < 0.0) ? false : (er >= InpRegimeErMin); }

double RegimeER()
  {
   int n = InpRegimeErDays;
   if(n < 2 || g_daily_n < n + 1) return -1.0;
   double c0 = g_daily[g_daily_n - 1];        // close diario mais recente
   double cn = g_daily[g_daily_n - 1 - n];    // n dias antes
   double denom = 0.0;
   for(int i = g_daily_n - n; i <= g_daily_n - 1; i++)
      denom += MathAbs(g_daily[i] - g_daily[i - 1]);
   if(denom <= 0.0) return -1.0;
   return MathAbs(c0 - cn) / denom;
  }

//+------------------------------------------------------------------+
//| Append do close diario na serie interna (monotonico por data).   |
//+------------------------------------------------------------------+
void PushDaily(string d, double cl)
  {
   if(d <= g_last_daily) return;              // dedup / so avanca
   if(g_daily_n < CAM_DAILY_MAX)
      g_daily[g_daily_n++] = cl;
   else
     {
      for(int i = 1; i < CAM_DAILY_MAX; i++) g_daily[i - 1] = g_daily[i];
      g_daily[CAM_DAILY_MAX - 1] = cl;
     }
   g_last_daily = d;
  }

//+------------------------------------------------------------------+
//| Pre-seed da serie diaria com o historico (best-effort). No tester |
//| pode vir vazio/curto -> a serie completa-se com o fluxo M1.       |
//+------------------------------------------------------------------+
void SeedDaily()
  {
   double cl[]; datetime tm[];
   int got  = CopyClose(_Symbol, PERIOD_D1, 1, 120, cl);
   int gott = CopyTime(_Symbol, PERIOD_D1, 1, 120, tm);
   if(got <= 0 || gott != got) return;
   for(int i = 0; i < got; i++)            // 0=mais antigo .. got-1=mais recente
     {
      MqlDateTime s; TimeToStruct(tm[i], s);
      PushDaily(StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day), cl[i]);
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

void UpdatePanel()
  {
   double er = RegimeER();
   string regime = (er<0.0) ? "sem dados" :
                   (er >= InpRegimeErMin ? "TENDENCIA (opera)" : "LATERAL (de fora)");
   Comment(StringFormat(
      "CaM D1 ORB-30 — EXECUTOR + regime (DEMO)\n"
      "Sessao: %s   OR: %s / %s\n"
      "Tendencia(%d) | Regime ER%d=%.2f -> %s | Filtro: %s\n"
      "SL %.0f  trail %.0f  posicao: %s",
      g_session,
      g_or_ready ? DoubleToString(g_or_high,_Digits) : "-",
      g_or_ready ? DoubleToString(g_or_low,_Digits) : "-",
      InpTrendFilterBars, InpRegimeErDays, er, regime,
      (InpUseRegimeFilter ? "ON" : "OFF"),
      InpStopPoints, InpTrailPoints,
      (HasPosition() ? "ABERTA" : "flat")));
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//|  cam_hibrido_orb30_vwap.mq5                                       |
//|  CaM StrategyLab — EA HIBRIDO: ORB-30 (D1) + VWAP fade (D2)       |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  Robo executor que OPERA DUAS estrategias complementares e troca  |
//|  entre elas conforme o REGIME de mercado (medido por Efficiency   |
//|  Ratio diario):                                                   |
//|    - TENDENCIA (ER alto)  -> D1 "ORB-30": breakout do range de     |
//|      abertura a favor da tendencia, com stop movel (deixa correr).|
//|    - LATERAL  (ER baixo) -> D2 "VWAP fade": reversao a media —     |
//|      vende a esticada acima do VWAP, compra a esticada abaixo,     |
//|      alvo no VWAP (ganha do chop que mata o breakout).            |
//|  Assim o robo esta sempre na estrategia certa para o momento: a   |
//|  D1 ganha quando ha tendencia; a D2 ganha quando ha lateralizacao.|
//|                                                                   |
//|  =========================  COMO DECIDE  =======================  |
//|  Efficiency Ratio (N dias) = |close[1]-close[1+N]| / soma das     |
//|  variacoes diarias absolutas. ~1 = movimento direcional limpo;    |
//|  ~0 = vai e volta (lateral). ER >= InpRegimeErMin -> opera D1;     |
//|  abaixo -> opera D2. A serie diaria e montada internamente do M1  |
//|  (funciona no Strategy Tester, sem depender de PERIOD_D1).        |
//|                                                                   |
//|  Uma posicao por vez. SL/alvo da D1 com stop movel; SL/alvo da D2 |
//|  fixos no VWAP +- k*sigma. Flat no fim do pregao (sem overnight). |
//|                                                                   |
//|  =========================  ATENCAO  ===========================  |
//|  VALORES BRUTOS (sem custo/IR). SEM Risk Engine. Unica trava:     |
//|  guard-rail DEMO. Na allowlist do lint_mql5 (envia ordem).        |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "CaM Hibrido ORB-30 + VWAP fade — troca por regime (ER). DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_HIB_VERSION "0.1.0"
#define CAM_DAILY_MAX 400

//================== REGIME (a chave que troca D1 <-> D2) ============
input group "Regime (chave D1<->D2)"
input int    InpRegimeErDias        = 10;     // Janela do Efficiency Ratio (dias)
input double InpRegimeErMin         = 0.35;   // ER >= isto = TENDENCIA (opera D1); abaixo = LATERAL (opera D2)

//================== D1 — ORB-30 (regime de TENDENCIA) ==============
input group "D1 ORB-30 (tendencia)"
input int    InpOR_Minutos          = 30;     // Janela do range de abertura (minutos)
input double InpD1_StopInicial_Pts  = 700.0;  // D1: stop inicial, em pontos da entrada
input double InpD1_AlvoFixo_Pts     = 0.0;    // D1: alvo fixo em pontos (0 = sem alvo, deixa correr)
input double InpD1_StopMovel_Pts    = 800.0;  // D1: stop movel (trailing), pontos atras do pico (0 = off)
input int    InpD1_FiltroTend_Barras= 5000;   // D1: so a favor da tendencia das ultimas N barras (0 = off)

//================== D2 — VWAP fade (regime LATERAL) ================
input group "D2 VWAP fade (lateral)"
input double InpD2_KEntry           = 2.0;    // D2: fade na esticada de K x sigma do VWAP
input double InpD2_KStop            = 3.0;    // D2: stop alem de K_stop x sigma (alvo = VWAP)
input int    InpD2_WarmupBarras     = 30;     // D2: barras minimas na sessao p/ sigma confiavel

//================== SESSAO (horario do grafico) ====================
input group "Sessao (horario do grafico)"
input int    InpAbertura_Hora       = 9;      // Abertura do pregao — hora
input int    InpAbertura_Min        = 0;      // Abertura do pregao — minuto
input int    InpEntradaAte_Hora     = 17;     // Nao abre nova posicao apos esta hora
input int    InpEntradaAte_Min      = 0;      // Nao abre nova posicao apos este minuto
input int    InpFechamento_Hora     = 17;     // Zera posicao (flat) a partir desta hora
input int    InpFechamento_Min      = 55;     // Zera posicao (flat) a partir deste minuto

//================== EXECUCAO =======================================
input group "Execucao"
input double InpContratos           = 1.0;    // QUANTIDADE DE CONTRATOS por ordem (WIN/WDO: 1 = 1 contrato)
input long   InpMagicNumber         = 20260606;// Identificador do robo
input ulong  InpDesvioMax_Pts       = 10;     // Desvio maximo no preenchimento (pontos)
input bool   InpMostrarPainel       = true;   // Mostra painel de regime/estado no grafico

//================== SEGURANCA ======================================
input group "Seguranca"
input bool   InpExigirContaDemo     = true;   // So inicia em conta DEMO

CTrade   g_trade;
string   g_session     = "";
datetime g_last_bar    = 0;
int      g_pos_estrat  = 0;        // 0=flat, 1=posicao da D1, 2=posicao da D2

//--- D1 (ORB)
double   g_or_high=0.0, g_or_low=0.0;
bool     g_or_ready=false, g_d1_long_armed=true, g_d1_short_armed=true;
double   g_max_favor=0.0;

//--- D2 (VWAP)
double   g_sum_pv=0.0, g_sum_v=0.0, g_sum_pv2=0.0;
int      g_n=0;
bool     g_d2_long_armed=true, g_d2_short_armed=true;

//--- Regime: serie diaria interna (montada do M1) + pre-seed.
double   g_daily[CAM_DAILY_MAX];
int      g_daily_n=0;
string   g_last_daily="";
double   g_run_close=0.0;
bool     g_have_run=false;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpExigirContaDemo)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamHibrido] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpDesvioMax_Pts);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   SeedDaily();
   PrintFormat("[CamHibrido] %s ativo. Symbol=%s Contratos=%.2f diarias_seed=%d.",
               CAM_HIB_VERSION, _Symbol, InpContratos, g_daily_n);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { if(InpMostrarPainel) Comment(""); }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar) { if(InpMostrarPainel) UpdatePanel(); return; }
   g_last_bar = cur;
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iOpen(_Symbol,_Period,1), iHigh(_Symbol,_Period,1),
              iLow(_Symbol,_Period,1), iClose(_Symbol,_Period,1));
   if(InpMostrarPainel) UpdatePanel();
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double o, double h, double l, double c)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      if(g_have_run && g_session != "") PushDaily(g_session, g_run_close);
      g_session = session;
      g_or_ready=false; g_d1_long_armed=true; g_d1_short_armed=true;
      g_sum_pv=0.0; g_sum_v=0.0; g_sum_pv2=0.0; g_n=0;
      g_d2_long_armed=true; g_d2_short_armed=true;
     }
   g_run_close = c; g_have_run = true;

   // VWAP/sigma cumulativos da sessao (sempre — D2 precisa).
   double tp = (h + l + c) / 3.0;
   double v  = (double)iVolume(_Symbol, _Period, 1); if(v <= 0.0) v = 1.0;
   g_sum_pv += tp*v; g_sum_v += v; g_sum_pv2 += tp*tp*v; g_n++;

   // posicao fechou (SL/TP do broker)? libera a propriedade.
   if(g_pos_estrat != 0 && !HasPosition()) g_pos_estrat = 0;

   // stop movel da D1 (so se a posicao aberta for da D1).
   if(g_pos_estrat == 1 && InpD1_StopMovel_Pts > 0 && HasPosition())
      ManageTrailing(h, l);

   int tod     = MinutesOfDay(t);
   int or_beg  = InpAbertura_Hora*60 + InpAbertura_Min;
   int or_end  = or_beg + InpOR_Minutos;
   int cut     = InpEntradaAte_Hora*60 + InpEntradaAte_Min;
   int s_close = InpFechamento_Hora*60 + InpFechamento_Min;

   // flat compulsorio no fim da sessao.
   if(tod >= s_close)
     {
      if(HasPosition()) { g_trade.PositionClose(_Symbol); g_pos_estrat = 0; }
      return;
     }

   // range de abertura (sem entradas durante a abertura).
   if(tod >= or_beg && tod < or_end)
     {
      if(!g_or_ready) { g_or_high=h; g_or_low=l; g_or_ready=true; }
      else { g_or_high=MathMax(g_or_high,h); g_or_low=MathMin(g_or_low,l); }
      return;
     }
   if(tod >= cut) return;
   if(HasPosition()) return;          // uma posicao por vez

   // REGIME decide a estrategia. Sem dado de regime ainda -> fica de fora.
   double er = RegimeER();
   if(er < 0.0) return;
   if(er >= InpRegimeErMin) TryD1(c);     // tendencia
   else                     TryD2(c);     // lateral
  }

//+------------------------------------------------------------------+
//| D1 ORB-30 — entra na quebra a favor da tendencia (regime trend).  |
//+------------------------------------------------------------------+
void TryD1(double c)
  {
   if(!g_or_ready) return;
   double rng = g_or_high - g_or_low;
   if(rng <= 0.0) return;
   bool up   = TrendOk(c, +1);
   bool down = TrendOk(c, -1);
   bool static_exits = (InpD1_StopInicial_Pts > 0);

   if(g_d1_long_armed && c > g_or_high && up)
     {
      g_d1_long_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_exits ? ref - InpD1_StopInicial_Pts : g_or_low;
      double tp  = static_exits ? (InpD1_AlvoFixo_Pts > 0 ? ref + InpD1_AlvoFixo_Pts : 0.0)
                                : g_or_high;
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hib_d1"))
        { g_max_favor = ref; g_pos_estrat = 1; }
     }
   else if(g_d1_short_armed && c < g_or_low && down)
     {
      g_d1_short_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_exits ? ref + InpD1_StopInicial_Pts : g_or_high;
      double tp  = static_exits ? (InpD1_AlvoFixo_Pts > 0 ? ref - InpD1_AlvoFixo_Pts : 0.0)
                                : g_or_low;
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hib_d1"))
        { g_max_favor = ref; g_pos_estrat = 1; }
     }
  }

//+------------------------------------------------------------------+
//| D2 VWAP fade — fade da esticada de +-K*sigma (regime lateral).    |
//+------------------------------------------------------------------+
void TryD2(double c)
  {
   if(g_n < InpD2_WarmupBarras || g_sum_v <= 0.0) return;
   double vwap = g_sum_pv/g_sum_v;
   double var  = MathMax(0.0, g_sum_pv2/g_sum_v - vwap*vwap);
   double sg   = MathSqrt(var);
   if(sg <= 0.0) return;
   double ue = vwap + InpD2_KEntry*sg;
   double le = vwap - InpD2_KEntry*sg;

   if(c >= le && c <= ue) { g_d2_long_armed=true; g_d2_short_armed=true; return; }

   if(g_d2_short_armed && c > ue)   // esticou pra cima -> vende, alvo no VWAP
     {
      g_d2_short_armed=false;
      double sl=NormTick(vwap + InpD2_KStop*sg), tpx=NormTick(vwap);
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, sl, tpx, "cam_hib_d2"))
         g_pos_estrat = 2;
     }
   else if(g_d2_long_armed && c < le) // esticou pra baixo -> compra
     {
      g_d2_long_armed=false;
      double sl=NormTick(vwap - InpD2_KStop*sg), tpx=NormTick(vwap);
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, sl, tpx, "cam_hib_d2"))
         g_pos_estrat = 2;
     }
  }

//+------------------------------------------------------------------+
void ManageTrailing(double h, double l)
  {
   if(!PositionSelect(_Symbol)) return;
   if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) return;
   long type = PositionGetInteger(POSITION_TYPE);
   double cur_sl = PositionGetDouble(POSITION_SL);
   double cur_tp = PositionGetDouble(POSITION_TP);
   double new_sl = cur_sl;
   if(type == POSITION_TYPE_BUY)
     {
      g_max_favor = MathMax(g_max_favor, h);
      double cand = NormTick(g_max_favor - InpD1_StopMovel_Pts);
      if(cand > cur_sl) new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0) g_max_favor = l;
      g_max_favor = MathMin(g_max_favor, l);
      double cand = NormTick(g_max_favor + InpD1_StopMovel_Pts);
      if(cur_sl <= 0.0 || cand < cur_sl) new_sl = cand;
     }
   if(new_sl != cur_sl) g_trade.PositionModify(_Symbol, new_sl, cur_tp);
  }

//+------------------------------------------------------------------+
bool TrendOk(double c_now, int side)
  {
   int n = InpD1_FiltroTend_Barras;
   if(n <= 0) return true;
   double ref = iClose(_Symbol, _Period, 1 + n);
   if(ref <= 0.0) return false;
   return (side>0) ? (c_now > ref) : (c_now < ref);
  }

//+------------------------------------------------------------------+
//| Regime: Efficiency Ratio da serie diaria interna (g_daily).       |
//+------------------------------------------------------------------+
double RegimeER()
  {
   int n = InpRegimeErDias;
   if(n < 2 || g_daily_n < n + 1) return -1.0;
   double c0 = g_daily[g_daily_n - 1];
   double cn = g_daily[g_daily_n - 1 - n];
   double denom = 0.0;
   for(int i = g_daily_n - n; i <= g_daily_n - 1; i++)
      denom += MathAbs(g_daily[i] - g_daily[i - 1]);
   if(denom <= 0.0) return -1.0;
   return MathAbs(c0 - cn) / denom;
  }

void PushDaily(string d, double cl)
  {
   if(d <= g_last_daily) return;
   if(g_daily_n < CAM_DAILY_MAX) g_daily[g_daily_n++] = cl;
   else { for(int i=1;i<CAM_DAILY_MAX;i++) g_daily[i-1]=g_daily[i]; g_daily[CAM_DAILY_MAX-1]=cl; }
   g_last_daily = d;
  }

void SeedDaily()
  {
   double cl[]; datetime tm[];
   int got  = CopyClose(_Symbol, PERIOD_D1, 1, 120, cl);
   int gott = CopyTime(_Symbol, PERIOD_D1, 1, 120, tm);
   if(got <= 0 || gott != got) return;
   for(int i = 0; i < got; i++)
     {
      MqlDateTime s; TimeToStruct(tm[i], s);
      PushDaily(StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day), cl[i]);
     }
  }

//+------------------------------------------------------------------+
double NormTick(double price)
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts <= 0.0) ts = _Point;
   return NormalizeDouble(MathRound(price/ts)*ts, _Digits);
  }

bool HasPosition()
  {
   if(!PositionSelect(_Symbol)) return false;
   return (PositionGetInteger(POSITION_MAGIC) == InpMagicNumber);
  }

void UpdatePanel()
  {
   double er = RegimeER();
   string reg = (er<0.0) ? "aquecendo (sem regime)"
              : (er >= InpRegimeErMin ? "TENDENCIA -> D1 (ORB)" : "LATERAL -> D2 (VWAP fade)");
   string pos = (g_pos_estrat==1) ? "D1 aberta" : (g_pos_estrat==2 ? "D2 aberta" : "flat");
   Comment(StringFormat(
      "CaM HIBRIDO ORB-30 + VWAP (DEMO)\n"
      "Sessao: %s   Regime ER%d=%.2f (min %.2f)\n"
      "Ativo agora: %s\n"
      "OR: %s / %s   Posicao: %s   Contratos: %.0f",
      g_session, InpRegimeErDias, er, InpRegimeErMin, reg,
      g_or_ready ? DoubleToString(g_or_high,_Digits) : "-",
      g_or_ready ? DoubleToString(g_or_low,_Digits) : "-",
      pos, InpContratos));
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

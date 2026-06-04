//+------------------------------------------------------------------+
//| cam_d1_orb30_exec.mq5                                             |
//| StrategyLab — D1 (ORB-30) — EA EXECUTOR (opera de verdade).      |
//|                                                                   |
//| ADR-SL-04: modelo de DOIS EAs para a mesma estrategia D1:         |
//|   - cam_d1_orb30.mq5      -> GRAVADOR de paridade (sem ordem).    |
//|   - cam_d1_orb30_exec.mq5 -> EXECUTOR (este): envia ordens de     |
//|     mercado com SL/TP, para ver a estrategia OPERANDO no Strategy |
//|     Tester (aba Negociacoes preenchida).                          |
//|                                                                   |
//| ESCOPO (decisao do Founder): executa a estrategia PURA. Ainda NAO |
//| verifica risco (sem Risk Engine / Assets RiskManager) — isso vem  |
//| depois. A unica trava ativa e o guard-rail DEMO.                  |
//|                                                                   |
//| Logica D1 (mesma de d1_orb30.py):                                 |
//|   1. Opening Range = [high,low] dos primeiros InpOrMinutes do     |
//|      pregao.                                                       |
//|   2. Na QUEBRA (close > OR_high -> compra; close < OR_low ->       |
//|      vende), entra A MERCADO no inicio da barra seguinte.          |
//|   3. SL no extremo oposto do range; TP = InpTargetR x range —      |
//|      geridos pela corretora/tester (saida intrabar realista).      |
//|   4. Um disparo por direcao por dia; flat no fim da sessao.        |
//|                                                                   |
//| SEC (Kevin): este EA ENVIA ORDEM. Guard-rail duplo DEMO —          |
//|   InpRequireDemoAccount + checagem em runtime de                  |
//|   ACCOUNT_TRADE_MODE. Recusa init se a conta nao for DEMO. Esta    |
//|   na allowlist do lint_mql5 (junto de cam_risk_mirror).            |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D1 ORB-30 — EXECUTOR (opera a estrategia; DEMO-only)"

#include <Trade/Trade.mqh>

#define CAM_D1_EXEC_VERSION "0.1.0-onda1"

//--- Parametros da estrategia (espelham D1Params do Python) ---------
input int    InpOrMinutes        = 30;     // janela do opening range (min)
// SL/TP ESTATICOS em pontos, relativos ao preco de entrada (R-15b). Ativos
// quando ambos > 0 (prioridade sobre o modo range/InpTargetR).
input double InpStopPoints        = 200.0; // SL estatico (pontos da entrada)
input double InpTargetPoints      = 400.0; // TP estatico (pontos da entrada)
input double InpTargetR          = 1.0;    // modo range (fallback): TP = R x range
input int    InpSessionOpenHour  = 9;      // abertura do pregao (hora)
input int    InpSessionOpenMin   = 0;
input int    InpEntryUntilHour   = 17;     // nao abre nova posicao apos esta hora
input int    InpEntryUntilMin    = 0;
input int    InpSessionCloseHour = 17;     // flat compulsorio (hora)
input int    InpSessionCloseMin  = 55;
//--- Execucao -------------------------------------------------------
input double InpLots             = 1.0;    // volume por ordem
input long   InpMagic            = 20260603;
input ulong  InpDeviationPoints  = 10;     // desvio maximo no preenchimento
//--- Seguranca (guard-rail duplo DEMO) ------------------------------
input bool   InpRequireDemoAccount = true;

CTrade   g_trade;

//--- Estado da maquina (espelha generate_signals) -------------------
string   g_session     = "";
double   g_or_high     = 0.0;
double   g_or_low      = 0.0;
bool     g_or_ready    = false;
bool     g_long_armed  = true;
bool     g_short_armed = true;
datetime g_last_bar    = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   // SEC — guard-rail DEMO (este EA envia ordem; recusa fora de DEMO).
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD1Exec] ABORTANDO: conta nao e DEMO (mode=%d). "
                     "Executor so opera em DEMO.", mode);
         return(INIT_FAILED);
        }
     }

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpDeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("[CamD1Exec] %s ativo. Symbol=%s TF=%s Lots=%.2f Magic=%d.",
               CAM_D1_EXEC_VERSION, _Symbol,
               EnumToString((ENUM_TIMEFRAMES)_Period), InpLots, InpMagic);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
//| OnTick — processa no fechamento de cada barra (nova barra). A     |
//| barra recem-completada e a de shift 1 (espelha "barra i" Python). |
//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar)
      return;
   g_last_bar = cur;

   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0)
      return;
   double h = iHigh(_Symbol, _Period, 1);
   double l = iLow(_Symbol, _Period, 1);
   double c = iClose(_Symbol, _Period, 1);

   ProcessBar(t, h, l, c);
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double h, double l, double c)
  {
   string session = SessionDate(t);

   // novo pregao -> reseta estado (espelha generate_signals).
   if(session != g_session)
     {
      g_session     = session;
      g_or_ready    = false;
      g_long_armed  = true;
      g_short_armed = true;
     }

   int tod     = MinutesOfDay(t);
   int or_beg  = InpSessionOpenHour * 60 + InpSessionOpenMin;
   int or_end  = or_beg + InpOrMinutes;
   int cut     = InpEntryUntilHour * 60 + InpEntryUntilMin;
   int s_close = InpSessionCloseHour * 60 + InpSessionCloseMin;

   // flat compulsorio no fim da sessao (sem overnight) — antes de tudo.
   if(tod >= s_close)
     {
      if(HasPosition())
         g_trade.PositionClose(_Symbol);
      return;
     }

   // 1) construcao do opening range (primeiros InpOrMinutes do pregao).
   if(tod >= or_beg && tod < or_end)
     {
      if(!g_or_ready)
        {
         g_or_high = h;  g_or_low = l;  g_or_ready = true;
        }
      else
        {
         g_or_high = MathMax(g_or_high, h);
         g_or_low  = MathMin(g_or_low, l);
        }
      return;
     }

   if(!g_or_ready)
      return;

   // 2) janela de entrada (apos o range, antes do corte).
   if(tod >= cut)
      return;

   double rng = g_or_high - g_or_low;
   if(rng <= 0.0)
      return;

   // 3) uma posicao por vez (single-symbol).
   if(HasPosition())
      return;

   // 4) gatilhos na quebra — entra A MERCADO; SL/TP geridos pelo tester.
   //    SL/TP estaticos relativos ao preco de fill (Ask na compra, Bid na venda);
   //    fallback para os niveis do range quando os pontos nao estao setados.
   bool   static_exits = (InpStopPoints > 0 && InpTargetPoints > 0);
   if(g_long_armed && c > g_or_high)
     {
      g_long_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_exits ? ref - InpStopPoints : g_or_low;
      double tp  = static_exits ? ref + InpTargetPoints : g_or_high + InpTargetR * rng;
      if(!g_trade.Buy(InpLots, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_exec"))
         PrintFormat("[CamD1Exec] Buy falhou ret=%d", g_trade.ResultRetcode());
     }
   else if(g_short_armed && c < g_or_low)
     {
      g_short_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_exits ? ref + InpStopPoints : g_or_high;
      double tp  = static_exits ? ref - InpTargetPoints : g_or_low - InpTargetR * rng;
      if(!g_trade.Sell(InpLots, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_exec"))
         PrintFormat("[CamD1Exec] Sell falhou ret=%d", g_trade.ResultRetcode());
     }
  }

//+------------------------------------------------------------------+
//| Normaliza um preco ao tick size do simbolo (ex.: WIN = 5).        |
//+------------------------------------------------------------------+
double NormTick(double price)
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts <= 0.0)
      ts = _Point;
   return NormalizeDouble(MathRound(price / ts) * ts, _Digits);
  }

//+------------------------------------------------------------------+
//| Ha posicao deste EA neste simbolo? (magic + symbol)               |
//+------------------------------------------------------------------+
bool HasPosition()
  {
   if(!PositionSelect(_Symbol))
      return false;
   return (PositionGetInteger(POSITION_MAGIC) == InpMagic);
  }

//+------------------------------------------------------------------+
//| Helpers de tempo.                                                 |
//+------------------------------------------------------------------+
int MinutesOfDay(datetime t)
  {
   MqlDateTime st;
   TimeToStruct(t, st);
   return st.hour * 60 + st.min;
  }

string SessionDate(datetime t)
  {
   MqlDateTime st;
   TimeToStruct(t, st);
   return StringFormat("%04d-%02d-%02d", st.year, st.mon, st.day);
  }
//+------------------------------------------------------------------+

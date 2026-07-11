//+------------------------------------------------------------------+
//|  cam_hibrido_orb30_vwap.mq5                                       |
//|  CaM StrategyLab — EA HIBRIDO: ORB-30 (D1) + VWAP fade (D2)       |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  Robo executor com logica de RECUPERACAO sequencial (nao e mais   |
//|  switch por regime):                                              |
//|    1) D1 "ORB-30" opera SO DE MANHA (abertura ate InpD1_EntradaAte,|
//|       default 11:00). Breakout do range de abertura a favor da    |
//|       tendencia, com stop movel (deixa correr).                   |
//|    2) D2 "VWAP fade" SO ENTRA SE A D1 FECHOU NO PREJUIZO no dia    |
//|       (recuperacao). Reversao a media: fade da esticada de +-k*sg |
//|       do VWAP, com stop/alvo/trailing em pontos. Se a D1 nao       |
//|       perdeu, o dia termina apos a janela da D1 (sem D2).          |
//|                                                                   |
//|  IMPORTANTE: recuperacao = TROCAR de estrategia (D1->D2), NUNCA    |
//|  aumentar volume apos perda (sem martingale). Mesmo lote sempre.   |
//|                                                                   |
//|  Uma posicao por vez. Flat no fim do pregao (sem overnight).      |
//|                                                                   |
//|  =========================  ATENCAO  ===========================  |
//|  VALORES BRUTOS (sem custo/IR). SEM Risk Engine. Unica trava:     |
//|  guard-rail DEMO. Na allowlist do lint_mql5 (envia ordem).        |
//|                                                                   |
//|  Defaults = config do Founder otimizada p/ o hibrido:            |
//|    D1: OR 10min / stop 700 / alvo 1600 / trail 900 / ate 11:00.   |
//|    D2: fade 1sg / stop 400 / alvo 1600 / trail 900 / warmup 124.  |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.2"
#property strict
#property description "CaM Hibrido ORB-30 (manha) + VWAP fade (recuperacao apos loss da D1). DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_HIB_VERSION "0.2.0"

//================== D1 — ORB-30 (manha, ate 11:00) ================
input group "D1 ORB-30 (manha)"
input int    InpOR_Minutos          = 10;     // Janela do range de abertura (minutos)
input int    InpD1_EntradaAte_Hora  = 11;     // D1 nao abre nova posicao apos esta hora
input int    InpD1_EntradaAte_Min   = 0;      // D1 nao abre nova posicao apos este minuto
input double InpD1_StopInicial_Pts  = 700.0;  // D1: stop inicial, em pontos da entrada
input double InpD1_AlvoFixo_Pts     = 1600.0; // D1: alvo fixo em pontos (0 = sem alvo, deixa correr)
input double InpD1_StopMovel_Pts    = 900.0;  // D1: stop movel (trailing), pontos atras do pico (0 = off)
input int    InpD1_FiltroTend_Barras= 0;      // D1: so a favor da tendencia das ultimas N barras (0 = off)

//================== D2 — VWAP fade (recuperacao apos loss) =========
input group "D2 VWAP fade (recuperacao)"
input double InpD2_KEntry           = 1.0;    // D2: fade na esticada de K x sigma do VWAP
input double InpD2_KStop            = 30.0;   // D2: stop na banda K_stop x sigma (inocuo se StopInicial>0)
input int    InpD2_WarmupBarras     = 124;    // D2: barras minimas na sessao p/ sigma confiavel
input double InpD2_StopInicial_Pts  = 400.0;  // D2: stop estatico em pontos (0 = banda sigma)
input double InpD2_AlvoFixo_Pts     = 1600.0; // D2: alvo fixo em pontos (0 = alvo no VWAP)
input double InpD2_StopMovel_Pts    = 900.0;  // D2: stop movel (trailing) em pontos (0 = off)

//================== SESSAO (horario do grafico) ====================
input group "Sessao (horario do grafico)"
input int    InpAbertura_Hora       = 9;      // Abertura do pregao — hora
input int    InpAbertura_Min        = 0;      // Abertura do pregao — minuto
input int    InpEntradaAte_Hora     = 17;     // Corte GLOBAL: nao abre nova posicao apos esta hora
input int    InpEntradaAte_Min      = 0;      // Corte global — minuto
input int    InpFechamento_Hora     = 17;     // Zera posicao (flat) a partir desta hora
input int    InpFechamento_Min      = 55;     // Zera posicao (flat) a partir deste minuto

//================== EXECUCAO =======================================
input group "Execucao"
input double InpContratos           = 1.0;    // QUANTIDADE DE CONTRATOS por ordem (WIN/WDO: 1 = 1 contrato)
input long   InpMagicNumber         = 20260606;// Identificador do robo
input ulong  InpDesvioMax_Pts       = 10;     // Desvio maximo no preenchimento (pontos)
input bool   InpMostrarPainel       = true;   // Mostra painel de estado no grafico

//================== SEGURANCA ======================================
input group "Seguranca"
input bool   InpExigirContaDemo     = true;   // So inicia em conta DEMO

CTrade   g_trade;
string   g_session     = "";
datetime g_last_bar    = 0;
datetime g_day_start   = 0;        // inicio do pregao (p/ varrer historico do dia)
int      g_pos_estrat  = 0;        // 0=flat, 1=posicao da D1, 2=posicao da D2
bool     g_d1_loss_today = false;  // a D1 fechou no prejuizo hoje? -> libera a D2

//--- D1 (ORB)
double   g_or_high=0.0, g_or_low=0.0;
bool     g_or_ready=false, g_d1_long_armed=true, g_d1_short_armed=true;
double   g_max_favor=0.0;

//--- D2 (VWAP)
double   g_sum_pv=0.0, g_sum_v=0.0, g_sum_pv2=0.0;
int      g_n=0;
bool     g_d2_long_armed=true, g_d2_short_armed=true;

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
   PrintFormat("[CamHibrido] %s ativo. Symbol=%s Contratos=%.2f. D1 ate %02d:%02d; "
               "D2 so apos loss da D1.", CAM_HIB_VERSION, _Symbol, InpContratos,
               InpD1_EntradaAte_Hora, InpD1_EntradaAte_Min);
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
      g_session = session;
      g_day_start = t;
      g_or_ready=false; g_d1_long_armed=true; g_d1_short_armed=true;
      g_sum_pv=0.0; g_sum_v=0.0; g_sum_pv2=0.0; g_n=0;
      g_d2_long_armed=true; g_d2_short_armed=true;
      g_d1_loss_today=false;
     }

   // VWAP/sigma cumulativos da sessao (sempre — a D2 precisa quando for chamada).
   double tp = (h + l + c) / 3.0;
   double v  = (double)iVolume(_Symbol, _Period, 1); if(v <= 0.0) v = 1.0;
   g_sum_pv += tp*v; g_sum_v += v; g_sum_pv2 += tp*tp*v; g_n++;

   // posicao fechou? Se era da D1 e fechou no prejuizo, LIBERA a D2 (recuperacao).
   if(g_pos_estrat != 0 && !HasPosition())
     {
      if(g_pos_estrat == 1 && LastClosedProfit() < 0.0)
         g_d1_loss_today = true;
      g_pos_estrat = 0;
     }

   // stop movel da posicao aberta (distancia conforme a estrategia dona).
   double trail = (g_pos_estrat == 2) ? InpD2_StopMovel_Pts : InpD1_StopMovel_Pts;
   if(g_pos_estrat != 0 && trail > 0 && HasPosition())
      ManageTrailing(h, l, trail);

   int tod     = MinutesOfDay(t);
   int or_beg  = InpAbertura_Hora*60 + InpAbertura_Min;
   int or_end  = or_beg + InpOR_Minutos;
   int d1_cut  = InpD1_EntradaAte_Hora*60 + InpD1_EntradaAte_Min;
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
   if(tod >= cut) return;             // corte global de novas entradas
   if(HasPosition()) return;          // uma posicao por vez

   // DECISAO: D1 so de manha (ate d1_cut); D2 so DEPOIS e SE a D1 perdeu hoje.
   if(tod < d1_cut)
      TryD1(c);                       // janela da D1 (manha)
   else if(g_d1_loss_today)
      TryD2(c);                       // recuperacao: D2 apos loss da D1
  }

//+------------------------------------------------------------------+
//| D1 ORB-30 — entra na quebra a favor da tendencia (so de manha).   |
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
//| D2 VWAP fade — fade da esticada (recuperacao). Saidas em pontos.  |
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

   bool static_stop = (InpD2_StopInicial_Pts > 0);
   bool fixed_tp    = (InpD2_AlvoFixo_Pts > 0);

   if(g_d2_short_armed && c > ue)   // esticou pra cima -> vende (fade)
     {
      g_d2_short_armed=false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_stop ? ref + InpD2_StopInicial_Pts : vwap + InpD2_KStop*sg;
      double tpx = fixed_tp    ? ref - InpD2_AlvoFixo_Pts    : vwap;
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tpx), "cam_hib_d2"))
        { g_max_favor = ref; g_pos_estrat = 2; }
     }
   else if(g_d2_long_armed && c < le) // esticou pra baixo -> compra (fade)
     {
      g_d2_long_armed=false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_stop ? ref - InpD2_StopInicial_Pts : vwap - InpD2_KStop*sg;
      double tpx = fixed_tp    ? ref + InpD2_AlvoFixo_Pts    : vwap;
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tpx), "cam_hib_d2"))
        { g_max_favor = ref; g_pos_estrat = 2; }
     }
  }

//+------------------------------------------------------------------+
//| Stop movel: segue o pico a `trail` pontos; o SL so anda a favor.  |
//+------------------------------------------------------------------+
void ManageTrailing(double h, double l, double trail)
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
      double cand = NormTick(g_max_favor - trail);
      if(cand > cur_sl) new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0) g_max_favor = l;
      g_max_favor = MathMin(g_max_favor, l);
      double cand = NormTick(g_max_favor + trail);
      if(cur_sl <= 0.0 || cand < cur_sl) new_sl = cand;
     }
   if(new_sl != cur_sl) g_trade.PositionModify(_Symbol, new_sl, cur_tp);
  }

//+------------------------------------------------------------------+
//| Lucro do ULTIMO fechamento (deal OUT) deste robo no dia. <0=loss. |
//+------------------------------------------------------------------+
double LastClosedProfit()
  {
   if(!HistorySelect(g_day_start, TimeCurrent() + 60)) return 0.0;
   int total = HistoryDealsTotal();
   for(int i = total - 1; i >= 0; i--)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0) continue;
      if(HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber) continue;
      if(HistoryDealGetInteger(ticket, DEAL_ENTRY) != DEAL_ENTRY_OUT) continue;
      return HistoryDealGetDouble(ticket, DEAL_PROFIT);
     }
   return 0.0;
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
   int tod = MinutesOfDay(iTime(_Symbol,_Period,1));
   int d1_cut = InpD1_EntradaAte_Hora*60 + InpD1_EntradaAte_Min;
   string fase;
   if(tod < d1_cut)                 fase = "D1 (ORB) — janela da manha";
   else if(g_d1_loss_today)         fase = "D2 (VWAP) — RECUPERACAO (D1 perdeu)";
   else                             fase = "encerrado (D1 nao perdeu / fora de janela)";
   string pos = (g_pos_estrat==1) ? "D1 aberta" : (g_pos_estrat==2 ? "D2 aberta" : "flat");
   Comment(StringFormat(
      "CaM HIBRIDO ORB-30 + VWAP (DEMO)\n"
      "Sessao: %s\n"
      "Fase: %s\n"
      "D1 perdeu hoje? %s   Posicao: %s   Contratos: %.0f",
      g_session, fase, (g_d1_loss_today ? "SIM" : "nao"), pos, InpContratos));
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

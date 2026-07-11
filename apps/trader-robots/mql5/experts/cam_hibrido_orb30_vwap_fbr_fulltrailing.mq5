//+------------------------------------------------------------------+
//|  cam_hibrido_orb30_vwap_fbr_fulltrailing.mq5                      |
//|  CaM StrategyLab — HIBRIDO 3 pernas + STOP HIBRIDO TICK-A-TICK    |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  Igual ao cam_hibrido_orb30_vwap_fbr (D1 ORB + D3 FBR de manha;   |
//|  D2 VWAP fade de recuperacao apos loss da D1), MAS com a saida    |
//|  reescrita como STOP HIBRIDO "FULL TRAILING":                     |
//|                                                                   |
//|    1) STOP ESTATICO (piso): no fill, SL = entrada -+ StopInicial. |
//|       E a protecao de catastrofe; nunca afrouxa.                  |
//|    2) STOP MOVEL CONTINUO: a CADA TICK (nao so no fechamento da    |
//|       barra), o stop persegue o preco mantendo-se a X pts do pico  |
//|       favoravel (Bid p/ compra, Ask p/ venda). So anda a favor.   |
//|       Quando ultrapassa o piso estatico, ele assume = trava lucro. |
//|    3) REALIZA em X: alvo fixo (TP) em pontos; 0 = deixa o trailing |
//|       conduzir ate o fim.                                          |
//|    4) (opcional) o trailing so ATIVA apos +N pts de lucro          |
//|       (InpTrail_AtivaApos_Pts) — evita ser raspado no ruido.      |
//|                                                                   |
//|  Motivacao: em janelas curtas a saida por barra devolvia muito do |
//|  topo do movimento. O trailing tick-a-tick e mais ORGANICO: trava |
//|  o lucro mais cedo e cede menos no recuo.                          |
//|                                                                   |
//|  >>> TESTE em "Every tick"/"Every tick based on real ticks" no    |
//|      Strategy Tester — em "1 minute OHLC" o trailing fica grosso  |
//|      (so 4 pontos por barra) e NAO reflete o comportamento real.  |
//|                                                                   |
//|  Uma posicao por vez. Sem martingale. Flat no fim do pregao.      |
//|  VALORES BRUTOS. SEM Risk Engine. Guard-rail DEMO. Allowlist lint.|
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "CaM Hibrido ORB+FBR+VWAP com STOP HIBRIDO full trailing (tick a tick). DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_HIBFT_VERSION "0.1.0"

//================== D1 — ORB-30 (manha, ate 11:00) ================
input group "D1 ORB-30 (manha)"
input int    InpOR_Minutos          = 10;     // Janela do range de abertura (min) — compartilhada D1/D3
input int    InpD1_EntradaAte_Hora  = 11;     // D1 e D3 nao abrem nova posicao apos esta hora
input int    InpD1_EntradaAte_Min   = 0;      // ... e este minuto
input double InpD1_StopInicial_Pts  = 700.0;  // D1: STOP ESTATICO (piso), em pontos da entrada
input double InpD1_AlvoFixo_Pts     = 1600.0; // D1: realiza (TP) em pontos (0 = sem alvo, so trailing)
input double InpD1_StopMovel_Pts    = 900.0;  // D1: TRAILING continuo (X pts do preco); 0 = off
input int    InpD1_FiltroTend_Barras= 0;      // D1: so a favor da tendencia das ultimas N barras (0 = off)

//================== D3 — Failed Breakout Reversal (manha) ==========
input group "D3 FBR (rompimento falso — manha)"
input double InpD3_BufferPts        = 400.0;  // D3: rompimento so conta se esticar > N pts do range
input double InpD3_StopInicial_Pts  = 700.0;  // D3: STOP ESTATICO (piso) em pontos da entrada
input double InpD3_AlvoFixo_Pts     = 1600.0; // D3: realiza (TP) em pontos (0 = sem alvo)
input double InpD3_StopMovel_Pts    = 900.0;  // D3: TRAILING continuo (X pts do preco); 0 = off

//================== D2 — VWAP fade (recuperacao apos loss) =========
input group "D2 VWAP fade (recuperacao)"
input double InpD2_KEntry           = 1.0;    // D2: fade na esticada de K x sigma do VWAP
input double InpD2_KStop            = 30.0;   // D2: stop na banda K_stop x sigma (inocuo se StopInicial>0)
input int    InpD2_WarmupBarras     = 124;    // D2: barras minimas na sessao p/ sigma confiavel
input double InpD2_StopInicial_Pts  = 400.0;  // D2: STOP ESTATICO (piso) em pontos (0 = banda sigma)
input double InpD2_AlvoFixo_Pts     = 1600.0; // D2: realiza (TP) em pontos (0 = alvo no VWAP)
input double InpD2_StopMovel_Pts    = 900.0;  // D2: TRAILING continuo (X pts do preco); 0 = off

//================== STOP HIBRIDO (full trailing) ==================
input group "Stop hibrido (full trailing)"
input double InpTrail_AtivaApos_Pts = 0.0;    // Trailing so ATIVA apos +N pts de lucro (0 = imediato)

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
input long   InpMagicNumber         = 20260608;// Identificador do robo
input ulong  InpDesvioMax_Pts       = 10;     // Desvio maximo no preenchimento (pontos)
input bool   InpMostrarPainel       = true;   // Mostra painel de estado no grafico

//================== SEGURANCA ======================================
input group "Seguranca"
input bool   InpExigirContaDemo     = true;   // So inicia em conta DEMO

CTrade   g_trade;
string   g_session     = "";
datetime g_last_bar    = 0;
datetime g_day_start   = 0;        // inicio do pregao (p/ varrer historico do dia)
int      g_pos_estrat  = 0;        // 0=flat, 1=D1, 2=D2, 3=D3
bool     g_d1_loss_today = false;  // a D1 fechou no prejuizo hoje? -> libera a D2

//--- D1/D3 compartilham o range de abertura
double   g_or_high=0.0, g_or_low=0.0;
bool     g_or_ready=false, g_d1_long_armed=true, g_d1_short_armed=true;
double   g_max_favor=0.0;          // pico favoravel (preco) desde a entrada

//--- D3 (failed breakout reversal)
bool     g_d3_broke_up=false, g_d3_broke_dn=false;
bool     g_d3_fired_short=false, g_d3_fired_long=false;

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
         PrintFormat("[CamHibFT] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpDesvioMax_Pts);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   PrintFormat("[CamHibFT] %s ativo. Symbol=%s Contratos=%.2f. Full trailing tick-a-tick. "
               "D1+D3 ate %02d:%02d; D2 so apos loss da D1.", CAM_HIBFT_VERSION, _Symbol,
               InpContratos, InpD1_EntradaAte_Hora, InpD1_EntradaAte_Min);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { if(InpMostrarPainel) Comment(""); }

//+------------------------------------------------------------------+
//| OnTick — o full trailing roda a CADA TICK; as entradas, so no    |
//| fechamento de cada barra (sinais consistentes com o CAM).        |
//+------------------------------------------------------------------+
void OnTick()
  {
   // 1) STOP HIBRIDO: trailing continuo (cada tick) na posicao aberta.
   if(g_pos_estrat != 0 && HasPosition())
     {
      double trail = (g_pos_estrat == 2) ? InpD2_StopMovel_Pts
                   : (g_pos_estrat == 3) ? InpD3_StopMovel_Pts
                   : InpD1_StopMovel_Pts;
      ManageTrailingLive(trail, InpTrail_AtivaApos_Pts);
     }

   // 2) logica de barra (entradas) so no fechamento de uma nova barra.
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
      g_d3_broke_up=false; g_d3_broke_dn=false;
      g_d3_fired_short=false; g_d3_fired_long=false;
      g_sum_pv=0.0; g_sum_v=0.0; g_sum_pv2=0.0; g_n=0;
      g_d2_long_armed=true; g_d2_short_armed=true;
      g_d1_loss_today=false;
     }

   // VWAP/sigma cumulativos da sessao (sempre — a D2 precisa quando for chamada).
   double tp = (h + l + c) / 3.0;
   double v  = (double)iVolume(_Symbol, _Period, 1); if(v <= 0.0) v = 1.0;
   g_sum_pv += tp*v; g_sum_v += v; g_sum_pv2 += tp*tp*v; g_n++;

   // posicao fechou? Se era da D1 e fechou no prejuizo, LIBERA a D2 (recuperacao).
   // (o trailing tick-a-tick pode ter fechado a posicao no meio da barra anterior.)
   if(g_pos_estrat != 0 && !HasPosition())
     {
      if(g_pos_estrat == 1 && LastClosedProfit() < 0.0)
         g_d1_loss_today = true;
      g_pos_estrat = 0;
     }

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
   if(!g_or_ready) return;

   // rastreio do rompimento (p/ a D3): roda SEMPRE apos o range.
   double rng = g_or_high - g_or_low;
   if(rng > 0.0)
     {
      if(c > g_or_high + InpD3_BufferPts) g_d3_broke_up = true;
      if(c < g_or_low  - InpD3_BufferPts) g_d3_broke_dn = true;
     }

   if(tod >= cut) return;             // corte global de novas entradas
   if(HasPosition()) return;          // uma posicao por vez

   // DECISAO: manha = D1 (breakout) e, se ficar flat, D3 (rompimento falso).
   //          tarde = D2 (VWAP fade) SO se a D1 perdeu hoje (recuperacao).
   if(tod < d1_cut)
     {
      TryD1(c);
      if(!HasPosition()) TryD3(c);
     }
   else if(g_d1_loss_today)
      TryD2(c);
  }

//+------------------------------------------------------------------+
//| D1 ORB-30 — entra na quebra a favor da tendencia (so de manha).   |
//+------------------------------------------------------------------+
void TryD1(double c)
  {
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
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hibft_d1"))
        { g_max_favor = ref; g_pos_estrat = 1; }
     }
   else if(g_d1_short_armed && c < g_or_low && down)
     {
      g_d1_short_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_exits ? ref + InpD1_StopInicial_Pts : g_or_high;
      double tp  = static_exits ? (InpD1_AlvoFixo_Pts > 0 ? ref - InpD1_AlvoFixo_Pts : 0.0)
                                : g_or_low;
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hibft_d1"))
        { g_max_favor = ref; g_pos_estrat = 1; }
     }
  }

//+------------------------------------------------------------------+
//| D3 FBR — rompeu o range (> buffer) e voltou pra dentro: REVERTE.  |
//+------------------------------------------------------------------+
void TryD3(double c)
  {
   double rng = g_or_high - g_or_low;
   if(rng <= 0.0) return;

   if(g_d3_broke_up && !g_d3_fired_short && c < g_or_high)   // falhou a alta -> SHORT
     {
      g_d3_fired_short = true;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = ref + InpD3_StopInicial_Pts;
      double tp  = (InpD3_AlvoFixo_Pts > 0) ? ref - InpD3_AlvoFixo_Pts : 0.0;
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hibft_d3"))
        { g_max_favor = ref; g_pos_estrat = 3; }
     }
   else if(g_d3_broke_dn && !g_d3_fired_long && c > g_or_low) // falhou a baixa -> LONG
     {
      g_d3_fired_long = true;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = ref - InpD3_StopInicial_Pts;
      double tp  = (InpD3_AlvoFixo_Pts > 0) ? ref + InpD3_AlvoFixo_Pts : 0.0;
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_hibft_d3"))
        { g_max_favor = ref; g_pos_estrat = 3; }
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
      if(g_trade.Sell(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tpx), "cam_hibft_d2"))
        { g_max_favor = ref; g_pos_estrat = 2; }
     }
   else if(g_d2_long_armed && c < le) // esticou pra baixo -> compra (fade)
     {
      g_d2_long_armed=false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_stop ? ref - InpD2_StopInicial_Pts : vwap - InpD2_KStop*sg;
      double tpx = fixed_tp    ? ref + InpD2_AlvoFixo_Pts    : vwap;
      if(g_trade.Buy(InpContratos, _Symbol, 0.0, NormTick(sl), NormTick(tpx), "cam_hibft_d2"))
        { g_max_favor = ref; g_pos_estrat = 2; }
     }
  }

//+------------------------------------------------------------------+
//| STOP HIBRIDO — full trailing tick-a-tick. Persegue o pico (Bid na |
//| compra, Ask na venda) a `trail` pts; o SL so anda a favor e so a  |
//| partir de +`ativa_apos` pts de lucro. Preserva o TP. via Modify.  |
//+------------------------------------------------------------------+
void ManageTrailingLive(double trail, double ativa_apos)
  {
   if(trail <= 0.0) return;
   if(!PositionSelect(_Symbol)) return;
   if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) return;
   long   type   = PositionGetInteger(POSITION_TYPE);
   double open   = PositionGetDouble(POSITION_PRICE_OPEN);
   double cur_sl = PositionGetDouble(POSITION_SL);
   double cur_tp = PositionGetDouble(POSITION_TP);
   double bid    = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask    = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double new_sl = cur_sl;

   if(type == POSITION_TYPE_BUY)
     {
      g_max_favor = MathMax(g_max_favor, bid);
      if(bid - open < ativa_apos) return;            // trailing ainda nao ativou
      double cand = NormTick(g_max_favor - trail);
      if(cand > cur_sl) new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0) g_max_favor = ask;
      g_max_favor = MathMin(g_max_favor, ask);
      if(open - ask < ativa_apos) return;            // trailing ainda nao ativou
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
   if(tod < d1_cut)          fase = "MANHA — D1 (breakout) + D3 (rompimento falso)";
   else if(g_d1_loss_today)  fase = "TARDE — D2 (VWAP) RECUPERACAO (D1 perdeu)";
   else                      fase = "encerrado (D1 nao perdeu / fora de janela)";
   string pos = (g_pos_estrat==1) ? "D1 aberta"
              : (g_pos_estrat==2) ? "D2 aberta"
              : (g_pos_estrat==3) ? "D3 aberta" : "flat";
   Comment(StringFormat(
      "CaM HIBRIDO ORB+FBR+VWAP — FULL TRAILING (DEMO)\n"
      "Sessao: %s\n"
      "Fase: %s\n"
      "D1 perdeu hoje? %s   Posicao: %s   Contratos: %.0f\n"
      "Trailing tick-a-tick (ativa apos +%.0f pts)",
      g_session, fase, (g_d1_loss_today ? "SIM" : "nao"), pos, InpContratos,
      InpTrail_AtivaApos_Pts));
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

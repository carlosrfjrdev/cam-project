//+------------------------------------------------------------------+
//|  cam_d1_orb30_exec.mq5                                            |
//|  CaM StrategyLab — Estrategia D1 "ORB-30" — EA EXECUTOR           |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  Robo que OPERA (envia ordens) a estrategia D1 no grafico onde    |
//|  esta atachado. E o par "executor" do modelo de dois EAs:         |
//|    - cam_d1_orb30.mq5       -> GRAVADOR (nao opera; so registra o  |
//|                                ledger p/ conferir paridade com o   |
//|                                backtest do CAM).                   |
//|    - cam_d1_orb30_exec.mq5  -> EXECUTOR (ESTE): manda ordem a      |
//|                                mercado, com stop/alvo/stop-movel.  |
//|    - cam_d1_orb30_sinais.mq5-> executor + filtro de regime (so     |
//|                                opera em tendencia).                |
//|                                                                   |
//|  ===================  A ESTRATEGIA D1 (ORB-30)  ================  |
//|  "Opening Range Breakout" de 30 minutos, a favor da tendencia:    |
//|    1) ABERTURA: nos primeiros 30 min do pregao (configuravel),    |
//|       mede a maxima e a minima da sessao = o "range de abertura". |
//|    2) ENTRADA: quando o preco FECHA acima da maxima do range,      |
//|       COMPRA; quando fecha abaixo da minima, VENDE. So entra a     |
//|       favor da tendencia recente (filtro). Um trade por direcao    |
//|       por dia, a mercado.                                          |
//|    3) SAIDA: stop inicial em pontos + STOP MOVEL (trailing) que    |
//|       acompanha o pico travando lucro; alvo fixo OPCIONAL. Sem     |
//|       posicao virando a noite: zera no fim do pregao.             |
//|  Tese: dias de tendencia esticam alem do range de abertura; o     |
//|  trailing deixa o vencedor correr e o filtro evita o lateral.     |
//|                                                                   |
//|  =========================  ATENCAO  ===========================  |
//|  - VALORES BRUTOS: nao desconta corretagem/emolumentos/IR.        |
//|  - SEM Risk Engine nesta versao (estrategia pura). Unica trava:   |
//|    guard-rail DEMO (recusa iniciar fora de conta de demonstracao).|
//|  - Os parametros de estrategia devem ser IDENTICOS aos do         |
//|    backtest do CAM para a paridade fechar.                        |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.2"
#property strict
#property description "CaM D1 ORB-30 — robo executor (breakout de 30min + trailing). DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_D1_EXEC_VERSION "0.2.0"

//================== ESTRATEGIA — ENTRADA (range de abertura) ========
input group "Estrategia — Entrada"
input int    InpOR_Minutos          = 30;     // Janela do range de abertura (minutos do pregao)
input int    InpFiltroTendencia_Barras = 5000;// So opera a FAVOR da tendencia das ultimas N barras (0 = sem filtro)
input double InpRangeMinimoOR_Pts   = 0.0;    // Range minimo do dia p/ operar, em pontos (0 = sem minimo)

//================== ESTRATEGIA — SAIDA (stop / alvo / trailing) =====
// >> Defaults = config validada pelo Founder (MT5 tick): stop 700 / trail 800 /
//    tendencia 5000. IDENTICOS ao NTSL e ao CAM (validacao tripla / paridade). <<
input group "Estrategia — Saida"
input double InpStopInicial_Pts     = 700.0;  // Stop inicial: distancia da entrada, em pontos
input double InpAlvoFixo_Pts        = 0.0;    // Alvo fixo (take profit) em pontos (0 = sem alvo, deixa correr)
input double InpStopMovel_Pts       = 800.0;  // Stop movel (trailing): pontos atras do pico (0 = desligado)
input double InpAlvoRange_Mult      = 1.0;    // [avancado] modo range: alvo = N x tamanho do range (so se StopInicial=0)

//================== SESSAO (horario do pregao, fuso do grafico) =====
input group "Sessao (horario do grafico)"
input int    InpAbertura_Hora       = 9;      // Abertura do pregao — hora
input int    InpAbertura_Min        = 0;      // Abertura do pregao — minuto
input int    InpEntradaAte_Hora     = 17;     // Nao abre nova posicao apos esta hora
input int    InpEntradaAte_Min      = 0;      // Nao abre nova posicao apos este minuto
input int    InpFechamento_Hora     = 17;     // Zera posicao (flat) a partir desta hora
input int    InpFechamento_Min      = 55;     // Zera posicao (flat) a partir deste minuto

//================== EXECUCAO (ordem / volume) =======================
input group "Execucao"
input double InpContratos           = 1.0;    // QUANTIDADE DE CONTRATOS por ordem (WIN/WDO: 1 unidade = 1 contrato; ex.: 1, 2, 5)
input long   InpMagicNumber         = 20260603;// Identificador do robo (para isolar suas ordens)
input ulong  InpDesvioMax_Pts       = 10;     // Desvio maximo aceito no preenchimento (pontos)

//================== SEGURANCA =======================================
input group "Seguranca"
input bool   InpExigirContaDemo     = true;   // So inicia em conta DEMO (recusa conta real)

CTrade   g_trade;

//--- Estado interno da estrategia (espelha o generate_signals do Python).
string   g_session     = "";
double   g_or_high     = 0.0;
double   g_or_low      = 0.0;
bool     g_or_ready    = false;
bool     g_long_armed  = true;
bool     g_short_armed = true;
datetime g_last_bar    = 0;
double   g_max_favor   = 0.0;    // melhor preco a favor desde a entrada (p/ o stop movel)

//+------------------------------------------------------------------+
int OnInit()
  {
   // SEC — guard-rail DEMO (este EA envia ordem; recusa fora de DEMO).
   if(InpExigirContaDemo)
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

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpDesvioMax_Pts);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("[CamD1Exec] %s ativo. Symbol=%s TF=%s Contratos=%.2f Magic=%d.",
               CAM_D1_EXEC_VERSION, _Symbol,
               EnumToString((ENUM_TIMEFRAMES)_Period), InpContratos, InpMagicNumber);

   // Diagnostico de VOLUME/MARGEM — explica por que "acima de N contratos nao
   // opera": e limite do simbolo (volume max) ou falta de margem (conta pequena),
   // nao bug. Acima do max afordavel, a corretora rejeita por NO_MONEY.
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double vstep= SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double margem = MargemPorContrato();
   double livre  = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   int    afordavel = (margem > 0.0) ? (int)MathFloor(livre / margem) : -1;
   PrintFormat("[CamD1Exec] Volume do simbolo: min=%.2f max=%.2f step=%.2f.",
               vmin, vmax, vstep);
   PrintFormat("[CamD1Exec] Margem/contrato=%.2f | margem livre=%.2f | "
               "MAX AFORDAVEL ~%d contratos (acima disso a corretora rejeita).",
               margem, livre, afordavel);
   if(vmax > 0.0 && InpContratos > vmax)
      PrintFormat("[CamD1Exec] ATENCAO: InpContratos=%.2f > volume max do simbolo "
                  "(%.2f); sera limitado ao max.", InpContratos, vmax);
   if(afordavel >= 0 && InpContratos > afordavel)
      PrintFormat("[CamD1Exec] ATENCAO: InpContratos=%.2f acima do afordavel (~%d) "
                  "p/ a margem livre atual; ordens vao FALHAR por falta de margem.",
                  InpContratos, afordavel);
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

   // stop movel: ratcheta o SL a cada barra enquanto ha posicao (R-15c).
   if(InpStopMovel_Pts > 0 && HasPosition())
      ManageTrailing(h, l);

   int tod     = MinutesOfDay(t);
   int or_beg  = InpAbertura_Hora * 60 + InpAbertura_Min;
   int or_end  = or_beg + InpOR_Minutos;
   int cut     = InpEntradaAte_Hora * 60 + InpEntradaAte_Min;
   int s_close = InpFechamento_Hora * 60 + InpFechamento_Min;

   // flat compulsorio no fim da sessao (sem overnight) — antes de tudo.
   if(tod >= s_close)
     {
      if(HasPosition())
         g_trade.PositionClose(_Symbol);
      return;
     }

   // 1) construcao do range de abertura (primeiros InpOR_Minutos do pregao).
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

   // GATE DE REGIME A (R-15d): range minimo do OR (suprime chop). Day-level.
   if(InpRangeMinimoOR_Pts > 0 && rng < InpRangeMinimoOR_Pts)
      return;

   // 3) uma posicao por vez (single-symbol).
   if(HasPosition())
      return;

   // GATE DE REGIME B (R-15d): so a FAVOR da tendencia (~N barras).
   bool up   = TrendOk(c, +1);
   bool down = TrendOk(c, -1);

   // 4) gatilhos na quebra — entra A MERCADO. Modo estatico quando StopInicial>0:
   //    SL inicial em pontos, alvo fixo OPCIONAL (0 = sem alvo), stop movel via
   //    ManageTrailing. Fallback modo range quando StopInicial=0.
   bool   static_exits = (InpStopInicial_Pts > 0);
   double lote = NormalizarVolume(InpContratos);   // respeita min/max/step
   if(g_long_armed && c > g_or_high && up)
     {
      g_long_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double sl  = static_exits ? ref - InpStopInicial_Pts : g_or_low;
      double tp  = static_exits
                   ? (InpAlvoFixo_Pts > 0 ? ref + InpAlvoFixo_Pts : 0.0)
                   : g_or_high + InpAlvoRange_Mult * rng;
      if(g_trade.Buy(lote, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_exec"))
         g_max_favor = ref;   // reseta o pico p/ o stop movel
      else
         LogFalha("Compra", lote);
     }
   else if(g_short_armed && c < g_or_low && down)
     {
      g_short_armed = false;
      double ref = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double sl  = static_exits ? ref + InpStopInicial_Pts : g_or_high;
      double tp  = static_exits
                   ? (InpAlvoFixo_Pts > 0 ? ref - InpAlvoFixo_Pts : 0.0)
                   : g_or_low - InpAlvoRange_Mult * rng;
      if(g_trade.Sell(lote, _Symbol, 0.0, NormTick(sl), NormTick(tp), "cam_d1_exec"))
         g_max_favor = ref;
      else
         LogFalha("Venda", lote);
     }
  }

//+------------------------------------------------------------------+
//| Margem exigida por 1 contrato (p/ diagnostico de "nao opera").    |
//+------------------------------------------------------------------+
double MargemPorContrato()
  {
   double m = 0.0;
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(price <= 0.0) price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(!OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, 1.0, price, m))
      return 0.0;
   return m;
  }

//+------------------------------------------------------------------+
//| Normaliza o volume aos limites do simbolo (min/max/step).         |
//+------------------------------------------------------------------+
double NormalizarVolume(double vol)
  {
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double vstep= SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(vstep > 0.0) vol = MathRound(vol / vstep) * vstep;
   if(vmin  > 0.0 && vol < vmin) vol = vmin;
   if(vmax  > 0.0 && vol > vmax) vol = vmax;
   return vol;
  }

//+------------------------------------------------------------------+
//| Log de falha de ordem em TEXTO (retcode + motivo + margem).       |
//+------------------------------------------------------------------+
void LogFalha(string lado, double lote)
  {
   double margem_op = 0.0;
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, lote, price, margem_op);
   PrintFormat("[CamD1Exec] %s falhou ret=%d (%s). lote=%.2f margem_exigida=%.2f "
               "margem_livre=%.2f. Se for NO_MONEY: conta pequena p/ esse nro de "
               "contratos -> reduza InpContratos ou aumente o capital.",
               lado, g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription(),
               lote, margem_op, AccountInfoDouble(ACCOUNT_MARGIN_FREE));
  }

//+------------------------------------------------------------------+
//| Stop movel (R-15c): segue o pico a InpStopMovel_Pts; o SL so anda |
//| a favor (sobe na compra, desce na venda) via PositionModify.      |
//+------------------------------------------------------------------+
void ManageTrailing(double h, double l)
  {
   if(!PositionSelect(_Symbol))
      return;
   if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber)
      return;
   long   type   = PositionGetInteger(POSITION_TYPE);
   double cur_sl = PositionGetDouble(POSITION_SL);
   double cur_tp = PositionGetDouble(POSITION_TP);
   double new_sl = cur_sl;

   if(type == POSITION_TYPE_BUY)
     {
      g_max_favor = MathMax(g_max_favor, h);
      double cand = NormTick(g_max_favor - InpStopMovel_Pts);
      if(cand > cur_sl)
         new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0)
         g_max_favor = l;
      g_max_favor = MathMin(g_max_favor, l);
      double cand = NormTick(g_max_favor + InpStopMovel_Pts);
      if(cur_sl <= 0.0 || cand < cur_sl)
         new_sl = cand;
     }
   if(new_sl != cur_sl)
      g_trade.PositionModify(_Symbol, new_sl, cur_tp);
  }

//+------------------------------------------------------------------+
//| Filtro de tendencia (R-15d). Espelha _trend_ok do Python: compara |
//| o close da barra atual (shift 1) com o de N barras antes.         |
//+------------------------------------------------------------------+
bool TrendOk(double c_now, int side)
  {
   int n = InpFiltroTendencia_Barras;
   if(n <= 0)
      return true;
   double ref = iClose(_Symbol, _Period, 1 + n);
   if(ref <= 0.0)
      return false;
   return (side > 0) ? (c_now > ref) : (c_now < ref);
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
   return (PositionGetInteger(POSITION_MAGIC) == InpMagicNumber);
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

//+------------------------------------------------------------------+
//| cam_d1_orb30_sinais.mq5                                          |
//| StrategyLab — D1 (ORB-30) — EA de SINAIS / ALERTAS (nao opera).  |
//|                                                                   |
//| Mostra ao vivo onde a D1 dispararia: desenha o opening range,    |
//| marca uma seta na quebra valida (quebra + filtro de tendencia) e |
//| dispara Alert. Exibe o REGIME (Efficiency Ratio diario) — sinal  |
//| de macro/volatilidade validado: ER alto = tendencia (operar),    |
//| ER baixo = lateral (evitar). NAO envia ordem, NAO grava ledger   |
//| (fora da allowlist do lint_mql5).                                |
//|                                                                   |
//| Logica de entrada (espelha d1_orb30.py):                          |
//|   OR = [high,low] dos primeiros InpOrMinutes; quebra long se     |
//|   close>OR_high, short se <OR_low; filtro de tendencia (so a      |
//|   favor de N barras); 1 disparo por direcao/dia.                  |
//|                                                                   |
//| Regime: ER(N dias) = |close[0]-close[N]| / soma|variacoes diarias||
//|   Lido das barras D1 (PERIOD_D1). >= InpRegimeErMin => TENDENCIA. |
//|   InpUseRegimeFilter=false: mostra TODOS os sinais, anotando o    |
//|   regime; true: suprime os sinais em regime lateral.              |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D1 ORB-30 — sinais/alertas + regime (nao opera)"

#define CAM_D1_SINAIS_VERSION "0.1.0"

//--- Estrategia (espelha D1Params) ----------------------------------
input int    InpOrMinutes        = 30;     // janela do opening range (min)
input int    InpTrendFilterBars  = 5000;   // so a favor da tendencia de N barras; 0=off
input int    InpSessionOpenHour  = 9;
input int    InpSessionOpenMin   = 0;
input int    InpEntryUntilHour   = 17;
input int    InpEntryUntilMin    = 0;
//--- Referencia de exits (so para exibir no alerta) -----------------
input double InpStopPoints        = 700.0; // SL inicial (exibicao)
input double InpTrailPoints        = 800.0; // stop movel (exibicao)
//--- Gate de REGIME (Efficiency Ratio diario) -----------------------
input bool   InpUseRegimeFilter   = false; // true = suprime sinais em lateral
input int    InpRegimeErDays       = 10;    // janela do ER (dias)
input double InpRegimeErMin         = 0.35;  // ER >= isto => tendencia
//--- Visual ---------------------------------------------------------
input bool   InpDrawOrLines       = true;   // desenha linhas do OR
input bool   InpSendAlerts        = true;   // dispara Alert no sinal

//--- Estado ---------------------------------------------------------
string   g_session     = "";
double   g_or_high     = 0.0;
double   g_or_low      = 0.0;
bool     g_or_ready    = false;
bool     g_long_armed  = true;
bool     g_short_armed = true;
datetime g_last_bar    = 0;
int      g_sig_count   = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   PrintFormat("[CamD1Sinais] %s ativo. Symbol=%s TF=%s (nao opera).",
               CAM_D1_SINAIS_VERSION, _Symbol,
               EnumToString((ENUM_TIMEFRAMES)_Period));
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   ObjectsDeleteAll(0, "camd1_");
   Comment("");
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar)
     {
      UpdatePanel();   // atualiza painel/regime mesmo sem nova barra
      return;
     }
   g_last_bar = cur;

   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iHigh(_Symbol,_Period,1), iLow(_Symbol,_Period,1),
              iClose(_Symbol,_Period,1));
   UpdatePanel();
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double h, double l, double c)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      g_session = session;
      g_or_ready = false;
      g_long_armed = true;
      g_short_armed = true;
     }

   int tod    = MinutesOfDay(t);
   int or_beg = InpSessionOpenHour*60 + InpSessionOpenMin;
   int or_end = or_beg + InpOrMinutes;
   int cut    = InpEntryUntilHour*60 + InpEntryUntilMin;

   // construcao do opening range
   if(tod >= or_beg && tod < or_end)
     {
      if(!g_or_ready) { g_or_high=h; g_or_low=l; g_or_ready=true; }
      else { g_or_high=MathMax(g_or_high,h); g_or_low=MathMin(g_or_low,l); }
      if(InpDrawOrLines) DrawOrLines(t);
      return;
     }
   if(!g_or_ready) return;
   if(tod >= cut) return;
   if(g_or_high - g_or_low <= 0.0) return;

   bool up   = TrendOk(c, +1);
   bool down = TrendOk(c, -1);
   double er = RegimeER();
   bool regime_ok = (er < 0.0) ? true : (er >= InpRegimeErMin);

   if(g_long_armed && c > g_or_high && up)
     {
      g_long_armed = false;
      EmitSignal(t, +1, c, er, regime_ok);
     }
   else if(g_short_armed && c < g_or_low && down)
     {
      g_short_armed = false;
      EmitSignal(t, -1, c, er, regime_ok);
     }
  }

//+------------------------------------------------------------------+
//| Emite o sinal: seta + alerta. Em regime lateral, marca diferente  |
//| (e suprime se InpUseRegimeFilter).                                |
//+------------------------------------------------------------------+
void EmitSignal(datetime t, int side, double price, double er, bool regime_ok)
  {
   if(InpUseRegimeFilter && !regime_ok)
     {
      PrintFormat("[CamD1Sinais] sinal %s FILTRADO (lateral, ER=%.2f)",
                  (side>0?"COMPRA":"VENDA"), er);
      return;
     }
   g_sig_count++;
   string name = StringFormat("camd1_sig_%d", g_sig_count);
   double y = (side>0) ? iLow(_Symbol,_Period,1) : iHigh(_Symbol,_Period,1);
   color clr = regime_ok ? (side>0 ? clrLime : clrRed) : clrGray;
   ObjectCreate(0, name, OBJ_ARROW, 0, t, y);
   ObjectSetInteger(0, name, OBJPROP_ARROWCODE, side>0 ? 233 : 234);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);

   string regime = (er<0.0) ? "?" : (regime_ok ? "TENDENCIA" : "LATERAL");
   string msg = StringFormat(
      "CaM D1 ORB-30 %s %s @ %s | regime=%s ER=%.2f | SL~%.0fpts trail~%.0f",
      _Symbol, (side>0?"COMPRA":"VENDA"),
      DoubleToString(price,_Digits), regime, er,
      InpStopPoints, InpTrailPoints);
   PrintFormat("[CamD1Sinais] %s", msg);
   if(InpSendAlerts) Alert(msg);
  }

//+------------------------------------------------------------------+
//| Filtro de tendencia (espelha _trend_ok do Python).               |
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
//| Efficiency Ratio diario sobre InpRegimeErDays. -1 se sem dados.   |
//| ER = |close[1]-close[1+N]| / soma|variacao diaria| (N dias).      |
//+------------------------------------------------------------------+
double RegimeER()
  {
   int n = InpRegimeErDays;
   if(n < 2) return -1.0;
   if(Bars(_Symbol, PERIOD_D1) < n + 2) return -1.0;
   double c0 = iClose(_Symbol, PERIOD_D1, 1);     // ultima diaria fechada
   double cn = iClose(_Symbol, PERIOD_D1, 1 + n);
   if(c0 <= 0.0 || cn <= 0.0) return -1.0;
   double denom = 0.0;
   for(int k = 1; k <= n; k++)
     {
      double a = iClose(_Symbol, PERIOD_D1, k);
      double b = iClose(_Symbol, PERIOD_D1, k + 1);
      if(a > 0.0 && b > 0.0) denom += MathAbs(a - b);
     }
   if(denom <= 0.0) return -1.0;
   return MathAbs(c0 - cn) / denom;
  }

//+------------------------------------------------------------------+
void DrawOrLines(datetime t)
  {
   DrawHLine("camd1_orh_" + g_session, g_or_high, clrDodgerBlue);
   DrawHLine("camd1_orl_" + g_session, g_or_low,  clrDodgerBlue);
  }

void DrawHLine(string name, double price, color clr)
  {
   if(ObjectFind(0, name) < 0)
      ObjectCreate(0, name, OBJ_HLINE, 0, 0, price);
   ObjectSetDouble(0, name, OBJPROP_PRICE, price);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DOT);
  }

//+------------------------------------------------------------------+
void UpdatePanel()
  {
   double er = RegimeER();
   string regime = (er<0.0) ? "sem dados" :
                   (er >= InpRegimeErMin ? "TENDENCIA (operar)" : "LATERAL (evitar)");
   string filt = InpUseRegimeFilter ? "ON" : "OFF (mostra todos)";
   Comment(StringFormat(
      "CaM D1 ORB-30 — SINAIS (nao opera)\n"
      "Sessao: %s   OR: %s / %s   %s\n"
      "Tendencia(%d barras) | Regime ER%d=%.2f  ->  %s\n"
      "Filtro de regime: %s (min %.2f)   Sinais hoje: %d",
      g_session,
      g_or_ready ? DoubleToString(g_or_high,_Digits) : "-",
      g_or_ready ? DoubleToString(g_or_low,_Digits) : "-",
      g_or_ready ? "" : "(coletando)",
      InpTrendFilterBars, InpRegimeErDays, er, regime,
      filt, InpRegimeErMin, g_sig_count));
  }

//+------------------------------------------------------------------+
int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

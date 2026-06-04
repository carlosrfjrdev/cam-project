//+------------------------------------------------------------------+
//| cam_d1_orb30.mq5                                                  |
//| StrategyLab — D1 (ORB-30) — lado MQL5 da DUPLA IMPLEMENTACAO.     |
//|                                                                   |
//| ADR-SL-01: este EA implementa a MESMA logica de                  |
//|   cam/features/strategy_lab/strategies/d1_orb30.py + backtest_    |
//|   engine.py, escrita A MAO e de forma INDEPENDENTE. A paridade    |
//|   (parity.py) compara os dois ledgers trade-a-trade e detecta     |
//|   qualquer divergencia silenciosa. Codegen NAO e usado (decisao   |
//|   do Founder) — a redundancia dissimilar e a defesa.              |
//|                                                                   |
//| NATUREZA: EA-GRAVADOR de paridade. Roda no Strategy Tester (ou    |
//|   atachado a um grafico) e EXPORTA o ledger canonico em CSV. NAO  |
//|   envia ordem (lint_mql5 reserva OrderSend para cam_risk_mirror). |
//|   A execucao real em DEMO e uma etapa posterior (Assets Experts). |
//|                                                                   |
//| VALORES BRUTOS (R-11): sem corretagem/emolumentos/IR/slippage. O  |
//|   ledger registra os precos CANONICOS de decisao (open da barra   |
//|   seguinte na entrada; nivel de stop/alvo na saida), nao o fill   |
//|   real de book — paridade e da MATEMATICA da estrategia.          |
//|                                                                   |
//| Contrato de paridade (subset C1-C6, sem C7/C8):                   |
//|   C4 fill next-bar-open · C5 pior caso intrabar (stop antes do    |
//|   alvo) · C6 gap honesto no open · C11 flat no fim da sessao.     |
//|                                                                   |
//| SEC: guard-rail DEMO de defesa em profundidade (sem OrderSend, e  |
//|   read-only por construcao; o guard-rail e redundancia barata).   |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "StrategyLab D1 ORB-30 — gravador de ledger canonico p/ paridade (sem OrderSend)"

#define CAM_D1_ORB30_VERSION "0.1.0-onda1"

//--- Parametros da estrategia (espelham D1Params do Python) ---------
input int    InpOrMinutes        = 30;     // janela do opening range (min)
// SL/TP ESTATICOS em pontos, relativos a entrada (R-15b). Ativos quando ambos
// > 0 (tem prioridade sobre o modo range/InpTargetR). Espelham stop_points/
// target_points do Python — DEVEM ser identicos no backtest do CAM p/ paridade.
input double InpStopPoints        = 100.0; // SL inicial (pontos da entrada)
input double InpTargetPoints      = 0.0;   // TP fixo (pontos); 0 = sem TP (deixa correr)
input double InpTrailPoints        = 400.0; // STOP MOVEL (pontos atras do pico); 0 = off
// GATE DE REGIME (R-15d) — devem ser IDENTICOS ao backtest do CAM (paridade):
input int    InpTrendFilterBars   = 400;   // so a favor da tendencia de N barras; 0 = off
input double InpMinOrPoints        = 0.0;   // range minimo do OR p/ operar o dia; 0 = off
input double InpTargetR          = 1.0;    // modo range (fallback): alvo = R x range
input int    InpSessionOpenHour  = 9;      // abertura do pregao (hora)
input int    InpSessionOpenMin   = 0;      // abertura do pregao (min)
input int    InpEntryUntilHour   = 17;     // nao abre nova posicao apos esta hora
input int    InpEntryUntilMin    = 0;
input int    InpSessionCloseHour = 17;     // flat compulsorio (hora)
input int    InpSessionCloseMin  = 55;     // flat compulsorio (min)
//--- Contabilizacao bruta (espelham point_value/qty do Python) ------
input double InpPointValue       = 0.20;   // valor financeiro de 1 ponto (WIN=0.20)
input int    InpQty              = 1;      // contratos
//--- Saida do ledger ------------------------------------------------
input string InpLedgerFile       = "cam_d1_orb30_ledger.csv";
//--- Seguranca (defesa em profundidade; este EA nao envia ordem) ----
input bool   InpRequireDemoAccount = true;

//--- Estado da maquina (espelha o loop de backtest_engine.py) -------
string   g_session       = "";       // session_date corrente ("YYYY-MM-DD")
double   g_or_high       = 0.0;
double   g_or_low        = 0.0;
bool     g_or_ready      = false;    // range coletado nesta sessao
bool     g_long_armed    = true;
bool     g_short_armed   = true;

// sinal pendente gerado no fechamento da barra anterior (consumido no open seguinte)
bool     g_pending       = false;
int      g_pending_side  = 0;        // +1 long, -1 short
double   g_pending_stop  = 0.0;
double   g_pending_tgt   = 0.0;

// posicao aberta (single-symbol: no maximo uma)
bool     g_pos_open      = false;
int      g_pos_side      = 0;        // +1 long, -1 short
datetime g_pos_ts_entry  = 0;
double   g_pos_entry     = 0.0;
double   g_pos_stop      = 0.0;
double   g_pos_tgt       = 0.0;
bool     g_pos_has_tgt   = true;     // ha TP fixo? (target_points>0)
double   g_pos_maxfavor  = 0.0;      // pico a favor (p/ stop movel)
int      g_pair_id       = 0;

datetime g_last_bar      = 0;        // deteccao de nova barra
int      g_file          = INVALID_HANDLE;
int      g_trades_out    = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   // SEC — guard-rail DEMO (defesa em profundidade; nao ha OrderSend aqui).
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD1ORB30] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }

   g_file = FileOpen(InpLedgerFile,
                     FILE_WRITE | FILE_CSV | FILE_ANSI, ';');
   if(g_file == INVALID_HANDLE)
     {
      PrintFormat("[CamD1ORB30] Falha ao abrir ledger '%s' (err=%d).",
                  InpLedgerFile, GetLastError());
      return(INIT_FAILED);
     }
   // Cabecalho do schema canonico (alinha com strategy_leg_trade).
   FileWrite(g_file,
             "pair_id", "leg", "symbol",
             "ts_entry", "price_entry", "ts_exit", "price_exit",
             "qty", "exit_reason", "pnl_bruto", "volume_financeiro");

   PrintFormat("[CamD1ORB30] %s ativo. Symbol=%s TF=%s -> ledger '%s'.",
               CAM_D1_ORB30_VERSION, _Symbol,
               EnumToString((ENUM_TIMEFRAMES)_Period), InpLedgerFile);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // posicao ainda aberta no fim da serie -> flat no ultimo close (espelha
   // o passo 3 de run_d1_backtest: fecha no ultimo close, motivo "session").
   if(g_pos_open)
     {
      double close_last = iClose(_Symbol, _Period, 1);
      datetime ts_last  = iTime(_Symbol, _Period, 1);
      if(close_last > 0.0)
         RecordExit(ts_last, close_last, "session");
     }
   if(g_file != INVALID_HANDLE)
     {
      FileClose(g_file);
      PrintFormat("[CamD1ORB30] Ledger fechado: %d trade(s) gravado(s).",
                  g_trades_out);
     }
  }

//+------------------------------------------------------------------+
//| OnTick — processa apenas no fechamento de cada barra (nova barra).|
//| A barra recem-completada e a de shift 1 (espelha "barra i" do      |
//| loop Python). Ordem: saida -> entrada pendente -> OR -> sinal.     |
//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar)
      return;                      // ainda na mesma barra
   g_last_bar = cur;

   // dados da barra recem-completada (shift 1)
   datetime t  = iTime(_Symbol, _Period, 1);
   if(t == 0)
      return;
   double o = iOpen(_Symbol, _Period, 1);
   double h = iHigh(_Symbol, _Period, 1);
   double l = iLow(_Symbol, _Period, 1);
   double c = iClose(_Symbol, _Period, 1);

   ProcessBar(t, o, h, l, c);
  }

//+------------------------------------------------------------------+
//| Porte fiel de uma iteracao de run_d1_backtest + generate_signals. |
//+------------------------------------------------------------------+
void ProcessBar(datetime t, double o, double h, double l, double c)
  {
   string session = SessionDate(t);

   // novo pregao -> reseta estado (espelha generate_signals).
   if(session != g_session)
     {
      g_session     = session;
      g_or_ready    = false;
      g_long_armed  = true;
      g_short_armed = true;
      // posicao nao deveria cruzar sessao: ja saiu por flat C11. Defensivo:
      // se ainda aberta, fecha no open desta barra do novo dia.
      if(g_pos_open)
         RecordExit(t, o, "session");
     }

   // 1) gerir posicao aberta — saidas ANTES de novas entradas (C3).
   if(g_pos_open)
     {
      double xprice; string reason;
      if(ResolveExit(o, h, l, c, t, xprice, reason))
         RecordExit(t, xprice, reason);
     }

   // 2) entrada: sinal nasceu no fechamento da barra anterior -> open desta (C4).
   if(!g_pos_open && g_pending)
     {
      g_pos_open     = true;
      g_pos_side     = g_pending_side;
      g_pos_ts_entry = t;
      g_pos_entry    = o;                 // fill next-bar-open
      g_pos_maxfavor = o;                 // pico inicial = entrada (stop movel)
      // Exits resolvidos no FILL (relativos a entrada) — espelha _resolve_levels
      // do backtest_engine.py. Modo estatico quando StopPoints>0; TP opcional
      // (TargetPoints=0 => sem TP). Fallback: niveis do range.
      if(InpStopPoints > 0)
        {
         g_pos_has_tgt = (InpTargetPoints > 0);
         if(g_pending_side > 0)
           { g_pos_stop = o - InpStopPoints; g_pos_tgt = o + InpTargetPoints; }
         else
           { g_pos_stop = o + InpStopPoints; g_pos_tgt = o - InpTargetPoints; }
        }
      else
        {
         g_pos_has_tgt = true;
         g_pos_stop = g_pending_stop; g_pos_tgt = g_pending_tgt;
        }
     }
   g_pending = false;                     // consome (ou descarta) pendente

   // 3) construcao do opening range (primeiros InpOrMinutes do pregao).
   int tod    = MinutesOfDay(t);
   int or_beg = InpSessionOpenHour * 60 + InpSessionOpenMin;
   int or_end = or_beg + InpOrMinutes;
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
      return;                             // dentro do range: sem sinal
     }

   if(!g_or_ready)
      return;                             // sessao sem range coletado

   // 4) janela de entrada (apos o range, antes do corte).
   int entry_cut = InpEntryUntilHour * 60 + InpEntryUntilMin;
   if(tod >= entry_cut)
      return;

   double rng = g_or_high - g_or_low;
   if(rng <= 0.0)
      return;

   // GATE DE REGIME A (R-15d): range minimo do OR (suprime chop). Day-level.
   if(InpMinOrPoints > 0 && rng < InpMinOrPoints)
      return;

   // 5) gatilhos na quebra (decisao no fechamento da barra; consumo em t+1).
   //    So arma sinal se estiver flat (uma posicao por vez, single-symbol).
   if(g_pos_open)
      return;

   // GATE DE REGIME B (R-15d): so a FAVOR da tendencia (~N barras). Espelha
   // _trend_ok do Python: long se close > close[N atras]; short se menor.
   bool up   = TrendOk(c, +1);
   bool down = TrendOk(c, -1);

   if(g_long_armed && c > g_or_high && up)
     {
      g_long_armed   = false;
      g_pending      = true;
      g_pending_side = +1;
      g_pending_stop = g_or_low;
      g_pending_tgt  = g_or_high + InpTargetR * rng;
     }
   else if(g_short_armed && c < g_or_low && down)
     {
      g_short_armed  = false;
      g_pending      = true;
      g_pending_side = -1;
      g_pending_stop = g_or_high;
      g_pending_tgt  = g_or_low - InpTargetR * rng;
     }
  }

//+------------------------------------------------------------------+
//| Filtro de tendencia (R-15d). Espelha _trend_ok: compara o close   |
//| da barra atual (shift 1) com o close de N barras antes (shift     |
//| 1+N). off (InpTrendFilterBars<=0) -> sempre true.                 |
//+------------------------------------------------------------------+
bool TrendOk(double c_now, int side)
  {
   int n = InpTrendFilterBars;
   if(n <= 0)
      return true;
   double ref = iClose(_Symbol, _Period, 1 + n);
   if(ref <= 0.0)
      return false;                  // sem historico suficiente
   return (side > 0) ? (c_now > ref) : (c_now < ref);
  }

//+------------------------------------------------------------------+
//| Resolve a saida da posicao na barra atual. Espelha _resolve_exit: |
//|   gap honesto no open (C6) -> pior caso intrabar stop>alvo (C5)   |
//|   -> flat compulsorio na sessao (C11).                            |
//| Retorna true se houve saida; preenche xprice/reason.              |
//+------------------------------------------------------------------+
bool ResolveExit(double o, double h, double l, double c, datetime t,
                 double &xprice, string &reason)
  {
   bool is_long = (g_pos_side > 0);
   double stop = g_pos_stop;
   double tgt  = g_pos_tgt;
   bool has_tgt = g_pos_has_tgt;

   // gap honesto no open
   if(is_long)
     {
      if(o <= stop)            { xprice = o; reason = "stop";   return true; }
      if(has_tgt && o >= tgt)  { xprice = o; reason = "target"; return true; }
     }
   else
     {
      if(o >= stop)            { xprice = o; reason = "stop";   return true; }
      if(has_tgt && o <= tgt)  { xprice = o; reason = "target"; return true; }
     }

   // intrabar — pior caso: stop antes do alvo
   if(is_long)
     {
      if(l <= stop)            { xprice = stop; reason = "stop";   return true; }
      if(has_tgt && h >= tgt)  { xprice = tgt;  reason = "target"; return true; }
     }
   else
     {
      if(h >= stop)            { xprice = stop; reason = "stop";   return true; }
      if(has_tgt && l <= tgt)  { xprice = tgt;  reason = "target"; return true; }
     }

   // stop movel (R-15c): ratcheta o stop com o extremo desta barra (vale p/ as
   // proximas). Espelha exatamente o backtest_engine.py — o stop nunca recua.
   if(InpTrailPoints > 0)
     {
      if(is_long)
        {
         g_pos_maxfavor = MathMax(g_pos_maxfavor, h);
         g_pos_stop = MathMax(g_pos_stop, g_pos_maxfavor - InpTrailPoints);
        }
      else
        {
         g_pos_maxfavor = MathMin(g_pos_maxfavor, l);
         g_pos_stop = MathMin(g_pos_stop, g_pos_maxfavor + InpTrailPoints);
        }
     }

   // flat compulsorio no fechamento da sessao (sem overnight).
   int tod    = MinutesOfDay(t);
   int s_close = InpSessionCloseHour * 60 + InpSessionCloseMin;
   if(tod >= s_close)
     {
      xprice = c; reason = "session"; return true;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Grava a perna fechada no ledger canonico e zera a posicao.        |
//| pnl_bruto e volume_financeiro usam a MESMA formula de domain.py.  |
//+------------------------------------------------------------------+
void RecordExit(datetime ts_exit, double price_exit, string reason)
  {
   double direction = (g_pos_side > 0) ? 1.0 : -1.0;
   double pnl = (price_exit - g_pos_entry) * direction
                * (double)InpQty * InpPointValue;
   double vol = (MathAbs(g_pos_entry) + MathAbs(price_exit))
                * (double)InpQty * InpPointValue;
   string leg = (g_pos_side > 0) ? "long" : "short";

   if(g_file != INVALID_HANDLE)
     {
      FileWrite(g_file,
                IntegerToString(g_pair_id),
                leg,
                _Symbol,
                FmtTs(g_pos_ts_entry),
                DoubleToString(g_pos_entry, _Digits),
                FmtTs(ts_exit),
                DoubleToString(price_exit, _Digits),
                IntegerToString(InpQty),
                reason,
                DoubleToString(pnl, 2),
                DoubleToString(vol, 2));
      g_trades_out++;
     }

   g_pair_id++;
   g_pos_open = false;
   g_pos_side = 0;
  }

//+------------------------------------------------------------------+
//| Helpers de tempo (sem dependencia externa).                       |
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

// ISO "YYYY-MM-DDTHH:MM:SS" — o service do backend normaliza o ts do
// Python para o MESMO formato antes de chamar parity.compare (alinhamento
// por (ts_entry, leg, symbol)).
string FmtTs(datetime t)
  {
   MqlDateTime st;
   TimeToStruct(t, st);
   return StringFormat("%04d-%02d-%02dT%02d:%02d:%02d",
                       st.year, st.mon, st.day, st.hour, st.min, st.sec);
  }
//+------------------------------------------------------------------+

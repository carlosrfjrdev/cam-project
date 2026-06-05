//+------------------------------------------------------------------+
//| cam_bridge.mq5                                                    |
//| EA principal do CaM — bridge ZeroMQ read-only (SPEC v0.2)         |
//|                                                                   |
//| Artigos constitucionais aplicaveis:                               |
//|   Art. 15o — Risk Engine e autoridade. Este EA NAO valida.        |
//|   Art. 18o — Kill switch e externo (Python). EA respeita.         |
//|   Art. 25o — P&L em mensagens DEVE conter pnl_net.                |
//|   Art. 35o — IA nao toca este EA.                                 |
//|                                                                   |
//| Canais ZeroMQ que PUBLICA:                                        |
//|   mt5.tick       — preco/bid/ask/volume/timestamp                 |
//|   mt5.position   — posicoes abertas                                |
//|   mt5.fill       — execucoes detectadas                            |
//|   mt5.heartbeat  — 1 msg/segundo                                   |
//|                                                                   |
//| Canais ZeroMQ que RESPONDE (REQ/REP read-only):                   |
//|   PING               -> PONG                                       |
//|   GET_STATE          -> {balance, equity, margin}                  |
//|   GET_POSITIONS      -> lista de posicoes abertas                  |
//|   GET_SYMBOL_INFO    -> metadata do simbolo                        |
//|   GET_CANDLES        -> OHLCV historico (CopyRates) — Inspetor      |
//|   GET_SYMBOLS        -> lista de simbolos disponiveis — Inspetor    |
//|   SUBSCRIBE          -> SymbolSelect + MarketBookAdd — Inspetor     |
//|   UNSUBSCRIBE        -> remove watch do simbolo — Inspetor          |
//|                                                                   |
//| Canal PUB adicional (Inspetor):                                   |
//|   mt5.book           -> profundidade (DOM) via OnBookEvent          |
//|                                                                   |
//| CA15.1 — NAO chama OrderSend/OrderClose/PositionOpen/PositionClose|
//| §7.1 sec — verifica conta DEMO no startup, abort se REAL          |
//+------------------------------------------------------------------+
#property copyright "CaM — The Carlos Alternative Money"
#property version   "0.40"
#property strict
#property description "CaM Bridge ZeroMQ — Read-only v0.4 (Inspetor de Ativo: candles+book+symbols)"

// TASK-009 (BL-A): Control Plane G2 — PAUSE_EA, RESUME_EA, GET_VERSION
// Estes comandos NÃO disparam OrderSend — bridge segue READ-ONLY (CA15.1).
// SUBMIT_ORDER será adicionado APENAS em cam_risk_mirror.mq5 (T025/T027 BL-E),
// nunca aqui.

#include <cam_zmq.mqh>

#define CAM_BRIDGE_VERSION "0.4.2-ticks-bulk"

input int    InpPubPort = 5556;
input int    InpReqPort = 5557;
input int    InpHeartbeatMs = 1000;       // 1 msg/segundo (SPEC R12.04)
input int    InpMagicNumber = 20260525;   // distinto p/ identificar v0.2
// sec §7.1 / ADR-014 R-10 — defesa em profundidade. Default TRUE (so DEMO).
// Para o Inspetor em conta REAL (read-only): setar FALSE conscientemente no
// attach do EA. A bridge nao tem OrderSend; ler dado de conta real e seguro.
input bool   InpRequireDemoAccount = true;
// Inspetor — publica profundidade de mercado (DOM) quando o ativo fornece book.
input bool   InpPublishBook = true;
// Inspetor — limite de barras por GET_CANDLES (protege heartbeat do EA single-thread).
input int    InpMaxCandles = 5000;

datetime g_last_heartbeat_ms = 0;

// TASK-009 — flag de pausa: quando true, OnTick NÃO publica em mt5.tick
// (heartbeat continua via OnTimer — isso é critério CA-A.5).
bool     g_ontick_paused = false;

// Inspetor — simbolo atualmente observado para tick/book ao vivo.
// Default: o simbolo do grafico onde o EA esta atachado.
string   g_watched_symbol = "";

//+------------------------------------------------------------------+
int OnInit()
  {
   // sec §7.1 — verifica conta DEMO antes de inicializar bridge
   if(InpRequireDemoAccount)
     {
      ENUM_ACCOUNT_TRADE_MODE mode = (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamBridge] ABORTANDO: conta nao e DEMO (mode=%d). v0.2 e read-only mas requer DEMO por seguranca.", mode);
         return(INIT_FAILED);
        }
     }

   if(!CamZMQInit(InpPubPort, InpReqPort))
     {
      Print("[CamBridge] Falha ao inicializar ZeroMQ.");
      return(INIT_FAILED);
     }

   // Inspetor — observa por padrao o simbolo do grafico atual.
   g_watched_symbol = Symbol();
   if(InpPublishBook)
      MarketBookAdd(g_watched_symbol);

   EventSetMillisecondTimer(InpHeartbeatMs);
   PrintFormat("[CamBridge] v%s read-only ativo. Magic=%d Watched=%s Book=%s",
               CAM_BRIDGE_VERSION, InpMagicNumber, g_watched_symbol,
               (InpPublishBook ? "on" : "off"));
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
   if(InpPublishBook && StringLen(g_watched_symbol) > 0)
      MarketBookRelease(g_watched_symbol);
   CamZMQShutdown();
  }

//+------------------------------------------------------------------+
//| OnBookEvent — Inspetor: publica DOM (profundidade) em mt5.book    |
//| READ-ONLY: apenas le MarketBookGet, nunca envia ordem.            |
//+------------------------------------------------------------------+
void OnBookEvent(const string &symbol)
  {
   if(!InpPublishBook) return;
   if(symbol != g_watched_symbol) return;

   MqlBookInfo book[];
   if(!MarketBookGet(symbol, book)) return;

   string bids = "";
   string asks = "";
   int n = ArraySize(book);
   for(int i = 0; i < n; i++)
     {
      string level = StringFormat("{\"price\":%.5f,\"vol\":%d}",
                                  book[i].price, (int)book[i].volume);
      if(book[i].type == BOOK_TYPE_BUY || book[i].type == BOOK_TYPE_BUY_MARKET)
        {
         if(StringLen(bids) > 0) bids += ",";
         bids += level;
        }
      else if(book[i].type == BOOK_TYPE_SELL || book[i].type == BOOK_TYPE_SELL_MARKET)
        {
         if(StringLen(asks) > 0) asks += ",";
         asks += level;
        }
     }
   string payload = StringFormat(
      "{\"symbol\":\"%s\",\"ts\":%d,\"bids\":[%s],\"asks\":[%s]}",
      symbol, (int)TimeCurrent(), bids, asks);
   CamZMQPub("mt5.book", payload);
  }

//+------------------------------------------------------------------+
void OnTimer()
  {
   // PUB: heartbeat
   string heartbeat = StringFormat("{\"ts\":%d}", (int)TimeCurrent());
   CamZMQPub("mt5.heartbeat", heartbeat);

   // PUB: posicoes (snapshot a cada heartbeat — pode ser otimizado)
   string positions = SerializePositions();
   if(StringLen(positions) > 2)
      CamZMQPub("mt5.position", positions);

   // REP: processa um comando se chegou
   string cmd = CamZMQRecv();
   if(StringLen(cmd) > 0)
      HandleCommand(cmd);
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   // TASK-009 — PAUSE_EA suspende publicação de ticks; heartbeat segue.
   if(g_ontick_paused)
      return;

   // PUB: tick do simbolo observado (default = simbolo do grafico).
   string sym = (StringLen(g_watched_symbol) > 0 ? g_watched_symbol : Symbol());
   MqlTick tick;
   if(SymbolInfoTick(sym, tick))
     {
      string payload = StringFormat(
         "{\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,\"last\":%.5f,\"volume\":%d,\"ts_unix_ms\":%d}",
         sym, tick.bid, tick.ask, tick.last, (int)tick.volume, (int)(tick.time_msc));
      CamZMQPub("mt5.tick", payload);
     }
  }

//+------------------------------------------------------------------+
//| Helpers minimos de extracao de campo JSON (read-only, sem libs)   |
//+------------------------------------------------------------------+
string JsonGetString(const string json, const string key)
  {
   string needle = "\"" + key + "\"";
   int k = StringFind(json, needle);
   if(k < 0) return("");
   int colon = StringFind(json, ":", k);
   if(colon < 0) return("");
   int q1 = StringFind(json, "\"", colon + 1);
   if(q1 < 0) return("");
   int q2 = StringFind(json, "\"", q1 + 1);
   if(q2 < 0) return("");
   return(StringSubstr(json, q1 + 1, q2 - q1 - 1));
  }

int JsonGetInt(const string json, const string key, const int fallback)
  {
   string needle = "\"" + key + "\"";
   int k = StringFind(json, needle);
   if(k < 0) return(fallback);
   int colon = StringFind(json, ":", k);
   if(colon < 0) return(fallback);
   // pula espacos e aspas
   int i = colon + 1;
   string num = "";
   while(i < StringLen(json))
     {
      ushort c = StringGetCharacter(json, i);
      if((c >= '0' && c <= '9') || c == '-') num += ShortToString(c);
      else if(StringLen(num) > 0) break;
      i++;
     }
   if(StringLen(num) == 0) return(fallback);
   return((int)StringToInteger(num));
  }

//+------------------------------------------------------------------+
//| JsonGetLong — igual ao JsonGetInt mas retorna long (time_msc      |
//| estoura int32). Usado por GET_TICKS (from_msc).                   |
//+------------------------------------------------------------------+
long JsonGetLong(const string json, const string key, const long fallback)
  {
   string needle = "\"" + key + "\"";
   int k = StringFind(json, needle);
   if(k < 0) return(fallback);
   int colon = StringFind(json, ":", k);
   if(colon < 0) return(fallback);
   int i = colon + 1;
   string num = "";
   while(i < StringLen(json))
     {
      ushort c = StringGetCharacter(json, i);
      if((c >= '0' && c <= '9') || c == '-') num += ShortToString(c);
      else if(StringLen(num) > 0) break;
      i++;
     }
   if(StringLen(num) == 0) return(fallback);
   return(StringToInteger(num));
  }

ENUM_TIMEFRAMES TimeframeFromString(const string tf)
  {
   if(tf == "M1")  return(PERIOD_M1);
   if(tf == "M5")  return(PERIOD_M5);
   if(tf == "M15") return(PERIOD_M15);
   if(tf == "M30") return(PERIOD_M30);
   if(tf == "H1")  return(PERIOD_H1);
   if(tf == "H4")  return(PERIOD_H4);
   if(tf == "D1")  return(PERIOD_D1);
   if(tf == "W1")  return(PERIOD_W1);
   if(tf == "MN1") return(PERIOD_MN1);
   return(PERIOD_H1); // default
  }

//+------------------------------------------------------------------+
//| Serializa posicoes abertas em JSON                                |
//+------------------------------------------------------------------+
string SerializePositions()
  {
   int total = PositionsTotal();
   if(total == 0) return("[]");
   string out = "[";
   for(int i = 0; i < total; i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;
      if(i > 0) out += ",";
      out += StringFormat(
         "{\"symbol\":\"%s\",\"contracts\":%d,\"direction\":\"%s\",\"entry\":%.5f,\"current\":%.5f,\"pnl_gross\":%.2f}",
         PositionGetString(POSITION_SYMBOL),
         (int)PositionGetDouble(POSITION_VOLUME),
         (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "LONG" : "SHORT"),
         PositionGetDouble(POSITION_PRICE_OPEN),
         PositionGetDouble(POSITION_PRICE_CURRENT),
         PositionGetDouble(POSITION_PROFIT));
     }
   out += "]";
   return(out);
  }

//+------------------------------------------------------------------+
//| Whitelist de comandos read-only (CA15.3)                          |
//+------------------------------------------------------------------+
void HandleCommand(const string cmd)
  {
   string c = cmd;
   StringTrimLeft(c);
   StringTrimRight(c);

   if(StringFind(c, "PING") >= 0)
     {
      CamZMQSend("{\"status\":\"ok\",\"data\":\"PONG\"}");
      return;
     }

   if(StringFind(c, "GET_STATE") >= 0)
     {
      string resp = StringFormat(
         "{\"status\":\"ok\",\"data\":{\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f}}",
         AccountInfoDouble(ACCOUNT_BALANCE),
         AccountInfoDouble(ACCOUNT_EQUITY),
         AccountInfoDouble(ACCOUNT_MARGIN));
      CamZMQSend(resp);
      return;
     }

   if(StringFind(c, "GET_POSITIONS") >= 0)
     {
      string positions = SerializePositions();
      CamZMQSend(StringFormat("{\"status\":\"ok\",\"data\":%s}", positions));
      return;
     }

   if(StringFind(c, "GET_SYMBOL_INFO") >= 0)
     {
      string resp = StringFormat(
         "{\"status\":\"ok\",\"data\":{\"symbol\":\"%s\",\"point\":%.5f,\"tick_size\":%.5f}}",
         Symbol(),
         SymbolInfoDouble(Symbol(), SYMBOL_POINT),
         SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_SIZE));
      CamZMQSend(resp);
      return;
     }

   // TASK-009 (BL-A) — Control Plane G2: PAUSE / RESUME / GET_VERSION
   if(StringFind(c, "PAUSE_EA") >= 0)
     {
      g_ontick_paused = true;
      PrintFormat("[CamBridge] PAUSE_EA ativado — OnTick suspenso, heartbeat segue.");
      CamZMQSend("{\"status\":\"ok\",\"data\":\"PAUSED\"}");
      return;
     }

   if(StringFind(c, "RESUME_EA") >= 0)
     {
      g_ontick_paused = false;
      PrintFormat("[CamBridge] RESUME_EA — OnTick retomado.");
      CamZMQSend("{\"status\":\"ok\",\"data\":\"RESUMED\"}");
      return;
     }

   if(StringFind(c, "GET_VERSION") >= 0)
     {
      string resp = StringFormat(
         "{\"status\":\"ok\",\"data\":{\"version\":\"%s\",\"build\":\"%s\",\"magic\":%d,\"paused\":%s}}",
         CAM_BRIDGE_VERSION,
         TimeToString(__DATETIME__, TIME_DATE | TIME_MINUTES),
         InpMagicNumber,
         (g_ontick_paused ? "true" : "false"));
      CamZMQSend(resp);
      return;
     }

   // Inspetor (ADR-014) — GET_CANDLES: OHLCV historico via CopyRates (read-only)
   if(StringFind(c, "GET_CANDLES") >= 0)
     {
      HandleGetCandles(c);
      return;
     }

   // Inspetor — GET_SYMBOLS: lista de simbolos disponiveis (read-only)
   if(StringFind(c, "GET_SYMBOLS") >= 0)
     {
      HandleGetSymbols();
      return;
     }

   // Research (v0.5) — PROBE_TICKS: testa se o feed entrega flag de agressor.
   // Usa CopyTicks (traz MqlTick.flags com TICK_FLAG_BUY/SELL). Read-only.
   if(StringFind(c, "PROBE_TICKS") >= 0)
     {
      HandleProbeTicks(c);
      return;
     }

   // Dataset — GET_TICKS: ticks em BULK paginado (CopyTicks a partir de from_msc).
   // Retorna os ticks reais p/ ingestao (read-only). Vem ANTES do GET por nome.
   if(StringFind(c, "GET_TICKS") >= 0)
     {
      HandleGetTicks(c);
      return;
     }

   // Inspetor — SUBSCRIBE: passa a observar o simbolo (SymbolSelect + book)
   if(StringFind(c, "UNSUBSCRIBE") >= 0)
     {
      string sym = JsonGetString(c, "symbol");
      if(InpPublishBook && StringLen(g_watched_symbol) > 0)
         MarketBookRelease(g_watched_symbol);
      g_watched_symbol = Symbol();
      if(InpPublishBook)
         MarketBookAdd(g_watched_symbol);
      CamZMQSend(StringFormat("{\"status\":\"ok\",\"data\":\"%s\"}", g_watched_symbol));
      return;
     }
   if(StringFind(c, "SUBSCRIBE") >= 0)
     {
      string sym = JsonGetString(c, "symbol");
      if(StringLen(sym) == 0)
        {
         CamZMQSend("{\"error\":\"MISSING_SYMBOL\"}");
         return;
        }
      if(!SymbolSelect(sym, true))
        {
         CamZMQSend(StringFormat("{\"error\":\"SYMBOL_NOT_FOUND\",\"symbol\":\"%s\"}", sym));
         return;
        }
      if(InpPublishBook && StringLen(g_watched_symbol) > 0 && g_watched_symbol != sym)
         MarketBookRelease(g_watched_symbol);
      g_watched_symbol = sym;
      if(InpPublishBook)
         MarketBookAdd(g_watched_symbol);
      CamZMQSend(StringFormat("{\"status\":\"ok\",\"data\":\"%s\"}", sym));
      return;
     }

   // CA15.3 — comando fora da whitelist
   string err = StringFormat("{\"error\":\"UNAUTHORIZED_COMMAND\",\"cmd\":\"%s\"}", c);
   PrintFormat("[CamBridge] Comando rejeitado: %s", c);
   CamZMQSend(err);
  }

//+------------------------------------------------------------------+
//| GET_CANDLES — responde OHLCV via CopyRates (read-only)            |
//| req: {"cmd":"GET_CANDLES","symbol":"PETR4","timeframe":"D1",      |
//|       "count":200}                                                |
//+------------------------------------------------------------------+
void HandleGetCandles(const string cmd)
  {
   string sym = JsonGetString(cmd, "symbol");
   string tfs = JsonGetString(cmd, "timeframe");
   int    cnt = JsonGetInt(cmd, "count", 200);
   // start_pos: deslocamento a partir da barra mais recente (0 = mais recente).
   // Permite PAGINACAO: o backend pede blocos de <= InpMaxCandles com start_pos
   // crescente p/ ingerir historico longo sem estourar o heartbeat (single-thread).
   int    start_pos = JsonGetInt(cmd, "start_pos", 0);
   if(StringLen(sym) == 0) { CamZMQSend("{\"error\":\"MISSING_SYMBOL\"}"); return; }
   if(cnt < 1)   cnt = 1;
   if(cnt > InpMaxCandles) cnt = InpMaxCandles;  // protege heartbeat (ADR-014)
   if(start_pos < 0) start_pos = 0;

   SymbolSelect(sym, true);
   ENUM_TIMEFRAMES tf = TimeframeFromString(tfs);

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int got = CopyRates(sym, tf, start_pos, cnt, rates);
   if(got <= 0)
     {
      CamZMQSend(StringFormat(
         "{\"error\":\"NO_RATES\",\"symbol\":\"%s\",\"timeframe\":\"%s\"}", sym, tfs));
      return;
     }

   // monta array do mais antigo para o mais recente (lightweight-charts espera asc)
   string arr = "";
   for(int i = got - 1; i >= 0; i--)
     {
      if(StringLen(arr) > 0) arr += ",";
      arr += StringFormat(
         "{\"ts\":%d,\"o\":%.5f,\"h\":%.5f,\"l\":%.5f,\"c\":%.5f,\"v\":%d}",
         (int)rates[i].time, rates[i].open, rates[i].high,
         rates[i].low, rates[i].close, (int)rates[i].tick_volume);
     }
   string resp = StringFormat(
      "{\"status\":\"ok\",\"data\":{\"symbol\":\"%s\",\"timeframe\":\"%s\",\"candles\":[%s]}}",
      sym, tfs, arr);
   CamZMQSend(resp);
  }

//+------------------------------------------------------------------+
//| GET_SYMBOLS — lista simbolos disponiveis (read-only)             |
//+------------------------------------------------------------------+
void HandleGetSymbols()
  {
   int total = SymbolsTotal(false);
   string arr = "";
   for(int i = 0; i < total; i++)
     {
      string name = SymbolName(i, false);
      if(StringLen(name) == 0) continue;
      if(StringLen(arr) > 0) arr += ",";
      arr += "\"" + name + "\"";
     }
   CamZMQSend(StringFormat("{\"status\":\"ok\",\"data\":[%s]}", arr));
  }

//+------------------------------------------------------------------+
//| PROBE_TICKS — Research v0.5: o feed entrega flag de agressor?      |
//| req: {"cmd":"PROBE_TICKS","symbol":"WIN$","count":500}            |
//| Usa CopyTicks (COPY_TICKS_ALL) e conta quais flags vem nos ticks. |
//| Decide empiricamente se OFI/tick (Cubo Rapido) e viavel no CaM.    |
//| READ-ONLY: so leitura de historico de tick.                       |
//+------------------------------------------------------------------+
void HandleProbeTicks(const string cmd)
  {
   string sym = JsonGetString(cmd, "symbol");
   int    cnt = JsonGetInt(cmd, "count", 500);
   if(StringLen(sym) == 0) sym = g_watched_symbol;
   if(StringLen(sym) == 0) sym = Symbol();
   if(cnt < 1) cnt = 1;
   if(cnt > 5000) cnt = 5000;

   SymbolSelect(sym, true);
   MqlTick ticks[];
   // COPY_TICKS_ALL: todos os ticks (info + trade). flags revela o agressor.
   int got = CopyTicks(sym, ticks, COPY_TICKS_ALL, 0, cnt);
   if(got <= 0)
     {
      CamZMQSend(StringFormat(
         "{\"error\":\"NO_TICKS\",\"symbol\":\"%s\",\"copied\":%d}", sym, got));
      return;
     }

   int n_buy = 0, n_sell = 0, n_last = 0, n_volume = 0, n_flagged = 0;
   long first_ms = 0, last_ms = 0;
   for(int i = 0; i < got; i++)
     {
      uint f = ticks[i].flags;
      if((f & TICK_FLAG_BUY)  != 0) n_buy++;
      if((f & TICK_FLAG_SELL) != 0) n_sell++;
      if((f & TICK_FLAG_LAST) != 0) n_last++;
      if((f & TICK_FLAG_VOLUME) != 0) n_volume++;
      if(f != 0) n_flagged++;
      if(i == 0) first_ms = ticks[i].time_msc;
      last_ms = ticks[i].time_msc;
     }
   // aggressor_available = ha ticks com BUY ou SELL marcado.
   bool aggressor = (n_buy + n_sell) > 0;
   // amostra dos 3 primeiros ticks (flags crus) para inspecao manual.
   string sample = "";
   int smax = (got < 3 ? got : 3);
   for(int i = 0; i < smax; i++)
     {
      if(i > 0) sample += ",";
      sample += StringFormat(
         "{\"t_msc\":%I64d,\"last\":%.5f,\"vol\":%I64d,\"flags\":%u}",
         ticks[i].time_msc, ticks[i].last, ticks[i].volume_real > 0 ?
         (long)ticks[i].volume_real : (long)ticks[i].volume, ticks[i].flags);
     }
   string resp = StringFormat(
      "{\"status\":\"ok\",\"data\":{\"symbol\":\"%s\",\"copied\":%d,"
      "\"aggressor_available\":%s,\"n_buy\":%d,\"n_sell\":%d,\"n_last\":%d,"
      "\"n_volume\":%d,\"n_flagged\":%d,\"span_ms\":%I64d,\"sample\":[%s]}}",
      sym, got, (aggressor ? "true" : "false"),
      n_buy, n_sell, n_last, n_volume, n_flagged,
      (last_ms - first_ms), sample);
   CamZMQSend(resp);
  }

//+------------------------------------------------------------------+
//| GET_TICKS — ticks em BULK (paginado por from_msc). Retorna os     |
//| ticks reais (t_msc/bid/ask/last/v/flags) p/ ingestao do dataset.  |
//| req: {"cmd":"GET_TICKS","symbol":"WINM26","from_msc":0,"count":N} |
//| O caller pagina: proximo from_msc = last_msc + 1.                  |
//+------------------------------------------------------------------+
void HandleGetTicks(const string cmd)
  {
   string sym = JsonGetString(cmd, "symbol");
   long   from_msc = JsonGetLong(cmd, "from_msc", 0);
   int    cnt = JsonGetInt(cmd, "count", 10000);
   if(StringLen(sym) == 0) { CamZMQSend("{\"error\":\"MISSING_SYMBOL\"}"); return; }
   if(cnt < 1) cnt = 1;
   if(cnt > 20000) cnt = 20000;     // cap por requisicao (protege heartbeat)
   if(from_msc < 0) from_msc = 0;

   SymbolSelect(sym, true);
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   MqlTick ticks[];
   int got = CopyTicks(sym, ticks, COPY_TICKS_ALL, from_msc, cnt);
   if(got < 0) got = 0;

   string arr = "";
   long last_ms = from_msc;
   for(int i = 0; i < got; i++)
     {
      if(StringLen(arr) > 0) arr += ",";
      last_ms = (long)ticks[i].time_msc;
      long vol = (ticks[i].volume_real > 0) ? (long)ticks[i].volume_real
                                            : (long)ticks[i].volume;
      arr += StringFormat(
         "{\"t\":%I64d,\"bid\":%.*f,\"ask\":%.*f,\"last\":%.*f,\"v\":%I64d,\"f\":%u}",
         last_ms, dg, ticks[i].bid, dg, ticks[i].ask, dg, ticks[i].last,
         vol, ticks[i].flags);
     }
   string resp = StringFormat(
      "{\"status\":\"ok\",\"data\":{\"symbol\":\"%s\",\"ticks\":[%s],"
      "\"last_msc\":%I64d,\"count\":%d}}", sym, arr, last_ms, got);
   CamZMQSend(resp);
  }
//+------------------------------------------------------------------+

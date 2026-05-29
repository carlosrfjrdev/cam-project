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
//|                                                                   |
//| CA15.1 — NAO chama OrderSend/OrderClose/PositionOpen/PositionClose|
//| §7.1 sec — verifica conta DEMO no startup, abort se REAL          |
//+------------------------------------------------------------------+
#property copyright "CaM — The Carlos Alternative Money"
#property version   "0.3"
#property strict
#property description "CaM Bridge ZeroMQ — Read-only v0.3 (SPEC v0.4 BL-A G2)"

// TASK-009 (BL-A): Control Plane G2 — PAUSE_EA, RESUME_EA, GET_VERSION
// Estes comandos NÃO disparam OrderSend — bridge segue READ-ONLY (CA15.1).
// SUBMIT_ORDER será adicionado APENAS em cam_risk_mirror.mq5 (T025/T027 BL-E),
// nunca aqui.

#include <cam_zmq.mqh>

#define CAM_BRIDGE_VERSION "0.3.0-bla"

input int    InpPubPort = 5556;
input int    InpReqPort = 5557;
input int    InpHeartbeatMs = 1000;       // 1 msg/segundo (SPEC R12.04)
input int    InpMagicNumber = 20260525;   // distinto p/ identificar v0.2
input bool   InpRequireDemoAccount = true; // sec §7.1 — protege contra ativacao em conta real

datetime g_last_heartbeat_ms = 0;

// TASK-009 — flag de pausa: quando true, OnTick NÃO publica em mt5.tick
// (heartbeat continua via OnTimer — isso é critério CA-A.5).
bool     g_ontick_paused = false;

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

   EventSetMillisecondTimer(InpHeartbeatMs);
   Print("[CamBridge] v0.2 read-only ativo. Magic=", InpMagicNumber);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
   CamZMQShutdown();
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

   // PUB: tick atual do simbolo onde o EA esta atachado
   MqlTick tick;
   if(SymbolInfoTick(Symbol(), tick))
     {
      string payload = StringFormat(
         "{\"symbol\":\"%s\",\"bid\":%.5f,\"ask\":%.5f,\"last\":%.5f,\"volume\":%d,\"ts_unix_ms\":%d}",
         Symbol(), tick.bid, tick.ask, tick.last, (int)tick.volume, (int)(tick.time_msc));
      CamZMQPub("mt5.tick", payload);
     }
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
         (int)PositionGetInteger(POSITION_VOLUME),
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
         __DATE__ " " __TIME__,
         InpMagicNumber,
         (g_ontick_paused ? "true" : "false"));
      CamZMQSend(resp);
      return;
     }

   // CA15.3 — comando fora da whitelist
   string err = StringFormat("{\"error\":\"UNAUTHORIZED_COMMAND\",\"cmd\":\"%s\"}", c);
   PrintFormat("[CamBridge] Comando rejeitado: %s", c);
   CamZMQSend(err);
  }
//+------------------------------------------------------------------+

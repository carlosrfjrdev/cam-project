//+------------------------------------------------------------------+
//| cam_zmq.mqh                                                       |
//| Wrapper MQL5 minimo sobre libzmq.dll para a bridge CaM (SPEC v0.2)|
//|                                                                   |
//| Read-only em v0.2 — NAO expoe send_order (CA15).                  |
//| Adaptado de dwx-zeromq-connector (Darwinex) — Apache 2.0.         |
//|                                                                   |
//| Pre-requisitos no MT5:                                            |
//|   - libzmq.dll em MQL5/Libraries/                                 |
//|   - "Allow DLL imports" habilitado em Tools → Options             |
//|                                                                   |
//| Funcoes expostas:                                                 |
//|   CamZMQInit()       — inicializa contexto ZMQ                    |
//|   CamZMQPub(...)     — publica mensagem no socket PUB             |
//|   CamZMQRecv(...)    — recebe comando do socket REP               |
//|   CamZMQSend(...)    — envia resposta pelo socket REP             |
//|   CamZMQShutdown()   — limpa contexto                             |
//+------------------------------------------------------------------+
#property strict

#import "libzmq.dll"
   long  zmq_ctx_new();
   int   zmq_ctx_term(long context);
   long  zmq_socket(long context, int type);
   int   zmq_bind(long socket, string endpoint);
   int   zmq_close(long socket);
   int   zmq_send(long socket, uchar &buf[], int len, int flags);
   int   zmq_recv(long socket, uchar &buf[], int len, int flags);
   int   zmq_setsockopt(long socket, int option, uchar &value[], int length);
#import

#define ZMQ_PUB    1
#define ZMQ_REP    4
#define ZMQ_DONTWAIT 1

long  g_zmq_context = 0;
long  g_pub_socket  = 0;
long  g_rep_socket  = 0;

//+------------------------------------------------------------------+
bool CamZMQInit(const int pub_port, const int rep_port)
  {
   g_zmq_context = zmq_ctx_new();
   if(g_zmq_context == 0)
      return(false);

   g_pub_socket = zmq_socket(g_zmq_context, ZMQ_PUB);
   if(g_pub_socket == 0)
      return(false);
   string pub_endpoint = StringFormat("tcp://*:%d", pub_port);
   if(zmq_bind(g_pub_socket, pub_endpoint) != 0)
      return(false);

   g_rep_socket = zmq_socket(g_zmq_context, ZMQ_REP);
   if(g_rep_socket == 0)
      return(false);
   string rep_endpoint = StringFormat("tcp://*:%d", rep_port);
   if(zmq_bind(g_rep_socket, rep_endpoint) != 0)
      return(false);

   Print("[CamZMQ] Bridge inicializada — PUB:", pub_port, " REP:", rep_port);
   return(true);
  }

//+------------------------------------------------------------------+
bool CamZMQPub(const string topic, const string payload)
  {
   if(g_pub_socket == 0) return(false);

   string full = topic + " " + payload;
   uchar buf[];
   StringToCharArray(full, buf, 0, StringLen(full));
   int sent = zmq_send(g_pub_socket, buf, ArraySize(buf) - 1, ZMQ_DONTWAIT);
   return(sent > 0);
  }

//+------------------------------------------------------------------+
string CamZMQRecv(const int max_len = 8192)
  {
   if(g_rep_socket == 0) return("");

   uchar buf[8192];
   int n = zmq_recv(g_rep_socket, buf, max_len, ZMQ_DONTWAIT);
   if(n <= 0) return("");
   return(CharArrayToString(buf, 0, n));
  }

//+------------------------------------------------------------------+
bool CamZMQSend(const string payload)
  {
   if(g_rep_socket == 0) return(false);
   uchar buf[];
   StringToCharArray(payload, buf, 0, StringLen(payload));
   return(zmq_send(g_rep_socket, buf, ArraySize(buf) - 1, 0) > 0);
  }

//+------------------------------------------------------------------+
void CamZMQShutdown()
  {
   if(g_pub_socket != 0) { zmq_close(g_pub_socket); g_pub_socket = 0; }
   if(g_rep_socket != 0) { zmq_close(g_rep_socket); g_rep_socket = 0; }
   if(g_zmq_context != 0) { zmq_ctx_term(g_zmq_context); g_zmq_context = 0; }
   Print("[CamZMQ] Bridge encerrada.");
  }

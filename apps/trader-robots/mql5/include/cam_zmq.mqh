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
   // endpoint como uchar[] (UTF-8/ANSI). MQL5 passa `string` como UTF-16 (wchar_t*),
   // incompativel com o `const char*` esperado pela libzmq C — por isso uchar[].
   int   zmq_bind(long socket, uchar &endpoint[]);
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
// Converte endpoint para uchar[] UTF-8/ANSI terminado em null (C string).
void CamZMQEndpoint(const string ep, uchar &out[])
  {
   StringToCharArray(ep, out, 0, StringLen(ep) + 1, CP_UTF8);
  }

bool CamZMQInit(const int pub_port, const int rep_port)
  {
   g_zmq_context = zmq_ctx_new();
   if(g_zmq_context == 0)
     { Print("[CamZMQ] FALHA: zmq_ctx_new retornou 0"); return(false); }

   g_pub_socket = zmq_socket(g_zmq_context, ZMQ_PUB);
   if(g_pub_socket == 0)
     { Print("[CamZMQ] FALHA: zmq_socket(PUB) retornou 0"); return(false); }
   uchar pub_ep[];
   CamZMQEndpoint(StringFormat("tcp://*:%d", pub_port), pub_ep);
   if(zmq_bind(g_pub_socket, pub_ep) != 0)
     { Print("[CamZMQ] FALHA: zmq_bind(PUB) tcp://*:", pub_port); return(false); }

   g_rep_socket = zmq_socket(g_zmq_context, ZMQ_REP);
   if(g_rep_socket == 0)
     { Print("[CamZMQ] FALHA: zmq_socket(REP) retornou 0"); return(false); }
   uchar rep_ep[];
   CamZMQEndpoint(StringFormat("tcp://*:%d", rep_port), rep_ep);
   if(zmq_bind(g_rep_socket, rep_ep) != 0)
     { Print("[CamZMQ] FALHA: zmq_bind(REP) tcp://*:", rep_port); return(false); }

   Print("[CamZMQ] Bridge inicializada — PUB:", pub_port, " REP:", rep_port);
   return(true);
  }

//+------------------------------------------------------------------+
bool CamZMQPub(const string topic, const string payload)
  {
   if(g_pub_socket == 0) return(false);

   string full = topic + " " + payload;
   uchar buf[];
   // WHOLE_ARRAY + CP_UTF8: copia a string + null e retorna a contagem COM o null.
   // len = bytes reais sem o null (corrige o off-by-one que dropava o ultimo char).
   int len = StringToCharArray(full, buf, 0, WHOLE_ARRAY, CP_UTF8) - 1;
   if(len < 0) len = 0;
   int sent = zmq_send(g_pub_socket, buf, len, ZMQ_DONTWAIT);
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
   // len = bytes reais sem o null (corrige off-by-one que truncava a resposta,
   // ex.: o `}` final do JSON de GET_CANDLES — causava JSONDecodeError no backend).
   int len = StringToCharArray(payload, buf, 0, WHOLE_ARRAY, CP_UTF8) - 1;
   if(len < 0) len = 0;
   return(zmq_send(g_rep_socket, buf, len, 0) > 0);
  }

//+------------------------------------------------------------------+
void CamZMQShutdown()
  {
   if(g_pub_socket != 0) { zmq_close(g_pub_socket); g_pub_socket = 0; }
   if(g_rep_socket != 0) { zmq_close(g_rep_socket); g_rep_socket = 0; }
   if(g_zmq_context != 0) { zmq_ctx_term(g_zmq_context); g_zmq_context = 0; }
   Print("[CamZMQ] Bridge encerrada.");
  }

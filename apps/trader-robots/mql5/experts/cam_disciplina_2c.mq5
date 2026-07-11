//+------------------------------------------------------------------+
//|  cam_disciplina_2c.mq5                                            |
//|  CaM — Robo EXECUTOR DE DISCIPLINA (2 contratos)                  |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  NAO decide ENTRADA. O trader (Carlos) entra na MAO — a edge dele |
//|  esta na leitura de entrada. Este robo IMPOE A SAIDA DISCIPLINADA |
//|  e os guard-rails, tirando o emocional (que e onde ele perde:     |
//|  corta o vencedor cedo e arrisca ~100 p/ tirar ~50).             |
//|                                                                   |
//|  ====================  COMO ELE GERENCIA  ======================  |
//|  Ao detectar uma posicao aberta (manual, magic 0) no simbolo:     |
//|    - PERNA 1 (InpLeg1_Contratos): sai no ALVO CURTO (InpAlvo1) —  |
//|      mata a ansiedade, trava o scalp que ele gosta.               |
//|    - PERNA 2 (resto): quando a P1 realiza, o STOP vai a BREAKEVEN |
//|      e a posicao CORRE com trailing ate o ALVO LONGO (InpAlvo2).  |
//|    - STOP inicial unico (InpStop) protege as 2 pernas ate a P1.   |
//|                                                                   |
//|  =====================  GUARD-RAILS  ===========================  |
//|    - Janela de NAO-OPERAR (ex.: 09:00-09:30 e o leilao/ruido que  |
//|      mais sangra): posicao aberta nela e ENCERRADA na hora.        |
//|    - MAX OPS/DIA: acima do limite, novas posicoes sao encerradas. |
//|    - STOP DIARIO (R$): atingido, encerra e bloqueia o resto do dia.|
//|    - FLAT no fim do pregao (sem overnight).                        |
//|                                                                   |
//|  Numeros (stop/alvos) sao PARAMETROS — calibrados pelo motor      |
//|  estatistico do CAM (MAE/MFE x regime). Defaults provisorios.     |
//|                                                                   |
//|  =========================  ATENCAO  ===========================  |
//|  - DEMO-only por default (guard-rail). Liberar real e decisao do  |
//|    Founder apos paridade (POLITICA-ROBOS.md).                     |
//|  - Assume conta NETTING (WIN/WDO): 1 posicao de volume N.          |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.1"
#property strict
#property description "CaM Disciplina 2C — gestor de saida disciplinada p/ entradas manuais. DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_DISC_VERSION "0.1.0"

//================== BRACKET — 2 pernas (PARAMETROS do motor) ========
input group "Bracket (calibrar pelo motor MAE/MFE x regime)"
input double InpStop_Pts        = 80.0;   // Stop inicial (pts) — protege as 2 pernas
input double InpAlvo1_Pts       = 100.0;  // Alvo da PERNA 1 (curto) — realiza o scalp
input double InpAlvo2_Pts       = 300.0;  // Alvo da PERNA 2 (runner) — deixa correr
input double InpTrail_Pts       = 80.0;   // Trailing da P2 apos breakeven (0 = desligado)
input int    InpLeg1_Contratos  = 1;      // Contratos da PERNA 1 (resto = PERNA 2)
input double InpBreakeven_Offset_Pts = 0.0; // Offset do breakeven da P2 (entrada +/- offset)

//================== GUARD-RAILS ====================================
input group "Guard-rails (disciplina)"
input bool   InpEnforce         = true;   // Encerrar posicoes que violam os guard-rails
input int    InpMaxOpsDia       = 10;     // Maximo de operacoes encerradas por dia (0 = sem limite)
input double InpStopDiario_BRL  = 300.0;  // Perda maxima do dia em R$ (0 = sem stop diario)
input string InpNaoOperar_Ini   = "09:00";// Janela de NAO-operar — inicio (HH:MM, vazio = off)
input string InpNaoOperar_Fim   = "09:30";// Janela de NAO-operar — fim (HH:MM)
input int    InpFechamento_Hora = 17;     // Flat (zera) a partir desta hora
input int    InpFechamento_Min  = 55;     // Flat — minuto

//================== EXECUCAO / SEGURANCA ===========================
input group "Execucao / Seguranca"
input long   InpMagicNumber     = 20260630;// Identificador do robo (ordens proprias)
input ulong  InpDesvioMax_Pts   = 10;     // Desvio maximo no preenchimento (pontos)
input bool   InpGerenciarSomenteManual = true; // So gerencia posicao manual (magic 0)
input bool   InpExigirContaDemo = true;   // So inicia em conta DEMO

CTrade   g_trade;

//--- Estado da gestao
bool     g_managing   = false;
bool     g_is_long    = false;
double   g_entry      = 0.0;
double   g_init_vol   = 0.0;
bool     g_leg1_done  = false;
double   g_max_favor  = 0.0;   // melhor preco a favor desde a entrada (trailing P2)
string   g_session    = "";
bool     g_blocked    = false; // dia bloqueado (stop diario batido)

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpExigirContaDemo)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamDisc2C] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpDesvioMax_Pts);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   PrintFormat("[CamDisc2C] %s ativo. Symbol=%s stop=%.0f alvo1=%.0f alvo2=%.0f "
               "trail=%.0f leg1=%d maxOps=%d stopDia=%.0f.",
               CAM_DISC_VERSION, _Symbol, InpStop_Pts, InpAlvo1_Pts, InpAlvo2_Pts,
               InpTrail_Pts, InpLeg1_Contratos, InpMaxOpsDia, InpStopDiario_BRL);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
//| OnTick — gestao roda a CADA tick (breakeven/trailing precisam     |
//| reagir intrabar, nao so no fechamento de barra).                  |
//+------------------------------------------------------------------+
void OnTick()
  {
   // reset diario por data de sessao
   string sess = SessionDate(TimeCurrent());
   if(sess != g_session)
     {
      g_session = sess;
      g_blocked = false;
     }

   // flat compulsorio no fim do pregao
   if(MinutesOfDay(TimeCurrent()) >= InpFechamento_Hora * 60 + InpFechamento_Min)
     {
      if(HasManagedPosition())
         ClosePosition("flat fim de pregao");
      return;
     }

   bool has = HasManagedPosition();

   // posicao nova detectada -> aplica guard-rails de ENTRADA + arma o bracket
   if(has && !g_managing)
     {
      OnNewPosition();
      return;
     }
   // gerenciando -> conduz as 2 pernas
   if(has && g_managing)
     {
      ManagePosition();
      return;
     }
   // posicao sumiu -> encerra o ciclo de gestao
   if(!has && g_managing)
      g_managing = false;

   // stop diario: bate -> bloqueia o resto do dia
   if(!g_blocked && InpStopDiario_BRL > 0 && RealizedTodayBRL() <= -InpStopDiario_BRL)
     {
      g_blocked = true;
      PrintFormat("[CamDisc2C] STOP DIARIO atingido (R$ %.2f). Bloqueando o dia.",
                  RealizedTodayBRL());
     }
  }

//+------------------------------------------------------------------+
//| Posicao recem-aberta: valida guard-rails; se ok, arma o bracket.  |
//+------------------------------------------------------------------+
void OnNewPosition()
  {
   if(!PositionSelect(_Symbol))
      return;

   // ---- guard-rails de bloqueio (encerra a posicao se violar) ----
   string motivo = "";
   if(g_blocked)
      motivo = "dia bloqueado (stop diario)";
   else if(InNoTradeWindow(TimeCurrent()))
      motivo = "janela de nao-operar";
   else if(InpMaxOpsDia > 0 && OpsToday() >= InpMaxOpsDia)
      motivo = "max ops/dia atingido";

   if(motivo != "")
     {
      if(InpEnforce)
        {
         ClosePosition(motivo);
         PrintFormat("[CamDisc2C] Entrada BLOQUEADA (%s) — posicao encerrada.", motivo);
        }
      else
         PrintFormat("[CamDisc2C] Entrada violou guard-rail (%s) — Enforce off.", motivo);
      return;
     }

   // ---- arma o bracket sobre a posicao manual ----
   g_is_long   = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
   g_entry     = PositionGetDouble(POSITION_PRICE_OPEN);
   g_init_vol  = PositionGetDouble(POSITION_VOLUME);
   g_leg1_done = false;
   g_max_favor = g_entry;

   double sl = g_is_long ? g_entry - InpStop_Pts : g_entry + InpStop_Pts;
   double tp = g_is_long ? g_entry + InpAlvo2_Pts : g_entry - InpAlvo2_Pts; // runner
   if(!g_trade.PositionModify(_Symbol, NormTick(sl), NormTick(tp)))
      PrintFormat("[CamDisc2C] Falha ao armar SL/TP ret=%d (%s).",
                  g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
   g_managing = true;
   PrintFormat("[CamDisc2C] Bracket armado: %s vol=%.0f entry=%.1f SL=%.1f TP=%.1f.",
               (g_is_long ? "LONG" : "SHORT"), g_init_vol, g_entry, sl, tp);
  }

//+------------------------------------------------------------------+
//| Conduz as 2 pernas: P1 no alvo curto -> breakeven; P2 trailing.   |
//+------------------------------------------------------------------+
void ManagePosition()
  {
   if(!PositionSelect(_Symbol))
      return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double price_favor = g_is_long ? bid : ask; // preco que mede o lucro corrente

   // PERNA 1: realiza parcial no alvo curto e move o stop a breakeven.
   if(!g_leg1_done)
     {
      double alvo1 = g_is_long ? g_entry + InpAlvo1_Pts : g_entry - InpAlvo1_Pts;
      bool hit1 = g_is_long ? (price_favor >= alvo1) : (price_favor <= alvo1);
      if(hit1)
        {
         double leg1 = NormalizarVolume((double)InpLeg1_Contratos);
         double cur  = PositionGetDouble(POSITION_VOLUME);
         if(leg1 > 0 && leg1 < cur)
            g_trade.PositionClosePartial(_Symbol, leg1);
         g_leg1_done = true;
         double be = g_is_long ? g_entry + InpBreakeven_Offset_Pts
                               : g_entry - InpBreakeven_Offset_Pts;
         double tp = PositionGetDouble(POSITION_TP);
         g_trade.PositionModify(_Symbol, NormTick(be), tp);
         g_max_favor = price_favor;
         PrintFormat("[CamDisc2C] PERNA 1 realizada no alvo %.1f; P2 a breakeven %.1f.",
                     alvo1, be);
        }
      return;
     }

   // PERNA 2: trailing apos breakeven (SL so anda a favor, nunca abaixo do BE).
   if(InpTrail_Pts > 0)
      TrailLeg2(bid, ask);
  }

//+------------------------------------------------------------------+
//| Trailing da PERNA 2: segue o pico a InpTrail_Pts, so a favor.     |
//+------------------------------------------------------------------+
void TrailLeg2(double bid, double ask)
  {
   if(!PositionSelect(_Symbol))
      return;
   double cur_sl = PositionGetDouble(POSITION_SL);
   double cur_tp = PositionGetDouble(POSITION_TP);
   double be = g_is_long ? g_entry + InpBreakeven_Offset_Pts
                         : g_entry - InpBreakeven_Offset_Pts;
   double new_sl = cur_sl;

   if(g_is_long)
     {
      g_max_favor = MathMax(g_max_favor, bid);
      double cand = NormTick(g_max_favor - InpTrail_Pts);
      if(cand > cur_sl && cand >= NormTick(be))
         new_sl = cand;
     }
   else
     {
      if(g_max_favor <= 0.0) g_max_favor = ask;
      g_max_favor = MathMin(g_max_favor, ask);
      double cand = NormTick(g_max_favor + InpTrail_Pts);
      if((cur_sl <= 0.0 || cand < cur_sl) && cand <= NormTick(be))
         new_sl = cand;
     }
   if(new_sl != cur_sl)
      g_trade.PositionModify(_Symbol, new_sl, cur_tp);
  }

//+------------------------------------------------------------------+
//| Posicao gerenciavel neste simbolo? (manual = magic 0, conforme    |
//| InpGerenciarSomenteManual; senao tambem aceita a propria magic).  |
//+------------------------------------------------------------------+
bool HasManagedPosition()
  {
   if(!PositionSelect(_Symbol))
      return false;
   long magic = PositionGetInteger(POSITION_MAGIC);
   if(InpGerenciarSomenteManual)
      return (magic == 0 || magic == InpMagicNumber);
   return true;
  }

void ClosePosition(string motivo)
  {
   if(g_trade.PositionClose(_Symbol))
      PrintFormat("[CamDisc2C] Posicao encerrada (%s).", motivo);
   g_managing = false;
  }

//+------------------------------------------------------------------+
//| Janela de NAO-operar (HH:MM-HH:MM). Vazio = desligado.            |
//+------------------------------------------------------------------+
bool InNoTradeWindow(datetime t)
  {
   int ini = ParseHHMM(InpNaoOperar_Ini);
   int fim = ParseHHMM(InpNaoOperar_Fim);
   if(ini < 0 || fim < 0)
      return false;
   int tod = MinutesOfDay(t);
   return (tod >= ini && tod < fim);
  }

int ParseHHMM(string s)
  {
   if(StringLen(s) < 4)
      return -1;
   int pos = StringFind(s, ":");
   if(pos <= 0)
      return -1;
   int hh = (int)StringToInteger(StringSubstr(s, 0, pos));
   int mm = (int)StringToInteger(StringSubstr(s, pos + 1));
   return hh * 60 + mm;
  }

//+------------------------------------------------------------------+
//| Operacoes encerradas HOJE (deals de saida do simbolo).            |
//+------------------------------------------------------------------+
int OpsToday()
  {
   datetime ini = StartOfDay(TimeCurrent());
   if(!HistorySelect(ini, TimeCurrent()))
      return 0;
   int n = 0;
   int total = HistoryDealsTotal();
   for(int i = 0; i < total; i++)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0) continue;
      if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol) continue;
      if(HistoryDealGetInteger(ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
         n++;
     }
   return n;
  }

//+------------------------------------------------------------------+
//| Resultado REALIZADO hoje em R$ (lucro+swap+comissao dos deals).   |
//+------------------------------------------------------------------+
double RealizedTodayBRL()
  {
   datetime ini = StartOfDay(TimeCurrent());
   if(!HistorySelect(ini, TimeCurrent()))
      return 0.0;
   double total = 0.0;
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0) continue;
      if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol) continue;
      total += HistoryDealGetDouble(ticket, DEAL_PROFIT)
             + HistoryDealGetDouble(ticket, DEAL_SWAP)
             + HistoryDealGetDouble(ticket, DEAL_COMMISSION);
     }
   return total;
  }

datetime StartOfDay(datetime t)
  {
   MqlDateTime st;
   TimeToStruct(t, st);
   st.hour = 0; st.min = 0; st.sec = 0;
   return StructToTime(st);
  }

//+------------------------------------------------------------------+
//| Helpers compartilhados (mesma semantica dos demais EAs do CaM).   |
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

double NormTick(double price)
  {
   if(price <= 0.0)
      return 0.0;
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts <= 0.0)
      ts = _Point;
   return NormalizeDouble(MathRound(price / ts) * ts, _Digits);
  }

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

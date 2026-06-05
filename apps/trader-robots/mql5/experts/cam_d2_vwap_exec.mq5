//+------------------------------------------------------------------+
//|  cam_d2_vwap_exec.mq5                                             |
//|  CaM StrategyLab — Estrategia D2 "VWAP fade" — EA EXECUTOR        |
//|                                                                   |
//|  ========================  O QUE E ESTE EA  ====================  |
//|  Robo que OPERA (envia ordens) a estrategia D2 — uma estrategia   |
//|  de REVERSAO A MEDIA, pensada para mercado LATERAL (o oposto do   |
//|  ORB-30, que e de tendencia). E o par "executor" da D2:           |
//|    - cam_d2_vwap.mq5      -> GRAVADOR (nao opera; ledger/paridade).|
//|    - cam_d2_vwap_exec.mq5 -> EXECUTOR (ESTE): manda ordem a mercado|
//|                                                                   |
//|  ===================  A ESTRATEGIA D2 (VWAP fade)  ============== |
//|  "Fade" (operar CONTRA) a esticada do preco em relacao ao VWAP:   |
//|    1) Calcula o VWAP (preco medio ponderado por volume) e o desvio|
//|       padrao (sigma) ACUMULADOS na sessao, resetando a cada dia.  |
//|    2) Quando o preco estica ACIMA de VWAP + K*sigma -> VENDE       |
//|       (aposta que volta); quando estica ABAIXO de VWAP - K*sigma   |
//|       -> COMPRA. Um trade por excursao.                           |
//|    3) ALVO no VWAP (a media para onde o preco tende a voltar);     |
//|       STOP alem de K_stop*sigma. Sem runner. Flat no fim do dia.  |
//|  Tese: sem choque macro, o preco intradia oscila em torno do VWAP;|
//|  esticadas de 2-2.5 sigma sao insustentaveis e revertem. GANHA do |
//|  momentum tardio que persegue a extensao. (Frageil a NOTICIA: o   |
//|  desvio informacional vira continuacao -> use com filtro de       |
//|  evento / regime, ver EA hibrido.)                                |
//|                                                                   |
//|  =========================  ATENCAO  ===========================  |
//|  VALORES BRUTOS (sem custo/IR). SEM Risk Engine. Unica trava:     |
//|  guard-rail DEMO. Na allowlist do lint_mql5 (envia ordem).        |
//+------------------------------------------------------------------+
#property copyright "CaM — Cockpit de gestao de ativos"
#property version   "0.2"
#property strict
#property description "CaM D2 VWAP fade — robo executor (reversao a media). DEMO-only."

#include <Trade/Trade.mqh>

#define CAM_D2_EXEC_VERSION "0.2.0"

//================== ESTRATEGIA (fade em torno do VWAP) ==============
input group "Estrategia — VWAP fade"
input double InpFade_KSigma         = 2.0;    // Faz fade quando o preco estica K x sigma do VWAP (entrada)
input double InpStop_KSigma         = 3.0;    // Stop alem de K x sigma do VWAP (alvo = proprio VWAP)
input int    InpWarmup_Barras       = 30;     // Barras minimas na sessao antes de operar (sigma confiavel)

//================== SESSAO (horario do grafico) ====================
input group "Sessao (horario do grafico)"
input int    InpAbertura_Hora       = 9;      // Abertura do pregao — hora
input int    InpAbertura_Min        = 0;      // Abertura do pregao — minuto
input int    InpEntradaAte_Hora     = 17;     // Nao abre nova posicao apos esta hora
input int    InpEntradaAte_Min      = 0;      // Nao abre nova posicao apos este minuto
input int    InpFechamento_Hora     = 17;     // Zera posicao (flat) a partir desta hora
input int    InpFechamento_Min      = 55;     // Zera posicao (flat) a partir deste minuto

//================== EXECUCAO =======================================
input group "Execucao"
input double InpContratos           = 1.0;    // QUANTIDADE DE CONTRATOS por ordem (WDO/WIN: 1 = 1 contrato)
input long   InpMagicNumber         = 20260604;// Identificador do robo
input ulong  InpDesvioMax_Pts       = 10;     // Desvio maximo no preenchimento (pontos)

//================== SEGURANCA ======================================
input group "Seguranca"
input bool   InpExigirContaDemo     = true;   // So inicia em conta DEMO

CTrade   g_trade;
string   g_session    = "";
double   g_sum_pv=0.0, g_sum_v=0.0, g_sum_pv2=0.0;
int      g_n=0;
bool     g_armed_long=true, g_armed_short=true;
datetime g_last_bar=0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpExigirContaDemo)
     {
      ENUM_ACCOUNT_TRADE_MODE mode =
         (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
      if(mode != ACCOUNT_TRADE_MODE_DEMO)
        {
         PrintFormat("[CamD2Exec] ABORTANDO: conta nao e DEMO (mode=%d).", mode);
         return(INIT_FAILED);
        }
     }
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpDesvioMax_Pts);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   PrintFormat("[CamD2Exec] %s ativo. Symbol=%s Contratos=%.2f.",
               CAM_D2_EXEC_VERSION, _Symbol, InpContratos);

   // Diagnostico de VOLUME/MARGEM (ver cam_d1_orb30_exec): explica "acima de N
   // contratos nao opera" = falta de margem (NO_MONEY) ou volume max do simbolo.
   double margem = MargemPorContrato();
   double livre  = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   int    afordavel = (margem > 0.0) ? (int)MathFloor(livre / margem) : -1;
   PrintFormat("[CamD2Exec] Volume do simbolo: min=%.2f max=%.2f step=%.2f.",
               SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN),
               SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX),
               SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP));
   PrintFormat("[CamD2Exec] Margem/contrato=%.2f | margem livre=%.2f | "
               "MAX AFORDAVEL ~%d contratos.", margem, livre, afordavel);
   if(afordavel >= 0 && InpContratos > afordavel)
      PrintFormat("[CamD2Exec] ATENCAO: InpContratos=%.2f acima do afordavel (~%d); "
                  "ordens vao FALHAR por falta de margem.", InpContratos, afordavel);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur == g_last_bar) return;
   g_last_bar = cur;
   datetime t = iTime(_Symbol, _Period, 1);
   if(t == 0) return;
   ProcessBar(t, iHigh(_Symbol,_Period,1), iLow(_Symbol,_Period,1),
              iClose(_Symbol,_Period,1), (double)iVolume(_Symbol,_Period,1));
  }

//+------------------------------------------------------------------+
void ProcessBar(datetime t, double h, double l, double c, double vol)
  {
   string session = SessionDate(t);
   if(session != g_session)
     {
      g_session = session;
      g_sum_pv=0.0; g_sum_v=0.0; g_sum_pv2=0.0; g_n=0;
      g_armed_long=true; g_armed_short=true;
     }

   // VWAP/sigma cumulativos da sessao (typical=(h+l+c)/3, ponderado por volume).
   double tp = (h + l + c) / 3.0;
   double v  = (vol > 0.0) ? vol : 1.0;
   g_sum_pv += tp*v; g_sum_v += v; g_sum_pv2 += tp*tp*v; g_n++;

   int tod = MinutesOfDay(t);
   int s_close = InpFechamento_Hora*60 + InpFechamento_Min;
   // flat compulsorio no fim da sessao (sem overnight).
   if(tod >= s_close)
     {
      if(HasPosition()) g_trade.PositionClose(_Symbol);
      return;
     }

   int beg = InpAbertura_Hora*60 + InpAbertura_Min;
   int cut = InpEntradaAte_Hora*60 + InpEntradaAte_Min;
   if(tod < beg || tod >= cut) return;
   if(g_n < InpWarmup_Barras || g_sum_v <= 0.0) return;

   double vwap = g_sum_pv/g_sum_v;
   double var  = MathMax(0.0, g_sum_pv2/g_sum_v - vwap*vwap);
   double sg   = MathSqrt(var);
   if(sg <= 0.0) return;

   double ue = vwap + InpFade_KSigma*sg;   // banda superior de entrada
   double le = vwap - InpFade_KSigma*sg;   // banda inferior de entrada

   // re-arma quando o preco volta pra dentro da banda (1 trade por excursao).
   if(c >= le && c <= ue)
     { g_armed_long=true; g_armed_short=true; return; }

   if(HasPosition()) return;

   double lote = NormalizarVolume(InpContratos);
   // FADE a mercado. ALVO = VWAP; STOP = VWAP +- K_stop*sigma (congelados).
   if(g_armed_short && c > ue)            // esticou pra cima -> VENDE
     {
      g_armed_short=false;
      double sl=NormTick(vwap + InpStop_KSigma*sg), tpx=NormTick(vwap);
      if(!g_trade.Sell(lote, _Symbol, 0.0, sl, tpx, "cam_d2_exec"))
         LogFalha("Venda", lote);
     }
   else if(g_armed_long && c < le)        // esticou pra baixo -> COMPRA
     {
      g_armed_long=false;
      double sl=NormTick(vwap - InpStop_KSigma*sg), tpx=NormTick(vwap);
      if(!g_trade.Buy(lote, _Symbol, 0.0, sl, tpx, "cam_d2_exec"))
         LogFalha("Compra", lote);
     }
  }

//+------------------------------------------------------------------+
//| Margem exigida por 1 contrato (diagnostico de "nao opera").       |
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
   PrintFormat("[CamD2Exec] %s falhou ret=%d (%s). lote=%.2f margem_exigida=%.2f "
               "margem_livre=%.2f. Se NO_MONEY: reduza InpContratos ou aumente "
               "o capital.", lado, g_trade.ResultRetcode(),
               g_trade.ResultRetcodeDescription(), lote, margem_op,
               AccountInfoDouble(ACCOUNT_MARGIN_FREE));
  }

//+------------------------------------------------------------------+
bool HasPosition()
  {
   if(!PositionSelect(_Symbol)) return false;
   return (PositionGetInteger(POSITION_MAGIC) == InpMagicNumber);
  }

double NormTick(double price)
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts <= 0.0) ts = _Point;
   return NormalizeDouble(MathRound(price/ts)*ts, _Digits);
  }

int MinutesOfDay(datetime t){ MqlDateTime s; TimeToStruct(t,s); return s.hour*60+s.min; }
string SessionDate(datetime t){ MqlDateTime s; TimeToStruct(t,s);
   return StringFormat("%04d-%02d-%02d", s.year, s.mon, s.day); }
//+------------------------------------------------------------------+

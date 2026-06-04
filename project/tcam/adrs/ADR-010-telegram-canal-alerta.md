---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-010 — Telegram como Canal Externo de Alerta Independente do Cockpit

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-010-telegram-canal-alerta.md`

---

## 1. Contexto

O CaM precisa de um canal de alerta que funcione **independentemente** da UI do cockpit. Se o frontend estiver fechado, se o browser travar, se Carlos não estiver olhando o dashboard — alertas críticos (kill switch ativado, limite de loss atingido, DARF atrasada, falha técnica com posição aberta) precisam chegar até o operador de outra forma.

O canal deve:
- funcionar quando o frontend não está aberto
- ser gratuito e não requerer infraestrutura adicional
- ser acessível no celular de Carlos em qualquer lugar
- ter latência suficientemente baixa para alertas operacionais (segundos, não minutos)
- ser independente do cockpit (falha do backend não impede alerta de ser enfileirado)

---

## 2. Decisão

Telegram Bot é o canal oficial de alertas externos do CaM Cockpit.

**Implementação:** `cam/features/notifications/` com `python-telegram-bot` (ou `aiogram`).

**Eventos que disparam alerta Telegram:**

| Evento | Urgência | Conteúdo do alerta |
|---|---|---|
| KillSwitchActivated | Crítico | Motivo + timestamp + P&L do dia |
| DailyLossLimitReached (3%) | Crítico | Valor perdido + pregão encerrado |
| WeeklyLossLimitReached (7%) | Crítico | Acumulado semanal |
| MonthlyLossLimitReached (15%) | Crítico | Fase congelada + instruções |
| GainLockReached (2%) | Informativo | P&L líquido + pregão encerrado |
| DarfOverdue | Urgente | Mês vencido + operação bloqueada |
| DarfDueSoon | Aviso | N dias para vencimento |
| TradeCompleted | Informativo | Ativo + resultado líquido |
| TechnicalFailureWithOpenPosition | Crítico | Art. 19º — posição aberta sem cobertura |
| AIAnalysisReady | Informativo | Resumo pós-mercado |

**Segurança do bot:**
- Token de bot privado (não exposto no código — `.env`)
- Validação de `chat_id` do operador (somente Carlos recebe mensagens)
- Comandos de bot (`/killswitch`, `/status`) requerem validação de `chat_id`
- Confirmação dupla para ações que alteram estado (desativar kill switch via Telegram)

**Resiliência:**
- Alertas críticos enfileirados em banco local se Telegram estiver indisponível
- Re-tentativa com backoff exponencial
- Falha de entrega do Telegram **não desbloqueia operação** — o cockpit permanece no estado em que está

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | WhatsApp Business API | Custo por mensagem; integração mais complexa; aprovação necessária do Meta |
| 2 | E-mail | Latência alta para alertas operacionais (minutos vs. segundos); não acessível durante pregão sem abrir cliente de e-mail |
| 3 | Push notification (Firebase) | Requer app mobile ou PWA instalado; dependência de serviço cloud adicional; viola princípio de localidade absoluta |
| 4 | SMS | Custo por mensagem; sem API gratuita confiável; encoding limitado |
| 5 | Alertas apenas no frontend (sem canal externo) | Se o frontend não estiver aberto, alertas críticos não chegam ao operador — risco inaceitável |

---

## 4. Consequências

### Positivas
- Gratuito — custo zero de mensagem
- Carlos já usa Telegram — sem onboarding
- Biblioteca Python madura (`python-telegram-bot` ou `aiogram`)
- Funciona em qualquer lugar com internet no celular
- Pode servir como segundo canal do kill switch (comando `/killswitch` pelo Telegram)

### Negativas
- Requer internet — se Carlos estiver sem internet, alertas não chegam (mas o cockpit local ainda funciona)
- Token de bot deve ser protegido — vazamento permite que terceiros enviem mensagens ao bot
- Telegram pode ter indisponibilidades pontuais (mitigado por enfileiramento local)

### Neutras
- O canal Telegram é **adicional** ao frontend — não substitui o kill switch do dashboard

---

## 5. Custo de Reversão

**Baixo** — Telegram é um canal de alerta isolado. Trocar para outro canal (e-mail, outro app de mensagem) exige apenas mudar a implementação em `features/notifications/` sem impacto em outras features.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §4.5 (fluxo de alertas)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §5
- Constituição: Art. 18º (kill switch), Art. 19º (posição sem cobertura)
- ADRs relacionadas: ADR-006 (IA sem autoridade — analista pós-mercado envia via Telegram)

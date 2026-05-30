---
template: ADR
phase: ARCH
status: Superseded-in-part
---

# ADR-008 — Integração ~~Profit~~ **MetaTrader 5** Faseada (F1 → F5)

> ⚠️ **ATUALIZADA (soft-stage, 2026-05-30).** O broker é **MetaTrader 5**, não
> Profit (ver ADR-001 supersedida). O **princípio de faseamento sequencial
> permanece válido** (cada camada só avança quando a anterior é estável; falha
> degrada para "não opera"). Releitura dos termos: "Profit" → MT5; "NTSL" → MQL5
> EAs; "ProfitDLL/ctypes" → **bridge ZeroMQ** (`cam_bridge.mq5` read-only +
> `cam_risk_mirror.mq5`), com o `MetaTrader5` package nativo como opção futura
> (Windows). Soft-stage (pré-v1) — sem ADR HARD.
> SSoT: [`../../STACK-CAM-OFICIAL.md`](../../STACK-CAM-OFICIAL.md) §6.1.

> **Data:** 2026-05-24 · **Atualizada:** 2026-05-30
> **Status:** Superseded-in-part (princípio mantido; broker = MT5)
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-008-integracao-profit-faseada.md`

---

## 1. Contexto

O CaM Cockpit é o cockpit de governança; o Profit/Nelogica é a plataforma de execução. A integração entre os dois sistemas pode ser feita de formas distintas, com graus crescentes de automação e acoplamento.

O princípio de falha segura (Stack, Princípio 5) exige que qualquer falha técnica degrade para "não opera", nunca para "executa fora de regra". Isso favorece uma integração que cresce em automação somente quando a camada anterior é estável e validada.

Integrar via ProfitDLL (ctypes) desde o início cria acoplamento com uma DLL proprietária da Nelogica que pode mudar sem aviso, é Windows-only, e não é necessária para as fases iniciais onde Carlos opera manualmente e importa CSV.

---

## 2. Decisão

A integração entre CaM e Profit cresce de forma **faseada e sequencial** — cada fase é pré-requisito para a próxima e não avança sem validação pelo Founder.

| Fase de integração | O que o CaM faz | Gate de avanço |
|---|---|---|
| **F1 — Manual** | CaM gera checklist e Risk Engine valida intenção. Carlos opera o Profit manualmente. Journal preenchido manualmente no frontend CaM | Zero violações em 1 semana de uso |
| **F2 — Importação CSV** | CaM importa CSV/extrato Profit pós-pregão. Concilia journal manual × execução real. Ledger fiscal automático via importação | Importação cobre 100% das operações sem erro |
| **F3 — Semi-automática** | CaM monitora estado do Profit em tempo real (status, P&L, posição) via export periódico ou interface oficial. Ainda não envia ordem | Monitoramento estável por 30 dias úteis |
| **F4 — NTSL com regras espelhadas** | Estratégia em NTSL no Profit com Risk hard-coded em NTSL (2ª linha de defesa). CaM publica parâmetros vigentes. Execução automática real | Validação em simulação + módulo de Automação de Estratégias contratado |
| **F5 — ProfitDLL (avaliação)** | Adapter Python via ctypes para controle fino. **Não obrigatório** — somente se necessidade real comprovar | Decisão futura por emenda formal |

**Feature de integração:** `cam/features/profit_integration/`
- `csv_importer.py`: importação e conciliação de extrato CSV (F2)
- `monitor.py`: monitoramento em tempo real de estado do Profit (F3)
- `ntsl_publisher.py`: publica parâmetros vigentes do Risk Engine para NTSL consumir (F4)
- `dll_adapter.py`: ProfitDLL via ctypes (F5 — arquivo placeholder, não implementado antes de F4 validado)

**Injeção de dependência:** em Linux (dev), os adapters usam mock; em Windows (prod), usam implementação real. Sem `if sys.platform == 'win32'` espalhado pelo código — adaptadores injetados no startup do FastAPI.

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | ProfitDLL desde o início (Fase 0) | Acoplamento com DLL proprietária que pode mudar; Windows-only bloqueia desenvolvimento em Linux; risco de falha catastrófica durante operação real antes de ter cobertura de testes adequada |
| 2 | API direta de corretora (bypass do Profit) | Cada corretora tem API diferente; sem book visual para Carlos durante operação manual; complexidade regulatória adicional |
| 3 | Integração completa via webhooks do Profit | Profit não expõe webhooks públicos no MVP — dependente de roadmap Nelogica |

---

## 4. Consequências

### Positivas
- Risco de falha controlado: falha em F1-F2 não causa operação incorreta (Carlos ainda opera manualmente)
- Desenvolvimento em Linux é possível em F1-F3 (sem dependência de Profit real)
- Cada fase pode ser validada de forma isolada antes de avançar
- F5 (ProfitDLL) não é comprometimento — é opção avaliada por necessidade real

### Negativas
- F1-F2 exigem trabalho manual do operador (checklist + journal + importação CSV)
- F4 requer contratação do módulo de Automação de Estratégias (custo adicional)
- Sincronização entre Risk Engine Python e NTSL espelhada (ADR-009) requer manutenção ativa

### Neutras
- F3 de monitoramento depende de formato de export do Profit — pode variar por versão do software

---

## 5. Custo de Reversão

**Baixo por fase** — cada fase de integração é incremental. Reverter de F3 para F2 (parar monitoramento, voltar ao CSV) é simples. Reverter de F4 para F3 requer desabilitar estratégia NTSL e voltar ao monitoramento manual.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §4 (fluxo de registro de operação)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.1
- ADRs relacionadas: ADR-001 (Profit como plataforma), ADR-009 (NTSL como 2ª linha de defesa), ADR-012 (dev Linux / prod Windows)

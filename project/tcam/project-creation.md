---
template: PDOC
phase: PDOC
status: Vigente
---

# PDOC — cam-cockpit

> **Registro Formal de Criação do Projeto**
> **Data de criação:** 2026-05-24
> **Leads:** Leo (orquestrador) + Denis (documentação)
> **Aprovador:** Founder (Carlos Rodrigues Ferreira Junior)

---

## 1. Identificação do Projeto

| Campo | Valor |
|---|---|
| **Nome completo** | CaM Cockpit |
| **Codinome** | `cam-cockpit` |
| **Projeto pai** | CaM — The Carlos Alternative Money |
| **Natureza** | Cockpit pessoal, local, não comercial |
| **Operador único** | Carlos Rodrigues Ferreira Junior |
| **Separação institucional** | Projeto separado e independente da Teczilabs (Art. 8º da Constituição) |

---

## 2. Objetivo

Construir o cockpit operacional completo do CaM — a camada de software que:

- aplica o Risk Engine constitucional antes de qualquer operação;
- registra toda operação no Journal (Art. 31º);
- provisiona imposto automaticamente e exibe resultado líquido (Art. 25º);
- executa a Harvest Rule convertendo lucro em patrimônio (Art. 21º);
- controla o Kill Switch de forma imediata e sem justificativa (Art. 18º);
- integra a plataforma Profit/Nelogica para execução de estratégias;
- provê backtest engine com o mesmo Risk Engine do ambiente live;
- oferece auditoria IA pós-mercado sem autoridade de execução (Arts. 34º–36º).

---

## 3. Escopo Geral

O cam-cockpit é um monorepo local composto por:

- **Backend Python 3.12 + FastAPI** — Risk Engine, Journal, Ledger Fiscal, Harvest, Backtest Engine, IA auditora, Integração Profit, Alertas Telegram
- **Frontend React 19 + Vite + MUI** — SPA local servida pelo backend
- **Banco PostgreSQL 16 + TimescaleDB** — dados operacionais e séries temporais (ticks/candles)
- **Estratégias NTSL** — versionadas em `apps/cam-cockpit/ntsl/`

---

## 4. Classificação

| Campo | Valor |
|---|---|
| **Classificação P/M/G** | **G (Grande)** — múltiplas frentes, múltiplos módulos, decomposição obrigatória |
| **Justificativa** | 9+ módulos funcionais distintos (Risk Engine, Journal, Ledger Fiscal, Frontend, Integração Profit, Backtest Engine, IA Auditora, Alertas, Infraestrutura), cada um com contratos e critérios de aceite próprios |
| **Não é MVP parcial** | Cockpit completo para operador único — o escopo reduzido viria de fases operacionais (Fase 0 → Fase 1 → ...), não de redução de funcionalidades essenciais |

---

## 5. Stakeholders e Papéis

| Papel | Pessoa |
|---|---|
| **Founder / Operador único** | Carlos Rodrigues Ferreira Junior |
| **Orquestrador** | Leo (CTO/COO virtual) |
| **Autoridade de processo** | NCC-1701 DevFlow v6.0 |
| **Lei suprema** | Constituição Operacional do CaM v1.0 |

Não há usuários finais além do próprio Founder. Não há equipe externa, cliente, investidor ou stakeholder adicional.

---

## 6. Fase Atual do CaM

**Fase 0 — Construção** (conforme Constituição Anexo II)

Critérios de saída da Fase 0 (gate para Fase 1 — Paper Trading):
- Cockpit funcional end-to-end
- Risk Engine com cobertura de testes ≥ 80%
- Kill switch validado em teste real
- Pipeline de backtest funcional
- Pipeline de paper trading funcional

---

## 7. Artefatos-Mãe

| Documento | Localização | Papel |
|---|---|---|
| Constituição Operacional do CaM v1.0 | `/CONSTITUICAO.md` | Lei suprema — hierarquia inviolável |
| Stack Oficial CaM (variante Windows+Profit) | `/project/STACK-CAM-OFICIAL.md` | Decisões técnicas e ADRs propostos |
| NCC-1701 Process | `/teczi-devflow/NCC-1701/process.md` | Framework de processo de desenvolvimento |

---

## 8. Hierarquia Constitucional Aplicável

```
Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual
```

**Artigos inegociáveis que todo artefato e código deste projeto deve respeitar:**

| Artigo | Regra |
|---|---|
| Art. 11º | Máximo 2 contratos WIN / 2 WDO — intocável |
| Art. 15º | Risk Engine bloqueia → operação não ocorre, sem exceção |
| Art. 18º | Kill switch obrigatório, acionável sem justificativa |
| Art. 19º | Posição aberta sem cobertura sistêmica é risco inaceitável |
| Art. 25º | UIs exibem resultado LÍQUIDO de imposto provisionado, nunca bruto |
| Art. 26º | DARF atrasada bloqueia novas operações |
| Art. 31º | Operação sem registro no journal é falha operacional |
| Art. 35º | IA NÃO PODE enviar ordem, desabilitar Risk Engine, justificar exceção constitucional |
| Art. 36º | Hierarquia constitucional — inviolável |
| Art. 6º | Em dúvida entre abordagens, prevalece a que preserva mais capital |

---

## 9. Estrutura de Pastas do Projeto

```
project/cam-cockpit/          ← INTENÇÃO VIVA (artefatos DevFlow)
├── PDOC/
│   └── project-creation.md  ← este arquivo
├── SCOPE.md
├── DVP.md
├── DAS.md
├── SPEC.md
├── adrs/
│   ├── ADR-001-*.md
│   └── ADR-013-*.md
└── demands/                  ← demandas futuras por módulo

apps/cam-cockpit/             ← ESTADO REAL (código)
├── backend/
│   ├── cam/_shared/          ← Risk Engine, domain, events, audit, infra
│   └── cam/features/         ← slices por módulo
├── frontend/
│   └── src/features/
└── ntsl/
```

---

## 10. Gates de Aprovação do Founder

Toda transição entre fases NCC-1701 requer aprovação explícita do Founder. Não há gate automático.

| Gate | Quando |
|---|---|
| PDOC → DISC | Founder valida esta estrutura de projeto |
| DISC → ARCH | Founder aprova o SCOPE (In/Out/Later) |
| ARCH → SPEC | Founder aprova as decisões arquiteturais e ADRs |
| SPEC → PLAN | Founder aprova a especificação completa |
| PLAN → CODE | Founder aprova letscode (gate final do PLAN) |

---

## 11. Histórico

| Versão | Data | Evento |
|---|---|---|
| 1.0 | 2026-05-24 | Criação do projeto. PDOC inicial. Produzido por Leo + Denis via NCC-1701 |

---

> **Gate de aprovação PDOC:** Founder valida esta estrutura antes de avançar para DISC.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

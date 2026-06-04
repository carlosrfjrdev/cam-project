---
template: DVP
phase: DISC
status: Draft
---

# DVP — CaM Cockpit

> **Documento de Visão de Produto**
> **Data:** 2026-05-24
> **Versão:** 1 · **Status:** Draft — aguarda aprovação do Founder
> **Lead:** Marty (criação) · Founder (aprovação)
> **Vive em:** `/project/cam-cockpit/DVP.md`

---

## 1. Identidade do Produto

| Campo | Valor |
|---|---|
| **Nome** | CaM Cockpit |
| **Codinome** | `cam-cockpit` |
| **Categoria** | Interno — uso pessoal exclusivo do operador |
| **Stage** | Concept → MVP (Fase 0 atual) |
| **Natureza** | Cockpit pessoal, local, não comercial |
| **Separação** | Independente da Teczilabs (Art. 8º) |

---

## 2. Problema Central

Em 2020, Carlos perdeu R$ 100 mil operando com convicção excessiva sobre uma reserva de R$ 50 mil. O inimigo do operador não é o mercado — é o operador em estado de emoção: ganância, medo, pressa de recuperar o passado (Preâmbulo da Constituição).

O problema não é ausência de conhecimento técnico ou falta de estratégia. O problema é a **ausência de um árbitro sistêmico** que interponha regras invioláveis entre a intenção do operador e a execução da ordem. Quando o árbitro é apenas a mente humana em tempo real de mercado, as regras são contornadas toda vez que a emoção vence.

Sem um cockpit que torne as regras constitucionais não-contornáveis:
- O operador pode aumentar contratos após perda (Martingale — Art. 13º)
- O operador pode ignorar o limite de perda diária e continuar operando
- O operador pode não registrar operações que prefere esquecer (Art. 31º)
- O operador pode ver o resultado bruto e ignorar o imposto devido (Art. 25º)
- O operador pode deixar DARF acumular e operar sem provisão (Art. 26º)
- O operador pode nunca executar a Harvest Rule, mantendo todo capital em risco especulativo

O CaM Cockpit existe para tornar a disciplina operacional **estrutural**, não volitiva.

---

## 3. Usuário-Alvo

**Quem é:** Carlos Rodrigues Ferreira Junior, engenheiro de software, trader individual B3.

**O que faz hoje:**
- Opera (ou operará) mini índice WIN e mini dólar WDO na Nelogica Profit
- Desenvolveu uma constituição operacional com 43 artigos de regras invioláveis
- Está na Fase 0 — construindo o cockpit antes de qualquer operação real ou paper trade

**O que precisa:**
- Um sistema que aplique as regras constitucionais automaticamente, sem depender de força de vontade em tempo real
- Visibilidade clara de P&L líquido (não bruto) para nunca confundir resultado com obrigação fiscal
- Registro automático e obrigatório de toda operação
- Um kill switch imediato que não exija justificativa
- Backtest com as mesmas regras de risco do live (sem "iludir o backtest desligando o Risk Engine")
- IA como analista pós-mercado, nunca como tomadora de decisão de execução

---

## 4. Proposta de Valor

**O CaM Cockpit não existe para operar mais. Existe para impedir operação ruim.**

| Dimensão | O que o CaM entrega |
|---|---|
| **Proteção sistêmica** | Risk Engine torna regras constitucionais não-contornáveis — sem bypass, sem "só dessa vez" |
| **Visibilidade honesta** | P&L sempre líquido de imposto provisionado — sem ilusão de resultado bruto |
| **Disciplina estrutural** | Journal obrigatório, checklists bloqueantes, DARF que interrompe operação se atrasada |
| **Conversão de lucro em patrimônio** | Harvest Rule calculada automaticamente — lucro tático vira Carteira Hard |
| **Backtest sem duplo padrão** | O mesmo Risk Engine que roda no live é o que valida o backtest — sem estratégia que "funciona no backtest mas falha na regra de risco real" |
| **Auditabilidade completa** | Toda decisão do Risk Engine, toda operação, toda violação registradas com timestamp imutável |
| **Resiliência técnica** | Journal duplo (banco + JSONL local) — posição jamais perde registro por falha de banco |

---

## 5. Hipóteses Centrais (a Validar)

- **[H1]** Um Risk Engine de software que bloqueie operações fora de regra é mais eficaz do que regras escritas que dependem de força de vontade
- **[H2]** Exibir P&L líquido de imposto provisionado em todas as telas reduz a distorção cognitiva entre "resultado do dia" e "quanto de fato foi ganho"
- **[H3]** A automação da Harvest Rule aumenta a probabilidade de conversão real de lucro em patrimônio (vs. decisão manual que pode ser postergada indefinidamente)
- **[H4]** O backtest com Risk Engine ativo produz expectâncias mais conservadoras e realistas do que backtest sem controles de risco
- **[H5]** O journal obrigatório, quando técnico e rápido de preencher, tem aderência superior ao journal opcional que depende de disciplina pós-operação

---

## 6. Não-Objetivos

O CaM Cockpit **explicitamente não é**:

- Um produto comercial ou SaaS
- Uma plataforma de execução de ordens (o Profit executa; o CaM governa)
- Um sistema multi-usuário ou multi-tenant
- Um robô de trading autônomo (IA não tem autoridade de execução — Art. 35º)
- Uma plataforma de gestão de carteira de renda variável (Carteira Hard é acompanhada, não gerida)
- Um sistema escalável horizontalmente (mono-host por design)
- Uma aplicação HFT (latência alvo: dezenas de ms)
- Um produto cloud-first (localidade absoluta é princípio da stack)
- Uma ferramenta para outros operadores ou ativos fora de WIN/WDO/B3
- Um substituto para a Constituição (o cockpit implementa a Constituição, não a substitui)

---

## 7. Estratégia de Evolução

**Marcos por fase do CaM (não por janela temporal):**

| Marco | Conteúdo | Gate de saída |
|---|---|---|
| **M0 (atual)** | Constituição + Stack Oficial + PDOC/DISC/ARCH/SPEC | Artefatos aprovados pelo Founder |
| **M1** | Infra base: Docker Compose (Postgres+Timescale) + FastAPI esqueleto + Risk Engine Pure Python primeiros validators | Founder valida PLAN → CODE → QA |
| **M2** | Schema DB completo + hypertables + backfill de tick histórico | Founder valida entrega |
| **M3** | Frontend passivo (Dashboard + Journal + Risk Console + Constituição read-only) | Founder valida UI |
| **M4** | Ledger Fiscal + Importador CSV Profit + conciliação trade-a-trade | Founder valida fiscal |
| **M5** | Risk Engine completo (todos validators Arts. 11º–20º) com property-based testing ≥ 100% | Founder valida cobertura |
| **M6** | Backtest engine + walk-forward + DuckDB research | Founder valida backtests |
| **M7** | Pattern studies (Timescale hyperfunctions) + IA auditora (Ollama + Anthropic) | Founder valida análises |
| **M8** | Integração Profit operacional: NTSL espelhada + paper trading | Founder valida integração |
| **M9** | Kill switch hardening + Telegram + critérios de saída Fase 0 completos | Founder valida gate Fase 0 → Fase 1 |

---

## 8. Sinais de Sucesso

**Fase 0 — Construção (critérios objetivos da Constituição Anexo II):**
- Cockpit funcional end-to-end (todos os módulos integrados)
- Risk Engine com cobertura de testes ≥ 80% (todos validators presentes)
- Kill switch validado em teste real (não apenas teste unitário)
- Pipeline de backtest funcional com Risk Engine ativo
- Pipeline de paper trading funcional

**Operacionais (Fase 1+):**
- Zero operações com resultado exibido como bruto (Art. 25º violado = falha)
- Zero operações com Risk Engine bypassed (Art. 15º violado = falha)
- Zero operações sem registro no journal (Art. 31º violado = falha)
- Harvest Rule executada mensalmente sem intervenção manual adicional além da aprovação do Founder
- Aderência operacional ≥ 95% mensalmente (Art. 29º)

---

## 9. Sinais de Fracasso

- O operador encontra forma de contornar o Risk Engine "só por hoje"
- P&L bruto fica visível sem o líquido em qualquer tela operacional
- Journal vira campo opcional de fato (operações sem registro passam sem bloqueio)
- Harvest Rule nunca é executada porque "não compensa com esse valor"
- O backtest usa parâmetros de risco diferentes do live, gerando expectância inflada
- A IA começa a receber dados que permitem recomendar execução (violação Art. 35º)
- DARF acumula meses sem bloqueio operacional (violação Art. 26º)
- O kill switch não está acessível em alguma tela operacional

---

## 10. Decisões Herdadas (ADRs)

Decisões já tomadas no STACK-CAM-OFICIAL.md que este DVP herda:

| ADR | Decisão | Status |
|---|---|---|
| ADR-001 | Profit como plataforma oficial de execução | Aceita |
| ADR-002 | Python 3.12 + FastAPI como backend | Aceita |
| ADR-003 | React 19 + Vite + MUI (SPA local, sem Next.js) | Aceita |
| ADR-004 | PostgreSQL 16 + TimescaleDB desde Fase 0 | Aceita |
| ADR-005 | DuckDB como motor analítico auxiliar (read-only sobre arquivos) | Aceita |
| ADR-006 | IA sem autoridade operacional (vinculante constitucional) | Aceita (Arts. 34º–36º) |
| ADR-007 | Risk Engine Pure Python no Shared Kernel | Aceita |
| ADR-008 | Integração Profit faseada (F1→F5) | Aceita |
| ADR-009 | Risk Engine espelhado em NTSL como 2ª linha de defesa | Aceita |
| ADR-010 | Telegram como canal externo de alerta independente | Aceita |
| ADR-011 | Monorepo único `apps/cam-cockpit/` no MVP | Aceita |
| ADR-012 | Dev em Linux, produção em Windows; code cross-platform | Aceita |
| ADR-013 | Feature-Based Vertical Slice + Shared Kernel mínimo | Aceita |

---

## 11. Riscos Conhecidos

| Risco | Impacto | Mitigação |
|---|---|---|
| Profit/NTSL muda sem aviso | Integração F4 quebra | Travar versão; smoke test pré-pregão; changelog próprio |
| Operador desliga Risk Engine "só por hoje" | Violação Art. 15º | Flag `PRODUCTION_ALLOWED` versionada + edição requer cooldown |
| Backtest diverge do live (DRY quebrado) | Expectância inflada, estratégia falha no live | Contrato `MarketContext` único; testes de paridade backtest↔paper |
| Acoplamento acidental `risk/` ↔ `features/` | Risk Engine deixa de ser Pure Python | `import-linter` no CI bloqueia merge |
| Falha do banco com posição aberta | Perda de registro de operação (Art. 31º) | Journal duplo: Postgres + JSONL local append-only |
| Vazamento de credenciais | Segurança comprometida | `.env` nunca versionado; pré-commit hook detecta padrões de chave |
| NTSL espelhada diverge do Risk Engine Python | Segunda linha de defesa falha | Testes de paridade NTSL↔Python por cenário canônico |
| Edge da estratégia não cobre custos de plataforma | Capital se deteriora (Voltaire: R$ 200–380/mês = 4–8% sobre R$ 5.000) | Backtest deve incluir custos reais de corretagem + plataforma |

---

## 12. Histórico de Versões

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-05-24 | Criação — produzido via NCC-1701 DISC | — (aguarda Founder) |

---

> **Gate de aprovação DVP:** Founder valida junto com SCOPE antes de avançar para ARCH.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

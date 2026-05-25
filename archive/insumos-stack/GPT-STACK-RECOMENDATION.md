# GPT-STACK-RECOMENDATION.MD

# CaM Project — Recomendação de Stack

**Projeto:** CaM — The Carlos Alternative Money  
**Versão:** 0.1  
**Autor da recomendação:** GPT  
**Data:** 2026-05-24  
**Natureza:** Cockpit local pessoal para operação, governança, risco, ledger e automação controlada com Profit  
**Status:** Recomendação técnica inicial

---

## 1. Decisão central

A stack recomendada para o CaM Project é:

```text
Profit/Nelogica        -> Plataforma efetiva de operação, gráficos, simulação, automação e execução
Python + FastAPI       -> Backend local, Risk Engine, Ledger, Journal, integrações e orquestração
React + Vite           -> Frontend local do cockpit operacional
SQLite                 -> Banco local inicial
DuckDB                 -> Camada analítica local para backtests, métricas e estudos
Ollama opcional        -> IA local para análise, auditoria e relatórios não críticos
Git                    -> Versionamento do projeto, regras, estratégias e documentação
```

O CaM não deve tentar substituir o Profit.  
O CaM deve funcionar como **camada local de governança, risco, auditoria, ledger, journal e inteligência operacional** ao redor do Profit.

---

## 2. Premissa operacional

O operador irá operar efetivamente com **Profit**.

Portanto, a arquitetura deve respeitar esta premissa:

```text
Profit é o executor.
CaM é o cockpit.
Risk Engine é a autoridade.
Python é o cérebro operacional local.
React/Vite é a interface.
Banco local é a memória.
IA é apoio analítico, não autoridade de execução.
```

O Profit possui Editor de Estratégias para codificar, testar e simular estratégias usando NTSL — Nelogica Trading System Language. A automação em conta de simulação está disponível nos planos Profit Ultra e Profit Pro, enquanto operação em conta real exige contratação do módulo opcional de Automação de Estratégias.  
Fontes consultadas:
- https://ajuda.nelogica.com.br/hc/pt-br/articles/9165042993691-Editor-de-Estrat%C3%A9gias-Crie-estrat%C3%A9gias-pr%C3%B3prias-atrav%C3%A9s-do-Profit
- https://ajuda.nelogica.com.br/hc/pt-br/articles/8865257831195-Como-utilizar-a-Automa%C3%A7%C3%A3o-de-Estrat%C3%A9gias
- https://ajuda.nelogica.com.br/hc/pt-br/articles/18501196212251-Conhe%C3%A7a-o-m%C3%B3dulo-de-Automa%C3%A7%C3%A3o-de-Estrat%C3%A9gias

---

## 3. Arquitetura recomendada

```text
┌─────────────────────────────────────────────────────────────────────┐
│                             CaM Cockpit                             │
│                          React + Vite + UI                          │
│                                                                     │
│  Dashboard | Journal | Risk Panel | Ledger | Harvest | Reports      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                              CaM Core                               │
│                         Python + FastAPI                            │
│                                                                     │
│  Risk Engine | Ledger | Journal | Strategy Registry | Tax Ledger     │
│  Profit Adapter | Audit Log | AI Analyst | Backtest/Simulation      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
┌──────────────────────────────────┐  ┌───────────────────────────────┐
│          Local Storage            │  │          Profit/Nelogica       │
│ SQLite | DuckDB | Files | Git      │  │ NTSL | Estratégias | Execução  │
└──────────────────────────────────┘  └───────────────────────────────┘
```

---

## 4. Papel de cada componente

### 4.1 Profit/Nelogica

**Papel:** executor operacional e ambiente de mercado.

Responsabilidades:

- gráficos;
- cotações;
- simulação;
- replay/backtesting disponível na plataforma;
- execução manual ou automatizada;
- estratégias NTSL;
- automação de estratégias;
- operação efetiva de WIN e WDO.

Decisão:

```text
Toda ordem real deve passar pelo Profit.
Nenhuma ordem real deve ser enviada diretamente por uma automação improvisada fora da plataforma sem validação formal.
```

Motivo:

- reduz risco técnico;
- aproveita plataforma especializada;
- evita reinventar roteamento;
- mantém execução dentro do ecossistema operacional escolhido;
- facilita simulação antes da conta real.

---

### 4.2 Python + FastAPI

**Papel:** backend local do CaM.

Responsabilidades:

- API local para o cockpit;
- Risk Engine;
- registro de operações;
- controle de limites;
- journal;
- ledger de carteira;
- trilha fiscal;
- integração com arquivos/exportações do Profit;
- processamento de relatórios;
- execução de rotinas;
- análise de métricas;
- preparação de dados para IA.

Recomendação:

```text
Python 3.12+
FastAPI
Pydantic
SQLAlchemy
Alembic
APScheduler
Pandas
Polars opcional
DuckDB
```

Por que Python:

- excelente para análise de dados;
- bom ecossistema para mercado financeiro;
- rápido para prototipar;
- simples para rodar local;
- combina bem com FastAPI e dashboards;
- permite scripts, automações e relatórios com baixa fricção.

---

### 4.3 React + Vite

**Papel:** cockpit local.

Responsabilidades:

- dashboard operacional;
- painel de risco;
- posição do dia;
- status do Profit;
- journal;
- histórico;
- carteira hard;
- harvest;
- relatórios;
- tela de checklist;
- kill switch visual;
- auditoria de aderência.

Recomendação:

```text
React
Vite
TypeScript
TanStack Query
React Router
Zustand
MUI ou shadcn/ui
Recharts
Zod
Axios ou Fetch wrapper
```

Decisão de UI:

```text
React + Vite é suficiente.
Não usar Next.js no MVP.
```

Motivo:

- sistema local;
- sem necessidade de SSR;
- menos complexidade;
- build leve;
- integração simples com FastAPI local;
- ótimo para dashboard desktop.

---

### 4.4 SQLite

**Papel:** banco local transacional inicial.

Responsabilidades:

- operações;
- setups;
- journal;
- posições;
- limites;
- carteira;
- impostos;
- eventos de risco;
- parâmetros operacionais;
- trilha de auditoria.

Recomendação:

```text
SQLite no MVP.
PostgreSQL apenas se o projeto crescer.
```

Motivo:

- simples;
- local;
- confiável;
- fácil de versionar backup;
- baixa manutenção;
- adequado para projeto pessoal.

---

### 4.5 DuckDB

**Papel:** motor analítico local.

Responsabilidades:

- análise de histórico;
- backtests;
- estatísticas;
- agregações;
- métricas por setup;
- métricas por horário;
- métricas por ativo;
- estudos de performance;
- leitura de CSV/Parquet.

Por que DuckDB:

- excelente para analytics local;
- roda embutido;
- ótimo com arquivos;
- combina bem com Pandas/Polars;
- evita acoplar analytics pesado no SQLite.

---

### 4.6 IA local/opcional

**Papel:** analista, auditor e gerador de relatórios.

Recomendação:

```text
Ollama local para análises simples e privadas.
LLM externo apenas para relatórios não sensíveis ou dados anonimizados.
```

A IA pode:

- revisar journal;
- identificar desvio comportamental;
- resumir o dia;
- explicar violações de regra;
- sugerir hipóteses de melhoria;
- classificar regime operacional;
- criar relatório semanal;
- ajudar na análise de drawdown.

A IA não pode:

- autorizar ordem;
- ignorar Risk Engine;
- aumentar mão;
- decidir martingale;
- operar contra regra;
- ser autoridade final.

---

## 5. Integração com Profit

A integração deve começar simples e crescer por fases.

### Fase 1 — Sem integração direta

O CaM funciona como cockpit manual:

```text
Profit executa/simula.
CaM registra manualmente.
CaM calcula risco.
CaM gera checklist.
CaM audita comportamento.
```

### Fase 2 — Integração por arquivos/exportações

O CaM importa:

- CSV de operações;
- notas;
- relatórios;
- logs;
- extratos;
- resultados do dia.

Essa fase já permite:

- ledger;
- journal;
- tax ledger;
- relatórios;
- validação de estratégia;
- análise de aderência.

### Fase 3 — Integração semi-automática

O CaM passa a monitorar:

- status do dia;
- risco aberto;
- limite diário;
- estratégia habilitada;
- plano operacional;
- violações de regra.

Nessa fase, o CaM ainda não deve executar ordem diretamente.

### Fase 4 — Automação via Profit

A estratégia de execução roda no Profit/NTSL.

O CaM atua como:

- cockpit;
- pré-validador;
- auditor;
- ledger;
- risk policy manager;
- relatório pós-mercado.

### Fase 5 — Integrações avançadas

Somente se houver documentação, plano contratado, testes e validação:

- APIs/DLLs disponíveis;
- monitoramento em tempo real;
- sincronização de dados;
- alertas;
- bloqueios auxiliares;
- automações periféricas.

Importante:

```text
A execução real deve permanecer dentro do caminho suportado pela plataforma e pela corretora.
```

---

## 6. Módulos do backend

### 6.1 cam-risk

Responsável por:

- limite diário;
- limite semanal;
- limite por fase;
- limite de contratos;
- não simultaneidade inicial;
- bloqueio por sequência de losses;
- bloqueio por checklist incompleto;
- bloqueio por ausência de journal;
- bloqueio por drawdown;
- status pode operar / não pode operar.

Regras fundacionais:

```text
Máximo futuro: 2 WIN e 2 WDO.
Fase inicial real: 1 contrato.
Sem WIN e WDO simultâneos na fase inicial.
Risk Engine sempre prevalece.
```

---

### 6.2 cam-ledger

Responsável por:

- capital inicial;
- operações;
- posição;
- resultado bruto;
- custos;
- resultado líquido;
- carteira hard;
- compras recorrentes;
- dividendos/JCP;
- saldo operacional;
- caixa fiscal;
- caixa de harvest.

---

### 6.3 cam-journal

Responsável por:

- plano do dia;
- checklist pré-mercado;
- motivo da entrada;
- motivo da saída;
- aderência;
- estado emocional;
- pós-mercado;
- lições aprendidas;
- falhas técnicas;
- violações de regra.

---

### 6.4 cam-harvest

Responsável por:

- separar gain líquido;
- destinar parte para carteira hard;
- destinar parte para reserva operacional;
- destinar parte para imposto/custos;
- impedir que lucro do dia seja devolvido por overtrade.

---

### 6.5 cam-tax

Responsável por:

- resultado mensal;
- prejuízo acumulado;
- base de DARF;
- custos;
- taxas;
- separação por tipo de operação;
- relatório para conferência manual.

Observação:

```text
O CaM Tax deve apoiar controle fiscal, mas a apuração final deve ser conferida antes de qualquer pagamento.
```

---

### 6.6 cam-strategy-registry

Responsável por catalogar estratégias:

- nome;
- ativo;
- timeframe;
- premissa;
- regra de entrada;
- regra de saída;
- stop;
- alvo;
- versão;
- status;
- elegibilidade para simulação;
- elegibilidade para real.

---

### 6.7 cam-profit-adapter

Responsável por isolar integração com Profit.

No início:

- importação manual;
- leitura de CSV;
- leitura de pastas locais;
- normalização de relatórios.

No futuro:

- integração com interfaces oficiais disponíveis;
- monitoramento;
- sincronização;
- validação operacional.

---

### 6.8 cam-ai-analyst

Responsável por:

- análise pós-mercado;
- resumo semanal;
- identificação de padrão ruim;
- análise de journal;
- sugestões de estudo;
- geração de relatórios.

Nunca responsável por:

- envio de ordem;
- liberação de limite;
- aumento de contrato;
- override do Risk Engine.

---

## 7. Estrutura de repositório recomendada

```text
cam-project/
├── README.md
├── docs/
│   ├── CONSTITUICAO-OPERACIONAL-CAM.md
│   ├── GPT-STACK-RECOMENDATION.md
│   ├── architecture/
│   │   ├── C4-CONTEXT.md
│   │   ├── C4-CONTAINER.md
│   │   └── DECISIONS.md
│   ├── operations/
│   │   ├── CHECKLIST-PRE-MERCADO.md
│   │   ├── CHECKLIST-POS-MERCADO.md
│   │   └── RISK-POLICY.md
│   └── strategies/
│       ├── TEMPLATE-STRATEGY.md
│       └── registry.md
│
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── modules/
│   │   │   ├── risk/
│   │   │   ├── ledger/
│   │   │   ├── journal/
│   │   │   ├── harvest/
│   │   │   ├── tax/
│   │   │   ├── strategy_registry/
│   │   │   ├── profit_adapter/
│   │   │   └── ai_analyst/
│   │   └── infra/
│   │       ├── db/
│   │       ├── files/
│   │       └── scheduler/
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── app/
│       ├── components/
│       ├── modules/
│       │   ├── dashboard/
│       │   ├── risk/
│       │   ├── ledger/
│       │   ├── journal/
│       │   ├── harvest/
│       │   └── reports/
│       └── shared/
│
├── data/
│   ├── raw/
│   ├── imports/
│   ├── exports/
│   ├── duckdb/
│   └── backups/
│
├── strategies/
│   ├── ntsl/
│   ├── research/
│   └── backtests/
│
└── scripts/
    ├── dev.sh
    ├── backup.sh
    └── import_profit_csv.py
```

---

## 8. Decisões técnicas formais

### ADR-001 — Profit como plataforma de execução

**Decisão:** o CaM usará Profit como plataforma efetiva de operação.  
**Consequência:** o CaM não tentará substituir o Profit no MVP.  
**Motivo:** reduzir risco técnico e usar infraestrutura especializada de mercado.

---

### ADR-002 — Python como backend local

**Decisão:** backend em Python com FastAPI.  
**Consequência:** desenvolvimento rápido e forte capacidade analítica.  
**Motivo:** o domínio exige análise, dados, automação local e integração leve.

---

### ADR-003 — React/Vite como cockpit

**Decisão:** frontend em React + Vite.  
**Consequência:** aplicação local simples, rápida e sem complexidade de SSR.  
**Motivo:** o cockpit não precisa de Next.js no MVP.

---

### ADR-004 — SQLite no MVP

**Decisão:** SQLite como banco transacional inicial.  
**Consequência:** menor complexidade operacional.  
**Motivo:** projeto local, pessoal e de baixo volume.

---

### ADR-005 — DuckDB para analytics

**Decisão:** DuckDB para análise local.  
**Consequência:** separação entre transacional e analítico.  
**Motivo:** backtests e relatórios podem exigir consultas pesadas.

---

### ADR-006 — IA sem autoridade operacional

**Decisão:** IA será usada como apoio, não como executor.  
**Consequência:** IA não envia ordem, não aumenta mão e não ignora Risk Engine.  
**Motivo:** reduzir risco comportamental, técnico e financeiro.

---

## 9. Roadmap técnico recomendado

### Milestone 0 — Fundação documental

- Constituição Operacional;
- Stack Recommendation;
- Risk Policy;
- templates de estratégia;
- checklist pré/pós mercado.

### Milestone 1 — Backend local mínimo

- FastAPI;
- SQLite;
- entidades principais;
- endpoints de risk, ledger e journal;
- testes unitários do Risk Engine.

### Milestone 2 — Frontend cockpit passivo

- dashboard;
- status pode operar / não pode operar;
- cadastro de capital;
- cadastro de operações manuais;
- checklist;
- journal;
- visão de carteira hard.

### Milestone 3 — Ledger e Tax básico

- resultado diário;
- resultado mensal;
- custos;
- prejuízo acumulado;
- estimativa fiscal;
- relatório de conferência.

### Milestone 4 — Importador Profit

- importação CSV;
- normalização;
- conciliação;
- validação;
- relatório pós-mercado.

### Milestone 5 — Risk Engine completo

- limites;
- fases;
- bloqueios;
- violações;
- kill switch lógico;
- auditoria.

### Milestone 6 — Camada analítica

- DuckDB;
- métricas de estratégia;
- análise por setup;
- análise por horário;
- drawdown;
- payoff;
- sequência de perdas.

### Milestone 7 — IA analítica

- resumo diário;
- análise de aderência;
- relatório semanal;
- detecção de padrões ruins;
- sugestão de melhoria.

### Milestone 8 — Integração operacional com Profit

- validação com automação em simulação;
- estratégia NTSL;
- logs;
- conciliação;
- operação real apenas após fase de validação.

---

## 10. Stack final recomendada

```text
Runtime:
- Python 3.12+
- Node.js LTS

Backend:
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- APScheduler
- Pandas
- DuckDB
- SQLite
- Pytest

Frontend:
- React
- Vite
- TypeScript
- TanStack Query
- React Router
- Zustand
- MUI ou shadcn/ui
- Recharts
- Zod

Trading Platform:
- Profit Pro ou Profit Ultra
- Módulo de Automação de Estratégias para conta real
- NTSL para estratégias
- Conta de simulação antes de conta real

IA:
- Ollama local opcional
- LLM externo apenas com anonimização ou dados não sensíveis

Dev/Ops local:
- Git
- Makefile ou scripts shell
- Docker opcional, não obrigatório
- Backup local versionado
- Exportação CSV/Parquet
```

---

## 11. Recomendação final

A melhor stack para o CaM Project é:

```text
Profit como executor.
Python/FastAPI como cérebro local.
React/Vite como cockpit.
SQLite como memória operacional.
DuckDB como motor analítico.
IA como analista e auditora.
Git como trilha de governança.
```

A decisão mais importante não é técnica.

A decisão mais importante é arquitetural e comportamental:

```text
O CaM não deve ser construído para operar mais.
O CaM deve ser construído para impedir operação ruim.
```

O Profit executa.  
O Python fiscaliza.  
O React mostra.  
O Ledger registra.  
O Risk Engine manda.  
A IA comenta.  
O Carlos obedece ao sistema.

---

## 12. Frase de arquitetura

```text
CaM é um cockpit local de soberania operacional:
usa o Profit para operar,
Python para governar,
React para visualizar,
dados locais para lembrar,
IA para analisar
e regras duras para impedir que coragem vire prejuízo.
```

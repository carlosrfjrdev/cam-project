---
template: SPEC
phase: SPEC
status: Draft
---

# SPEC — cam-cockpit · Cockpit Operacional Completo CaM

> **Data:** 2026-05-24
> **Status:** Draft — aguarda aprovação do Founder
> **Produto:** CaM Cockpit
> **Lead:** Albert · **Cross-cutting:** Kevin (SEC-GOV)
> **Aprovador:** Founder (Carlos Rodrigues Ferreira Junior)

---

## 1. Resumo

Esta SPEC especifica o cockpit operacional completo do CaM — todos os módulos, contratos, regras de negócio e critérios de aceite necessários para que o Founder saia da Fase 0 (Construção) e entre na Fase 1 (Paper Trading) da Constituição.

---

## 2. Referências de Entrada

- SCOPE: [`SCOPE.md`](./SCOPE.md) — aprovado em gate DISC
- DVP: [`DVP.md`](./DVP.md)
- DAS: [`DAS.md`](./DAS.md)
- ADRs: ADR-001 a ADR-013 em [`adrs/`](./adrs/)
- Constituição: `/CONSTITUICAO.md` — lei suprema
- Stack Oficial: `/project/STACK-CAM-OFICIAL.md`

---

## 3. Classificação P/M/G

| Campo | Valor |
|---|---|
| **Classe** | **G (Grande)** |
| **Rationale** | Projeto completo com 9+ módulos funcionais distintos (Risk Engine, Journal, Ledger Fiscal, Harvest, Frontend, Integração Profit, Backtest Engine, IA Auditora, Alertas, Infraestrutura), cada um com contratos independentes, regras de negócio complexas e critérios de aceite próprios. Exige decomposição em TASKs no PLAN. |

---

## 4. Marcadores de Segurança

| Marcador | Aplicável | Justificativa |
|---|---|---|
| `sec` (check intrabloco no CODE) | **sim** | Risk Engine, kill switch, journal e parâmetros de POV são superfícies sensíveis em todos os módulos |
| `qa-sec` (QA-SEC no QA) | **sim** | Arts. 34º–36º: IA sem autoridade; Risk Engine sem endpoint de parametrização por IA; credenciais Profit/Telegram/Anthropic |

Kevin entra como cross-cutting em CODE e QA-SEC.

**Gatilhos SEC-GOV específicos do CaM** (além dos 9 canônicos do NCC-1701):
- Qualquer código que toque o Risk Engine ou seus validators
- Qualquer código que toque o kill switch
- Qualquer código que toque o journal, ledger fiscal ou provisão de imposto
- Qualquer código que expanda autoridade da IA além de read-only

---

## 5. Módulo 1 — Risk Engine (`cam/_shared/risk/`)

### 5.1 Regras de Negócio

- **R1.01** O Risk Engine recebe `OrderCandidate` + `RiskContext` e retorna `RiskDecision: Approved | Rejected(reason: str)`
- **R1.02** O Risk Engine é Pure Python — Zero I/O. Não faz queries ao banco, não lê arquivos, não chama APIs
- **R1.03** Toda feature que valide operação chama `from cam._shared.risk import engine` — nenhuma feature duplica validator
- **R1.04** O Risk Engine é a única fonte de verdade sobre regras operacionais — nenhuma exceção é aceita sem emenda constitucional formal
- **R1.05** Toda decisão do Risk Engine é registrada em `cam_risk_decisions` com timestamp e motivo (se Rejected)
- **R1.06** O Risk Engine executa validators na seguinte ordem (primeiro Rejected termina a validação):
  1. `kill_switch_active_check` — se ativo, bloqueia tudo
  2. `pre_market_checklist_check` — checklist pré-mercado do dia deve estar preenchido
  3. `post_market_checklist_check` — bloqueia se checklist do pregão anterior ausente
  4. `tax_compliance_check` — DARF atrasada bloqueia (Art. 26º)
  5. `phase_authorization_check` — estratégia deve estar autorizada na fase atual
  6. `max_contracts_check` — nunca > 2 WIN ou > 2 WDO (Art. 11º — INTOCÁVEL)
  7. `phase_contracts_check` — Fase 2: max 1 contrato; sem WIN+WDO simultâneo
  8. `simultaneous_position_check` — WIN+WDO simultâneo vetado na Fase 1 e 2
  9. `daily_loss_limit_check` — P&L do dia ≤ -3% do capital total (R$ 150,00)
  10. `weekly_loss_limit_check` — P&L da semana ≤ -7% do capital total (R$ 350,00)
  11. `monthly_loss_limit_check` — P&L do mês ≤ -15% do capital total (R$ 750,00) — congela fase
  12. `gain_lock_check` — P&L do dia ≥ +2% do capital total (R$ 100,00) — encerra dia
  13. `daily_operations_count_check` — max 3 ops (Fase 1-2), max 5 ops (Fase 3-4)
  14. `martingale_check` — proibido aumentar contratos imediatamente após loss (Art. 13º)
  15. `trading_window_check` — vedado nos primeiros 15min pós-abertura e últimos 10min pré-fechamento
  16. `setup_a_plus_check` — 2 contratos permitidos APENAS em Setup A+ (Fase 4+)
  17. `circuit_breaker_check` — configurável; padrão off
- **R1.07** Parâmetros do Risk Engine (limites de perda, gain lock, contagem de operações) são lidos da POV vigente (`cam_pov_versions`) — não hardcoded além dos limites absolutamente invioláveis (Art. 11º)
- **R1.08** O limite absoluto de 2 contratos WIN / 2 WDO (Art. 11º) é hardcoded e não pode ser sobrescrito por POV

### 5.2 Contrato da Interface

```python
# cam/_shared/risk/engine.py

@dataclass
class OrderCandidate:
    asset: AssetType          # WIN | WDO
    direction: Direction      # LONG | SHORT
    quantity: ContractCount   # número de contratos a operar
    strategy_id: str
    proposed_stop_loss: Money

@dataclass
class RiskContext:
    phase: Phase                          # Fase 0–4 atual
    daily_pnl: Money                      # P&L líquido do dia (negativo = loss)
    weekly_pnl: Money                     # P&L líquido da semana
    monthly_pnl: Money                    # P&L líquido do mês
    total_capital: Money                  # Capital total declarado (R$ 5.000)
    open_positions: list[OpenPosition]    # posições abertas no momento
    daily_operations_count: int           # operações já executadas hoje
    last_operation_pnl: Money | None      # resultado da última operação (para martingale)
    kill_switch_active: bool
    pre_market_checklist_done: bool       # Art. 32º
    post_market_checklist_done: bool      # Art. 33º (do pregão anterior)
    tax_compliance: bool                  # False se DARF atrasada (Art. 26º)
    strategy_authorized: bool             # estratégia autorizada na fase atual (Art. 30º)
    current_time: datetime                # para trading_window_check
    is_setup_a_plus: bool                 # sinalizador Setup A+ (Fase 4 apenas)

class RiskDecision(Protocol):
    pass

@dataclass
class Approved(RiskDecision):
    pass

@dataclass
class Rejected(RiskDecision):
    reason: str
    validator: str                        # qual validator rejeitou

def validate(candidate: OrderCandidate, context: RiskContext) -> RiskDecision:
    ...
```

### 5.3 Critérios de Aceite — Risk Engine

| CA# | Cenário | Esperado |
|---|---|---|
| CA1.1 | Operação com 3 WIN solicitada | Rejected — `max_contracts_check` — "Art. 11º: máximo 2 contratos WIN" |
| CA1.2 | Operação com 1 WIN em Fase 2 com 1 WIN já aberto | Rejected — `phase_contracts_check` — "Art. 12º: máximo 1 contrato em Fase 2" |
| CA1.3 | Operação com P&L do dia = -R$ 150,01 | Rejected — `daily_loss_limit_check` — "Art. 16º: limite diário atingido" |
| CA1.4 | Operação com P&L do dia = +R$ 100,00 | Rejected — `gain_lock_check` — "Art. 17º: gain lock — dia encerrado" |
| CA1.5 | Operação com kill switch ativo | Rejected — `kill_switch_active_check` — "Art. 18º: kill switch ativo" |
| CA1.6 | Operação com DARF atrasada (tax_compliance=False) | Rejected — `tax_compliance_check` — "Art. 26º: DARF atrasada" |
| CA1.7 | Operação em janela vedada (14min após abertura) | Rejected — `trading_window_check` — "POV: janela vedada pós-abertura" |
| CA1.8 | Aumento de contratos após loss com martingale | Rejected — `martingale_check` — "Art. 13º: proibido aumentar após loss" |
| CA1.9 | Operação válida em todos os validators | Approved |
| CA1.10 | WIN + WDO simultâneo em Fase 2 | Rejected — `simultaneous_position_check` |
| CA1.11 | 4ª operação do dia em Fase 1 | Rejected — `daily_operations_count_check` |
| CA1.12 | Checklist pré-mercado não preenchido | Rejected — `pre_market_checklist_check` |
| CA1.13 | Checklist pós-mercado do pregão anterior ausente | Rejected — `post_market_checklist_check` |
| CA1.14 | Property test: geração de 10.000 cenários adversos aleatórios | Nenhum cenário produz Approved quando viola Art. 11º |

---

## 6. Módulo 2 — Journal (`cam/features/journal/`)

### 6.1 Regras de Negócio

- **R2.01** Toda operação executada DEVE ter um `JournalEntry` correspondente — sem exceção (Art. 31º)
- **R2.02** O campo `resultado_liquido` é calculado como: `resultado_bruto - custos_corretagem - imposto_provisionado`
- **R2.03** Nenhuma visualização do journal exibe `resultado_bruto` sem exibir junto `resultado_liquido` (Art. 25º)
- **R2.04** `imposto_provisionado` = 20% do `resultado_bruto` quando positivo; 0 quando negativo (Day Trade IR)
- **R2.05** Campos obrigatórios para salvar um `JournalEntry`: ativo, direção, contratos, timestamp_entrada, timestamp_saida, preco_entrada, preco_saida, resultado_bruto, custos, resultado_liquido, imposto_provisionado, estrategia, setup, aderencia_regra (boolean), notas
- **R2.06** Campos opcionais: observacao_emocional, licao_aprendida
- **R2.07** Um `JournalEntry` uma vez criado é **imutável** — não pode ser editado ou deletado (audit trail)
- **R2.08** Correções de erro são registradas como `JournalCorrection` com referência ao entry original
- **R2.09** Journal publica evento `JournalEntryCreated` após persistência — fiscal/ e harvest/ consomem este evento
- **R2.10** Relatórios disponíveis: diário, semanal, mensal, por estratégia, por ativo, por aderência
- **R2.11** Exportação CSV/JSON para auditoria externa disponível (sem PII adicional)

### 6.2 Schema Principal

```python
class JournalEntry(BaseModel):
    id: UUID
    ativo: AssetType           # WIN | WDO
    direcao: Direction         # LONG | SHORT
    contratos: ContractCount
    timestamp_entrada: datetime
    timestamp_saida: datetime
    preco_entrada: Money
    preco_saida: Money
    resultado_bruto: Money
    custos_corretagem: Money
    imposto_provisionado: Money
    resultado_liquido: Money   # = bruto - custos - imposto
    estrategia: str
    setup: str
    aderencia_regra: bool
    notas: str
    observacao_emocional: str | None
    licao_aprendida: str | None
    created_at: datetime
    fonte: JournalSource       # MANUAL | CSV_IMPORT | NTSL_CALLBACK
```

### 6.3 Endpoints da Feature

```
POST   /api/v1/journal/entries           # criar entry (manual)
GET    /api/v1/journal/entries           # listar (filtros: data, ativo, estrategia, aderencia)
GET    /api/v1/journal/entries/{id}      # detalhe
POST   /api/v1/journal/import-csv        # importar CSV do Profit
GET    /api/v1/journal/reports/daily     # relatório diário
GET    /api/v1/journal/reports/weekly    # relatório semanal
GET    /api/v1/journal/reports/monthly   # relatório mensal
GET    /api/v1/journal/reports/by-strategy  # por estratégia
GET    /api/v1/journal/export            # exportar CSV/JSON
```

### 6.4 Critérios de Aceite — Journal

| CA# | Cenário | Esperado |
|---|---|---|
| CA2.1 | Criar JournalEntry com todos campos obrigatórios | HTTP 201; entry persistido em cam_journal_entries; evento JournalEntryCreated publicado |
| CA2.2 | Criar JournalEntry sem campo obrigatório | HTTP 422; mensagem de validação explicando campo faltante |
| CA2.3 | Tentar editar JournalEntry existente | HTTP 405 ou 403; entry permanece inalterado |
| CA2.4 | Relatório diário com 3 entradas do dia | Retorna as 3 entradas com resultado_liquido calculado corretamente |
| CA2.5 | resultado_bruto positivo → imposto_provisionado = 20% | Valor calculado e persistido corretamente |
| CA2.6 | resultado_bruto negativo → imposto_provisionado = 0 | Sem provisão fiscal em dia de loss |
| CA2.7 | Importação CSV do Profit com 5 trades | 5 JournalEntries criados; nenhum duplicado se reimportado |
| CA2.8 | Exportação da semana | Arquivo CSV gerado com todos os campos; resultado_bruto e resultado_liquido ambos presentes |

---

## 7. Módulo 3 — Ledger Fiscal (`cam/features/fiscal/`)

### 7.1 Regras de Negócio

- **R3.01** IR Day Trade: alíquota 20% sobre lucro mensal líquido (Art. 24º)
- **R3.02** IRRF: 1% retido na fonte como antecipação — deduzido do DARF a pagar
- **R3.03** DARF mensal gerada automaticamente após apuração do mês com resultado positivo
- **R3.04** Status de DARF: `PENDING` | `PAID` | `OVERDUE` (gerado automaticamente se não paga após vencimento)
- **R3.05** DARF com status `OVERDUE` dispara `tax_compliance = False` no RiskContext → Risk Engine bloqueia operação (Art. 26º)
- **R3.06** Compensação de prejuízo: saldo compensável = soma de resultados líquidos negativos do período — deduzido do base de cálculo do IR mensal (Art. 27º)
- **R3.07** Saldo compensável deve ser exibido explicitamente na UI de fiscal
- **R3.08** Provisão fiscal é atualizada em tempo real a cada novo JournalEntry (consumindo evento JournalEntryCreated)
- **R3.09** A apuração mensal usa janela M1 (primeiro dia do mês) a M-último (último dia útil)
- **R3.10** Resultado fiscal exibido na UI: sempre líquido de imposto provisionado + saldo compensável visível

### 7.2 Endpoints da Feature

```
GET    /api/v1/fiscal/current-month      # apuração do mês corrente (provisório)
GET    /api/v1/fiscal/apurations         # histórico de apurações mensais
GET    /api/v1/fiscal/darfs              # histórico de DARFs
PATCH  /api/v1/fiscal/darfs/{id}/mark-paid  # marcar DARF como paga
GET    /api/v1/fiscal/compensation-balance  # saldo compensável atual
GET    /api/v1/fiscal/summary            # resumo fiscal para a UI operacional
```

### 7.3 Critérios de Aceite — Ledger Fiscal

| CA# | Cenário | Esperado |
|---|---|---|
| CA3.1 | Lucro bruto R$ 500 no mês com IRRF de R$ 50 retido | DARF = R$ 500 × 20% - R$ 50 = R$ 50 a pagar |
| CA3.2 | Resultado negativo no mês | Sem DARF; saldo compensável atualizado |
| CA3.3 | DARF não paga após vencimento | Status OVERDUE; RiskContext.tax_compliance = False; Risk Engine bloqueia |
| CA3.4 | Operador marca DARF como paga | Status PAID; RiskContext.tax_compliance = True; Risk Engine desbloqueia |
| CA3.5 | Compensação: -R$ 200 no mês anterior, +R$ 300 no mês atual | Base de cálculo = R$ 300 - R$ 200 = R$ 100; DARF = R$ 20 |
| CA3.6 | UI exibe resultado do mês | Exibe resultado_liquido = resultado_bruto × (1 - 0.20); nunca exibe apenas bruto sem dedução |

---

## 8. Módulo 4 — Harvest Rule e Ledger de Capital (`cam/features/harvest/` + `cam/features/ledger/`)

### 8.1 Regras de Negócio

- **R4.01** Harvest Rule ocorre em janela mensal pós-apuração fiscal — não diariamente (Art. 21º)
- **R4.02** Base de cálculo do harvest: lucro_liquido_mensal - imposto_pago_no_mes
- **R4.03** Distribuição do harvest:
  - 60% → Carteira Hard
  - 40% → Buffer Operacional (somente até restaurar linha de base R$ 1.000,00)
  - Após Buffer restaurado: 100% excedente → Carteira Hard
- **R4.04** Sangria do Bucket Derivativo disparada automaticamente quando bucket ≥ R$ 4.500,00:
  - Excedente = valor_bucket - R$ 3.000 (base)
  - 80% do excedente → Carteira Hard
  - 20% do excedente → Buffer Operacional / Provisão Fiscal
  - Bucket retorna a R$ 3.000,00
- **R4.05** Toda movimentação entre buckets é registrada em `cam_bucket_transactions` com timestamp, origem, destino e valor
- **R4.06** O saldo de cada bucket é calculado como: saldo_inicial + entradas - saídas (recalculado das transações)
- **R4.07** Harvest não é automático — o sistema **propõe** a distribuição e exibe para o Founder aprovar; a execução requer confirmação explícita

### 8.2 Endpoints da Feature

```
GET    /api/v1/ledger/buckets                # saldos atuais dos 3 buckets
GET    /api/v1/ledger/transactions           # histórico de movimentações
GET    /api/v1/harvest/proposal              # proposta de harvest do mês
POST   /api/v1/harvest/execute               # executar harvest (gate Founder)
GET    /api/v1/harvest/history               # histórico de harvests executados
GET    /api/v1/ledger/carteira-hard/snapshot # snapshot patrimonial
```

### 8.3 Critérios de Aceite — Harvest

| CA# | Cenário | Esperado |
|---|---|---|
| CA4.1 | Buffer a R$ 800 (abaixo da linha de base); lucro líquido pós-fiscal = R$ 500 | Proposta: 40% × R$ 500 = R$ 200 → Buffer (sobe para R$ 1.000); 60% × R$ 500 = R$ 300 → Carteira Hard |
| CA4.2 | Buffer a R$ 1.000 (linha de base); lucro líquido pós-fiscal = R$ 500 | Proposta: 100% × R$ 500 = R$ 500 → Carteira Hard |
| CA4.3 | Bucket Derivativo = R$ 4.600 | Sangria automática proposta: excedente R$ 1.600; R$ 1.280 → Carteira Hard; R$ 320 → Buffer; Bucket retorna a R$ 3.000 |
| CA4.4 | Founder rejeita proposta de harvest | Harvest não executado; proposta arquivada; novo pregão não bloqueado |
| CA4.5 | Founder aprova harvest | Transações registradas em cam_bucket_transactions; saldos atualizados |

---

## 9. Módulo 5 — Frontend Operacional (`frontend/src/features/`)

### 9.1 Regras de Negócio

- **R5.01** O kill switch DEVE estar visível e acessível em TODA tela operacional (Art. 18º) — componente global persistente
- **R5.02** Nenhuma tela do cockpit exibe P&L bruto sem o correspondente P&L líquido (Art. 25º)
- **R5.03** O kill switch requer confirmação dupla para ativação via UI (prevenção de acionamento acidental)
- **R5.04** O status do Risk Engine (ATIVO / BLOQUEADO + motivo) é exibido no header de toda tela operacional
- **R5.05** Quando kill switch ativo, o frontend exibe banner de alerta vermelho persistente
- **R5.06** Parâmetros do Risk Engine são exibidos como read-only na UI — sem campo editável para IA
- **R5.07** A tela da Constituição é read-only — sem edição inline

### 9.2 Telas Obrigatórias

| Tela | Funcionalidade Principal | Art. Constitucional |
|---|---|---|
| **Cockpit Live** | P&L líquido em tempo real, posições, gauges de limites, kill switch | Arts. 15º, 17º, 18º, 25º |
| **Journal** | Listagem de entries, filtros, criação manual, importação CSV | Art. 31º |
| **Ledger Fiscal** | Apuração mensal, DARFs, compensação, alertas de vencimento | Arts. 24º–27º |
| **Harvest** | Proposta de distribuição, histórico de execuções, saldos de buckets | Arts. 21º–22º |
| **Risk Console** | POV vigente, log de decisões do Risk Engine, audit trail | Arts. 15º, 29º |
| **Backtest** | Configurar, executar, comparar resultados, walk-forward | Art. 28º |
| **Paper Trading** | Mesma UI do Live com badge "PAPER" em vermelho — claramente simulação | Anexo II Fase 0 |
| **Carteira Hard** | Snapshot patrimonial, dividendos, harvest history | Art. 23º |
| **Constituição** | Visualização read-only, histórico de versões, proposta de emenda | Arts. 37º–40º |
| **Configurações** | Conexão Profit, Telegram, paths — sem parâmetros do Risk Engine editáveis | Art. 35º |

### 9.3 Critérios de Aceite — Frontend

| CA# | Cenário | Esperado |
|---|---|---|
| CA5.1 | Abrir qualquer tela operacional | Kill switch visível e clicável |
| CA5.2 | P&L do dia = +R$ 80 (bruto) com imposto = R$ 16 | Exibe: Bruto R$ 80 / Líquido R$ 64 — nunca apenas R$ 80 |
| CA5.3 | Kill switch ativo | Banner vermelho em todas as telas; Risk Engine status "BLOQUEADO — Kill Switch" |
| CA5.4 | Tentar clicar em parâmetro do Risk Engine para editar | Campo é read-only — sem edição possível |
| CA5.5 | Paper Trading ativo | Badge "SIMULAÇÃO" grande e vermelho visível em toda a tela |
| CA5.6 | DARF overdue | Alerta amarelo/vermelho na tela de Fiscal e no header do cockpit |

---

## 10. Módulo 6 — Integração Profit/Nelogica (`cam/features/profit_integration/`)

### 10.1 Regras de Negócio

- **R6.01** Em Fase F1, a integração é zero — o backend apenas valida intenção via Risk Engine e Carlos opera manualmente
- **R6.02** Em Fase F2, o importador CSV aceita o extrato padrão do Profit (formato CSV definido na SPEC de demanda específica quando F2 for iniciada)
- **R6.03** O importador CSV detecta duplicatas e não reimporta a mesma operação
- **R6.04** A reconciliação F2 exibe lado-a-lado: journal manual de Carlos × operações importadas do Profit
- **R6.05** Em Fase F4, a estratégia NTSL deve ler os parâmetros publicados pelo CaM (kill switch ativo, fase atual, Setup A+ autorizado) antes de cada ciclo de operação
- **R6.06** O Risk Engine Python é pré-validador primário — NTSL é segunda linha de defesa (ADR-009)
- **R6.07** Callbacks de ordens executadas pelo Profit (F4) disparam criação automática de JournalEntry

### 10.2 Critérios de Aceite — Integração Profit

| CA# | Cenário | Esperado |
|---|---|---|
| CA6.1 | Importação de CSV com 10 trades; reimportação do mesmo CSV | 10 JournalEntries criados na primeira importação; 0 duplicatas na segunda |
| CA6.2 | CSV com formato inválido importado | HTTP 422; nenhum entry criado; mensagem de erro descritiva |
| CA6.3 | Reconciliação F2: 1 operação manual vs 1 no CSV com mesmo horário | Sistema identifica as como provavelmente a mesma; exibe para confirmação do operador |

---

## 11. Módulo 7 — Backtest Engine (`cam/features/backtest/`)

### 11.1 Regras de Negócio

- **R7.01** O backtest usa o MESMO Risk Engine (`cam/_shared/risk/`) que o ambiente live — sem parâmetros diferentes (DRY constitucional)
- **R7.02** O backtest NÃO pode ser executado com o Risk Engine desligado ou com limites mais permissivos que a fase simulada — isso violaria a honestidade do backtest
- **R7.03** Os custos de corretagem são incluídos obrigatoriamente no cálculo do backtest
- **R7.04** O IR Day Trade (20%) é provisionado sobre os resultados simulados do backtest
- **R7.05** O backtest opera sobre dados de `cam_market_ticks` (hypertable TimescaleDB)
- **R7.06** Métricas obrigatórias de resultado: P&L total, Sharpe ratio, max drawdown, win rate, fator de lucro, distribuição de resultados, número de operações, aderência às regras
- **R7.07** Walk-forward: validação com parâmetros otimizados em janela A aplicados em janela B (sem data snooping)
- **R7.08** Resultados de backtest são persistidos em `cam_backtest_runs` + `cam_backtest_trades`
- **R7.09** DuckDB pode ser usado para research exploratório em CSV/Parquet antes de carregar dados no Timescale

### 11.2 Critérios de Aceite — Backtest

| CA# | Cenário | Esperado |
|---|---|---|
| CA7.1 | Backtest com limit de contracts acima de 2 configurado | Backtest recusa configuração; exibe "Art. 11º: máximo 2 contratos" |
| CA7.2 | Backtest com custos de corretagem = 0 | Sistema alerta que custos zerados podem produzir expectância irreal; permite mas exibe aviso |
| CA7.3 | Backtest com 1000 trades simulados | Relatório com todas as 7 métricas obrigatórias calculadas corretamente |
| CA7.4 | Walk-forward executado com janela A = Jan-Jun, B = Jul-Dez | Resultado separado por janela; degradação entre janelas calculada |
| CA7.5 | Tentativa de rodar backtest com Risk Engine "desligado" | Operação não disponível na UI — nenhuma configuração desabilita o Risk Engine no backtest |

---

## 12. Módulo 8 — IA Auditora (`cam/features/ai_analyst/`)

### 12.1 Regras de Negócio

- **R8.01** A IA tem acesso somente leitura a `cam_journal_entries`, `cam_risk_decisions`, `cam_violations` (Art. 35º)
- **R8.02** A IA não tem acesso a nenhum endpoint de escrita ou parametrização do Risk Engine
- **R8.03** O job de análise pós-mercado roda como processo separado do backend live (CLI ou scheduler isolado)
- **R8.04** Dados enviados para Anthropic API são anonimizados (sem nome do operador, sem CPF, sem valores absolutos de capital quando não necessário para a análise)
- **R8.05** Ollama local é o provider padrão para análises com dados sensíveis
- **R8.06** A análise é enviada via Telegram ao operador e salva em banco (read-only para o cockpit)
- **R8.07** A IA NUNCA gera recomendação de entrada ou saída de posição no mercado (Art. 35º)
- **R8.08** A IA NUNCA justifica exceção a regra constitucional (Art. 35º)
- **R8.09** O prompt enviado à IA inclui explicitamente: "Você é uma IA auditora. Não pode recomendar trades, não pode sugerir contornar regras de risco, não pode emitir opinião sobre oportunidades de mercado."

### 12.2 Critérios de Aceite — IA Auditora

| CA# | Cenário | Esperado |
|---|---|---|
| CA8.1 | Job pós-mercado roda sem erros | Análise gerada; enviada via Telegram; salva em banco |
| CA8.2 | Análise tenta sugerir trade | Verificação pós-análise detecta conteúdo proibido; análise é descartada com log de violação |
| CA8.3 | Análise tenta justificar exceção constitucional | Idem CA8.2 |
| CA8.4 | Anthropic API indisponível | Fallback para Ollama local; sem falha do processo principal |
| CA8.5 | Dados enviados para Anthropic API | Auditoria confirma que nenhum dado de identificação pessoal ou capital absoluto está presente |

---

## 13. Módulo 9 — Alertas Telegram (`cam/features/notifications/`)

### 13.1 Regras de Negócio

- **R9.01** O bot Telegram publica alertas para os eventos listados na DAS §4.5
- **R9.02** Alertas críticos (kill switch, loss limit) são enfileirados com retry exponencial se Telegram estiver indisponível
- **R9.03** Falha no envio de alerta NÃO afeta o estado do cockpit — o cockpit permanece no estado correto independentemente do canal de alerta
- **R9.04** O token do bot e o chat_id do operador são lidos de variáveis de ambiente (nunca no código)
- **R9.05** Somente o chat_id configurado do operador recebe mensagens

### 13.2 Critérios de Aceite — Alertas

| CA# | Cenário | Esperado |
|---|---|---|
| CA9.1 | Kill switch ativado | Mensagem Telegram enviada em < 5 segundos |
| CA9.2 | Limite diário de loss atingido | Mensagem com P&L do dia e confirmação de bloqueio |
| CA9.3 | Telegram indisponível por 5 minutos | Alertas enfileirados; enviados quando Telegram volta; cockpit não é afetado |
| CA9.4 | Token de bot não configurado | Sistema inicia sem Telegram (modo degradado); log de aviso; sem crash |

---

## 14. Módulo 10 — Checklists Pré e Pós Mercado (`cam/features/checklists/`)

### 14.1 Regras de Negócio

- **R10.01** Checklist pré-mercado obrigatório antes de qualquer operação do dia (Art. 32º) — sem ele, `pre_market_checklist_check` rejeita
- **R10.02** Checklist pós-mercado obrigatório após último pregão do dia (Art. 33º) — sem ele, `post_market_checklist_check` rejeita no próximo pregão
- **R10.03** Itens obrigatórios do checklist pré-mercado: sistema funcionando, Profit funcionando, conexão estável, plataforma sem erro, limite diário configurado, contrato máximo respeitado, estratégia habilitada, Risk Engine ativo, kill switch disponível, plano do dia registrado
- **R10.04** Itens obrigatórios do checklist pós-mercado: resultado do dia, número de operações, aderência, violações, falhas técnicas, estado emocional, aprendizado, decisão sobre harvest, ledger atualizado, atualização fiscal
- **R10.05** O checklist não pode ser marcado como completo sem que todos os itens obrigatórios estejam preenchidos

### 14.2 Critérios de Aceite — Checklists

| CA# | Cenário | Esperado |
|---|---|---|
| CA10.1 | Operação sem checklist pré-mercado do dia | Risk Engine retorna Rejected — `pre_market_checklist_check` |
| CA10.2 | Operação no dia seguinte sem checklist pós-mercado do pregão anterior | Risk Engine retorna Rejected — `post_market_checklist_check` |
| CA10.3 | Checklist pré-mercado preenchido com todos os itens | `pre_market_checklist_done = True` no RiskContext; operações permitidas |
| CA10.4 | Tentar salvar checklist com item obrigatório em branco | HTTP 422; checklist não salvo |

---

## 15. Módulo 11 — Infraestrutura Local (`docker-compose.yml`, scripts, migrations)

### 15.1 Regras de Negócio

- **R11.01** Docker Compose com `timescale/timescaledb:latest-pg16` e Redis (opcional) — funcional com `docker compose up -d`
- **R11.02** Migration inicial inclui `CREATE EXTENSION IF NOT EXISTS timescaledb` e criação de todas as hypertables
- **R11.03** Continuous aggregates criados como `MATERIALIZED VIEW ... WITH (timescaledb.continuous)` para todos os timeframes de candle
- **R11.04** `pg_dump` backup diário automatizado: Linux via cron, Windows via Task Scheduler
- **R11.05** `rclone` sync noturno para Google Drive (configurável)
- **R11.06** Journal duplo: banco + JSONL append-only em `~/.cam/journal/YYYY-MM-DD.jsonl`
- **R11.07** `backend/.env.example` documenta todas as variáveis de ambiente com placeholder sem valor real
- **R11.08** `.gitignore` inclui `.env`, `*.jsonl` de journal, `cam-backups/`
- **R11.09** Script de setup Linux: `scripts/dev.sh` — instala deps, cria banco, roda migrations
- **R11.10** Script de setup Windows: `scripts/dev.ps1` — equivalente para PowerShell

### 15.2 Critérios de Aceite — Infraestrutura

| CA# | Cenário | Esperado |
|---|---|---|
| CA11.1 | `docker compose up -d` em Linux limpo | Postgres+Timescale sobe; porta 5432 acessível; extensão TimescaleDB ativa |
| CA11.2 | `alembic upgrade head` em banco limpo | Todas as tabelas criadas; hypertables configuradas; continuous aggregates criados |
| CA11.3 | JournalEntry criado | Persiste em cam_journal_entries E em ~/.cam/journal/YYYY-MM-DD.jsonl |
| CA11.4 | `.env` commitado acidentalmente | pré-commit hook detecta e bloqueia o commit |

---

## 16. Saídas Esperadas (Entregáveis Fase 0)

O cam-cockpit em Fase 0 deve produzir:

1. **Repositório `apps/cam-cockpit/`** com estrutura monorepo completa (ADR-011)
2. **Backend Python** com todos os módulos em `cam/features/` + `cam/_shared/risk/`
3. **Risk Engine** com todos os 17 validators e cobertura de testes ≥ 80% (critério Fase 0, Constituição Anexo II)
4. **Frontend React** com as 10 telas obrigatórias
5. **Banco Postgres+Timescale** com schema completo, hypertables e continuous aggregates
6. **Backtest Engine** funcional com Risk Engine ativo
7. **Paper Trading** funcional com as mesmas regras do live
8. **Kill switch** validado em teste real (não apenas unitário)
9. **Telegram Bot** com todos os alertas críticos
10. **Scripts de setup** para Linux e Windows

---

## 17. Critérios de Aceite de Gate — Saída de Fase 0

Para avançar da Fase 0 para a Fase 1 (Paper Trading), o Founder valida:

| Critério | Verificação |
|---|---|
| Cockpit funcional end-to-end | Fluxo completo: checklist → Risk Engine → Journal → Fiscal → Harvest em teste de integração |
| Risk Engine cobertura ≥ 80% | `pytest --cov=cam/_shared/risk/ --cov-report=term` mostra ≥ 80% |
| Kill switch validado em teste real | Kill switch ativado, operação bloqueada, Telegram alertado, desativado — em ambiente de integração |
| Backtest funcional com Risk Engine | Backtest de 100 trades simulados com all validators ativos completa sem erro |
| Paper trading funcional | 10 operações simuladas completas: desde checklist até journal + fiscal |
| DARF bloqueio funcional | Simulação de DARF overdue → operação bloqueada pelo Risk Engine |
| Journal duplo funcional | JournalEntry persistido no banco E no JSONL local |
| Zero credenciais no código | `git log` não contém nenhuma chave, token ou senha |

---

## 18. Histórico

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1 | 2026-05-24 | Draft inicial — produzido via NCC-1701 SPEC | — (aguarda Founder) |

---

> **Gate de aprovação SPEC:** Founder valida esta especificação antes de avançar para PLAN.
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______
>
> **Nota ao Founder:** Esta SPEC é classificada como G (Grande). O PLAN (Nico) irá decompor em TASKs para implementação por blocos. Nico tem direito formal de contestar a classificação G — se isso ocorrer, o loop Albert-Nico é acionado e você decide quando parar.

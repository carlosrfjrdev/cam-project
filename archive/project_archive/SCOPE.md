---
template: SCOPE
phase: DISC
status: Draft
---

# SCOPE — cam-cockpit · Cockpit Operacional CaM

> **Data:** 2026-05-24
> **Status:** Draft — aguarda aprovação do Founder
> **Produto:** CaM Cockpit
> **Lead:** Marty (DISC)
> **Solicitante:** Founder (Carlos Rodrigues Ferreira Junior)

---

## 1. Problema

Carlos opera (ou operará) mini índice WIN e mini dólar WDO na B3 via Profit/Nelogica. O risco do operador não é o mercado — é ele mesmo em estado de convicção excessiva, ganância, medo ou pressa (Preâmbulo da Constituição). Sem um cockpit sistêmico que interponha controles duros entre a intenção do operador e a execução, toda regra disciplinar vira intenção sem enforcement. O CaM precisa de software que torne as regras constitucionais não-contornáveis.

---

## 2. Usuário / Contexto

**Usuário único:** Carlos Rodrigues Ferreira Junior, trader individual B3.

**Contexto operacional:**
- Ativos: WIN (mini índice Bovespa) e WDO (mini dólar)
- Plataforma de execução: Profit Pro ou Profit Ultra (Nelogica) — Windows-only
- Capital declarado: R$ 5.000 segregados em três buckets (Art. 10º)
- Fase atual do CaM: Fase 0 — Construção (sem trade real, sem paper trading)
- Ambiente de desenvolvimento: Linux; produção: Windows 11
- Uso: local, pessoal, mono-usuário, sem conexão à internet para operações críticas

**Quando o problema aparece:**
- Antes de operar: Carlos precisa de checklist validado e Risk Engine ativo
- Durante operação: P&L líquido visível em tempo real, kill switch acessível imediatamente
- Após operar: journal obrigatório registrado, ledger fiscal atualizado, harvest calculado
- Diariamente: cockpit pronto para ser o árbitro entre intenção e execução

---

## 3. Resultado Esperado

Quando o cam-cockpit estiver entregue:

1. Carlos não consegue executar operação se o Risk Engine bloquear (Art. 15º)
2. Toda operação está registrada no journal imediatamente (Art. 31º)
3. O frontend exibe P&L LÍQUIDO com imposto provisionado — nunca bruto (Art. 25º)
4. O kill switch interrompe tudo imediatamente, sem confirmação complexa (Art. 18º)
5. DARF atrasada bloqueia novas operações automaticamente (Art. 26º)
6. O backtest engine usa o mesmo Risk Engine do ambiente live (princípio DRY)
7. A Harvest Rule é calculada automaticamente após apuração mensal (Art. 21º)
8. A IA analisa o journal pós-mercado sem jamais ter autoridade de execução (Arts. 34º–36º)
9. Carlos pode fazer paper trading com as mesmas regras da operação real (Critério Fase 0)

---

## 4. Dentro (In)

### 4.1 Risk Engine (núcleo constitucional)
- Validação de toda candidata a operação contra regras dos Arts. 11º–20º
- Validators: limite de contratos, limite de perda diária/semanal/mensal, gain lock, operações máximas por dia, anti-martingale, janelas vedadas, posição simultânea WIN+WDO por fase, kill switch ativo, DARF atrasada, checklist pré-mercado não preenchido
- Pure Python sem I/O — testado 100% com property-based testing (hypothesis)
- Shared Kernel: `cam/_shared/risk/` — toda feature consulta este módulo, nenhuma duplica regra

### 4.2 Journal Operacional (Art. 31º)
- Registro obrigatório de toda operação (manual + automático via integração Profit)
- Campos obrigatórios completos: ativo, direção, contratos, entrada, saída, resultado bruto, custos, resultado líquido, imposto provisionado, timestamp, estratégia, setup, aderência, notas emocionais, lição
- Importação de CSV/extrato Profit (Fase F2 de integração)
- Relatórios: diário, semanal, mensal, por estratégia, por ativo
- Exportação para auditoria

### 4.3 Ledger Fiscal (Arts. 24º–27º)
- Provisão automática de IR Day Trade (20% sobre lucro mensal líquido)
- IRRF 1% retido na fonte como antecipação
- Geração e controle de DARFs (histórico, status pago/pendente/atrasado)
- Bloqueio operacional automático quando DARF atrasada (Art. 26º)
- Compensação de prejuízo acumulado (Art. 27º — saldo compensável visível)
- Resultado sempre exibido líquido de imposto provisionado

### 4.4 Harvest Rule e Ledger de Capital (Arts. 21º–22º)
- Cálculo automático da distribuição mensal pós-apuração fiscal
- 60% do lucro líquido → Carteira Hard; 40% → Buffer Operacional (até linha de base R$ 1.000)
- Sangria do Bucket Derivativo quando atinge R$ 4.500: 80% → Carteira Hard, 20% → Buffer/Provisão
- Rastreamento dos três buckets (Derivativo, Buffer, Carteira Hard) com histórico de movimentações

### 4.5 Frontend Operacional (Art. 25º)
- Dashboard principal (Cockpit Live): P&L líquido em tempo real, posições, status Risk Engine, kill switch grande/vermelho/confirmação dupla, gauges de limite diário/semanal/mensal
- Painel Journal: listagem com filtros, exportação
- Painel Ledger Fiscal: apuração, DARFs, compensação de prejuízo, alertas
- Painel Harvest: distribuição mensal, histórico dos buckets, Carteira Hard
- Painel Risk Console: POV vigente, log de decisões do Risk Engine, audit trail
- Painel Backtest: configurar, executar, comparar resultados, walk-forward
- Painel Paper Trading: mesma UI do Live com badge "PAPER" grande em vermelho
- Painel Constituição (read-only): visualização + histórico + botão "propor emenda" com cooldowns
- Painel Configurações: conexão Profit, Telegram, parâmetros (somente leitura para IA)
- Painel Carteira Hard: snapshot patrimonial, dividendos, harvest history
- Regra inviolável: NUNCA exibir resultado bruto sem o líquido correspondente

### 4.6 Integração Profit/Nelogica (faseada)
- F1: CaM gera checklist e Risk Engine valida; Carlos opera manualmente; registro manual no journal
- F2: Importação de CSV/extrato Profit pós-mercado; conciliação journal manual × execução real
- F3: Monitoramento do estado Profit em tempo real (status, P&L, posição) via export periódico
- F4: Estratégias em NTSL com regras de risco espelhadas + publicação de parâmetros pelo CaM
- Estratégias NTSL versionadas em `apps/cam-cockpit/ntsl/`

### 4.7 Backtest Engine
- Ingestão de ticks históricos via TimescaleDB (hipertabelas `cam_market_ticks`)
- DRY com Risk Engine e lógica de estratégia do ambiente live (mesmo código)
- Métricas: P&L, Sharpe ratio, max drawdown, win rate, fator de lucro, distribuição de resultados
- Walk-forward validation
- DuckDB como motor auxiliar para research exploratório em CSV/Parquet/Jupyter

### 4.8 IA Auditora (Arts. 34º–36º)
- Job assíncrono pós-mercado: lê journal do dia → gera análise → envia via Telegram
- Análise de aderência operacional, padrões de loss, anomalias comportamentais
- Sugestões de hipóteses de estudo (nunca recomendações de execução)
- Revisão de journal por Ollama local (dados sensíveis) ou Anthropic API (dados anonimizados)
- Interface read-only sobre dados operacionais — zero autoridade de execução

### 4.9 Alertas Telegram
- Kill switch ativado
- Limite diário/semanal/mensal de perda atingido
- Gain lock atingido (dia encerrado)
- DARF vencendo (aviso antecipado) ou atrasada (bloqueio ativo)
- Operação completada (confirmação)
- Falha técnica com posição aberta (Art. 19º)
- Análise IA pós-mercado

### 4.10 Checklists Pré e Pós Mercado (Arts. 32º–33º)
- Checklist pré-mercado obrigatório: sistema, Profit, conexão, Risk Engine ativo, etc.
- Checklist pós-mercado obrigatório: resultado, aderência, estado emocional, harvest decision
- Risk Engine bloqueia operação do próximo pregão se checklist pós-mercado ausente

### 4.11 Infraestrutura Local
- PostgreSQL 16 + TimescaleDB via Docker Compose
- Hypertables para tick data (cam_market_ticks, cam_market_book_snapshots)
- Continuous aggregates para candles em múltiplos timeframes (1s, 5s, 1m, 5m, 15m, 1h, 1d)
- Backup automatizado (pg_dump + rclone para Google Drive)
- Journal duplo: banco + JSONL append-only em disco local (fallback para falha catastrófica)
- Scripts de setup: Linux (bash) + Windows (PowerShell)
- .env para variáveis sensíveis (nunca commitadas)

### 4.12 Audit Trail Constitucional
- Registro imutável de toda decisão do Risk Engine (cam_risk_decisions)
- Registro de violações para cálculo de aderência (cam_violations)
- Histórico de versões da Constituição e POV
- Histórico de transições de fase
- Eventos de kill switch

---

## 5. Fora (Out)

O CaM **NÃO** faz as seguintes coisas — nenhuma delas será implementada neste projeto:

- **Execução autônoma de ordens** — a IA não envia ordem (Art. 35º); o CaM não substitui o Profit como broker de ordens no MVP
- **Gestão de carteira de renda variável** — a Carteira Hard é acompanhada como snapshot, não gerida ativamente pelo cockpit
- **Análise fundamentalista** — fora do domínio do cockpit operacional
- **Multi-usuário** — sem autenticação por usuário, sem tenant, sem compartilhamento
- **Cloud-first** — nenhum componente essencial depende de serviço externo
- **HFT (High-Frequency Trading)** — latência alvo dezenas de ms, não microssegundos
- **Cross-broker** — single venue (B3 via Profit); sem MT5, sem Interactive Brokers, sem API de corretora direta no MVP
- **Produto comercial** — sem pricing, sem distribuição, sem venda
- **Mobile** — cockpit local desktop; nenhuma interface mobile no escopo atual
- **SSR/Next.js** — frontend é SPA local; sem server-side rendering
- **Execução em outros ativos** — somente WIN e WDO; sem ações, opções, criptomoedas
- **Escalabilidade horizontal** — mono-host por design
- **Alertas por canais além do Telegram** — sem e-mail, WhatsApp, push notification
- **Reversão automática de posição** — o kill switch interrompe, não reverte automaticamente
- **Backtest em ativos fora da B3** — somente WIN e WDO

---

## 6. Depois (Later)

Funcionalidades conscientemente adiadas. Podem entrar em fases futuras mediante decisão formal do Founder:

- **F5 — ProfitDLL via ctypes**: integração Python↔Profit via DLL para controle fino (só se necessidade real comprovar — ADR-001 marca como Fase 4+)
- **Estratégias NTSL adicionais**: a primeira estratégia ainda não foi definida (ver FOUNDER-QUESTIONS.MD)
- **MT5 como fallback**: variante Linux+MetaTrader5 descrita em STACK-CAM-OFICIAL-LINUX.MD, disponível se Profit/Windows apresentar problemas críticos — decisão pendente do Founder
- **Interface mobile**: visualização read-only do cockpit em dispositivo móvel
- **Codex/CLI/MCP**: materialização tecnológica do SSoT descrita no NCC-1701 §9
- **Setup A+**: definição técnica do setup de alta confluência para 2 contratos (Fase 4 — ainda não definível)
- **Criptomoedas ou outros mercados**: fora do perímetro atual
- **Relatório PDF de operações**: exportação formatada do journal
- **Integração com declaração de IR**: geração automática de DCTF/DIMOB (avaliação futura)
- **Análise de correlação WIN×WDO**: pesquisa quant avançada para Fase 3+

---

## 7. Restrições Constitucionais Relevantes ao Scope

| Restrição | Artigo | Impacto no scope |
|---|---|---|
| Risk Engine é autoridade máxima | Art. 15º | Toda feature de execução obrigatoriamente consulta `cam/_shared/risk/` |
| Limite absoluto 2 WIN / 2 WDO | Art. 11º | Validator `max_contracts_check` é não-negociável e não-parametrizável pelo operador |
| Kill switch sem justificativa | Art. 18º | Frontend deve ter acesso imediato ao kill switch em qualquer tela |
| Resultado líquido — nunca bruto | Art. 25º | Todo componente de UI que exiba P&L deve mostrar líquido de imposto provisionado |
| DARF atrasada bloqueia operação | Art. 26º | `tax_compliance_check` no Risk Engine é gate hard — sem bypass |
| Journal obrigatório | Art. 31º | Não existe "registrar depois" — o registro é condição da operação |
| IA sem autoridade de execução | Art. 35º | Componentes de IA têm acesso read-only; sem endpoint que acione ordem ou altere parâmetros do Risk Engine |
| Hierarchia constitucional | Art. 36º | Nenhum código, configuração ou decisão técnica pode violar a hierarquia |
| Preservar mais capital em dúvida | Art. 6º | Em qualquer ambiguidade de design, a escolha mais conservadora prevalece |

---

## 8. Perguntas Abertas

- [ ] Qual a versão exata do Profit contratada — Pro ou Ultra? (impacta Fase F4 de integração NTSL e módulo de Automação de Estratégias)
- [ ] Qual corretora está vinculada ao Profit? (impacta cálculo de corretagem no ledger e edge mínimo — honestidade de Voltaire no STACK-CAM-OFICIAL.md §10)
- [ ] Qual a tese de edge da primeira estratégia? (sem isso, a Fase 0 constrói infra sem destino para backtest)
- [ ] Qual a fonte de tick histórico para backfill inicial? (Profit exporta tick raw? Apenas candles? Define estratégia de backfill da TimescaleDB no M2)
- [ ] Parâmetros iniciais do Risk Engine: drawdown diário máximo (POV define 3% do capital total), stop loss por operação por ativo (POV define 150–250p WIN / 3–7p WDO) — Carlos confirma esses valores como ponto de partida?

---

## 9. Assunções Tomadas

- A stack definida em `STACK-CAM-OFICIAL.md` está vigente e aprovada como referência canônica para este SCOPE
- O SO de produção é Windows 11; desenvolvimento ocorre primariamente em Linux
- Monorepo único em `apps/cam-cockpit/` conforme ADR-011
- PostgreSQL 16 + TimescaleDB é o banco desde o primeiro commit (ADR-004) — SQLite não é opção
- A Harvest Rule opera em janela mensal (Art. 21º), não diária
- A IA auditora opera em modo assíncrono pós-mercado — sem real-time durante operação
- O frontend não tem autenticação (cockpit local, mono-usuário, rede local)
- Código cross-platform via `pathlib`; adapters de integração Profit injetados via DI

---

## 10. Decisão de Saída

- [ ] Avançar para ARCH + SPEC (recomendado — scope aprovado)
- [ ] Incubar
- [ ] Descartar
- [ ] Investigar mais (volta para DISC)

**Quem decide:** Founder · **Quando:** ___/___/______

---

## 11. Referências

- DVP: [`DVP.md`](./DVP.md)
- PDOC: [`PDOC/project-creation.md`](./PDOC/project-creation.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md)
- Constituição: [`/CONSTITUICAO.md`](/CONSTITUICAO.md)
- NCC-1701 Process: [`/teczi-devflow/NCC-1701/process.md`](/teczi-devflow/NCC-1701/process.md)

---
template: GATE-CHECKLIST
phase: QA
status: Draft
version: 1
date: 2026-05-25
---

# GATE-FASE-0-PARA-1 — Checklist Binário de Transição

> **Lead:** Albert (critérios de aceite)
> **Suporte:** Linus (QA, validação)
> **Skills:** `teczi-demand-specification` + `teczi-quality-assurance`
> **Aprovador:** Founder
> **Vinculação constitucional:** Anexo II (critérios de saída Fase 0), Art. 28º (gates de validação), Art. 6º (preservar capital)
>
> **Princípio:** Este é um checklist **binário** — TRUE ou FALSE. Sem "quase", sem "praticamente", sem "vai estar pronto na próxima semana". Se um item está em FALSE, **Fase 1 não começa**.

---

## 1. Princípio e propósito

A Constituição (Anexo II) e a SPEC do `cam-cockpit` definem critérios de saída da Fase 0 espalhados em múltiplos documentos. Este documento **consolida** tudo em **um único checklist binário** que serve como **gate único** para autorização da Fase 1.

### Por que binário

- **Não-binário convida flexibilização sob pressão emocional** — "70% pronto" vira "vai dar tempo" em estado de convicção (Art. 4º).
- **Founder em estado frio** tem direito a ler 30+ linhas e responder TRUE/FALSE sem ambiguidade.
- **Auditoria histórica** depois pode reconstruir exatamente o que estava OK e o que estava FALSE no momento de gate.

### Como funciona a regra de saída

```
TODOS os itens da §2 = TRUE  →  Fase 1 autorizada
QUALQUER item da §2 = FALSE  →  Fase 1 NÃO autorizada (sem exceções)
```

Não há "exceção por bom senso". Não há "Founder dispensa". Se há exceção legítima, a regra do checklist é **alterada por emenda** (com cooldown), não burlada.

### Flag de código vinculada

Existe (ou existirá) uma flag em código:

```python
# cam/_shared/config/production_gate.py
PRODUCTION_ALLOWED: bool = False
```

Esta flag **só pode ser alterada manualmente** após este documento estar totalmente TRUE e o Founder ter assinado a §6. Alterações automáticas via código são **proibidas constitucionalmente** (Art. 35º — IA não justifica exceção; por extensão, código não auto-eleva permissão).

---

## 2. Checklist binário

> Cada item é rastreável a um artefato (SPEC §, Constituição Art., PLAN TASK, etc.). Founder marca TRUE/FALSE em cada linha **antes** de assinar §6.

### Categoria A — Cockpit funcional end-to-end

A.1 [x] Backend FastAPI inicia sem erro e responde `GET /api/v1/health` com `{"status":"ok"}`
> Rastreabilidade: T-A05 + verificado em `tests/test_api_health.py`

A.2 [x] Frontend React inicia (`npm run dev`) e renderiza Cockpit Live sem erros de TypeScript
> Rastreabilidade: T-E01 + T-E02 + `npx tsc --noEmit` limpo

A.3 [x] Banco PostgreSQL+TimescaleDB sobe via `docker compose up -d db` e responde `pg_isready`
> Rastreabilidade: T-A02 + verificado em `tests/test_docker.py`

A.4 [x] Migrations aplicam sem erro (`uv run alembic upgrade head` em banco limpo)
> Rastreabilidade: T-A07 + T-A08 + T-A09 + `tests/test_migrations.py` (4 testes passando)

A.5 [x] Schema completo presente: 24+ tabelas `cam_*` (operacionais, fiscais, market data, paper trades)
> Rastreabilidade: validado por `tests/test_migrations.py::test_operational_tables_exist + test_fiscal_patrimonial_tables_exist + test_hypertables_exist`

A.6 [x] Hypertables TimescaleDB criadas: `cam_market_ticks`, `cam_market_book_snapshots`
> Rastreabilidade: T-A09 + `tests/test_migrations.py::test_hypertables_exist`

A.7 [ ] Fluxo end-to-end manual demonstrado: checklist pré → criar JournalEntry → Risk Engine valida → fiscal recalcula → harvest atualiza
> Rastreabilidade: T-H06 + `tests/test_fase0_gate.py::TestCriterio1_FluxoCompleto`

### Categoria B — Risk Engine com cobertura adequada

B.1 [ ] Risk Engine implementado: 17 validators dos Arts. 11º–20º + 26º + 32º–33º
> Rastreabilidade: T-B02 a T-B05 + `cam/_shared/risk/validators/`

B.2 [ ] Cobertura global do Risk Engine ≥ 80% (`pytest --cov=cam/_shared/risk`)
> Rastreabilidade: T-B07 + Anexo II Fase 0

B.3 [ ] Cobertura ≥ 100% nos validators críticos: `max_contracts_check` (Art. 11º), `kill_switch_active_check` (Art. 18º), `tax_compliance_check` (Art. 26º)
> Rastreabilidade: T-B07

B.4 [ ] Property-based tests com Hypothesis: 13.000+ cenários gerados, nunca `Approved` quando viola Art. 11º
> Rastreabilidade: T-B07 + `tests/test_risk_hypothesis.py`

B.5 [ ] Risk Engine Pure Python — `lint-imports` confirma que `cam/_shared/risk/` não importa `sqlalchemy`, `psycopg`, `httpx`, `aiohttp`, `requests`, `fastapi`, `pydantic`, `apscheduler`
> Rastreabilidade: T-A06 + contrato `"Risk Engine nao importa I/O"` em `pyproject.toml`

B.6 [ ] Pipeline do Risk Engine retorna primeiro `Rejected` (ordem constitucional dos Arts. 11º–20º preservada)
> Rastreabilidade: SPEC R1.06 + T-B06 + `cam/_shared/risk/engine.py::validate`

### Categoria C — Kill Switch validado em teste real

C.1 [ ] Endpoint `POST /api/v1/kill-switch/activate` cria registro em `cam_kill_switch_events`
> Rastreabilidade: T-C01 + `cam/features/kill_switch/`

C.2 [ ] Endpoint `POST /api/v1/kill-switch/deactivate` exige `confirm: true` no body
> Rastreabilidade: T-C01

C.3 [ ] Com kill switch ativo, Risk Engine bloqueia 100% das tentativas de operação
> Rastreabilidade: `tests/test_fase0_gate.py::TestCriterio3_KillSwitch`

C.4 [ ] Telegram bot recebe alerta `KillSwitchActivated` (modo degradado aceitável se Telegram não configurado, mas teste manual obrigatório)
> Rastreabilidade: T-D04 + verificado por OP-007 do TODO-OPERACIONAL

C.5 [ ] UI exibe banner vermelho persistente em **todas as telas** quando kill switch ativo (CA5.1, CA5.3)
> Rastreabilidade: T-E01 + `KillSwitchButton` no `Layout.tsx`

C.6 [ ] Teste manual end-to-end documentado: ativar kill switch → tentar criar JournalEntry via API → resposta `400 KILL_SWITCH_ATIVO`
> Rastreabilidade: TODO-OPERACIONAL OP-011 + entrada no journal documentando o teste

### Categoria D — Pipeline de backtest funcional

D.1 [ ] `BacktestSimulator` executa run com Risk Engine ATIVO (sem parâmetro `skip_risk`, `bypass`, `disable_risk`)
> Rastreabilidade: `tests/test_fase0_gate.py::TestCriterio4_BacktestComRiskEngine` + T-F01

D.2 [ ] Backtest com 100 trades simulados gera resultado consistente (não-crash, métricas calculadas)
> Rastreabilidade: SPEC §17 critério (4) + T-F02

D.3 [ ] Backtest inclui custos de corretagem (T-F01 implementação) e IR 20% (Art. 24º)
> Rastreabilidade: T-F01 + SPEC R7.03, R7.04

D.4 [ ] Walk-forward retorna janela de otimização + janela de validação (CA7.4)
> Rastreabilidade: T-F02 + `cam/features/backtest/walk_forward.py`

D.5 [ ] Endpoint `POST /api/v1/backtest/run` aceita configuração e retorna `BacktestRun`
> Rastreabilidade: T-F03 + UI Bloco E (T-E11)

### Categoria E — Pipeline de paper trading funcional

E.1 [ ] `PaperTradingService.simulate()` usa o MESMO Risk Engine do live
> Rastreabilidade: T-H01 + verificado em `cam/features/paper_trading/service.py`

E.2 [ ] Paper trades têm flag `is_paper=True` e (futuramente) persistência em tabela própria `cam_paper_trades` — não em `cam_journal_entries` (CA5.5)
> Rastreabilidade: T-H01 + migration `cam_paper_trades` (TD-022 — pendente persistência DB)

E.3 [ ] 10 simulações paper completas executadas e registradas (manual ou automatizado)
> Rastreabilidade: SPEC §17 critério (5) + journal manual ou logs

E.4 [ ] UI Paper Trading exibe badge SIMULAÇÃO vermelho fixo em toda tela (CA5.5)
> Rastreabilidade: T-E09 + `PaperTradingPage.tsx`

E.5 [ ] Paper trading bloqueado por kill switch e por Art. 11º (max contracts) igual ao live
> Rastreabilidade: `tests/test_fase0_gate.py::TestCriterio5_PaperTrading`

### Categoria F — Documentos governamentais aprovados

F.1 [ ] Constituição v1.0 ratificada com assinatura simbólica do Founder
> Rastreabilidade: `CONSTITUICAO.md` final "Assinatura Simbólica"

F.2 [ ] POV-VIGENTE-v1.0 aprovado (gate Founder §7)
> Rastreabilidade: [`POV-VIGENTE-v1.0.md`](./POV-VIGENTE-v1.0.md)

F.3 [ ] DECISION-MEMO-LINUX-OR-WINDOWS resolvido (§6 do doc preenchida, §8 cascata executada)
> Rastreabilidade: [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md)

F.4 [ ] CORRETORA-EVAL §9 criada com corretora vinculada confirmada
> Rastreabilidade: [`CORRETORA-EVAL.md`](./CORRETORA-EVAL.md) §9

F.5 [ ] EDGE-THESIS-S1 aprovado OU rejeitado com S1 alternativa proposta (§11 do doc)
> Rastreabilidade: [`strategies/EDGE-THESIS-S1.md`](./strategies/EDGE-THESIS-S1.md)

F.6 [ ] RUNBOOK-INCIDENTE-TECNICO §4 (contatos) preenchido pelo Founder
> Rastreabilidade: [`runbooks/RUNBOOK-INCIDENTE-TECNICO.md`](./runbooks/RUNBOOK-INCIDENTE-TECNICO.md) §4

F.7 [ ] MAPPING-CONSTITUICAO-RISK-ENGINE sem lacunas críticas (artigos executáveis sem validator)
> Rastreabilidade: [`MAPPING-CONSTITUICAO-RISK-ENGINE.md`](./MAPPING-CONSTITUICAO-RISK-ENGINE.md) §5

F.8 [ ] PROTOCOLO-EMENDA-CONSTITUCIONAL validado pelo Founder
> Rastreabilidade: [`PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](./PROTOCOLO-EMENDA-CONSTITUCIONAL.md) §8

### Categoria G — Decisões pendentes resolvidas

G.1 [ ] S1 escolhida e tese aprovada (DOC 4 §11 = Opção A)
> Rastreabilidade: EDGE-THESIS-S1 §11

G.2 [ ] Corretora vinculada com tabela de corretagem confirmada (não mais "(C)" na matriz)
> Rastreabilidade: CORRETORA-EVAL §9

G.3 [ ] Stack canônica decidida (Windows+Profit OU Linux+MT5)
> Rastreabilidade: DECISION-MEMO §6

G.4 [ ] Versão do Profit (Pro vs Ultra) ou hospedagem do MT5 (Wine vs VPS) definida
> Rastreabilidade: TODO-OPERACIONAL OP-002 (Profit) ou DECISION-MEMO §5.3 (Linux)

G.5 [ ] Custos totais por trade WIN/WDO recalculados com tabela real, edge mínimo atualizado em `cam/features/journal/domain.py`
> Rastreabilidade: TD-... (a criar) + CORRETORA-EVAL §9.5

### Categoria H — Runbook testado em simulação

H.1 [ ] Simulação do cenário §2.1 (plataforma trava) executada em conta demo nos últimos 90 dias
> Rastreabilidade: RUNBOOK-INCIDENTE §6.1 + entrada no journal `event_type=TRAINING_SIMULATION`

H.2 [ ] Simulação do cenário §2.4 (internet cai) executada em conta demo nos últimos 90 dias
> Rastreabilidade: RUNBOOK-INCIDENTE §6.2

H.3 [ ] Resultado da simulação documentado: tempo até fechar posição ≤ critério de aceite
> Rastreabilidade: RUNBOOK-INCIDENTE §6.3

### Categoria I — Infra de backup ativa

I.1 [ ] `scripts/backup.sh` executável e testado (pg_dump + JSONL → diretório local)
> Rastreabilidade: T-H04 + `apps/cam-cockpit/scripts/backup.sh`

I.2 [ ] Cron Linux (ou Task Scheduler Windows) agendado para backup diário às 02:00
> Rastreabilidade: TODO-OPERACIONAL OP-008 (rclone) + cron entry

I.3 [ ] Pelo menos 1 backup completo testado e restaurado com sucesso em ambiente isolado
> Rastreabilidade: registro em journal `event_type=BACKUP_RESTORE_TEST`

I.4 [ ] Journal duplo JSONL ativo e validado: arquivo `~/.cam/journal/YYYY-MM-DD.jsonl` é criado a cada operação registrada
> Rastreabilidade: T-C04 + SPEC R11.06

I.5 [ ] rclone configurado e testado para sincronizar `~/cam-backups/` com Google Drive (ou destino equivalente)
> Rastreabilidade: TODO-OPERACIONAL OP-008

### Categoria J — Telegram bot configurado e testado

J.1 [ ] `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` configurados em `.env`
> Rastreabilidade: TODO-OPERACIONAL OP-007 + `.env.example`

J.2 [ ] Bot envia mensagem teste manualmente (`curl https://api.telegram.org/bot{TOKEN}/sendMessage`)
> Rastreabilidade: teste manual documentado em journal

J.3 [ ] Evento `KillSwitchActivated` dispara mensagem real no Telegram do Founder
> Rastreabilidade: T-D04 + handler em `cam/features/notifications/`

### Categoria K — Segurança e compliance básico

K.1 [ ] Zero credenciais commitadas no repositório (hook anti-secrets ativo)
> Rastreabilidade: T-A10 + `.gitignore` + verificação `git log --all -p | grep -i "token\|password\|api_key"`

K.2 [ ] `.env` listado no `.gitignore` e ausente do histórico de commits
> Rastreabilidade: `git ls-files | grep -v ".env.example" | grep -q "^.env$" && false`

K.3 [ ] Audit trail ativo: funções de `cam/_shared/audit/logger.py` integradas em kill_switch e Risk Engine (não apenas disponíveis)
> Rastreabilidade: T-H05 + TD-027 (resolver antes de Fase 1) + log file `~/.cam/logs/cam-audit.log`

---

## 3. Critério de saída

```
Cada item da §2 deve estar em [X] (TRUE) para Fase 1 ser autorizada.

Total de itens binários: 50+
Itens TRUE necessários: 50+
Itens TRUE tolerados como FALSE: 0 (sem exceções)
```

> **Não existe "Fase 1 condicional".** Não há gate parcial. Ou o sistema está pronto, ou não está.

---

## 4. Flag de código vinculada

### 4.1 Onde fica a flag

A flag `PRODUCTION_ALLOWED` deve ser implementada em um arquivo versionado dedicado:

```
apps/cam-cockpit/backend/cam/_shared/config/production_gate.py
```

Conteúdo proposto (tech debt: a implementar — TD a abrir):

```python
"""
Production Gate — autoriza Fase 1+ (paper trading e além).

Alteração desta flag de False para True exige:
  - Checklist GATE-FASE-0-PARA-1 100% TRUE
  - Assinatura simbólica do Founder neste documento
  - Edição manual deste arquivo (NUNCA por código automatizado)

Constituição Art. 35º (IA não justifica exceção) aplicado por extensão:
  Nenhum agente/script automatizado pode alterar esta flag.
"""

PRODUCTION_ALLOWED: bool = False  # Fase 0 — Construção
PRODUCTION_ALLOWED_AT: str = ""    # ISO8601 da liberação, vazio enquanto False
PRODUCTION_ALLOWED_BY: str = ""    # Founder, vazio enquanto False
```

### 4.2 Quem lê a flag

- Endpoint `POST /api/v1/risk/validate-intention` retorna 503 se `PRODUCTION_ALLOWED=False`.
- Endpoint `POST /api/v1/paper-trading/simulate-operation` retorna 503 se `False` (paper também é Fase 1).
- Endpoint `POST /api/v1/journal/entries` aceita apenas se `True` E source `MANUAL` (registro retroativo OK em qualquer estado).

### 4.3 Como alterar a flag

1. Founder confirma que **TODOS** os itens da §2 estão TRUE.
2. Founder assina §6 deste documento.
3. Founder edita `production_gate.py` manualmente, alterando para `True` + preenchendo `PRODUCTION_ALLOWED_AT` + `PRODUCTION_ALLOWED_BY`.
4. Commit + push **manual** (não via agente).
5. Reinicia o backend para a flag ter efeito.

### 4.4 Cooldown de reversão

Se a flag for revertida para `False` (motivo: incidente, falha de aderência, decisão fria do Founder), ela só pode voltar a `True` após:

- **Cooldown mínimo de 7 dias** (analogia ao Art. 38º — emenda restritiva).
- Nova validação completa do checklist §2.

---

## 5. Histórico de avaliações do gate

> Cada avaliação completa do gate (passou ou não) é registrada abaixo.

| Avaliação # | Data | Resultado | Itens TRUE / Total | Notas |
|---|---|---|---|---|
| 1 | ___/___/______ | [ ] PASSOU  [ ] NÃO | __ / 50+ | Aguardando primeira avaliação |

> Entradas futuras devem ser appendadas, **nunca editadas retroativamente**.

---

## 6. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior reconhece que:

    a) Marcou cada item da §2 em estado frio, com pregão fechado, sem
       pressão emocional.

    b) Compreende que QUALQUER item em FALSE bloqueia a Fase 1
       independentemente do estado dos demais.

    c) Vai alterar a flag PRODUCTION_ALLOWED manualmente em
       production_gate.py se e somente se todos os itens estiverem TRUE.

    d) Reverter a flag para False não exige justificativa (Art. 18º
       princípio kill switch). Reativar exige cooldown de 7 dias.

    Resultado da avaliação:
    [ ] TODOS os itens da §2 TRUE — Fase 1 AUTORIZADA
    [ ] Algum item em FALSE — Fase 1 NÃO AUTORIZADA

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) — Anexo II Fase 0 critérios de saída + Art. 28º gates
- [`POV-VIGENTE-v1.0.md`](./POV-VIGENTE-v1.0.md) §3 — parâmetros que o Risk Engine valida
- [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md) — pré-requisito F.3
- [`CORRETORA-EVAL.md`](./CORRETORA-EVAL.md) — pré-requisito F.4 / G.2 / G.5
- [`strategies/EDGE-THESIS-S1.md`](./strategies/EDGE-THESIS-S1.md) — pré-requisito F.5 / G.1
- [`runbooks/RUNBOOK-INCIDENTE-TECNICO.md`](./runbooks/RUNBOOK-INCIDENTE-TECNICO.md) — pré-requisito F.6 / H.1-H.3
- [`MAPPING-CONSTITUICAO-RISK-ENGINE.md`](./MAPPING-CONSTITUICAO-RISK-ENGINE.md) — pré-requisito F.7
- [`PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](./PROTOCOLO-EMENDA-CONSTITUCIONAL.md) — pré-requisito F.8
- [`apps/cam-cockpit/TECH-DEBT.md`](../apps/cam-cockpit/TECH-DEBT.md) — tech debts conhecidos (TD-022, TD-027 críticos para Fase 1)
- [`apps/cam-cockpit/TODO-OPERACIONAL.md`](../apps/cam-cockpit/TODO-OPERACIONAL.md) — itens OP-007 a OP-013 relevantes

---

> **Princípio operacional deste documento:**
>
> Linus valida. Albert escreve o critério. O Founder marca TRUE/FALSE.
>
> Sem TRUE em tudo, sem Fase 1. **Sem exceção, sem nuance, sem "praticamente pronto".**

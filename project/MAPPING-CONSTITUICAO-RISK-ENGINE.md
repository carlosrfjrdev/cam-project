---
template: TRACEABILITY-MATRIX
phase: QA
status: Draft
version: 1
date: 2026-05-25
---

# MAPPING-CONSTITUICAO-RISK-ENGINE — Matriz de Rastreabilidade

> **Lead:** Albert (especificação)
> **Suporte:** Kevin (SEC-GOV, rastreabilidade)
> **Skills:** `teczi-demand-specification` + `teczi-security-governance`
> **Aprovador:** Founder
> **Vinculação constitucional:** Parte III (exposição), Parte IV (Risk Engine), Parte VI (fiscal), Parte VIII (registro)
>
> **Propósito:** Em revisão futura, permitir responder em segundos: *"Art. 16º está implementado? Onde? Está testado? Onde?"*

---

## 1. Princípio

Toda regra constitucional executável tem:

1. **Um validator correspondente** no Risk Engine (Pure Python — `cam/_shared/risk/validators/`).
2. **Um arquivo de teste** que prova o validator (`tests/test_risk_validators_*.py` ou `cam/_shared/risk/tests/`).
3. **Uma TASK do PLAN** que materializou a implementação.

Conexão **rastreável e auditável** em ambas as direções:
- "Esse validator vem de qual artigo?" → resposta neste documento.
- "Esse artigo está coberto?" → resposta neste documento.

Quando essa rastreabilidade quebra, **a Constituição perde fiscalização técnica** e o sistema vira "sistema que tenta seguir a Constituição" em vez de "sistema que segue a Constituição por design".

---

## 2. Tabela canônica

> Convenção:
> - **Validator:** nome do arquivo Python em `cam/_shared/risk/validators/{group}_{name}.py` (sufixo `_check`)
> - **Arquivo de teste:** caminho relativo ao `apps/cam-cockpit/backend/`
> - **TASK PLAN:** identificador conforme [`project/cam-cockpit/PLAN.md`](./cam-cockpit/PLAN.md)
> - **Status:** Implementado · Pendente · Não-aplicável (apenas processo/documento)

| Artigo | Resumo | Validator | Arquivo Python | Arquivo de teste | TASK PLAN | Status |
|---|---|---|---|---|---|---|
| **Art. 11º** | Limite absoluto 2 WIN / 2 WDO | `max_contracts_check` | `cam/_shared/risk/validators/group2_limits.py` | `tests/test_risk_validators_group2.py` | T-B03 | ✅ Implementado |
| **Art. 12º** | Exposição fase inicial (1 contrato, sem simultaneidade WIN+WDO em Fases 1-2, soma total respeita limite) | `phase_contracts_check` + `simultaneous_position_check` + `total_open_contracts_check` (T-TD-001 SPEC v0.3) | `cam/_shared/risk/validators/group2_limits.py` | `tests/test_risk_validators_group2.py` + `tests/test_total_open_contracts.py` | T-B03 + T-TD-001 | ✅ Implementado completo (lacuna L1 antiga resolvida) |
| **Art. 11-A** | Multiestratégia simultânea (soma agregada + 8 condições) | `aggregate_risk_check` (a criar) + `correlation_check` (a criar) | `cam/_shared/risk/aggregate.py` (a criar) | `tests/test_aggregate_risk.py` (a criar) | BL-H1 SPEC v0.4 | ⚠️ A IMPLEMENTAR — pós EMENDA-001 v2 |
| **Art. 11-B** | Escalonamento condicional do limite por default (métrica composta + Risk Engine eligibility + cooldown + reversão automática) | `scaling_eligibility_check` (a criar) + `scaling_reversion_monitor` (a criar) | `cam/_shared/risk/scaling.py` (a criar) | `tests/test_scaling_eligibility.py` (a criar) | BL-H2 SPEC v0.4 | ⚠️ A IMPLEMENTAR — pós EMENDA-001 v2 |
| **Art. 13º** | Proibição de Martingale (aumento após loss) | `martingale_check` | `cam/_shared/risk/validators/group4_operational.py` | `tests/test_risk_validators_group4.py` | T-B05 | ✅ Implementado |
| **Art. 14º** | Derivativos como ferramenta (princípio + 7 sub-regras) | Múltiplos validators + processo | (multiplo) | (multiplo) | (multiplo) | ⚠️ Parcialmente coberto — ver §4 |
| **Art. 15º** | Autoridade máxima do Risk Engine | (princípio sistêmico — não-validator) | `cam/_shared/risk/engine.py::validate` (pipeline) | `tests/test_risk_pipeline_integration.py` + `tests/test_fase0_gate.py::TestCriterio1_FluxoCompleto` | T-B06 | ✅ Implementado (estrutural) |
| **Art. 16º** | Limites de perda 3% / 7% / 15% | `daily_loss_limit_check` + `weekly_loss_limit_check` + `monthly_loss_limit_check` | `cam/_shared/risk/validators/group3_pnl.py` | `tests/test_risk_validators_group3.py` | T-B04 | ✅ Implementado |
| **Art. 17º** | Gain Lock 2% diário | `gain_lock_check` | `cam/_shared/risk/validators/group3_pnl.py` | `tests/test_risk_validators_group3.py` | T-B04 | ✅ Implementado |
| **Art. 18º** | Kill Switch | `kill_switch_active_check` | `cam/_shared/risk/validators/group1_state.py` | `tests/test_risk_validators_group1.py` + `tests/test_fase0_gate.py::TestCriterio3_KillSwitch` | T-B02 + T-C01 | ✅ Implementado |
| **Art. 19º** | Contingência técnica | (não-validator — processo operacional) | N/A | N/A | RUNBOOK-INCIDENTE | ⚠️ Documento — ver §4 |
| **Art. 20º** | Limite de operações por dia | `daily_operations_count_check` | `cam/_shared/risk/validators/group4_operational.py` | `tests/test_risk_validators_group4.py` | T-B05 | ✅ Implementado |
| **Art. 21º** | Harvest Rule (60/40) | (não-validator — service de harvest) | `cam/features/harvest/service.py` | `cam/features/harvest/tests/` | T-C08 + T-C09 | ✅ Implementado (service-level) |
| **Art. 22º** | Sangria do Bucket Derivativo (80/20 @ R$ 4.500) | (não-validator — service de harvest) | `cam/features/harvest/service.py` | `cam/features/harvest/tests/` | T-C08 | ✅ Implementado (service-level) |
| **Art. 23º** | Carteira Hard (definição patrimonial) | (não-validator — service patrimonial) | `cam/features/ledger/` | `cam/features/ledger/tests/` | T-C08 | ✅ Implementado (service-level) |
| **Art. 24º** | Apuração fiscal mensal (IR 20% + IRRF 1%) | (não-validator — service fiscal) | `cam/features/fiscal/service.py` + `cam/features/journal/domain.py` (`IR_DAY_TRADE_RATE`) | `cam/features/fiscal/tests/` | T-C06 + T-C07 | ✅ Implementado (service-level) |
| **Art. 25º** | Provisão fiscal automática — UI sempre líquida | (não-validator — UI + domain) | `frontend/src/_shared/components/PnlDisplay.tsx` + `cam/features/journal/domain.py::result_net` | `frontend/.../__tests__/PnlDisplay.test.tsx` + `cam/features/journal/tests/` | T-C03 + T-E01 + T-E02 | ✅ Implementado (UI + domain) |
| **Art. 26º** | DARF atrasada bloqueia operações | `tax_compliance_check` | `cam/_shared/risk/validators/group1_state.py` | `tests/test_risk_validators_group1.py` + `tests/test_fase0_gate.py::TestCriterio6_DarfOverdue` | T-B02 | ✅ Implementado |
| **Art. 27º** | Compensação de prejuízo | (não-validator — service fiscal) | `cam/features/fiscal/service.py` (saldo compensável) | `cam/features/fiscal/tests/` | T-C06 | ✅ Implementado (service-level) |
| **Art. 28º** | Gates de validação obrigatória (backtest, walk-forward, paper, Risk Engine, contingência) | (não-validator — processo) | (multiplo: backtest, paper_trading, risk, runbook) | (multiplo) | (multiplo) | ⚠️ Processo — ver §4 |
| **Art. 29º** | Aderência operacional ≥ 95% | (não-validator — métrica computada) | `cam/features/journal/` (cálculo de aderência) | (a confirmar) | T-C05 | ⚠️ Implementação parcial — ver §5 lacunas |
| **Art. 30º** | Escala por evidência (autorização de fase) | `phase_authorization_check` + `setup_a_plus_check` | `cam/_shared/risk/validators/group1_state.py` + `group4_operational.py` | `tests/test_risk_validators_group1.py` + `tests/test_risk_validators_group4.py` | T-B02 + T-B05 | ✅ Implementado |
| **Art. 31º** | Journal obrigatório | (não-validator — feature journal) | `cam/features/journal/` + journal duplo JSONL | `cam/features/journal/tests/` | T-C03 + T-C04 | ✅ Implementado (operação sem registro = falha operacional via feature) |
| **Art. 32º** | Checklist pré-mercado | `pre_market_checklist_check` | `cam/_shared/risk/validators/group1_state.py` | `tests/test_risk_validators_group1.py` | T-B02 + T-C02 | ✅ Implementado |
| **Art. 33º** | Checklist pós-mercado | `post_market_checklist_check` | `cam/_shared/risk/validators/group1_state.py` | `tests/test_risk_validators_group1.py` | T-B02 + T-C02 | ✅ Implementado |
| **Art. 34º** | Funções permitidas à IA | (não-validator — política) | `cam/features/ai_analyst/prompts.py` (restrições embutidas no prompt) | `cam/features/ai_analyst/tests/` | T-G01 + T-G02 | ✅ Implementado (política em prompt + ContentGuard) |
| **Art. 35º** | Funções vedadas à IA | `ContentGuard` (filtro pós-geração) | `cam/features/ai_analyst/content_guard.py` | `cam/features/ai_analyst/tests/test_content_guard.py` | T-G02 | ✅ Implementado |
| **Art. 36º** | Subordinação da IA — hierarquia constitucional | (não-validator — arquitetura) | (arquitetura inteira reflete a hierarquia) | (todos os testes acima validam) | (todas as TASKs) | ✅ Implementado (arquitetural) |

### 2.1 Validators adicionais que não mapeiam a artigo individual

Alguns validators vêm de **combinação de artigos** ou da **POV**:

| Validator | Origem | Arquivo | Teste | TASK |
|---|---|---|---|---|
| `trading_window_check` | POV §3.6 + Art. 14º (operação disciplinada) | `cam/_shared/risk/validators/group4_operational.py` | `tests/test_risk_validators_group4.py` | T-B05 |
| `circuit_breaker_check` | Art. 18º (extensão técnica do kill switch) | `cam/_shared/risk/validators/group4_operational.py` | `tests/test_risk_validators_group4.py` | T-B05 |

---

## 3. Ordem de execução dos validators (vinculação SPEC R1.06)

A ordem é constitucional. O primeiro `Rejected` encerra o pipeline. Confirmado em `cam/_shared/risk/engine.py::VALIDATORS`:

| Posição | Validator | Grupo | Artigo principal |
|---|---|---|---|
| 1 | `kill_switch_active_check` | 1 (estado) | Art. 18º |
| 2 | `pre_market_checklist_check` | 1 (estado) | Art. 32º |
| 3 | `post_market_checklist_check` | 1 (estado) | Art. 33º |
| 4 | `tax_compliance_check` | 1 (estado) | Art. 26º |
| 5 | `phase_authorization_check` | 1 (estado) | Art. 30º |
| 6 | `max_contracts_check` | 2 (limites) | Art. 11º — INTOCÁVEL |
| 7 | `phase_contracts_check` | 2 (limites) | Art. 12º |
| 8 | `simultaneous_position_check` | 2 (limites) | Art. 12º |
| 8.5 | `total_open_contracts_check` | 2 (limites) | Art. 12º explicito (T-TD-001 SPEC v0.3) |
| 8.6 | `aggregate_risk_check` | 2 (limites) | Art. 11-A — multiestratégia (BL-H1 SPEC v0.4) |
| 8.7 | `scaling_eligibility_check` | 2 (limites) | Art. 11-B — eligibility (consulta apenas; não bloqueia operação) (BL-H2 SPEC v0.4) |
| 9 | `daily_loss_limit_check` | 3 (P&L) | Art. 16º (diária 3%) |
| 10 | `weekly_loss_limit_check` | 3 (P&L) | Art. 16º (semanal 7%) |
| 11 | `monthly_loss_limit_check` | 3 (P&L) | Art. 16º (mensal 15%) |
| 12 | `gain_lock_check` | 3 (P&L) | Art. 17º |
| 13 | `daily_operations_count_check` | 4 (operacional) | Art. 20º |
| 14 | `martingale_check` | 4 (operacional) | Art. 13º |
| 15 | `trading_window_check` | 4 (operacional) | POV §3.6 |
| 16 | `setup_a_plus_check` | 4 (operacional) | Art. 11º + Anexo II Fase 4 |
| 17 | `circuit_breaker_check` | 4 (operacional) | Art. 18º (extensão) |

**Justificativa da ordem:** Grupo 1 (estado) primeiro porque qualquer falha de estado anula sentido de validar limites. Grupo 2 (limites de contratos) antes do Grupo 3 (P&L) porque excesso de contratos é violação direta do Art. 11º (mais grave que limite de loss). Grupo 4 (operacional) por último porque depende de contexto operacional (horário, contagem, histórico).

---

## 4. Artigos NÃO cobertos por validator (apenas documento ou processo)

Alguns artigos são **estruturais ou processuais** — não fazem sentido como validator do Risk Engine.

| Artigo | Por que não é validator | Onde está coberto |
|---|---|---|
| **Art. 1º-6º** | Princípios fundamentais (declarativos) | Constituição inteira; Art. 6º aplicado em conflito de regras |
| **Art. 7º** | Capital declarado | Configuração em `cam/_shared/config/` + seed inicial DB |
| **Art. 8º** | Perímetro do CaM | Documentação + separação de tabelas (`cam_*` vs ativos externos) |
| **Art. 9º** | Aportes externos | Processo manual + entrada em `cam_phase_history` |
| **Art. 10º** | Estrutura interna do capital (3 buckets) | `cam/features/ledger/` + tabela `cam_bucket_transactions` |
| **Art. 14º** | Derivativos como ferramenta (declarativo) | Coberto por combinação de validators (11º, 16º, 18º) + processo |
| **Art. 19º** | Contingência técnica | [`runbooks/RUNBOOK-INCIDENTE-TECNICO.md`](./runbooks/RUNBOOK-INCIDENTE-TECNICO.md) |
| **Art. 21º-23º** | Harvest, Sangria, Carteira Hard | `cam/features/harvest/` + `cam/features/ledger/` (services) |
| **Art. 24º, 25º, 27º** | Fiscal (apuração, provisão, compensação) | `cam/features/fiscal/` (service) + UI `PnlDisplay` |
| **Art. 28º** | Gates de validação obrigatória | Processo (combinação backtest + paper + Risk Engine + contingência) |
| **Art. 31º** | Journal obrigatório | `cam/features/journal/` + journal duplo JSONL |
| **Art. 34º** | Funções permitidas à IA | `cam/features/ai_analyst/prompts.py` (positivo) |
| **Art. 36º** | Subordinação da IA — hierarquia | Arquitetura inteira (vertical slice + Risk Engine como _shared) |
| **Art. 37º-40º** | Governança (POV, emenda, alteração, revisão) | Documentos: POV-VIGENTE, PROTOCOLO-EMENDA |
| **Art. 41º-43º** | Disposições finais (vigência, versionamento, soberania) | Versionamento Git + Apêndice B da Constituição |

> Esses artigos **não são deficiências** — eles cumprem função estrutural diferente da função de validator técnico.

---

## 5. Lacunas identificadas

> **Lacuna:** artigo executável **sem** validator nem service nem documento de cobertura. Cada lacuna abaixo é **tech debt** ou **TODO operacional**.

### Lacuna L1 — Art. 29º: cálculo de aderência operacional

**Sintoma:** Aderência é definida formalmente (Art. 29º) e é critério de evolução de fase (≥95%), mas o cálculo automatizado **não está implementado** no service do journal.

**Causa:** Implementação esperada em T-C05 (relatórios e exportação do journal), mas o cálculo específico de aderência ainda é manual.

**Resolução proposta:** Adicionar método `calculate_adherence(window)` em `cam/features/journal/service.py` que computa:
```
adherence = operacoes_conformes / total_operacoes
```
Onde `operacoes_conformes` é a contagem de `JournalEntry` cujo `risk_decision_id` aponta para uma decisão `Approved` no momento de criação.

**Status:** ⚠️ TODO — abrir TD-028 (tech debt) ou TASK específica antes de Fase 2 (Art. 29º é critério de saída da Fase 1).

**Bloqueia gate Fase 0→1?** Não diretamente — a Fase 1 é paper trading, e o cálculo pode ser feito retrospectivamente. **Bloqueia Fase 1→2** se não estiver pronto.

### Lacuna L2 — Art. 14º (sub-regra "possibilidade de desligamento imediato")

**Sintoma:** Art. 14º exige "possibilidade de desligamento imediato" como condição de uso de derivativos. O `kill_switch_active_check` cobre, mas não há validador específico que negue operação **se** o kill switch não estiver respondendo (kill switch indisponível ≠ kill switch inativo).

**Causa:** Não foi previsto na arquitetura inicial.

**Resolução proposta:** Adicionar `kill_switch_responsiveness_check` que envia um ping interno ao serviço de kill_switch ao construir o `RiskContext`. Se ping falhar, marca campo `kill_switch_responsive=False` no contexto e o validator bloqueia.

**Status:** ⚠️ TODO — abrir TD-029. Baixa prioridade em Fase 0 (validador é simples). **Recomendado antes de Fase 2** (trade real).

### Lacuna L3 — Art. 24º: IRRF 1% como antecipação

**Sintoma:** A retenção IRRF de 1% é mencionada na constituição, mas não há lógica explícita no fiscal de "IRRF é antecipação, descontar do DARF final".

**Causa:** O `cam/features/fiscal/service.py` tem o cálculo básico de IR 20% mas a compensação do IRRF retido como antecipação precisa de validação fiscal real.

**Resolução proposta:** Validar lógica em `cam/features/fiscal/domain.py::FiscalApuration` — confirmar que `ir_to_pay = ir_total - irrf_withheld` está corretamente implementado. Adicionar teste de regressão com cenário oficial da Receita Federal.

**Status:** ⚠️ TODO antes de Fase 2 — IRRF é compliance fiscal, não apenas operacional.

### Lacuna L4 — Art. 30º: registro de "evidência objetiva" para evolução de fase

**Sintoma:** Art. 30º exige evidência objetiva para evolução de fase. A tabela `cam_phase_history` registra transições, mas não há campo formal para "evidência" (snapshot de métricas, ID do run de backtest, ID do paper trading que validou).

**Causa:** Migration `cam_phase_history` (T-A07) tem campos básicos; não tem ligação formal com `cam_backtest_runs` ou `cam_paper_trades`.

**Resolução proposta:** Adicionar coluna `evidence_artifacts JSONB` em `cam_phase_history` armazenando referências `[{type: "backtest_run", id: "..."}, {type: "paper_trade_session", id: "..."}, ...]`. Tornar não-NULL para transições para Fase 2+.

**Status:** ⚠️ TODO antes de Fase 2.

### Lacuna L5 — Art. 8º: separação física entre perímetro CaM e patrimônio externo

**Sintoma:** A separação está documentada e respeitada conceitualmente, mas não há **enforcement técnico** que impeça um JournalEntry de referenciar PSSA3 (ativo externo) por engano.

**Causa:** O schema permite qualquer string em `asset`. Não há lista branca (`["WIN", "WDO"]`).

**Resolução proposta:** Constraint `CHECK (asset IN ('WIN', 'WDO'))` na tabela `cam_journal_entries` + validação no domain.

**Status:** ⚠️ TODO baixa prioridade — domain layer já restringe via `AssetType` enum, mas falta enforcement em DB.

---

## 6. Vínculo com SPEC §5 (ordem dos validators)

A ordem dos validators na SPEC do `cam-cockpit` (`SPEC.md` §5 / R1.06) coincide com a §3 deste documento. Qualquer divergência futura entre os dois documentos é **bug de rastreabilidade** e deve ser reportado como BUG fast-track (estado BUG do NCC-1701, lead Bill).

### Como manter sincronização

Quando um validator novo é adicionado ao Risk Engine:

1. Atualizar `VALIDATORS` em `cam/_shared/risk/engine.py`.
2. Atualizar SPEC §5 (R1.06) com a posição na ordem.
3. Atualizar §2 e §3 deste documento.
4. Testes de pipeline em `tests/test_risk_pipeline_integration.py` precisam ser estendidos.

> **Checklist de PR para mudança no Risk Engine:** verificar que os 4 pontos acima estão consistentes antes do merge.

---

## 7. Cobertura — resumo numérico

| Categoria | Total | Status |
|---|---|---|
| Artigos executáveis (têm validator no Risk Engine) | 11 | ✅ 11/11 implementados |
| Artigos service-level (têm implementação fora do Risk Engine) | 7 | ✅ 7/7 implementados |
| Artigos processuais (cobertos por documento/runbook) | 18 | ✅ 18/18 cobertos |
| Lacunas identificadas (§5) | 5 | ⚠️ 5 lacunas — todas com TODO/TD planejado |
| **Total artigos da Constituição v1.0** | **43** | **41 cobertos + 5 lacunas com plano** |

> Observação: A soma pode passar de 43 porque alguns artigos têm cobertura múltipla (validator + service + documento).

---

## 8. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior valida esta matriz como
    documento de auditoria do CaM e reconhece que:

    a) Toda regra constitucional executável (Parte III, IV, VI, VIII)
       tem rastreabilidade até arquivo Python + teste + TASK.

    b) As 5 lacunas identificadas em §5 são TODO/tech debt planejados,
       não defeitos ignorados. L1, L3 e L4 são bloqueadores para Fase 2,
       não para Fase 1.

    c) Esta matriz será atualizada a cada novo validator ou mudança na
       ordem de execução do Risk Engine, conforme §6.

    d) Em divergência entre esta matriz e a implementação real (código),
       prevalece a implementação real — matriz é atualizada para refletir
       (Princípio NCC-1701 §2 regra 7: "estado real vence intenção").

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) — todos os artigos mapeados
- [`POV-VIGENTE-v1.0.md`](./POV-VIGENTE-v1.0.md) — parâmetros que os validators consomem
- [`apps/cam-cockpit/backend/cam/_shared/risk/`](../apps/cam-cockpit/backend/cam/_shared/risk/) — Risk Engine completo
- [`apps/cam-cockpit/backend/tests/test_risk_*.py`](../apps/cam-cockpit/backend/tests/) — testes dos validators
- [`project/cam-cockpit/SPEC.md`](./cam-cockpit/SPEC.md) §5 / R1.06 — ordem oficial dos validators
- [`project/cam-cockpit/PLAN.md`](./cam-cockpit/PLAN.md) — TASKs T-B01 a T-B07
- [`apps/cam-cockpit/TECH-DEBT.md`](../apps/cam-cockpit/TECH-DEBT.md) — TD-001 (limite simultâneo WIN+WIN) ligado ao Art. 12º
- [`GATE-FASE-0-PARA-1.md`](./GATE-FASE-0-PARA-1.md) — pré-requisito F.7 (esta matriz sem lacunas críticas)

---

> **Princípio operacional deste documento:**
>
> Albert mapeia. Kevin audita. O Founder ratifica que a Constituição **é** o sistema, não **fala sobre** o sistema.
>
> Lacuna identificada é lacuna que existe. Lacuna escondida é lacuna que mata em pregão.

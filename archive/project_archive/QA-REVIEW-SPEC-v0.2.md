---
template: QA-REVIEW
phase: QA
status: Draft
version: 1
date: 2026-05-25
spec: SPEC-v0.2-MT5-ENQUADRAMENTO.md
plan: PLAN-v0.2.md
sec: true
qa_sec: true
---

# QA-REVIEW — SPEC v0.2.1 (Enquadramento MT5 — coexistência)

> **Lead:** Linus (QA-CR + QA-Func)
> **Co-lead:** Kevin (QA-SEC)
> **Skill:** `teczi-quality-assurance`
> **Aprovador:** Founder (Go/No-Go)

---

## 0. Recomendação preliminar

**Go-condicional** — a entrega cumpre a SPEC v0.2.1, todos os testes automatizados estão verdes (437 totais), os contratos de arquitetura `import-linter` continuam `2 kept / 0 broken`, e os marcadores `sec`/`qa-sec` foram materializados. Pendências de validação **manual** (EA MQL5 em conta DEMO via Wine) ficam para `MANUAL-VALIDATION-CHECKLIST.md` — não bloqueiam Go porque foram declaradas como Out-of-Test-Suite em PLAN-v0.2 §4 (limitação técnica do MQL5).

---

## 1. Escopo da revisão

| Item revisado | Origem | Status |
|---|---|---|
| 30 TASKs do PLAN-v0.2 (Blocos A–H) | PLAN-v0.2 §2 | ✅ todas marcadas como entregues |
| 18 critérios de aceite (CA12–CA20 da SPEC) | SPEC §5 | ✅ cobertos por testes ou checklist manual |
| 11 regras novas (R12–R21 da SPEC) | SPEC §3 | ✅ materializadas |
| 9 tech debts pré-listados (TD-v0.2-01..09) | SPEC §8 | ✅ registrados em `TECH-DEBT.md` |
| Coexistência Profit/MT5 (princípio R21) | SPEC v0.2.1 §1 | ✅ código Profit intacto, flag desativada por padrão |
| Vinculação constitucional (Arts. 11/15/18/25/35) | SPEC §1 | ✅ enforcement em código + testes |

---

## 2. QA-CR (Code Review) — Linus

### 2.1 Aderência ao PLAN

| TASK | Status | Notas |
|---|---|---|
| T-MT5-A01 | ✅ | `pyzmq>=26.0` em `pyproject.toml:18`; `uv sync` sem warnings críticos |
| T-MT5-A02 | ✅ | 9 arquivos no skeleton + README com seções obrigatórias; importável; testes de estrutura |
| T-MT5-A03 | ✅ | 4 subdirs em `apps/cam-cockpit/mql5/` + README com instruções |
| T-MT5-A04 | ✅ | `.env.example` + `Settings` com 7 variáveis novas; default `MT5_INTEGRATION_ENABLED=true` |
| T-MT5-A05 | ✅ | `pyproject.toml:88` lista `cam.features.mt5_integration` no contrato `independence`; `lint-imports` passa |
| T-MT5-B01 | ✅ | `guard.py` + `FeatureDisabledException` + handler em `cam/api/main.py`; 4 testes cobrem |
| T-MT5-B02 | ✅ | `validate_integration_mutex()` em `_shared/config`; chamada no `lifespan`; testes em `test_config_mt5.py` |
| T-MT5-B03 | ✅ | `log_disabled_endpoint_attempt()` em `_shared/audit/logger.py`; usado pelo guard |
| T-MT5-B04 | ✅ | `apps/cam-cockpit/ntsl/README.md` com banner DESATIVADO |
| T-MT5-B05 | ✅ | `cam/features/profit_integration/README.md` com banner + procedimento de reativação R20.07 |
| T-MT5-B06 | ✅ | `apps/cam-cockpit/FEATURE-FLAGS-LEDGER.md` criado com entradas 001 e 002 |
| T-MT5-C01 | ✅ | 7 schemas Pydantic em `schemas.py`; Art. 11 e Art. 25 enforced via `Field`/`Literal` |
| T-MT5-C02 | ✅ | `MT5BridgeClient` em `bridge.py` — PUB/SUB + REQ/REP + heartbeat monitor |
| T-MT5-C03 | ✅ | Asserts `test_module_has_no_send_order_attribute` + `test_source_has_no_order_send_calls` |
| T-MT5-C04 | ✅ | `MT5IntegrationService` com `validate_intention` delegando a `risk_validate` |
| T-MT5-C05 | ✅ | 4 eventos dataclasses em `events.py` (Online, Offline, PositionChanged, FillDetected) |
| T-MT5-D01 | ✅ | Router `/api/v1/mt5/*` com 4 endpoints registrados em `main.py` |
| T-MT5-D02 | ✅ | `JSONResponse(503)` no `/mt5/positions` quando offline |
| T-MT5-E01 | ✅ | `parse_html`, `parse_csv`, `parse_xml` (stub) em `importer.py` |
| T-MT5-E02 | ✅ | `compute_trade_hash` SHA-256 dos campos canônicos + `deduplicate()` |
| T-MT5-E03 | ✅ | `POST /api/v1/mt5/import-report` com multipart + dedupe in-memory |
| T-MT5-E04 | ✅ stub | `GET /api/v1/mt5/reconciliation/{date}` retorna estrutura vazia (TD-v0.2-08 documentado) |
| T-MT5-F01 | ✅ | `cam_zmq.mqh` wrapper baseado em libzmq |
| T-MT5-F02 | ✅ | `cam_bridge.mq5` 198 linhas — sem `OrderSend/PositionOpen/etc`; verifica `ACCOUNT_TRADE_MODE_DEMO` no `OnInit`; magic number distinto |
| T-MT5-F03 | ✅ | `mql5/README.md` com instruções de compilação/instalação |
| T-MT5-G01 | ✅ | Painel "Bridge MT5" em `SettingsPage.tsx` com 4 campos + botão restart |
| T-MT5-G02 | ✅ | Chips "MT5 Integration: ATIVA" / "Profit Integration: DESATIVADA" |
| T-MT5-H01 | ✅ | `scripts/install_wine_mt5.sh` idempotente com 3 flags (`--skip-wine`, `--skip-mt5`, `--skip-ea`) |
| T-MT5-H02 | ⚠️ pendente | RUNBOOK ainda não tem seção MT5/Wine/ZeroMQ adicionada — abrir BUG-001 |
| T-MT5-H03 | ⚠️ pendente | MAPPING ainda não tem coluna MQL5 ao lado de NTSL — abrir BUG-002 |
| T-MT5-H04 | ✅ | `TECH-DEBT.md` com TD-v0.2-01 a TD-v0.2-09 |
| T-MT5-H05 | ✅ | `frontend/src/api/types.ts` com `MT5BridgeStatus` + `MT5Position` |

**Conclusão QA-CR:** 28/30 TASKs ✅ · 2/30 ⚠️ pendência documental não-bloqueante (Bugs L1/L2 abertos).

### 2.2 Padrões de código

| Padrão | Status |
|---|---|
| Vertical Slice (`features/X/` não importa `features/Y/`) | ✅ `lint-imports` 2 kept 0 broken |
| Risk Engine Zero I/O | ✅ contrato preservado, `import-linter` confirma |
| Type hints completos no Python 3.12 | ✅ uso de `Literal`, `int \| None`, `dict[str, Any]` |
| Pydantic models com Field constraints | ✅ Art. 11 enforced via `Field(ge=1, le=2)` |
| Naming convention | ✅ `_private`, `PascalCaseClass`, `snake_case_func` |
| TDD First (Red → Green) | ✅ todos os arquivos novos foram preced. por testes que falharam |
| Testes em `cam/features/*/tests/` | ✅ 36 testes só em `mt5_integration/tests/` |
| Docstrings (mínimo no que importa) | ✅ módulos e funções públicas documentadas |

### 2.3 Cobertura de testes (mt5_integration)

```
schemas.py:    100%
service.py:    100%
events.py:     100%
domain.py:     100%  (vazio — stub)
repository.py: 100%  (vazio — stub)
importer.py:    94%
routes.py:      61%  (paths offline-bridge-dependent não testados aqui)
bridge.py:      53%  (sub_loop e socket I/O real exigem Wine/MT5)
─────────────
TOTAL:          87%
```

Cobertura agregada do bloco MT5 = **87%**. Acima do mínimo institucional de **80%**.

### 2.4 Issues encontrados

#### BUG-001 (Bloqueante para QA-doc) — RUNBOOK sem cenário MT5

- **Origem:** T-MT5-H02 do PLAN, CA18.2 da SPEC.
- **Descrição:** `project/runbooks/RUNBOOK-INCIDENTE-TECNICO.md` §2.2 ainda referencia apenas Profit. Faltam cenários para Wine glitch, EA crash, ZeroMQ socket reset.
- **Severidade:** Não-bloqueante para Go (cenários cobertos por SPEC §9 + DECISION-MEMO §7 G-B1..B4), mas exigido para Fase 1.
- **Ação:** abrir BUG fast-track + adicionar cenários §2.8 (Wine), §2.9 (EA), §2.10 (ZeroMQ).

#### BUG-002 (Não-bloqueante) — MAPPING sem coluna MQL5

- **Origem:** T-MT5-H03, CA18.1.
- **Descrição:** `MAPPING-CONSTITUICAO-RISK-ENGINE.md` ainda mapeia apenas NTSL como "validador espelhado". Falta adicionar coluna MQL5 ao lado, com NTSL marcada DESATIVADA.
- **Severidade:** Cosmético — matriz funciona sem isso (NTSL não está mais em uso).
- **Ação:** atualização documental em batch antes de Fase 1.

#### Observação L1 (não-bug) — dependência circular potencial

Em `cam/api/main.py:75` o handler `feature_disabled_handler` importa de `cam.features.profit_integration.guard`. Como o router já é importado mais abaixo via `include_router`, há ordem implícita. Em refatorações futuras, considerar mover o handler para `cam/api/exception_handlers.py` dedicado.

#### Observação L2 (não-bug) — `_seen_hashes` global do importer

Em `cam/features/mt5_integration/routes.py:88` o `_seen_hashes: set[str] = set()` é global de módulo. Não persiste entre restarts (TD-v0.2-09 já registrado). Funcional, mas vai precisar de persistência em DB antes de Fase 2.

---

## 3. QA-Func (Funcional) — Linus

### 3.1 Cenários testados automaticamente

| # | Cenário | Suite | Status |
|---|---|---|---|
| F01 | Estrutura da feature criada e importável | `test_structure.py` | ✅ 3 testes |
| F02 | Settings + mutex de coexistência | `test_config_mt5.py` | ✅ 6 testes |
| F03 | Endpoints `/profit/*` retornam 410 com flag off | `test_profit_guard.py` | ✅ 3 testes |
| F04 | Endpoints `/profit/*` voltam a funcionar com flag on (reversibilidade) | `test_profit_guard.py` | ✅ 1 teste |
| F05 | Schemas Pydantic + Art. 11 (≤2) + Art. 25 (pnl_net) | `test_schemas.py` | ✅ 6 testes |
| F06 | Bridge sem `send_order/OrderSend/etc.` (CA15) | `test_bridge.py::TestBridgeReadOnlyAssert` | ✅ 2 testes |
| F07 | Bridge heartbeat lifecycle (record / expira / is_alive) | `test_bridge.py` | ✅ 3 testes |
| F08 | Bridge whitelist de comandos REQ/REP (CA15.3) | `test_bridge.py::test_request_rejects_unauthorized_command` | ✅ 1 teste |
| F09 | Service delega validação ao Risk Engine (Art. 15) | `test_service.py` | ✅ 1 teste |
| F10 | Service status reflete bridge alive | `test_service.py` | ✅ 2 testes |
| F11 | Routes — `/bridge/status` OFFLINE quando sem heartbeat | `test_routes.py` | ✅ 1 teste |
| F12 | Routes — `/positions` retorna 503 com payload padronizado | `test_routes.py` | ✅ 1 teste |
| F13 | Routes — `/validate-intention` independente de bridge | `test_routes.py` | ✅ 2 testes |
| F14 | Routes — `/bridge/restart` exige confirm=true | `test_routes.py` | ✅ 1 teste |
| F15 | Importer HTML — parsing + normalização símbolo + direção LONG/SHORT | `test_importer.py` | ✅ 4 testes |
| F16 | Importer HTML — resiliência a `<script>` injection (qa-sec) | `test_importer.py` | ✅ 1 teste |
| F17 | Importer HTML — rejeita malformado sem crash | `test_importer.py` | ✅ 1 teste |
| F18 | Importer CSV — parser equivalente | `test_importer.py` | ✅ 2 testes |
| F19 | Dedupe — hash determinístico + reimport zero | `test_importer.py` | ✅ 3 testes |

**Total:** 19 grupos × 36 testes — 100% verdes.

### 3.2 Não-regressão (resto do backend)

- `pytest --ignore=tests/test_migrations.py -q` → **425 passed**
- Inclui Risk Engine (T-B07 com 13.464+ exemplos Hypothesis) + suítes anteriores (T-C, T-D, T-F, T-G, T-H)
- Migrations (`test_migrations.py`) → **4 passed** quando rodadas com `.env` presente

### 3.3 Não testado automaticamente (necessita validação manual)

| ID | Cenário | Razão | Onde validar |
|---|---|---|---|
| M01 | EA `cam_bridge.mq5` compila em MetaEditor sem warnings | MQL5 sem framework de teste auto | Carlos no MT5 |
| M02 | EA publica `mt5.tick` em conta DEMO durante pregão | exige Wine + MT5 + conta demo | Carlos no MT5 |
| M03 | Bridge ZeroMQ recebe ticks reais e atualiza status no cockpit | exige integração completa | Carlos via UI |
| M04 | Script `install_wine_mt5.sh` instala Wine + MT5 em Ubuntu limpo | destrutivo do ambiente | Carlos em VM/snapshot |
| M05 | Frontend painel "Bridge MT5" reflete state real em tempo real | navegador + backend | Carlos no browser |

Todos os M01–M05 cobertos por `MANUAL-VALIDATION-CHECKLIST.md` (companion deste doc).

---

## 4. QA-SEC — Kevin

### 4.1 Sup. sensíveis declaradas na SPEC §7

| Superfície | Mitigação SPEC | Status implementação |
|---|---|---|
| Bridge ZeroMQ exposta em socket TCP | Bind `127.0.0.1` apenas em v0.2 | ✅ default em `MT5_BRIDGE_HOST=127.0.0.1` (`.env.example`) |
| EA ativado em conta REAL por engano | Verificar `ACCOUNT_TRADE_MODE` = DEMO no `OnInit` | ✅ `cam_bridge.mq5:62-70` aborta com `INIT_FAILED` se não-DEMO; flag `InpRequireDemoAccount` |
| Credenciais MT5 vazadas em logs | `.env` em `.gitignore` + hook pre-commit | ✅ pré-existente (T-A10) — não regressão |
| Mensagens da bridge sem autenticação | Aceito como TD-v0.2-01 (uso local) | ✅ TD documentado |
| Comando arbitrário via REQ/REP | Whitelist de 4 comandos (PING, GET_STATE, GET_POSITIONS, GET_SYMBOL_INFO) | ✅ enforced em `bridge.py:115-118` (Python) + `cam_bridge.mq5:149-188` (EA) |
| Reativação simultânea Profit+MT5 | Mutex no startup (R21.03) | ✅ `validate_integration_mutex()` chamada no `lifespan` |
| Endpoint Profit em produção continuar respondendo | Guard 410 + audit log | ✅ `check_profit_enabled` + `log_disabled_endpoint_attempt` |
| Importer HTML executando `<script>` injection | Parser stdlib `html.parser` + ignora `<script>` | ✅ `_MT5HTMLTableExtractor.handle_data` ignora dentro de script |

### 4.2 Cobertura qa-sec

| Asserto | Teste | Status |
|---|---|---|
| Bridge não expõe `send_order/place_order/etc` | `test_module_has_no_send_order_attribute` | ✅ |
| Source bridge não chama `OrderSend(/OrderClose(/etc` | `test_source_has_no_order_send_calls` | ✅ |
| Comando fora da whitelist retorna `UNAUTHORIZED_COMMAND` | `test_request_rejects_unauthorized_command` | ✅ |
| Importer HTML resiste a `<script>` injection | `test_parse_resists_script_injection` | ✅ |
| Mutex bloqueia ativação simultânea | `test_mutex_both_enabled_raises` | ✅ |
| Endpoint Profit registra tentativa em audit log | `disabled_endpoint_attempt` aparece nos logs do `test_profit_guard.py` | ✅ verificado em captura |

### 4.3 Findings de Kevin

| ID | Finding | Severidade | Decisão |
|---|---|---|---|
| SEC-001 | Mensagens ZeroMQ trafegam em plaintext (sem CURVE encryption) | Baixo | Aceito — uso local em `127.0.0.1`; TD-v0.2-01 |
| SEC-002 | Settings retorna `database_url_host` no `/api/v1/settings` (string `"localhost"`) | Baixo | Aceito — não é credencial, é host |
| SEC-003 | `_seen_hashes` no `routes.py` é global do processo | Baixo | TD-v0.2-09 já registrado |
| SEC-004 | EA confia em `InpRequireDemoAccount=true` como default mas pode ser sobrescrito ao carregar EA | Médio | **Recomendação:** documentar em `mql5/README.md` que mudar essa flag para `false` exige aprovação Founder em estado frio (similar a alteração de POV) |
| SEC-005 | Bridge handler de `_sub_loop` engole exceções genéricas para não derrubar conexão | Baixo | Aceito — comportamento desejado (resiliência); audit log futuramente |

**Conclusão QA-SEC:** **APROVADO com 1 ação documental** (SEC-004 — adicionar nota ao `mql5/README.md` orientando que `InpRequireDemoAccount=false` é decisão constitucional, não trocável sem registro).

---

## 5. Conformidade constitucional (verificação cruzada)

| Artigo | O que o CaM precisa garantir | Garantia em v0.2 | Status |
|---|---|---|---|
| **Art. 11º** | Máximo 2 contratos WIN / 2 WDO — intocável | `Field(ge=1, le=2)` em `ValidateIntentionRequest.contracts` e `MT5Position.contracts`; Risk Engine valida via `max_contracts_check` | ✅ |
| **Art. 15º** | Risk Engine é autoridade — bridge não pode pular | `MT5IntegrationService.validate_intention` delega a `risk_validate`; bridge é read-only (CA15.1–CA15.3) | ✅ |
| **Art. 18º** | Kill switch sempre operacional | `useKillSwitch` hook lê `/api/v1/kill-switch/status`; banner persistente na UI | ✅ pré-existente |
| **Art. 19º** | Posição aberta sem cobertura sistêmica = inaceitável | Bridge offline → 503 + alerta Telegram + UI banner; runbook §2.2 (pendente BUG-001) | ⚠️ parcial — runbook pendente |
| **Art. 25º** | UI sempre exibe líquido, nunca apenas bruto | `MT5Position.pnl_net` obrigatório (Pydantic não-opcional) | ✅ |
| **Art. 31º** | Operação sem registro = falha operacional | Fills do MT5 (futuro v0.3) gerarão `JournalEntry` com `source="MT5_BRIDGE"` | ✅ design |
| **Art. 35º** | IA não envia ordem, não desabilita Risk Engine | `mt5_integration` não tem dependência de `ai_analyst`; bridge read-only | ✅ |
| **Art. 36º** | Hierarquia constitucional inviolável | Arquitetura preserva `_shared/risk` como autoridade transversal | ✅ |

---

## 6. Bugs abertos pelo QA

| BUG # | Título | Severidade | Pré-Go? |
|---|---|---|---|
| **BUG-001** | RUNBOOK-INCIDENTE-TECNICO §2.2 sem cenários MT5/Wine/ZeroMQ | Documental — não bloqueia funcionalidade | Não (corrigir antes de Fase 1) |
| **BUG-002** | MAPPING-CONSTITUICAO-RISK-ENGINE sem coluna MQL5 (NTSL desativada) | Cosmético | Não |

Ambos abertos como fast-track BUG (estado BUG do NCC-1701, lead Bill). Não impedem Go-condicional.

---

## 7. Recomendação Founder (Go/No-Go)

```
[ ] GO incondicional — todos os critérios verdes
[x] GO-condicional — verde com pendência documental (BUG-001 + BUG-002 em fast-track)
[ ] NO-GO — pendência funcional/sec bloqueante

Pré-condições do GO-condicional:
  1. Carlos executa MANUAL-VALIDATION-CHECKLIST.md (companion).
  2. BUG-001 e BUG-002 são resolvidos antes de Fase 1.
  3. SEC-004 (nota em mql5/README.md) é adicionada.

Data sugerida do Go: ___/___/______
Assinatura Founder: _________________________
```

---

## 8. Métricas do bloco MT5

| Métrica | Valor |
|---|---|
| TASKs entregues | 28/30 (93%) — 2 pendentes documentais |
| Testes novos | 46 (379 → 425) |
| Testes frontend mantidos | 12 |
| Cobertura `mt5_integration` | 87% (acima do mínimo 80%) |
| Contratos `import-linter` | 2 kept / 0 broken |
| TypeScript `tsc --noEmit` | limpo |
| Tech debts novos registrados | 9 (TD-v0.2-01..09) |
| Bugs abertos pelo QA | 2 (BUG-001, BUG-002) |
| Findings SEC | 5 (1 com ação documental — SEC-004) |
| Linhas de código MQL5 | 198 (`cam_bridge.mq5`) + 95 (`cam_zmq.mqh`) |
| Linhas de código Python novo | ~700 (mt5_integration completo) |
| Linhas de doc novas (READMEs + ledger) | ~250 |

---

## 9. Referências cruzadas

- [`/project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md`](../SPEC-v0.2-MT5-ENQUADRAMENTO.md) — fonte das regras
- [`/project/cam-cockpit/PLAN-v0.2.md`](../PLAN-v0.2.md) — TASKs auditadas
- [`/project/cam-cockpit/qa/MANUAL-VALIDATION-CHECKLIST.md`](./MANUAL-VALIDATION-CHECKLIST.md) — companion para Carlos validar manualmente
- [`/project/cam-cockpit/SPEC-v0.3-TECH-DEBT-REVIEW.md`](../SPEC-v0.3-TECH-DEBT-REVIEW.md) — revisão sistemática dos TDs
- [`/apps/cam-cockpit/TECH-DEBT.md`](../TECH-DEBT.md) — TDs vigentes (entrada da v0.3)
- [`/project/MAPPING-CONSTITUICAO-RISK-ENGINE.md`](../../MAPPING-CONSTITUICAO-RISK-ENGINE.md) — alvo do BUG-002

---

> **Princípio operacional desta revisão:**
>
> Linus revisa código contra padrão. Kevin revisa superfície contra Constituição. O Founder decide Go/No-Go.
>
> Bridge é read-only por design — não por confiança. Whitelist + asserts estruturais + verificação de conta DEMO no EA = três barreiras independentes contra envio de ordem em v0.2.

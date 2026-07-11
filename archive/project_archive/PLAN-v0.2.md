---
template: PLAN
phase: PLAN
status: Approved (letscode)
version: 0.2
date: 2026-05-25
parent_spec: SPEC-v0.2-MT5-ENQUADRAMENTO.md
pmg: G
sec: true
qa_sec: true
---

# PLAN v0.2 — Enquadramento MT5 (coexistência com Profit)

> **Lead:** Nico · **Co-lead:** Albert (loop P/M/G) · **SEC:** Kevin
> **Skill:** `teczi-code-planning`
> **Aprovador:** Founder
> **Origem:** [`SPEC-v0.2-MT5-ENQUADRAMENTO.md`](./SPEC-v0.2-MT5-ENQUADRAMENTO.md) v0.2.1
>
> **Princípio operacional:** TDD First (Nikola escreve testes antes do código). Toda TASK que toca código produz teste → falha (Red) → mínimo de código (Green) → refatora se necessário.

---

## 1. P/M/G

| Campo | Valor |
|---|---|
| Classe SPEC | **G** (Albert) |
| Concordância Nico | **Sim — G confirmada.** Sete frentes técnicas distintas (Python feature, MQL5 EA, ZeroMQ, importer multi-formato, frontend, script Bash, governança de feature flags). |
| Re-classificação | Não aplicável |
| Loop com Albert | Não necessário |

---

## 2. Blocos e TASKs (flat, executáveis por Nikola)

> Convenção: T-MT5-{BLOCO}{N}. Cada TASK é auto-contida. Dependências explicitam apenas pré-condições estruturais.
> Marcadores: `[sec]` = Kevin obrigatório no CODE; `[qa-sec]` = Kevin obrigatório no QA.

### Bloco MT5-A — Fundação (estrutura + deps + flags)

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-A01 | Adicionar `pyzmq` em `pyproject.toml` (deps principais) | `pyproject.toml` com `pyzmq>=26.0`; `uv sync` instala sem conflito | — | — |
| T-MT5-A02 | Criar skeleton de `cam/features/mt5_integration/` (domain, schemas, repository, service, routes, events, bridge, importer, tests, README) | Pasta com 9 arquivos vazios + `README.md` documentando contrato da feature; importável (`from cam.features import mt5_integration`) | T-MT5-A01 | — |
| T-MT5-A03 | Criar estrutura `apps/cam-cockpit/mql5/{experts,indicators,scripts,include}/` + `README.md` raiz | 4 diretórios + 1 README com instruções de compilação/instalação | — | — |
| T-MT5-A04 | Adicionar variáveis MT5 em `.env.example` e `cam/_shared/config/` | Variáveis novas (sem remover Profit): `MT5_BRIDGE_HOST`, `MT5_BRIDGE_PUB_PORT`, `MT5_BRIDGE_REQ_PORT`, `MT5_WINE_PREFIX`, `MT5_TERMINAL_PATH`, `MT5_INTEGRATION_ENABLED`, `PROFIT_INTEGRATION_ENABLED` | T-MT5-A02 | — |
| T-MT5-A05 | Adicionar `cam.features.mt5_integration` ao contrato `import-linter` (independência); `lint-imports` continua passando | `pyproject.toml` atualizado; CI `uv run lint-imports` → 2 kept, 0 broken | T-MT5-A02 | — |

### Bloco MT5-B — Coexistência + Desativação Profit `[sec]` `[qa-sec]`

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-B01 | Implementar guard `Depends(check_profit_enabled)` no router de `profit_integration` que retorna HTTP 410 quando flag desativada | Endpoints `/api/v1/profit/*` retornam 410 com payload R20.02 da SPEC; testes covering | T-MT5-A04 | sec, qa-sec |
| T-MT5-B02 | Implementar mutex de startup: backend falha graciosamente se `PROFIT_INTEGRATION_ENABLED=true` E `MT5_INTEGRATION_ENABLED=true` | `cam/api/lifespan.py` valida no startup; mensagem clara referenciando R21.03 | T-MT5-A04 | sec |
| T-MT5-B03 | Adicionar funções audit `log_disabled_endpoint_attempt` em `cam/_shared/audit/logger.py` | Função registra: endpoint, IP do cliente, timestamp, motivo (`PROFIT_INTEGRATION_DISABLED`) | — | sec |
| T-MT5-B04 | Criar `apps/cam-cockpit/ntsl/README.md` com banner "DESATIVADO em 2026-05-25 — ver SPEC v0.2 §2.1" | README criado; diretório `ntsl/` NÃO movido | — | — |
| T-MT5-B05 | Atualizar (ou criar) `cam/features/profit_integration/README.md` com banner DESATIVADO + procedimento de reativação (R20.07) | README com banner claro + comando exato para reativar via `.env` | — | — |
| T-MT5-B06 | Criar `apps/cam-cockpit/FEATURE-FLAGS-LEDGER.md` com primeira entrada (PROFIT_INTEGRATION_ENABLED→false em 2026-05-25) | Ledger inicial criado | — | sec |

### Bloco MT5-C — Bridge ZeroMQ (read-only) `[sec]` `[qa-sec]`

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-C01 | Implementar schemas Pydantic em `cam/features/mt5_integration/schemas.py` (MT5Tick, MT5Position, MT5BridgeStatus, ValidateIntentionRequest/Response, ImportResult) | Schemas conforme SPEC §4.1; testes de serialização | T-MT5-A02 | — |
| T-MT5-C02 | Implementar `cam/features/mt5_integration/bridge.py` — cliente ZeroMQ assíncrono (SUB para PUB do EA, REQ para REP), com heartbeat monitor (R12.04) | `MT5BridgeClient` com `connect()`, `disconnect()`, `request(cmd) -> dict`, `subscribe(topic, handler)`, `is_alive() -> bool`, propriedade `last_heartbeat_age_ms` | T-MT5-C01 | sec, qa-sec |
| T-MT5-C03 | Garantir que `bridge.py` NÃO expõe `send_order` (CA15) — assert estrutural via teste | Teste verifica via inspeção que módulo não tem atributo `send_order` nem chama `OrderSend`; falha em CI se for adicionado | T-MT5-C02 | sec, qa-sec |
| T-MT5-C04 | Implementar `cam/features/mt5_integration/service.py` — `MT5IntegrationService` orquestra bridge + heartbeat + reconexão + publicação de eventos `MT5BridgeOnline/Offline` | Service com `start()`, `stop()`, `get_status()`, `validate_intention(candidate, ctx)`; reconexão automática a cada 2s quando offline (R16.02) | T-MT5-C02 | sec |
| T-MT5-C05 | Implementar eventos em `cam/features/mt5_integration/events.py` — `MT5BridgeOffline`, `MT5BridgeOnline`, `MT5FillDetected`, `MT5PositionChanged` | Dataclasses de evento + payload mínimo | T-MT5-C01 | — |

### Bloco MT5-D — Routes + Endpoints HTTP `[sec]` `[qa-sec]`

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-D01 | Implementar `cam/features/mt5_integration/routes.py` — `/mt5/bridge/status`, `/mt5/bridge/restart`, `/mt5/positions`, `/mt5/validate-intention` (stub conectado ao service) | Router registrado em `cam/api/main.py`; respostas conforme SPEC §4.2 | T-MT5-C04 | sec |
| T-MT5-D02 | Endpoints retornam HTTP 503 com payload `{"error":"MT5_BRIDGE_OFFLINE", ...}` quando bridge offline (R16.01) | Testes cobrindo cenário offline | T-MT5-D01 | sec, qa-sec |

### Bloco MT5-E — Importador de relatório MT5 `[qa-sec]`

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-E01 | Implementar parsers em `cam/features/mt5_integration/importer.py` — `parse_html(content) -> list[ParsedTrade]`, `parse_xml`, `parse_csv` | Parser HTML usa `html.parser` ou `lxml` (sem `<script>` injection); cobertura ≥90% | T-MT5-C01 | qa-sec |
| T-MT5-E02 | Implementar deduplicação por hash da operação (SPEC R15.02) — `compute_trade_hash(parsed) -> str` | SHA-256 de `(timestamp, ativo, direção, contratos, entry, exit)`; reimportação detecta 100% duplicatas | T-MT5-E01 | — |
| T-MT5-E03 | Endpoint `POST /api/v1/mt5/import-report` com `multipart/form-data`, retorna `ImportResult` | Endpoint funcional; cria `JournalEntry` com `source = "MT5_IMPORT"` via `journal/service.py` | T-MT5-E02, T-MT5-D01 | qa-sec |
| T-MT5-E04 | Endpoint `GET /api/v1/mt5/reconciliation/{date}` — compara JournalEntries manuais × importados | Endpoint retorna pares prováveis; matching por (timestamp, ativo, contratos) | T-MT5-E03 | — |

### Bloco MT5-F — EA MQL5 `cam_bridge.mq5` `[sec]` `[qa-sec]`

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-F01 | Implementar `apps/cam-cockpit/mql5/include/cam_zmq.mqh` — wrapper MQL5 para libzmq.dll (PUB/SUB + REQ/REP) | Wrapper com inicialização, send/recv, cleanup; documentação inline | T-MT5-A03 | sec |
| T-MT5-F02 | Implementar `apps/cam-cockpit/mql5/experts/cam_bridge.mq5` — EA read-only que publica `mt5.tick`, `mt5.position`, `mt5.fill`, `mt5.heartbeat` via PUB e responde `GET_STATE`, `GET_POSITIONS`, `GET_SYMBOL_INFO`, `PING` via REP | EA sem `OrderSend/PositionOpen/etc` (CA15.1); verifica conta DEMO no startup; magic number distinto v0.2 (sec §7.1) | T-MT5-F01 | sec, qa-sec |
| T-MT5-F03 | Atualizar `apps/cam-cockpit/mql5/README.md` com instruções: compilar via MetaEditor, instalar em `MQL5/Experts/`, atachar a símbolo WIN ou WDO, canais ZeroMQ documentados | README operacional | T-MT5-F02 | — |

### Bloco MT5-G — Frontend (Settings + status badges)

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-G01 | Atualizar `frontend/src/features/settings/SettingsPage.tsx` adicionando seção "Bridge MT5" (status chip, heartbeat, latência, restart button, path detectado) | Painel novo abaixo dos existentes; consome `/api/v1/mt5/bridge/status` | T-MT5-D01 | — |
| T-MT5-G02 | Atualizar SettingsPage com chips lado a lado: "Profit Integration: DESATIVADA" + "MT5 Integration: ATIVA" | Status visível conforme `/api/v1/settings` (que precisa expor flags) | T-MT5-G01 | — |

### Bloco MT5-H — Setup Wine + Documentação Governamental

| # | TASK | Saída esperada | Depende de | Marcadores |
|---|---|---|---|---|
| T-MT5-H01 | Criar `apps/cam-cockpit/scripts/install_wine_mt5.sh` — instala Wine, baixa MT5, copia EA para diretório `Experts` do MT5 | Script idempotente com flags `--skip-wine`, `--skip-mt5`; cabeçalho com pré-requisitos | T-MT5-F02 | — |
| T-MT5-H02 | Atualizar `project/runbooks/RUNBOOK-INCIDENTE-TECNICO.md` §2.2 ADICIONANDO comandos Wine + MT5 + ZeroMQ (cenários Profit permanecem) | RUNBOOK atualizado sem remoção | — | — |
| T-MT5-H03 | Atualizar `project/MAPPING-CONSTITUICAO-RISK-ENGINE.md` adicionando referências MQL5 ao lado de NTSL (NTSL com marca DESATIVADO) | Matriz expandida sem remoção | — | — |
| T-MT5-H04 | Atualizar `apps/cam-cockpit/TECH-DEBT.md` com TD-v0.2-01 a TD-v0.2-07 da SPEC §8 | 7 entradas novas appendadas | — | — |
| T-MT5-H05 | Atualizar `frontend/src/api/types.ts` adicionando tipos MT5 (`MT5BridgeStatus`, `MT5Position`, `MT5Tick`) | Tipos consistentes com Pydantic do backend | T-MT5-C01 | — |

---

## 3. Sequência sugerida (caminho crítico)

```
A (Fundação)
   ↓
B (Coexistência/Desativação Profit) — pode rodar paralelo a C, D, E
   ↓
C (Bridge ZeroMQ) → D (Routes) → E (Importer)
   ↓
F (EA MQL5) — paralelo a C/D/E porque é código MQL5 separado
   ↓
G (Frontend) — depende de D
   ↓
H (Setup Wine + Documentação) — encerra
```

Em prática esta sessão: A → B → C → D → E → H (parcial) → F (estrutura, não executável sem Wine) → G

---

## 4. Riscos do PLAN

| Risco | Mitigação |
|---|---|
| EA MQL5 não testável automatizado em Linux dev | Implementar conforme spec MQL5 oficial; validação manual em conta demo fica para Founder (TODO-OPERACIONAL) |
| Bridge ZeroMQ requer MT5 + EA rodando para teste de integração real | Testes Python usam mocks do socket ZeroMQ; teste real só com Wine + MT5 (TD-v0.2-02) |
| `pyzmq` exige `libzmq3-dev` no sistema | Documentar no `scripts/install_wine_mt5.sh`; cair gracioso se import falhar |
| Reativação acidental de Profit em paralelo | Mutex de startup T-MT5-B02 garante falha clara |
| Endpoints `/api/v1/profit/*` em produção sendo consumidos por algum cliente externo | 410 com payload claro orienta migração; ledger de tentativas T-MT5-B03 |

---

## 5. Reuso aplicado

| Decisão/Artefato | Onde aplicado |
|---|---|
| ADR-013 (Vertical Slice + Shared Kernel) | `mt5_integration/` segue mesma anatomia de outras features (T-MT5-A02) |
| Feature flag pattern | T-MT5-B01 usa Depends() do FastAPI — padrão idiomático |
| Audit logger T-H05 | Reaproveitado em T-MT5-B03 (`log_disabled_endpoint_attempt`) |
| Padrão de routers existentes | T-MT5-D01 segue `kill_switch/routes.py` como template |
| Padrão de feature README | T-MT5-A02 segue README das outras features |

---

## 6. `letscode`

| Campo | Valor |
|---|---|
| Status | **`true`** |
| Aprovado por | Founder (Carlos Rodrigues Ferreira Junior) em 2026-05-25 |
| Motivo | Mensagem direta do Founder: "OK spec aprovada vamos para plan e code direto" |

> **Instrução TDD First confirmada:** Nikola escreve testes antes de cada TASK. Os testes são o "modelo mental" da TASK.

**Proof Pack:** G obrigatório. Consolidado ao final dos blocos quando todos os testes verdes + cobertura preservada.

---

## 7. Histórico

| Versão | Data | Mudança |
|---|---|---|
| 0.2 | 2026-05-25 | PLAN inicial — produzido via NCC-1701 PLAN, lead Nico |

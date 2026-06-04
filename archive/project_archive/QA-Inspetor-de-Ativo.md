---
template: QA
phase: QA
status: Draft — aguarda execução E2E do Founder
produto: CaM — The Carlos Alternative Money
slice: Inspetor de Ativo (MVP)
lead: Linus
sec_colead: Kevin (QA-SEC)
date: 2026-06-01
relacionados: SPEC-Inspetor-de-Ativo, PLAN-Inspetor-de-Ativo, ADR-014, RUNBOOK-MT5-INSPETOR
---

# QA — Inspetor de Ativo (MVP)

> Homologação contra os 12 critérios de aceite (SPEC §10 / SCOPE §12). Três frentes:
> **QA-CR** (code review/estático) · **QA-Func** (funcional E2E) · **QA-SEC** (Kevin).
> **Go** = todos os critérios verdes, com destaque bloqueante para o critério 8 (read-only).

---

## 0. Sumário de status

| Frente | Estado | Observação |
|---|---|---|
| **QA-CR** (estático) | ✅ **VERDE** | ruff All checks passed · import-linter 2 kept/0 broken · 82 testes pass · app importa · alembic head único |
| **QA-Func** (E2E) | ⏳ **PENDENTE** | exige MT5 + EA atachado + `npm install` + `alembic upgrade head` na máquina do Founder |
| **QA-SEC** (Kevin) | 🟡 **PARCIAL** | provas estáticas verdes; falta validar banner REAL + book em conta real |
| **Gaps conhecidos** | ✅ **0** | Critério 7 (tick → `cam_market_ticks`) implementado via `TickPersister` (batch) — ver §4 |

---

## 1. QA-CR — Code review / verificação estática (✅ executável já)

| # | Verificação | Comando | Esperado | Status |
|---|---|---|---|---|
| CR-1 | Lint dos arquivos do slice | `ruff check cam/features/{regime,mt5_integration,fundamentals}` | All checks passed | ✅ |
| CR-2 | Contratos de arquitetura (ADR-013) | `python -m importlinter.cli lint` | 2 kept / 0 broken | ✅ |
| CR-3 | Testes puros + feature | `pytest cam/features/{regime,fundamentals,mt5_integration}/tests` | 82 passed | ✅ |
| CR-4 | App compõe sem erro | `python -c "import cam.api.main"` | APP_IMPORT_OK | ✅ |
| CR-5 | Migration encadeia | `alembic heads` | head único `e1f2a3b4c5d6` | ✅ |
| CR-6 | Frontend typecheck/build | `npm install && npm run build` | build ok | ⏳ (sem Node no ambiente de dev) |
| CR-7 | Testes de UI | `npm test` (Sidebar MVP) | pass | ⏳ |

---

## 2. QA-Func — Critérios de aceite E2E (⏳ requer MT5 ligado)

> Pré-condições: MT5 aberto + `cam_bridge` atachado (`InpRequireDemoAccount=false`),
> `MT5_BRIDGE_AUTOCONNECT=true`, `alembic upgrade head`, backend + frontend no ar.
> Ver `RUNBOOK-MT5-INSPETOR.md`.

| # | Critério | Passo | Esperado | Status |
|---|---|---|---|---|
| 1 | Candles rápidos | Buscar `PETR4` (D1) | Gráfico em < 2s | ⏳ |
| 2 | Tick/book ao vivo | Observar após buscar | Chip "Último" atualiza sem reload; book quando disponível | ⏳ |
| 3 | 7 indicadores R-20 | Buscar `PETR4` | DY, P/L, P/VP, ROE, Dív/EBITDA, Payout, ROIC (N/A onde a brapi não tem) | ⏳ |
| 4 | Dividendos + 2 estimativas | Buscar `PETR4` | Histórico + run-rate 12m + DY-médio 3–5a, ambos rotulados "estimativa" | ⏳ |
| 5 | Futuro só gráfico | Buscar `WIN$` | Só gráfico; sem bloco de fundamentos/regime; **sem erro** | ⏳ |
| 6 | Falha segura | Matar o EA | Header → `WS OFFLINE`; tela não mente sobre dado fresco | ⏳ |
| 7 | Tick persistido | Tick ao vivo → banco | Aparece em `cam_market_ticks` (`TickPersister` em lote) | ⏳ E2E (impl ✅) |
| 8 | **Read-only (bloqueante)** | `grep -r OrderSend` no slice + allowlist | `OrderSend` vazio; comando fora da allowlist rejeitado | 🟡 estático ✅ / E2E ⏳ |
| 9 | Sidebar reduzido | Abrir cockpit | 4 itens (Inspetor, Cockpit, Constituição, Configurações); rotas ocultas acessíveis por URL | ⏳ (teste unit ✅) |
| 10 | Banner REAL | Conta MT5 real | Banner **REAL** no header durante a sessão | ⏳ |
| 11 | Bloco de Regime (ação) | Buscar `PETR4` em D1 | Estado, matriz 3×3, estacionária, sinal, Sharpe/maxDD + "histórico, não preditivo" | ⏳ |
| 12 | Regime omitido | Buscar `MXRF11`/`WIN$` | Bloco de Regime ausente, sem erro | ⏳ |

### Verificação por endpoint (sem UI)

```
GET /api/v1/mt5/symbols              → {"symbols":[...]}  (503 se OFFLINE)
GET /api/v1/mt5/candles?symbol=PETR4&timeframe=D1&count=200
GET /api/v1/fundamentals/PETR4       → 7 R-20 + dividends_history + dividend_projection
GET /api/v1/regime/PETR4             → após carregar D1 (popula cam_inspector_candles)
```

---

## 3. QA-SEC — Kevin (gatilho: perímetro EA + Art. 35º)

| # | Controle | Verificação | Status |
|---|---|---|---|
| SEC-1 | EA sem ordem | `grep OrderSend apps/cam-cockpit/mql5/experts/cam_bridge.mq5` = vazio | ✅ (estático) |
| SEC-2 | Allowlist bridge | `MT5BridgeClient._READ_ONLY_COMMANDS` só leitura; comando fora → `UNAUTHORIZED_COMMAND` | ✅ (código) / ⏳ E2E |
| SEC-3 | Allowlist EA (CA15.3) | comando fora da whitelist no `cam_bridge.mq5` → rejeitado + logado | ✅ (código) / ⏳ E2E |
| SEC-4 | Sem secret commitado | `BRAPI_TOKEN` só via `.env`/keyring; `.env` não versionado | ✅ |
| SEC-5 | Banner REAL | header marca REAL em conta real | ⏳ E2E |
| SEC-6 | Slice read-only | nenhuma rota do Inspetor envia ordem/parametriza Risk Engine | ✅ (revisão) |
| SEC-7 | Regime read-only | `/regime` não emite sinal de execução (papel A); instalador Markov **não** rodado | ✅ |

---

## 4. Critério 7 (tick → `cam_market_ticks`) — implementado

**Estado:** ✅ **implementado** (faltava na primeira passada; fechado no QA).

**Como:** `TickPersister` (`tick_persister.py`) assina `mt5.tick` no bridge, normaliza
(`asset, price, volume, timestamp, source="mt5.cam_bridge"`) e faz **flush em lote**
a cada ~1s (não um INSERT por tick — protege o event loop; `Art. 19` fail-safe: erro de
banco não derruba o stream). Iniciado em `service.connect()`, parado em `disconnect()`.

**Mapeamento de preço:** usa `last`; se ausente, cai para o mid `(bid+ask)/2`.

**A validar no E2E:** após observar `PETR4` por alguns segundos,
`SELECT count(*) FROM cam_market_ticks WHERE source='mt5.cam_bridge'` > 0.

---

## 5. Veredito

- **QA-CR:** ✅ Go.
- **QA-Func / QA-SEC E2E:** ⏳ bloqueado por ambiente (MT5 + Node) — executar pelo runbook.
- **Critério 7:** ✅ implementado (`TickPersister`) — resta confirmar no E2E.

> **Gate QA/Founder:** após o E2E, Carlos marca Go/No-Go. Critério 8 (read-only) é
> bloqueante — se falhar, No-Go imediato (SEC-GOV/Kevin).
>
> [ ] Carlos Rodrigues Ferreira Junior — Data: ___/___/______

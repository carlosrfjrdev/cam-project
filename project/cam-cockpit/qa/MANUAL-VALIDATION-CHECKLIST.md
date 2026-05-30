---
template: MANUAL-VALIDATION
phase: QA
status: Draft
version: 1
date: 2026-05-25
companion_of: QA-REVIEW-SPEC-v0.2.md
---

# MANUAL-VALIDATION — Checklist de Validação Manual do Cockpit CaM

> **Para:** Founder (Carlos)
> **Pré-condição:** QA-REVIEW-SPEC-v0.2 com recomendação **Go-condicional**.
> **Duração estimada:** sessão única em PC com Wine instalado, ou divisível em blocos.
>
> Cada item é binário (✅ OK / ❌ Falhou). Em caso de falha, abrir BUG fast-track citando o item.

---

## Como usar

1. Tenha o RUNBOOK aberto em outra aba: [`/project/runbooks/RUNBOOK-INCIDENTE-TECNICO.md`](../../runbooks/RUNBOOK-INCIDENTE-TECNICO.md)
2. Tenha o [`RUNBOOK.md`](../../runbooks/RUNBOOK.md) (técnico de subida) aberto.
3. Execute item a item, marcando ✅/❌.
4. Ao final, assine §10 (Go/No-Go do Founder).

---

## Bloco 1 — Subida do ambiente (Backend + Frontend + DB)

> Use `RUNBOOK.md` "Subir o ambiente (uso diário)" como referência.

- [ ] **1.1** `docker compose up -d db` sobe TimescaleDB sem erro.
  - Verificar: `docker compose ps` mostra `db` healthy.
- [ ] **1.2** `cd backend && uv run uvicorn cam.api.main:app --reload --port 8000` sobe sem traceback.
  - Verificar: logs mostram `Application startup complete.`
  - **R21.03 check:** se a saída tiver `RuntimeError: R21.03 violado`, o `.env` está com Profit+MT5 ambos true — corrigir.
- [ ] **1.3** `cd frontend && npm run dev` sobe sem erro de compile.
  - Verificar: `VITE ready` no terminal + http://localhost:5173 abre.
- [ ] **1.4** Health check: `curl http://localhost:8000/api/v1/health` → `{"status":"ok","version":"0.1.0"}`.

---

## Bloco 2 — Painéis básicos (regressão visual)

Abra http://localhost:5173 e navegue por cada item:

- [ ] **2.1** Cockpit Live carrega. P&L exibe R$ 0,00 (sem WS conectado, fallback gracioso).
- [ ] **2.2** **Layout sem padding/margin esquisito** — content alinhado ao drawer (fix anterior).
- [ ] **2.3** Header tem o botão "Kill Switch" visível e responsivo (sem cinza/quebrado).
- [ ] **2.4** Drawer lateral mostra 10 itens de navegação clicáveis.
- [ ] **2.5** Navegar para cada uma das 10 rotas — nenhuma deve mostrar tela branca:
  - / (Cockpit Live)
  - /journal
  - /fiscal
  - /harvest
  - /risk
  - /constitution
  - /paper-trading
  - /carteira-hard
  - /backtest
  - /settings

---

## Bloco 3 — Fluxo Journal (criar entrada manual)

- [ ] **3.1** Em `/journal`, preencher o formulário:
  - Data: hoje
  - Ativo: WIN
  - Direção: LONG
  - Contratos: 1
  - Entrada: 135000
  - Saída: 135200
  - Custos: 1.50
  - Estratégia: "teste validacao"
  - Setup: "manual"
- [ ] **3.2** Clicar "Registrar" → não exibe `Alert` de erro (`submitError === null`).
- [ ] **3.3** Tabela abaixo lista a nova entrada com:
  - Bruto = R$ 40,00 (200 pontos × R$ 0,20)
  - Líquido = positivo (40 - 1.50 - 8 = 30.50)
  - IR Prov. ≈ R$ 8,00
- [ ] **3.4** Reimportar não está em escopo — testar apenas criação manual.

---

## Bloco 4 — Kill switch (Art. 18º)

- [ ] **4.1** No header, clicar "Kill Switch".
- [ ] **4.2** Dialog aparece pedindo motivo (proteção contra acidente).
- [ ] **4.3** Digitar "Teste validação Q&A" + clicar "Ativar Kill Switch".
- [ ] **4.4** Chip "ATIVO" vermelho aparece ao lado do botão.
- [ ] **4.5** Banner vermelho aparece imediatamente abaixo do header.
- [ ] **4.6** Banner permanece visível em **todas as 10 telas** ao navegar.
- [ ] **4.7** No Risk Console, verificar que decisão recente registra kill switch acionado.
- [ ] **4.8** Tentar `POST /api/v1/mt5/validate-intention` via curl com kill switch ativo (deve ser rejeitado):
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"WIN","direction":"LONG","contracts":1,"intended_stop_loss_points":"150"}'
  ```
  Esperado: `{"approved": false, "reason": "Kill switch ativo", ...}`.
- [ ] **4.9** Clicar "Kill Switch" novamente → dialog "Desativar" → confirmar → banner some, chip some.

---

## Bloco 5 — Coexistência Profit/MT5 (SPEC v0.2.1 R21)

- [ ] **5.1** Verificar que `.env` tem `PROFIT_INTEGRATION_ENABLED=false` e `MT5_INTEGRATION_ENABLED=true`.
- [ ] **5.2** Endpoint Profit retorna 410:
  ```bash
  curl -s http://localhost:8000/api/v1/profit/reconciliation/2026-05-25 | python3 -m json.tool
  ```
  Esperado: `error: PROFIT_INTEGRATION_DISABLED` no top-level (não dentro de `"detail"`).
- [ ] **5.3** Endpoint MT5 funciona:
  ```bash
  curl -s http://localhost:8000/api/v1/mt5/bridge/status | python3 -m json.tool
  ```
  Esperado: `state: OFFLINE` (porque EA não está rodando) + `host: 127.0.0.1`.
- [ ] **5.4** Em `/settings`, verificar chips:
  - "MT5 Integration: ATIVA" (verde)
  - "Profit Integration: DESATIVADA" (cinza outline)
- [ ] **5.5** Painel "Bridge MT5" exibe `OFFLINE` + heartbeat `—`.
- [ ] **5.6** **Mutex (R21.03)**: editar `.env` para `PROFIT_INTEGRATION_ENABLED=true` + `MT5_INTEGRATION_ENABLED=true`, reiniciar backend.
  - Esperado: backend falha no startup com `RuntimeError: R21.03 violado — PROFIT_INTEGRATION_ENABLED e MT5_INTEGRATION_ENABLED não podem estar ambos true...`
- [ ] **5.7** Reverter `.env` para `PROFIT=false / MT5=true` e reiniciar. Backend sobe normalmente.

---

## Bloco 6 — Constituição (read-only)

- [ ] **6.1** Em `/constitution`, a Constituição é exibida na íntegra (texto do CONSTITUICAO.md).
- [ ] **6.2** Chip "v1.0" aparece no header da página.
- [ ] **6.3** Botão "Propor Emenda (apenas registro)" abre dialog.
- [ ] **6.4** Preencher campos do dialog + clicar "Registrar Proposta" — não dá erro.
- [ ] **6.5** Sem endpoint PUT direto: tentar `curl -X PUT http://localhost:8000/api/v1/constitution/current` → resposta 405 Method Not Allowed.

---

## Bloco 7 — Paper Trading (CA5.5 — badge SIMULAÇÃO)

- [ ] **7.1** Em `/paper-trading`, badge **vermelho "SIMULAÇÃO — PAPER TRADING"** visível no canto superior direito.
- [ ] **7.2** Borda do form em vermelho (`error.light`).
- [ ] **7.3** Preencher form e clicar "Simular (Paper)":
  - Ativo: WIN, Direção: LONG, Contratos: 1, Entrada: 135000, Stop: 134850, Take Profit: 135300, Estratégia: "teste"
- [ ] **7.4** Painel "Resultado da Simulação" aparece com:
  - Chip verde "APROVADO PELO RISK ENGINE"
  - P&L líquido exibido com prefixo R$ (não NaN)
- [ ] **7.5** Tentar contracts=3 (violação Art. 11º): formulário aceita mas backend deve retornar 422 (validação Pydantic `Field(ge=1, le=2)`).

---

## Bloco 8 — Fiscal (Art. 25º — sempre líquido)

- [ ] **8.1** Em `/fiscal`, painel "Apuração Mensal" mostra valores (R$ 0,00 se não há entradas) — **nenhum NaN**.
- [ ] **8.2** "Histórico de DARFs" exibe tabela vazia ou DARFs gerados.
- [ ] **8.3** Não há campo "Resultado Bruto" sem o "Resultado Líquido" ao lado.

---

## Bloco 9 — EA MQL5 (Wine + MT5 — exige setup prévio)

> Pré-requisito: ter rodado `bash apps/cam-cockpit/scripts/install_wine_mt5.sh` ou instalado MT5 manualmente.

- [ ] **9.1** Wine instalado: `wine --version` retorna versão (winehq-stable 9.x+).
- [ ] **9.2** MT5 instalado em `~/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe`.
- [ ] **9.3** `libzmq.dll` copiada para `<MT5_data_folder>/MQL5/Libraries/` (download manual no GitHub do ZeroMQ).
- [ ] **9.4** Abrir MT5: `wine "$HOME/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"`.
- [ ] **9.5** Logar em **conta DEMO** (NUNCA conta real em v0.2).
- [ ] **9.6** Tools → Options → Expert Advisors:
  - [x] Allow Algo Trading
  - [x] Allow DLL imports
- [ ] **9.7** F4 (MetaEditor) → abrir `cam_bridge.mq5` → F7 (compilar).
  - **CA12.1:** compila sem warnings.
- [ ] **9.8** Drag-and-drop EA na janela de gráfico WIN ou WDO.
- [ ] **9.9** Confirmar parâmetros do EA:
  - PubPort = 5556
  - ReqPort = 5557
  - RequireDemoAccount = true (NÃO MEXER — sec §7.1)
  - MagicNumber = 20260525
- [ ] **9.10** Logs do MT5 (aba "Experts") mostram `[CamBridge] v0.2 read-only ativo`.
- [ ] **9.11** No backend rodando, verificar bridge online:
  ```bash
  curl -s http://localhost:8000/api/v1/mt5/bridge/status | python3 -m json.tool
  ```
  Esperado em 5–10 segundos: `state: ONLINE` + `last_heartbeat_age_ms` < 1500.
- [ ] **9.12** No frontend `/settings`, painel "Bridge MT5":
  - Chip verde `ONLINE`
  - Heartbeat "há 0.X s"
  - Latência média preenchida após primeiro comando REQ/REP
- [ ] **9.13** Testar comando ping:
  ```bash
  # opcional — exige client zmq python interativo
  python3 -c "
  import zmq
  c = zmq.Context()
  s = c.socket(zmq.REQ)
  s.connect('tcp://127.0.0.1:5557')
  s.send_json({'cmd': 'PING'})
  print(s.recv_json())
  "
  ```
  Esperado: `{"status":"ok","data":"PONG"}`.
- [ ] **9.14** Tentar comando não-whitelist:
  ```bash
  python3 -c "
  import zmq
  c = zmq.Context()
  s = c.socket(zmq.REQ)
  s.connect('tcp://127.0.0.1:5557')
  s.send_json({'cmd': 'SEND_ORDER'})
  print(s.recv_json())
  "
  ```
  Esperado: `{"error":"UNAUTHORIZED_COMMAND","cmd":"SEND_ORDER"}`.
- [ ] **9.15** Fechar MT5 (matar processo). Em ≤ 5 segundos:
  - `/api/v1/mt5/bridge/status` retorna `state: OFFLINE`.
  - Frontend painel reflete OFFLINE.

---

## Bloco 10 — Importador de relatório MT5

- [ ] **10.1** Em MT5 (qualquer conta com histórico), Reports → "Save as HTML" → salvar arquivo.
- [ ] **10.2** Importar via API:
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/import-report \
    -F "file=@/caminho/para/relatorio.html"
  ```
- [ ] **10.3** Resposta indica `imported: N` (número de trades parseados).
- [ ] **10.4** Reimportar o **mesmo arquivo** → resposta indica `duplicates: N, imported: 0`.

---

## 11. Tentativas adversariais (qa-sec)

- [ ] **11.1** **`<script>` injection no importer:** criar arquivo HTML contendo `<script>alert('xss')</script>` antes da tabela. Importar → não dá erro de execução; trades válidos da tabela ainda parseados.
- [ ] **11.2** **Direção inválida no validate-intention:**
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"WIN","direction":"BUY","contracts":1,"intended_stop_loss_points":"150"}'
  ```
  Esperado: 422 (apenas LONG/SHORT aceitos).
- [ ] **11.3** **Contracts > 2 (Art. 11º):**
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"WIN","direction":"LONG","contracts":3,"intended_stop_loss_points":"150"}'
  ```
  Esperado: 422 (Field(le=2)).
- [ ] **11.4** **Ativo não-WIN/WDO:**
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"PETR4","direction":"LONG","contracts":1,"intended_stop_loss_points":"150"}'
  ```
  Esperado: 422 (Literal["WIN","WDO"]).

---

## 12. Audit log (verificação opcional)

- [ ] **12.1** Logs estruturados em `~/.cam/logs/cam-audit.log` (se rodando com `--reload`, pode estar no stderr).
- [ ] **12.2** Após Bloco 5.2 (chamada a endpoint Profit desativado), verificar evento `DISABLED_ENDPOINT_ATTEMPT` no log.
- [ ] **12.3** Após Bloco 4.3 (kill switch ativo), verificar evento `KILL_SWITCH_ACTIVATED`.
- [ ] **12.4** (SPEC v0.3 T-TD-027) Após Bloco 4.9 (kill switch desativado), verificar evento `KILL_SWITCH_DEACTIVATED`.
- [ ] **12.5** (SPEC v0.3 T-TD-027) Após Bloco 7.3 (simulação paper) ou 13.E.2, verificar evento `RISK_DECISION` no log.

---

## 13. Itens SPEC v0.3 — saneamento tech debts (novos cenários)

### 13.A — T-TD-001: novo validator `total_open_contracts_check` (Art. 12º explícito)

- [ ] **13.A.1** Editar manualmente `cam/features/mt5_integration/routes.py::_build_stub_context` adicionando uma `OpenPosition(asset=AssetType.WIN, contracts=ContractCount(1), direction=Direction.LONG, entry_price=Decimal("135000"))` em `open_positions=[...]`. Salvar + reload do backend.
- [ ] **13.A.2** Tentar validar +1 WIN em Fase 1 (deve REJEITAR — soma 2 > limite 1):
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"WIN","direction":"LONG","contracts":1,"intended_stop_loss_points":"150"}'
  ```
  Esperado: `approved: false` + `validator: total_open_contracts_check`.
- [ ] **13.A.3** Reverter `_build_stub_context` ao estado original (sem `open_positions`). Reload. Validar `approved: true`.

### 13.B — T-TD-005: harvest reage a DARF paga

- [ ] **13.B.1** Em `/fiscal`, com pelo menos uma DARF visível, clicar "Marcar como Paga".
- [ ] **13.B.2** Verificar log do backend — `harvest_service.handle_darf_paid` é chamado via subscribe ao evento `DarfPaid`.
- [ ] **13.B.3** Sem crash do backend após mark-paid.

### 13.C — T-TD-026: WebSocket P&L emite mensagens

- [ ] **13.C.1** No browser, `/` (Cockpit Live) — chip "WS" deve ficar `ONLINE` em ≤ 6 segundos.
- [ ] **13.C.2** P&L mostra R$ 0,00 (stub) — sem erro no DevTools Console.
- [ ] **13.C.3** DevTools → Network → WS → frame `/api/v1/ws/pnl` recebe JSON com `daily_pnl_net`, `timestamp`, `source: "stub"` a cada 5s.

### 13.D — T-TD-v0.2-06: painel feature flags via API

- [ ] **13.D.1** `curl -s http://localhost:8000/api/v1/settings | python3 -m json.tool` mostra campo `feature_flags` com `profit_integration_enabled: false`, `mt5_integration_enabled: true`, `websocket_pnl_real_data: false`.

### 13.E — T-TD-027: audit log no Risk Engine via MT5

- [ ] **13.E.1** Executar:
  ```bash
  curl -X POST http://localhost:8000/api/v1/mt5/validate-intention \
    -H "Content-Type: application/json" \
    -d '{"asset":"WIN","direction":"LONG","contracts":1,"intended_stop_loss_points":"150"}'
  ```
  Esperado: log de audit contém `event_type=RISK_DECISION` com `decision=APPROVED`.

### 13.F — T-TD-012: Sharpe Ratio numérico (não NaN)

- [ ] **13.F.1** Em `/backtest`, executar backtest stub.
- [ ] **13.F.2** Campo "Sharpe Ratio" exibe `0.00` ou valor numérico — **nunca `NaN`**.

---

## 14. Resumo dos resultados

| Bloco | Total itens | ✅ | ❌ | Pendente |
|---|---:|---:|---:|---:|
| 1 — Subida | 4 | | | |
| 2 — Painéis básicos | 5 | | | |
| 3 — Journal | 4 | | | |
| 4 — Kill switch | 9 | | | |
| 5 — Coexistência | 7 | | | |
| 6 — Constituição | 5 | | | |
| 7 — Paper Trading | 5 | | | |
| 8 — Fiscal | 3 | | | |
| 9 — EA MQL5 | 15 | | | |
| 10 — Importador | 4 | | | |
| 11 — Adversarial | 4 | | | |
| 12 — Audit | 5 | | | |
| **13 — SPEC v0.3** | **9** | | | |
| **TOTAL** | **79** | | | |

---

## 15. Go/No-Go do Founder

```
[ ] GO — todos os blocos ≥ 90% verde, blocos críticos (4, 5, 11) = 100% verde
[ ] GO-CONDICIONAL — pendências documentadas como BUG fast-track
[ ] NO-GO — falha em bloco crítico (4 kill switch, 5 coexistência, 11 adversarial)

Comentários:
________________________________________________
________________________________________________

Data: ___/___/______
Assinatura: _________________________
```

---

> **Princípio operacional deste checklist:**
>
> Validação manual existe porque MQL5 não tem framework de teste automatizado e Wine introduz variável de ambiente real.
>
> Bloqueio em qualquer item adversarial (Bloco 11) = NO-GO automático. Bloqueio em kill switch (Bloco 4) = NO-GO constitucional (Art. 18º).

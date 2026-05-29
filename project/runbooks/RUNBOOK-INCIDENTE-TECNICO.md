---
template: RUNBOOK
phase: OPS
status: Draft
version: 1
date: 2026-05-25
---

# RUNBOOK — Incidente Técnico com Posição Aberta

> **Lead:** Vint (OPS, infra)
> **Suporte:** Bill (incidente)
> **Skill:** `teczi-deploy` (componente OPS)
> **Aprovador:** Founder
> **Vinculação constitucional:** Art. 19º (contingência técnica)
> **Dependência:** [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](../DECISION-MEMO-LINUX-OR-WINDOWS.md) — comandos e telefones específicos da plataforma variam conforme escolha
>
> **Este é documento de campo.** Em pânico técnico durante pregão, o Founder lê este doc. Não é manual conceitual.

---

## 1. Princípio

**Posição aberta sem cobertura sistêmica é risco inaceitável.** (Art. 19º)

- Falhou a primeira camada (plataforma local)? Use a segunda (home broker da corretora).
- Falhou a segunda? Use a terceira (telefone da mesa de operações).
- Nenhuma justificativa de "oportunidade perdida" pesa contra **fechar a posição** quando não há cobertura sistêmica.

### Princípio derivado para incidente

```
Em incidente com posição aberta:
1. FECHAR a posição (custo de loss é aceitável)
2. REGISTRAR o evento (Art. 19º + Art. 31º)
3. INVESTIGAR depois (pregão fechado)
```

**Nunca:** investigar primeiro, fechar depois.

---

## 2. Cenários cobertos

### 2.1 Plataforma (Profit / MT5) trava ou fecha sozinha

**Sintoma identificável:**
- Janela do Profit ou MT5 congelada (botões não respondem)
- Aplicativo fechou inesperadamente
- Plataforma reabre mas conta aparece desconectada

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO ficar tentando reiniciar a plataforma com posição aberta.
- ❌ NÃO assumir que "vai voltar em 1 minuto" — cada segundo com posição aberta sem visibilidade é risco.
- ❌ NÃO fechar o cockpit (Python/React) sem registrar o evento primeiro.

**Ação imediata (em ordem):**

1. **Confirmar posição aberta:** verificar no home broker da corretora ou ligar para a mesa de operações.
2. **Fechar pelo home broker:** entrar no home broker web (Clear, XP, Genial, etc.) → posições abertas → encerrar posição → confirmar OK.
3. **Se home broker não responder:** ligar para mesa de operações imediatamente.
4. **Registrar evento:** abrir `cam_kill_switch_events` via cockpit (se backend Python estiver rodando) OU abrir terminal e fazer entrada manual no JSONL fallback (`~/.cam/journal/YYYY-MM-DD.jsonl`).
5. **Acionar kill switch:** evitar nova operação no resto do dia.
6. **Pós-incidente (item §3):** investigar causa raiz antes do próximo pregão.

**Canal de fechamento:**
- **Home broker web da corretora** (vinculada em CORRETORA-EVAL.md §9).
- **Mesa de operações** — telefone confirmado em §4.
- **App mobile da corretora** — segundo canal alternativo.

---

### 2.2 Bridge (ProfitDLL / ZeroMQ) perde conexão com posição aberta

**Sintoma identificável:**
- Cockpit mostra "WS OFFLINE" persistentemente.
- Status do Risk Engine indica "stale" (sem heartbeat há > 3 segundos).
- Plataforma broker (Profit/MT5) parece estar OK localmente.
- Nenhum evento de tick chegou no log nos últimos 10 segundos.

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO assumir que cockpit ainda tem visibilidade da posição.
- ❌ NÃO enviar nova ordem pelo cockpit (Risk Engine pode estar trabalhando com dado defasado).
- ❌ NÃO desligar o backend Python sem registrar evento.

**Ação imediata (em ordem):**

1. **Confirmar posição na plataforma broker (não no cockpit):** abrir janela do Profit/MT5 e ver a tela de posições nativa.
2. **Decidir:** se posição está OK e estratégia ainda quer manter → ajustar stop manualmente na plataforma broker.
3. **Se decisão de fechar:** fechar **pela plataforma broker** (não pelo cockpit).
4. **Reiniciar a bridge:** comando do RUNBOOK do app (§4 deste doc).
5. **Verificar reconexão:** cockpit deve mostrar "WS ONLINE" + heartbeat OK.
6. **Registrar evento:** entrada em `cam_kill_switch_events` ou JSONL fallback.

**Comandos (variante Windows+Profit):**
```powershell
# Reiniciar bridge ProfitDLL (Fase 5+) — substituir pelo serviço real quando implementado
Stop-Service "CaM-ProfitBridge" -Force
Start-Service "CaM-ProfitBridge"
```

**Comandos (variante Linux+MT5):**
```bash
# Reiniciar EA + ZeroMQ bridge
docker compose -f ~/cam-cockpit/docker-compose.yml restart mt5_bridge
# ou se Wine local:
pkill -f cam_bridge && wine "$HOME/.wine/drive_c/.../terminal64.exe" &
```

---

### 2.3 Backend Python (FastAPI) cai com posição aberta

**Sintoma identificável:**
- Frontend (React) mostra erro de conexão ("Network Error" em todas as chamadas).
- `curl http://localhost:8000/api/v1/health` retorna erro.
- Logs do uvicorn pararam de rolar.

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO entrar em pânico — o backend caído **não afeta** a posição aberta na plataforma broker (Profit/MT5).
- ❌ NÃO reiniciar imediatamente sem entender o motivo da queda — pode estar em loop de crash.

**Ação imediata (em ordem):**

1. **Verificar posição na plataforma broker** (não no cockpit) — Profit/MT5 nativo.
2. **Decidir** se posição precisa ser fechada ou se pode continuar até a plataforma broker oferecer cobertura suficiente.
3. **Reiniciar backend:**
   ```bash
   cd ~/teczilabs/CaM-project/apps/cam-cockpit/backend
   uv run uvicorn cam.api.main:app --reload --port 8000
   ```
4. **Verificar health:** `curl http://localhost:8000/api/v1/health` deve retornar `{"status":"ok"}`.
5. **Verificar logs estruturados:** `tail -f ~/.cam/logs/cam-audit.log` para entender a causa da queda.
6. **Registrar evento** no journal duplo (banco + JSONL).
7. **Acionar kill switch preventivo** até causa raiz estar resolvida.

**Pós-incidente:**
- Causa raiz documentada em `BUG-NNN.md` em `/project/cam-cockpit/bugs/` (criar diretório se não existir).
- Teste de regressão adicionado se aplicável.

---

### 2.4 Internet local cai com posição aberta

**Sintoma identificável:**
- Plataforma broker (Profit/MT5) mostra "Sem conexão"
- Cockpit mostra todos os serviços offline simultaneamente
- Ping para google.com falha

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO ficar esperando a internet voltar com posição aberta sem stop ativo.

**Ação imediata (em ordem):**

1. **Ativar fallback de internet** (4G/5G via celular como hotspot — §4 contatos da operadora).
2. **Confirmar reconexão:** plataforma broker conecta no mercado.
3. **Confirmar posição:** verificar tela de posições da plataforma broker.
4. **Se hotspot demora > 2min:** **ligar para mesa de operações** e fechar por telefone.
5. **Registrar evento.**

**Pós-incidente:**
- Se a queda da operadora primária durar > 30min em horário de pregão, considerar **trocar** ou **adicionar** segundo provedor (operadora reserva permanente).

---

### 2.5 Banco PostgreSQL fica indisponível com posição aberta

**Sintoma identificável:**
- Backend Python logs: `psycopg.OperationalError: could not connect to server`
- Frontend: endpoints que tocam DB retornam 500
- `docker compose ps` mostra container `db` parado ou unhealthy

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO tentar UPDATE/DELETE direto no banco se conseguir conectar — pode corromper estado.
- ❌ NÃO desligar o container do banco sem fazer dump antes (a menos que esteja corrompido beyond repair).

**Ação imediata (em ordem):**

1. **Plataforma broker** (Profit/MT5) **continua operando normalmente** — banco caído não afeta posição aberta.
2. **Cockpit em modo degradado:** journal duplo JSONL (`~/.cam/journal/YYYY-MM-DD.jsonl`) continua sendo escrito ao lado.
3. **Investigar container:** `docker compose logs db`.
4. **Tentar reiniciar:** `docker compose restart db` (apenas o serviço db, não tudo).
5. **Se não voltar:** restaurar do último backup conhecido (`~/cam-backups/db/cam_db_YYYYMMDD.sql.gz`).
6. **Registrar evento operacional** via JSONL (Art. 31º — fallback obrigatório).
7. **Acionar kill switch** — nova operação só após banco voltar online + reconciliação JSONL → DB.

**Reconciliação pós-recuperação:**
- Comparar última entrada do JSONL com última entrada do banco.
- Replayar entradas JSONL ausentes via endpoint `POST /api/v1/journal/replay` (a implementar quando o banco voltar — atualmente é tech debt TD-002).

---

### 2.6 Energia elétrica cai

**Sintoma identificável:**
- Tudo desligado simultaneamente.
- No-break (se houver) começa a beepar.

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO assumir que o no-break vai aguentar até a luz voltar.

**Ação imediata (em ordem):**

1. **Verificar previsão de retorno** pela operadora de energia (§4).
2. **Se posição aberta:** ligar para mesa de operações da corretora **pelo celular** (não depende da energia local).
3. **Fechar a posição por telefone** (não tentar fechar por home broker mobile com bateria limitada).
4. **Aguardar energia voltar** e fazer fechamento ordenado dos serviços antes do no-break esgotar.
5. **Pós-recuperação:** verificar integridade do banco (`docker compose exec db pg_isready`), do JSONL e da última operação no broker.
6. **Registrar evento.**

**Pós-incidente:**
- Se quedas elétricas forem recorrentes (>1 por mês), considerar **no-break dedicado** para Mac/PC + roteador (custo PF, fora do perímetro Art. 8º).

---

### 2.7 Corretora reporta indisponibilidade

**Sintoma identificável:**
- Status page da corretora indica indisponibilidade.
- Comunicado oficial em redes/email.
- Outros operadores reportam o mesmo via Twitter / fóruns BR.

**Primeiro reflexo — o que NÃO fazer:**
- ❌ NÃO acreditar que "vai voltar em 5 minutos" — corretoras frequentemente subestimam recovery time.

**Ação imediata (em ordem):**

1. **Confirmar via canal oficial** (status page, e-mail oficial da corretora).
2. **Se posição aberta na corretora indisponível:** ligar para mesa de operações **imediatamente** — algumas corretoras mantêm telefone funcional mesmo com plataforma fora.
3. **Se mesa também indisponível:** registrar tudo (screenshots, logs) — é evento de cobertura de ressarcimento (CORRETORA-EVAL §6 pergunta 26).
4. **Aguardar normalização** sem tentar enviar novas ordens.
5. **Acionar kill switch** preventivo.
6. **Pós-recuperação:** reconciliar com extrato da corretora e abrir chamado formal se houver execução errada.

---

## 3. Para cada cenário — Estrutura comum

Esta seção formaliza a estrutura aplicada em §2.

### 3.1 Como registrar o evento

Todo evento da §2 deve gerar **3 artefatos**:

1. **Entrada em `cam_kill_switch_events`** (banco) — se backend e DB estiverem operacionais.
2. **Entrada em JSONL fallback** (`~/.cam/journal/YYYY-MM-DD.jsonl`) — sempre, mesmo com banco operacional (journal duplo Art. 31º).
3. **Entrada em audit log** (`~/.cam/logs/cam-audit.log`) — automático se `_shared/audit/logger.py` (T-H05) estiver carregado.

**Campos mínimos:**
```json
{
  "timestamp_utc": "2026-XX-XXTHH:MM:SSZ",
  "event_type": "TECH_FAILURE",
  "scenario_id": "2.X",
  "had_open_position": true,
  "position_closed_by": "home_broker | mesa | platform | none",
  "position_closed_at": "ISO8601 ou null",
  "kill_switch_activated": true,
  "raw_loss_brl": 0.00,
  "operator_note": "texto livre — descrição do incidente"
}
```

### 3.2 Pós-incidente — o que revisar antes do próximo pregão

| Verificação | Confirmação |
|---|---|
| Plataforma broker funciona normalmente | ✅ |
| Cockpit Python responde `/api/v1/health` | ✅ |
| Banco aceita conexões e tem dados consistentes | ✅ |
| Internet primária + fallback testados | ✅ |
| Mesa de operações da corretora atende | ✅ |
| Causa raiz do incidente identificada | ✅ |
| Plano de evitar repetição definido | ✅ |
| Evento registrado nos 3 artefatos da §3.1 | ✅ |
| Aderência calculada (Art. 29º) — se afetou alguma operação | ✅ |
| Checklist pré-mercado executado normalmente | ✅ |

> Sem TODOS os ✅, o próximo pregão começa **com kill switch ativo** até resolução.

---

## 4. Contatos pré-cadastrados

> Founder preenche cada campo antes do dia 1 da Fase 1. Sem campos preenchidos, este runbook é incompleto.

### 4.1 Corretora vinculada

> Definida em [`CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) §9 após decisão final.

| Campo | Valor |
|---|---|
| Nome da corretora | _________________________________ |
| Telefone mesa de operações | _________________________________ |
| Horário da mesa | _________________________________ |
| E-mail oficial | _________________________________ |
| Status page (URL) | _________________________________ |
| Conta vinculada (apenas final, sem dados completos) | ___ |

### 4.2 Suporte da plataforma de execução

> Específico para Profit (variante A do DOC 1) OU MT5 (variante B). Definir após DECISION-MEMO resolvido.

| Campo | Valor |
|---|---|
| Plataforma | _________________________________ |
| Suporte técnico (telefone) | _________________________________ |
| Suporte técnico (e-mail / chat) | _________________________________ |
| Horário do suporte | _________________________________ |
| Conta/login (apenas usuário, não senha) | _________________________________ |

### 4.3 Operadora de internet primária

| Campo | Valor |
|---|---|
| Operadora | _________________________________ |
| Telefone suporte | _________________________________ |
| Status page | _________________________________ |

### 4.4 Fallback de internet

| Campo | Valor |
|---|---|
| Modalidade (4G/5G via celular, segunda operadora) | _________________________________ |
| Operadora do fallback | _________________________________ |
| Dado mensal disponível | _________________________________ |
| Procedimento de ativação | _________________________________ |

### 4.5 Operadora de energia elétrica

| Campo | Valor |
|---|---|
| Operadora | _________________________________ |
| Telefone para previsão de retorno | _________________________________ |

### 4.6 Backup operacional pessoal

| Campo | Valor |
|---|---|
| Notebook reserva (modelo + onde está) | _________________________________ |
| Celular reserva (com app do home broker já configurado) | _________________________________ |

---

## 5. Checklist do pré-pregão para validar redundância

> Faz parte do checklist pré-mercado (Art. 32º) **expandido para o CaM**.

A cada início de pregão, verificar:

- [ ] Plataforma broker (Profit/MT5) conecta na corretora? Login OK?
- [ ] Cockpit responde em http://localhost:8000/api/v1/health?
- [ ] Banco aceita conexões? (`docker compose exec db pg_isready -U cam -d cam_db`)
- [ ] Internet primária estável? (`ping -c 3 google.com`)
- [ ] Fallback de internet testado nos últimos 7 dias?
- [ ] No-break ligado e bateria > 80%?
- [ ] Celular carregado > 50% como backup móvel?
- [ ] Mesa de operações da corretora foi confirmada como funcional nos últimos 30 dias?
- [ ] Kill switch responde quando acionado (teste rápido via UI)?
- [ ] JSONL do dia foi criado (`~/.cam/journal/YYYY-MM-DD.jsonl`)?
- [ ] Audit log do dia foi inicializado (`~/.cam/logs/cam-audit.log`)?

> **Falhou qualquer item:** próximo pregão começa com kill switch ativo até resolução.

---

## 6. Treinamento obrigatório pré-Fase 1

> **Exigência:** simulação dos cenários §2.1 e §2.4 antes de Carlos abrir conta real (Fase 2).

### 6.1 Cenário §2.1 — Plataforma broker trava

Procedimento de simulação (conta demo):
1. Abrir conta demo da corretora escolhida + plataforma broker.
2. Abrir 1 contrato simulado WIN.
3. **Forçar travamento** da plataforma broker (fechar processo via task manager / kill -9).
4. **Cronometrar** o tempo até fechar a posição pela home broker web.
5. **Registrar** o evento conforme §3.1.
6. **Critério de aceite:** posição fechada em ≤ 60 segundos via home broker, evento registrado nos 3 artefatos.

### 6.2 Cenário §2.4 — Internet cai

Procedimento de simulação:
1. Abrir 1 contrato simulado em conta demo.
2. **Desligar Wi-Fi/Ethernet** do PC.
3. **Ativar hotspot do celular** (4G/5G).
4. **Reconectar PC** via hotspot.
5. **Cronometrar** o tempo total de reconexão.
6. **Critério de aceite:** reconexão em ≤ 120 segundos, posição visível na plataforma broker após reconexão, evento registrado.

### 6.3 Registro de treinamento

Cada simulação concluída deve gerar entrada no journal com `event_type=TRAINING_SIMULATION`. Sem **pelo menos 1 simulação completa de cada cenário §6.1 e §6.2 nos últimos 90 dias**, a Fase 1 não está autorizada (referência [`GATE-FASE-0-PARA-1.md`](../GATE-FASE-0-PARA-1.md)).

---

## 7. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior:

    a) Leu este runbook integralmente e compreende as 7 categorias
       de cenário (§2.1 a §2.7).

    b) Comprometeu-se a preencher todos os campos da §4 antes do
       dia 1 da Fase 1.

    c) Executou — ou agendou para executar antes da Fase 1 — as
       simulações obrigatórias §6.1 e §6.2 em conta demo.

    d) Reconhece que o princípio operacional é "fechar primeiro,
       investigar depois" e não "investigar primeiro, decidir depois".

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../../CONSTITUICAO.md) Arts. 18º (kill switch), 19º (contingência), 31º (journal), 32º (checklist pré), 33º (checklist pós)
- [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](../DECISION-MEMO-LINUX-OR-WINDOWS.md) — define plataforma e comandos específicos
- [`CORRETORA-EVAL.md`](../CORRETORA-EVAL.md) — fonte de telefones e canais §4
- [`POV-VIGENTE-v1.0.md`](../POV-VIGENTE-v1.0.md) §3.4 — limites que pioram em estado degradado
- [`apps/cam-cockpit/backend/cam/_shared/audit/logger.py`](../../apps/cam-cockpit/backend/cam/_shared/audit/logger.py) — funções de audit trail (T-H05)
- [`apps/cam-cockpit/scripts/backup.sh`](../../apps/cam-cockpit/scripts/backup.sh) — para restauração pós-cenário §2.5
- [`GATE-FASE-0-PARA-1.md`](../GATE-FASE-0-PARA-1.md) — item de checklist que exige treinamento §6 completo

---

> **Princípio operacional deste documento:**
>
> Vint mantém a infra. Bill investiga depois. Carlos fecha primeiro.
>
> Em pânico técnico com posição aberta, **fechar > investigar > esperar**. Nenhuma justificativa pesa contra fechar a posição.

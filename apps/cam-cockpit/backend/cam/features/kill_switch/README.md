# Feature: kill_switch

## Propósito

Gerencia o estado operacional do Kill Switch do CaM. Quando ativo, bloqueia toda operação de trading via Risk Engine. Implementa o Art. 18º da Constituição.

## Artigos Constitucionais

- **Art. 18º** — Kill switch obrigatório, acionável sem justificar oportunidade perdida
- **Art. 15º** — Risk Engine bloqueia quando kill switch ativo (validator `kill_switch_active_check`)
- **Art. 19º** — Posição aberta com falha técnica aciona kill switch imediatamente

## I/O

**Inputs:**
- `POST /api/v1/kill-switch/activate` — `{ reason: str }`
- `POST /api/v1/kill-switch/deactivate` — `{ confirm: true }` (confirmação explícita obrigatória)
- `GET /api/v1/kill-switch/status` — sem body

**Outputs:**
- Estado atual: `{ active: bool, activated_at: datetime | null, reason: str | null }`

## Eventos Publicados

- `KillSwitchActivated` — consumido por `notifications` (alerta Telegram imediato)
- `KillSwitchDeactivated` — consumido por `notifications`

## Anti-padrões

- Desativar sem campo `confirm: true` explícito no body
- Implementar lógica de negócio fora deste módulo que altera o estado do kill switch
- Exportar o estado sem passar pela tabela `cam_kill_switch_events` (source of truth)
- IA acessar endpoints de ativação/desativação (Art. 35º)

## Dependências

- `cam._shared.risk` — validator `kill_switch_active_check` lê o estado daqui
- `cam._shared.events` — publica `KillSwitchActivated` / `KillSwitchDeactivated`
- `cam._shared.infra` — sessão de banco para persistir em `cam_kill_switch_events`

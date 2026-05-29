---
template: INSPECTION-MAP
phase: DISC
status: Aguardando-Gate-Founder
demand: cast-reorg-5-times
date: 2026-05-28
pmg: G
sec: true
lead: Leo (orquestração) · Oscar + Kevin (ADR perímetro)
gate: "⛔ §2 — reportar ao Founder e aguardar aprovação antes de mover/criar/reescrever"
---

# Mapa de Inspeção — Reorganização do Cast em 5 Times

> Fase obrigatória §2 do `PROMPT-CLAUDECODE-CAST-CAM-5TIMES.md`. **Read-only.**
> Nada foi movido, criado ou reescrito. Este documento existe para o gate do Founder.

---

## 1. Estado real (árvore)

### 1.1 `teczi-devflow/personas/` (dono atual do cast)

29 arquivos:
- **26 personas individuais:** ada, alan, albert, andy, bill, **carlos**, denis, don, florence, fred, grace, howard, kevin, leo, linus, mammon, marty, nico, nikola, oscar, peter, steve, sun, tom, vint, voltaire
- **3 índices/catálogos:** `README.md`, `personas-teczilabs.md` (cast unificado), `personas-devflow.md`

> ⚠️ `carlos.md` existe como persona do Founder. D6 diz "Founder é guardião constitucional, NÃO criar persona de compliance" — `carlos.md` não é compliance, é a ficha do Founder. **Decisão pendente:** mover para `/personas` (em qual time? ou raiz `/personas/carlos.md` sem time?) ou manter fora do cast operacional. Ver gate.

### 1.2 `.claude/agents/` (agents operacionais Claude Code)

25 agents (sem `carlos`, sem índices): ada, alan, albert, andy, bill, denis, don, florence, fred, grace, howard, kevin, leo, linus, mammon, marty, nico, nikola, oscar, peter, steve, sun, tom, vint, voltaire

### 1.3 `.claude/skills/` (13 skills)

Todas `teczi-*` (11 DevFlow) + `strategy-session` + `teczi-discovery-software`. **Nenhuma `cam-*` ainda.**

---

## 2. Padrão extraído (a replicar)

### 2.1 Persona canônica (`teczi-devflow/personas/X.md`)
```
# Nome — Role
> Persona de IA. Agente institucional especializado em ...
---
## Identidade   (TABELA: Nome | Inspiração | Origem do nome | Código | Cor | Ícone | Símbolo | Role | Tom)
## Quem é
## Funções Institucionais
...
```

### 2.2 Agent Claude Code (`.claude/agents/X.md`)
```
---
name: x
description: "X — Title. Invocar para ..."
---
# Nome — Role
Você é **X**, ...
## Inspiração
## Identidade   (BULLETS: Código / Cor / Ícone / Símbolo / Tom)
## Instruções
### Comportamento
...
- Persona completa: `teczi-devflow/personas/X.md`   ← rodapé com referência
```

### 2.3 Skill (`.claude/skills/{skill}/SKILL.md`)
```
---
name: skill-name
description: "..."
phase: FASE
lead_persona: X
co_lead_persona: Y
status: draft (Stage 0 — execução manual via Founder)
---
# Skill — skill-name
## 1. Propósito ... ## 2. Quando acionar ... (procedimento, in/out, gates, ancoragem)
```

> **Cor e ícone vivem no CORPO** (`## Identidade`), **não** no frontmatter. Cada persona tem `Código` (estável, MAIÚSCULO), cor hex + nome, ícone Lucide, símbolo, tom.

---

## 3. Inventário de cores + ícones (NÃO colidir)

| Persona | Cor (hex) | Nome cor | Ícone Lucide |
|---|---|---|---|
| ada | `#F43F5E` | Rose | Database |
| alan | `#22D3EE` | Cyan | Cpu |
| albert | `#F59E0B` | Amber | Lightbulb |
| andy | `#D946EF` | Fuchsia | Palette |
| bill | `#EF4444` | Red | Bug |
| denis | `#84CC16` | Lime | BookOpen |
| don | `#F97316` | Orange | Users |
| florence | `#C084FC` | Lavender | HeartPulse | *(será aposentada → cor liberada)* |
| fred | `#78716C` | Stone | Workflow |
| grace | `#EAB308` | Gold | Blocks |
| howard | `#A67C52` | Sandy Brown | ScanSearch |
| kevin | `#166534` | Forest Green | Fingerprint |
| leo | `#E65100` | Deep Orange | Crown |
| linus | `#0D9488` | Teal | ShieldCheck |
| mammon | `#D4AF37` | Gold | Star | *(mantém)* |
| marty | `#1A237E` | Deep Indigo | Telescope |
| nico | `#8B5CF6` | Purple | ClipboardList |
| nikola | `#10B981` | Green | Code2 |
| oscar | `#0EA5E9` | Blue | Building2 |
| peter | `#3B82F6` | Blue | Target |
| steve | `#EC4899` | Pink | Rocket |
| sun | `#6366F1` | Indigo | Compass |
| tom | `#334155` | Slate Deep | GitBranch |
| vint | `#64748B` | Slate | Server |
| voltaire | `#881337` | Wine | Sword |

---

## 4. Referências ao caminho antigo (a atualizar na execução)

| Arquivo | Refs | Tipo |
|---|---|---|
| `CLAUDE.md:71` | 1 | árvore ("Definições completas das 14+ personas") |
| `README.md:61` | 1 | árvore |
| `.claude/agents/*.md` (25 arquivos) | 25× | rodapé `- Persona completa: teczi-devflow/personas/{nome}.md` |
| `.claude/agents/leo.md` | +3 | linhas 94, 217, 234, 235 (catálogo `personas-teczilabs.md`) |
| `.claude/skills/teczi-discovery-software/SKILL.md:277` | 1 | ⚠️ usa path divergente `teczilabs/personas/howard.md` |
| `.claude/skills/strategy-session/SKILL.md` | n | refs a personas |
| `CLAUDE_MEMORY.MD` | a verificar | citado no prompt §2.3 |

> Total: **~32+ pontos** de referência a atualizar pós-movimento.

---

## 5. Mapa-alvo dos 5 times (§4 do prompt)

| Time | Pasta | Personas |
|---|---|---|
| 1 — Liderança/Estratégia | `1-lideranca-estrategia/` | leo, marty, albert, nico, peter, voltaire, sun |
| 2 — Tecnologia | `2-tecnologia/` | oscar, nikola, tom, vint, ada, grace, alan, steve |
| 3 — Governança/Seg/QA | `3-governanca-seguranca-qa/` | kevin, linus, bill, denis, howard |
| 4 — Experiência/Cockpit | `4-experiencia-cockpit/` | don, andy |
| 5 — Financeiro/Mercado | `5-financeiro-mercado-ativos/` | mammon, ray, jim, wyck, nassim, barsi, luca, daniel, fred |

**Total mapeado:** 31 slots = 24 ativos movidos + 7 novos. Florence sai (25→24). `carlos.md` não está no mapa dos times (ver gate Q).

---

## 6. Paleta PROPOSTA para os 7 novos (Time 5) — sem colisão

| Persona | Cor proposta | Nome | Ícone | Racional |
|---|---|---|---|---|
| ray | `#0E7490` | Petróleo (Deep Cyan) | Globe | macro/ciclos sistêmicos |
| jim | `#7E22CE` | Violeta Quant | FlaskConical | laboratório/edge |
| wyck | `#B45309` | Bronze | CandlestickChart | tape/fluxo |
| nassim | `#7F1D1D` | Carmim Escuro | ShieldAlert | risco de ruína |
| barsi | `#065F46` | Verde Perene | TreePine | patrimônio longo prazo |
| luca | `#1E3A8A` | Azul Ledger (Navy) | BookOpenCheck | contábil/partidas dobradas |
| daniel | `#3F3F46` | Grafite (Zinc) | Brain | decisão fria/analítica |

> Cada hex foi verificado contra a tabela §3. **2 proximidades a confirmar:** luca `#1E3A8A` (navy) × marty `#1A237E` (deep indigo) — famílias diferentes, hexes distintos; daniel `#3F3F46` (zinc puro) × tom `#334155`/vint `#64748B` (slate azulado) — tom neutro vs azulado. Founder pode vetar.

---

## 7. Pendências que exigem decisão do Founder (gate)

1. **Aprovar o mapa** e autorizar avanço para o ADR de perímetro (§5.1).
2. **Paleta dos 7 novos** (§6) — aprovar ou ajustar.
3. **Convenção de aposentadoria da Florence** (§8 prompt): `_archive/` físico OU `status: aposentada` no frontmatter. Não há convenção estabelecida no repo — prompt manda perguntar.
4. **`carlos.md`**: mover para `/personas/` (onde?) ou manter fora do cast dos 5 times?
5. **Local do ADR de perímetro**: criar `project/adrs/` (repo-wide) — os ADRs existentes ficam em `project/cam-cockpit/adrs/` (escopo cockpit). A reorg é repo-wide, não cockpit-only.
6. **Branch:** repo está em `main`; não existe `dev`. Prompt exige trabalhar em `dev`. Criar `dev` a partir de `main` antes de qualquer commit.

---

## 8. O que NÃO foi tocado (conformidade §10/§12)

- ❌ Nada movido/criado/reescrito.
- ❌ Risk Engine, Constituição, settings.json, REAL_TRADING_ALLOWED — intocados.
- ❌ Nenhum commit. Repo em `main` (sem `dev` ainda).

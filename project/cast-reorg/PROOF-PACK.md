---
template: PROOF-PACK
phase: DEPLOY-READY
demand: cast-reorg-5-times
pmg: G
sec: true
date: 2026-05-28
branch: dev
status: Aguardando-PR-gate-Founder
---

# Proof Pack — Reorganização do Cast em 5 Times (G)

> Demanda G. Proof Pack obrigatório. Branch `dev`. PR para gate do Founder.

## 1. Gates atravessados

| Gate | Status | Evidência |
|---|---|---|
| `⛔ §2` Inspeção aprovada pelo Founder | ✅ | [`INSPECTION-MAP.md`](INSPECTION-MAP.md) + decisões registradas |
| `⛔ §5.1` ADR de perímetro aprovado | ✅ | [`../adrs/ADR-001-perimetro-personas-cam-only.md`](../adrs/ADR-001-perimetro-personas-cam-only.md) (Accepted) |
| `⛔ §11` PR para gate final | ⏳ | este Proof Pack + PR na `dev` |

## 2. Definition of Done (§11 do prompt)

| DoD | Status |
|---|---|
| Mapa de inspeção reportado e aprovado | ✅ |
| ADR de perímetro registrado e aprovado | ✅ (`project/adrs/` — repo-wide) |
| `/personas/` criado na raiz com 5 subpastas + README/mapa | ✅ |
| Personas movidas para o time correto (histórico via `git mv`) | ✅ (7+8+5+2+2) |
| `teczi-devflow/personas/INDEX.md` apontando para `/personas` | ✅ |
| Referências de caminho atualizadas (CLAUDE.md, CLAUDE_MEMORY, READMEs, skills) | ✅ (sweep limpo) |
| 6 agents reescritos de escopo (mammon, sun, peter, fred, kevin, don) | ✅ (agent + persona) |
| 7 personas/agents novos (ray, jim, wyck, nassim, barsi, luca, daniel) | ✅ (persona + agent) |
| Florence aposentada conforme convenção | ✅ (`_archive/` + frontmatter `status: aposentada`; agent removido) |
| 4 skills `cam-*` em esqueleto DRAFT | ✅ |
| 6 skills later declaradas no README | ✅ ([`.claude/skills/README.md`](../../.claude/skills/README.md)) |
| Mammon: trava read-only em persona + agent + `cam-prosperity-scan` | ✅ (3 lugares) |
| Cores/ícones sem colisão | ✅ (verificado: 0 hex duplicado, 0 ícone duplicado) |
| Proof Pack G + PR na `dev` | ⏳ (este doc + PR) |

## 3. Verificações executadas

```
Colisão de cores (31 agents)   → 0 duplicados ✅
Colisão de ícones (31 agents)  → 0 duplicados ✅
Total de agents                → 31 (24 ativos + 7 novos; florence removida) ✅
Refs ao path antigo (residual) → 0 (excl. legado/INDEX/ADR) ✅
Estrutura /personas            → 5 times + _archive + carlos raiz ✅
```

## 4. Inventário final do cast (5 times)

| Time | Personas | #|
|---|---|---|
| 1 — Liderança/Estratégia | leo, marty, albert, nico, peter, voltaire, sun | 7 |
| 2 — Tecnologia | oscar, nikola, tom, vint, ada, grace, alan, steve | 8 |
| 3 — Governança/Seg/QA | kevin, linus, bill, denis, howard | 5 |
| 4 — Experiência/Cockpit | don, andy | 2 |
| 5 — Financeiro/Mercado | mammon, ray, jim, wyck, nassim, barsi, luca, daniel, fred | 9 |
| Founder (cross-time) | carlos | 1 |
| Aposentadas | florence | 1 |

**Total cast:** 31 personas ativas + Carlos + Florence (arquivada).
**Agents `.claude/agents/`:** 31 (sem carlos, sem florence).

## 5. Paleta dos 7 novos (sem colisão — confirmada pelo Founder)

| Persona | Cor | Ícone | Símbolo |
|---|---|---|---|
| ray | `#0E7490` Petróleo | Globe | 🌐 |
| jim | `#7E22CE` Violeta Quant | FlaskConical | 🧪 |
| wyck | `#B45309` Bronze | CandlestickChart | 🕯️ |
| nassim | `#7F1D1D` Carmim Escuro | TrendingDown | 🦢 |
| barsi | `#065F46` Verde Perene | TreePine | 🌳 |
| luca | `#1E3A8A` Azul Ledger | BookOpenCheck | 📒 |
| daniel | `#27272A` Grafite | Brain | 🧠 |
| mammon (mantido) | `#D4AF37` Gold | Star | ⭐ |

> Ajustes do Founder aplicados: daniel `#3F3F46→#27272A`; nassim ícone `ShieldAlert→TrendingDown`.

## 6. Trava read-only do Mammon (Art. 35º) — 3 lugares

1. **Persona:** `personas/5-financeiro-mercado-ativos/mammon.md` — seção "🔒 Trava read-only".
2. **Agent:** `.claude/agents/mammon.md` — seção "🔒 TRAVA READ-ONLY".
3. **Skill:** `.claude/skills/cam-prosperity-scan/SKILL.md` — §4 dedicada à trava.

## 7. Conformidade (§10/§12 — invioláveis)

| Regra | Status |
|---|---|
| Não tocar Risk Engine | ✅ não tocado |
| Não tocar Constituição (exceto ADR) | ✅ só ADR de perímetro (repo-wide, fora da Constituição) |
| Não tocar settings.json / REAL_TRADING_ALLOWED | ✅ não tocados |
| `git mv` preserva histórico | ✅ usado em todos os movimentos |
| Sem commit em `main` | ✅ trabalho em `dev` |
| Sem secrets | ✅ nenhum secret tocado |
| Cores/ícones sem colisão | ✅ verificado |

## 8. Decisões do Founder aplicadas

1. carlos.md → `/personas/carlos.md` raiz (fora dos times); README "O Founder" no topo ✅
2. Florence → `_archive/` + `status: aposentada` + data + motivo; agent removido ✅
3. ADR → `project/adrs/` (repo-wide) ✅
4. Branch `dev` criada de `main` ✅; linha "git init" atualizada no CLAUDE_MEMORY ✅
5. Paleta com ajustes daniel/nassim ✅

## 9. Pendência para o gate do PR

- Revisão de lente dos 18 agents tech/gov (resíduo "Teczilabs Tecnologia") foi aplicada
  nos 6 reescritos; os demais mantêm menção institucional herdada — **revisão de lente
  leve recomendada como follow-up** (não bloqueante; papéis intactos conforme §6).

---
template: ADR
phase: ARCH
status: Accepted
scope: repo-wide
demand: cast-reorg-5-times
sec_gov: true
---

# ADR-001 (repo-wide) — Elevação de `/personas` para raiz CaM-only (perímetro Art. 8º)

> **Data:** 2026-05-28
> **Status:** Accepted — aprovado pelo Founder em 2026-05-28 (gate §5.1)
> **Lead:** Oscar (arquitetura) · **Co-lead:** Kevin (SEC-GOV / threat model)
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/adrs/ADR-001-perimetro-personas-cam-only.md`
> **Numeração:** este é o **ADR-001 de escopo repo-wide** — distinto da série
> `project/cam-cockpit/adrs/ADR-001..013` (escopo cockpit). A reorganização do
> cast é uma decisão do repositório inteiro, não do app cockpit.

---

## 1. Contexto

O cast de personas/agents do CaM vive hoje em `teczi-devflow/personas/`. O
subdiretório `teczi-devflow/` tem **repositório próprio** (`github.com/Teczilabs/teczi-devflow`,
branch `dev`) e é **sincronizável com a Teczilabs** — é o framework de processo
compartilhável entre workspaces.

A reorganização do cast (PROMPT-CLAUDECODE-CAST-CAM-5TIMES) introduz **personas
financeiras CaM-only** (Mammon ampliado, Barsi, Nassim, Jim, Wyck, Ray, Luca,
Daniel) que são **íntimas do Founder e do domínio de mercado do CaM**. Se essas
personas permanecerem dentro de `teczi-devflow/personas/`, elas **vazam para a
Teczilabs** no próximo sync do framework.

Isso colide com o **Art. 8º** da Constituição (perímetro independente do CaM:
sem perímetro de capital, infraestrutura ou identidade compartilhada com a
Teczilabs). O cast financeiro do CaM **não pode** ser material compartilhável.

### 1.1 Gatilho SEC-GOV (Kevin)

Esta demanda ativa **2 dos 9 gatilhos canônicos** do NCC-1701:
- **Mudança em agentes/skills/permissão** (move + reescreve agents, cria skills).
- **Exposição pública / perímetro** (risco de vazamento cross-repo via sync).

Logo, ADR + threat model lógico são obrigatórios (skill `teczi-security-governance`).

---

## 2. Decisão

**Elevar `/personas/` para diretório de primeira classe na raiz do `cam-project`,
como espaço CaM-only**, fora do `teczi-devflow/`.

Concretamente:

1. Criar `/personas/` na raiz com **5 subpastas por time** + `_archive/` + `README.md`.
2. **Mover** (via `git mv`, preservando histórico) as 24 personas ativas para a
   subpasta do time correto; `carlos.md` para `/personas/carlos.md` (raiz, fora
   dos times — Founder é soberano cross-time, D6); Florence para
   `/personas/_archive/florence.md` (aposentada).
3. Em `teczi-devflow/personas/`, deixar **apenas `INDEX.md`** apontando para
   `/personas` — o DevFlow **referencia**, não é mais **dono** do cast.
4. As skills **`cam-*`** (mundo financeiro) nascem em `.claude/skills/` mas são
   **CaM-only por convenção de nome** — `teczi-*` é compartilhável; `cam-*` e
   `/personas` não.

### 2.1 Regra de perímetro (invariante resultante)

| Artefato | Compartilhável c/ Teczi? | Onde vive |
|---|---|---|
| `teczi-*` skills, `teczi-devflow/NCC-1701/` | ✅ Sim (framework) | `teczi-devflow/` (repo próprio) |
| `/personas` (cast CaM) | ❌ **Não** (Art. 8º) | raiz `cam-project` |
| `cam-*` skills (mundo financeiro) | ❌ **Não** | `.claude/skills/cam-*` |
| Constituição, Risk Engine, cockpit | ❌ **Não** | raiz / `apps/` |

---

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Manter cast em `teczi-devflow/personas/` e confiar em `.gitignore` seletivo no sync | Frágil: depende de disciplina manual; um sync errado vaza Mammon/Barsi para a Teczi. Viola Art. 8º por design fraco. |
| 2 | Duplicar o cast (cópia CaM + cópia Teczi) | Duplicação = divergência garantida; dois donos do mesmo conceito. Anti-padrão "estado real vence intenção". |
| 3 | Criar repo git separado só para `/personas` | Overengineering para um cockpit pessoal; fragmenta o monorepo sem ganho real. |
| 4 | **Elevar `/personas` para raiz CaM-only + INDEX.md no DevFlow** ✅ | **Escolhida.** Separação física clara: compartilhável vs CaM-only. Sync do DevFlow nunca toca `/personas`. Um único dono. |

---

## 4. Consequências

### Positivas
- **Art. 8º garantido por estrutura, não por disciplina** — o sync do `teczi-devflow/` fisicamente não alcança `/personas`.
- Um único dono do cast (`/personas`); DevFlow apenas referencia via `INDEX.md`.
- Organização por 5 times fica explícita e navegável.
- `cam-*` skills + `/personas` formam o perímetro CaM-only coeso.

### Negativas
- **~32+ referências** ao caminho antigo precisam ser atualizadas (CLAUDE.md, README, CLAUDE_MEMORY.MD, 25 rodapés de agents, leo.md catálogo, 2 SKILLs). Mitigação: feito em lote, com checklist na demanda.
- `teczi-discovery-software/SKILL.md` usa path divergente `teczilabs/personas/` — precisa correção também.

### Neutras
- Numeração de ADR repo-wide inicia em `ADR-001` (paralela à série cockpit). Documentado no cabeçalho para evitar confusão.

---

## 5. Custo de reversão

**Médio.** Reversão exige `git mv` de volta + restaurar referências. Como tudo é
versionado e os movimentos preservam histórico (`git mv`), reverter é mecânico
mas trabalhoso (32+ refs). Nenhum dado operacional é perdido.

---

## 6. Threat Model lógico (Kevin — SEC-GOV)

| Ameaça | Vetor | Mitigação nesta ADR |
|---|---|---|
| **Vazamento do cast financeiro para a Teczi** | Sync do `teczi-devflow/` arrasta `personas/` | `/personas` sai fisicamente do `teczi-devflow/`; sync nunca o alcança |
| **Divergência de identidade** (2 donos) | Cópia duplicada | Dono único `/personas` + `INDEX.md` read-only no DevFlow |
| **Quebra de referência silenciosa** | Path antigo em docs/skills após movimento | Checklist de 32+ refs + grep de verificação pós-movimento (DoD) |
| **Perda de histórico** | `mv` em vez de `git mv` | Mandato `git mv` (repo já versionado) |
| **Erosão de perímetro futura** | Nova persona financeira criada por engano em `teczi-devflow/` | Regra §2.1 + convenção de nome `cam-*` documentada no README do cast |

**Não há** toque em Risk Engine, kill switch, journal, provisão fiscal,
`REAL_TRADING_ALLOWED`, settings ou Constituição (exceto este ADR). Superfície
sensível: **organização de agents/skills** — sem superfície de execução de ordem.

---

## 7. Conformidade constitucional

| Artigo | Conformidade |
|---|---|
| **Art. 8º** (perímetro independente) | ✅ É o motivo da decisão — reforçado por estrutura física |
| **Art. 35º** (IA read-only) | ✅ Mammon nasce com trava read-only; não afetado por esta ADR estrutural |
| **Art. 36º** (hierarquia) | ✅ Cast serve à hierarquia; nenhuma persona ganha autoridade de execução |
| **Art. 43º** (Constituição soberana) | ✅ ADR não altera Constituição; apenas organiza o cast que a serve |

---

## 8. Referências

- Demanda: [`/PROMPT-CLAUDECODE-CAST-CAM-5TIMES.md`](../../PROMPT-CLAUDECODE-CAST-CAM-5TIMES.md)
- Mapa de inspeção: [`../cast-reorg/INSPECTION-MAP.md`](../cast-reorg/INSPECTION-MAP.md)
- Constituição: [`/CONSTITUICAO.md`](../../CONSTITUICAO.md) — Arts. 8º, 35º, 36º, 43º
- Governança: [`/teczi-devflow/NCC-1701/governance/SEC-GOV.md`](../../teczi-devflow/NCC-1701/governance/SEC-GOV.md)
- ADRs cockpit (série distinta): `/project/cam-cockpit/adrs/ADR-001..013`

---

## 9. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior aprova o ADR-001 repo-wide:

    Elevar /personas para a raiz como diretório CaM-only (Art. 8º),
    com INDEX.md no teczi-devflow apontando de volta, e convenção de
    nome cam-* para skills CaM-only.

    Reconhece que:
    a) O sync do teczi-devflow nunca mais alcança o cast financeiro.
    b) ~32 referências serão atualizadas em lote na execução.
    c) git mv preserva histórico; reversão é médio-custo.
    d) Nada toca Risk Engine / Constituição / settings.

    Após aprovação → executo movimentos §5.2-5.5 + reescritas §6-7.
```

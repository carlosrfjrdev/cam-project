# CLAUDE.md — teczi-devflow (no CaM-project)

> Framework de produção de software AI-driven embarcado no CaM Project. Subdiretório de **processo**, não de código de produto.
>
> Idioma padrão: **português**.

**Versão ativa neste projeto:** **NCC-1701 (v6.0)** — 9 fases · 2 estados · 2 governanças
**Substitui (conceitualmente):** NX-50A — que continua válido em outros workspaces Teczilabs, mas não é usado aqui

## Onde encontrar contexto

| Tema | Localização |
|---|---|
| Constituição do CaM (lei suprema) | `../CONSTITUICAO.md` |
| CLAUDE.md raiz do projeto | `../CLAUDE.md` |
| Processo completo NCC-1701 | `NCC-1701/process.md` |
| Fases (PDOC → SDOC) | `NCC-1701/phases/` |
| Estados (BUG, OPS) | `NCC-1701/states/` |
| Governanças (SEC-GOV, CHANGE) | `NCC-1701/governance/` |
| Templates de artefatos | `NCC-1701/templates/` |
| Drafts conceituais de skills | `NCC-1701/skills/` |
| Personas completas | `personas/` |
| Skills operacionais (Claude) | `../.claude/skills/teczi-*` |
| Agents (Claude) | `../.claude/agents/` |

## Distinção importante

- `NCC-1701/skills/` — **drafts conceituais** das 11 skills DevFlow (contrato YAML futuro, anti-padrões, referências). Não executáveis.
- `../.claude/skills/teczi-*/SKILL.md` — **skills operacionais** que o Claude Code reconhece via `Skill` tool. Foram portadas dos drafts conceituais e adaptadas ao contexto CaM (referências à Constituição, gatilhos adicionais para Risk Engine/kill switch/journal).

## Regras críticas (válidas neste subdiretório)

- **Não criar código-fonte aqui** — repositório de processo. Código vai em `../apps/{codinome}/`.
- **Artefatos por demanda** vão em `../project/{codinome}/demands/{id}/`, nunca em `../docs/` dos aplicativos.
- **Templates em kebab-case** em `NCC-1701/templates/`.
- **Escopo de trabalho do agente:** Bloco por Bloco (do PLAN), proporcional ao P/M/G.
- **Founder-only nos gates** — sem exceção nesta versão (NCC-1701 §7).
- **Sem estimativas em horas/dias/semanas** em qualquer artefato (proibição explícita do Founder).

## Constituição — DESCOMISSIONADA (2026-06-03)

> A Constituição do CaM foi **revogada** com a virada do projeto para produto comercial.
> NCC-1701 continua sendo o **método de engenharia**. Não há mais "lei suprema" acima
> dele. Os gatilhos SEC-GOV *constitucionais* (Risk Engine, kill switch, journal, fiscal,
> autoridade da IA) deixaram de ser obrigatórios — podem virar requisitos de **produto**
> quando fizer sentido comercial, mas como decisão de engenharia, não dogma. Ver
> `../project/tcam/` e `../CLAUDE.md`.

## Git

O `teczi-devflow/` tradicionalmente vive como repositório próprio em `github.com/Teczilabs/teczi-devflow` (branch `dev`). Dentro do CaM-project ele aparece como subdiretório embarcado de referência — quando houver atualização canônica, sincronizar do repositório upstream.

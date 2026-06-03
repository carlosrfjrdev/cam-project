# CONSTITUTION-DECOMMISSION — Plano de Descomissionamento da Constituição

> **Status:** PROPOSTA (planejamento — não executada). Aguarda aprovação explícita do Founder (⚖️ FOUNDER #5 do PIVOT).
> **Autor:** Leo (Chief Orchestrator)
> **Data:** 2026-06-03
> **Pré-condição:** checkpoint do estado antigo já preservado em branch `the_old_cam` @ `82fb17a`.

---

## 0. Princípio

A Constituição era a **disciplina pessoal de trader** do Carlos. Com a virada para produto
(TCaM), o Carlos **deixa de operar** — a Constituição perde objeto e **morre inteira como
autoridade**. Este documento lista, item por item, **o que remover, o que neutralizar e o que
reaproveitar como feature de produto**.

**Regra de ouro:** *mate a lei, preserve o mecanismo.* (Voltaire — o Risk Engine é o moat.)

**Nada neste documento é executado até o Founder aprovar.** A execução será uma demanda
DevFlow própria (provável estado BUG/CODE com SEC-GOV, dado que toca Risk Engine, kill switch
e autoridade da IA — gatilhos do `CLAUDE.md`).

---

## 1. Documento soberano — `CONSTITUICAO.md`

| Ação | Detalhe |
|---|---|
| **ARQUIVAR** (não deletar) | Mover `CONSTITUICAO.md` → `archive/CONSTITUICAO-v1.1-DECOMMISSIONED.md` com cabeçalho "DESCOMISSIONADA em 2026-06-XX pela virada TCaM. Mantida como memória histórica. Sem efeito normativo." |
| **Justificativa** | É memória de anos de aprendizado (Voltaire). Apagar destrói história; arquivar preserva sem dar autoridade. |
| **Artigos relacionados (`/project/cam-constitution/`, emendas, POV)** | Mover para `archive/cam-constitution-legacy/`. Sem efeito normativo. |

---

## 2. `CLAUDE.md` (raiz) — remover hierarquia constitucional e travas

Blocos a **remover/reescrever** (hoje o `CLAUDE.md` é fortemente constitucional):

| Bloco atual | Ação |
|---|---|
| "Hierarquia constitucional — LEIA antes de qualquer ação" (incl. tabela Arts. 11/15/18/25/26/31/35/36/6) | **REMOVER** integralmente |
| `Constituição > Risk Engine > Estratégia > IA > Operador` | **REMOVER** |
| "Fase 0 — Construção (CONSTITUICAO.md Anexo II)" e referências de fase constitucional | **REESCREVER** para "Fase 1 — Virada TCaM (ver PIVOT-TCaM-STRATEGY.md)" |
| "Art. 6º: preserve mais capital" como regra de desempate | **REMOVER** |
| Seção "Gatilhos automáticos para SEC-GOV no CaM" citando Arts. 15/18/25/26/34-36 | **REESCREVER**: manter gatilho SEC-GOV para Risk/kill-switch/credenciais como **boa prática de produto**, sem citar artigos |
| Identidade "CaM — The Carlos Alternative Money / não comercial / operador único" | **REESCREVER** para "TCaM — Teczi Cockpit Assets Manager / produto comercial multi-usuário (em construção)" |
| Checklist "Leia CONSTITUICAO.md (Parte I, IV, IX, X)" | **REMOVER** o item 1; renumerar |
| "Quando em dúvida: preserve mais capital (Art. 6º)" | **REMOVER** |

**Mantém-se** no `CLAUDE.md`: stack oficial, estrutura `/apps` × `/project`, DevFlow NCC-1701,
personas, política de documentação, git posture, proibições universais de engenharia (commit em
main, secrets, rebase/force push — **essas não são constitucionais, são higiene de engenharia**).

> A reescrita completa do `CLAUDE.md` será proposta como **diff revisável** na execução da Fase 1,
> não aqui.

---

## 3. Memory do projeto (`~/.claude/.../memory/`)

| Arquivo | Ação |
|---|---|
| `MEMORY.md` | **REESCREVER** índice: remover linha "artigos não-negociáveis"; trocar visão CaM-pessoal por TCaM-produto |
| `project-cam-vision.md` | **REESCREVER** — visão de produto TCaM, não cockpit pessoal |
| `feedback-work-rules.md` | **REVISAR** — manter proibições de engenharia (P/M/G, no horas/dias, no commit main); remover qualquer trava constitucional |
| `project-cam-open-decisions.md` | **REESCREVER** — substituir "OPs de Fase 1 trader (broker/capital/estratégia)" pelas ⚖️ FOUNDER #1-6 do PIVOT |
| `project-cam-code-state.md` | **ATUALIZAR** — refletir os 8 módulos Assets* |
| `project-cam-stack.md` | **MANTER** (stack não muda) — remover só o enquadramento "não comercial" |
| `project-cam-inspetor-spec.md`, `project-cam-leadlag.md` | **MANTER** (são features reais = Assets Inspector / Assets Labs) |
| `feedback-commit-push.md`, `reference-devflow.md`, `user-carlos.md` | **MANTER** (processo/perfil, não constitucional) |

> Memory é do harness Claude Code — atualização via edição dos `.md` (ou skill `update-config`
> se envolver settings). Proposta de diffs na execução.

---

## 4. Código — feature `constitution` e Risk Engine

### 4.1 Feature `constitution` (backend + frontend)

| Item | Ação |
|---|---|
| `backend/cam/features/constitution/` (domain, routes, service, repository, schemas, tests) | **REMOVER do produto** (mantém histórico git). Serve a um documento que deixa de existir. Alternativa: reaproveitar como "Termos/Política do cliente" — **decisão de produto** (ver ⚖️ FOUNDER #4) |
| `frontend/src/features/constitution/ConstitutionPage.tsx` | **REMOVER da nav e do router** |
| Item de nav "Constituição" (`nav.tsx` linha 61) | **REMOVER** |
| Migração Alembic relacionada | **MANTER** (histórico imutável; não criar down-migration destrutiva sem necessidade) |

### 4.2 Risk Engine → `Assets RiskManager` (NÃO deletar — converter)

| Item | Ação |
|---|---|
| `_shared/risk/engine.py` e `validators/` | **MANTER o motor.** Remover linguagem constitucional dos docstrings ("Art. 15º autoridade máxima", "Art. 11º INTOCÁVEL", "a ordem é lei") → reescrever como "regras configuráveis do RiskManager" |
| Limites constantes (2 WIN/2 WDO, 3%/7%/15%) | **PARAMETRIZAR** — viram config (futuramente por-tenant), não constantes de lei. Mantêm-se como **defaults sensatos** |
| `_shared/autonomy/matrix.py` | **MANTER** como política de produto. Remover condicionantes constitucionais ("assinatura simbólica do Founder", "cooldown 30 dias", `REAL_TRADING_ALLOWED` como lei) → viram política configurável |
| `kill_switch` (backend + `KillSwitchButton.tsx`) | **MANTER** como **feature de segurança vendável** (não dever moral). Renomear narrativa, não código |
| `RiskEngineStatusBanner.tsx`, `RiskConsolePage.tsx` | **MANTER** como UI do Assets RiskManager |

### 4.3 `REAL_TRADING_ALLOWED`

| Item | Ação |
|---|---|
| Flag em backend/`useEnvironment.ts` | **MANTER como flag de ambiente/produto.** Já tratada defensivamente. Muda só a **narrativa**: não é mais "trava constitucional", é "guardrail de ambiente" (default seguro: DEMO, nunca REAL silencioso) |

---

## 5. Personas / agents — "guardiões constitucionais"

> O Founder citou Kevin-enforce, Daniel etc. Esclarecimento: **as personas são processo de
> engenharia, não a Constituição** — continuam válidas. O que muda é o **mandato** de algumas.

| Persona | Era | Vira |
|---|---|---|
| **Kevin** (SEC-GOV) | Enforçador de "Risk Engine constitucional", autoridade da IA (Arts. 34-36) | **Segurança de PRODUTO**: compliance de SaaS, fronteira regulatória, segregação multi-tenant, secrets. **Ganha relevância**, não perde |
| **Daniel** (decision post-mortem) | RCA do erro pessoal do trader Carlos | **Candidato a aposentadoria/standby** — era coaching pessoal. Não há "operador" para fazer RCA. Reavaliar se vira analytics de produto para o cliente |
| **Linus** (QA) | Validava "Risk Engine, kill switch, provisão fiscal" como obrigação constitucional | **MANTÉM** — QA de produto. Valida RiskManager como feature, não como lei |
| **Time 5 financeiro** (mammon, ray, jim, wyck, nassim, barsi, luca, fred) | Conselheiros do **trader Carlos** (read-only Art. 35º) | **Reavaliar em bloco** — eram para o Carlos operar. Como ele não opera, viram **candidatos a standby** OU **base de features de produto** (ex.: Mammon→scanner de oportunidade vendável). **Decisão de produto futura** |
| Personas DevFlow base (Leo, Marty, Albert, Oscar, Nico, Nikola, Bill, Steve, Tom, Vint, Denis, Howard) | Engenharia | **MANTÊM intactas** |

> **Nenhuma persona é deletada na Fase 1.** A reavaliação do Time 5 e Daniel é **decisão de
> produto** posterior (não trava o app rodar). As skills `cam-*` (carteira-hard, fiscal-closing,
> session-ritual, risk-modeling, etc.) que ancoram em artigos constitucionais devem ter as
> **âncoras constitucionais removidas** quando/se forem reaproveitadas — ou marcadas DEPRECATED.

---

## 6. Skills `cam-*` ancoradas na Constituição

Estas skills citam artigos como âncora ("Ancoragem Arts. Xº"). Ação na execução:

| Skill | Ação |
|---|---|
| `cam-risk-modeling`, `cam-prosperity-scan` (trava Art. 35º), `cam-strategy-lab`, `cam-fiscal-closing`, `cam-session-ritual`, `cam-market-regime`, `cam-flow-analysis`, `cam-market-data-intake`, `cam-carteira-hard-review`, `cam-decision-postmortem` | **MARCAR DEPRECATED** (Fase 1) — todas pressupõem o trader Carlos operando. Reavaliar caso-a-caso se viram features de produto (Fase 2+). Remover âncoras constitucionais ao reaproveitar |

> Skills `teczi-*` e `strategy-session` **mantêm** (processo de engenharia/estratégia).

---

## 7. `.claude/settings.json`

| Item | Ação |
|---|---|
| `bypassPermissions`, `skipDangerousModePermissionPrompt` | **MANTER** (config de dev, não constitucional). Reavaliar hardening na Fase 3 (SaaS) |

Nenhuma trava constitucional vive em settings hoje — nada a remover aqui na Fase 1.

---

## 8. Ordem de execução sugerida (quando o Founder aprovar)

1. **Arquivar** `CONSTITUICAO.md` + `/project/cam-constitution/` → `archive/`.
2. **Reescrever** `CLAUDE.md` (raiz) — remover hierarquia/artigos, rebrand TCaM. *[diff revisável]*
3. **Atualizar** memory (`MEMORY.md`, vision, open-decisions, work-rules). *[diff revisável]*
4. **Converter** Risk Engine: limpar docstrings constitucionais, parametrizar limites. *[SEC-GOV/Kevin]*
5. **Remover** feature `constitution` (backend+frontend+nav). *[mantém migração no histórico]*
6. **Neutralizar** autonomy matrix (remover condicionantes constitucionais).
7. **Marcar DEPRECATED** skills `cam-*` ancoradas na Constituição.
8. **Recompor** navegação nos 8 módulos Assets* (ver MAP-MODULES-TCaM.md).
9. **App roda** end-to-end → **Gate Founder**.

> Passos 4-5 tocam Risk Engine/kill switch → **SEC-GOV (Kevin) obrigatório** na execução,
> agora como segurança de produto (não enforcement constitucional).

---

## 9. Checklist do que NÃO fazer (proteções)

- ❌ NÃO deletar `CONSTITUICAO.md` — **arquivar**.
- ❌ NÃO deletar o motor do Risk Engine — **converter** em feature.
- ❌ NÃO criar down-migrations destrutivas no Alembic — manter histórico.
- ❌ NÃO deletar personas/agents na Fase 1 — **standby/reavaliar** depois.
- ❌ NÃO renomear pastas `apps/cam-cockpit` agora sem decisão ⚖️ FOUNDER #3 (churn de imports).
- ❌ NÃO executar nada deste plano antes da aprovação do Founder.

---

*Documento de planejamento. Nenhuma alteração executada. Aguarda ⚖️ FOUNDER #5.*

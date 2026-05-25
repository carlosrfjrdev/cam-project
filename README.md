# CaM — The Carlos Alternative Money

> **Cockpit pessoal de operação, disciplina e governança.**
> Projeto pessoal, local, não comercial — operador único: Carlos Rodrigues Ferreira Junior.
> **Fase atual:** Fase 0 — Construção (Anexo II da Constituição).

---

## O que é o CaM

O CaM não existe para enriquecer rapidamente. Existe para **impedir decisões impulsivas, proteger capital, controlar risco, registrar operações, validar estratégias e converter ganhos táticos em patrimônio de longo prazo** (Art. 1º).

> *"O CaM não existe para provar que o operador está certo. O CaM existe para impedir que o operador quebre quando estiver convicto demais."*
> — Art. 4º, Regra de Ouro

O CaM **não é**: produto financeiro, consultoria, robô de promessa de lucro.
O CaM **é**: um sistema vivo que vincula o operador presente ao operador passado e protege o operador futuro.

---

## Hierarquia constitucional

```
Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual
```

A [`CONSTITUICAO.md`](./CONSTITUICAO.md) é **soberana** sobre o cockpit, sobre a estratégia, sobre a IA e sobre decisões manuais em estado emocional. Leitura obrigatória antes de qualquer trabalho no projeto.

**Pontos não-negociáveis:**

- **Art. 11º** — Máximo absoluto: 2 contratos WIN / 2 contratos WDO. Limite intocável por qualquer motivo.
- **Art. 15º** — Risk Engine bloqueia? CaM não opera. Sem exceções.
- **Art. 18º** — Kill switch obrigatório, acionável sem justificar oportunidade perdida.
- **Art. 25º** — Toda UI exibe resultado **LÍQUIDO de imposto provisionado**, nunca bruto.
- **Art. 35º** — IA não envia ordem, não desabilita/parametriza Risk Engine, não justifica exceção constitucional.
- **Art. 6º** — Em conflito entre regras, prevalece a que preserva mais capital.

---

## Estrutura do repositório

```
CaM-project/
├── CONSTITUICAO.md             ← Lei suprema do CaM (v1.0 consolidada)
├── CLAUDE.md                   ← Contexto operacional para Claude Code
├── README.md                   ← Este arquivo
│
├── apps/                       ← Aplicativos do cockpit (Risk Engine, Journal, Backtest, UI, ...)
│   └── README.md
│
├── project/                    ← Artefatos DevFlow por demanda (intenção viva)
│   └── README.md
│
├── archive/                    ← Memória física (.txt originais da Constituição)
│   └── README.md
│
├── teczi-devflow/              ← Framework de processo (NCC-1701) que rege a construção
│   ├── NCC-1701/               ← Versão ativa: 9 fases / 2 estados / 2 governanças
│   └── personas/
│
└── .claude/                    ← Configuração Claude Code (agents + skills)
    ├── agents/                 ← 14 personas NCC-1701 + cast estendido
    ├── skills/                 ← Skills operacionais portadas do DevFlow
    └── settings*.json
```

**Princípio de separação `apps` vs `project`** (NCC-1701 §9.3):

| Pasta | Significado | Quando consultar |
|---|---|---|
| [`/apps`](./apps/) | **Estado real** — código construído | "O que de fato existe e roda" |
| [`/project`](./project/) | **Intenção viva** — SCOPE, SPEC, PLAN, ADRs, PROOF-PACKs | "O que está sendo decidido e construído" |

Quando ambos divergirem, **estado real vence intenção** (NCC-1701 §2, regra 7).

---

## Como construir no CaM — Teczi DevFlow NCC-1701

Toda construção segue o framework [`teczi-devflow/NCC-1701/`](./teczi-devflow/NCC-1701/).

**9 fases sequenciais (com proporcionalidade P/M/G):**

```
PDOC → DISC → ARCH → SPEC → PLAN → CODE → QA → DEPLOY → SDOC
```

**2 estados não numerados:** BUG (fast-track, Bill) · OPS (contínuo, Vint)
**2 governanças transversais:** SEC-GOV (por gatilho, Kevin) · CHANGE (dentro de DEPLOY, Tom)

**Gates Founder-only:** nenhum estado avança sem aprovação explícita de Carlos.

Processo completo: [`teczi-devflow/NCC-1701/process.md`](./teczi-devflow/NCC-1701/process.md).

### Skills operacionais Claude (uma por fase/estado/governança)

Disponíveis em `.claude/skills/`, invocáveis pelo tool `Skill`:

| Skill | Fase/Estado/Gov | Lead |
|---|---|---|
| `teczi-project-creation` | PDOC | Leo + Denis |
| `teczi-project-discovery` | DISC | Marty |
| `teczi-architecture-decision` | ARCH | Oscar (+Vint) |
| `teczi-demand-specification` | SPEC | Albert (+Kevin) |
| `teczi-code-planning` | PLAN | Nico (loop com Albert) |
| `teczi-code-execution` | CODE | Nikola (+Linus/Kevin intrabloco) |
| `teczi-quality-assurance` | QA | Linus (+Kevin em QA-SEC) |
| `teczi-deploy` | DEPLOY | Steve + Tom (Vint executor) |
| `teczi-software-documentation` | SDOC | Denis (+Howard em DRIFT) |
| `teczi-bug-fix` | Estado BUG | Bill |
| `teczi-security-governance` | Governança SEC-GOV | Kevin |

### Personas (`.claude/agents/`)

14 personas ativas no NCC-1701 — invocáveis via `Agent` tool:

`leo` (orquestrador) · `marty` · `albert` · `oscar` · `nico` · `nikola` · `linus` · `bill` · `steve` · `tom` · `vint` · `kevin` · `denis` · `howard`

Cast estendido (chamado por Leo quando necessário): `sun`, `voltaire`, `mammon`, `grace`, `alan`, `andy`, `ada`, `peter`, `florence`, `fred`, `don`.

---

## Stack vigente

**Documento canônico:** [`project/STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md)

A stack do CaM **revoga** os Combos A/B/C do catálogo Teczilabs (Java/Spring, Firebase, Next.js, MongoDB) — esses combos foram inferidos para produtos comerciais e não se aplicam ao CaM.

**Resumo:** Profit/Nelogica (executor) · Python 3.12 + FastAPI (cockpit) · React 19 + Vite + MUI (UI) · **PostgreSQL 16 + TimescaleDB desde Fase 0** (tick storage + continuous aggregates) · DuckDB (research auxiliar em CSV/Parquet) · Telegram (alertas) · Ollama/Anthropic (IA auditora).

**SO produção:** Windows 11 (Profit Windows-only). **SO desenvolvimento:** Linux.

Faseamento da integração com Profit, ADRs, riscos e custos detalhados: ver [`STACK-CAM-OFICIAL.md`](./project/STACK-CAM-OFICIAL.md).

---

## Critérios de saída da Fase 0

(Anexo II da Constituição)

- [ ] Cockpit funcional end-to-end
- [ ] Risk Engine com cobertura de testes **≥ 80%**
- [ ] Kill switch validado em teste real
- [ ] Pipeline de backtest funcional
- [ ] Pipeline de paper trading funcional

Cumpridos → Fase 1 (Paper Trading, 30 dias úteis ou 100 operações).

---

## Para futuros instâncias de Claude Code

Leia [`CLAUDE.md`](./CLAUDE.md) na raiz antes de qualquer ação. Idioma padrão de resposta: **português**.

---

## Relação com a Teczilabs

O CaM nasce dentro do contexto Teczilabs como projeto pessoal do Founder, mas é uma **estrutura separada** — não usa receita, capital, infraestrutura ou perímetro da Teczilabs (Art. 8º). A relação com a Teczilabs é metodológica: o CaM é o **primeiro cliente real do Teczi DevFlow NCC-1701**, em modo dogfood.

---

> *Sobreviver. Preservar capital. Obedecer regras. Registrar tudo. Aprender. Melhorar o sistema. Gerar fluxo. Converter fluxo em patrimônio. Escalar somente com evidência.*
> — Art. 3º, Prioridade Absoluta

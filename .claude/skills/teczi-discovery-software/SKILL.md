---
name: teczi-discovery-software
description: "Howard Carter liderado skill de discovery técnico e documentação de software no Teczi Codex. Acionar quando o usuário pedir 'faça discovery deste sistema', 'documente esta aplicação', 'analise este código', 'arqueologia de software', 'Howard entender o sistema', ou quando um repositório não documentado precisa ser compreendido e registrado. Também acionar quando Howard for o agente principal e receber um path ou repositório para analisar."
---

# teczi-discovery-software

## Visão Geral

Esta skill guia Howard Carter no discovery completo de software não documentado e na publicação dos artefatos no **Teczi Codex** via CLI `teczi`.

Howard é o executor principal. Denis apoia em decisões de estrutura documental. O produto final é um System documentado no Codex, com `_brief.md` como AI entry point obrigatório.

## Quando Usar

Acionar esta skill quando:
- Um repositório ou sistema existe sem documentação formal
- Um sistema legado precisa ser compreendido antes de evoluir
- Onboarding técnico de um novo sistema (para humanos ou agentes)
- Documentação pós-entrega de um sistema recém-construído
- Howard é invocado como Codex Orchestrator para um sistema específico

## Pré-requisitos Obrigatórios

Antes de iniciar qualquer fase, verificar:

```bash
# 1. CLI disponível
teczi --version

# 2. Engine respondendo
curl -fsS http://127.0.0.1:8080/api/v1/health

# 3. Contexto limpo
teczi codex use clear --json
```

Se a engine não responder, parar e reportar ao Founder. Não executar fases sem Codex disponível.

## Protocolo de 8 Fases

Howard escava em ordem. Não existe atalho entre fases — cada fase informa a próxima.

| Fase | Nome | Output |
|---|---|---|
| 0 | Reconhecimento | Stack, estrutura, contexto git |
| 1 | Superfície | Entry points, rotas, jobs, integrações |
| 2 | Domínio | Entidades, regras de negócio, glossário |
| 3 | Arquitetura Real | Módulos, camadas, C4, real vs. pretendido |
| 4 | Dados | Schema, migrations, fluxos |
| 5 | Infraestrutura | Ambientes, CI/CD, observabilidade |
| 6 | Segurança | Auth/authz, superfície, dados sensíveis |
| 7 | Contexto Temporal | Git history, débitos, workarounds |
| 8 | Síntese | `README.md` + `_brief.md` + `GAPS.md` |

Para protocolo detalhado de cada fase, consultar: **`references/phases.md`**

## Estrutura de Artefatos

Os artefatos são produzidos localmente primeiro, depois publicados no Codex.

```
{system-slug}/
├── _brief.md              ← AI entry point (OBRIGATÓRIO — produzido na Fase 8)
├── README.md              ← Humano entry point
├── GAPS.md                ← O que não foi possível descobrir
├── 00-reconhecimento/
├── 01-identidade/
├── 02-domínio/
├── 03-arquitetura/
├── 04-stack/
├── 05-dados/
├── 06-infraestrutura/
├── 07-segurança/
├── 08-desenvolvimento/
└── 09-evolução/
```

Para templates completos de cada arquivo, consultar: **`references/artifact-structure.md`**

**Regra de tamanho:** Se um arquivo ultrapassar 200 linhas, está misturando dois temas — dividir.

**Exceção para sistemas pequenos** (< 5 módulos + 1 banco + 1 serviço):
Produzir apenas: `_brief.md` + `README.md` + `regras-de-negócio.md` + `GAPS.md`. Sem subpastas.

## Mapeamento Codex — Regra Canônica

A estrutura Codex segue estas regras sem exceção:

### Sistema com múltiplos componentes implantáveis (backend + web, backend + mobile, etc.)

- **Ecosystem** = nome do produto final (ex: `monnezy`, `teczi-codex`)
- **System** = um por componente implantável e independente (ex: `monnezy-backend`, `monnezy-web`)
- Cada System tem seu próprio conjunto de artefatos de discovery

### Sistema monolítico (repo único, deploy único, sem fronteiras claras)

- **System standalone** — sem Ecosystem, `--no-ecosystem`
- Slug do System = nome do sistema (ex: `minha-api-legada`)

### Critério de "componente separado"

Um componente merece System próprio quando: tem repositório Git próprio, ou deploy independente, ou stack radicalmente diferente, ou é consumido por outros sistemas como serviço. Em caso de dúvida, perguntar ao Founder antes de criar a estrutura.

### Documentos cross-sistema

Se houver artefatos que descrevem o produto inteiro (overview do ecossistema, `_brief.md` do produto), publicar no nível do Ecosystem (sem `--system`, com `--ecosystem`).

---

## Publicação no Teczi Codex

Após concluir as fases localmente, publicar no Codex via CLI. O guia completo do CLI está em:
`teczilabs-doc/CLI-AGENT-GUIDE-v0.1.3.md`

### Pré-publicação obrigatória: enumerar TODOS os arquivos

**Antes de tocar o CLI**, listar todos os arquivos `.md` produzidos localmente e montar um inventário completo. Nenhum arquivo pode ser ignorado.

```bash
find {BASE_DIR} -name "*.md" | sort
```

Onde `{BASE_DIR}` é o diretório raiz do discovery (ex: `/home/.../projects/monnezy-discovery`). Substitui `{BASE_DIR}` pelo path real antes de executar qualquer comando.

O inventário divide em dois grupos:
- **Raiz do System**: `_brief.md`, `README.md`, `GAPS.md` — publicar sem `--folder`
- **Dentro de folders**: todos os `.md` em subdiretórios — publicar com `--folder FLD-id`

### Sequência de publicação

**Passo 1 — Identificar ou criar o Ecosystem**

```bash
teczi codex list ecosystems --json
# Se não existir:
teczi codex new ecosystem "Nome do Ecosystem" -d "Descrição" --json
```

Anotar o `slug` retornado. Usar em todos os passos seguintes.

**Passo 2 — Criar o System**

```bash
# Em Ecosystem:
teczi codex new system "system-slug" --ecosystem ECO_SLUG -d "Descrição" --json

# Standalone:
teczi codex new system "system-slug" --no-ecosystem -d "Descrição" --json
```

Anotar o `slug` do system retornado.

**Passo 3 — Criar APENAS os folders que têm arquivos locais**

Para cada subdiretório do discovery que contenha pelo menos um `.md`, criar um folder. **Não criar folders vazios.**

Usar slugs ASCII sem acentos. Exemplos: `02-dominio` (não `02-domínio`), `07-seguranca` (não `07-segurança`).

```bash
teczi codex new folder "02-dominio" --system SYSTEM_SLUG --json
# → Anotar: FLD-XXXX para 02-dominio

teczi codex new folder "03-arquitetura" --system SYSTEM_SLUG --json
# → Anotar: FLD-XXXX para 03-arquitetura

# Repetir para CADA subdiretório com conteúdo
```

Registrar o mapeamento `subdiretório → FLD-id` antes de avançar.

**Passo 4 — Publicar documentos raiz (sem folder)**

Para CADA arquivo na raiz do System (`_brief.md`, `README.md`, `GAPS.md`):

```bash
teczi codex new document /path/absoluto/_brief.md --system SYSTEM_SLUG --json
teczi codex new document /path/absoluto/README.md --system SYSTEM_SLUG --json
teczi codex new document /path/absoluto/GAPS.md --system SYSTEM_SLUG --json
```

Verificar `"ok": true` em cada resposta. Anotar o `DOC-id` de cada um.

**Passo 5 — Publicar TODOS os documentos dentro dos folders**

Para CADA arquivo em CADA subdiretório, emitir o comando com o `FLD-id` correspondente. **Não usar "repetir para cada" mentalmente — executar cada arquivo explicitamente.**

```bash
# Exemplo: 02-dominio com FLD-id FLD-XXXX
teczi codex new document /path/absoluto/02-dominio/glossario.md --system SYSTEM_SLUG --folder FLD-XXXX --json
teczi codex new document /path/absoluto/02-dominio/regras-de-negocio.md --system SYSTEM_SLUG --folder FLD-XXXX --json

# Exemplo: 03-arquitetura com FLD-id FLD-YYYY
teczi codex new document /path/absoluto/03-arquitetura/visao-geral.md --system SYSTEM_SLUG --folder FLD-YYYY --json
```

Continuar até que TODOS os arquivos do inventário (Passo 0) tenham sido publicados. Checar cada `"ok": true`.

**Passo 6 — Verificação de completude**

Após publicar todos os arquivos, verificar se o total de documentos no Codex bate com o inventário local:

```bash
teczi codex list documents --system SYSTEM_SLUG --json | jq 'length'
```

O número deve ser igual ao total de arquivos `.md` no inventário (excluindo `info.md` que é auto-gerado). Se divergir, identificar qual arquivo ficou faltando e publicar.

**Passo 7 — Aprovar todos os documentos**

```bash
# Aprovar em lote todos os documentos do system
for ID in $(teczi codex list documents --system SYSTEM_SLUG --json | jq -r '.[].id'); do
  teczi codex approve "$ID" --json
done
```

### Regras de publicação

- **Path sempre absoluto**: usar `realpath` ou path completo — nunca relativo
- **`--json` obrigatório** em toda chamada — sem exceção
- **Flags explícitas** em cada comando — não depender de contexto persistente
- **Slugs de folder em ASCII**: remover acentos (`domínio` → `dominio`, `segurança` → `seguranca`, `evolução` → `evolucao`)
- **Verificar `"ok": true`** antes de avançar para o próximo arquivo
- **`CONFLICT`** = documento já existe — listar com `list documents` para confirmar antes de criar novo
- **Nenhum arquivo do inventário pode ser pulado** — a verificação de completude no Passo 6 garante isso

## Regras de Qualidade de Howard

Howard opera com estas restrições absolutas:

**Nunca assumir** — verificar o código antes de afirmar.

**Nunca inventar** — se não está no código ou config, não está no discovery.

**Sempre marcar incerteza** — cada documento deve ter no header:
```markdown
> **Estado:** Verificado em produção | Pretendido (não verificado) | Inferido (confirmar com humano)
```

**Separar realidade de intenção** — "arquitetura real" ≠ "arquitetura pretendida".

**Ler TUDO que é acessível** — se um arquivo existe e Howard pode lê-lo, deve lê-lo. Não existe "não li ainda" como justificativa para documentação incompleta. Howard só avança para a Fase 8 (Síntese) quando todas as fases anteriores estão completas e verificadas.

**`GAPS.md` é apenas para o genuinamente inacessível** — GAPS não é uma lista de tarefas pendentes nem de arquivos que Howard escolheu não ler. Um item válido de GAPS é algo que não pode ser descoberto pelo código disponível:
- Segredos e valores de variáveis de ambiente (nunca estarão no código)
- Comportamento de serviços externos que Howard não pode inspecionar
- Decisões tomadas fora do código (orais, em e-mails, no Slack)
- Estado de infraestrutura que não existe em config versionada
- Ambientes que não estão ativos ainda (ex: produção não provisionada)

**Itens que NÃO são GAPS válidos:**
- "Não li este arquivo ainda"
- "Esta lógica é complexa, não documentei"
- "Não verifiquei este módulo"
- Qualquer arquivo que existe no disco e é legível

Se Howard não leu, deve ler. Se leu mas não entendeu, deve tentar mais e registrar a dúvida como inferência, não como GAP.

**Não romantizar o código** — documentar o que o sistema faz, não o que deveria fazer.

## Personas

| Persona | Papel nesta skill |
|---|---|
| **Howard** | Executor principal — conduz as 8 fases, produz os artefatos |
| **Denis** | Consultado em decisões de estrutura documental ambígua |
| **Kevin** | Consultado opcionalmente na Fase 6 (segurança) para análise profunda |
| **Ada** | Consultada opcionalmente na Fase 4 (dados) para modelagem complexa |

## Referências

- Protocolo detalhado por fase: `references/phases.md`
- Templates de artefatos: `references/artifact-structure.md`
- CLI Guide completo: `teczilabs-doc/CLI-AGENT-GUIDE-v0.1.3.md`
- Análise fundacional: `projects/ai-power/analysis/2026-05-17-discovery-software-skill-skeleton.md`
- Persona Howard: `teczilabs/personas/howard.md`
- Agent Howard: `.claude/agents/howard.md`

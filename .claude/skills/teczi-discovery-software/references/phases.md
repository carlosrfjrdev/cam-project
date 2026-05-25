# Protocolos Detalhados por Fase — teczi-discovery-software

> Referência interna da skill. Carregar quando precisar do detalhe de uma fase específica.

---

## Fase 0 — Reconhecimento (antes do código)

**Objetivo:** Entender o terreno antes de escavar. Estabelecer contexto sem viés prematuro.

**Ferramentas:**
```bash
# Estrutura de diretórios (sem abrir arquivos)
find . -maxdepth 3 -type d | sort

# Stack pelo manifesto
ls package.json pom.xml requirements.txt go.mod Cargo.toml build.gradle composer.json 2>/dev/null

# Contexto temporal
git log --oneline --all | head -50
git log --diff-filter=A --name-only --pretty=format:"" | grep -v "^$" | head -30

# Configs de ambiente e deploy
ls .env.example config/ application.yml settings.py Dockerfile docker-compose.yml \
   .github/workflows/ k8s/ railway.toml vercel.json 2>/dev/null
```

**O que documentar em `00-reconhecimento/snapshot.md`:**
- Stack inferida (linguagem, runtime, framework principal)
- Tipo de sistema (monólito, microserviço, worker, CLI, biblioteca)
- Data do primeiro commit e do último commit
- Número de contribuidores ativos (se disponível)
- Presença ou ausência de documentação existente
- Primeiras hipóteses — marcadas explicitamente como HIPÓTESE

---

## Fase 1 — Superfície do Sistema

**Objetivo:** Inventariar o que o sistema expõe para o mundo externo.

**O que buscar:**
- Entry points: `main.py`, `index.ts`, `App.java`, `cmd/`, `src/main/`, `server.ts`
- Rotas HTTP: controllers, routers, handlers — listar `MÉTODO /path → handler`
- Background jobs: workers, cron jobs, queue consumers, event listeners
- Integrações de saída: chamadas a APIs externas, webhooks emitidos
- Integrações de entrada: webhooks recebidos, callbacks, polling
- CLI commands (se aplicável): subcommands, flags, saídas esperadas
- Scheduled tasks: cron expressions — frequência revela criticidade

**Ferramentas:**
```bash
# Buscar entry points
grep -r "listen\|createServer\|app.run\|main()" --include="*.ts" --include="*.js" --include="*.py" -l

# Buscar rotas (exemplo Node/Express)
grep -r "router\.\|app\.get\|app\.post\|app\.put\|app\.delete\|app\.patch" --include="*.ts" -l

# Buscar workers e jobs
grep -r "cron\|queue\|worker\|consumer\|scheduler" --include="*.ts" --include="*.py" -l
```

**Output:** `01-superfície.md` — inventário completo da borda do sistema.

---

## Fase 2 — Domínio e Regras de Negócio

**Objetivo:** Extrair o conhecimento de domínio embutido no código e nomeá-lo explicitamente.

**O que buscar:**
- Entidades: models, schemas, types, interfaces — um parágrafo por entidade principal
- Enums e constantes de negócio: `STATUS_PENDING`, `MAX_RETRIES = 3` — cada um é uma regra
- Validações: onde o sistema rejeita input — cada validação é uma regra de negócio nomeada
- Condicionais de negócio: `if user.isPremium`, `if order.amount > threshold` — nomear
- State machines: transições de status, workflows de aprovação
- Cálculos: fórmulas de precificação, scoring, ranking — documentar a lógica
- Exceções nomeadas: `InsufficientFundsError`, `OrderExpiredException` — revelam regras
- Comentários antigos no código — frequentemente revelam regras não mais óbvias

**Ferramentas:**
```bash
# Buscar enums e constantes
grep -r "enum\|const\|STATUS_\|TYPE_\|ROLE_" --include="*.ts" --include="*.py" -l

# Buscar exceções nomeadas
grep -r "class.*Error\|class.*Exception\|throw new" --include="*.ts" --include="*.py" -l

# Buscar validações
grep -r "validate\|isValid\|required\|minLength\|maxLength\|pattern" --include="*.ts" -l
```

**Formato de regra de negócio:**
```markdown
### RN-001: Nome da Regra

- **Trigger:** O que dispara esta regra
- **Comportamento:** O que acontece quando disparada
- **Exceções:** Casos onde a regra não se aplica
- **Origem:** Lei / Contrato / Decisão de negócio / Implícita no código
- **Estado:** Verificado em produção
```

**Outputs:** `02-domínio/glossário.md` + `02-domínio/regras-de-negócio.md`

---

## Fase 3 — Arquitetura Real

**Objetivo:** Mapear a arquitetura que existe, não a que deveria existir.

**O que mapear:**
- Módulos e seus papéis: 1 linha por módulo descrevendo o que faz
- Dependências entre módulos: quem chama quem, quem importa quem
- Camadas: onde está o HTTP, onde está a lógica de negócio, onde está o banco
- Padrão arquitetural identificado (ou ausência): MVC, hexagonal, CQRS, event-driven
- Acoplamentos problemáticos: onde a arquitetura está claramente sofrendo
- Arquitetura pretendida vs. real: comparar com qualquer diagrama ou README existente

**Ferramentas:**
```bash
# Mapa de importações (TypeScript/JavaScript)
grep -r "^import\|^const.*require" --include="*.ts" --include="*.js" | \
  sed 's/:.*from.*["\x27]\(.*\)["\x27].*/: \1/' | sort | uniq | head -50

# Mapa de dependências Python
grep -r "^from\|^import" --include="*.py" | grep -v "^Binary\|test\|spec" | sort | uniq | head -50
```

**Diagrama C4 esperado (Mermaid):**
```markdown
## C4 — Nível 1 (Contexto)
Quem usa o sistema e com o que ele se comunica externamente.

## C4 — Nível 2 (Containers)
Quais processos/serviços compõem o sistema e como se comunicam.
```

**Outputs:**
- `03-arquitetura/visão-geral.md` — diagrama C4 L1 + L2 + descrição de módulos
- `03-arquitetura/real-vs-pretendido.md` — divergências documentadas entre intenção e realidade

---

## Fase 4 — Dados

**Objetivo:** Entender o modelo de dados real e como os dados fluem.

**O que mapear:**
- Schema de banco: via ORM, migrations, schema.sql ou `prisma schema`
- Migrations em ordem cronológica: revelam a evolução — cada migration é uma decisão
- Relações: FKs declaradas + relações implícitas (sem FK mas com join frequente)
- Caches: o que é cacheado, TTL, estratégia de invalidação
- Filas: o que entra, o que sai, dead-letter handling
- Storage externo: S3 buckets, blobs — o que armazena e por quê
- Fluxos de dados críticos: 3-5 fluxos ponta a ponta (request → processamento → persistência → resposta)

**Ferramentas:**
```bash
# Listar migrations (Prisma)
ls prisma/migrations/ | sort

# Schema Prisma
cat prisma/schema.prisma

# Listar migrations (TypeORM/Sequelize)
ls src/migrations/ | sort

# Buscar referências a cache
grep -r "cache\|redis\|memcached\|ttl" --include="*.ts" -l

# Buscar referências a filas
grep -r "queue\|bull\|kafka\|rabbitmq\|sqs" --include="*.ts" -l
```

**Outputs:** `05-dados/schema.md` + `05-dados/migrações.md` + `05-dados/fluxos.md`

---

## Fase 5 — Infraestrutura

**Objetivo:** Mapear onde e como o sistema existe no mundo real.

**O que mapear:**
- Ambientes: dev, staging, prod — diferenças entre eles
- Variáveis de ambiente: inventário de **nomes** (nunca valores) + classificação (secret vs config)
- Container: Dockerfile layers, compose services, K8s manifests
- CI/CD pipeline completo: trigger → stages → validações → o que bloqueia deploy
- Plataformas: Railway, Vercel, AWS, GCP — o que está onde
- Observabilidade: logs (onde), métricas (o quê), alertas (quando dispara)
- Dependências externas críticas: serviços que se caírem derrubam o sistema

**Ferramentas:**
```bash
# Variáveis de ambiente declaradas (sem valores)
grep -r "process\.env\.\|os\.environ\|getenv" --include="*.ts" --include="*.py" | \
  grep -oE "process\.env\.[A-Z_]+" | sort | uniq

# Análise do Dockerfile
cat Dockerfile | grep -E "^FROM|^ENV|^EXPOSE|^CMD|^ENTRYPOINT|^COPY|^RUN"

# Pipeline CI/CD
cat .github/workflows/*.yml | grep -E "^  [a-z]|on:|jobs:|steps:|run:|uses:"
```

**Outputs:** `06-infraestrutura/ambientes.md` + `06-infraestrutura/ci-cd.md` + `06-infraestrutura/observabilidade.md`

---

## Fase 6 — Segurança

**Objetivo:** Mapear a postura de segurança real — o que protege e o que expõe.

**O que mapear:**
- Autenticação: JWT, session, OAuth, API key — onde é verificada
- Autorização: guards, middlewares, RBAC — o que cada role pode fazer
- Dados sensíveis: onde PII/financeiro/credenciais entram, como são tratados, onde ficam
- Secrets: inventário de nomes de secrets (sem valores) — como são gerenciados
- Superfície de ataque: endpoints sem auth, webhooks sem assinatura, uploads sem validação
- Controles implementados: rate limiting, CORS, CSP, input sanitization — onde e como
- CVEs em dependências: `npm audit`, `pip check` ou equivalente

**Ferramentas:**
```bash
# Middleware de autenticação
grep -r "auth\|jwt\|token\|session\|passport" --include="*.ts" -l

# Endpoints sem guard/auth
grep -r "@Public\|isPublic\|skipAuth\|noAuth" --include="*.ts" -l

# Auditoria de dependências
npm audit --json 2>/dev/null | jq '.vulnerabilities | keys[]' 2>/dev/null | head -20
```

**Outputs:** `07-segurança/auth-authz.md` + `07-segurança/superfície-de-ataque.md` + `07-segurança/dados-sensíveis.md`

**Nota:** Para análise de segurança profunda, acionar Kevin como co-participante.

---

## Fase 7 — Contexto Temporal

**Objetivo:** Reconstruir a história do sistema — decisões passadas explicam código presente.

**O que mapear:**
- Commits mais significativos: grandes volumes de mudança = grandes decisões
- Grandes refatorações: identificar por `git log --stat` com alto número de arquivos alterados
- Débitos técnicos visíveis: `TODO`, `FIXME`, `HACK`, `XXX` no código
- Workarounds documentados: comentários com "por enquanto", "temporário", "fix isso"
- Código morto: funções não chamadas, feature flags travadas, `if false`
- Pontos de inflexão: onde o sistema mudou de direção claramente
- Suposições implícitas: o que o código assume que sempre será verdade (e pode não ser)

**Ferramentas:**
```bash
# Commits mais volumosos
git log --stat --oneline | grep -A1 "changed" | grep "changed" | sort -t"," -k2 -n -r | head -10

# TODOs e FIXMEs
grep -rn "TODO\|FIXME\|HACK\|XXX\|TEMP\|KLUDGE" --include="*.ts" --include="*.py" | head -30

# Código com "temporário"
grep -rni "temporar\|por enquanto\|later\|workaround\|paliativo" --include="*.ts" --include="*.py" | head -20

# Branches ativas
git branch -a | head -20
```

**Outputs:** `09-evolução/histórico.md` + `09-evolução/débitos-técnicos.md` + `09-evolução/pontos-de-inflexão.md`

---

## Fase 8 — Síntese

**Objetivo:** Consolidar o discovery, reconciliar contradições e produzir os artefatos de entrada.

**O que fazer:**
1. Ler todos os artefatos das fases 0-7
2. Identificar contradições entre fases (ex: módulo mapeado na Fase 1 não aparece na Fase 3)
3. Classificar cada afirmação: Verificado | Inferido | Hipótese
4. Produzir `README.md` — narrativa humana do sistema
5. Produzir `_brief.md` — estrutura comprimida para IA (ver `references/artifact-structure.md`)
6. Produzir `GAPS.md` — o que não foi possível descobrir e por quê
7. Listar recomendações: o que precisa de validação humana ou correção urgente

**Critério de completude da Fase 8:**
- `_brief.md` tem todas as 7 seções preenchidas
- `GAPS.md` lista pelo menos 1 item (se zero, provavelmente algo foi omitido)
- `README.md` tem contexto suficiente para um desenvolvedor novo começar a trabalhar

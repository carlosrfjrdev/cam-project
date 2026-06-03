# PIVOT-TCaM-STRATEGY — Virada Estratégica para Produto

> **Status:** PROPOSTA (planejamento — não executada). Aguarda revisão e aprovação do Founder.
> **Autor (orquestração):** Leo (Chief Orchestrator)
> **Data:** 2026-06-03
> **Branch:** `dev` (checkpoint do estado antigo preservado em `the_old_cam` @ `82fb17a`)
> **Codinome novo do produto:** **TCaM — Teczi Cockpit Assets Manager** (substitui "The CaM — The Carlos Alternative Money")

---

## 0. Nota de método (honestidade de processo)

Este documento foi produzido por **Leo** lendo o **estado real do código** (`apps/cam-cockpit/`)
e os documentos institucionais. O ambiente atual **não disponibilizou o dispatch de
subagents** (Agent tool), então os pareceres de Marty, Albert, Oscar, Voltaire, Kevin,
Peter e Don abaixo são **consolidações que Leo redigiu a partir do mandato de cada persona**
— não saídas de invocações reais. **Recomendação:** antes da execução da Fase 1, rodar uma
sessão real com Oscar (ARCH), Voltaire (challenger) e Kevin (segurança/compliance) para
validar as seções 5, 6 e 7. As decisões marcadas `⚖️ FOUNDER` no final são as que travam a execução.

---

## 1. Contexto da virada

O Founder identificou **potencial comercial** no produto. A direção muda de natureza:

| Dimensão | O que ERA (The CaM) | O que PASSA a ser (TCaM) |
|---|---|---|
| **Natureza** | Cockpit pessoal, local, **não comercial** | Produto **comercial** (SaaS/ferramenta) |
| **Usuário** | **Um** operador (Carlos) | **Terceiros** (múltiplos clientes) |
| **Papel do Carlos** | Operador único | **Fornecedor de solução** (não opera) |
| **Autoridade central** | **Constituição** (disciplina pessoal soberana) | Inexistente — disciplina vira **feature configurável** do cliente |
| **Risk Engine** | Trava moral/constitucional inviolável (Art. 15º) | **Feature de produto** (Assets RiskManager) que o cliente parametriza |
| **Modelo de dados** | Single-operator (sem tenant) | Multi-tenant (planejado para fase futura) |
| **Operação real** | Proibida na Fase 0 (trava constitucional) | **Config de produto/ambiente** (`REAL_TRADING_ALLOWED` vira flag, não lei) |

A **Constituição morre inteira** (ver `CONSTITUTION-DECOMMISSION.md`). Ela era a disciplina
**pessoal de trader** do Carlos. Como ele deixa de operar, ela perde objeto.

---

## 2. Restrições de execução do Founder (vinculantes)

1. **PRIMEIRO fazer o app RODAR** sob o novo paradigma (estabilizar o que existe).
2. **Camada de usuário** (multi-tenant, auth, billing) vem **DEPOIS** — não implementar agora.
3. Esta entrega é **PLANEJAMENTO**. Nenhum código removido, nenhuma Constituição apagada
   até o Founder aprovar os 3 documentos.
4. **DevFlow NCC-1701 e as personas CONTINUAM válidos** — são processo de engenharia, não a
   Constituição-do-trader. Só a Constituição morre.

---

## 3. Os 8 módulos "Assets *" — visão de produto

Nomenclatura do Founder. Mapeamento detalhado feature-a-feature em `MAP-MODULES-TCaM.md`.

| # | Módulo | Função | Estado hoje | Veredito |
|---|---|---|---|---|
| 1 | **Assets Cockpit** | Cockpit operacional | `features/cockpit` + `dashboard_routes` + WS | ✅ Existe → renomear/recompor |
| 2 | **Assets Manager** | Gerenciador de Ativos (carteira/posições) | `carteira-hard` + `harvest` + `ledger` + `holdings` | ⚠️ Existe parcial → consolidar |
| 3 | **Assets RiskManager** | Gerenciador de Risco **configurável** | `_shared/risk` (engine + validators) | ⚠️ Existe como trava → **converter em config** |
| 4 | **Assets Inspector** | Inspetor de Ativos (gráficos, dividendos, fundamentos) | `features/inspetor` (frontend) + `fundamentals`/`regime`/`market_data` | ✅ **Pronto (MVP)** |
| 5 | **Assets Strategy** | Gestão e lista de estratégias | `features/strategies` + `strategy lifecycle` | ✅ Existe → renomear |
| 6 | **Assets RunTests** | Backtest matemático (Python) | `features/backtest` + `walk_forward` + `simulator` | ✅ Existe → renomear |
| 7 | **Assets Experts** | Gestão de Robôs MT5 | `mt5_integration` + `robot_orchestrator` + EAs `mql5/` | ✅ Existe → renomear |
| 8 | **Assets Labs** | Laboratório de pesquisas (Quant Lab) | `quant-lab` + `research` (lead-lag) | ✅ **Pronto** |

**Leitura:** 5 dos 8 módulos já têm base sólida no código. Nenhum módulo nasce do zero —
a virada é majoritariamente **rebrand + recomposição de navegação + conversão da camada de
disciplina (Constituição/Risk) em configuração de produto**. Isso favorece a restrição #1
do Founder ("fazer o app rodar primeiro").

---

## 4. Parecer de produto — Leo channeling Marty (DISC) + Albert (SPEC)

**Marty (reposicionamento, anti-feature-factory):**
- A virada **não cria features novas agora** — recompõe as existentes em 8 módulos nomeados.
  Isso é saudável: evita feature factory. O risco de produto é **dispersão** — 21 features de
  backend hoje, 19 telas de frontend. Os 8 módulos são um bom **chassi de consolidação**.
- **In (Fase 1):** rebrand para TCaM, navegação pelos 8 módulos, app rodando sem a Constituição
  como autoridade, Risk vira config.
- **Out (Fase 1):** multi-tenancy, auth, billing, onboarding de cliente.
- **Later:** features que hoje são "disciplina pessoal" (journal obrigatório, checklists,
  session ritual, harvest, carteira-hard, decision-postmortem) → reavaliar se viram **features
  opcionais do produto** ou se saem do MVP comercial.
- **Pergunta aberta:** os módulos pessoais de disciplina (journal, harvest, fiscal/DARF BR)
  são **diferencial de produto** ou **bagagem pessoal do Carlos**? (ver `⚖️ FOUNDER` #4)

**Albert (o que vira feature vs o que morre):**
- **Vira feature configurável:** Risk Engine → `Assets RiskManager` (limites por-cliente,
  não constitucionais). Kill switch → botão de produto. Autonomy matrix → política de produto.
- **Vira feature opcional:** journal, checklists, fiscal/DARF, harvest, carteira-hard.
- **Morre como autoridade:** a hierarquia constitucional, os Arts. 11/15/18/25/35 como lei,
  `REAL_TRADING_ALLOWED=false` como trava moral.
- **Fica como boa engenharia:** isolamento research↔live, audit log, provenance de dados.

---

## 5. Parecer de arquitetura — Leo channeling Oscar (ARCH)

> ⚠️ Validar com Oscar real antes de executar.

**Impacto de remover a Constituição/Risk soberano:**

1. **O Risk Engine NÃO deve ser deletado.** Ele é código maduro (pipeline de validators
   determinístico, pure-Python, em `_shared/risk/`). O que muda é a **semântica**: deixa de ser
   "autoridade constitucional inviolável" e passa a ser **motor de regras configurável por
   cliente**. Os validators (`max_contracts_check`, `daily_loss_limit_check`, etc.) viram
   **regras parametrizáveis**, não constantes de lei. Os comentários que citam "Art. Xº
   INTOCÁVEL" saem; os limites viram colunas de config (futuramente por-tenant).

2. **`feature constitution`** (backend + frontend `ConstitutionPage` + tabela): candidata a
   **remoção** ou reaproveitamento como "Política/Termos do cliente". Hoje serve a um documento
   que deixa de existir. Decisão: remover do MVP, manter migração no histórico Alembic.

3. **Autonomy matrix** (`_shared/autonomy/matrix.py`): a matriz ambiente×modo é **boa
   engenharia de produto** (controla o que é signal/one-click/semi/full por ambiente).
   **Fica**, mas perde os condicionantes constitucionais ("assinatura simbólica do Founder",
   "cooldown 30 dias"). Vira política default configurável.

4. **Multi-tenancy: antecipar SIM, implementar NÃO.** O Founder disse multi-user vem depois,
   mas a arquitetura **não pode fechar portas**. Recomendação mínima de antecipação (sem
   implementar agora): (a) não assumir "operador único" em novos contratos de API; (b)
   reservar conceito de `tenant_id`/`account_id` no design dos novos endpoints sem ainda
   persistir; (c) o `nav.tsx` já tem comentário "single-operator: sem troca de tenant" — marcar
   como dívida explícita. Isto evita retrabalho destrutivo na Fase 2.

5. **`REAL_TRADING_ALLOWED`**: de trava constitucional → **flag de ambiente/produto**. O
   `useEnvironment.ts` já trata como booleano defensivo; só muda a **narrativa** (não é mais lei).

6. **ADRs:** abrir ADR-TCaM-001 "Decomissionamento da Constituição e reposicionamento do Risk
   Engine como feature configurável" (irreversível e caro → exige ADR formal).

---

## 6. Parecer do challenger — Leo channeling Voltaire

> ⚠️ Validar com Voltaire real — esta seção é deliberadamente desconfortável.

**A pergunta dura: matar a Constituição liberta ou remove o diferencial defensivo?**

- **Tese a favor (liberta):** a Constituição era um pacto **pessoal** do Carlos consigo mesmo.
  Para um terceiro, ela é irrelevante e até hostil — ninguém compra um produto que impõe a
  disciplina psicológica de outra pessoa. Matar a Constituição **destrava o produto**.

- **Antítese (cuidado — há um bebê na água do banho):** a Constituição codificava **anos de
  dor e lições reais** sobre ruína de trader. O *mecanismo* (Risk Engine, limites, kill switch,
  loss limits, anti-martingale, anti-revenge) é **exatamente o que falta na maioria das
  ferramentas de trading do mercado**. Jogar fora a **autoridade** é correto. Jogar fora o
  **mecanismo** seria destruir o maior diferencial competitivo do TCaM: *"a única ferramenta
  que protege o operador dele mesmo, por configuração"*. **Recomendação: mate a lei, venda o
  mecanismo como `Assets RiskManager` — esse é o moat.**

- **Risco estratégico:** sem a Constituição, o produto vira "mais um cockpit de trading". Há
  centenas. O diferencial defensivo (gestão de risco séria, anti-ruína, disciplina
  configurável) é o que separa TCaM de um terminal genérico. **Não confundir matar a lei com
  matar a tese.**

- **Provocação final ao Founder:** "Você está vendendo a *ferramenta de fazer dinheiro* ou a
  *ferramenta de não perder tudo*? São produtos diferentes, com clientes diferentes e
  responsabilidades legais diferentes. Decida isso ANTES de codar." (ver `⚖️ FOUNDER` #1)

---

## 7. Parecer de segurança/responsabilidade — Leo channeling Kevin (SEC-GOV)

> ⚠️ Validar com Kevin real — compliance de ferramenta de trading para terceiros é material.

**Vender ferramenta que ajuda terceiros a operar muda o perfil de risco legal radicalmente:**

1. **Responsabilidade por perdas do cliente.** No mundo pessoal, o único prejudicado era o
   Carlos. Vendendo a terceiros, **perdas de clientes podem gerar reivindicação**. Exige, no
   mínimo: Termos de Uso + disclaimer de risco robusto ("ferramenta, não consultoria; não
   garante resultado; trading envolve risco de perda total").

2. **A IA NÃO pode virar "robô que promete lucro".** O Art. 1º da Constituição moribunda dizia
   "não é robô de promessa de lucro" — essa **postura deve sobreviver como política de produto/
   marketing**, não como lei moral. Vender promessa de retorno tem implicação regulatória (CVM
   no Brasil: gestão/consultoria de valores mobiliários é atividade **regulada**).

3. **Fronteira regulatória (CVM/BR).** Se o TCaM **apenas fornece ferramenta** que o cliente
   opera com a própria conta/corretora → menor exposição. Se o TCaM **dá recomendação,
   gere capital de terceiro, ou executa por ele** → entra em **território de atividade
   regulada** (consultor/gestor de valores mobiliários). **Linha vermelha de produto a
   definir.** (ver `⚖️ FOUNDER` #2)

4. **Execução de ordem por terceiros = superfície crítica.** Multi-tenant + ordem real +
   credenciais de corretora de cliente = dados sensíveis, segregação por tenant, auditoria,
   secrets management. Hoje é single-operator local; vira **alvo de ataque** quando for SaaS.
   **Gatilho SEC-GOV obrigatório** quando a Fase 2 (multi-tenant) começar.

5. **O que sobrevive como boa engenharia (e agora como dever de cuidado do produto):** audit
   log, isolamento research↔live, provenance de dados, kill switch (vira feature de segurança
   vendável, não trava moral).

**Veredito de Kevin:** a virada é legítima, mas **abre exposição legal/regulatória que não
existia**. Não bloqueia a Fase 1 (rebrand + app rodando), mas **a Fase 2+ não pode começar sem
definição da fronteira regulatória e dos Termos de Uso.**

---

## 8. Parecer de UX/navegação — Leo channeling Peter (produto) + Don (UX)

Mapeamento de navegação detalhado em `MAP-MODULES-TCaM.md` §4. Resumo:

- A nav atual tem 19 itens em 6 grupos ("Pesquisa, Operação, Estratégia, Registro, Patrimônio,
  Sistema") + flag `visibleInMvp`. **Os 8 módulos Assets* são uma IA (arquitetura de
  informação) melhor** — menos itens, mais clara para um cliente que não é o Carlos.
- **Don:** a navegação deve falar a língua do **cliente-trader genérico**, não a língua do
  diário pessoal do Carlos ("Harvest", "Carteira Hard", "Constituição" são jargão pessoal).
  Renomear para os 8 Assets* já melhora drasticamente a clareza.
- **Peter:** sequência de valor para o cliente: **Inspector (entender ativo) → Strategy
  (definir) → RunTests (validar) → Experts (rodar robô) → RiskManager (proteger) → Cockpit
  (operar/monitorar) → Manager (gerir carteira) → Labs (pesquisar)**. Essa ordem vira a
  estrutura do menu.

---

## 9. O que morre com a Constituição (resumo — detalhe em CONSTITUTION-DECOMMISSION.md)

- ❌ Hierarquia constitucional como autoridade (`Constituição > Risk Engine > ... > IA`)
- ❌ Arts. 11/15/18/25/26/31/35/36 como **lei** (viram, no máximo, defaults de config)
- ❌ Limite "2 WIN / 2 WDO" como constante intocável → vira parâmetro de cliente
- ❌ Kill switch / DARF bloqueante / journal obrigatório como **dever moral** → features opcionais
- ❌ "IA não pode operar" como **dogma** → vira política de produto + escolha do cliente
- ❌ `CONSTITUICAO.md` como documento soberano → **arquivado** (memória histórica)

## 10. O que SOBREVIVE (reaproveitado)

- ✅ Risk Engine (vira `Assets RiskManager` configurável) — **o moat (Voltaire)**
- ✅ Inspetor, Quant Lab, Backtest, Strategies, MT5/robôs — base dos módulos Assets*
- ✅ Isolamento research↔live (import-linter) — boa engenharia, não mais mandato
- ✅ Audit log, provenance de dados, autonomy matrix — viram dever de cuidado do produto
- ✅ DevFlow NCC-1701 + personas — processo de engenharia

---

## 11. Faseamento proposto

### Fase 1 — Limpeza + Rebrand + App Rodando (FOCO ATUAL)
- Descomissionar Constituição (arquivar `CONSTITUICAO.md`; limpar `CLAUDE.md` e memory).
- Rebrand The CaM → **TCaM** nos textos de produto (não no path `cam-cockpit` ainda — evitar
  churn de import; decisão de renomear pastas é separada).
- Converter Risk Engine de "trava constitucional" em **feature configurável** (remover
  comentários de "Art. Xº INTOCÁVEL"; limites viram config, não constantes de lei).
- Recompor navegação nos 8 módulos Assets*.
- **App roda end-to-end** (backend + frontend + Inspetor/MT5 funcionando) sob o novo paradigma.
- **Gate Founder.**

### Fase 2 — Camada de Usuário
- Multi-tenancy (modelagem `tenant_id`/`account_id`), auth, isolamento por cliente.
- **SEC-GOV obrigatório (Kevin).** Termos de Uso + fronteira regulatória **definidos antes**.

### Fase 3 — Comercial
- Billing, onboarding, planos, observabilidade SaaS, hardening de segurança.

### Fase 4 — Escala
- Performance multi-tenant, suporte a múltiplas corretoras, marketplace de estratégias/robôs.

> Estimativas em horas/dias/semanas **proibidas** (NCC-1701). Proporcionalidade P/M/G será
> atribuída por Albert (SPEC) quando cada frente virar demanda.

---

## 12. Decisões que dependem do Founder (travam a execução)

| # | Decisão | Por quê trava |
|---|---|---|
| ⚖️ FOUNDER #1 | **Qual produto?** "Ferramenta de fazer dinheiro" vs "ferramenta de não perder tudo" (Voltaire §6) | Define posicionamento, moat e clientes |
| ⚖️ FOUNDER #2 | **Fronteira regulatória:** TCaM só fornece ferramenta, ou recomenda/gere/executa por terceiro? (Kevin §7.3) | Define exposição CVM/legal; trava Fase 2 |
| ⚖️ FOUNDER #3 | **Renomear pastas** `apps/cam-cockpit` → `tcam`? Ou só rebrand de UI/produto agora? | Path-rename é destrutivo (imports); recomendo adiar |
| ⚖️ FOUNDER #4 | Módulos de disciplina pessoal (journal, harvest, carteira-hard, fiscal/DARF) entram no MVP comercial ou saem? (Marty §4) | Define escopo do MVP |
| ⚖️ FOUNDER #5 | Aprovar o descomissionamento da Constituição conforme `CONSTITUTION-DECOMMISSION.md`? | Gate da Fase 1 |
| ⚖️ FOUNDER #6 | Rodar sessão real de Oscar/Voltaire/Kevin para validar §§5-7 antes de codar? | Qualidade dos pareceres (ver §0) |

---

*Documento de planejamento. Nenhuma alteração de código ou de documento institucional foi
executada. Aguarda aprovação do Founder.*

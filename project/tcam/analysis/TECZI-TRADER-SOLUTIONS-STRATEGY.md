# Teczi Trader Solutions — Análise e Estratégia

**Data:** 2026-06-04
**Sessão:** Power Strategy Session — Leo (orquestrador) + Sun, Voltaire, Mammon, Grace, Kevin, Peter, Fred
**Status:** Decisões do Founder respondidas. Pronto para execução.

---

## 1. Contexto — O que mudou e por quê

### Motivação (D1 — respondida pelo Founder)

O CaM foi concebido como base de operação pessoal. Ao longo da construção, tornou-se comercialmente interessante — o Founder não encontrou no mercado nada comparável em rigor de validação. A primeira virada (2026-06-03) tentou transformar o CaM em produto SaaS multi-tenant (TCaM). O reposicionamento de 2026-06-04 vai mais fundo:

**"The Carlos Alternative Money"** — múltiplas fontes de renda, não só mercado. O mercado financeiro é arriscado; uma fonte sustentável complementar muda a equação. Testando a estratégia D1 ORB-30, o Founder identificou potencial real de gerar valor a terceiros com robôs validados.

> Resultado positivo gera caixa. Resultado negativo gera experiência. Ambos constroem o produto.

### Papel do CaM no novo ecossistema

O CaM **não é o produto final** neste momento. É o **laboratório de validação** — onde estratégias são desenvolvidas, testadas e aprovadas antes de virarem produto vendável.

| Papel | O que faz | Estado |
|---|---|---|
| **Laboratório** | Desenvolver, testar e validar estratégias próprias (StrategyLab, RunTests, Experts, RiskManager) | Ativo — é o que está sendo construído |
| **Produto futuro** | Plataforma TCaM para terceiros usarem | Fase 0 — base existe, produto não é foco agora |

---

## 2. Posicionamento

**Marca:** Teczi Trader Solutions
**Site institucional:** `https://www.teczi.tech/`
**Landing de vendas:** `https://robots.teczi.tech/`

**Para quem:** Traders que querem automatizar — do iniciante que nunca programou ao experiente que quer parar de operar manualmente. A dor é a mesma: *"quero um robô que funcione de verdade, com backtest honesto."*

**O que vende (em ordem de fase):**
1. Robôs prontos (EA MT5) com backtest auditável e disclaimers claros
2. Criação de robôs custom (serviço sob demanda)
3. Plataforma TCaM como produto separado — ainda não é o foco

**Tese central:** a maioria das ferramentas de trading vende promessa de lucro. A Teczi vende o oposto — robôs que passaram por critério de edge comprovado com gestão de risco embutida. O **Assets RiskManager** (ex-Risk Engine do CaM) é o moat: é o que diferencia os robôs Teczi do lixo do mercado.

---

## 3. Análise Estratégica — Cast Completo

### 3.1 Sun — Postura Estratégica

**Postura: ATACAR com estreitamento progressivo.**

"Construir amplo, liberar estreito." Em vez de SaaS multi-tenant (anos de trabalho, regulação pesada, compliance CVM), o Founder foca no que já existe: EAs MT5 validados. Superfície de ataque menor, ciclo de validação mais rápido, capital inicial praticamente zero.

| O que GANHA vs TCaM SaaS | O que PERDE vs TCaM SaaS |
|---|---|
| Time-to-revenue dramático (semanas vs anos) | Receita não-recorrente (sem MRR natural) |
| Infraestrutura de distribuição trivial | Escalabilidade aritmética em vez de compounding |
| Risco regulatório menor | IP vulnerável |
| Validação imediata de mercado | Barreira de entrada baixa (qualquer dev MQL5 compete) |
| Capital inicial quase zero | Suporte operacional por cliente |

**Risco de postura crítico:** dois reposicionamentos em 24 horas. O mercado de robôs tem suas próprias dificuldades. O Founder precisa se comprometer e ficar.

### 3.2 Voltaire — Devil's Advocate

> *"Duas viradas em dois dias. Ou você descobriu a direção certa muito rápido, ou ainda não sabe qual é."*

**Inversão 1 — O produto real:**
Você está vendendo o robô (que qualquer dev MQL5 pode copiar em uma semana) e o que genuinamente construiu é o processo de validação (CaM, backtest honesto, walk-forward, Evidence Pack). O moat de um EA é frágil. O moat do método de validação é muito mais sólido — e o Founder mantém isso como diferencial.

**Inversão 2 — O modelo não estava definido:**
"Licenciamento OU venda do código-fonte" não é "a definir" — é a decisão central. **Venda de código-fonte está descartada** (IP sai de mão, sem escala, sem recorrência). Decisão fica para quando os primeiros clientes aparecerem.

**Inversão 3 — O produto não está validado em real:**
Backtest bom é condição necessária, não suficiente. O mercado de robôs MT5 está cheio de backtest lindo que explode em real. **D3 resolvido:** intenção declarada de testar em real antes de vender.

**Pergunta respondida:** o insight é genuíno — "percebi que meu diferencial real são os EAs validados pelo meu método" + múltiplas fontes de renda como princípio. Não foi fuga de complexidade.

### 3.3 Mammon — Oportunidade e Modelo de Negócio

**O mercado é real. A assimetria existe. O moat não é o código — é o método.**

O mercado de robôs MT5 no Brasil existe e tem demanda comprovada (dezenas de vendedores no Hotmart/Kiwify, preços entre R$300 e R$3.000 por EA). O que o Founder tem que nenhum deles tem: um laboratório de validação real com backtest honesto, walk-forward e Evidence Pack.

**Modelo de negócio (D4 — a decidir na Fase 3):**

| Modelo | Receita estimada | Complexidade | Quando usar |
|---|---|---|---|
| **A — Licença perpétua** | ~R$5K para validar | Mínima | Fase 3 — primeiras vendas |
| **B — Assinatura recorrente** | R$7.500/mês com 50 clientes | Média | Quando tiver 3+ robôs e demanda comprovada |
| **C — Revenue share** | Variável | Alta (risco CVM) | **Evitar** |

**Recomendação:** começa com A, migra para B quando tiver portfólio e clientes recorrentes, nunca faz C sem consultar advogado especializado em CVM.

### 3.4 Grace — Stack e Tecnologia

**A virada é tecnicamente mais simples que o TCaM SaaS. O ponto crítico é a distribuição/DRM do EA.**

**Distribuição do EA:**

| Opção | Proteção IP | Complexidade | Recomendação |
|---|---|---|---|
| MQL5 Market (MetaQuotes) | Alta — DRM nativo | Baixa | Fase 2+ (quando tiver portfólio e reputação) |
| **Venda direta (.ex5)** | Média-baixa | Mínima | **Fase 3 — primeiras vendas** |
| Licenciamento próprio no MQL5 | Média (quebrável) | Alta | Evitar inicialmente |

**Para pagamentos:** Hotmart/Kiwify antes de Stripe — zero infraestrutura própria, resolve NF BR, chargeback gerenciado, checkout localizado. Stripe quando houver volume e razão técnica para controle total.

**Para landing page:** no-code (Webflow/Framer) para validação rápida. Migraria para React/Vite se houver razão técnica real.

**Para o CaM interno:** quase nada muda. O que pode precisar: Evidence Packs exportáveis de forma mais legível para clientes (relatórios de backtest/walk-forward em linguagem de trader, não só de quant).

**Profit/NTSL:** STANDBY. MT5 primeiro, expansão depois com tração comprovada.

### 3.5 Kevin — Legal e Regulatório

**A fronteira regulatória é a decisão mais importante antes de qualquer venda.**

**O que separa ferramenta de serviço regulado:**

| Modelo seguro | Modelo proibido (exposição CVM) |
|---|---|
| Vende software, cliente instala e opera com conta própria | Cobrar % sobre lucros do cliente (gestor de recursos — regulado) |
| Sem acesso à conta do cliente | Gerir a conta do cliente automaticamente |
| Sem performance fee | Dar recomendação personalizada de compra/venda (consultor — regulado) |

**Três itens não-negociáveis antes da primeira venda:**
1. **Termos de Uso + Disclaimer de Risco:** "Este software é uma ferramenta algorítmica. Resultados passados não garantem resultados futuros. Trading envolve risco de perda total do capital investido. A Teczi não presta consultoria de investimentos."
2. **Política de Privacidade (LGPD):** obrigatória ao coletar email/nome.
3. **Decisão de distribuição confirmada** (direta + futuro MT5 Market): impacta IP e responsabilidade legal.

**Linha vermelha absoluta:** nenhuma promessa de retorno. "100% de assertividade", "R$3.000/mês garantido", "robô que nunca perde" = propaganda enganosa (PROCON/SENACON) + potencialmente atividade de consultoria não registrada (CVM) + reputação destruída quando o EA perde (e todo EA perde em algum momento).

### 3.6 Peter — Produto e Go-to-Market

**Dois segmentos com a mesma dor — abordagens distintas:**

| Segmento | Perfil | Argumento de venda | Risco |
|---|---|---|---|
| **Trader experiente** | Já usa MT5, entende walk-forward, compra pelo Evidence Pack | Método + transparência + risk management | Baixo |
| **Trader iniciante** | Quer automatizar mas não tem histórico | Simplicidade + suporte + sem jargão técnico | Suporte mais alto |

**Evitar:** trader que busca "robô que faz dinheiro garantido" — é o cliente do lixo do mercado. Alto chargeback, insatisfação garantida, destrói reputação.

**Estratégia de portfólio declarada pelo Founder:**
- Fase 1: 5 robôs com performance real documentada → cria reputação
- Fase 2: serviço de criação de robôs custom — "construímos 5, agora construímos o seu"

**Go-to-market mínimo:**
1. Publicar resultados em grupos MT5 BR (Telegram, Discord, LinkedIn) — medir interesse real, zero investimento
2. Landing de uma página + primeiro EA + disclaimer + preço
3. Meta: 5 primeiros clientes. Depois: decidir modelo definitivo com dados reais.

### 3.7 Fred — Domínio de Mercado

**Gaps de vocabulário e posicionamento a resolver antes do lançamento:**

- O D1 ORB-30 é **EA de execução** (automação total) — declarar isso de forma inequívoca. Confusão é a causa #1 de insatisfação e chargeback.
- D1 em timeframe **diário é swing, não day trade** — nicho dentro do mercado BR de robôs (dominado por day traders). Não é problema; é segmentação que precisa ser declarada.
- "Evidence Pack" precisa de nome mais vendável: **"Relatório de Validação"** ou **"Análise de Robustez"**.
- Declarar explicitamente: opera WIN ou WDO? Quantos contratos? Qual a expectativa de frequência de trades?
- Modelo de licenciamento que o mercado entende: **"por conta MT5"** — o EA funciona apenas na conta registrada pelo cliente.

---

## 4. Roadmap em Fases

### Fase 1 — Validação em real (agora)

**Objetivo:** ter pelo menos 1 robô rodando em conta real própria com resultado documentado.

- Finalizar validação do D1 ORB-30 no StrategyLab (paridade de PASS no tester + aprovação do Founder)
- Rodar em conta demo → documentar resultado por semanas
- CaM é o laboratório — não é produto ao cliente ainda
- **Marco de saída:** resultado positivo documentado OU loss com diagnóstico limpo

### Fase 2 — Portfólio de 5 robôs

**Objetivo:** 5 estratégias diferentes com backtest auditável + walk-forward aprovados.

- Diversificação por ativo (WIN, WDO, outros), timeframe e tipo (trend, fade, ORB)
- Cada robô passa pelo pipeline: StrategyLab → validação em real (pequeno capital) → Evidence Pack publicável
- **Marco de saída:** 5 EAs com documentação de performance honesta

### Fase 3 — Primeira venda

**Objetivo:** primeiro cliente pagante via venda direta.

- Canal: LinkedIn, Discord de traders, rede pessoal
- Modelo (D4): decidir aqui com base nos primeiros contatos
- Produto entregue: EA MT5 (.ex5) + Relatório de Validação + suporte básico
- **Marco de saída:** ticket recebido, suporte dado, feedback coletado

### Fase 4 — Serviço custom

**Objetivo:** primeiro contrato de robô sob demanda.

- Posicionamento: "temos 5 robôs próprios com track record — agora construímos o seu"
- Precificação mais alta, entrega mais longa, margem melhor
- CaM/TCaM como ferramenta interna do processo de desenvolvimento
- **Marco de saída:** primeiro contrato de criação de EA sob demanda entregue

---

## 5. Estrutura de Produto (Componentes)

| Componente | Papel | Fase |
|---|---|---|
| **Teczi Landing** (`teczi.tech`) | Site institucional — quem somos, o que fazemos | Fase 3 |
| **Robots Landing** (`robots.teczi.tech`) | Landing de vendas — portfólio + Evidence Packs + CTA de compra | Fase 3 |
| **HeroRobots** | Comparação e showcase de robôs | Fase 3–4 |
| **RobotShop** | Sistema de venda e distribuição dos algoritmos | Fase 4 |
| **Pagamentos** | Hotmart/Kiwify (inicial) → Stripe (quando houver volume) | Fase 3 |

> ⚠️ **HeroRobots e RobotShop são destino, não ponto de partida.** Construí-los antes de ter portfólio e tração é feature factory prematura.

---

## 6. O que NÃO fazer

| Armadilha | Por quê evitar |
|---|---|
| Construir TCaM SaaS agora | É Fase 4. Construir para ninguém é desperdício. |
| Apostar concentrado em uma única estratégia | Concentração de portfólio mata a reputação junto com um mercado adverso. |
| Entrar no MT5 Market cedo demais | Perde controle antes de entender o que o cliente valoriza. |
| Qualquer promessa de retorno | Risco CVM + reputação destruída. Sem exceção. |
| Decidir D4 (modelo de negócio) agora | Sem clientes ainda. Otimização prematura. |
| Descontinuar o Assets RiskManager | É o moat. Diferencia da concorrência. Sobrevive como feature de produto. |
| Vender código-fonte | IP sai de mão, sem escala, sem recorrência. Descartado. |

---

## 7. Próximas ações

### Imediato (próxima sessão operacional)

1. Abrir sessão com StrategyLab para fechar validação do D1 ORB-30
   - Confirmar paridade de PASS no Strategy Tester
   - Revisar parâmetros de risco embutidos no EA executor
   - Decidir: entra como **Robô 1** do portfólio ou volta para refinamento?

### Curto prazo (antes da primeira venda)

2. Redigir Termos de Uso + Disclaimer de Risco + Política de Privacidade (LGPD)
3. Produzir Evidence Pack publicável do Robô 1 (legível para trader, não só para quant)
4. Publicar resultados em comunidades MT5 BR — medir demanda antes de investir em landing
5. Decisão de canal de distribuição inicial (direta vs MT5 Market)

### Médio prazo (com os primeiros clientes)

6. Decidir D4 — modelo de negócio (licença perpétua vs assinatura)
7. Landing mínima em `robots.teczi.tech`
8. Expandir portfólio para 5 robôs seguindo o mesmo rigor

---

## 8. Decisões em aberto (D4)

A única decisão não resolvida é o **modelo de negócio (D4)**. Decidir quando os primeiros clientes aparecerem:

- **Opção A (Fase 3):** Licença perpétua — simples, sem infraestrutura, valida o mercado
- **Opção B (Fase 4):** Assinatura recorrente — MRR, alinhamento de incentivos, mais complexo
- **Opção C:** Revenue share — descartada (risco CVM desproporcional)

---

*Documento gerado a partir de Power Strategy Session em 2026-06-04. Founder confirmou D1–D7. Próxima revisão: após Fase 3 (primeiros clientes).*

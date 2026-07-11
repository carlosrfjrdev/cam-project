# Relatório de Análise — Stack UI e Frontend do Cockpit CaM

> Status: recomendação multi-persona para decisão do Founder.
> Escopo: UI library e framework frontend do **cockpit CaM** (web-only, single-operator).
> Contexto: React 19 + Vite, AI-agent-first (IA auditora, nunca executora — Arts. 34º-36º) e security-first.

---

## 1. Resumo executivo

A recomendação consolidada é adotar **MUI como UI Library do cockpit CaM**, com os tokens do CAM como Single Source of Truth e uma camada de tema/componentes acima da biblioteca.

O cockpit é **uma única interface** — não há multi-produto a harmonizar. A questão não é "qual biblioteca para muitos produtos", e sim "qual biblioteca dá menor variância, maior governança e melhor defesa de capital para um cockpit operacional crítico". MUI vence nesses critérios.

> Direção: **MUI como motor de comportamento e acessibilidade; tokens CAM como identidade visual; brutalismo funcional a serviço da clareza operacional.**

---

## 2. Personas consultadas

| Persona | Foco | Resultado |
|---|---|---|
| Andy | Identidade visual, DS, showcase | MUI como base; outras UIs apenas laboratório |
| Grace | Stack, maturidade, lock-in, arquitetura | MUI é defensável; precisa virar contrato de tema |
| Alan | AI-agent-first, previsibilidade para agentes | MUI é a stack mais governável, tipada e auditável |
| Kevin | Security-first, supply-chain, XSS, CSP | MUI é a opção mais defensável com hardening obrigatório |
| Don | UX e defesa de capital | MUI reduz surpresa, melhora formulários densos e leitura operacional |

Convergência: **5/5 personas recomendam MUI para o cockpit**.

---

## 3. Decisão recomendada

### 3.1 Stack do cockpit

| Camada | Recomendação |
|---|---|
| Tokens | `tokens.md` como SSoT humano e futuro `tokens.json` machine-readable |
| Framework | React 19 + Vite (SPA local) — ver `../../project/STACK-CAM-OFICIAL.md` |
| UI Library | **MUI / @mui/material** |
| Ícones | **@mui/icons-material**, variante Outlined por padrão |
| Estilização | MUI System: `sx` para overrides pontuais e `styled()` para padrões reutilizáveis |
| Forms | React Hook Form + Zod |
| Server state | TanStack React Query |
| UI state | Zustand apenas para estado visual |
| Showcase DS | Storybook ou catálogo equivalente usando o tema oficial |

### 3.2 Modelo de tiers (para experimentação)

Mesmo num único cockpit, vale separar produção de experimentação:

| Tier | Uso | Bibliotecas |
|---|---|---|
| Tier 0 — Tokens | Fonte universal de verdade | `tokens.md`, futuro `tokens.json` |
| Tier 1 — Cockpit oficial | Telas operacionais do cockpit | MUI |
| Tier 2 — Exceção controlada | Caso técnico específico com ADR e revisão | React Aria, headless pontual |
| Tier 3 — Protótipo descartável | Spike visual, validação rápida, sem dado real | qualquer kit, com prazo de remoção |

Regra: **Tier 2 e Tier 3 não viram cockpit silenciosamente**. Exigem ADR, revisão de segurança/acessibilidade e aprovação do Founder.

---

## 4. Avaliação das UI libraries

### 4.1 Matriz comparativa

| Critério | MUI | shadcn/ui | Mantine UI | DaisyUI |
|---|---:|---:|---:|---:|
| Maturidade enterprise | Alta | Média/Alta | Alta | Média |
| Theming e tokens | Alta | Alta com disciplina | Alta | Média |
| React/Vite | Alta | Alta | Alta | Alta |
| Acessibilidade base | Alta | Alta se Radix preservado | Média/Alta | Média/Baixa |
| Governança AI-agent-first | Alta | Média | Média/Alta | Baixa/Média |
| Densidade de dados operacionais (DataGrid, etc.) | Alta | Média | Média/Alta | Baixa |
| Bundle/performance | Médio/Alto | Baixo | Médio | Baixo |
| Risco de fragmentação | Baixo | Alto | Médio | Alto |
| Status recomendado | **Oficial** | Exceção controlada | Plano B técnico | Protótipo descartável |

### 4.2 MUI

**Veredito:** aprovado como biblioteca do cockpit.

Pontos fortes:

- Melhor alinhamento com o DS: Dark Mode First, grid 4px, tokens, tonal layering, Poppins/Inter e WCAG AA.
- API semântica e tipada: `Button`, `TextField`, `Dialog`, `Card`, `DataGrid`, `Typography`, `Stack`, `Box`.
- Boa base para agentes: menos ambiguidade, menos variação visual, mais refatoração automatizável.
- Ecossistema forte para telas operacionais densas: Data Grid, Date Pickers, Charts.
- Funciona nativamente em React 19 + Vite.

Riscos:

- Pode ficar com cara de Material genérico se usado cru — mitigado pelo tema CAM (`mui-theme-cam.md`).
- Bundle maior que alternativas minimalistas — aceitável num cockpit local.
- Emotion/CSS-in-JS exige cuidado com CSP.
- MUI X/Data Grid pode criar dependência de licença se recursos pagos forem usados.

Condição de aprovação:

- Tema CAM obrigatório.
- Overrides globais para densidade, radius, sombras, focus, tipografia e surfaces.
- Imports diretos, sem barrel import de ícones.
- Hardening de CSP e regra contra valores dinâmicos não confiáveis em `sx`.

### 4.3 shadcn/ui

**Veredito:** não adotar como base; manter como exceção controlada.

Pontos fortes: excelente controle visual, Radix oferece primitives acessíveis, bom para prototipagem.

Riscos: modelo copy-paste aumenta divergência; Tailwind utility-first facilita "classe soup"; componentes vendorizados viram responsabilidade interna de patch; agentes tendem a ajustar classes localmente, gerando drift.

### 4.4 Mantine UI

**Veredito:** plano B técnico, sem ganho suficiente para substituir MUI agora.

Boa DX e theming, mas criaria segunda gramática visual e exigiria novo adaptador de tokens. Troca lateral: resolve problemas que MUI já resolve no contexto do cockpit.

### 4.5 DaisyUI

**Veredito:** no-go para o cockpit; aceitável só como protótipo descartável sem dado real.

Tailwind-first conflita com a direção; componentes são classes, não contratos ricos; fraco para formulários, modais e tabelas densas.

---

## 5. Tecnologias complementares

| Tecnologia | Papel |
|---|---|
| React Aria Components | Base headless para componentes customizados críticos (Tier 2) |
| Storybook | Showcase vivo, exemplos canônicos, regressão visual, apoio a agentes |
| Style Dictionary | Gerar tokens para CSS variables, tema MUI e docs |
| Axe/Lighthouse | Auditoria automatizada de acessibilidade |

---

## 6. Framework frontend

O cockpit é uma **SPA local web-only**: React 19 + Vite. **Não usa Next.js** (sem SSR, sem multi-tenant, sem BFF público) e **não tem frontend mobile nativo**.

Recomendação: não abrir o leque de frameworks. Cada framework adicional aumenta superfície para humanos, agentes, testes, segurança e documentação — custo injustificado num cockpit de um único operador.

---

## 7. Arquitetura recomendada do Design System

MUI é a implementação, não a identidade. O contrato (tokens + tema) está acima da biblioteca.

```txt
Design Tokens
  ↓
CAM Theme Adapter
  ↓
UI Foundation
  ↓
Cockpit Components
  ↓
Telas / Features
```

### 7.1 Design Tokens

Fonte: `tokens.md`. Evolução recomendada: `tokens.json` machine-readable, CSS variables, tema MUI, documentação gerada.

### 7.2 CAM Theme Adapter

Responsabilidade:

- mapear tokens para MUI;
- expor `createCamTheme('dark' | 'light')` (ver `mui-theme-cam.md`);
- centralizar `palette`, `typography`, `spacing`, `shape`, `surface` e overrides;
- impedir hex solto.

Estrutura sugerida:

```txt
src/theme/
├── tokens.ts
├── create-cam-theme.ts
├── palette.ts
├── typography.ts
├── components.ts
├── surfaces.ts
└── index.ts
```

### 7.3 UI Foundation

Criar componentes CAM apenas quando houver regra repetida, segurança, acessibilidade ou defesa de capital.

Componentes prováveis (alinhados à Constituição):

- `CamThemeProvider`
- `AppShell`
- `PageHeader`
- `ModeBanner` (DEMO/REAL — Art. 19º)
- `KillSwitch` (Art. 18º)
- `RiskBlockBanner` (Art. 15º)
- `NetResultDisplay` (resultado líquido — Art. 25º)
- `ConfirmDialog` (ações destrutivas)
- `StatusChip`

Regra: não criar wrapper para tudo. Wrapper universal demais vira uma segunda biblioteca mal mantida.

---

## 8. Hardening security-first

### 8.1 Regras obrigatórias

- Nunca expor segredos ao client; o cockpit é local, mas o backend FastAPI guarda credenciais e estado fiscal.
- Nunca usar `dangerouslySetInnerHTML` em componente DS sem ADR, sanitização allowlist e testes XSS.
- Nunca usar valor vindo de backend/IA direto em `sx`, `style`, classe dinâmica ou `backgroundImage`.
- Links externos com `target="_blank"` exigem `rel="noopener noreferrer"` e validação de protocolo.
- Formulários: Zod no client e validação no backend.
- Tabelas: paginação quando volume alto; nunca expor dados além do necessário.
- Dependência nova exige justificativa, lockfile, SCA e revisão.
- **A IA nunca executa ordem nem desabilita o Risk Engine pela UI** (Arts. 35º).

### 8.2 CSP e CSS-in-JS

MUI com Emotion exige política explícita. Evitar liberar `unsafe-inline` como solução fácil.

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{nonce}';
  style-src 'self' 'nonce-{nonce}';
  img-src 'self' data:;
  font-src 'self';
  connect-src 'self';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

### 8.3 Red flags de bloqueio

- DaisyUI como base do cockpit.
- shadcn/Tailwind novo sem ADR.
- CSP relaxada sem justificativa.
- Focus ring removido.
- Modal sem focus trap.
- Kill switch / ação destrutiva sem confirmação.
- Resultado bruto exibido no lugar do líquido (viola Art. 25º).
- UI que permita bypass do Risk Engine (viola Arts. 15º, 35º).
- Pacote visual abandonado ou com alta/crítica em SCA sem triagem.

---

## 9. PoC recomendada para showcase do cockpit

Para validar a decisão com evidência, o showcase deve conter as telas do cockpit em MUI + tema CAM.

### 9.1 Telas de referência

1. Acesso (login local).
2. Dashboard operacional com cards de resultado **líquido**.
3. Journal / ledger com filtros e paginação.
4. Formulário denso (parâmetros) com React Hook Form + Zod.
5. Modal de confirmação destrutiva (kill switch).
6. Layout com sidebar/topbar + banner DEMO/REAL.
7. Estado de bloqueio do Risk Engine.
8. Dark/light toggle.

### 9.2 Métricas de aceitação

- Lighthouse accessibility >= 95.
- Sem violações críticas no axe.
- Nenhum componente sem focus visível.
- Nenhum texto abaixo de 12px.
- Nenhum hex solto fora do tema.
- Nenhum import proibido.
- Resultado sempre líquido (Art. 25º).
- Kill switch acessível em todas as telas operacionais (Art. 18º).

Pergunta central da PoC:

> Qual stack produz a menor variância de resultado quando humanos e agentes diferentes implementam telas do cockpit, sem comprometer a defesa de capital?

Nesse critério, a recomendação multi-persona é que **MUI vence**.

---

## 10. Plano de governança recomendado

1. Formalizar ADR: `Padronizar MUI como implementação do Design System do cockpit CaM`.
2. Criar `CamThemeProvider` e `createCamTheme`.
3. Criar `tokens.json` e pipeline de tokens para o tema MUI.
4. Criar showcase do DS com Storybook ou catálogo equivalente.
5. Exigir ADR para shadcn, Mantine, DaisyUI, Tailwind, Radix direto ou outra UI lib.
6. Adicionar checklist security-first/a11y + defesa de capital em PRs frontend.

---

## 11. Conclusão

A decisão não é "MUI porque sim". É:

> **MUI como implementação porque reduz fragmentação, favorece UX operacional consistente, é governável por agentes, tem maturidade enterprise e pode ser endurecido para security-first — tudo a serviço da defesa de capital do cockpit.**

As outras UIs continuam no radar com papéis claros:

- **shadcn/ui:** inspiração visual ou exceção custom-first.
- **Mantine UI:** plano B técnico se MUI falhar em critérios objetivos.
- **DaisyUI:** protótipo descartável, nunca cockpit.
- **React Aria:** base headless para componentes críticos (exceção técnica).

Frase de direção:

> O cockpit CaM deve ter **um Design System**, **uma linguagem visual** e **uma biblioteca**. Outras UIs podem ser laboratório. Não podem ser identidade.

# Layout System — Cockpit CaM

> Documento técnico e prescritivo para padronização estrutural das telas do cockpit.
> Utilizado por humanos e agentes de IA para construção e refatoração de layouts.
> Stack alvo: React 19 + Vite + MUI (@mui/material) — ver `../../project/STACK-CAM-OFICIAL.md`.

---

## 1. Princípios de Layout

### 1.1 Hierarquia Clara
Toda página deve deixar evidente: o que é mais importante, o que é secundário, o que é ação.

### 1.2 Consistência Estrutural
Layouts similares seguem a mesma estrutura base.

### 1.3 Densidade Controlada
A interface suporta alta densidade de informação sem perder legibilidade.

### 1.4 Responsividade Funcional
A adaptação para mobile preserva intenção, não apenas quebra layout.

### 1.5 Previsibilidade
Usuário e IA devem conseguir prever onde cada elemento estará.

---

## 2. Layout Primitives

### 2.1 Container
Define limites horizontais do conteúdo.

| Variante | Classe | Uso |
|---|---|---|
| `container-narrow` | `maxWidth: 672` | Formulários, wizards |
| `container-default` | `maxWidth: 1024` | Páginas padrão |
| `container-wide` | `maxWidth: 1280` | Dashboards |
| `container-full` | `width: '100%'` | Tabelas, workspaces |

- NÃO usar largura arbitrária — sempre escolher uma variante

### 2.2 Stack (Vertical Layout)
Empilhamento vertical: `<Stack direction="column">`.

| Escala | Token | Uso |
|---|---|---|
| Compacto | `spacing={1}` (8px) | Entre ícone e texto, dentro de grupos |
| Padrão | `spacing={2}` (16px) | Entre itens de lista, campos de formulário |
| Seção | `spacing={3}` (24px) | Entre blocos lógicos, padding do AppShell |
| Macro | `gap-8` | Entre grandes seções de conteúdo |

### 2.3 Inline (Horizontal Layout)
Elementos em linha: `flex items-center`.
- Alinhamento padrão: center
- Gap consistente: `gap-2` ou `gap-3`

### 2.4 Grid
Para layouts complexos.
- Desktop: `grid-cols-12` quando necessário
- Mobile: `grid-cols-4`
- NÃO usar grid para layouts simples — preferir flex

### 2.5 Section
Bloco lógico da página.
- Espaçamento vertical consistente: `space-y-6` ou `space-y-8`

### 2.6 Surface Region
Define camadas visuais (baseado no Design System).
- `background` → `surface-1 (card)` → `surface-2 (muted)` → `surface-3 (hover)`
- Não misturar múltiplas superfícies sem hierarquia

### 2.7 Scroll Region
Área com scroll independente. Uso: tabelas, listas longas, side panels.

### 2.8 Split Pane
Layout dividido (lista + detalhe, editor + preview).
- Flex horizontal com proporção definida (ex: 30/70)

---

## 3. Shells (Estrutura Global)

### 3.1 AppShell (Padrão Principal)

Toda aplicação autenticada segue esta estrutura:

```
┌─────────────────────────────────────────┐
│ Header (h-14, full-width)               │
├──────────┬──────────────────────────────┤
│ Sidebar  │ Content Area                 │
│ (w-52    │ (flex-1, overflow-y-auto)    │
│  ou w-14)│                              │
└──────────┴──────────────────────────────┘
```

**Estrutura CSS:**
```
flex flex-col h-screen overflow-hidden
├── Header (shrink-0)
└── div.flex.flex-1.overflow-hidden
    ├── Sidebar (shrink-0, desktop-only)
    └── main (flex-1, overflow-y-auto, p-4 md:p-6)
```

**Especificações do AppShell:**

| Componente | Posição | Dimensões |
|---|---|---|
| Header | Topo, full-width, no fluxo flex | `h-14` (56px) |
| Sidebar (expandido) | Lateral esquerda, abaixo do header | `w-52` (208px) |
| Sidebar (colapsado) | Lateral esquerda, abaixo do header | `w-14` (56px) |
| Content Area | À direita do sidebar | `flex-1`, scroll em `overflow-y-auto` |

**Regras:**
- Header é full-width — sidebar NÃO afeta a largura do header ao colapsar
- Scroll vertical ocorre apenas na Content Area
- Header e Sidebar são estáticos — não scrollam
- Content padding: `p-4` (mobile) / `p-6` (desktop via `md:p-6`)

**Defesa de capital no AppShell (lente Don):**
- O Header de telas operacionais exibe o **banner de modo DEMO/REAL** sempre visível (Art. 19º) e dá acesso ao **kill switch** sem fricção (Art. 18º).
- Estado de **bloqueio do Risk Engine** (Art. 15º) é comunicado de forma inequívoca, acima do conteúdo (banner persistente).

### 3.2 AuthShell
Para login, cadastro, reset de senha.
- Layout centralizado (`flex items-center justify-center min-h-screen`)
- Card único com foco total

### 3.3 FocusShell
Para wizards e fluxos críticos.
- Remover distrações (sidebar opcional)
- Centralizar conteúdo

### 3.4 EmptyShell
Para erro global, manutenção, fallback.

---

## 4. Page Templates

### 4.1 Dashboard Page
```
PageHeader
├── Grid de métricas (grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4)
├── Bloco principal (gráfico/tabela)
└── Seções secundárias
```
- Card de métrica: `bgcolor: 'background.paper'`, `border: 1, borderColor: 'divider'`, `p: 2`, `borderRadius: 3`
- Priorizar leitura rápida
- **Métricas de resultado sempre líquidas** de imposto provisionado (Art. 25º); ganho/loss com cor funcional + ícone + texto

### 4.2 List Page
```
PageHeader
├── Toolbar (filtros + ações)
└── Lista ou tabela
```
- Toolbar sempre acima da lista, filtros agrupados, ações à direita
- Header de tabela: `bgcolor: 'action.hover'`, Typography variant="caption" fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em'
- Linhas: `borderBottom: 1, borderColor: 'divider'`, hover `bgcolor: 'action.hover'`, `transition: 'background-color 150ms'`

### 4.3 Detail Page
```
PageHeader
├── Conteúdo principal
├── Seções (cards)
└── Aside (opcional — info secundária)
```

### 4.4 Form Page
```
PageHeader
├── FormContainer
└── Ações (submit/cancel)
```
- Máximo 2 colunas, padrão 1 coluna
- Labels obrigatórios

### 4.5 Wizard Page
```
Stepper
├── Conteúdo da etapa
└── Navegação (next/back)
```
- Foco total, sem distrações externas

### 4.6 Workspace Page (Alta Densidade)
```
Header contextual
├── Área principal
└── Painel secundário (opcional)
```
- Para editores, revisão, engenharia

---

## 5. Page Anatomy

Toda página na Content Area segue esta anatomia:

```
Breadcrumb
├── PageHeader (título + descrição + ações)
├── PageToolbar (filtros, busca — opcional)
├── PageContent (conteúdo principal)
├── PageAside (info secundária — opcional)
└── PageFooterActions (paginação — opcional)
```

### PageHeader (Componente)
```tsx
<Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
  <Box>
    <Typography variant="h5" sx={{ fontFamily: 'Poppins', fontWeight: 600, letterSpacing: '-0.02em' }}>
      Título
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Descrição curta.
    </Typography>
  </Box>
  <Box>{/* Botões de ação */}</Box>
</Box>
```

---

## 6. Espaçamento e Ritmo

### Regras Globais

| Contexto | Token | Valor |
|---|---|---|
| Dentro de componente | `gap-2` / `gap-3` | 8px / 12px |
| Entre elementos relacionados | `gap-4` | 16px |
| Entre seções | `gap-6` | 24px |
| Entre blocos principais | `gap-8` | 32px |

**Proibido:** valores arbitrários fora da escala de 4px.

---

## 7. Responsividade

### Breakpoints

| Nome | Valor | Uso |
|---|---|---|
| Mobile | `< 768px` | Single-column, sidebar oculto |
| Desktop | `≥ 768px` (`md:`) | Sidebar visível, multi-column |
| Desktop largo | `≥ 1024px` (`lg:`) | Grids expandidos |
| Desktop extra | `≥ 1280px` (`xl:`) | Dashboards, 4+ colunas |

### Comportamento

| Componente | Mobile | Desktop |
|---|---|---|
| Sidebar | Drawer (Sheet) | Fixo (expandido/colapsado) |
| Toolbar | Empilha verticalmente | Em linha |
| Grid | Colapsa progressivamente | Layout completo |
| Tabelas | Scroll horizontal | Layout normal |
| Content padding | `p-4` | `p-6` |

---

## 8. Densidade

| Modo | Uso | Espaçamento |
|---|---|---|
| Cozy | Onboarding, formulários simples | `spacing: 3`, `p: 3` |
| Default | Uso geral | `spacing: 2`, `p: 2` |
| Dense | Tabelas, dashboards, operações | `spacing: 1`, Typography variant="body2" |

Definir densidade por página.

---

## 9. Interaction Patterns

### 9.1 Loading (Skeletons)
- Skeleton espelha a forma final do componente (ex: `<Skeleton variant="rounded" height={40} />` para botões)
- Loading granulado por componente — evitar spinners centralizados na tela toda

### 9.2 Feedback de Ações
- **Success:** Toast (MUI Snackbar + Alert) no canto superior direito
- **Critical:** Modal de confirmação (MUI Dialog) com botão `color="error"`

---

## 10. Anti-patterns de Layout

| Proibido | Correção |
|---|---|
| Padding arbitrário | Usar escala 4px |
| Múltiplos containers aninhados sem motivo | Simplificar hierarquia |
| Cards dentro de cards excessivos | Achatar estrutura |
| Formulários com mais de 2 colunas | Máximo 2 colunas |
| Toolbar inflada | Agrupar ações em dropdown |
| Header sem hierarquia clara | Título > Ações > Filtros |
| Width fixa fora dos containers definidos | Usar variantes de container |
| Sombras em dark mode | Usar bordas sutis e tonal shift |

---

## 11. Checklist de Conformidade (IA/Review)

1. [ ] Usa AppShell corretamente?
2. [ ] Existe PageHeader com título + descrição?
3. [ ] Layout segue um template conhecido? (Dashboard, List, Detail, Form, Wizard, Workspace)
4. [ ] Espaçamentos na escala de 4px?
5. [ ] Responsividade implementada?
6. [ ] Densidade consistente na página?
7. [ ] Sem valores arbitrários?
8. [ ] Sidebar não afeta header ao colapsar?
9. [ ] Títulos usam `Poppins` com `letterSpacing: '-0.02em'`?
10. [ ] Sem sombras em dark mode? (Apenas bordas sutis)

---

## 12. Regra Final

Se um layout não pode ser descrito usando primitives + shell + template, ele está incorreto.

---

## 13. Referências

| Documento | Descrição |
|---|---|
| `design-system.md` | Design System consolidado |
| `ui-library.md` | UI Library — MUI como padrão |
| `layout-directive.md` | Diretriz operacional de layout |
| `paleta-cam.md` | Cores e tipografia detalhados |
| `branding-cam.md` | Identidade visual do cockpit |

# Diretriz de Layout — Cockpit CaM

> Documento operacional de layout para o frontend do cockpit CaM.
> Escopo: telas do cockpit (operacionais, consulta, configuração). O cockpit é **single-operator** (Carlos) — sem multi-tenant, sem cadastro público.
> Stack: React 19 + Vite + MUI (`../../project/STACK-CAM-OFICIAL.md`).

---

## 1. Princípios de Layout

- **Responsivo sempre** — toda página funciona em mobile, tablet e desktop
- **Dark Mode First** — layout nasce no tema escuro e adapta para claro
- **Consistência** — todas as aplicações web seguem esta diretriz
- **Simplicidade funcional** — estruturas claras, previsíveis, sem decoração
- **Acessibilidade** — WCAG AA obrigatório, foco visível, contraste adequado

---

## 2. Páginas de Acesso (Login local, Sorry Pages)

> O cockpit é local e single-operator: há autenticação de acesso ao cockpit, mas **sem cadastro público, sem multi-tenant**.

### 2.1 Estrutura

Layout centrado, card único, foco total.

```
Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}
└── Card sx={{ maxWidth: 384, p: 3, borderRadius: 3 }}
    ├── Wordmark CaM (centralizado)
    ├── Divider
    ├── Typography variant="h5" (fontWeight: 700, letterSpacing: '-0.02em', textAlign: 'center')
    ├── Typography variant="body2" (textAlign: 'center', color: 'text.secondary')
    ├── Conteúdo/Form
    └── Button fullWidth + Link secundário
```

### 2.2 Wordmark (Branding)

Enquanto não houver logo vetorial:
- **`CaM`** — `C` e `M` em cor `foreground`; `a` em acento `primary` (Esmeralda CAM, `#059669`)
- Tipografia: Poppins, semibold 600, fontSize: 24px (1.5rem)
- Posição: primeiro elemento do CardHeader, centralizado

### 2.3 Sorry Pages

- Card (maxWidth: 448px)
- Ícone centralizado (64×64px, color: `warning.main`)
- Identificação obrigatória: `CaM — v{X.Y.Z}` em Typography variant="caption" color="text.secondary"

---

## 3. Layout Principal (Pós-Login)

### 3.1 Estrutura Macro

```
┌──────────────────────────────────────────────────────┐
│ HEADER (full-width, height: 56px)                    │
├──────────┬───────────────────────────────────────────┤
│ SIDEBAR  │ CONTENT AREA                              │
│          │ Breadcrumb → Título → Ações → Conteúdo    │
└──────────┴───────────────────────────────────────────┘
```

### 3.2 AppShell (Contêiner Raiz)

```tsx
<Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
  <ModeBanner />        {/* DEMO / REAL — sempre visível em telas operacionais (Art. 19º) */}
  <RiskBlockBanner />   {/* condicional — bloqueio do Risk Engine (Art. 15º) */}
  <Header />            {/* inclui acesso ao kill switch (Art. 18º) */}
  <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
    <Sidebar />
    <Box component="main" sx={{ flex: 1, overflowY: 'auto', p: { xs: 2, md: 3 } }}>
      <Breadcrumb />
      {children}
    </Box>
  </Box>
</Box>
```

---

## 4. Header (Topbar)

| Propriedade | Valor |
|---|---|
| Altura | 56px (`height: 56`) |
| Fundo | `theme.palette.background.default` |
| Borda inferior | `borderBottom: 1, borderColor: 'divider'` |
| Layout | `display: 'flex', alignItems: 'center', justifyContent: 'space-between'` |
| Padding | 16px (`px: 2`) |

### Desktop (≥768px)

| Posição | Conteúdo |
|---|---|
| Esquerda | Wordmark CaM (ícone + texto) |
| Centro | Banner de modo **DEMO / REAL** (Art. 19º) + estado do Risk Engine |
| Direita | Kill switch (Art. 18º) + ThemeToggle + UserMenu |

### Mobile (<768px)

| Posição | Conteúdo |
|---|---|
| Esquerda | Botão ☰ (abre sidebar Sheet) |
| Centro | Logo centralizado |
| Direita | Avatar (UserMenu) |

---

## 5. User Menu

### 5.1 Trigger

- Avatar circular (32×32px, `bgcolor: 'primary.main'`, `color: 'primary.contrastText'`) com iniciais (máx. 2 chars)
- Desktop: avatar + nome
- Mobile: apenas avatar

### 5.2 Dropdown

Estrutura base do cockpit (single-operator):

```
┌────────────────────────────┐
│ 👤 Operador (Carlos)       │
├────────────────────────────┤
│ 📊 Estado da sessão        │
│ ⚙️ Configurações            │
├────────────────────────────┤
│ 🚪 Sair                    │  destructive
└────────────────────────────┘
```

> Sem troca de tenant, sem gestão de usuários/times — o cockpit é de um único operador.

| Regra | Valor |
|---|---|
| Largura | 224px (`width: 224`) |
| Alinhamento | `align="end"` |
| Separadores | Entre seções lógicas |
| Logout | Variante `destructive` |

---

## 6. Sidebar (Menu Lateral)

### 6.1 Especificações

| Propriedade | Valor |
|---|---|
| Fundo | `theme.palette.background.paper` (sidebar) |
| Borda | `borderRight: 1, borderColor: 'divider'` |
| Transição | `transition: 'all 300ms ease-in-out'` |
| Desktop | Sempre visível (expandido/colapsado) |
| Mobile | Sheet (drawer lateral esquerdo) |

### 6.2 Estados

| Estado | Largura | Itens | Detalhe |
|---|---|---|---|
| Expandido | 208px | Ícone + label | `px: 1, pt: 1` |
| Colapsado | 56px | Apenas ícone | Centrado, 36×36px, Tooltip placement="right" |
| Mobile | 208px | Ícone + label | MUI Drawer, overlay `rgba(0,0,0,0.5)` |

### 6.3 Botão de Colapso

| Propriedade | Valor |
|---|---|
| Formato | Circular 24×24px |
| Posição | Borda sidebar/content, posição relativa ao container |
| Ícone | `ChevronLeftOutlined` (expandido) / `ChevronRightOutlined` (colapsado) |
| Estilo | `border: 1, bgcolor: 'background.default'`, elevation: 1, opacidade 70% → 100% hover |
| Z-index | `zIndex: 20` |

### 6.4 Itens de Menu

- Item ativo: `bgcolor: 'primary.main'`, `color: 'primary.contrastText'`
- Item inativo: `color: 'text.secondary'`, hover `bgcolor: 'action.hover'`
- Ícones: @mui/icons-material (Outlined), fontSize: 20px
- Máximo 3 níveis (item → subitem → sub-subitem)
- Colapsado + hover: Tooltip com label
- Colapsado + subitens: Popover/flyout ao clicar

### 6.5 Comportamento

- Sidebar colapsando **não afeta** o header — apenas Content Area expande
- Estado gerenciado via Zustand
- Estado persistido em localStorage
- Transição suave: `transition: 'all 300ms'`

---

## 7. Content Area

| Propriedade | Valor |
|---|---|
| Scroll | `overflowY: 'auto'` (independente) |
| Padding | `p: { xs: 2, md: 3 }` (16px / 24px) |
| Fundo | `theme.palette.background.default` (herdado) |

### Estrutura Interna

```
Breadcrumb (marginBottom: 16px)
├── PageHeader (título + descrição + ações)
├── Toolbar / Filtros (opcional)
├── Conteúdo Principal
└── Footer (paginação — opcional)
```

---

## 8. Toasts

| Propriedade | Valor |
|---|---|
| Biblioteca | MUI Snackbar + Alert |
| Posição | `top-right` |
| Duração | ~4 segundos |
| Botão fechar | Habilitado |

| Variante | Uso |
|---|---|
| `success` | Confirmações |
| `info` | Informações neutras |
| `warning` | Avisos |
| `error` | Erros |

- Toasts são temporários — não substituem validação de formulário
- Para confirmações destrutivas, usar Dialog
- Mensagens em PT-BR, claras e concisas

---

## 9. Dialogs

| Propriedade | Valor |
|---|---|
| Biblioteca | MUI Dialog |
| Overlay | `rgba(0,0,0,0.3)` |
| Largura | `maxWidth="sm"` (512px) |
| Padding | 24px (`p: 3`) |
| Border radius | `theme.shape.borderRadius` (8px) |
| Animação | Fade + zoom ~200ms |

- **Todo dialog deve ter botão X** (canto superior direito, `position: 'absolute', top: 16, right: 16`)
- Fechar ao clicar overlay e ao pressionar Escape
- Não empilhar dialogs

---

## 10. Bloqueio do Risk Engine

> Quando o Risk Engine bloqueia, o CaM não opera (Art. 15º). A UI comunica isso de forma inequívoca e impede ações de execução.

| Componente | Especificação |
|---|---|
| Banner | Acima do Header, cores `warning`/`error`, ícone `BlockOutlined` (@mui/icons-material) |
| Mensagem | "Risk Engine bloqueou — operação suspensa." (ou motivo: DARF pendente, Art. 26º; limite atingido, Art. 11º) |
| Ação | Sem botão de bypass — IA/UI não desabilitam o Risk Engine (Art. 35º) |
| Consulta | Permitida (journal, ledger, histórico) |
| Execução de ordem | Bloqueada |

---

## 11. Responsividade

| Componente | Mobile (<768px) | Desktop (≥768px) |
|---|---|---|
| Header | ☰ + Wordmark centro + Avatar | Wordmark esquerda + UserMenu direita |
| Sidebar | Sheet (drawer) | Visível (expandido/colapsado) |
| Content padding | 16px (`p: 2`) | 24px (`p: 3`) |
| Tabelas | Scroll horizontal | Normal |
| Grids | 1 coluna | 2–4 colunas |
| Toolbar | `flexDirection: 'column', gap: 1` | `flexDirection: 'row'` |
| Dialog | Full-width com margem | `maxWidth="sm"` |

---

## 12. Implementação de Referência

O frontend do cockpit ainda está em construção (Fase 0). Quando materializado, viverá em `apps/cam-cockpit/frontend/` conforme a stack oficial (React 19 + Vite + MUI). Estrutura sugerida dos componentes de layout:

| Componente | Caminho sugerido |
|---|---|
| AppShell | `apps/cam-cockpit/frontend/src/shared/layout/AppShell.tsx` |
| Header (com kill switch + banner de modo) | `apps/cam-cockpit/frontend/src/shared/layout/Header.tsx` |
| Sidebar | `apps/cam-cockpit/frontend/src/shared/layout/Sidebar.tsx` |
| ModeBanner (DEMO/REAL) | `apps/cam-cockpit/frontend/src/shared/layout/ModeBanner.tsx` |
| RiskBlockBanner | `apps/cam-cockpit/frontend/src/shared/layout/RiskBlockBanner.tsx` |
| UI Shell Store (Zustand) | `apps/cam-cockpit/frontend/src/shared/stores/uiShellStore.ts` |

> Estado real vence intenção (NCC-1701 §2): ao materializar, este documento é atualizado para refletir os caminhos efetivos.

---

## 13. Checklist de Conformidade

- [ ] Página de acesso centrada com wordmark **CaM** no card
- [ ] Header responsivo (desktop: wordmark esquerda + menu direita; mobile: ☰ + wordmark centro + avatar)
- [ ] Banner de modo **DEMO/REAL** sempre visível em telas operacionais (Art. 19º)
- [ ] Kill switch acessível a partir do Header (Art. 18º)
- [ ] Bloqueio do Risk Engine comunicado de forma inequívoca, sem bypass (Arts. 15º, 35º)
- [ ] UserMenu single-operator (sem troca de tenant)
- [ ] Sidebar expandido (ícone + label) e colapsado (ícone + tooltip)
- [ ] Botão de colapso na borda sidebar/content
- [ ] Sidebar não afeta header ao colapsar
- [ ] Content Area: Breadcrumb → Título → Ações → Conteúdo
- [ ] Resultado exibido líquido de imposto provisionado (Art. 25º)
- [ ] Toasts via MUI Snackbar + Alert em `top-right`
- [ ] Dialogs com overlay, botão X obrigatório
- [ ] WCAG AA em todos os temas
- [ ] Responsivo em todos os breakpoints

---

## 14. Referências

| Documento | Descrição |
|---|---|
| `design-system.md` | Design System consolidado |
| `ui-library.md` | UI Library — MUI como padrão |
| `layout-system.md` | Primitivos, shells e templates |
| `paleta-cam.md` | Cores e tipografia |
| `branding-cam.md` | Identidade visual |
| `../../CONSTITUICAO.md` | Lei suprema — o que o cockpit protege |
| `../../project/STACK-CAM-OFICIAL.md` | Stack oficial do cockpit |

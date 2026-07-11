# UI Library — MUI (Material UI)

> Documento prescritivo sobre a biblioteca de componentes do cockpit CaM.
> MUI (@mui/material) é a **única** biblioteca de componentes aprovada para o frontend do cockpit (React 19 + Vite).
> Para valores atômicos (cores, tipografia, espaçamento): `tokens.md` — Single Source of Truth.
> Para regras visuais e filosofia: `design-system.md`. Para o tema completo: `mui-theme-cam.md`.

---

## 1. Por que MUI

| Critério | Decisão |
|---|---|
| Consistência | Uma biblioteca para todo o cockpit — sem fragmentação |
| Maturidade | MUI tem 10+ anos, componentes enterprise-grade, acessibilidade nativa |
| Theming | Sistema de tema robusto que mapeia diretamente para os tokens do CAM |
| Dark Mode | Suporte nativo com `ThemeProvider` + `CssBaseline` |
| Ecossistema | Data Grid, Date Pickers, Charts — densidade de dados operacionais no mesmo design language |
| Estilização | Emotion embutido, `sx` prop e `styled()` sem dependências externas |

### O que foi depreciado

| Antes | Status | Substituto |
|---|---|---|
| shadcn/ui (Radix primitives) | ❌ Depreciado | MUI (@mui/material) |
| TailwindCSS | ❌ Depreciado | MUI System (`sx` + `styled()`) + Emotion |
| Lucide React | ❌ Depreciado | @mui/icons-material |

---

## 2. Stack Web Universal

| Camada | Tecnologia | Versão Mínima |
|---|---|---|
| Framework | React 19 + Vite (SPA local) | — |
| UI Library | MUI (@mui/material) | 6.x |
| Ícones | @mui/icons-material | — |
| Estilização | MUI System (`sx` prop + `styled()`) + Emotion | — |
| Formulários | React Hook Form + Zod | — |
| Estado servidor | React Query (@tanstack/react-query) | 5.x |
| Estado UI | Zustand | — |

> **Válido para:** o frontend do cockpit CaM (`apps/cam-cockpit/frontend`). Ver `../../project/STACK-CAM-OFICIAL.md`.

---

## 3. Configuração do Tema

### 3.1 Estrutura de Arquivos

```
src/theme/
├── theme.ts           # createTheme() — tema dark + light
├── palette.ts         # Paleta de cores (tokens CAM)
├── typography.ts      # Poppins + Inter
├── components.ts      # Overrides globais de componentes MUI
└── index.ts           # Re-export
```

### 3.2 Tema Base

```typescript
// src/theme/theme.ts
import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#059669',       // Esmeralda CAM
      light: '#34D399',      // Esmeralda Light
      dark: '#047857',       // Esmeralda Core
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#1A1A1A',    // background
      paper: '#1F1F1F',      // surface-1
    },
    success: { main: '#10B981' },
    error: { main: '#EF4444' },
    warning: { main: '#F59E0B' },
    info: { main: '#0EA5E9' },
    divider: 'rgba(255, 255, 255, 0.08)',
  },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h1: { fontFamily: '"Poppins", sans-serif', fontWeight: 600, letterSpacing: '-0.02em' },
    h2: { fontFamily: '"Poppins", sans-serif', fontWeight: 600, letterSpacing: '-0.02em' },
    h3: { fontFamily: '"Poppins", sans-serif', fontWeight: 600, letterSpacing: '-0.01em' },
    h4: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    h5: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    h6: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 500 },
    overline: { letterSpacing: '0.08em' },
  },
  shape: {
    borderRadius: 4,         // Padrão global — botões e inputs
  },
  spacing: 4,                // Base 4px — theme.spacing(1) = 4px
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { scrollbarWidth: 'thin' },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 4 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 6, backgroundImage: 'none' },
      },
    },
    MuiTextField: {
      defaultProps: { variant: 'outlined', size: 'small' },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 4 },
      },
    },
  },
});
```

### 3.3 Border Radius

| Componente | Valor | Token |
|---|---|---|
| Botões | 4px | `shape.borderRadius` (padrão) |
| Inputs | 4px | `shape.borderRadius` (padrão) |
| Cards | 6px | Override em `MuiCard` |
| Chips / Badges | 4px | Override em `MuiChip` |

**Proibido:** `borderRadius: '9999px'` ou equivalente a pills — a identidade do cockpit é prática, não amigável.

---

## 4. Ícones

### 4.1 Biblioteca

`@mui/icons-material` — única biblioteca de ícones aprovada para web.

### 4.2 Variantes

| Variante | Quando usar |
|---|---|
| **Outlined** | Padrão para toda a interface |
| **Filled** | Apenas ícone de navegação no estado **ativo** |
| Rounded, Sharp, TwoTone | ❌ Proibidos |

### 4.3 Importação

```tsx
// ✅ Correto — named import do ícone específico
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import HomeIcon from '@mui/icons-material/Home'; // Filled — nav ativo

// ❌ Proibido — import barrel (aumenta bundle)
import { Search } from '@mui/icons-material';
```

### 4.4 Tamanhos

| Prop `fontSize` | Pixels | Uso |
|---|---|---|
| `"small"` | 20px | Inline em texto, badges, botões compactos |
| `"medium"` | 24px | Padrão — nav, listas, inputs |
| `"large"` | 35px | Feature cards, hero sections |
| `"inherit"` | — | Adapta ao contexto tipográfico |

---

## 5. Estilização

### 5.1 Hierarquia de Mecanismos

Ordem de preferência — usar o mecanismo mais simples que resolve:

1. **Props do componente MUI** — `variant`, `color`, `size`, `fullWidth`
2. **`sx` prop** — overrides pontuais em instância única (1–3 props)
3. **`styled()`** — componente reutilizado 3+ vezes
4. **Theme overrides** — padrão global para todos os usos de um componente

### 5.2 `sx` Prop — Regras

```tsx
// ✅ 1–3 props — adequado para sx
<Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>

// ✅ Usar tokens do tema
<Typography sx={{ color: 'text.secondary', mb: 1 }}>

// ❌ Hex solto — usar token
<Box sx={{ color: '#059669' }}>           // PROIBIDO
<Box sx={{ color: 'primary.main' }}>      // ✅ Correto

// ❌ Muitas props — extrair para styled()
<Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 3, borderRadius: 2, bgcolor: 'background.paper', border: 1, borderColor: 'divider' }}>
```

### 5.3 `styled()` — Regras

```tsx
import { styled } from '@mui/material/styles';

// ✅ Componente reutilizado 3+ vezes
const SectionCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(6),
  borderRadius: 6,
  border: `1px solid ${theme.palette.divider}`,
}));
```

### 5.4 Proibições de Estilização

| Proibido | Motivo | Alternativa |
|---|---|---|
| `style={{...}}` inline | Não participa do tema | `sx` prop |
| CSS Modules | Stack não aprovada | MUI System |
| TailwindCSS | Stack não aprovada | MUI System |
| Styled Components (lib) | Conflita com Emotion | `styled()` do MUI (Emotion) |
| Hex solto no `sx` | Tokens devem vir do tema | `theme.palette.*` ou string shorthand |
| `!important` | Indica arquitetura ruim | Revisar especificidade |
| Classes CSS manuais | Não participa do tema | `sx` ou `styled()` |

---

## 6. Componentes Essenciais

### 6.1 Mapeamento por Caso de Uso

| Caso de Uso | Componente MUI |
|---|---|
| Navegação lateral | `Drawer` (permanent ou responsive) |
| Top bar | `AppBar` + `Toolbar` |
| Tabelas de dados | `DataGrid` (@mui/x-data-grid) |
| Formulários | `TextField`, `Select`, `Autocomplete`, `Switch` |
| Modais / diálogos | `Dialog` + `DialogTitle` + `DialogContent` + `DialogActions` |
| Cards informativos | `Card` + `CardContent` + `CardActions` |
| Feedback | `Alert`, `Snackbar` |
| Loading | `Skeleton`, `CircularProgress`, `LinearProgress` |
| Navegação por abas | `Tabs` + `Tab` |
| Status / tags | `Chip` |
| Seleção de data | `DatePicker` (@mui/x-date-pickers) |
| Menu de ações | `Menu` + `MenuItem` |
| Listas | `List` + `ListItem` + `ListItemText` + `ListItemIcon` |
| Empty states | Composição customizada (ícone + Typography + Button) |
| Breadcrumbs | `Breadcrumbs` + `Link` |

### 6.2 Regras de Uso

- Usar componentes MUI **nativamente** — sem wrappers desnecessários
- Criar wrappers apenas quando há lógica de negócio envolvida (ex: `ProtectedAction`)
- Preferir composição MUI (`Stack`, `Box`, `Grid`) sobre `div` + estilos manuais
- `Typography` obrigatório para textos — nunca `<p>`, `<h1>` etc. diretamente

---

## 7. Integração com Vite (SPA)

> O cockpit CaM é uma SPA local React 19 + Vite. **Não usa Next.js** — sem SSR, sem cache provider.

### 7.1 Dependências

```bash
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
```

### 7.2 App Root

```typescript
// src/App.tsx
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { camDarkTheme } from '@/theme';

export default function App() {
  return (
    <ThemeProvider theme={camDarkTheme}>
      <CssBaseline />
      {/* Router, QueryClientProvider, etc. */}
    </ThemeProvider>
  );
}
```

---

## 9. Dark Mode

### 9.1 Estratégia

- **Padrão: dark** — toda interface nasce escura
- Toggle permite mudar para light
- Persistir preferência em `localStorage`
- Fallback para `prefers-color-scheme` do sistema

### 9.2 Implementação

```typescript
// Hook de toggle
const [mode, setMode] = useState<'dark' | 'light'>('dark');

const theme = useMemo(() => createTheme({
  palette: { mode },
  // ... restante do tema
}), [mode]);
```

### 9.3 Regras Dark Mode

| Regra | Detalhe |
|---|---|
| Sem sombras em dark mode | Usar bordas sutis (`divider`) e variação de superfície |
| Sem `#000000` absoluto | Causa "smearing" em OLED — usar deep charcoals (`#1A1A1A`) |
| Bordas sutis | `rgba(255,255,255, 0.08–0.15)` para separar superfícies |
| Textos sobre escuro | 100% branco (títulos), 90% (subtítulos), 70–80% (parágrafos) |

---

## 10. Proibições

| Proibido | Motivo |
|---|---|
| shadcn/ui | Depreciado — usar MUI |
| Radix UI | Depreciado — MUI já inclui primitives acessíveis |
| TailwindCSS | Stack não aprovada — usar MUI System |
| CSS Modules | Stack não aprovada |
| Styled Components (lib) | Conflita com Emotion embutido no MUI |
| Lucide React | Depreciado — usar @mui/icons-material |
| Font Awesome | Não aprovado — usar @mui/icons-material |
| Heroicons | Não aprovado — usar @mui/icons-material |
| Ant Design | Não aprovado — usar MUI |
| Chakra UI | Não aprovado — usar MUI |
| Ícones Rounded / Sharp / TwoTone | Usar apenas Outlined (padrão) e Filled (nav ativo) |
| `borderRadius: '9999px'` (pills) | Identidade do cockpit: prática, não amigável |
| Hex solto no `sx` | Usar `theme.palette.*` |
| `style={{...}}` inline | Usar `sx` prop |

---

## Referências

| Documento | Descrição |
|---|---|
| [`tokens.md`](tokens.md) | Design Tokens — Single Source of Truth |
| [`design-system.md`](design-system.md) | Design System completo |
| [`mui-theme-cam.md`](mui-theme-cam.md) | Especificação do tema MUI do cockpit |
| [`layout-system.md`](layout-system.md) | Sistema de layout |
| [`layout-directive.md`](layout-directive.md) | Padrões de telas |
| [`paleta-cam.md`](paleta-cam.md) | Filosofia de cor |
| `../../project/STACK-CAM-OFICIAL.md` | Stack oficial do cockpit (React 19 + Vite) |

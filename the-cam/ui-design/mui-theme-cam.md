# Tema MUI — Cockpit CaM

> **Especificação prescritiva** do tema Material UI (MUI) para o frontend do cockpit CaM (React 19 + Vite).
> Versão: 1.0 | Autor: Andy (Design & Advertising) | Aprovação: Founder
> SSoT de tokens: `tokens.md`. SSoT de filosofia visual: `design-system.md`.

---

## Decisão Arquitetural

| Item | Valor |
|---|---|
| Biblioteca de componentes | **Material UI (MUI) v6+** — obrigatória |
| Ícones | **@mui/icons-material** (variante `Outlined` como padrão) |
| Estilização | **MUI System** (`sx` prop) + `styled()` (Emotion) |
| Tailwind CSS | **DEPRECIADO** — proibido em projetos novos |
| shadcn/ui | **DEPRECIADO** — proibido em projetos novos |
| Lucide React | **DEPRECIADO** — substituído por `@mui/icons-material` |

---

## 1. Mapeamento de Tokens → `createTheme`

### 1.1 Palette

```tsx
import { createTheme, type ThemeOptions } from '@mui/material/styles';

// ─── Tokens CAM ───
const tokens = {
  primary:      '#059669',
  primaryDark:  '#047857',
  primaryLight: '#34D399',

  info:         '#0EA5E9',
  success:      '#10B981',
  error:        '#EF4444',
  warning:      '#F59E0B',

  accentPurple: '#8B5CF6',
  accentPink:   '#EC4899',
  accentTeal:   '#0D9488',
} as const;

const darkPalette = {
  mode: 'dark' as const,
  primary:    { main: tokens.primary, dark: tokens.primaryDark, light: tokens.primaryLight, contrastText: '#FFFFFF' },
  secondary:  { main: '#2C2C2C', light: '#3A3A3A', dark: '#1F1F1F', contrastText: '#FFFFFF' },
  error:      { main: tokens.error,   contrastText: '#FFFFFF' },
  warning:    { main: tokens.warning,  contrastText: '#1A1A1A' },
  info:       { main: tokens.info,     contrastText: '#FFFFFF' },
  success:    { main: tokens.success,  contrastText: '#FFFFFF' },
  background: { default: '#1A1A1A', paper: '#1F1F1F' },
  text:       { primary: '#FFFFFF', secondary: 'rgba(255,255,255,0.70)', disabled: 'rgba(255,255,255,0.38)' },
  divider:    'rgba(255,255,255,0.10)',
  action: {
    hover:    'rgba(255,255,255,0.05)',
    selected: 'rgba(5,150,105,0.12)',
    focus:    'rgba(16,185,129,0.20)',
  },
};

const lightPalette = {
  mode: 'light' as const,
  primary:    { main: tokens.primary, dark: tokens.primaryDark, light: tokens.primaryLight, contrastText: '#FFFFFF' },
  secondary:  { main: '#F0F0F0', light: '#F7F7F7', dark: '#E5E5E5', contrastText: '#1F1F1F' },
  error:      { main: tokens.error,   contrastText: '#FFFFFF' },
  warning:    { main: tokens.warning,  contrastText: '#1A1A1A' },
  info:       { main: tokens.info,     contrastText: '#FFFFFF' },
  success:    { main: tokens.success,  contrastText: '#FFFFFF' },
  background: { default: '#F7F7F7', paper: '#FFFFFF' },
  text:       { primary: '#1F1F1F', secondary: '#4A4A4A', disabled: 'rgba(0,0,0,0.38)' },
  divider:    '#D9D9D9',
  action: {
    hover:    'rgba(0,0,0,0.04)',
    selected: 'rgba(5,150,105,0.08)',
    focus:    'rgba(16,185,129,0.16)',
  },
};
```

#### Superfícies Customizadas (Custom Palette)

MUI não possui tokens nativos para surface hierarchy. Estender via `declare module`:

```tsx
// types/mui-theme.d.ts
declare module '@mui/material/styles' {
  interface Palette {
    surface: {
      s1: string;  // Cards, sidebar
      s2: string;  // Inputs, dropdowns
      s3: string;  // Hover states
      elevated: string;  // Modais, tooltips
    };
    accent: {
      purple: string;
      pink: string;
      teal: string;
    };
  }
  interface PaletteOptions {
    surface?: {
      s1?: string;
      s2?: string;
      s3?: string;
      elevated?: string;
    };
    accent?: {
      purple?: string;
      pink?: string;
      teal?: string;
    };
  }
}
```

Valores por tema:

```tsx
// Dark
surface: { s1: '#1F1F1F', s2: '#2C2C2C', s3: '#3A3A3A', elevated: '#444444' },
accent:  { purple: '#8B5CF6', pink: '#EC4899', teal: '#0D9488' },

// Light
surface: { s1: '#FFFFFF', s2: '#F0F0F0', s3: '#E5E5E5', elevated: '#FFFFFF' },
accent:  { purple: '#8B5CF6', pink: '#EC4899', teal: '#0D9488' },
```

---

### 1.2 Typography

```tsx
const typography: ThemeOptions['typography'] = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',

  // ─── Headings (Poppins 600) ───
  h1: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '2.625rem',   // 42px
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },
  h2: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '2rem',       // 32px
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },
  h3: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '1.5rem',     // 24px
    lineHeight: 1.3,
    letterSpacing: '-0.01em',
  },
  h4: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '1.25rem',    // 20px
    lineHeight: 1.3,
  },
  h5: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '1.125rem',   // 18px
    lineHeight: 1.4,
  },
  h6: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '1rem',       // 16px
    lineHeight: 1.4,
  },

  // ─── Body (Inter 400) ───
  body1: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 400,
    fontSize: '1rem',       // 16px — text-body
    lineHeight: 1.6,
  },
  body2: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 400,
    fontSize: '0.875rem',   // 14px — text-dense
    lineHeight: 1.4,
  },
  subtitle1: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 500,
    fontSize: '1rem',       // 16px — labels enfatizados
    lineHeight: 1.4,
  },
  subtitle2: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 500,
    fontSize: '0.8125rem',  // 13px — text-small
    lineHeight: 1.4,
  },
  caption: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 400,
    fontSize: '0.75rem',    // 12px — text-caption (mínimo absoluto)
    lineHeight: 1.4,
  },
  overline: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 600,
    fontSize: '0.6875rem',  // 11px (exceção: APENAS overline decorativo)
    lineHeight: 1.4,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
  button: {
    fontFamily: '"Inter", sans-serif',
    fontWeight: 500,
    fontSize: '0.875rem',   // 14px
    lineHeight: 1.4,
    textTransform: 'none',  // OBRIGATÓRIO — MUI usa uppercase por padrão
  },
};
```

#### Mapeamento Completo de Tokens

| Token CAM | MUI Variant | Tamanho | Fonte |
|---|---|---|---|
| `text-display` | Variante custom `display` (ver abaixo) | 48px / 3rem | Poppins 600 |
| `text-h1` | `h1` | 42px / 2.625rem | Poppins 600 |
| `text-h2` | `h2` | 32px / 2rem | Poppins 600 |
| `text-h3` | `h3` | 24px / 1.5rem | Poppins 600 |
| `text-body` | `body1` | 16px / 1rem | Inter 400 |
| `text-dense` | `body2` | 14px / 0.875rem | Inter 400 |
| `text-small` | `subtitle2` | 13px / 0.8125rem | Inter 500 |
| `text-caption` | `caption` | 12px / 0.75rem | Inter 400 |

#### Variante Custom: `display`

```tsx
// types/mui-theme.d.ts (adicionar)
declare module '@mui/material/styles' {
  interface TypographyVariants {
    display: React.CSSProperties;
  }
  interface TypographyVariantsOptions {
    display?: React.CSSProperties;
  }
}
declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    display: true;
  }
}

// No tema:
typography: {
  ...typography,
  display: {
    fontFamily: '"Poppins", "Inter", sans-serif',
    fontWeight: 600,
    fontSize: '3rem',       // 48px
    lineHeight: 1.1,
    letterSpacing: '-0.02em',
  },
},
```

---

### 1.3 Spacing

```tsx
// MUI spacing base = 4px (grid CAM)
const spacing = 4;

// Uso:
// theme.spacing(1)  =  4px  →  space-1
// theme.spacing(2)  =  8px  →  space-2
// theme.spacing(3)  = 12px  →  space-3
// theme.spacing(4)  = 16px  →  space-4
// theme.spacing(6)  = 24px  →  space-6
// theme.spacing(8)  = 32px  →  space-8
// theme.spacing(12) = 48px  →  space-12
// theme.spacing(16) = 64px  →  space-16
// theme.spacing(24) = 96px  →  space-24
```

**Regra:** Usar SOMENTE multiplicadores inteiros. Valores como `theme.spacing(1.5)` são **proibidos** (6px não está na escala de 4px). Exceção: `theme.spacing(0.5)` = 2px é permitido apenas para micro-ajustes de alinhamento de ícones.

---

### 1.4 Shape

```tsx
const shape = {
  borderRadius: 4,  // 4px — padrão global (botões, inputs)
};
```

Cards usam 6px via override de componente (seção 2.3).

---

### 1.5 Shadows

```tsx
// Dark mode: array de sombras zerado (tonal layering)
const darkShadows = [
  'none',
  'none', 'none', 'none', 'none', 'none',
  'none', 'none', 'none', 'none', 'none',
  'none', 'none', 'none', 'none', 'none',
  'none', 'none', 'none', 'none', 'none',
  'none', 'none', 'none', 'none',
] as const;

// Light mode: sombras sutis (restrito)
const lightShadows = [
  'none',
  '0px 1px 3px rgba(0,0,0,0.08)',                          // elevation 1 — cards
  '0px 2px 6px rgba(0,0,0,0.10)',                          // elevation 2
  '0px 4px 12px rgba(0,0,0,0.12)',                         // elevation 3
  '0px 6px 16px rgba(0,0,0,0.14)',                         // elevation 4
  ...Array(20).fill('0px 8px 24px rgba(0,0,0,0.16)'),     // elevation 5-24 (cap)
] as const;
```

**Dark mode: 0 sombras.** Profundidade = variação de superfície + bordas sutis.

---

### 1.6 Breakpoints

```tsx
const breakpoints = {
  values: {
    xs: 0,
    sm: 600,
    md: 768,    // CAM: tablet
    lg: 1024,   // CAM: desktop
    xl: 1280,   // CAM: wide
  },
};
```

---

### 1.7 Transitions

```tsx
const transitions = {
  duration: {
    shortest:       150,  // --duration-fast
    shorter:        150,
    short:          200,  // --duration-default
    standard:       200,
    complex:        250,  // --duration-slow
    enteringScreen: 250,
    leavingScreen:  200,
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut:   'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn:    'cubic-bezier(0.4, 0, 1, 1)',
    sharp:     'cubic-bezier(0.4, 0, 0.6, 1)',
  },
};
```

---

## 2. Overrides de Componentes

### 2.1 MuiButton

```tsx
MuiButton: {
  styleOverrides: {
    root: {
      borderRadius: 4,
      textTransform: 'none',
      fontWeight: 500,
      fontSize: '0.875rem',
      padding: '8px 16px',
      transition: 'all 200ms ease',
      '&:active': {
        transform: 'scale(0.98)',
      },
    },
    sizeSmall: {
      padding: '4px 12px',
      fontSize: '0.8125rem',
    },
    sizeLarge: {
      padding: '12px 24px',
      fontSize: '1rem',
    },
    containedPrimary: {
      '&:hover': {
        backgroundColor: '#047857',
      },
    },
  },
  defaultProps: {
    disableElevation: true,  // Sem sombra em botões — brutalismo funcional
    disableRipple: false,
  },
},
```

#### Variantes de Botão → Mapeamento CAM

| CAM | MUI | Props |
|---|---|---|
| Primary | `contained` | `variant="contained" color="primary"` |
| Secondary | `contained` | `variant="contained" color="secondary"` |
| Outline | `outlined` | `variant="outlined" color="primary"` |
| Ghost | `text` | `variant="text"` |
| Destructive | `contained` | `variant="contained" color="error"` |

**Proibido:** `sx={{ borderRadius: '9999px' }}` ou qualquer valor que resulte em pill.

---

### 2.2 MuiTextField / MuiOutlinedInput

```tsx
MuiOutlinedInput: {
  styleOverrides: {
    root: {
      borderRadius: 4,
      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: '#059669',
        borderWidth: 2,
      },
      '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: 'rgba(5,150,105,0.4)',
      },
    },
    notchedOutline: ({ theme }) => ({
      borderColor: theme.palette.divider,
    }),
  },
},
MuiInputLabel: {
  styleOverrides: {
    root: {
      '&.Mui-focused': {
        color: '#059669',
      },
    },
  },
  defaultProps: {
    shrink: true,  // Label sempre visível — obrigatório
  },
},
MuiTextField: {
  defaultProps: {
    variant: 'outlined',
    size: 'small',
    fullWidth: true,
  },
},
```

**Regra:** Todo input deve ter label visível. Proibido: `placeholder` como substituto de label.

---

### 2.3 MuiCard

```tsx
MuiCard: {
  styleOverrides: {
    root: ({ theme }) => ({
      borderRadius: 6,  // Cards = 6px (não 4px)
      padding: theme.spacing(6),  // 24px
      backgroundImage: 'none',    // Remove gradiente MUI padrão
      ...(theme.palette.mode === 'dark'
        ? {
            backgroundColor: theme.palette.background.paper,
            border: '1px solid rgba(255,255,255,0.08)',
            boxShadow: 'none',
            '&:hover': {
              borderColor: 'rgba(5,150,105,0.4)',
            },
          }
        : {
            backgroundColor: theme.palette.background.paper,
            border: '1px solid #E5E5E5',
            boxShadow: '0px 1px 3px rgba(0,0,0,0.08)',
            '&:hover': {
              borderColor: 'rgba(5,150,105,0.4)',
            },
          }
      ),
    }),
  },
},
MuiCardContent: {
  styleOverrides: {
    root: {
      padding: 0,
      '&:last-child': {
        paddingBottom: 0,
      },
    },
  },
},
```

---

### 2.4 MuiChip

```tsx
MuiChip: {
  styleOverrides: {
    root: {
      borderRadius: 4,  // NUNCA pill — brutalismo funcional
      fontWeight: 500,
      fontSize: '0.75rem',
    },
    colorPrimary: {
      backgroundColor: 'rgba(5,150,105,0.15)',
      color: '#059669',
    },
    colorSuccess: {
      backgroundColor: 'rgba(16,185,129,0.15)',
      color: '#10B981',
    },
    colorWarning: {
      backgroundColor: 'rgba(245,158,11,0.15)',
      color: '#F59E0B',
    },
    colorError: {
      backgroundColor: 'rgba(239,68,68,0.15)',
      color: '#EF4444',
    },
    colorInfo: {
      backgroundColor: 'rgba(14,165,233,0.15)',
      color: '#0EA5E9',
    },
  },
  defaultProps: {
    size: 'small',
  },
},
```

---

### 2.5 MuiDialog

```tsx
MuiDialog: {
  styleOverrides: {
    paper: ({ theme }) => ({
      borderRadius: 6,
      backgroundImage: 'none',
      ...(theme.palette.mode === 'dark'
        ? {
            backgroundColor: theme.palette.surface.elevated,
            border: '1px solid rgba(255,255,255,0.10)',
            boxShadow: '0px 20px 40px rgba(0,0,0,0.4)',
          }
        : {
            backgroundColor: '#FFFFFF',
            boxShadow: '0px 20px 40px rgba(0,0,0,0.15)',
          }
      ),
    }),
  },
},
MuiDialogTitle: {
  styleOverrides: {
    root: {
      fontFamily: '"Poppins", "Inter", sans-serif',
      fontWeight: 600,
      fontSize: '1.25rem',
      padding: '24px 24px 16px',
    },
  },
},
```

---

### 2.6 MuiDrawer

```tsx
MuiDrawer: {
  styleOverrides: {
    paper: ({ theme }) => ({
      backgroundImage: 'none',
      ...(theme.palette.mode === 'dark'
        ? {
            backgroundColor: theme.palette.surface.s1,
            borderRight: '1px solid rgba(255,255,255,0.08)',
          }
        : {
            backgroundColor: '#FFFFFF',
            borderRight: '1px solid #E5E5E5',
          }
      ),
    }),
  },
},
```

---

### 2.7 MuiTabs

```tsx
MuiTabs: {
  styleOverrides: {
    indicator: {
      backgroundColor: '#059669',
      height: 2,
    },
  },
},
MuiTab: {
  styleOverrides: {
    root: {
      textTransform: 'none',
      fontWeight: 500,
      fontSize: '0.875rem',
      minHeight: 44,  // Touch target mínimo
      '&.Mui-selected': {
        color: '#059669',
      },
    },
  },
},
```

---

### 2.8 MuiAlert

```tsx
MuiAlert: {
  styleOverrides: {
    root: {
      borderRadius: 4,
      fontSize: '0.875rem',
    },
    standardError:   { backgroundColor: 'rgba(239,68,68,0.12)',  color: '#EF4444' },
    standardWarning: { backgroundColor: 'rgba(245,158,11,0.12)', color: '#F59E0B' },
    standardInfo:    { backgroundColor: 'rgba(14,165,233,0.12)', color: '#0EA5E9' },
    standardSuccess: { backgroundColor: 'rgba(16,185,129,0.12)', color: '#10B981' },
  },
  defaultProps: {
    variant: 'standard',
  },
},
```

---

### 2.9 MuiSkeleton

```tsx
MuiSkeleton: {
  styleOverrides: {
    root: ({ theme }) => ({
      borderRadius: 4,
      ...(theme.palette.mode === 'dark'
        ? { backgroundColor: 'rgba(255,255,255,0.06)' }
        : { backgroundColor: 'rgba(0,0,0,0.06)' }
      ),
    }),
  },
  defaultProps: {
    animation: 'pulse',
  },
},
```

---

### 2.10 MuiDataGrid

```tsx
MuiDataGrid: {
  styleOverrides: {
    root: ({ theme }) => ({
      border: 'none',
      borderRadius: 6,
      fontSize: '0.875rem',
      '& .MuiDataGrid-columnHeaders': {
        backgroundColor:
          theme.palette.mode === 'dark'
            ? theme.palette.surface.s2
            : theme.palette.secondary.main,
        borderBottom: `1px solid ${theme.palette.divider}`,
        fontWeight: 600,
        fontSize: '0.8125rem',
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
      },
      '& .MuiDataGrid-row:hover': {
        backgroundColor:
          theme.palette.mode === 'dark'
            ? 'rgba(255,255,255,0.03)'
            : 'rgba(0,0,0,0.02)',
      },
      '& .MuiDataGrid-row.Mui-selected': {
        backgroundColor: 'rgba(5,150,105,0.08)',
        '&:hover': {
          backgroundColor: 'rgba(5,150,105,0.12)',
        },
      },
      '& .MuiDataGrid-cell': {
        borderBottom: `1px solid ${theme.palette.divider}`,
      },
    }),
  },
  defaultProps: {
    density: 'comfortable',
    disableColumnMenu: false,
    pageSizeOptions: [10, 25, 50],
  },
},
```

---

### 2.11 Demais Overrides Globais

```tsx
MuiCssBaseline: {
  styleOverrides: {
    body: {
      scrollbarColor: 'rgba(255,255,255,0.15) transparent',
      '&::-webkit-scrollbar': { width: 8 },
      '&::-webkit-scrollbar-thumb': {
        borderRadius: 4,
        backgroundColor: 'rgba(255,255,255,0.15)',
      },
    },
  },
},
MuiTooltip: {
  styleOverrides: {
    tooltip: ({ theme }) => ({
      borderRadius: 4,
      fontSize: '0.75rem',
      ...(theme.palette.mode === 'dark'
        ? {
            backgroundColor: theme.palette.surface.elevated,
            border: '1px solid rgba(255,255,255,0.10)',
            backdropFilter: 'blur(8px)',
          }
        : {
            backgroundColor: '#1F1F1F',
            color: '#FFFFFF',
          }
      ),
    }),
  },
},
MuiAppBar: {
  styleOverrides: {
    root: ({ theme }) => ({
      backgroundImage: 'none',
      boxShadow: 'none',
      borderBottom: `1px solid ${theme.palette.divider}`,
      backgroundColor: theme.palette.background.default,
    }),
  },
  defaultProps: {
    elevation: 0,
    color: 'transparent',
  },
},
MuiListItemButton: {
  styleOverrides: {
    root: {
      borderRadius: 4,
      '&.Mui-selected': {
        backgroundColor: 'rgba(5,150,105,0.12)',
        '&:hover': {
          backgroundColor: 'rgba(16,185,129,0.16)',
        },
      },
    },
  },
},
MuiFab: {
  styleOverrides: {
    root: {
      borderRadius: 4,  // Sem pill, mesmo no FAB
      boxShadow: 'none',
    },
  },
},
MuiPaper: {
  styleOverrides: {
    root: {
      backgroundImage: 'none',  // Remove gradiente padrão MUI em dark
    },
  },
},
```

---

## 3. Montagem Final do Tema

```tsx
// lib/theme.ts
import { createTheme, responsiveFontSizes } from '@mui/material/styles';

export function createCamTheme(mode: 'dark' | 'light') {
  const palette = mode === 'dark' ? darkPalette : lightPalette;
  const shadows = mode === 'dark' ? darkShadows : lightShadows;

  let theme = createTheme({
    palette,
    typography,
    spacing,
    shape,
    breakpoints,
    transitions,
    shadows,
    components: {
      // ... todos os overrides das seções 2.1–2.11
    },
  });

  // Responsividade tipográfica automática (headings)
  theme = responsiveFontSizes(theme, {
    breakpoints: ['md', 'lg'],
    factor: 2,
  });

  return theme;
}

// Tema padrão: DARK (Dark Mode First)
export const camDarkTheme = createCamTheme('dark');
export const camLightTheme = createCamTheme('light');
```

---

## 4. Ícones — @mui/icons-material

### Variante Padrão: `Outlined`

```tsx
// ✅ CORRETO — variante Outlined
import SearchOutlined from '@mui/icons-material/SearchOutlined';
import SettingsOutlined from '@mui/icons-material/SettingsOutlined';
import DashboardOutlined from '@mui/icons-material/DashboardOutlined';

// ❌ PROIBIDO como padrão — variante Filled
import Search from '@mui/icons-material/Search';
import Settings from '@mui/icons-material/Settings';
```

### Exceção: Ícones de Navegação Ativa

Ícones de nav items **ativos** usam variante **Filled** (sem sufixo) para indicar estado:

```tsx
// Nav item inativo
<ListItemIcon><DashboardOutlined /></ListItemIcon>

// Nav item ativo
<ListItemIcon><Dashboard /></ListItemIcon>  // Filled
```

### Tamanhos de Ícone

| Contexto | MUI `fontSize` prop | Equivalente px |
|---|---|---|
| Inline em textos, badges | `"small"` | 20px |
| Botões, inputs, nav items | `"small"` | 20px |
| Navegação, listas | `"medium"` (padrão) | 24px |
| Feature cards, hero | `"large"` | 35px |
| 16px (extra small) | `sx={{ fontSize: 16 }}` | 16px |

---

## 5. Regras de Estilização

### 5.1 `sx` prop vs `styled()`

| Usar `sx` quando | Usar `styled()` quando |
|---|---|
| Estilização pontual de 1 instância | Componente reutilizado em 3+ lugares |
| Override de 1-3 propriedades | Lógica condicional complexa de estilo |
| Prototipação rápida | Composição de estilos com props customizadas |
| Responsividade inline simples | Animações complexas com keyframes |

```tsx
// ✅ sx — override pontual
<Box sx={{ p: 6, bgcolor: 'surface.s1', borderRadius: '6px' }}>

// ✅ styled — componente reutilizável
const MetricCard = styled(Card)(({ theme }) => ({
  padding: theme.spacing(6),
  backgroundColor: theme.palette.surface.s1,
}));
```

**Proibido:**
- `style={{...}}` inline — usar `sx` ou `styled()`
- CSS modules — usar MUI System exclusivamente
- Tailwind classes — depreciado
- Emotion `css` prop diretamente — usar via `styled()` do MUI

### 5.2 Acesso a Tokens via `sx`

```tsx
// Cores da palette
sx={{ color: 'primary.main' }}
sx={{ bgcolor: 'background.paper' }}
sx={{ color: 'text.secondary' }}

// Superfícies customizadas
sx={{ bgcolor: 'surface.s1' }}
sx={{ bgcolor: 'surface.elevated' }}

// Acentos
sx={{ color: 'accent.purple' }}

// Spacing (multiplicador de 4px)
sx={{ p: 6 }}      // 24px
sx={{ m: 4 }}      // 16px
sx={{ gap: 4 }}    // 16px

// Responsividade
sx={{ p: { xs: 4, md: 6 } }}  // 16px mobile, 24px tablet+
```

### 5.3 Proibições Visuais (Checklist)

| Proibição | Motivo | Alternativa |
|---|---|---|
| `borderRadius: '9999px'` / pills | Contra identidade do cockpit | `borderRadius: '4px'` ou `'6px'` |
| `boxShadow` em dark mode | Tonal layering, não shadow | Bordas sutis + variação de superfície |
| `#000000` absoluto | Smearing em OLED | `#1A1A1A` ou tokens de superfície |
| Hex solto no `sx` | Quebra consistência | Tokens da palette (`'primary.main'`, etc.) |
| `textTransform: 'uppercase'` em botões | MUI default descartado | `textTransform: 'none'` (já no override) |
| Mais de 1 CTA primário por seção | Esmeralda = identidade do cockpit | 1 contained primary, resto outlined/text |
| `fontSize` abaixo de 12px | Mínimo absoluto | 12px (caption) |
| Sombras em `elevation > 0` em dark | Design system proíbe | `elevation={0}` + bordas |

### 5.4 Dark / Light Mode — Integração

```tsx
// ThemeProvider no root da aplicação
import { ThemeProvider, CssBaseline } from '@mui/material';
import { useMemo, useState } from 'react';
import { createCamTheme } from '@/lib/theme';

function App({ children }) {
  const [mode, setMode] = useState<'dark' | 'light'>('dark'); // Dark Mode First
  const theme = useMemo(() => createCamTheme(mode), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
```

- **Persistir** preferência do operador em `localStorage`
- **Fallback**: `window.matchMedia('(prefers-color-scheme: dark)')` se sem preferência salva
- **Padrão**: `'dark'` — Dark Mode First, sempre

### 5.5 Fontes — Carregamento

```tsx
// Cockpit React 19 + Vite — via @fontsource (sem Next.js)
// npm install @fontsource/poppins @fontsource/inter

import '@fontsource/poppins/600.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';

// Alternativa: Google Fonts via <link> no index.html
```

---

## 6. Dependências npm

```json
{
  "@mui/material": "^6.x",
  "@mui/icons-material": "^6.x",
  "@mui/x-data-grid": "^7.x",
  "@emotion/react": "^11.x",
  "@emotion/styled": "^11.x"
}
```

Remover ao migrar:
- `tailwindcss`, `@tailwindcss/*`, `postcss` (se só Tailwind usava)
- `lucide-react`
- `@radix-ui/*`, `class-variance-authority`, `clsx`, `tailwind-merge`
- `shadcn` / `components/ui/` (diretório inteiro)

---

## 7. Checklist de Conformidade (IA/Review)

1. [ ] Usa `ThemeProvider` com `createCamTheme('dark')` como padrão?
2. [ ] Headings com `Poppins 600`? Body com `Inter 400`?
3. [ ] Todos os botões com `borderRadius: 4`? Sem pills?
4. [ ] Cards com `borderRadius: 6`? Sem shadow em dark?
5. [ ] Inputs com focus ring `#059669`? Label sempre visível?
6. [ ] Chips com `borderRadius: 4`? Cores em 15% opacity?
7. [ ] Ícones `Outlined` por padrão? Filled apenas em nav ativo?
8. [ ] Tokens via palette, nunca hex solto em `sx`?
9. [ ] Espaçamentos em múltiplos de `theme.spacing()` (base 4px)?
10. [ ] Sombras zeradas em dark mode (exceto modais)?
11. [ ] `textTransform: 'none'` em botões e tabs?
12. [ ] WCAG AA em ambas variantes de tema?
13. [ ] Sem TailwindCSS, sem shadcn/ui, sem Lucide?
14. [ ] `CssBaseline` incluído no root?

---

## Referências

| Documento | Relação |
|---|---|
| `tokens.md` | Valores canônicos (upstream — SSoT) |
| `design-system.md` | Filosofia e componentes (upstream) |
| `paleta-cam.md` | Princípios de cor (upstream) |
| `branding-cam.md` | Identidade visual (upstream) |
| `ui-library.md` | UI Library — MUI (peer) |
| `layout-directive.md` | Diretriz de layout (peer) |
| `layout-system.md` | Shells e templates (downstream) |

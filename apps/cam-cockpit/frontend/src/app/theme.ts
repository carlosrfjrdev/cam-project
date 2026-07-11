/**
 * Theme MUI — DS CAM Esmeralda. TASK-U009 (BL-UI-1, SPEC v0.5-COCKPIT-UI).
 *
 * SSoT: the-cam/ui-design/tokens.md + mui-theme-cam.md.
 * Dark Mode First · Full Web · Esmeralda = identidade · Founder Orange = acento raro.
 *
 * Substitui o tema azul/monospace anterior (#1565c0 + JetBrains Mono global).
 * Headings em Poppins, corpo em Inter, monospace só para números técnicos.
 */
import { createTheme } from "@mui/material/styles";

// --- Tokens DS CAM (espelham tokens.css do showcase) -----------------------
export const camTokens = {
  primary: "#059669",
  primaryDark: "#047857",
  primaryLight: "#34D399",
  founderOrange: "#FF7A00",
  founderEmber: "#C2410C",
  founderGlow: "#FDBA74",
  background: "#1A1A1A",
  surface1: "#1F1F1F",
  surface2: "#2C2C2C",
  surface3: "#3A3A3A",
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  info: "#0EA5E9",
  ring: "#10B981",
  radiusBtn: 4,
  radiusCard: 6,
  radiusInput: 4,
  focusRing: "2px solid #10B981",
  fontHead: "'Poppins', system-ui, sans-serif",
  fontBody: "'Inter', system-ui, sans-serif",
  fontMono: "'JetBrains Mono', ui-monospace, monospace",
} as const;

// Augmenta o theme com tokens próprios do CaM (Founder Orange + extras).
declare module "@mui/material/styles" {
  interface Palette {
    founderOrange: Palette["primary"];
  }
  interface PaletteOptions {
    founderOrange?: PaletteOptions["primary"];
  }
  interface Theme {
    cam: {
      radiusCard: number;
      focusRing: string;
      fontMono: string;
      surface2: string;
      surface3: string;
    };
  }
  interface ThemeOptions {
    cam?: Theme["cam"];
  }
}

const headingFont = camTokens.fontHead;

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: camTokens.primary,
      dark: camTokens.primaryDark,
      light: camTokens.primaryLight,
      contrastText: "#FFFFFF",
    },
    success: { main: camTokens.success },
    warning: { main: camTokens.warning },
    error: { main: camTokens.error },
    info: { main: camTokens.info },
    founderOrange: {
      main: camTokens.founderOrange,
      light: camTokens.founderGlow,
      dark: camTokens.founderEmber,
      contrastText: "#1A1A1A",
    },
    background: { default: camTokens.background, paper: camTokens.surface1 },
    text: { primary: "#FFFFFF", secondary: "#A0A0A0" },
    divider: "rgba(255,255,255,0.10)",
  },
  shape: { borderRadius: camTokens.radiusBtn },
  cam: {
    radiusCard: camTokens.radiusCard,
    focusRing: camTokens.focusRing,
    fontMono: camTokens.fontMono,
    surface2: camTokens.surface2,
    surface3: camTokens.surface3,
  },
  typography: {
    fontFamily: camTokens.fontBody,
    h1: { fontFamily: headingFont, fontWeight: 600 },
    h2: { fontFamily: headingFont, fontWeight: 600 },
    h3: { fontFamily: headingFont, fontWeight: 600 },
    h4: { fontFamily: headingFont, fontWeight: 600 },
    h5: { fontFamily: headingFont, fontWeight: 600 },
    h6: { fontFamily: headingFont, fontWeight: 600 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: {
          borderRadius: camTokens.radiusBtn,
          textTransform: "none",
          "&:focus-visible": { outline: camTokens.focusRing, outlineOffset: 2 },
        },
      },
    },
    MuiCard: {
      styleOverrides: { root: { borderRadius: camTokens.radiusCard } },
    },
    MuiPaper: {
      styleOverrides: { root: { backgroundImage: "none" } },
    },
  },
});

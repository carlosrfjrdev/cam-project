import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#1565c0" },
    error: { main: "#d32f2f" },
    warning: { main: "#f57c00" },
    success: { main: "#2e7d32" },
    background: { default: "#0a0a0a", paper: "#121212" },
  },
  typography: {
    fontFamily: "'JetBrains Mono', 'Roboto Mono', monospace",
    h4: { fontWeight: 700 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
    },
  },
});

/**
 * Markdown — renderer de markdown com GFM (tabelas, listas, headings).
 *
 * Usado para exibir a narrativa da IA (Trade Analyzer) que vem em markdown.
 * Estilização via sx no wrapper (tabelas/headings/código) usando o tema CaM.
 */
import { Box } from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function Markdown({ children }: { children: string }) {
  return (
    <Box
      sx={{
        fontSize: 14,
        lineHeight: 1.6,
        color: "text.primary",
        "& h1, & h2, & h3, & h4": { mt: 2, mb: 1, fontWeight: 700, lineHeight: 1.3 },
        "& h1": { fontSize: "1.4rem" },
        "& h2": { fontSize: "1.2rem" },
        "& h3": { fontSize: "1.05rem" },
        "& p": { my: 1 },
        "& ul, & ol": { my: 1, pl: 3 },
        "& li": { mb: 0.5 },
        "& a": { color: "primary.main" },
        "& strong": { fontWeight: 700 },
        "& code": {
          fontFamily: (t) => t.cam?.fontMono ?? "monospace",
          bgcolor: (t) => t.cam?.surface2 ?? "action.hover",
          px: 0.5, py: 0.2, borderRadius: 0.5, fontSize: "0.85em",
        },
        "& pre": {
          bgcolor: (t) => t.cam?.surface2 ?? "action.hover",
          p: 1.5, borderRadius: 1, overflow: "auto",
        },
        "& pre code": { bgcolor: "transparent", p: 0 },
        "& blockquote": {
          borderLeft: (t) => `3px solid ${t.palette.divider}`,
          pl: 2, ml: 0, color: "text.secondary",
        },
        "& table": {
          borderCollapse: "collapse", width: "100%", my: 1.5, fontSize: 13,
        },
        "& th, & td": {
          border: (t) => `1px solid ${t.palette.divider}`,
          px: 1, py: 0.75, textAlign: "left", verticalAlign: "top",
        },
        "& th": { bgcolor: (t) => t.cam?.surface2 ?? "action.hover", fontWeight: 700 },
        "& hr": { border: 0, borderTop: (t) => `1px solid ${t.palette.divider}`, my: 2 },
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </Box>
  );
}

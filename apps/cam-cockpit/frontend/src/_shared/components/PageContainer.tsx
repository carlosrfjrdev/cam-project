/**
 * PageContainer — wrapper único de página (Design Review §5.2, Andy).
 *
 * UMA densidade de margem no produto inteiro: acaba com a inconsistência
 * `px:"5%"` (Inspetor/Lab) vs `p:3` (resto). Toda tela nova usa este.
 */
import type { ReactNode } from "react";
import { Box } from "@mui/material";

interface PageContainerProps {
  children: ReactNode;
  /** Limita a largura do conteúdo (telas de leitura). Default: full. */
  maxWidth?: number | string;
}

export function PageContainer({ children, maxWidth }: PageContainerProps) {
  return (
    <Box
      sx={{
        px: { xs: 2, md: 4 },
        py: 2,
        width: "100%",
        maxWidth: maxWidth ?? "100%",
        mx: maxWidth ? "auto" : 0,
        boxSizing: "border-box",
      }}
    >
      {children}
    </Box>
  );
}

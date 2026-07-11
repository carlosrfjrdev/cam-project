/**
 * PageHeader — título seco + ações (Design Review §5.1, Andy).
 *
 * Substitui o par `Typography h5` + `body2`-subtítulo-prosa repetido em toda
 * tela. UMA manchete textual; sem parágrafo de reapresentação. Ações/chips de
 * status à direita.
 */
import type { ReactNode } from "react";
import { Box, Stack, Typography } from "@mui/material";

interface PageHeaderProps {
  title: string;
  /** Ícone opcional à esquerda do título. */
  icon?: ReactNode;
  /** Chips de status / botões à direita. */
  actions?: ReactNode;
}

export function PageHeader({ title, icon, actions }: PageHeaderProps) {
  return (
    <Stack
      direction="row"
      alignItems="center"
      justifyContent="space-between"
      sx={{ mb: 2, gap: 1, flexWrap: "wrap" }}
    >
      <Stack direction="row" alignItems="center" spacing={1}>
        {icon}
        <Typography variant="h5">{title}</Typography>
      </Stack>
      {actions && (
        <Box sx={{ display: "flex", gap: 1, alignItems: "center", flexWrap: "wrap" }}>
          {actions}
        </Box>
      )}
    </Stack>
  );
}

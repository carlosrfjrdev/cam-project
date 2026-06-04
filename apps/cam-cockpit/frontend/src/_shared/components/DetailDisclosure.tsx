/**
 * DetailDisclosure — accordion fechado padronizado (Design Review §5.4, Andy).
 *
 * Recipiente canônico de TUDO que é detalhe/evidência/tabela longa: tabela de
 * trades, walk-forward, logs de robô, parâmetros avançados, glossários. Fechado
 * por default — a superfície mostra a CONCLUSÃO; a evidência fica a um clique.
 */
import type { ReactNode } from "react";
import {
  Accordion, AccordionDetails, AccordionSummary, Typography,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

interface DetailDisclosureProps {
  title: string;
  children: ReactNode;
  /** Conta opcional ao lado do título: "Trades (88)". */
  count?: number;
  defaultExpanded?: boolean;
}

export function DetailDisclosure({
  title, children, count, defaultExpanded = false,
}: DetailDisclosureProps) {
  return (
    <Accordion
      defaultExpanded={defaultExpanded}
      disableGutters
      elevation={0}
      sx={{ bgcolor: "transparent", "&:before": { display: "none" }, mt: 1 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ px: 0 }}>
        <Typography variant="subtitle2">
          {title}
          {count !== undefined && (
            <Typography component="span" color="text.secondary">
              {" "}({count})
            </Typography>
          )}
        </Typography>
      </AccordionSummary>
      <AccordionDetails sx={{ px: 0 }}>{children}</AccordionDetails>
    </Accordion>
  );
}

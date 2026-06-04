/**
 * Quant Lab — Research Lane (Lead-Lag) · ANÁLISES.
 *
 * READ-ONLY, isolado do Cockpit Live. A INGESTÃO de dados saiu daqui para o
 * módulo /dataset (fonte única de entrada). O Lab mantém só as análises.
 */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, Box, Chip, Stack, TextField, Typography } from "@mui/material";
import ScienceIcon from "@mui/icons-material/Science";
import { fetchDataHealth } from "./api";
import { LeadLagAnalysis } from "./LeadLagAnalysis";
import { RunRegistry } from "./RunRegistry";

const DEFAULT_UNIVERSE = "WIN$, WDO$, VALE3, ITUB4, PETR4, AXIA3, BBDC4, B3SA3";

export function QuantLabPage() {
  const [universe, setUniverse] = useState(DEFAULT_UNIVERSE);

  // só para saber se há dado a analisar (a ingestão vive em /dataset).
  const health = useQuery({
    queryKey: ["research", "data-health"],
    queryFn: fetchDataHealth,
    retry: false,
  });
  const hasData = !!health.data && health.data.bars.length > 0;

  return (
    <Box sx={{ px: "5%", py: 2, width: "100%", boxSizing: "border-box" }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
        <ScienceIcon color="secondary" />
        <Typography variant="h5">Quant Lab</Typography>
        <Chip size="small" color="secondary" label="RESEARCH" />
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Laboratório de pesquisa Lead-Lag — descoberta estatística read-only.
        A ingestão de dados fica em <strong>Dataset</strong>. Nenhuma ação aqui envia ordem.
      </Typography>

      <TextField
        size="small" fullWidth value={universe}
        onChange={(e) => setUniverse(e.target.value)}
        label="Universo de análise (símbolos, vírgula)" sx={{ mb: 2 }}
      />

      {!hasData && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Sem dados de research ainda — rode a ingestão no módulo <strong>Dataset</strong>.
        </Alert>
      )}

      {hasData && (
        <LeadLagAnalysis
          universe={universe.split(",").map((s) => s.trim().toUpperCase()).filter(Boolean)}
        />
      )}

      <RunRegistry />
    </Box>
  );
}

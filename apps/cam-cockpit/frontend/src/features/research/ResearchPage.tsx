/**
 * Research / AI Workbench — TASK-U023 (BL-UI-5). Rota lazy (bundle isolado).
 *
 * Correlação cross-asset, spread de pair trade e output estruturado do AI
 * Workbench (Anthropic/Ollama; OpenAI bloqueado → mensagem). Research-only.
 *
 * NOTA: visualização gráfica é placeholder SVG/CSS — Recharts ainda não está no
 * stack (TD-v0.5-RECHARTS). A estrutura de dados já está pronta para troca.
 */
import { useState } from "react";
import {
  Box, Typography, Stack, Paper, Button, TextField, MenuItem, Alert, Chip,
} from "@mui/material";
import BiotechIcon from "@mui/icons-material/Biotech";
import { useCorrelation, useWorkbench } from "./useResearch";

function CorrelationGauge({ value }: { value: number | null }) {
  // Placeholder visual (TD-v0.5-RECHARTS substitui por gráfico real).
  const pct = value === null ? 0 : Math.abs(value) * 100;
  return (
    <Box data-testid="correlation-chart" sx={{ mt: 1 }}>
      <Box sx={{ height: 12, borderRadius: 1, bgcolor: "background.default", overflow: "hidden" }}>
        <Box sx={{ height: "100%", width: `${pct}%`, bgcolor: "primary.main" }} />
      </Box>
      <Typography variant="caption" color="text.secondary">
        ρ = {value === null ? "indisponível (Fase 0)" : value.toFixed(3)}
      </Typography>
    </Box>
  );
}

export function ResearchPage() {
  const { data: corr } = useCorrelation();
  const workbench = useWorkbench();
  const [provider, setProvider] = useState("ollama");
  const [prompt, setPrompt] = useState("");

  const openAiBlocked =
    workbench.isError && /OpenAINotEnabled|OpenAI/.test((workbench.error as Error)?.message ?? "");

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={2}>
        <BiotechIcon sx={{ fontSize: 30, color: "primary.main" }} />
        <Typography variant="h4">Research / AI Workbench</Typography>
        <Chip label="RESEARCH-ONLY" size="small" variant="outlined" />
      </Stack>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6">Correlação cross-asset</Typography>
        <Typography variant="body2" color="text.secondary">
          {corr ? `${corr.asset_a} × ${corr.asset_b}` : "—"}
        </Typography>
        <CorrelationGauge value={corr?.correlation ?? null} />
        {corr?.note && <Alert severity="info" sx={{ mt: 1 }}>{corr.note}</Alert>}
      </Paper>

      <Paper sx={{ p: 2 }} data-testid="ai-workbench">
        <Typography variant="h6" sx={{ mb: 1 }}>AI Workbench</Typography>
        <Stack spacing={2}>
          <TextField
            select label="Provider" size="small" value={provider}
            onChange={(e) => setProvider(e.target.value)} sx={{ maxWidth: 200 }}
          >
            <MenuItem value="ollama">Ollama (local)</MenuItem>
            <MenuItem value="anthropic">Anthropic</MenuItem>
            <MenuItem value="openai">OpenAI (bloqueado)</MenuItem>
          </TextField>
          <TextField
            label="Prompt" multiline minRows={2} value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <Box>
            <Button
              variant="contained"
              onClick={() => workbench.mutate({ provider, prompt })}
              disabled={!prompt || workbench.isPending}
            >
              Analisar
            </Button>
          </Box>

          {openAiBlocked && (
            <Alert severity="warning" data-testid="openai-not-enabled">
              OpenAI está bloqueado (TD-v0.4-02 — aguarda ADR formal). Use
              Anthropic ou Ollama.
            </Alert>
          )}

          {workbench.data && (
            <Alert severity="success" data-testid="workbench-output">
              <Typography variant="body2" sx={{ fontFamily: (t) => t.cam.fontMono }}>
                provider: {workbench.data.provider} · model: {workbench.data.model}
                <br />
                prompt_hash: {workbench.data.prompt_hash.slice(0, 16)}…
                <br />
                anonymized: {String(workbench.data.anonymized)}
              </Typography>
            </Alert>
          )}
        </Stack>
      </Paper>
    </Box>
  );
}

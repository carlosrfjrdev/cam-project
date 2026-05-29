import {
  Box, Typography, Paper, Stack, Chip, Alert, Button, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField,
} from "@mui/material";
import GavelIcon from "@mui/icons-material/Gavel";
import LockIcon from "@mui/icons-material/Lock";
import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { ConstitutionVersion } from "../../api/types";

export function ConstitutionPage() {
  const [amendOpen, setAmendOpen] = useState(false);
  const [amendText, setAmendText] = useState("");
  const [amendReason, setAmendReason] = useState("");

  const { data: constitution } = useQuery({
    queryKey: ["constitution-current"],
    queryFn: () => api.get<ConstitutionVersion>("/constitution/current"),
  });

  const proposeAmendment = useMutation({
    mutationFn: () => api.post("/constitution/amendments", { text: amendText, reason: amendReason }),
    onSuccess: () => {
      setAmendOpen(false);
      setAmendText("");
      setAmendReason("");
    },
  });

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" spacing={2} mb={3}>
        <GavelIcon sx={{ fontSize: 32 }} />
        <Typography variant="h4" fontWeight={700}>Constituição CaM</Typography>
        <Chip label="READ ONLY" icon={<LockIcon />} size="small" color="warning" />
        {constitution && (
          <Chip label={`v${constitution.version}`} size="small" color="primary" />
        )}
      </Stack>

      <Alert severity="info" sx={{ mb: 3 }}>
        A Constituição é soberana (Art. 43º). Exibição read-only — sem edição inline (SPEC R5.07).
        Propostas de emenda são apenas registros — execução real requer aprovação do Founder.
      </Alert>

      <Paper sx={{ p: 3, mb: 3, maxHeight: 600, overflow: "auto" }}>
        {constitution ? (
          <Box
            component="pre"
            sx={{ whiteSpace: "pre-wrap", fontFamily: "inherit", fontSize: 14, lineHeight: 1.6 }}
          >
            {constitution.content}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Constituição não encontrada no banco. Execute a migration e insira a versão inicial.
          </Typography>
        )}
      </Paper>

      <Stack direction="row" justifyContent="flex-end">
        <Button
          variant="outlined"
          onClick={() => setAmendOpen(true)}
        >
          Propor Emenda (apenas registro)
        </Button>
      </Stack>

      <Dialog open={amendOpen} onClose={() => setAmendOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Proposta de Emenda Constitucional</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Esta proposta é apenas um registro. A emenda real requer aprovação explícita do Founder e processo formal definido na Constituição.
          </Alert>
          <TextField
            fullWidth
            label="Artigo / Texto da Emenda"
            multiline
            rows={4}
            value={amendText}
            onChange={e => setAmendText(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Justificativa"
            multiline
            rows={2}
            value={amendReason}
            onChange={e => setAmendReason(e.target.value)}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAmendOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={() => proposeAmendment.mutate()}
            disabled={!amendText || proposeAmendment.isPending}
          >
            Registrar Proposta
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

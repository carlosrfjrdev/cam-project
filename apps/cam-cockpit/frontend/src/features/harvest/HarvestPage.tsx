import {
  Box, Typography, Paper, Stack, Grid, Button, Alert, Dialog, DialogTitle,
  DialogContent, DialogActions, Divider, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow,
} from "@mui/material";
import SavingsIcon from "@mui/icons-material/Savings";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { BucketSnapshot, HarvestProposal } from "../../api/types";

function formatBRL(v: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(v);
}

interface BucketCard {
  label: string;
  value: number;
  description: string;
}

function BucketCard({ label, value, description }: BucketCard) {
  return (
    <Paper sx={{ p: 3, textAlign: "center" }}>
      <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
        {label}
      </Typography>
      <Typography variant="h4" fontWeight={700} color={value >= 0 ? "primary.main" : "error.main"} sx={{ my: 1 }}>
        {formatBRL(value)}
      </Typography>
      <Typography variant="caption" color="text.secondary">{description}</Typography>
    </Paper>
  );
}

export function HarvestPage() {
  const qc = useQueryClient();
  const [confirmOpen, setConfirmOpen] = useState(false);

  const { data: snapshot } = useQuery({
    queryKey: ["bucket-snapshot"],
    queryFn: () => api.get<BucketSnapshot>("/harvest/snapshot"),
  });

  const { data: proposal } = useQuery({
    queryKey: ["harvest-proposal"],
    queryFn: () => api.get<HarvestProposal>("/harvest/proposal"),
  });

  const executeHarvest = useMutation({
    mutationFn: () => api.post("/harvest/execute", { founder_approved: true }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bucket-snapshot"] });
      qc.invalidateQueries({ queryKey: ["harvest-proposal"] });
      setConfirmOpen(false);
    },
  });

  const sangriaTrigger = 4500;
  const sangriaNear = (snapshot?.bucket_derivativo ?? 0) >= sangriaTrigger * 0.8;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} mb={3}>Harvest — Distribuição de Lucros</Typography>

      {sangriaNear && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Bucket Derivativo próximo do gatilho de Sangria (R$ {sangriaTrigger.toLocaleString("pt-BR")}).
          Sangria automaticamente proposta quando atingir o limite.
        </Alert>
      )}

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <BucketCard label="Bucket Derivativo" value={snapshot?.bucket_derivativo ?? 0} description="Capital de giro operacional" />
        </Grid>
        <Grid item xs={12} md={4}>
          <BucketCard label="Buffer Operacional" value={snapshot?.buffer_operacional ?? 0} description="40% do harvest até linha de base R$ 1.000" />
        </Grid>
        <Grid item xs={12} md={4}>
          <BucketCard label="Carteira Hard" value={snapshot?.carteira_hard ?? 0} description="60% do harvest — capital preservado" />
        </Grid>
      </Grid>

      {proposal && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>Proposta de Harvest</Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Gerada em {new Date(proposal.proposed_at).toLocaleString("pt-BR")}
          </Typography>
          <Stack spacing={1} mt={2}>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2">Lucro Líquido Distribuível</Typography>
              <Typography variant="body2" fontWeight={700} color="success.main">{formatBRL(proposal.net_profit)}</Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2">→ Carteira Hard (60%)</Typography>
              <Typography variant="body2" color="primary.main">{formatBRL(proposal.carteira_hard_transfer)}</Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2">→ Buffer Operacional (40%)</Typography>
              <Typography variant="body2">{formatBRL(proposal.buffer_transfer)}</Typography>
            </Stack>
          </Stack>
          <Divider sx={{ my: 2 }} />
          <Stack direction="row" justifyContent="flex-end">
            <Button
              variant="contained"
              color="success"
              startIcon={<SavingsIcon />}
              onClick={() => setConfirmOpen(true)}
            >
              Executar Harvest
            </Button>
          </Stack>
        </Paper>
      )}

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Confirmar Harvest</DialogTitle>
        <DialogContent>
          <Typography>
            Esta ação distribui {formatBRL(proposal?.net_profit ?? 0)} entre os buckets.
            Esta operação requer aprovação explícita do Founder (SPEC R4.07).
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => executeHarvest.mutate()}
            disabled={executeHarvest.isPending}
          >
            Confirmar e Executar
          </Button>
        </DialogActions>
      </Dialog>

      <Typography variant="h6" gutterBottom>Histórico de Harvests</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Data</TableCell>
              <TableCell align="right">Lucro Líquido</TableCell>
              <TableCell align="right">Carteira Hard</TableCell>
              <TableCell align="right">Buffer</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell colSpan={4} align="center">
                <Typography variant="body2" color="text.secondary">Histórico carregado do banco</Typography>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

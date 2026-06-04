/**
 * Assets Experts — "meus robôs estão rodando?" (Design Review §3.3, Andy).
 *
 * Manchete: lista de robôs com status grande + SELO DEMO sempre visível
 * (guard-rail vira affordance, não letra miúda). Sobriedade máxima — cor forte
 * só em DEMO/parar. Painel de Paridade (Py↔EA) é o detalhe operacional: gate
 * bloqueante — FAIL abre divergências para investigar.
 */
import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Alert, Box, Button, Chip, Stack, Table, TableBody, TableCell, TableHead,
  TableRow, TextField, Tooltip, Typography,
} from "@mui/material";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { DetailDisclosure } from "../../_shared/components/DetailDisclosure";
import {
  parseEaLedgerCsv, postParity, type ParityReport,
} from "./api";

// Onda 1: o "robô" é o gravador de paridade cam_d1_orb30 (sem ordem).
const ROBOTS = [
  {
    id: "cam_d1_orb30",
    name: "D1 ORB-30",
    symbol: "WIN$",
    unit: "ativo único",
    state: "gravador (sem ordem)",
    demo: true,
  },
];

export function AssetsExpertsPage() {
  return (
    <PageContainer maxWidth={1000}>
      <PageHeader
        title="Robôs (Experts)"
        icon={<SmartToyIcon color="secondary" />}
        actions={
          <Tooltip title="Os EAs da Onda 1 só rodam em conta DEMO (guard-rail duplo).">
            <Chip
              size="small"
              color="warning"
              icon={<VerifiedUserIcon />}
              label="DEMO"
            />
          </Tooltip>
        }
      />

      {/* Manchete: lista de robôs */}
      <Stack spacing={1}>
        {ROBOTS.map((r) => (
          <Box
            key={r.id}
            sx={{
              p: 2, borderRadius: 1, border: "1px solid", borderColor: "divider",
              bgcolor: "background.paper",
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="subtitle1" fontWeight={700}>
                  {r.name} · {r.symbol}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {r.unit} · {r.state}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1} alignItems="center">
                <Chip size="small" variant="outlined" label="○ parado" />
                <Chip size="small" color="warning" label="DEMO" />
              </Stack>
            </Stack>
          </Box>
        ))}
      </Stack>

      <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 1 }}>
        O EA cam_d1_orb30 não envia ordem — grava o ledger canônico no Strategy
        Tester para a paridade. Execução real em DEMO é etapa posterior.
      </Typography>

      <ParityPanel />
    </PageContainer>
  );
}

// --------------------------------------------------------------------------- //
// Painel de Paridade — cola o CSV do EA, casa contra um run do CAM (gate).
// --------------------------------------------------------------------------- //
function ParityPanel() {
  const [runId, setRunId] = useState<number | "">("");
  const [tickSize, setTickSize] = useState(5);
  const [csv, setCsv] = useState("");
  const [report, setReport] = useState<ParityReport | null>(null);

  const ledger = useMemo(() => parseEaLedgerCsv(csv), [csv]);

  const parity = useMutation({
    mutationFn: () =>
      postParity(Number(runId), { ea_ledger: ledger, tick_size: tickSize }),
    onSuccess: (r) => setReport(r),
  });

  const canRun = runId !== "" && ledger.length > 0 && tickSize > 0;

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>
        Paridade Python ↔ EA
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Cole o conteúdo de <code>cam_d1_orb30_ledger.csv</code> (Strategy Tester)
        e o nº do run do CAM. PASS = a matemática do robô bate com o backtest.
      </Typography>

      <Stack direction="row" spacing={1} sx={{ mt: 1, mb: 1, flexWrap: "wrap", gap: 1 }}>
        <TextField
          size="small" type="number" label="Run ID" value={runId}
          onChange={(e) => setRunId(e.target.value === "" ? "" : Number(e.target.value))}
          sx={{ width: 110 }}
        />
        <TextField
          size="small" type="number" label="Tick size" value={tickSize}
          onChange={(e) => setTickSize(Number(e.target.value))} sx={{ width: 110 }}
        />
        <Chip
          size="small"
          variant="outlined"
          label={`${ledger.length} linha(s) lida(s)`}
          sx={{ alignSelf: "center" }}
        />
        <Button
          variant="contained"
          onClick={() => parity.mutate()}
          disabled={!canRun || parity.isPending}
        >
          {parity.isPending ? "Comparando…" : "Rodar paridade"}
        </Button>
      </Stack>

      <TextField
        multiline minRows={4} maxRows={10} fullWidth size="small"
        placeholder="pair_id;leg;symbol;ts_entry;price_entry;ts_exit;price_exit;qty;exit_reason;pnl_bruto;volume_financeiro&#10;0;long;WIN$;2026-06-03T09:36:00;102.0;..."
        value={csv}
        onChange={(e) => setCsv(e.target.value)}
        sx={{ fontFamily: "monospace" }}
      />

      {parity.isError && (
        <Alert severity="error" sx={{ mt: 1 }}>
          Falha ao rodar paridade — confira o Run ID (precisa existir no CAM).
        </Alert>
      )}

      {report && (
        <Box sx={{ mt: 2 }}>
          <Alert severity={report.verdict === "PASS" ? "success" : "error"}>
            <strong>{report.verdict}</strong> — {report.matched} de{" "}
            {Math.max(report.n_python, report.n_ea)} trade(s) idênticos
            (Python {report.n_python} · EA {report.n_ea}).
            {report.verdict === "FAIL" &&
              " Divergência detectada — abrir BUG antes de evoluir o EA."}
          </Alert>

          {report.divergences.length > 0 && (
            <DetailDisclosure title="Divergências" count={report.divergences.length} defaultExpanded>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Dimensão</TableCell>
                    <TableCell>Python</TableCell>
                    <TableCell>EA</TableCell>
                    <TableCell>Pista</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {report.divergences.map((d, i) => (
                    <TableRow key={i}>
                      <TableCell>{d.pair_id}</TableCell>
                      <TableCell>{d.dimension}</TableCell>
                      <TableCell>{String(d.python)}</TableCell>
                      <TableCell>{String(d.ea)}</TableCell>
                      <TableCell>{d.hint}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </DetailDisclosure>
          )}
        </Box>
      )}
    </Box>
  );
}

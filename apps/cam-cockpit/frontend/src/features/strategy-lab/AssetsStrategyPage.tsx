/**
 * Assets Strategy — "minhas estratégias" (Design Review §3.1, Andy).
 *
 * Manchete: GRID DE CARDS. Cada card = nome + família + unidade + 1 chip de
 * status. Clicar abre DRAWER com parâmetros e o otimizador on-demand (sugere,
 * não aplica). Nada de tabela na superfície.
 */
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Box, Button, Chip, CircularProgress, Divider, Drawer, Stack,
  TextField, Tooltip, Typography,
} from "@mui/material";
import HubIcon from "@mui/icons-material/Hub";
import { PageContainer } from "../../_shared/components/PageContainer";
import { PageHeader } from "../../_shared/components/PageHeader";
import { DetailDisclosure } from "../../_shared/components/DetailDisclosure";
import {
  fetchStrategies, postOptimize, type OptimizeResult, type StrategyDef,
} from "./api";

const UNIT_LABEL: Record<string, string> = {
  single: "ativo único",
  pair: "par",
  basket: "cesta",
};

function GrossChip() {
  return (
    <Tooltip title="Valores brutos: sem custo, sem IR — não confirma edge líquido.">
      <Chip size="small" variant="outlined" label="bruto" />
    </Tooltip>
  );
}

export function AssetsStrategyPage() {
  const [selected, setSelected] = useState<StrategyDef | null>(null);
  const strategies = useQuery({
    queryKey: ["strategy-lab", "strategies"],
    queryFn: fetchStrategies,
    retry: false,
  });

  return (
    <PageContainer>
      <PageHeader
        title="Estratégias"
        icon={<HubIcon color="secondary" />}
        actions={<GrossChip />}
      />

      {strategies.isLoading && <CircularProgress size={22} />}
      {strategies.isError && (
        <Typography color="text.secondary">
          Não foi possível carregar o catálogo. O backend está no ar?
        </Typography>
      )}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr 1fr", sm: "repeat(3, 1fr)", md: "repeat(4, 1fr)" },
          gap: 1.5,
        }}
      >
        {strategies.data?.strategies.map((s) => (
          <Box
            key={s.id}
            onClick={() => setSelected(s)}
            sx={{
              p: 2,
              borderRadius: 1,
              border: "1px solid",
              borderColor: "divider",
              cursor: "pointer",
              bgcolor: "background.paper",
              transition: "border-color 120ms",
              "&:hover": { borderColor: "secondary.main" },
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="subtitle1" fontWeight={700}>
                {s.id}
              </Typography>
              <Chip
                size="small"
                label={s.runnable ? "pronta" : "em breve"}
                color={s.runnable ? "success" : "default"}
                variant={s.runnable ? "filled" : "outlined"}
              />
            </Stack>
            <Typography variant="body2" noWrap title={s.name}>
              {s.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {UNIT_LABEL[s.unit] ?? s.unit} · {s.timeframe}
            </Typography>
          </Box>
        ))}
      </Box>

      <StrategyDrawer strategy={selected} onClose={() => setSelected(null)} />
    </PageContainer>
  );
}

// --------------------------------------------------------------------------- //
// Drawer de detalhe — parâmetros + otimizador on-demand
// --------------------------------------------------------------------------- //
function StrategyDrawer({
  strategy, onClose,
}: {
  strategy: StrategyDef | null;
  onClose: () => void;
}) {
  const [symbol, setSymbol] = useState("WIN$");
  const [result, setResult] = useState<OptimizeResult | null>(null);

  const optimize = useMutation({
    mutationFn: () =>
      postOptimize(strategy!.id, { symbol, method: "grid" }),
    onSuccess: (r) => setResult(r),
  });

  return (
    <Drawer anchor="right" open={!!strategy} onClose={onClose}>
      <Box sx={{ width: { xs: 320, sm: 420 }, p: 3 }}>
        {strategy && (
          <>
            <Typography variant="h6">{strategy.id} · {strategy.name}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {strategy.description}
            </Typography>

            <Divider sx={{ my: 2 }} />

            {!strategy.runnable && (
              <Typography variant="body2" color="text.secondary">
                Estratégia listada para as próximas ondas — ainda sem par MQL5 +
                paridade. Só D1 é executável na Onda 1.
              </Typography>
            )}

            {strategy.runnable && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Parâmetros (padrão)
                </Typography>
                <Stack spacing={0.5} sx={{ mb: 2 }}>
                  {Object.entries(strategy.default_params).map(([k, v]) => (
                    <Stack key={k} direction="row" justifyContent="space-between">
                      <Typography variant="body2" color="text.secondary">{k}</Typography>
                      <Typography variant="body2">{String(v)}</Typography>
                    </Stack>
                  ))}
                </Stack>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Otimizar (on-demand)
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Varre o espaço de parâmetros e SUGERE — não aplica nada sozinho.
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                  <TextField
                    size="small"
                    label="Símbolo"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  />
                  <Button
                    variant="contained"
                    onClick={() => optimize.mutate()}
                    disabled={optimize.isPending}
                  >
                    {optimize.isPending ? "Otimizando…" : "Otimizar"}
                  </Button>
                </Stack>

                {optimize.isError && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    Falha ao otimizar — confira se há dado do símbolo.
                  </Typography>
                )}

                {result && <OptimizerVerdict result={result} />}
              </>
            )}
          </>
        )}
      </Box>
    </Drawer>
  );
}

// Veredito do otimizador: 1 recomendação + selo de robustez como 3 chips
// (Design Review §3.1 — NÃO mostrar a grade inteira na superfície).
function OptimizerVerdict({ result }: { result: OptimizeResult }) {
  if (result.error || result.verdict === "INSUFFICIENT_DATA") {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Dados insuficientes para sugerir com robustez ({result.n_trials ?? 0}{" "}
        combinações testadas). Sem sugestão — é uma resposta honesta, não um erro.
      </Typography>
    );
  }
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="body2" sx={{ mb: 1 }}>
        Sugerido:{" "}
        <strong>
          {Object.entries(result.best_params)
            .map(([k, v]) => `${k} ${v}`)
            .join(" · ")}
        </strong>
      </Typography>
      <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
        <Chip size="small" label={`${result.n_trials} combinações`} />
        <Tooltip title="Superfície 'chata' ao redor do ótimo = robusto. Pico isolado = frágil.">
          <Chip
            size="small"
            color={result.no_cliff ? "success" : "warning"}
            label={result.no_cliff ? "superfície estável" : "pico frágil"}
          />
        </Tooltip>
        <Tooltip title="Sharpe deflacionado pelo nº de tentativas (anti-data-snooping).">
          <Chip
            size="small"
            variant="outlined"
            label={`DSR ${result.deflated_sharpe?.toFixed(2) ?? "—"}`}
          />
        </Tooltip>
      </Stack>
      <DetailDisclosure title="O que isto significa">
        <Typography variant="body2" color="text.secondary">
          {result.note} A sugestão fica salva como conjunto de parâmetros
          (origem: sugerido). Você decide adotar — nada é aplicado
          automaticamente.
        </Typography>
      </DetailDisclosure>
    </Box>
  );
}

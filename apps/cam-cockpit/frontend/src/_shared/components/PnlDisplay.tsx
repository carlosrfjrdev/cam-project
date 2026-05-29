import { Box, Typography, Stack } from "@mui/material";

interface PnlDisplayProps {
  grossAmount: number;
  netAmount: number;
  currency?: string;
  size?: "small" | "medium" | "large";
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value);
}

export function PnlDisplay({ grossAmount, netAmount, currency = "BRL", size = "medium" }: PnlDisplayProps) {
  void currency;
  const isNegativeNet = netAmount < 0;
  const isNegativeGross = grossAmount < 0;

  const netColor = isNegativeNet ? "error.main" : netAmount > 0 ? "success.main" : "text.primary";
  const grossColor = isNegativeGross ? "error.light" : grossAmount > 0 ? "success.light" : "text.secondary";

  const netVariant = size === "large" ? "h4" : size === "medium" ? "h6" : "body1";
  const labelVariant = size === "large" ? "body2" : "caption";

  return (
    <Stack direction={size === "small" ? "row" : "column"} spacing={size === "small" ? 2 : 0.5}>
      <Box>
        <Typography variant={labelVariant} color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
          Líquido
        </Typography>
        <Typography
          variant={netVariant}
          color={netColor}
          fontWeight={700}
          data-testid="pnl-net"
          data-negative={isNegativeNet ? "true" : "false"}
        >
          {formatCurrency(netAmount)}
        </Typography>
      </Box>
      <Box>
        <Typography variant={labelVariant} color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
          Bruto
        </Typography>
        <Typography variant="body2" color={grossColor} data-testid="pnl-gross">
          {formatCurrency(grossAmount)}
        </Typography>
      </Box>
    </Stack>
  );
}

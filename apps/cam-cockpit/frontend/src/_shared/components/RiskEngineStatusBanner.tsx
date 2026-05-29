import { Alert, AlertTitle } from "@mui/material";

interface RiskEngineStatusBannerProps {
  killSwitchActive: boolean;
  riskEngineBlocked: boolean;
  blockReason?: string;
}

export function RiskEngineStatusBanner({ killSwitchActive, riskEngineBlocked, blockReason }: RiskEngineStatusBannerProps) {
  if (killSwitchActive) {
    return (
      <Alert severity="error" role="alert" sx={{ borderRadius: 0, fontWeight: 700 }}>
        <AlertTitle>KILL SWITCH ATIVO — Todas as operações bloqueadas (Art. 18º)</AlertTitle>
        Nenhuma ordem pode ser enviada ao Profit enquanto o Kill Switch estiver ativo.
      </Alert>
    );
  }

  if (riskEngineBlocked && blockReason) {
    return (
      <Alert severity="warning" role="alert" sx={{ borderRadius: 0 }}>
        <AlertTitle>Risk Engine Bloqueou</AlertTitle>
        {blockReason}
      </Alert>
    );
  }

  return null;
}

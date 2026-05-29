import { useState } from "react";
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Chip, Stack } from "@mui/material";
import PowerOffIcon from "@mui/icons-material/PowerOff";
import PowerIcon from "@mui/icons-material/Power";

interface KillSwitchButtonProps {
  isActive: boolean;
  onActivate: (reason: string) => void;
  onDeactivate: () => void;
}

export function KillSwitchButton({ isActive, onActivate, onDeactivate }: KillSwitchButtonProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [reason, setReason] = useState("");

  const handleClick = () => setDialogOpen(true);

  const handleConfirm = () => {
    if (isActive) {
      onDeactivate();
    } else {
      onActivate(reason || "Acionado manualmente");
    }
    setDialogOpen(false);
    setReason("");
  };

  return (
    <>
      <Stack direction="row" alignItems="center" spacing={1}>
        <Button
          aria-label="Kill Switch"
          variant="contained"
          color={isActive ? "error" : "warning"}
          startIcon={isActive ? <PowerOffIcon /> : <PowerIcon />}
          onClick={handleClick}
          sx={{ fontWeight: 700, minWidth: 140 }}
        >
          Kill Switch
        </Button>
        {isActive && (
          <Chip label="ATIVO" color="error" size="small" sx={{ fontWeight: 700, animation: "pulse 1s infinite" }} />
        )}
      </Stack>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>
          {isActive ? "Desativar Kill Switch?" : "Ativar Kill Switch?"}
        </DialogTitle>
        <DialogContent>
          {!isActive && (
            <TextField
              fullWidth
              label="Motivo (opcional)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              margin="normal"
              autoFocus
            />
          )}
          {isActive && (
            <span>Todas as operações serão liberadas. Confirme a desativação.</span>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleConfirm} color={isActive ? "success" : "error"} variant="contained">
            {isActive ? "Desativar" : "Ativar Kill Switch"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

/**
 * Painel de book (DOM) ao vivo — R-05. Condicional: oculto/aviso se indisponível.
 */
import { Box, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";

export interface BookLevel {
  price: number;
  vol: number;
}
export interface BookSnapshot {
  bids: BookLevel[];
  asks: BookLevel[];
}

export function BookPanel({ book }: { book: BookSnapshot | null }) {
  if (!book || (!book.bids?.length && !book.asks?.length)) {
    return (
      <Typography variant="body2" color="text.secondary">
        Book não disponível para este símbolo.
      </Typography>
    );
  }
  const rows = Math.max(book.bids.length, book.asks.length);
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
        Book (DOM)
      </Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell align="right">Compra (vol)</TableCell>
            <TableCell align="center">Preço</TableCell>
            <TableCell>Venda (vol)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Array.from({ length: rows }).map((_, i) => {
            const bid = book.bids[i];
            const ask = book.asks[i];
            return (
              <TableRow key={i}>
                <TableCell align="right" sx={{ color: "success.main" }}>
                  {bid ? bid.vol : ""}
                </TableCell>
                <TableCell align="center">
                  {bid ? bid.price.toFixed(2) : ask ? ask.price.toFixed(2) : ""}
                </TableCell>
                <TableCell sx={{ color: "error.main" }}>{ask ? ask.vol : ""}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Box>
  );
}

/** Helper de teste — envolve componentes nos providers do app + router. */
import type { ReactNode } from "react";
import { render } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { theme } from "../app/theme";
import { UiProvider } from "../_shared/state/uiStore";

export function renderWithProviders(ui: ReactNode, route = "/") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <UiProvider>
          <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
        </UiProvider>
      </ThemeProvider>
    </QueryClientProvider>,
  );
}

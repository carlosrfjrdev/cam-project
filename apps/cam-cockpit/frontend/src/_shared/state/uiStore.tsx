/**
 * UI store leve — TASK-U010 (BL-UI-1). Context + localStorage, sem dependência
 * externa (Zustand não instalado). Persiste o estado da sidebar (colapsada).
 */
import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";

const STORAGE_KEY = "cam.sidebar.collapsed";

function readInitial(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

interface UiState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
}

const UiContext = createContext<UiState | null>(null);

export function UiProvider({ children }: { children: ReactNode }) {
  const [sidebarCollapsed, setCollapsed] = useState<boolean>(readInitial);

  const persist = useCallback((v: boolean) => {
    setCollapsed(v);
    try {
      localStorage.setItem(STORAGE_KEY, String(v));
    } catch {
      /* localStorage indisponível — estado fica em memória */
    }
  }, []);

  const toggleSidebar = useCallback(
    () => persist(!sidebarCollapsed),
    [persist, sidebarCollapsed],
  );

  return (
    <UiContext.Provider
      value={{
        sidebarCollapsed,
        toggleSidebar,
        setSidebarCollapsed: persist,
      }}
    >
      {children}
    </UiContext.Provider>
  );
}

export function useUiStore(): UiState {
  const ctx = useContext(UiContext);
  if (ctx === null) {
    throw new Error("useUiStore precisa estar dentro de <UiProvider>");
  }
  return ctx;
}
